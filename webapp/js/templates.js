// templates.js - GitHub Templates Management for Hide4 Control Dashboard

import { push } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js';
import { firebaseUtils, toast } from './firebase-config.js';

// GitHub Configuration
const GITHUB_CONFIG = {
  owner: 'mrkent19999x',
  repo: 'hide4-control-dashboard',
  templatesPath: 'xml-templates',
  apiBase: 'https://api.github.com'
};

// Get database reference
const database = window.firebaseDatabase;

class GitHubTemplatesManager {
  constructor() {
    this.templates = [];
    this.githubToken = localStorage.getItem('github_token') || '';
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadTemplates();
    this.updateStats();
    this.checkGitHubToken();
  }

  checkGitHubToken() {
    const tokenStatus = document.getElementById('token-status');
    if (this.githubToken) {
      tokenStatus.innerHTML = `
        <div class="flex items-center text-green-600">
          <span class="text-sm">✅ GitHub Token đã cấu hình</span>
          <button onclick="templatesManager.clearToken()" class="ml-2 text-xs text-red-600 hover:text-red-800">Xóa</button>
        </div>
      `;
    } else {
      tokenStatus.innerHTML = `
        <div class="flex items-center text-yellow-600">
          <span class="text-sm">⚠️ Chỉ đọc được templates (cần token để upload/xóa)</span>
          <button onclick="templatesManager.showTokenDialog()" class="ml-2 text-xs text-blue-600 hover:text-blue-800">Cấu hình</button>
        </div>
      `;
    }
  }

  showTokenDialog() {
    const token = prompt('Nhập GitHub Personal Access Token:\n\n1. Vào GitHub → Settings → Developer settings → Personal access tokens\n2. Tạo token mới với quyền "repo"\n3. Dán token vào đây:');
    
    if (token && token.trim()) {
      this.githubToken = token.trim();
      localStorage.setItem('github_token', this.githubToken);
      this.checkGitHubToken();
      toast.show('✅ GitHub Token đã được lưu', 'success');
    }
  }

  clearToken() {
    this.githubToken = '';
    localStorage.removeItem('github_token');
    this.checkGitHubToken();
    toast.show('🗑️ GitHub Token đã được xóa', 'info');
  }

  setupEventListeners() {
    console.log('🚀 Setting up GitHub templates event listeners...');

    // File input change
    document.getElementById('file-input').addEventListener('change', (e) => {
      console.log('📁 File input changed:', e.target.files.length);
      this.handleFileSelect(e.target.files);
    });

    // Upload area click
    document.getElementById('upload-area').addEventListener('click', () => {
      console.log('🖱️ Upload area clicked');
      if (!this.githubToken) {
        toast.show('⚠️ Cần GitHub Token để upload templates', 'warning');
        this.showTokenDialog();
        return;
      }
      document.getElementById('file-input').click();
    });

    // Drag and drop
    const uploadArea = document.getElementById('upload-area');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      uploadArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    });

    // Highlight drop area when item is dragged over it
    uploadArea.addEventListener('dragenter', (e) => {
      uploadArea.classList.add('border-blue-400', 'bg-blue-50');
    });

    uploadArea.addEventListener('dragover', (e) => {
      uploadArea.classList.add('border-blue-400', 'bg-blue-50');
    });

    uploadArea.addEventListener('dragleave', (e) => {
      uploadArea.classList.remove('border-blue-400', 'bg-blue-50');
    });

    uploadArea.addEventListener('drop', (e) => {
      uploadArea.classList.remove('border-blue-400', 'bg-blue-50');

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        console.log('📁 Files dropped:', files.length);
        if (!this.githubToken) {
          toast.show('⚠️ Cần GitHub Token để upload templates', 'warning');
          this.showTokenDialog();
          return;
        }
        this.handleFileSelect(files);
      }
    });

    // Select files button
    document.getElementById('select-files-btn').addEventListener('click', () => {
      if (!this.githubToken) {
        toast.show('⚠️ Cần GitHub Token để upload templates', 'warning');
        this.showTokenDialog();
        return;
      }
      document.getElementById('file-input').click();
    });

    // Refresh templates
    document.getElementById('refresh-templates').addEventListener('click', () => {
      this.loadTemplates();
    });

    // Clear all templates
    document.getElementById('clear-all-templates').addEventListener('click', () => {
      this.clearAllTemplates();
    });
  }

  async handleFileSelect(files) {
    console.log('📁 Files selected:', files.length);

    const xmlFiles = Array.from(files).filter(file => {
      const isXML = file.type === 'text/xml' ||
        file.type === 'application/xml' ||
        file.name.toLowerCase().endsWith('.xml');
      console.log(`📄 File: ${file.name}, Type: ${file.type}, IsXML: ${isXML}`);
      return isXML;
    });

    if (xmlFiles.length === 0) {
      toast.show('Vui lòng chọn file XML hợp lệ', 'error');
      return;
    }

    console.log(`✅ Found ${xmlFiles.length} XML files to upload`);

    for (const file of xmlFiles) {
      await this.uploadTemplate(file);
    }
  }

  async uploadTemplate(file) {
    if (!this.githubToken) {
      toast.show('❌ Cần GitHub Token để upload', 'error');
      return;
    }

    try {
      // Show progress
      this.showUploadProgress(file.name);

      // Read file content
      const content = await this.readFileAsBase64(file);
      
      // GitHub API upload
      const fileName = file.name;
      const path = `${GITHUB_CONFIG.templatesPath}/${fileName}`;
      
      const uploadData = {
        message: `Upload XML template: ${fileName}`,
        content: content,
        branch: 'main'
      };

      const response = await fetch(
        `${GITHUB_CONFIG.apiBase}/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${path}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `token ${this.githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(uploadData)
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const result = await response.json();

      // Add to templates list
      const template = {
        name: fileName,
        path: result.content.path,
        sha: result.content.sha,
        size: result.content.size,
        downloadURL: result.content.download_url,
        uploadedAt: new Date().toISOString(),
        lastModified: new Date().toISOString()
      };

      this.templates.push(template);

      // Update UI
      this.renderTemplates();
      this.updateStats();

      // Hide progress
      this.hideUploadProgress();

      toast.show(`✅ Đã upload thành công: ${fileName}`, 'success');

      // Log upload event
      this.logUploadEvent(fileName, file.size);

    } catch (error) {
      console.error('Upload error:', error);
      this.hideUploadProgress();
      toast.show(`❌ Upload thất bại: ${file.name} - ${error.message}`, 'error');
    }
  }

  async loadTemplates() {
    try {
      const templatesList = document.getElementById('templates-list');
      templatesList.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p class="mt-2">Đang tải templates từ GitHub...</p>
                </div>
            `;

      // GitHub API to list files
      const response = await fetch(
        `${GITHUB_CONFIG.apiBase}/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${GITHUB_CONFIG.templatesPath}`,
        {
          headers: {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Hide4-Control-Dashboard/3.0'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      this.templates = [];

      if (Array.isArray(data)) {
        for (const item of data) {
          if (item.name.endsWith('.xml')) {
            const template = {
              name: item.name,
              path: item.path,
              sha: item.sha,
              size: item.size,
              downloadURL: item.download_url,
              uploadedAt: item.created_at || new Date().toISOString(),
              lastModified: item.updated_at || new Date().toISOString()
            };

            this.templates.push(template);
          }
        }
      }

      // Sort by upload date (newest first)
      this.templates.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));

      this.renderTemplates();
      this.updateStats();

    } catch (error) {
      console.error('Error loading templates:', error);
      document.getElementById('templates-list').innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <p>❌ Lỗi tải templates: ${error.message}</p>
                    <p class="text-sm mt-2">Kiểm tra kết nối internet và thử lại</p>
                </div>
            `;
    }
  }

  renderTemplates() {
    const templatesList = document.getElementById('templates-list');

    if (this.templates.length === 0) {
      templatesList.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span class="text-2xl">📄</span>
                    </div>
                    <p class="text-lg font-medium">Chưa có templates nào</p>
                    <p class="text-sm">Upload XML template đầu tiên của bạn</p>
                </div>
            `;
      return;
    }

    templatesList.innerHTML = this.templates.map(template => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <span class="text-blue-600 text-lg">📄</span>
                        </div>
                        <div>
                            <h4 class="font-medium text-gray-900">${template.name}</h4>
                            <div class="flex items-center space-x-4 text-sm text-gray-500">
                                <span>📏 ${this.formatFileSize(template.size)}</span>
                                <span>📅 ${firebaseUtils.formatTimestamp(template.uploadedAt)}</span>
                                <span>🔗 GitHub</span>
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="templatesManager.downloadTemplate('${template.downloadURL}', '${template.name}')"
                                class="bg-green-100 text-green-700 px-3 py-1 rounded-md hover:bg-green-200 transition-colors text-sm">
                            📥 Download
                        </button>
                        <button onclick="templatesManager.previewTemplate('${template.downloadURL}', '${template.name}')"
                                class="bg-blue-100 text-blue-700 px-3 py-1 rounded-md hover:bg-blue-200 transition-colors text-sm">
                            👁️ Preview
                        </button>
                        ${this.githubToken ? `
                        <button onclick="templatesManager.deleteTemplate('${template.path}', '${template.name}', '${template.sha}')"
                                class="bg-red-100 text-red-700 px-3 py-1 rounded-md hover:bg-red-200 transition-colors text-sm">
                            🗑️ Xóa
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
  }

  async downloadTemplate(downloadURL, displayName) {
    try {
      // Create download link
      const link = document.createElement('a');
      link.href = downloadURL;
      link.download = displayName;
      link.click();

      toast.show(`📥 Đang tải: ${displayName}`, 'success');

    } catch (error) {
      console.error('Download error:', error);
      toast.show(`❌ Tải thất bại: ${displayName}`, 'error');
    }
  }

  async previewTemplate(downloadURL, fileName) {
    try {
      // Open in new tab
      window.open(downloadURL, '_blank');
      toast.show(`👁️ Đang mở preview: ${fileName}`, 'info');

    } catch (error) {
      console.error('Preview error:', error);
      toast.show(`❌ Không thể preview: ${fileName}`, 'error');
    }
  }

  async deleteTemplate(path, displayName, sha) {
    if (!this.githubToken) {
      toast.show('❌ Cần GitHub Token để xóa', 'error');
      return;
    }

    if (!confirm(`Bạn có chắc muốn xóa template "${displayName}"?`)) {
      return;
    }

    try {
      const deleteData = {
        message: `Delete XML template: ${displayName}`,
        sha: sha,
        branch: 'main'
      };

      const response = await fetch(
        `${GITHUB_CONFIG.apiBase}/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${path}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `token ${this.githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(deleteData)
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      // Remove from local list
      this.templates = this.templates.filter(t => t.path !== path);

      // Update UI
      this.renderTemplates();
      this.updateStats();

      toast.show(`🗑️ Đã xóa: ${displayName}`, 'success');

      // Log delete event
      this.logDeleteEvent(displayName);

    } catch (error) {
      console.error('Delete error:', error);
      toast.show(`❌ Xóa thất bại: ${displayName} - ${error.message}`, 'error');
    }
  }

  async clearAllTemplates() {
    if (!this.githubToken) {
      toast.show('❌ Cần GitHub Token để xóa', 'error');
      return;
    }

    if (!confirm('Bạn có chắc muốn xóa TẤT CẢ templates? Hành động này không thể hoàn tác!')) {
      return;
    }

    try {
      let deletedCount = 0;
      const errors = [];

      for (const template of this.templates) {
        try {
          const deleteData = {
            message: `Delete XML template: ${template.name}`,
            sha: template.sha,
            branch: 'main'
          };

          const response = await fetch(
            `${GITHUB_CONFIG.apiBase}/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${template.path}`,
            {
              method: 'DELETE',
              headers: {
                'Authorization': `token ${this.githubToken}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(deleteData)
            }
          );

          if (response.ok) {
            deletedCount++;
          } else {
            const errorData = await response.json();
            errors.push(`${template.name}: ${errorData.message}`);
          }
        } catch (error) {
          errors.push(`${template.name}: ${error.message}`);
        }
      }

      this.templates = [];
      this.renderTemplates();
      this.updateStats();

      if (errors.length === 0) {
        toast.show(`🗑️ Đã xóa ${deletedCount} templates`, 'success');
      } else {
        toast.show(`⚠️ Xóa ${deletedCount}/${this.templates.length} templates. Có ${errors.length} lỗi`, 'warning');
      }

      // Log clear event
      this.logClearEvent();

    } catch (error) {
      console.error('Clear all error:', error);
      toast.show('❌ Xóa tất cả thất bại', 'error');
    }
  }

  updateStats() {
    // Total templates
    document.getElementById('total-templates').textContent = this.templates.length;

    // Last update
    if (this.templates.length > 0) {
      const lastUpdate = this.templates[0].uploadedAt;
      document.getElementById('last-update').textContent = firebaseUtils.getRelativeTime(lastUpdate);
    } else {
      document.getElementById('last-update').textContent = 'Chưa có';
    }

    // Storage used
    const totalSize = this.templates.reduce((sum, template) => sum + template.size, 0);
    document.getElementById('storage-used').textContent = this.formatFileSize(totalSize);

    // Syncing machines (placeholder - will be updated from database)
    document.getElementById('syncing-machines').textContent = '-';
  }

  showUploadProgress(fileName) {
    const progressDiv = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    progressDiv.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressText.textContent = `Đang upload: ${fileName}`;

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress > 90) progress = 90;
      progressBar.style.width = `${progress}%`;
    }, 200);

    // Store interval for cleanup
    this.uploadInterval = interval;
  }

  hideUploadProgress() {
    const progressDiv = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');

    if (this.uploadInterval) {
      clearInterval(this.uploadInterval);
      this.uploadInterval = null;
    }

    progressBar.style.width = '100%';
    setTimeout(() => {
      progressDiv.classList.add('hidden');
    }, 1000);
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        // Remove data URL prefix (data:text/xml;base64,)
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async logUploadEvent(fileName, fileSize) {
    try {
      const logData = {
        event: 'TEMPLATE_UPLOADED',
        template_name: fileName,
        file_size: fileSize,
        timestamp: firebaseUtils.getTimestamp(),
        source: 'webapp',
        storage: 'github'
      };

      const logsRef = ref(database, 'logs');
      await push(logsRef, logData);

    } catch (error) {
      console.error('Log upload event error:', error);
    }
  }

  async logDeleteEvent(fileName) {
    try {
      const logData = {
        event: 'TEMPLATE_DELETED',
        template_name: fileName,
        timestamp: firebaseUtils.getTimestamp(),
        source: 'webapp',
        storage: 'github'
      };

      const logsRef = ref(database, 'logs');
      await push(logsRef, logData);

    } catch (error) {
      console.error('Log delete event error:', error);
    }
  }

  async logClearEvent() {
    try {
      const logData = {
        event: 'TEMPLATES_CLEARED',
        timestamp: firebaseUtils.getTimestamp(),
        source: 'webapp',
        storage: 'github'
      };

      const logsRef = ref(database, 'logs');
      await push(logsRef, logData);

    } catch (error) {
      console.error('Log clear event error:', error);
    }
  }
}

// Initialize templates manager
const templatesManager = new GitHubTemplatesManager();

// Make it globally available for onclick handlers
window.templatesManager = templatesManager;