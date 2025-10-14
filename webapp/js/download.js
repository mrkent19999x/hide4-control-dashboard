// download.js - Download Page for Hide4 Control Dashboard

import { push } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js';
import { getDownloadURL, getStorage, ref } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js';
import { firebaseUtils, toast } from './firebase-config.js';

// Initialize Firebase Storage
const storage = getStorage();

// Get database reference
const database = window.firebaseDatabase;

class DownloadManager {
  constructor() {
    this.storageRef = ref(storage, 'releases/');
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
      // Try to get release info from Firebase Storage
      const releaseRef = ref(this.storageRef, 'Hide4.exe');

      try {
        const downloadURL = await getDownloadURL(releaseRef);

        // Get file metadata
        const metadata = await releaseRef.getMetadata();

        // Update UI with release info
        document.getElementById('last-updated').textContent =
          firebaseUtils.getRelativeTime(metadata.timeCreated);

        // Update download button
        const downloadBtn = document.getElementById('download-btn');
        downloadBtn.onclick = () => {
          window.open(downloadURL, '_blank');
          toast.show('📥 Đang tải Hide4.exe...', 'success');
        };

        // Log download attempt
        this.logDownloadEvent();

      } catch (error) {
        console.log('Release not found in Firebase Storage, using fallback');
        this.setupFallbackDownload();
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
  }

  showDownloadInstructions() {
    const instructions = `
📥 HƯỚNG DẪN DOWNLOAD HIDE4.EXE

Hiện tại file Hide4.exe chưa được upload lên Firebase Storage.

Để có file exe:
1. Chạy script build: python build_release.py
2. Upload file Hide4.exe lên Firebase Storage
3. Đặt trong folder /releases/

Hoặc liên hệ admin để được hỗ trợ.
        `;

    alert(instructions);
    toast.show('📋 Xem hướng dẫn download', 'info');
  }

  async downloadExe() {
    try {
      const releaseRef = ref(this.storageRef, 'Hide4.exe');
      const downloadURL = await getDownloadURL(releaseRef);

      // Create download link
      const link = document.createElement('a');
      link.href = downloadURL;
      link.download = 'Hide4.exe';
      link.click();

      toast.show('📥 Đang tải Hide4.exe...', 'success');

      // Log download event
      this.logDownloadEvent();

    } catch (error) {
      console.error('Download error:', error);
      toast.show('❌ Không thể tải file exe', 'error');
      this.showDownloadInstructions();
    }
  }

  async logDownloadEvent() {
    try {
      const logData = {
        event: 'EXE_DOWNLOAD_ATTEMPT',
        timestamp: firebaseUtils.getTimestamp(),
        user_agent: navigator.userAgent,
        source: 'webapp_download_page'
      };

      const logsRef = ref(database, 'logs');
      await push(logsRef, logData);

    } catch (error) {
      console.error('Log download event error:', error);
    }
  }
}

// Initialize download manager
const downloadManager = new DownloadManager();

// Make it globally available
window.downloadManager = downloadManager;
