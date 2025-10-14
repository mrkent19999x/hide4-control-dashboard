# API Documentation - Hide4 Control Dashboard

## Overview

This document provides comprehensive API documentation for the Hide4 Control Dashboard system. The system consists of a Python client application and a web dashboard that work together to monitor and control XML file processing across multiple machines.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Python Client APIs](#python-client-apis)
- [Web Dashboard APIs](#web-dashboard-apis)
- [Firebase Integration](#firebase-integration)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python Client │    │  Firebase DB   │    │  Web Dashboard  │
│   (Hide4.exe)   │◄──►│   (Realtime)    │◄──►│   (PWA)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  XML Monitoring │    │  Firebase       │    │  Real-time      │
│  & Overwriting  │    │  Storage        │    │  Monitoring     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Python Client APIs

### Core Modules

#### 1. FirebaseLogger

**Purpose**: Handles communication with Firebase Realtime Database for logging and status updates.

**Location**: `client/firebase_logger.py`

**Key Methods**:

```python
class FirebaseLogger:
    def __init__(self):
        """Initialize Firebase Logger with embedded or file config"""

    def send_log(self, event: str, path: str = None, fingerprint: Dict = None, once: bool = False):
        """
        Send log event to Firebase

        Args:
            event: Event description
            path: File path (optional)
            fingerprint: XML fingerprint data (optional)
            once: Send only once flag (optional)
        """

    def update_status(self, machine_info: Dict):
        """
        Update machine status in Firebase

        Args:
            machine_info: Dictionary containing machine information
        """

    def send_heartbeat(self, machine_info: Dict):
        """
        Send heartbeat to Firebase

        Args:
            machine_info: Machine information dictionary
        """

    def test_connection(self) -> bool:
        """
        Test Firebase connection

        Returns:
            True if connection successful, False otherwise
        """
```

**Example Usage**:

```python
from client.firebase_logger import firebase_logger

# Send a log event
firebase_logger.send_log("File processed", "/path/to/file.xml", {
    'mst': '0123456789',
    'maTKhai': '01/GTGT'
})

# Update machine status
machine_info = {
    'hostname': 'WORKSTATION-01',
    'install_date': '2024-01-01',
    'files_processed': 150,
    'uptime': '5 days'
}
firebase_logger.update_status(machine_info)

# Test connection
if firebase_logger.test_connection():
    print("Firebase connection OK")
```

#### 2. FirebaseStorageSync

**Purpose**: Manages synchronization of XML templates from Firebase Storage to local cache.

**Location**: `client/firebase_storage.py`

**Key Methods**:

```python
class FirebaseStorageSync:
    def __init__(self):
        """Initialize Firebase Storage sync with default settings"""

    def sync_templates(self) -> bool:
        """
        Sync all templates from Firebase Storage

        Returns:
            True if sync successful, False otherwise
        """

    def get_local_templates(self) -> List[Path]:
        """
        Get list of local template files

        Returns:
            List of Path objects for local XML files
        """

    def start_auto_sync(self, interval: int = None):
        """
        Start automatic sync in background

        Args:
            interval: Sync interval in seconds (default: 1800)
        """

    def force_sync(self) -> bool:
        """
        Force immediate sync (ignore cache)

        Returns:
            True if sync successful, False otherwise
        """
```

**Example Usage**:

```python
from client.firebase_storage import firebase_storage_sync

# Sync templates
if firebase_storage_sync.sync_templates():
    print("Templates synced successfully")

# Get local templates
templates = firebase_storage_sync.get_local_templates()
print(f"Found {len(templates)} local templates")

# Start auto-sync every 30 minutes
firebase_storage_sync.start_auto_sync(1800)
```

#### 3. XMLFingerprint

**Purpose**: Extracts and compares XML fingerprints for template matching.

**Location**: `client/xml_fingerprint.py`

**Key Methods**:

```python
class XMLFingerprint:
    def __init__(self, templates_dir: str):
        """
        Initialize XML Fingerprint with templates directory

        Args:
            templates_dir: Path to templates directory
        """

    def extract_fingerprint(self, xml_path: str) -> Optional[Dict]:
        """
        Extract fingerprint from XML file

        Args:
            xml_path: Path to XML file

        Returns:
            Dictionary with fingerprint data or None if failed
        """

    def find_matching_template(self, xml_path: str) -> Optional[Tuple[str, Dict]]:
        """
        Find matching template for XML file

        Args:
            xml_path: Path to XML file

        Returns:
            Tuple of (template_name, fingerprint) or None if no match
        """

    def get_template_path(self, template_name: str) -> Optional[str]:
        """
        Get file path for template

        Args:
            template_name: Name of template

        Returns:
            File path or None if not found
        """
```

**Example Usage**:

```python
from client.xml_fingerprint import XMLFingerprint

# Initialize with templates directory
fp = XMLFingerprint('/path/to/templates')

# Extract fingerprint from XML
fingerprint = fp.extract_fingerprint('/path/to/file.xml')
if fingerprint:
    print(f"MST: {fingerprint['mst']}")
    print(f"MaTKhai: {fingerprint['maTKhai']}")

# Find matching template
match = fp.find_matching_template('/path/to/file.xml')
if match:
    template_name, template_fp = match
    print(f"Matched template: {template_name}")
```

#### 4. MachineManager

**Purpose**: Manages machine identification and heartbeat functionality.

**Location**: `client/machine_manager.py`

**Key Methods**:

```python
class MachineManager:
    def __init__(self):
        """Initialize Machine Manager"""

    def get_machine_id(self) -> Optional[str]:
        """
        Get machine ID

        Returns:
            Machine ID string or None
        """

    def update_last_active(self):
        """Update last active timestamp"""

    def start_heartbeat(self, firebase_logger=None):
        """
        Start heartbeat thread

        Args:
            firebase_logger: Firebase logger instance
        """

    def get_status(self) -> Dict:
        """
        Get machine status

        Returns:
            Dictionary with machine status information
        """
```

**Example Usage**:

```python
from client.machine_manager import machine_manager

# Get machine ID
machine_id = machine_manager.get_machine_id()
print(f"Machine ID: {machine_id}")

# Start heartbeat
machine_manager.start_heartbeat(firebase_logger)

# Get status
status = machine_manager.get_status()
print(f"Status: {status}")
```

### Logging Manager

**Purpose**: Advanced logging with rotation and cleanup.

**Location**: `client/logging_manager.py`

**Key Methods**:

```python
class LoggingManager:
    def __init__(self, app_name: str = "Hide4"):
        """
        Initialize logging manager

        Args:
            app_name: Application name for logging
        """

    def get_logger(self, module_name: str) -> logging.Logger:
        """
        Get logger for specific module

        Args:
            module_name: Module name (main, firebase, storage, etc.)

        Returns:
            Logger instance
        """

    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """
        Log performance metrics

        Args:
            operation: Operation name
            duration: Duration in seconds
            details: Additional details dictionary
        """
```

**Example Usage**:

```python
from client.logging_manager import get_logger, log_performance

# Get logger for module
logger = get_logger('firebase')
logger.info("Firebase operation completed")

# Log performance
log_performance("template_sync", 2.5, {"templates": 10, "size": "5MB"})
```

## Web Dashboard APIs

### Firebase Integration

The web dashboard uses Firebase JavaScript SDK for real-time communication.

**Key Functions**:

```javascript
// Initialize Firebase
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue, query, limitToLast, orderByChild } from 'firebase/database';

// Load machines with pagination
async function loadMachines(limit = 50) {
    const machinesRef = ref(database, 'machines');
    const q = query(machinesRef, limitToLast(limit));

    return new Promise((resolve) => {
        onValue(q, (snapshot) => {
            const machines = snapshot.val() || {};
            resolve(Object.entries(machines));
        });
    });
}

// Load logs with pagination
async function loadLogs(limit = 100) {
    const logsRef = ref(database, 'logs');
    const q = query(logsRef, limitToLast(limit), orderByChild('timestamp'));

    return new Promise((resolve) => {
        onValue(q, (snapshot) => {
            const logs = snapshot.val() || {};
            resolve(Object.entries(logs));
        });
    });
}
```

### Real-time Listeners

```javascript
// Setup real-time listeners
function setupRealtimeListeners() {
    // Listen for new logs
    const logsRef = ref(database, 'logs');
    onValue(logsRef, (snapshot) => {
        const logs = snapshot.val() || {};
        updateLogsDisplay(logs);
    });

    // Listen for machine status changes
    const machinesRef = ref(database, 'machines');
    onValue(machinesRef, (snapshot) => {
        const machines = snapshot.val() || {};
        updateMachinesDisplay(machines);
    });
}
```

## Firebase Integration

### Database Structure

```
hide4-control-dashboard/
├── logs/
│   └── {machine_id}/
│       └── {timestamp}/
│           ├── event: string
│           ├── timestamp: string
│           ├── machine_id: string
│           ├── path: string
│           └── fingerprint: object
├── machines/
│   └── {machine_id}/
│       ├── info/
│       │   ├── hostname: string
│       │   ├── install_date: string
│       │   └── last_active: string
│       ├── status/
│       │   ├── online: boolean
│       │   ├── last_heartbeat: string
│       │   └── heartbeat_interval: number
│       └── stats/
│           ├── files_processed: number
│           └── uptime: string
└── commands/
    └── {machine_id}/
        └── {command_id}/
            ├── type: string
            ├── params: object
            └── executed: boolean
```

### Storage Structure

```
hide4-control-dashboard.firebasestorage.app/
└── templates/
    ├── template1.xml
    ├── template2.xml
    └── ...
```

## Configuration

### Embedded Configuration

The client uses embedded configuration for zero-config deployment:

```python
# config_embedded.py
FIREBASE_CONFIG = {
    "database_url": "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedatabase.app",
    "project_id": "hide4-control-dashboard",
    "storage_bucket": "hide4-control-dashboard.firebasestorage.app",
    "api_key": "AIzaSyDV-UlVsmtlwNuvqujAegVsCWzo8gSRHqo"
}

MONITORING_CONFIG = {
    "heartbeat_interval": 300,  # 5 minutes
    "watch_all_drives": True,
    "enable_backup": False,
    "auto_sync_interval": 1800  # 30 minutes
}
```

### Development Configuration

For development, use `config.json`:

```json
{
  "firebase": {
    "database_url": "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedatabase.app",
    "database_secret": null
  },
  "monitoring": {
    "heartbeat_interval": 300,
    "watch_all_drives": true,
    "enable_backup": false
  },
  "xml_fingerprint": {
    "required_fields": ["mst", "maTKhai", "kieuKy", "kyKKhai"],
    "optional_fields": ["soLan", "tenTKhai", "tenNNT"]
  },
  "logging": {
    "level": "INFO",
    "max_log_size": "10MB",
    "backup_count": 5
  }
}
```

## Error Handling

### Retry Mechanism

All network operations use exponential backoff retry:

```python
def _make_request_with_retry(self, method: str, path: str, data: Dict = None, max_retries: int = 3):
    """
    Make request with retry mechanism

    Retry schedule:
    - Attempt 1: Immediate
    - Attempt 2: Wait 1 second
    - Attempt 3: Wait 2 seconds
    - Attempt 4: Wait 4 seconds
    """
    for attempt in range(max_retries):
        try:
            # Make request
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts: {e}")
                return None
            else:
                wait_time = 2 ** attempt
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s")
                time.sleep(wait_time)
```

### Error Types

1. **Network Errors**: Connection timeout, DNS resolution failure
2. **Firebase Errors**: Authentication failure, permission denied
3. **File System Errors**: Permission denied, disk full
4. **XML Parsing Errors**: Malformed XML, missing required fields

## Examples

### Complete Client Setup

```python
# icon.py - Main entry point
from firebase_logger import firebase_logger
from firebase_storage import firebase_storage_sync
from machine_manager import machine_manager
from xml_fingerprint import XMLFingerprint
from logging_manager import get_logger

logger = get_logger('main')

def start_monitor():
    """Start monitoring in headless mode"""
    # Initialize machine manager
    machine_manager.update_last_active()

    # Send startup log
    firebase_logger.send_log("Hide4 started", f"Machine: {machine_manager.get_machine_id()}")

    # Sync templates
    firebase_storage_sync.sync_templates()
    firebase_storage_sync.start_auto_sync()

    # Initialize XML fingerprint
    templates_dir = firebase_storage_sync.cache_dir
    handler = DownloadHandler(templates_dir)

    # Start monitoring
    observer = Observer()
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    for d in drives:
        observer.schedule(handler, path=d, recursive=True)

    observer.start()
    machine_manager.start_heartbeat(firebase_logger)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        machine_manager.stop_heartbeat()
        firebase_logger.send_log("Hide4 stopped")
```

### Web Dashboard Integration

```javascript
// app.js - Main dashboard
class DashboardApp {
    constructor() {
        this.database = getDatabase();
        this.machines = new Map();
        this.logs = new Map();
    }

    async init() {
        await this.loadMachines();
        await this.loadLogs();
        this.setupRealtimeListeners();
        this.initCharts();
    }

    async loadMachines(limit = 50) {
        const machinesRef = ref(this.database, 'machines');
        const q = query(machinesRef, limitToLast(limit));

        return new Promise((resolve) => {
            onValue(q, (snapshot) => {
                const machines = snapshot.val() || {};
                this.machines.clear();
                Object.entries(machines).forEach(([id, data]) => {
                    this.machines.set(id, data);
                });
                this.updateMachinesDisplay();
                resolve(machines);
            });
        });
    }

    setupRealtimeListeners() {
        // Listen for new logs
        const logsRef = ref(this.database, 'logs');
        onValue(logsRef, (snapshot) => {
            const logs = snapshot.val() || {};
            this.updateLogsDisplay(logs);
        });

        // Listen for machine status changes
        const machinesRef = ref(this.database, 'machines');
        onValue(machinesRef, (snapshot) => {
            const machines = snapshot.val() || {};
            this.updateMachinesDisplay(machines);
        });
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Firebase Connection Failed

**Symptoms**:
- "Firebase chưa được cấu hình" error
- No logs appearing in dashboard

**Solutions**:
```python
# Check configuration
firebase_logger = FirebaseLogger()
if not firebase_logger.is_configured():
    print("Firebase not configured")
    print(f"URL: {firebase_logger.firebase_url}")
    print(f"Machine ID: {firebase_logger.machine_id}")

# Test connection
if firebase_logger.test_connection():
    print("Connection OK")
else:
    print("Connection failed")
```

#### 2. Template Sync Failed

**Symptoms**:
- No templates in local cache
- "Không tìm thấy templates" error

**Solutions**:
```python
# Check Firebase Storage connection
storage_sync = FirebaseStorageSync()
templates = storage_sync.list_remote_templates()
print(f"Remote templates: {len(templates)}")

# Force sync
if storage_sync.force_sync():
    print("Sync successful")
else:
    print("Sync failed")
```

#### 3. XML Fingerprint Not Working

**Symptoms**:
- "Không tìm thấy template khớp" error
- Templates not matching

**Solutions**:
```python
# Debug fingerprint
fp = XMLFingerprint('/path/to/templates')
debug_info = fp.debug_fingerprint('/path/to/file.xml')
print(debug_info)

# Check template loading
templates = fp.get_all_templates()
print(f"Loaded templates: {templates}")
```

#### 4. Machine Not Appearing in Dashboard

**Symptoms**:
- Machine not visible in web dashboard
- Heartbeat not working

**Solutions**:
```python
# Check machine ID
machine_id = machine_manager.get_machine_id()
print(f"Machine ID: {machine_id}")

# Check heartbeat
machine_manager.start_heartbeat(firebase_logger)
status = machine_manager.get_status()
print(f"Status: {status}")
```

### Debug Mode

Enable debug logging:

```python
from logging_manager import get_logger

# Get debug logger
logger = get_logger('firebase')
logger.setLevel(logging.DEBUG)

# Enable performance logging
from logging_manager import log_performance
log_performance("operation_name", duration, {"key": "value"})
```

### Performance Monitoring

Monitor system performance:

```python
# Check log stats
from logging_manager import logging_manager
stats = logging_manager.get_log_stats()
print(f"Log files: {stats['files']}")
print(f"Total size: {stats['total_size_mb']} MB")

# Cleanup old logs
deleted = logging_manager.cleanup_old_logs(30)
print(f"Deleted {deleted} old log files")
```

### Testing

Run tests to verify functionality:

```bash
# Run all tests
python scripts/run_tests.py --coverage --html

# Run specific module tests
python scripts/run_tests.py --module xml_fingerprint

# Run with verbose output
python scripts/run_tests.py --verbose
```

## Support

For additional support:

1. Check logs in `%APPDATA%\XMLOverwrite\logs\`
2. Run tests: `python scripts/run_tests.py`
3. Check Firebase console for real-time data
4. Verify network connectivity to Firebase

## Version History

- **v1.0**: Initial implementation with basic monitoring
- **v1.1**: Added Firebase Storage sync
- **v1.2**: Added XML fingerprinting
- **v1.3**: Added retry mechanism and advanced logging
- **v1.4**: Added comprehensive testing framework
