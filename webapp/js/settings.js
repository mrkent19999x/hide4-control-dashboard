// Settings Page Application
import { firebaseUtils, toast } from './firebase-config.js';

// Authentication check
if (!window.auth || !window.auth.isLoggedIn()) {
  console.log('🔒 Authentication required - redirecting to login');
  window.location.href = 'login.html';
}

class SettingsApp {
  constructor() {
    this.settings = {
      heartbeatInterval: 300,
      dashboardRefresh: 5
    };

    this.init();
  }

  async init() {
    try {
      await this.loadSettings();
      await this.loadUsageStats();
      this.setupEventListeners();
      this.updateFirebaseInfo();

      console.log('✅ Settings page initialized');
    } catch (error) {
      console.error('❌ Settings page initialization failed:', error);
      toast.show('Lỗi khởi tạo trang cài đặt: ' + error.message, 'error');
    }
  }

  async loadSettings() {
    try {
      const settingsRef = window.firebaseRef(window.firebaseDatabase, 'settings');
      const snapshot = await new Promise((resolve) => {
        window.firebaseOnValue(settingsRef, resolve, { onlyOnce: true });
      });

      if (snapshot.exists()) {
        this.settings = { ...this.settings, ...snapshot.val() };
        this.updateSettingsForm();
      }
    } catch (error) {
      console.error('❌ Error loading settings:', error);
    }
  }

  async loadUsageStats() {
    try {
      // Load machines count
      const machinesRef = window.firebaseRef(window.firebaseDatabase, 'machines');
      const machinesSnapshot = await new Promise((resolve) => {
        window.firebaseOnValue(machinesRef, resolve, { onlyOnce: true });
      });

      const machinesCount = machinesSnapshot.exists() ? Object.keys(machinesSnapshot.val()).length : 0;

      // Load logs count
      const logsRef = window.firebaseRef(window.firebaseDatabase, 'logs');
      const logsSnapshot = await new Promise((resolve) => {
        window.firebaseOnValue(logsRef, resolve, { onlyOnce: true });
      });

      let logsCount = 0;
      let storageUsed = 0;

      if (logsSnapshot.exists()) {
        const logsData = logsSnapshot.val();
        Object.values(logsData).forEach(machineLogs => {
          logsCount += Object.keys(machineLogs).length;
        });

        // Estimate storage usage (rough calculation)
        storageUsed = Math.round(logsCount * 0.5); // ~0.5KB per log entry
      }

      this.updateUsageStats({
        totalMachines: machinesCount,
        totalLogs: logsCount,
        storageUsed: storageUsed,
        bandwidthUsed: Math.round(storageUsed * 0.1) // Estimate
      });

    } catch (error) {
      console.error('❌ Error loading usage stats:', error);
    }
  }

  setupEventListeners() {
    // Save settings button
    const saveSettingsBtn = document.getElementById('save-settings');
    if (saveSettingsBtn) {
      saveSettingsBtn.addEventListener('click', () => {
        this.saveSettings();
      });
    }

    // Delete old logs button
    const deleteOldLogsBtn = document.getElementById('delete-old-logs');
    if (deleteOldLogsBtn) {
      deleteOldLogsBtn.addEventListener('click', () => {
        this.deleteOldLogs();
      });
    }

    // Export all data button
    const exportAllDataBtn = document.getElementById('export-all-data');
    if (exportAllDataBtn) {
      exportAllDataBtn.addEventListener('click', () => {
        this.exportAllData();
      });
    }
  }

  updateSettingsForm() {
    const heartbeatInterval = document.getElementById('heartbeat-interval');
    const dashboardRefresh = document.getElementById('dashboard-refresh');

    if (heartbeatInterval) {
      heartbeatInterval.value = this.settings.heartbeatInterval;
    }

    if (dashboardRefresh) {
      dashboardRefresh.value = this.settings.dashboardRefresh;
    }
  }

  async saveSettings() {
    try {
      const heartbeatInterval = parseInt(document.getElementById('heartbeat-interval')?.value || '300');
      const dashboardRefresh = parseInt(document.getElementById('dashboard-refresh')?.value || '5');

      if (heartbeatInterval < 60 || heartbeatInterval > 3600) {
        toast.show('Heartbeat interval phải từ 60-3600 giây', 'error');
        return;
      }

      if (dashboardRefresh < 1 || dashboardRefresh > 60) {
        toast.show('Dashboard refresh phải từ 1-60 giây', 'error');
        return;
      }

      const newSettings = {
        heartbeatInterval,
        dashboardRefresh,
        lastUpdated: firebaseUtils.getTimestamp()
      };

      const settingsRef = window.firebaseRef(window.firebaseDatabase, 'settings');
      await window.firebaseSet(settingsRef, newSettings);

      this.settings = { ...this.settings, ...newSettings };

      toast.show('Đã lưu cài đặt thành công', 'success');

    } catch (error) {
      console.error('❌ Error saving settings:', error);
      toast.show('Lỗi lưu cài đặt: ' + error.message, 'error');
    }
  }

  async deleteOldLogs() {
    const deleteDays = parseInt(document.getElementById('delete-days')?.value || '30');

    if (deleteDays < 1 || deleteDays > 365) {
      toast.show('Số ngày phải từ 1-365', 'error');
      return;
    }

    if (!confirm(`Bạn có chắc chắn muốn xóa logs cũ hơn ${deleteDays} ngày?`)) {
      return;
    }

    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - deleteDays);
      const cutoffTimestamp = cutoffDate.toISOString();

      const logsRef = window.firebaseRef(window.firebaseDatabase, 'logs');
      const snapshot = await new Promise((resolve) => {
        window.firebaseOnValue(logsRef, resolve, { onlyOnce: true });
      });

      if (!snapshot.exists()) {
        toast.show('Không có logs để xóa', 'info');
        return;
      }

      const logsData = snapshot.val();
      let deletedCount = 0;

      // Delete old logs
      for (const [machineId, machineLogs] of Object.entries(logsData)) {
        for (const [timestamp, logData] of Object.entries(machineLogs)) {
          if (timestamp < cutoffTimestamp) {
            const logRef = window.firebaseRef(window.firebaseDatabase, `logs/${machineId}/${timestamp}`);
            await window.firebaseRemove(logRef);
            deletedCount++;
          }
        }
      }

      toast.show(`Đã xóa ${deletedCount} logs cũ`, 'success');

    } catch (error) {
      console.error('❌ Error deleting old logs:', error);
      toast.show('Lỗi xóa logs cũ: ' + error.message, 'error');
    }
  }

  async exportAllData() {
    try {
      // Load all data
      const [machinesSnapshot, logsSnapshot, settingsSnapshot] = await Promise.all([
        new Promise((resolve) => {
          window.firebaseOnValue(window.firebaseRef(window.firebaseDatabase, 'machines'), resolve, { onlyOnce: true });
        }),
        new Promise((resolve) => {
          window.firebaseOnValue(window.firebaseRef(window.firebaseDatabase, 'logs'), resolve, { onlyOnce: true });
        }),
        new Promise((resolve) => {
          window.firebaseOnValue(window.firebaseRef(window.firebaseDatabase, 'settings'), resolve, { onlyOnce: true });
        })
      ]);

      const exportData = {
        export_time: firebaseUtils.getTimestamp(),
        version: '1.0',
        machines: machinesSnapshot.exists() ? machinesSnapshot.val() : {},
        logs: logsSnapshot.exists() ? logsSnapshot.val() : {},
        settings: settingsSnapshot.exists() ? settingsSnapshot.val() : {}
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `hide4-full-backup-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.show('Đã xuất tất cả dữ liệu', 'success');

    } catch (error) {
      console.error('❌ Error exporting all data:', error);
      toast.show('Lỗi xuất dữ liệu: ' + error.message, 'error');
    }
  }

  updateUsageStats(stats) {
    this.updateElement('total-machines', stats.totalMachines);
    this.updateElement('total-logs', stats.totalLogs);
    this.updateElement('storage-used', stats.storageUsed);
    this.updateElement('bandwidth-used', stats.bandwidthUsed);

    // Update quota bar (Firebase free tier: 1GB storage, 10GB/month bandwidth)
    const storagePercent = Math.min((stats.storageUsed / 1024) * 100, 100); // Convert MB to GB
    const bandwidthPercent = Math.min((stats.bandwidthUsed / 10240) * 100, 100); // Convert MB to GB
    const quotaPercent = Math.max(storagePercent, bandwidthPercent);

    const quotaBar = document.getElementById('quota-bar');
    const quotaText = document.getElementById('quota-text');

    if (quotaBar) {
      quotaBar.style.width = `${quotaPercent}%`;
    }

    if (quotaText) {
      quotaText.textContent = `${quotaPercent.toFixed(1)}% sử dụng`;
    }
  }

  updateFirebaseInfo() {
    // Update Firebase URL
    const firebaseUrl = document.getElementById('firebase-url');
    if (firebaseUrl) {
      firebaseUrl.value = window.firebaseDatabase.app.options.databaseURL || 'Chưa cấu hình';
    }

    // Update Project ID
    const firebaseProject = document.getElementById('firebase-project');
    if (firebaseProject) {
      firebaseProject.value = window.firebaseDatabase.app.options.projectId || 'Chưa cấu hình';
    }
  }

  updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value;
    }
  }
}

// Initialize settings app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.settingsApp = new SettingsApp();
});
