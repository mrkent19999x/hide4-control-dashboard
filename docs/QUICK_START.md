# 🚀 HIDE4 CONTROL DASHBOARD - QUICK START GUIDE

## ⚡ Setup nhanh trong 5 phút

### 1️⃣ Tạo Firebase Project
```bash
# Truy cập: https://console.firebase.google.com
# Tạo project: hide4-control-dashboard
# Enable: Realtime Database + Hosting
```

### 2️⃣ Deploy Web Dashboard
```bash
# Chạy script deploy
./deploy.sh

# Hoặc thủ công
firebase deploy --only hosting
```

### 3️⃣ Cấu hình Hide4.exe
```bash
# Copy config mẫu
cp config.json.example config.json

# Chỉnh sửa config.json với Firebase credentials
{
  "firebase": {
    "database_url": "https://hide4-control-dashboard-default-rtdb.firebaseio.com",
    "database_secret": "YOUR_SECRET_HERE"
  }
}
```

### 4️⃣ Test Integration
```bash
# Test Firebase connection
python test_integration.py

# Test gửi log
python icon.py --test-log
```

### 5️⃣ Truy cập Dashboard
🌐 **URL**: https://hide4-control-dashboard.web.app

## 📱 PWA Installation

### Desktop (Chrome/Edge)
1. Mở dashboard URL
2. Click icon "+" trên thanh địa chỉ
3. "Install Hide4 Control Dashboard"

### Mobile (Android/iOS)
1. Mở dashboard URL
2. Menu → "Add to Home Screen"
3. Dashboard sẽ xuất hiện như app

## 🎯 Tính năng chính

### Dashboard
- 📊 Stats realtime: máy online/offline, files đã xử lý
- 📈 Charts: files theo ngày, trạng thái máy
- 🔔 Logs mới nhất (5 logs gần đây)

### Máy
- 📋 Danh sách tất cả máy đã cài Hide4
- 🟢/🔴 Status realtime (online/offline)
- 👁️ Xem chi tiết: hostname, uptime, files processed
- 🗑️ Gửi lệnh gỡ cài đặt từ xa

### Logs
- 📝 Stream logs realtime từ tất cả máy
- 🔍 Filter: theo máy, loại event, thời gian
- 📥 Export logs thành JSON/CSV
- 🔄 Auto-refresh mỗi 5 giây

### Cài đặt
- ⚙️ Cấu hình heartbeat interval
- 🗑️ Xóa logs cũ (theo số ngày)
- 📊 Xem Firebase quota usage
- 📥 Export toàn bộ dữ liệu

## 🔧 Troubleshooting

### Dashboard không load
```bash
# Kiểm tra Firebase config
python test_integration.py

# Kiểm tra Firebase Console
https://console.firebase.google.com/project/hide4-control-dashboard/database
```

### Máy không xuất hiện trên Dashboard
```bash
# Kiểm tra config.json
python icon.py --gui

# Test gửi log
python icon.py --test-log
```

### Lỗi Firebase connection
- Kiểm tra database_url trong config.json
- Kiểm tra database_secret
- Kiểm tra Firebase project settings

## 📊 Firebase Database Structure

```
hide4-control/
├── machines/
│   ├── {machine_id}/
│   │   ├── info: {hostname, install_date, last_active}
│   │   ├── status: {online, heartbeat_time}
│   │   ├── stats: {files_processed, uptime}
│   │   └── commands: {type, params, executed}
│
├── logs/
│   ├── {machine_id}/
│   │   ├── {timestamp}/
│   │   │   ├── event: "PHÁT HIỆN FILE FAKE"
│   │   │   ├── path: "C:\\fake.xml"
│   │   │   ├── fingerprint: {...}
│   │   │   └── timestamp: "..."
```

## 🎉 Hoàn thành!

Bây giờ anh có thể:
- ✅ Xem logs realtime từ tất cả máy
- ✅ Điều khiển máy từ xa qua Web Dashboard
- ✅ Cài đặt PWA trên điện thoại
- ✅ Export logs và dữ liệu
- ✅ Quản lý nhiều máy từ 1 dashboard

**Dashboard URL**: https://hide4-control-dashboard.web.app
