// Logs Page Application
import { firebaseUtils, toast } from './firebase-config.js';

class LogsApp {
  constructor() {
    this.logs = [];
    this.filteredLogs = [];
    this.filters = {
      machine: '',
      event: '',
      dateFrom: '',
      dateTo: ''
    };
    this.autoRefreshEnabled = true;
    this.refreshInterval = null;

    // Pagination settings
    this.pagination = {
      limit: 100,
      offset: 0,
      hasMore: true,
      loading: false,
      totalCount: 0
    };

    this.init();
  }

  async init() {
    try {
      await this.loadLogs();
      this.setupRealtimeListeners();
      this.setupEventListeners();
      this.setupAutoRefresh();

      console.log('✅ Logs page initialized');
    } catch (error) {
      console.error('❌ Logs page initialization failed:', error);
      toast.show('Lỗi khởi tạo trang logs: ' + error.message, 'error');
    }
  }

  async loadLogs(reset = false) {
    if (this.pagination.loading) return;

    try {
      this.pagination.loading = true;

      if (reset) {
        this.pagination.offset = 0;
        this.pagination.hasMore = true;
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

        // Apply filters
        const filteredLogs = this.filterLogs(allLogs);
        this.pagination.totalCount = filteredLogs.length;

        // Apply pagination
        const startIndex = this.pagination.offset;
        const endIndex = startIndex + this.pagination.limit;
        const paginatedLogs = filteredLogs.slice(startIndex, endIndex);

        // Check if there are more logs
        this.pagination.hasMore = endIndex < filteredLogs.length;
        this.pagination.offset = endIndex;

        this.logs.push(...paginatedLogs);
        this.filteredLogs = [...this.logs];

        this.updateLogsDisplay();
        this.updatePaginationControls();
      }
    } catch (error) {
      console.error('❌ Error loading logs:', error);
    } finally {
      this.pagination.loading = false;
    }
  }

  filterLogs(logsArray) {
    return logsArray.filter(log => {
      // Machine filter
      if (this.filters.machine && log.machineId !== this.filters.machine) {
        return false;
      }

      // Event filter
      if (this.filters.event && !log.event?.toLowerCase().includes(this.filters.event.toLowerCase())) {
        return false;
      }

      // Date filters
      if (this.filters.dateFrom) {
        const logDate = new Date(log.timestamp);
        const fromDate = new Date(this.filters.dateFrom);
        if (logDate < fromDate) return false;
      }

      if (this.filters.dateTo) {
        const logDate = new Date(log.timestamp);
        const toDate = new Date(this.filters.dateTo);
        if (logDate > toDate) return false;
      }

      return true;
    });
  }

  async loadMoreLogs() {
    if (!this.pagination.hasMore || this.pagination.loading) return;
    await this.loadLogs();
  }

  resetPagination() {
    this.pagination.offset = 0;
    this.pagination.hasMore = true;
  }

  updatePaginationControls() {
    const loadMoreBtn = document.getElementById('load-more-logs');
    if (loadMoreBtn) {
      loadMoreBtn.style.display = this.pagination.hasMore ? 'block' : 'none';
      loadMoreBtn.disabled = this.pagination.loading;
      loadMoreBtn.textContent = this.pagination.loading ? 'Đang tải...' : 'Tải thêm';
    }

    const paginationInfo = document.getElementById('pagination-info');
    if (paginationInfo) {
      const displayed = this.logs.length;
      const total = this.pagination.totalCount;
      paginationInfo.textContent = `Hiển thị ${displayed}/${total} logs`;
    }
  }

  setupRealtimeListeners() {
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
        this.applyFilters();
      }
    });
  }

  setupEventListeners() {
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('auto-refresh');
    if (autoRefreshToggle) {
      autoRefreshToggle.addEventListener('change', (e) => {
        this.autoRefreshEnabled = e.target.checked;
        if (this.autoRefreshEnabled) {
          this.setupAutoRefresh();
          toast.show('Auto-refresh đã bật', 'info');
        } else {
          this.clearAutoRefresh();
          toast.show('Auto-refresh đã tắt', 'warning');
        }
      });
    }

    // Apply filters button
    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
      applyFiltersBtn.addEventListener('click', () => {
        this.updateFilters();
        this.applyFilters();
        toast.show('Đã áp dụng bộ lọc', 'success');
      });
    }

    // Export logs button
    const exportLogsBtn = document.getElementById('export-logs');
    if (exportLogsBtn) {
      exportLogsBtn.addEventListener('click', () => {
        this.exportLogs();
      });
    }

    // Filter inputs
    const filterInputs = ['machine-filter', 'event-filter', 'date-from', 'date-to'];
    filterInputs.forEach(inputId => {
      const input = document.getElementById(inputId);
      if (input) {
        input.addEventListener('change', () => {
          this.updateFilters();
          this.applyFilters();
        });
      }
    });
  }

  setupAutoRefresh() {
    this.clearAutoRefresh();

    if (this.autoRefreshEnabled) {
      this.refreshInterval = setInterval(() => {
        this.loadLogs();
      }, 5000);
    }
  }

  clearAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  updateFilters() {
    this.filters.machine = document.getElementById('machine-filter')?.value || '';
    this.filters.event = document.getElementById('event-filter')?.value || '';
    this.filters.dateFrom = document.getElementById('date-from')?.value || '';
    this.filters.dateTo = document.getElementById('date-to')?.value || '';
  }

  applyFilters() {
    this.filteredLogs = this.logs.filter(log => {
      // Machine filter
      if (this.filters.machine && log.machineId !== this.filters.machine) {
        return false;
      }

      // Event filter
      if (this.filters.event && !log.event.includes(this.filters.event)) {
        return false;
      }

      // Date filters
      const logDate = new Date(log.timestamp).toISOString().split('T')[0];

      if (this.filters.dateFrom && logDate < this.filters.dateFrom) {
        return false;
      }

      if (this.filters.dateTo && logDate > this.filters.dateTo) {
        return false;
      }

      return true;
    });

    this.updateLogsDisplay();
  }

  updateLogsDisplay() {
    const logsListContainer = document.getElementById('logs-list');
    if (!logsListContainer) return;

    if (this.filteredLogs.length === 0) {
      logsListContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-gray-500 mb-4">Không có logs phù hợp</div>
                    <p class="text-sm text-gray-400">Thử thay đổi bộ lọc hoặc kiểm tra lại dữ liệu</p>
                </div>
            `;
      return;
    }

    logsListContainer.innerHTML = this.filteredLogs.map(log => {
      const timeAgo = firebaseUtils.getRelativeTime(log.timestamp);
      const formattedTime = firebaseUtils.formatTimestamp(log.timestamp);
      const logClass = this.getLogClass(log.event);

      return `
                <div class="log-entry ${logClass} p-4 rounded-lg border-l-4">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center space-x-2">
                            <span class="text-sm font-medium text-gray-900">${log.event}</span>
                            <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">${log.machineId}</span>
                        </div>
                        <div class="text-xs text-gray-400">
                            ${timeAgo}
                        </div>
                    </div>

                    ${log.path ? `
                        <div class="text-sm text-gray-600 mb-2">
                            <span class="font-medium">Đường dẫn:</span>
                            <span class="font-mono text-xs break-all">${log.path}</span>
                        </div>
                    ` : ''}

                    ${log.fingerprint ? `
                        <div class="text-sm text-gray-600 mb-2">
                            <span class="font-medium">Fingerprint:</span>
                            <div class="mt-1 grid grid-cols-2 gap-2 text-xs">
                                ${log.fingerprint.mst ? `<div><span class="font-medium">MST:</span> ${log.fingerprint.mst}</div>` : ''}
                                ${log.fingerprint.maTKhai ? `<div><span class="font-medium">Mã tờ khai:</span> ${log.fingerprint.maTKhai}</div>` : ''}
                                ${log.fingerprint.kyKKhai ? `<div><span class="font-medium">Kỳ khai:</span> ${log.fingerprint.kyKKhai}</div>` : ''}
                                ${log.fingerprint.soLan ? `<div><span class="font-medium">Số lần:</span> ${log.fingerprint.soLan}</div>` : ''}
                            </div>
                        </div>
                    ` : ''}

                    <div class="text-xs text-gray-400">
                        ${formattedTime}
                    </div>
                </div>
            `;
    }).join('');
  }

  getLogClass(event) {
    if (event.includes('PHÁT HIỆN FILE FAKE')) return 'detection';
    if (event.includes('khởi chạy')) return 'startup';
    if (event.includes('heartbeat')) return 'heartbeat';
    if (event.includes('lỗi') || event.includes('thất bại')) return 'error';
    return '';
  }

  exportLogs() {
    try {
      const exportData = {
        export_time: firebaseUtils.getTimestamp(),
        total_logs: this.filteredLogs.length,
        filters: this.filters,
        logs: this.filteredLogs.map(log => ({
          timestamp: log.timestamp,
          machine_id: log.machineId,
          event: log.event,
          path: log.path || null,
          fingerprint: log.fingerprint || null
        }))
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `hide4-logs-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.show(`Đã xuất ${this.filteredLogs.length} logs`, 'success');

    } catch (error) {
      console.error('❌ Error exporting logs:', error);
      toast.show('Lỗi xuất logs: ' + error.message, 'error');
    }
  }

  destroy() {
    this.clearAutoRefresh();
  }
}

// Initialize logs app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.logsApp = new LogsApp();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (window.logsApp) {
    window.logsApp.destroy();
  }
});
