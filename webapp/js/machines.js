// Machines Page Application
import { firebaseUtils, toast } from './firebase-config.js';

class MachinesApp {
  constructor() {
    this.machines = new Map();
    this.selectedMachine = null;

    // Pagination settings
    this.pagination = {
      limit: 50,
      offset: 0,
      hasMore: true,
      loading: false,
      totalCount: 0
    };

    // Search and filter
    this.searchTerm = '';
    this.statusFilter = 'all';

    this.init();
  }

  async init() {
    try {
      await this.loadMachines();
      this.setupRealtimeListeners();
      this.setupEventListeners();

      console.log('✅ Machines page initialized');
    } catch (error) {
      console.error('❌ Machines page initialization failed:', error);
      toast.show('Lỗi khởi tạo trang máy: ' + error.message, 'error');
    }
  }

  async loadMachines(reset = false) {
    if (this.pagination.loading) return;

    try {
      this.pagination.loading = true;

      if (reset) {
        this.pagination.offset = 0;
        this.pagination.hasMore = true;
        this.machines.clear();
      }

      const machinesRef = window.firebaseRef(window.firebaseDatabase, 'machines');
      const snapshot = await new Promise((resolve) => {
        window.firebaseOnValue(machinesRef, resolve, { onlyOnce: true });
      });

      if (snapshot.exists()) {
        const machinesData = snapshot.val();
        const allMachines = Object.entries(machinesData);

        // Apply search and filter
        const filteredMachines = this.filterMachines(allMachines);
        this.pagination.totalCount = filteredMachines.length;

        // Apply pagination
        const startIndex = this.pagination.offset;
        const endIndex = startIndex + this.pagination.limit;
        const paginatedMachines = filteredMachines.slice(startIndex, endIndex);

        // Check if there are more machines
        this.pagination.hasMore = endIndex < filteredMachines.length;
        this.pagination.offset = endIndex;

        paginatedMachines.forEach(([machineId, data]) => {
          this.machines.set(machineId, {
            id: machineId,
            ...data.info,
            status: data.status,
            stats: data.stats || {}
          });
        });

        this.updateMachinesList();
        this.updateMachineFilter();
        this.updatePaginationControls();
      }
    } catch (error) {
      console.error('❌ Error loading machines:', error);
    } finally {
      this.pagination.loading = false;
    }
  }

  filterMachines(machinesArray) {
    return machinesArray.filter(([machineId, data]) => {
      const machine = {
        id: machineId,
        ...data.info,
        status: data.status
      };

      // Apply search filter
      if (this.searchTerm) {
        const searchLower = this.searchTerm.toLowerCase();
        const matchesSearch =
          machine.hostname?.toLowerCase().includes(searchLower) ||
          machine.id?.toLowerCase().includes(searchLower) ||
          machine.info?.hostname?.toLowerCase().includes(searchLower);

        if (!matchesSearch) return false;
      }

      // Apply status filter
      if (this.statusFilter !== 'all') {
        const isOnline = firebaseUtils.isMachineOnline(machine.status?.last_heartbeat);
        if (this.statusFilter === 'online' && !isOnline) return false;
        if (this.statusFilter === 'offline' && isOnline) return false;
      }

      return true;
    });
  }

  async loadMoreMachines() {
    if (!this.pagination.hasMore || this.pagination.loading) return;
    await this.loadMachines();
  }

  resetPagination() {
    this.pagination.offset = 0;
    this.pagination.hasMore = true;
  }

  updatePaginationControls() {
    const loadMoreBtn = document.getElementById('load-more-machines');
    if (loadMoreBtn) {
      loadMoreBtn.style.display = this.pagination.hasMore ? 'block' : 'none';
      loadMoreBtn.disabled = this.pagination.loading;
      loadMoreBtn.textContent = this.pagination.loading ? 'Đang tải...' : 'Tải thêm';
    }

    const paginationInfo = document.getElementById('pagination-info');
    if (paginationInfo) {
      const displayed = this.machines.size;
      const total = this.pagination.totalCount;
      paginationInfo.textContent = `Hiển thị ${displayed}/${total} máy`;
    }
  }

  setupRealtimeListeners() {
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

        this.updateMachinesList();
        this.updateMachineFilter();
      }
    });
  }

  setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refresh-machines');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadMachines();
        toast.show('Đã làm mới danh sách máy', 'success');
      });
    }

    // Modal close buttons
    const closeModalBtn = document.getElementById('close-modal-btn');
    const closeModalIcon = document.getElementById('close-modal');
    const modal = document.getElementById('machine-modal');

    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', () => this.closeModal());
    }

    if (closeModalIcon) {
      closeModalIcon.addEventListener('click', () => this.closeModal());
    }

    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) this.closeModal();
      });
    }

    // Send command button
    const sendCommandBtn = document.getElementById('send-command');
    if (sendCommandBtn) {
      sendCommandBtn.addEventListener('click', () => {
        if (this.selectedMachine) {
          this.sendUninstallCommand(this.selectedMachine.id);
        }
      });
    }
  }

  updateMachinesList() {
    const machinesListContainer = document.getElementById('machines-list');
    if (!machinesListContainer) return;

    const machines = Array.from(this.machines.values())
      .sort((a, b) => new Date(b.status?.last_heartbeat || 0) - new Date(a.status?.last_heartbeat || 0));

    if (machines.length === 0) {
      machinesListContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-gray-500 mb-4">Chưa có máy nào được cài đặt</div>
                    <p class="text-sm text-gray-400">Cài đặt Hide4.exe trên máy để bắt đầu giám sát</p>
                </div>
            `;
      return;
    }

    machinesListContainer.innerHTML = machines.map(machine => {
      const isOnline = firebaseUtils.isMachineOnline(machine.status?.last_heartbeat);
      const lastActive = machine.status?.last_heartbeat ?
        firebaseUtils.getRelativeTime(machine.status.last_heartbeat) : 'Chưa biết';
      const uptime = this.calculateUptime(machine.install_date);
      const filesProcessed = machine.stats?.files_processed || 0;

      return `
                <div class="machine-card ${isOnline ? 'online' : 'offline'} p-6 rounded-lg border cursor-pointer hover:shadow-md transition-all"
                     onclick="window.machinesApp.showMachineDetails('${machine.id}')">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="flex items-center space-x-3 mb-2">
                                <h3 class="text-lg font-medium text-gray-900">${machine.hostname || machine.id}</h3>
                                <div class="flex items-center space-x-1">
                                    <div class="w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}"></div>
                                    <span class="text-xs ${isOnline ? 'text-green-600' : 'text-red-600'} font-medium">
                                        ${isOnline ? 'ONLINE' : 'OFFLINE'}
                                    </span>
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                <div>
                                    <span class="font-medium">Machine ID:</span><br>
                                    <span class="font-mono text-xs">${machine.id}</span>
                                </div>
                                <div>
                                    <span class="font-medium">Cài đặt:</span><br>
                                    <span>${machine.install_date || 'Chưa biết'}</span>
                                </div>
                                <div>
                                    <span class="font-medium">Uptime:</span><br>
                                    <span>${uptime}</span>
                                </div>
                                <div>
                                    <span class="font-medium">Files đã xử lý:</span><br>
                                    <span class="font-bold text-blue-600">${filesProcessed}</span>
                                </div>
                            </div>

                            <div class="mt-3 text-xs text-gray-500">
                                Hoạt động cuối: ${lastActive}
                            </div>
                        </div>

                        <div class="ml-4 flex flex-col space-y-2">
                            <button class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                                    onclick="event.stopPropagation(); window.machinesApp.showMachineDetails('${machine.id}')">
                                👁️ Xem chi tiết
                            </button>
                            <button class="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                                    onclick="event.stopPropagation(); window.machinesApp.sendUninstallCommand('${machine.id}')">
                                🗑️ Gỡ cài đặt
                            </button>
                        </div>
                    </div>
                </div>
            `;
    }).join('');
  }

  updateMachineFilter() {
    const machineFilter = document.getElementById('machine-filter');
    if (!machineFilter) return;

    // Clear existing options except first one
    machineFilter.innerHTML = '<option value="">Tất cả máy</option>';

    // Add machine options
    Array.from(this.machines.values()).forEach(machine => {
      const option = document.createElement('option');
      option.value = machine.id;
      option.textContent = `${machine.hostname || machine.id} (${machine.id})`;
      machineFilter.appendChild(option);
    });
  }

  showMachineDetails(machineId) {
    const machine = this.machines.get(machineId);
    if (!machine) return;

    this.selectedMachine = machine;

    const modal = document.getElementById('machine-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');

    if (!modal || !modalTitle || !modalContent) return;

    modalTitle.textContent = `Chi tiết máy: ${machine.hostname || machine.id}`;

    const isOnline = firebaseUtils.isMachineOnline(machine.status?.last_heartbeat);
    const lastActive = machine.status?.last_heartbeat ?
      firebaseUtils.formatTimestamp(machine.status.last_heartbeat) : 'Chưa biết';
    const uptime = this.calculateUptime(machine.install_date);

    modalContent.innerHTML = `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Machine ID</label>
                        <p class="mt-1 text-sm text-gray-900 font-mono">${machine.id}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Hostname</label>
                        <p class="mt-1 text-sm text-gray-900">${machine.hostname || 'Chưa biết'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Trạng thái</label>
                        <div class="mt-1 flex items-center space-x-2">
                            <div class="w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}"></div>
                            <span class="text-sm ${isOnline ? 'text-green-600' : 'text-red-600'} font-medium">
                                ${isOnline ? 'ONLINE' : 'OFFLINE'}
                            </span>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Cài đặt</label>
                        <p class="mt-1 text-sm text-gray-900">${machine.install_date || 'Chưa biết'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Uptime</label>
                        <p class="mt-1 text-sm text-gray-900">${uptime}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Files đã xử lý</label>
                        <p class="mt-1 text-sm text-gray-900 font-bold text-blue-600">${machine.stats?.files_processed || 0}</p>
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700">Hoạt động cuối</label>
                    <p class="mt-1 text-sm text-gray-900">${lastActive}</p>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700">Thống kê</label>
                    <div class="mt-2 grid grid-cols-3 gap-2 text-sm">
                        <div class="bg-gray-50 p-2 rounded">
                            <div class="font-medium">Files hôm nay</div>
                            <div class="text-blue-600 font-bold">${machine.stats?.files_today || 0}</div>
                        </div>
                        <div class="bg-gray-50 p-2 rounded">
                            <div class="font-medium">Files tuần này</div>
                            <div class="text-green-600 font-bold">${machine.stats?.files_week || 0}</div>
                        </div>
                        <div class="bg-gray-50 p-2 rounded">
                            <div class="font-medium">Files tháng này</div>
                            <div class="text-purple-600 font-bold">${machine.stats?.files_month || 0}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    modal.classList.remove('hidden');
  }

  closeModal() {
    const modal = document.getElementById('machine-modal');
    if (modal) {
      modal.classList.add('hidden');
    }
    this.selectedMachine = null;
  }

  async sendUninstallCommand(machineId) {
    if (!confirm(`Bạn có chắc chắn muốn gỡ cài đặt Hide4 trên máy ${machineId}?`)) {
      return;
    }

    try {
      const commandsRef = window.firebaseRef(window.firebaseDatabase, `machines/${machineId}/commands`);
      const commandData = {
        type: 'uninstall',
        timestamp: firebaseUtils.getTimestamp(),
        executed: false,
        params: {
          reason: 'Manual uninstall from dashboard'
        }
      };

      await window.firebasePush(commandsRef, commandData);

      toast.show(`Đã gửi lệnh gỡ cài đặt đến máy ${machineId}`, 'success');

      // Close modal if open
      this.closeModal();

    } catch (error) {
      console.error('❌ Error sending uninstall command:', error);
      toast.show('Lỗi gửi lệnh gỡ cài đặt: ' + error.message, 'error');
    }
  }

  calculateUptime(installDate) {
    if (!installDate) return 'Chưa biết';

    try {
      const install = new Date(installDate);
      const now = new Date();
      const diffMs = now - install;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffDays === 0) return 'Hôm nay';
      if (diffDays === 1) return '1 ngày';
      if (diffDays < 30) return `${diffDays} ngày`;

      const diffMonths = Math.floor(diffDays / 30);
      if (diffMonths < 12) return `${diffMonths} tháng`;

      const diffYears = Math.floor(diffMonths / 12);
      return `${diffYears} năm`;
    } catch {
      return 'Chưa biết';
    }
  }
}

// Initialize machines app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.machinesApp = new MachinesApp();
});
