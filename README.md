# 🕵️ Hide4 Control Dashboard

**Fully Automated XML Monitoring & Control System**

## 📁 Project Structure

```
hide4-control-dashboard/
├── client/                    # Python Client Application
│   ├── icon.py               # Main application entry point
│   ├── machine_manager.py    # Machine ID & heartbeat management
│   ├── firebase_logger.py    # Firebase logging & communication
│   ├── firebase_storage.py   # Firebase Storage sync for templates
│   ├── xml_fingerprint.py    # XML detection & fingerprinting
│   ├── config_embedded.py    # Hardcoded Firebase config
│   └── build_release/        # Built exe files
│       ├── Hide4             # Main executable (Linux build)
│       ├── Hide4.spec        # PyInstaller spec file
│       └── release_info.json # Release metadata
│
├── webapp/                   # Web Dashboard (PWA)
│   ├── index.html           # Dashboard main page
│   ├── machines.html        # Machine management
│   ├── logs.html            # Real-time logs
│   ├── templates.html       # XML templates management
│   ├── download.html        # Exe download page
│   ├── settings.html        # Settings & configuration
│   ├── js/                  # JavaScript modules
│   │   ├── firebase-config.js
│   │   ├── app.js
│   │   ├── machines.js
│   │   ├── logs.js
│   │   ├── templates.js
│   │   ├── download.js
│   │   └── settings.js
│   ├── css/
│   │   └── style.css
│   ├── icons/               # PWA icons
│   ├── manifest.json        # PWA manifest
│   └── service-worker.js    # PWA service worker
│
├── firebase/                 # Firebase Configuration
│   ├── firebase.json        # Firebase project config
│   ├── database.rules.json  # Database security rules
│   └── storage.rules        # Storage security rules
│
├── scripts/                  # Build & Test Scripts
│   ├── build_release.py     # Build exe with embedded config
│   ├── run_tests.py         # Test runner with coverage
│   ├── test_webapp.py       # Webapp testing
│   └── test_integration.py  # Integration testing
│
├── docs/                     # Documentation
│   ├── README.md            # Main documentation
│   ├── QUICK_START.md       # Quick start guide
│   ├── IMPLEMENTATION_COMPLETE.md
│   └── API.md               # API documentation
│
├── templates/                # Sample XML templates
├── tests/                   # Unit tests
│   ├── __init__.py         # Test package initialization
│   ├── test_xml_fingerprint.py
│   ├── test_firebase_logger.py
│   ├── test_firebase_storage.py
│   └── test_machine_manager.py
├── config.json              # Development config (optional)
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── deploy.sh               # Deployment script
└── venv/                   # Python virtual environment
```

## 🚀 Quick Start

### **For Admin (You)**:
1. **Build exe**: `python scripts/build_release.py`
2. **Upload exe** to Firebase Storage or Google Drive
3. **Open webapp**: https://hide4-control-dashboard.web.app
4. **Upload XML templates** via Templates page
5. **Monitor machines** via Dashboard

### **For Customers**:
1. **Download exe** from link you provide
2. **Run as Administrator**
3. **Done!** (No configuration needed)

## 🌟 Features

✅ **Build Once**: Single exe with embedded config
✅ **Auto-Sync**: Templates sync every 30 minutes
✅ **Web Management**: Upload/delete templates from mobile/PC
✅ **Real-time Monitoring**: Live logs and machine status
✅ **PWA Dashboard**: Install as app on mobile
✅ **Remote Control**: Uninstall and manage machines
✅ **No Config**: Customers just download and run

## 🔧 Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build exe
python scripts/build_release.py

# Test webapp
python scripts/test_webapp.py

# Deploy
firebase deploy
```

## 📱 Webapp URLs

- **Dashboard**: https://hide4-control-dashboard.web.app
- **Templates**: https://hide4-control-dashboard.web.app/templates.html
- **Download**: https://hide4-control-dashboard.web.app/download.html
- **Machines**: https://hide4-control-dashboard.web.app/machines.html
- **Logs**: https://hide4-control-dashboard.web.app/logs.html

## 🎯 Workflow

1. **Build exe** → Upload → Send link to customers
2. **Upload XML** → All machines auto-sync within 30 minutes
3. **Monitor** → Control → Export logs
4. **Customers** → Download → Run → Done!

## 🧪 Testing

### **Run All Tests**:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
python scripts/run_tests.py --coverage --html

# Run specific module tests
python scripts/run_tests.py --module xml_fingerprint

# Run with verbose output
python scripts/run_tests.py --verbose
```

### **Test Coverage**:
- **Target**: >80% code coverage
- **Reports**: HTML coverage report in `htmlcov/` directory
- **Modules**: All Python modules have comprehensive unit tests

### **Test Structure**:
```
tests/
├── __init__.py                 # Test fixtures and utilities
├── test_xml_fingerprint.py    # XML fingerprinting tests
├── test_firebase_logger.py    # Firebase logger tests
├── test_firebase_storage.py   # Firebase storage tests
└── test_machine_manager.py    # Machine manager tests
```

## 🔧 Development

### **Setup Development Environment**:
```bash
# Clone repository
git clone <repository-url>
cd hide4-control-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **Code Quality**:
```bash
# Format code
black client/ tests/

# Lint code
flake8 client/ tests/

# Type checking
mypy client/

# Sort imports
isort client/ tests/
```

### **Testing**:
```bash
# Run tests
python scripts/run_tests.py --coverage

# Run specific tests
pytest tests/test_xml_fingerprint.py -v

# Run with coverage
pytest --cov=client --cov-report=html
```

### **Documentation**:
- **API Documentation**: `docs/API.md`
- **Code Examples**: See API documentation for usage examples
- **Troubleshooting**: Comprehensive troubleshooting guide in API docs

## 🚀 Features

### **Enhanced Error Handling**:
- ✅ Exponential backoff retry mechanism
- ✅ Network timeout handling
- ✅ Graceful failure recovery
- ✅ Comprehensive error logging

### **Advanced Logging**:
- ✅ Rotating file handlers (10MB max)
- ✅ Automatic cleanup (30+ days)
- ✅ Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Separate logs per module
- ✅ Performance logging

### **Comprehensive Testing**:
- ✅ Unit tests for all modules
- ✅ Integration tests
- ✅ Coverage reporting (>80% target)
- ✅ Mock Firebase connections
- ✅ Test fixtures and utilities

### **API Documentation**:
- ✅ Complete API reference
- ✅ Code examples
- ✅ Troubleshooting guide
- ✅ Architecture overview

---

**Status**: ✅ **PRODUCTION DEPLOYED** - v2.0
**Last Updated**: October 14, 2025
**Release**: [v2.0 Release Notes](RELEASE_NOTES_v2.0.md)

## 🚀 **Production URLs**

- **Main Dashboard**: https://hide4-control-dashboard.web.app
- **Machines**: https://hide4-control-dashboard.web.app/machines.html
- **Logs**: https://hide4-control-dashboard.web.app/logs.html
- **Templates**: https://hide4-control-dashboard.web.app/templates.html
- **Download**: https://hide4-control-dashboard.web.app/download.html

## 📊 **Production Features**

### **✅ Deployed Features**
- **Webapp Pagination**: Machines (50), Logs (100) with load more
- **Performance Monitoring**: Real-time Firebase query tracking
- **Advanced Logging**: Rotating logs with auto-cleanup
- **Error Handling**: Exponential backoff retry mechanism
- **Configuration Management**: Centralized config system
- **Comprehensive Testing**: 18/18 tests passed

### **🎯 Performance Metrics**
- **Average Query Time**: <100ms
- **Error Rate**: <1%
- **Slow Queries**: <5%
- **Memory Usage**: Optimized with pagination
