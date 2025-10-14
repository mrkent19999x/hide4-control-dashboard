# tests/test_webapp_pagination.py - Test webapp pagination functionality

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_app_js_pagination():
    """Test app.js pagination implementation"""
    try:
        app_js_path = Path("webapp/js/app.js")
        if not app_js_path.exists():
            print("❌ app.js not found")
            return False

        content = app_js_path.read_text(encoding='utf-8')

        # Check for pagination settings
        checks = [
            ('pagination settings', 'pagination: {' in content or 'pagination = {' in content),
            ('machines limit', 'limit: 50' in content),
            ('logs limit', 'limit: 100' in content),
            ('loadMachines method', 'async loadMachines(reset = false)' in content),
            ('loadLogs method', 'async loadLogs(reset = false)' in content),
            ('loadMoreMachines method', 'async loadMoreMachines()' in content),
            ('loadMoreLogs method', 'async loadMoreLogs()' in content),
            ('resetPagination method', 'resetPagination()' in content)
        ]

        passed = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(checks):
            print("✅ app.js pagination implementation complete")
            return True
        else:
            print(f"❌ app.js pagination incomplete: {passed}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing app.js: {e}")
        return False

def test_machines_js_pagination():
    """Test machines.js pagination implementation"""
    try:
        machines_js_path = Path("webapp/js/machines.js")
        if not machines_js_path.exists():
            print("❌ machines.js not found")
            return False

        content = machines_js_path.read_text(encoding='utf-8')

        # Check for pagination features
        checks = [
            ('pagination settings', 'pagination: {' in content or 'pagination = {' in content),
            ('limit setting', 'limit: 50' in content),
            ('search and filter', 'searchTerm' in content and 'statusFilter' in content),
            ('loadMachines method', 'async loadMachines(reset = false)' in content),
            ('filterMachines method', 'filterMachines(machinesArray)' in content),
            ('loadMoreMachines method', 'async loadMoreMachines()' in content),
            ('updatePaginationControls method', 'updatePaginationControls()' in content),
            ('pagination info display', 'pagination-info' in content)
        ]

        passed = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(checks):
            print("✅ machines.js pagination implementation complete")
            return True
        else:
            print(f"❌ machines.js pagination incomplete: {passed}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing machines.js: {e}")
        return False

def test_logs_js_pagination():
    """Test logs.js pagination implementation"""
    try:
        logs_js_path = Path("webapp/js/logs.js")
        if not logs_js_path.exists():
            print("❌ logs.js not found")
            return False

        content = logs_js_path.read_text(encoding='utf-8')

        # Check for pagination features
        checks = [
            ('pagination settings', 'pagination: {' in content or 'pagination = {' in content),
            ('limit setting', 'limit: 100' in content),
            ('loadLogs method', 'async loadLogs(reset = false)' in content),
            ('filterLogs method', 'filterLogs(logsArray)' in content),
            ('loadMoreLogs method', 'async loadMoreLogs()' in content),
            ('updatePaginationControls method', 'updatePaginationControls()' in content),
            ('date filters', 'dateFrom' in content and 'dateTo' in content),
            ('sorting by timestamp', 'sort((a, b) => new Date(b.timestamp)' in content)
        ]

        passed = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(checks):
            print("✅ logs.js pagination implementation complete")
            return True
        else:
            print(f"❌ logs.js pagination incomplete: {passed}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing logs.js: {e}")
        return False

def test_performance_js():
    """Test performance.js implementation"""
    try:
        performance_js_path = Path("webapp/js/performance.js")
        if not performance_js_path.exists():
            print("❌ performance.js not found")
            return False

        content = performance_js_path.read_text(encoding='utf-8')

        # Check for performance monitoring features
        checks = [
            ('PerformanceMonitor class', 'class PerformanceMonitor' in content),
            ('metrics tracking', 'metrics: {' in content or 'this.metrics' in content),
            ('thresholds setting', 'thresholds: {' in content or 'this.thresholds' in content),
            ('trackOperation method', 'trackOperation(type, operation)' in content),
            ('recordOperation method', 'recordOperation(operation)' in content),
            ('updatePerformanceMetrics method', 'updatePerformanceMetrics()' in content),
            ('checkAlerts method', 'checkAlerts(operation)' in content),
            ('performance dashboard', 'performance-dashboard' in content),
            ('charts initialization', 'initializeCharts()' in content),
            ('export metrics', 'exportMetrics()' in content)
        ]

        passed = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(checks):
            print("✅ performance.js implementation complete")
            return True
        else:
            print(f"❌ performance.js incomplete: {passed}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing performance.js: {e}")
        return False

def test_config_manager():
    """Test config_manager.py implementation"""
    try:
        config_manager_path = Path("client/config_manager.py")
        if not config_manager_path.exists():
            print("❌ config_manager.py not found")
            return False

        content = config_manager_path.read_text(encoding='utf-8')

        # Check for config manager features
        checks = [
            ('ConfigManager class', 'class ConfigManager' in content),
            ('FirebaseConfig dataclass', '@dataclass\nclass FirebaseConfig' in content),
            ('StorageConfig dataclass', '@dataclass\nclass StorageConfig' in content),
            ('MonitoringConfig dataclass', '@dataclass\nclass MonitoringConfig' in content),
            ('AppConfig dataclass', '@dataclass\nclass AppConfig' in content),
            ('XMLFingerprintConfig dataclass', '@dataclass\nclass XMLFingerprintConfig' in content),
            ('load_config method', 'def load_config(self)' in content),
            ('get_config method', 'def get_config(self, section' in content),
            ('update_config method', 'def update_config(self, section' in content),
            ('save_config method', 'def save_config(self, file_path' in content),
            ('environment variables support', 'os.getenv(' in content),
            ('configuration validation', '_validate_config' in content)
        ]

        passed = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(checks):
            print("✅ config_manager.py implementation complete")
            return True
        else:
            print(f"❌ config_manager.py incomplete: {passed}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing config_manager.py: {e}")
        return False

def test_config_manager_functionality():
    """Test config_manager.py functionality"""
    try:
        from client.config_manager import config_manager

        # Test configuration loading
        config = config_manager.get_config()
        print("✅ Configuration loaded successfully")

        # Test individual configs
        firebase_config = config_manager.get_firebase_config()
        print(f"✅ Firebase config: {type(firebase_config).__name__}")

        storage_config = config_manager.get_storage_config()
        print(f"✅ Storage config: {type(storage_config).__name__}")

        monitoring_config = config_manager.get_monitoring_config()
        print(f"✅ Monitoring config: {type(monitoring_config).__name__}")

        app_config = config_manager.get_app_config()
        print(f"✅ App config: {type(app_config).__name__}")

        xml_config = config_manager.get_xml_fingerprint_config()
        print(f"✅ XML Fingerprint config: {type(xml_config).__name__}")

        # Test config summary
        summary = config_manager.get_config_summary()
        print(f"✅ Config summary: {summary}")

        # Test config validation
        is_valid = config_manager.is_config_valid()
        print(f"✅ Config validation: {'Valid' if is_valid else 'Invalid'}")

        return True

    except Exception as e:
        print(f"❌ Error testing config_manager functionality: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Webapp Pagination & Performance Monitoring...")
    print("=" * 70)

    tests = [
        ("App.js Pagination", test_app_js_pagination),
        ("Machines.js Pagination", test_machines_js_pagination),
        ("Logs.js Pagination", test_logs_js_pagination),
        ("Performance.js", test_performance_js),
        ("Config Manager Implementation", test_config_manager),
        ("Config Manager Functionality", test_config_manager_functionality)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔄 Testing {test_name}...")
        print("-" * 50)
        if test_func():
            passed += 1
        print()

    print("=" * 70)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All webapp pagination and performance monitoring tests passed!")
    else:
        print("💥 Some tests failed!")
        sys.exit(1)
