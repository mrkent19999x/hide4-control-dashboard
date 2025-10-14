// Main Dashboard Application
import { firebaseUtils, toast } from './firebase-config.js';

class DashboardApp {
  constructor() {
    this.machines = new Map();
    this.logs = [];
    this.charts = {};
    this.refreshInterval = null;
    this.autoRefreshEnabled = true;

    // Pagination settings
    this.pagination = {
      machines: {
        limit: 50,
        offset: 0,
        hasMore: true,
        loading: false
      },
      logs: {
        limit: 100,
        offset: 0,
        hasMore: true,
        loading: false
      }
    };

    this.init();
  }

  async init() {
    try {
      // Initialize charts
      this.initCharts();

      // Load initial data
      await this.loadMachines();
      await this.loadLogs();

      // Setup realtime listeners
      this.setupRealtimeListeners();

      // Setup auto-refresh
      this.setupAutoRefresh();

      // Setup event listeners
      this.setupEventListeners();

      console.log('✅ Dashboard initialized successfully');
      toast.show('Dashboard đã sẵn sàng', 'success');

    } catch (error) {
      console.error('❌ Dashboard initialization failed:', error);
      toast.show('Lỗi khởi tạo dashboard: ' + error.message, 'error');
    }
  }

  initCharts() {
    // Files Chart
    const filesCtx = document.getElementById('filesChart');
    if (filesCtx) {
      this.charts.files = new Chart(filesCtx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Files đã xử lý',
            data: [],
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }

    // Machines Chart
    const machinesCtx = document.getElementById('machinesChart');
    if (machinesCtx) {
      this.charts.machines = new Chart(machinesCtx, {
        type: 'doughnut',
        data: {
          labels: ['Online', 'Offline'],
          datasets: [{
            data: [0, 0],
            backgroundColor: ['#10b981', '#ef4444'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
    }
  }

  async loadMachines(reset = false) {
    if (this.pagination.machines.loading) return;

    try {
      this.pagination.machines.loading = true;

      if (reset) {
        this.pagination.machines.offset = 0;
        this.pagination.machines.hasMore = true;
        this.machines.clear();
      }

      const machinesRef = window.firebaseRef(window.firebaseDatabase, 'machines');
      const snapshot = await new Promise((resolve) => {
        window.firebaseOnValue(machinesRef, resolve, { onlyOnce: true });
      });

      if (snapshot.exists()) {
        const machinesData = snapshot.val();
        const machinesArray = Object.entries(machinesData);

        // Apply pagination
        const startIndex = this.pagination.machines.offset;
        const endIndex = startIndex + this.pagination.machines.limit;
        const paginatedMachines = machinesArray.slice(startIndex, endIndex);

        // Check if there are more machines
        this.pagination.machines.hasMore = endIndex < machinesArray.length;
        this.pagination.machines.offset = endIndex;

        paginatedMachines.forEach(([machineId, data]) => {
          this.machines.set(machineId, {
            id: machineId,
            ...data.info,
            status: data.status,
            stats: data.stats || {}
          });
        });

        this.updateMachinesDisplay();
        this.updateStatsCards();
      }
    } catch (error) {
      console.error('❌ Error loading machines:', error);
    } finally {
      this.pagination.machines.loading = false;
    }
  }

  async loadMoreMachines() {
    if (!this.pagination.machines.hasMore || this.pagination.machines.loading) return;
    await this.loadMachines();
  }

  async loadMoreLogs() {
    if (!this.pagination.logs.hasMore || this.pagination.logs.loading) return;
    await this.loadLogs();
  }

  resetPagination() {
    this.pagination.machines.offset = 0;
    this.pagination.machines.hasMore = true;
    this.pagination.logs.offset = 0;
    this.pagination.logs.hasMore = true;
  }

  async loadLogs(reset = false) {
    if (this.pagination.logs.loading) return;

    try {
      this.pagination.logs.loading = true;

      if (reset) {
        this.pagination.logs.offset = 0;
        this.pagination.logs.hasMore = true;
        this.logs = [];
      }

      const logsRef = window.firebaseRef(window.firebaseDatabase, 'logs');
      const snapshot = await new Promise((resolve) => {
        window.firebaseOnValue(logsRef, resolve, { onlyOnce: true });
      });

      if (snapshot.exists()) {
        const logsData = snapshot.val();
        const allLogs = [];

        Object.entries(logsData).forEach(([machineId, machineLogs]) => {
          Object.entries(machineLogs).forEach(([timestamp, logData]) => {
            allLogs.push({
              machineId,
              timestamp,
              ...logData
            });
          });
        });

        // Sort by timestamp (newest first)
        allLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        // Apply pagination
        const startIndex = this.pagination.logs.offset;
        const endIndex = startIndex + this.pagination.logs.limit;
        const paginatedLogs = allLogs.slice(startIndex, endIndex);

        // Check if there are more logs
        this.pagination.logs.hasMore = endIndex < allLogs.length;
        this.pagination.logs.offset = endIndex;

        this.logs.push(...paginatedLogs);

        // Sort by timestamp (newest first)
        this.logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        this.updateLogsDisplay();
      }
    } catch (error) {
      console.error('❌ Error loading logs:', error);
    } finally {
      this.pagination.logs.loading = false;
    }
  }

  setupRealtimeListeners() {
    // Listen for machine updates
    const machinesRef = window.firebaseRef(window.firebaseDatabase, 'machines');
    window.firebaseOnValue(machinesRef, (snapshot) => {
      if (snapshot.exists()) {
        const machinesData = snapshot.val();
        this.machines.clear();

        Object.entries(machinesData).forEach(([machineId, data]) => {
          this.machines.set(machineId, {
            id: machineId,
            ...data.info,
            status: data.status,
            stats: data.stats || {}
          });
        });

        this.updateMachinesDisplay();
        this.updateStatsCards();
      }
    });

    // Listen for new logs
    const logsRef = window.firebaseRef(window.firebaseDatabase, 'logs');
    window.firebaseOnValue(logsRef, (snapshot) => {
      if (snapshot.exists()) {
        const logsData = snapshot.val();
        this.logs = [];

        Object.entries(logsData).forEach(([machineId, machineLogs]) => {
          Object.entries(machineLogs).forEach(([timestamp, logData]) => {
            this.logs.push({
              machineId,
              timestamp,
              ...logData
            });
          });
        });

        this.logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        this.updateLogsDisplay();
      }
    });
  }

  setupAutoRefresh() {
    // Auto-refresh every 5 seconds
    this.refreshInterval = setInterval(() => {
      if (this.autoRefreshEnabled) {
        this.updateStatsCards();
        this.updateCharts();
      }
    }, 5000);
  }

  setupEventListeners() {
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('auto-refresh');
    if (autoRefreshToggle) {
      autoRefreshToggle.addEventListener('change', (e) => {
        this.autoRefreshEnabled = e.target.checked;
        if (this.autoRefreshEnabled) {
          toast.show('Auto-refresh đã bật', 'info');
        } else {
          toast.show('Auto-refresh đã tắt', 'warning');
        }
      });
    }
  }

  updateStatsCards() {
    const onlineCount = Array.from(this.machines.values()).filter(machine =>
      firebaseUtils.isMachineOnline(machine.status?.last_heartbeat)
    ).length;

    const offlineCount = this.machines.size - onlineCount;

    // Calculate files processed today
    const today = new Date().toDateString();
    const todayLogs = this.logs.filter(log =>
      new Date(log.timestamp).toDateString() === today &&
      log.event === 'PHÁT HIỆN FILE FAKE'
    ).length;

    // Calculate total files processed
    const totalFiles = this.logs.filter(log =>
      log.event === 'PHÁT HIỆN FILE FAKE'
    ).length;

    // Update DOM elements
    this.updateElement('online-machines', onlineCount);
    this.updateElement('offline-machines', offlineCount);
    this.updateElement('files-today', todayLogs);
    this.updateElement('total-files', totalFiles);
  }

  updateMachinesDisplay() {
    const activeMachinesContainer = document.getElementById('active-machines');
    if (!activeMachinesContainer) return;

    const machines = Array.from(this.machines.values())
      .sort((a, b) => new Date(b.status?.last_heartbeat || 0) - new Date(a.status?.last_heartbeat || 0))
      .slice(0, 5);

    if (machines.length === 0) {
      activeMachinesContainer.innerHTML = '<div class="text-gray-500 text-center py-4">Chưa có máy nào</div>';
      return;
    }

    activeMachinesContainer.innerHTML = machines.map(machine => {
      const isOnline = firebaseUtils.isMachineOnline(machine.status?.last_heartbeat);
      const lastActive = machine.status?.last_heartbeat ?
        firebaseUtils.getRelativeTime(machine.status.last_heartbeat) : 'Chưa biết';

      return `
                <div class="machine-card ${isOnline ? 'online' : 'offline'} p-4 rounded-lg border">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="font-medium text-gray-900">${machine.hostname || machine.id}</h4>
                            <p class="text-sm text-gray-500">${machine.id}</p>
                            <p class="text-xs text-gray-400">Hoạt động: ${lastActive}</p>
                        </div>
                        <div class="flex items-center space-x-2">
                            <div class="w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}"></div>
                            <span class="text-xs ${isOnline ? 'text-green-600' : 'text-red-600'}">
                                ${isOnline ? 'Online' : 'Offline'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
    }).join('');
  }

  updateLogsDisplay() {
    const recentLogsContainer = document.getElementById('recent-logs');
    if (!recentLogsContainer) return;

    const recentLogs = this.logs.slice(0, 5);

    if (recentLogs.length === 0) {
      recentLogsContainer.innerHTML = '<div class="text-gray-500 text-center py-4">Chưa có logs</div>';
      return;
    }

    recentLogsContainer.innerHTML = recentLogs.map(log => {
      const machine = this.machines.get(log.machineId);
      const machineName = machine?.hostname || log.machineId;
      const timeAgo = firebaseUtils.getRelativeTime(log.timestamp);
      const logClass = this.getLogClass(log.event);

      return `
                <div class="log-entry ${logClass} p-3 rounded-lg">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <p class="text-sm font-medium text-gray-900">${log.event}</p>
                            <p class="text-xs text-gray-500">${machineName}</p>
                            ${log.path ? `<p class="text-xs text-gray-400 truncate">${log.path}</p>` : ''}
                        </div>
                        <div class="text-xs text-gray-400 ml-2">
                            ${timeAgo}
                        </div>
                    </div>
                </div>
            `;
    }).join('');
  }

  updateCharts() {
    // Update files chart with last 7 days data
    this.updateFilesChart();

    // Update machines chart
    this.updateMachinesChart();
  }

  updateFilesChart() {
    if (!this.charts.files) return;

    const last7Days = [];
    const filesData = [];

    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];

      last7Days.push(date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' }));

      const dayLogs = this.logs.filter(log =>
        log.timestamp.startsWith(dateStr) && log.event === 'PHÁT HIỆN FILE FAKE'
      ).length;

      filesData.push(dayLogs);
    }

    this.charts.files.data.labels = last7Days;
    this.charts.files.data.datasets[0].data = filesData;
    this.charts.files.update();
  }

  updateMachinesChart() {
    if (!this.charts.machines) return;

    const onlineCount = Array.from(this.machines.values()).filter(machine =>
      firebaseUtils.isMachineOnline(machine.status?.last_heartbeat)
    ).length;

    const offlineCount = this.machines.size - onlineCount;

    this.charts.machines.data.datasets[0].data = [onlineCount, offlineCount];
    this.charts.machines.update();
  }

  getLogClass(event) {
    if (event.includes('PHÁT HIỆN FILE FAKE')) return 'detection';
    if (event.includes('khởi chạy')) return 'startup';
    if (event.includes('heartbeat')) return 'heartbeat';
    if (event.includes('lỗi') || event.includes('thất bại')) return 'error';
    return '';
  }

  updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value;
    }
  }

  destroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }

    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy();
    });
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dashboardApp = new DashboardApp();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (window.dashboardApp) {
    window.dashboardApp.destroy();
  }
});
