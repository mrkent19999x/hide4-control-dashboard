// download.js - GitHub Releases Download Page for Hide4 Control Dashboard

import { push, ref } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js';
import { firebaseUtils, toast } from './firebase-config.js';

// GitHub Configuration
const GITHUB_CONFIG = {
  owner: 'mrkent19999x',
  repo: 'hide4-control-dashboard',
  apiBase: 'https://api.github.com'
};

// Get database reference
const database = window.firebaseDatabase;

class GitHubDownloadManager {
  constructor() {
    this.releaseInfo = null;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadReleaseInfo();
  }

  setupEventListeners() {
    // Download button click
    document.getElementById('download-btn').addEventListener('click', () => {
      this.downloadExe();
    });
  }

  async loadReleaseInfo() {
    try {
      // Try to get latest release from GitHub
      const response = await fetch(
        `${GITHUB_CONFIG.apiBase}/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/releases/latest?t=${Date.now()}`,
        {
          headers: {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Hide4-Control-Dashboard/3.0'
          },
          cache: 'no-store'
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const release = await response.json();
      this.releaseInfo = release;

      // Find Hide4.exe asset
      const exeAsset = release.assets.find(asset =>
        asset.name.toLowerCase().includes('hide4') &&
        asset.name.toLowerCase().endsWith('.exe')
      );

      if (exeAsset) {
        // Update UI with release info
        document.getElementById('last-updated').textContent =
          firebaseUtils.getRelativeTime(release.published_at);

        document.getElementById('version').textContent = release.tag_name;
        const titleEl = document.getElementById('product-title');
        if (titleEl) titleEl.textContent = `Hide4 XML Monitor ${release.tag_name}`;
        document.getElementById('file-size').textContent = this.formatFileSize(exeAsset.size);

        // Update download button
        const downloadBtn = document.getElementById('download-btn');
        downloadBtn.textContent = `📥 Download ${release.tag_name}`;
        downloadBtn.onclick = () => {
          window.open(exeAsset.browser_download_url, '_blank');
          toast.show('📥 Đang tải Hide4.exe...', 'success');
          this.logDownloadEvent(release.tag_name, exeAsset.size);
        };

        // Show release notes
        this.showReleaseNotes(release);

      } else {
        throw new Error('Hide4.exe not found in release assets');
      }

    } catch (error) {
      console.error('Error loading release info:', error);
      this.setupFallbackDownload();
    }
  }

  setupFallbackDownload() {
    // Fallback: Show instructions for manual download
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.textContent = '📋 Hướng Dẫn Download';
    downloadBtn.onclick = () => {
      this.showDownloadInstructions();
    };

    document.getElementById('last-updated').textContent = 'Chưa có';
    document.getElementById('version').textContent = 'N/A';
    document.getElementById('file-size').textContent = 'N/A';
  }

  showDownloadInstructions() {
    const instructions = `
📥 HƯỚNG DẪN DOWNLOAD HIDE4.EXE

Hiện tại chưa có release trên GitHub.

Để có file exe:
1. Chạy script build: python scripts/build_release.py
2. Upload file Hide4.exe lên GitHub Releases
3. Tag version mới (ví dụ: v3.0.0)

Hoặc liên hệ admin để được hỗ trợ.

GitHub Repository: https://github.com/mrkent19999x/hide4-control-dashboard
        `;

    alert(instructions);
    toast.show('📋 Xem hướng dẫn download', 'info');
  }

  showReleaseNotes(release) {
    const releaseNotesDiv = document.getElementById('release-notes');
    if (releaseNotesDiv && release.body) {
      releaseNotesDiv.innerHTML = `
        <div class="bg-gray-50 rounded-lg p-4">
          <h4 class="font-medium text-gray-900 mb-2">📝 Release Notes (${release.tag_name})</h4>
          <div class="text-sm text-gray-700 whitespace-pre-wrap">${release.body}</div>
        </div>
      `;
    }
  }

  async downloadExe() {
    if (!this.releaseInfo) {
      toast.show('❌ Không có thông tin release', 'error');
      return;
    }

    try {
      // Find Hide4.exe asset
      const exeAsset = this.releaseInfo.assets.find(asset =>
        asset.name.toLowerCase().includes('hide4') &&
        asset.name.toLowerCase().endsWith('.exe')
      );

      if (!exeAsset) {
        throw new Error('Hide4.exe not found in release');
      }

      // Create download link
      const link = document.createElement('a');
      link.href = exeAsset.browser_download_url;
      link.download = exeAsset.name;
      link.click();

      toast.show('📥 Đang tải Hide4.exe...', 'success');

      // Log download event
      this.logDownloadEvent(this.releaseInfo.tag_name, exeAsset.size);

    } catch (error) {
      console.error('Download error:', error);
      toast.show('❌ Không thể tải file exe', 'error');
      this.showDownloadInstructions();
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async logDownloadEvent(version, fileSize) {
    try {
      const logData = {
        event: 'EXE_DOWNLOAD_ATTEMPT',
        version: version,
        file_size: fileSize,
        timestamp: firebaseUtils.getTimestamp(),
        user_agent: navigator.userAgent,
        source: 'webapp_download_page',
        platform: 'github_releases'
      };

      const logsRef = ref(database, 'logs');
      await push(logsRef, logData);

    } catch (error) {
      console.error('Log download event error:', error);
    }
  }
}

// Initialize download manager
const downloadManager = new GitHubDownloadManager();

// Make it globally available
window.downloadManager = downloadManager;
