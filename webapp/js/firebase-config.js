// Firebase Configuration
// This file will be updated with actual Firebase credentials after project setup

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getDatabase, limitToLast, onValue, orderByChild, push, query, ref, remove, set } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js';

// Firebase configuration - REAL VALUES FROM FIREBASE PROJECT
const firebaseConfig = {
  apiKey: "AIzaSyDV-UlVsmtlwNuvqujAegVsCWzo8gSRHqo",
  authDomain: "hide4-control-dashboard.firebaseapp.com",
  databaseURL: "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "hide4-control-dashboard",
  storageBucket: "hide4-control-dashboard.firebasestorage.app",
  messagingSenderId: "436134439293",
  appId: "1:436134439293:web:d310be5b839aa4971c0414",
  measurementId: "G-NKGYBCH1XK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// Export database reference for use in other modules
window.firebaseDatabase = database;
window.firebaseRef = ref;
window.firebaseOnValue = onValue;
window.firebasePush = push;
window.firebaseSet = set;
window.firebaseRemove = remove;
window.firebaseQuery = query;
window.firebaseOrderByChild = orderByChild;
window.firebaseLimitToLast = limitToLast;

// Connection status monitoring
let isConnected = false;

// Monitor connection status
const connectedRef = ref(database, '.info/connected');
onValue(connectedRef, (snapshot) => {
  isConnected = snapshot.val();
  updateConnectionStatus(isConnected);
});

function updateConnectionStatus(connected) {
  const statusElement = document.getElementById('connection-status');
  const textElement = document.getElementById('connection-text');

  if (statusElement && textElement) {
    if (connected) {
      statusElement.className = 'w-3 h-3 bg-green-500 rounded-full';
      textElement.textContent = 'Đã kết nối';
    } else {
      statusElement.className = 'w-3 h-3 bg-red-500 rounded-full animate-pulse';
      textElement.textContent = 'Mất kết nối';
    }
  }
}

// Utility functions
export const firebaseUtils = {
  // Get current timestamp
  getTimestamp: () => new Date().toISOString(),

  // Format timestamp for display
  formatTimestamp: (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  },

  // Get relative time (e.g., "2 phút trước")
  getRelativeTime: (timestamp) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Vừa xong';
    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    return `${diffDays} ngày trước`;
  },

  // Check if machine is online (heartbeat within last 10 minutes)
  isMachineOnline: (lastHeartbeat) => {
    if (!lastHeartbeat) return false;
    const now = new Date();
    const heartbeat = new Date(lastHeartbeat);
    const diffMs = now - heartbeat;
    return diffMs < 10 * 60 * 1000; // 10 minutes
  },

  // Generate unique ID
  generateId: () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }
};

// Toast notification system
export const toast = {
  show: (message, type = 'info', duration = 3000) => {
    const toastElement = document.createElement('div');
    toastElement.className = `toast ${type}`;
    toastElement.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    ${getToastIcon(type)}
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

    document.body.appendChild(toastElement);

    // Trigger animation
    setTimeout(() => toastElement.classList.add('show'), 100);

    // Auto remove
    setTimeout(() => {
      toastElement.classList.remove('show');
      setTimeout(() => toastElement.remove(), 300);
    }, duration);
  }
};

function getToastIcon(type) {
  const icons = {
    success: '<svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
    error: '<svg class="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
    warning: '<svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
    info: '<svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
  };
  return icons[type] || icons.info;
}

// Export connection status
export { isConnected };
