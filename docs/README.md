# Hide4 XML Monitor v3.0 🕵️‍♂️

**Tự động ghi đè file XML fake với template thật - Giám sát toàn hệ thống Windows với Web Dashboard Control**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![Firebase](https://img.shields.io/badge/Firebase-Hosting-orange.svg)](https://firebase.google.com)

## 🎯 **Chức năng chính v3.0**

- ✅ **Phát hiện thông minh**: Sử dụng XML fingerprint (MST, Kỳ, Mã tờ khai) thay vì khớp tên file
- ✅ **Web Dashboard Control**: Điều khiển từ xa qua PWA Web App với giao diện đẹp
- ✅ **Multi-machine Management**: Quản lý nhiều máy từ 1 Web Dashboard
- ✅ **Machine ID & Heartbeat**: Mỗi máy có ID riêng, heartbeat mỗi 5 phút
- ✅ **Giám sát tự động**: Theo dõi tất cả ổ đĩa (A-Z) trên Windows
- ✅ **Chạy ngầm**: Hoạt động không hiện cửa sổ, tự động startup
- ✅ **Báo cáo realtime**: Logs xuất hiện ngay lập tức trên Web Dashboard
- ✅ **PWA Support**: Cài đặt như app trên điện thoại, hoạt động offline

## 🚀 **Cài đặt nhanh**

### **Cách 1: Sử dụng EXE có sẵn (Khuyến nghị)**
1. Tải file `Hide4.exe` từ [Releases](../../releases)
2. Chạy với quyền Administrator
3. Xong! Phần mềm sẽ tự động giám sát

### **Cách 2: Build từ source code**
```bash
# 1. Clone repo
git clone https://github.com/mrkent19999x/Hide4-XML-Monitor.git
cd Hide4-XML-Monitor

# 2. Cài đặt Python 3.11+
# Tải từ: https://python.org/downloads/

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Build EXE
pyinstaller --onefile --noconsole --add-data "templates;templates" --name "Hide4" icon.py

# 5. Chạy file EXE từ thư mục dist/
```

## 📁 **Cấu trúc thư mục**

```
Hide4-XML-Monitor/
├── icon.py                 # File chính
├── requirements.txt        # Dependencies
├── Hide4.bat             # Script chạy Windows
├── templates/            # 📂 Thư mục XML templates
│   ├── ETAX11320250294522551.xml
│   ├── ETAX11320250307811609.xml
│   └── ...
├── dist/                 # File EXE sau khi build
└── README.md            # File này
```

## 🔧 **Cách thêm XML template mới**

### **Bước 1: Chuẩn bị file XML**
- Đặt file XML template vào thư mục `templates/`
- Tên file phải có format: `ETAX1132025XXXXXXXXX.xml`
- Message ID sẽ được tự động extract từ tên file

### **Bước 2: Build lại EXE**
```bash
pyinstaller --onefile --noconsole --add-data "templates;templates" --name "Hide4" icon.py
```

### **Bước 3: Test**
- Chạy EXE mới
- Tạo file XML fake có cùng Message ID
- Kiểm tra xem có được ghi đè không

## 🎮 **Cách sử dụng**

### **Chế độ giám sát (Mặc định)**
```bash
# Chạy EXE
./Hide4.exe

# Hoặc chạy Python script
python icon.py
```

### **Chế độ GUI (Xem templates & log)**
```bash
python icon.py --gui
```

### **Test gửi log**
```bash
python icon.py --test-log
```

## ⚙️ **Cấu hình Firebase Dashboard**

### **Bước 1: Tạo Firebase Project**
1. Truy cập [Firebase Console](https://console.firebase.google.com)
2. Tạo project mới: `hide4-control-dashboard`
3. Enable **Realtime Database** (chọn test mode)
4. Enable **Hosting**
5. Lưu lại **Database URL** và **Project ID**

### **Bước 2: Lấy Firebase Credentials**
1. Vào Project Settings → Service Accounts
2. Generate new private key → Download JSON
3. Hoặc sử dụng Database Secret (Settings → Database)

### **Bước 3: Tạo file config.json**
Copy `config.json.example` thành `config.json` và điền thông tin:
```json
{
  "firebase": {
    "database_url": "https://hide4-control-dashboard-default-rtdb.firebaseio.com",
    "database_secret": "YOUR_FIREBASE_DATABASE_SECRET_HERE"
  },
  "monitoring": {
    "heartbeat_interval": 300,
    "watch_all_drives": true
  }
}
```

### **Bước 4: Deploy Web Dashboard**
```bash
# Deploy dashboard lên Firebase Hosting
./deploy.sh

# Hoặc deploy thủ công
firebase deploy --only hosting
```

### **Bước 5: Test Integration**
```bash
# Test Firebase connection và gửi logs
python test_integration.py

# Test gửi log
python icon.py --test-log

# Chạy GUI để kiểm tra
python icon.py --gui
```

### **Thư mục lưu trữ**
- **Config**: `%APPDATA%\XMLOverwrite\`
- **Log file**: `%APPDATA%\XMLOverwrite\xml_overwrite.log`
- **State**: `%APPDATA%\XMLOverwrite\processed_files.pkl`

## 🔍 **Cách hoạt động v3.0**

1. **Khởi động**:
   - Tạo Machine ID duy nhất (hostname + UUID)
   - Tự thêm vào Windows Startup
   - Khởi động heartbeat (5 phút/lần) gửi lên Firebase

2. **Giám sát**: Theo dõi tất cả ổ đĩa (A-Z) với watchdog

3. **Phát hiện thông minh**: Khi có file XML mới được tạo/rename
   - Extract XML fingerprint: MST, Mã tờ khai, Kiểu kỳ, Kỳ khai, Số lần
   - So khớp với database templates (không cần khớp tên file)

4. **Xử lý**:
   - Tìm template có cùng fingerprint
   - Ghi đè nội dung (giữ thời gian Windows)
   - Gửi log lên Firebase Realtime Database với đầy đủ thông tin

5. **Web Dashboard Control**:
   - Truy cập PWA Web App để xem dashboard
   - Điều khiển từ xa: xem máy, gỡ cài đặt, kiểm tra trạng thái
   - Nhận log realtime khi phát hiện file fake
   - Cài đặt như app trên điện thoại

## 🛠️ **Troubleshooting**

### **Lỗi thường gặp**

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `python not found` | Python chưa cài hoặc không có PATH | Cài lại Python với "Add to PATH" |
| `Module not found` | Thiếu dependencies | `pip install -r requirements.txt` |
| Không giám sát được | Không có quyền Admin | Chạy với quyền Administrator |
| File không được ghi đè | Message ID không khớp | Kiểm tra tên file XML |

### **Debug mode**
```bash
# Xem log chi tiết
python icon.py --gui

# Test gửi log
python icon.py --test-log
```

## 📋 **Requirements v3.0**

- **OS**: Windows 10/11
- **Python**: 3.11+ (nếu build từ source)
- **Dependencies**:
  - `pyinstaller>=6.0.0`
  - `customtkinter>=5.2.0`
  - `watchdog>=3.0.0`
  - `requests>=2.31.0` ⭐ **Firebase REST API**
- **Web Dashboard**:
  - Firebase Hosting (miễn phí)
  - Firebase Realtime Database (miễn phí)
  - Modern browser với PWA support

## 🔒 **Bảo mật**

- ✅ Chạy với quyền Administrator
- ✅ Tự động startup không cần UAC
- ✅ Log được gửi về Firebase Realtime Database
- ✅ Web Dashboard chỉ có anh truy cập (URL bí mật)
- ✅ Không lưu trữ dữ liệu nhạy cảm
- ✅ Firebase Rules có thể cấu hình bảo mật

## 🌐 **Sử dụng Web Dashboard**

### **Truy cập Dashboard**
1. Mở trình duyệt và truy cập: `https://hide4-control-dashboard.web.app`
2. Dashboard sẽ hiển thị realtime:
   - 📊 Tổng số máy online/offline
   - 📈 Biểu đồ files đã xử lý
   - 🔔 Logs mới nhất
   - 🖥️ Danh sách máy hoạt động

### **Cài đặt PWA**
1. Trên desktop: Click icon "+" trên thanh địa chỉ
2. Trên mobile: "Add to Home Screen"
3. Dashboard sẽ hoạt động như app native

### **Các tính năng Dashboard**
- **Dashboard**: Tổng quan hệ thống với charts và stats
- **Máy**: Danh sách tất cả máy, xem chi tiết, gỡ cài đặt
- **Logs**: Xem logs realtime, filter, export
- **Cài đặt**: Cấu hình heartbeat, xóa logs cũ, xuất dữ liệu

### **Điều khiển từ xa**
- Xem trạng thái máy realtime
- Gửi lệnh gỡ cài đặt
- Xem logs chi tiết với fingerprint
- Export logs thành JSON/CSV

## 📞 **Hỗ trợ**

- **Issues**: [GitHub Issues](../../issues)
- **Email**: mrkent19999x@gmail.com
- **Log**: Kiểm tra file log trong `%APPDATA%\XMLOverwrite\`
- **Dashboard**: https://hide4-control-dashboard.web.app

## 📄 **License**

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

**⚠️ Lưu ý**: Phần mềm này chỉ dành cho mục đích giáo dục và nghiên cứu. Người dùng tự chịu trách nhiệm về việc sử dụng.
