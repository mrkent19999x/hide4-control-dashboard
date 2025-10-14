// Performance Monitoring System
import { toast } from './firebase-config.js';

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      queries: [],
      operations: [],
      errors: [],
      performance: {
        avgQueryTime: 0,
        totalQueries: 0,
        slowQueries: 0,
        errorRate: 0
      }
    };

    this.thresholds = {
      slowQuery: 2000, // 2 seconds
      errorRate: 0.1,  // 10%
      maxQueries: 1000
    };

    this.isMonitoring = false;
    this.monitoringInterval = null;

    this.init();
  }

  init() {
    this.setupPerformanceTracking();
    this.startMonitoring();
    this.setupUI();
    console.log('✅ Performance Monitor initialized');
  }

  setupPerformanceTracking() {
    // Track Firebase operations
    const originalFirebaseOnValue = window.firebaseOnValue;
    const originalFirebaseSet = window.firebaseSet;
    const originalFirebaseUpdate = window.firebaseUpdate;
    const originalFirebasePush = window.firebasePush;

    // Wrap Firebase operations with performance tracking
    window.firebaseOnValue = (...args) => {
      return this.trackOperation('read', () => originalFirebaseOnValue(...args));
    };

    window.firebaseSet = (...args) => {
      return this.trackOperation('write', () => originalFirebaseSet(...args));
    };

    window.firebaseUpdate = (...args) => {
      return this.trackOperation('update', () => originalFirebaseUpdate(...args));
    };

    window.firebasePush = (...args) => {
      return this.trackOperation('push', () => originalFirebasePush(...args));
    };
  }

  async trackOperation(type, operation) {
    const startTime = performance.now();
    const operationId = this.generateOperationId();

    try {
      const result = await operation();
      const endTime = performance.now();
      const duration = endTime - startTime;

      this.recordOperation({
        id: operationId,
        type,
        duration,
        success: true,
        timestamp: new Date().toISOString(),
        error: null
      });

      return result;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;

      this.recordOperation({
        id: operationId,
        type,
        duration,
        success: false,
        timestamp: new Date().toISOString(),
        error: error.message
      });

      throw error;
    }
  }

  recordOperation(operation) {
    // Add to operations array
    this.metrics.operations.push(operation);

    // Keep only recent operations (last 1000)
    if (this.metrics.operations.length > this.thresholds.maxQueries) {
      this.metrics.operations = this.metrics.operations.slice(-this.thresholds.maxQueries);
    }

    // Update performance metrics
    this.updatePerformanceMetrics();

    // Check for alerts
    this.checkAlerts(operation);
  }

  updatePerformanceMetrics() {
    const operations = this.metrics.operations;
    if (operations.length === 0) return;

    // Calculate average query time
    const totalTime = operations.reduce((sum, op) => sum + op.duration, 0);
    this.metrics.performance.avgQueryTime = totalTime / operations.length;

    // Count total queries
    this.metrics.performance.totalQueries = operations.length;

    // Count slow queries
    this.metrics.performance.slowQueries = operations.filter(
      op => op.duration > this.thresholds.slowQuery
    ).length;

    // Calculate error rate
    const errorCount = operations.filter(op => !op.success).length;
    this.metrics.performance.errorRate = errorCount / operations.length;
  }

  checkAlerts(operation) {
    // Slow query alert
    if (operation.duration > this.thresholds.slowQuery) {
      this.showAlert('slow_query', {
        type: operation.type,
        duration: operation.duration,
        threshold: this.thresholds.slowQuery
      });
    }

    // High error rate alert
    if (this.metrics.performance.errorRate > this.thresholds.errorRate) {
      this.showAlert('high_error_rate', {
        errorRate: this.metrics.performance.errorRate,
        threshold: this.thresholds.errorRate
      });
    }
  }

  showAlert(type, data) {
    const alerts = {
      slow_query: `⚠️ Slow ${data.type} query detected: ${data.duration.toFixed(2)}ms (threshold: ${data.threshold}ms)`,
      high_error_rate: `⚠️ High error rate: ${(data.errorRate * 100).toFixed(1)}% (threshold: ${(data.threshold * 100).toFixed(1)}%)`
    };

    console.warn(alerts[type]);
    toast.show(alerts[type], 'warning');
  }

  startMonitoring() {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.updateDashboard();
    }, 5000); // Update every 5 seconds
  }

  stopMonitoring() {
    if (!this.isMonitoring) return;

    this.isMonitoring = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  updateDashboard() {
    // Update performance metrics display
    this.updatePerformanceDisplay();

    // Update charts if they exist
    this.updatePerformanceCharts();
  }

  updatePerformanceDisplay() {
    const elements = {
      avgQueryTime: document.getElementById('avg-query-time'),
      totalQueries: document.getElementById('total-queries'),
      slowQueries: document.getElementById('slow-queries'),
      errorRate: document.getElementById('error-rate')
    };

    if (elements.avgQueryTime) {
      elements.avgQueryTime.textContent = `${this.metrics.performance.avgQueryTime.toFixed(2)}ms`;
    }

    if (elements.totalQueries) {
      elements.totalQueries.textContent = this.metrics.performance.totalQueries.toString();
    }

    if (elements.slowQueries) {
      elements.slowQueries.textContent = this.metrics.performance.slowQueries.toString();
    }

    if (elements.errorRate) {
      elements.errorRate.textContent = `${(this.metrics.performance.errorRate * 100).toFixed(1)}%`;
    }
  }

  updatePerformanceCharts() {
    // Update query time chart
    this.updateQueryTimeChart();

    // Update error rate chart
    this.updateErrorRateChart();
  }

  updateQueryTimeChart() {
    const chartElement = document.getElementById('query-time-chart');
    if (!chartElement) return;

    // Get recent operations (last 20)
    const recentOps = this.metrics.operations.slice(-20);
    const labels = recentOps.map(op => new Date(op.timestamp).toLocaleTimeString());
    const data = recentOps.map(op => op.duration);

    // Update chart if it exists
    if (window.queryTimeChart) {
      window.queryTimeChart.data.labels = labels;
      window.queryTimeChart.data.datasets[0].data = data;
      window.queryTimeChart.update();
    }
  }

  updateErrorRateChart() {
    const chartElement = document.getElementById('error-rate-chart');
    if (!chartElement) return;

    // Calculate error rate over time (last 10 intervals)
    const intervals = 10;
    const intervalSize = Math.max(1, Math.floor(this.metrics.operations.length / intervals));
    const errorRates = [];
    const labels = [];

    for (let i = 0; i < intervals; i++) {
      const start = i * intervalSize;
      const end = Math.min(start + intervalSize, this.metrics.operations.length);
      const intervalOps = this.metrics.operations.slice(start, end);

      if (intervalOps.length > 0) {
        const errorCount = intervalOps.filter(op => !op.success).length;
        errorRates.push((errorCount / intervalOps.length) * 100);
        labels.push(`Interval ${i + 1}`);
      }
    }

    // Update chart if it exists
    if (window.errorRateChart) {
      window.errorRateChart.data.labels = labels;
      window.errorRateChart.data.datasets[0].data = errorRates;
      window.errorRateChart.update();
    }
  }

  setupUI() {
    // Create performance dashboard if it doesn't exist
    this.createPerformanceDashboard();

    // Setup event listeners
    this.setupEventListeners();
  }

  createPerformanceDashboard() {
    const dashboard = document.getElementById('performance-dashboard');
    if (dashboard) return; // Already exists

    const container = document.querySelector('.container');
    if (!container) return;

    const performanceHTML = `
      <div id="performance-dashboard" class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-2xl font-bold mb-4">Performance Monitor</h2>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-blue-50 p-4 rounded-lg">
            <h3 class="text-sm font-medium text-blue-600">Avg Query Time</h3>
            <p id="avg-query-time" class="text-2xl font-bold text-blue-900">0ms</p>
          </div>

          <div class="bg-green-50 p-4 rounded-lg">
            <h3 class="text-sm font-medium text-green-600">Total Queries</h3>
            <p id="total-queries" class="text-2xl font-bold text-green-900">0</p>
          </div>

          <div class="bg-yellow-50 p-4 rounded-lg">
            <h3 class="text-sm font-medium text-yellow-600">Slow Queries</h3>
            <p id="slow-queries" class="text-2xl font-bold text-yellow-900">0</p>
          </div>

          <div class="bg-red-50 p-4 rounded-lg">
            <h3 class="text-sm font-medium text-red-600">Error Rate</h3>
            <p id="error-rate" class="text-2xl font-bold text-red-900">0%</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-lg font-semibold mb-2">Query Time Trend</h3>
            <canvas id="query-time-chart" width="400" height="200"></canvas>
          </div>

          <div>
            <h3 class="text-lg font-semibold mb-2">Error Rate Trend</h3>
            <canvas id="error-rate-chart" width="400" height="200"></canvas>
          </div>
        </div>

        <div class="mt-4 flex gap-2">
          <button id="start-monitoring" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            Start Monitoring
          </button>
          <button id="stop-monitoring" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            Stop Monitoring
          </button>
          <button id="clear-metrics" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
            Clear Metrics
          </button>
        </div>
      </div>
    `;

    container.insertAdjacentHTML('afterbegin', performanceHTML);

    // Initialize charts
    this.initializeCharts();
  }

  initializeCharts() {
    // Query time chart
    const queryTimeCtx = document.getElementById('query-time-chart');
    if (queryTimeCtx) {
      window.queryTimeChart = new Chart(queryTimeCtx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Query Time (ms)',
            data: [],
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }

    // Error rate chart
    const errorRateCtx = document.getElementById('error-rate-chart');
    if (errorRateCtx) {
      window.errorRateChart = new Chart(errorRateCtx, {
        type: 'bar',
        data: {
          labels: [],
          datasets: [{
            label: 'Error Rate (%)',
            data: [],
            backgroundColor: 'rgba(239, 68, 68, 0.8)',
            borderColor: 'rgb(239, 68, 68)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      });
    }
  }

  setupEventListeners() {
    // Start monitoring button
    const startBtn = document.getElementById('start-monitoring');
    if (startBtn) {
      startBtn.addEventListener('click', () => {
        this.startMonitoring();
        toast.show('Performance monitoring started', 'success');
      });
    }

    // Stop monitoring button
    const stopBtn = document.getElementById('stop-monitoring');
    if (stopBtn) {
      stopBtn.addEventListener('click', () => {
        this.stopMonitoring();
        toast.show('Performance monitoring stopped', 'info');
      });
    }

    // Clear metrics button
    const clearBtn = document.getElementById('clear-metrics');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.clearMetrics();
        toast.show('Performance metrics cleared', 'info');
      });
    }
  }

  clearMetrics() {
    this.metrics.operations = [];
    this.metrics.performance = {
      avgQueryTime: 0,
      totalQueries: 0,
      slowQueries: 0,
      errorRate: 0
    };

    this.updatePerformanceDisplay();
    this.updatePerformanceCharts();
  }

  generateOperationId() {
    return 'op_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  getMetrics() {
    return {
      ...this.metrics,
      isMonitoring: this.isMonitoring,
      thresholds: this.thresholds
    };
  }

  exportMetrics() {
    const data = {
      timestamp: new Date().toISOString(),
      metrics: this.getMetrics(),
      operations: this.metrics.operations.slice(-100) // Last 100 operations
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-metrics-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.show('Performance metrics exported', 'success');
  }
}

// Export for use in other modules
export { PerformanceMonitor };

// Auto-initialize if on main dashboard
if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
  window.performanceMonitor = new PerformanceMonitor();
}
