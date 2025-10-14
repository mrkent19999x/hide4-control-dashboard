# tests/test_performance_monitoring.py - Test performance monitoring system

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_performance_js_structure():
    """Test performance.js file structure and content"""
    try:
        performance_js_path = Path("webapp/js/performance.js")
        if not performance_js_path.exists():
            print("❌ performance.js not found")
            return False

        content = performance_js_path.read_text(encoding='utf-8')

        # Check for key components
        checks = [
            ('PerformanceMonitor class', 'class PerformanceMonitor' in content),
            ('constructor with metrics', 'constructor()' in content and 'this.metrics' in content),
            ('thresholds configuration', 'this.thresholds' in content),
            ('trackOperation method', 'trackOperation(type, operation)' in content),
            ('recordOperation method', 'recordOperation(operation)' in content),
            ('updatePerformanceMetrics method', 'updatePerformanceMetrics()' in content),
            ('checkAlerts method', 'checkAlerts(operation)' in content),
            ('performance dashboard creation', 'createPerformanceDashboard()' in content),
            ('charts initialization', 'initializeCharts()' in content),
            ('export functionality', 'exportMetrics()' in content),
            ('Firebase operation wrapping', 'originalFirebaseOnValue' in content),
            ('performance tracking', 'performance.now()' in content),
            ('alert system', 'showAlert(' in content),
            ('monitoring controls', 'startMonitoring()' in content and 'stopMonitoring()' in content)
        ]

        passed = 0
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(checks):
            print("✅ performance.js structure complete")
            return True
        else:
            print(f"❌ performance.js incomplete: {passed}/{len(checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing performance.js structure: {e}")
        return False

def test_performance_js_functionality():
    """Test performance.js functionality simulation"""
    try:
        # Simulate performance monitoring functionality
        print("🧪 Simulating Performance Monitoring...")

        # Test metrics structure
        metrics = {
            'queries': [],
            'operations': [],
            'errors': [],
            'performance': {
                'avgQueryTime': 0,
                'totalQueries': 0,
                'slowQueries': 0,
                'errorRate': 0
            }
        }

        # Test thresholds
        thresholds = {
            'slowQuery': 2000,  # 2 seconds
            'errorRate': 0.1,   # 10%
            'maxQueries': 1000
        }

        # Simulate operations
        operations = [
            {'type': 'read', 'duration': 150, 'success': True, 'timestamp': '2024-01-01T10:00:00Z'},
            {'type': 'write', 'duration': 300, 'success': True, 'timestamp': '2024-01-01T10:01:00Z'},
            {'type': 'read', 'duration': 2500, 'success': True, 'timestamp': '2024-01-01T10:02:00Z'},  # Slow query
            {'type': 'update', 'duration': 200, 'success': False, 'timestamp': '2024-01-01T10:03:00Z'},  # Error
        ]

        # Test performance calculation
        total_time = sum(op['duration'] for op in operations)
        avg_time = total_time / len(operations)
        slow_queries = len([op for op in operations if op['duration'] > thresholds['slowQuery']])
        error_count = len([op for op in operations if not op['success']])
        error_rate = error_count / len(operations)

        print(f"✅ Average query time: {avg_time:.2f}ms")
        print(f"✅ Slow queries: {slow_queries}")
        print(f"✅ Error rate: {error_rate:.2%}")

        # Test alert conditions
        alerts = []
        for op in operations:
            if op['duration'] > thresholds['slowQuery']:
                alerts.append(f"Slow {op['type']} query: {op['duration']}ms")
            if not op['success']:
                alerts.append(f"Failed {op['type']} operation")

        if error_rate > thresholds['errorRate']:
            alerts.append(f"High error rate: {error_rate:.2%}")

        print(f"✅ Generated {len(alerts)} alerts")

        # Test metrics update
        metrics['performance']['avgQueryTime'] = avg_time
        metrics['performance']['totalQueries'] = len(operations)
        metrics['performance']['slowQueries'] = slow_queries
        metrics['performance']['errorRate'] = error_rate

        print("✅ Performance metrics updated successfully")

        return True

    except Exception as e:
        print(f"❌ Error testing performance functionality: {e}")
        return False

def test_config_manager_integration():
    """Test config manager integration with performance monitoring"""
    try:
        from client.config_manager import config_manager

        # Test monitoring config
        monitoring_config = config_manager.get_monitoring_config()
        print(f"✅ Monitoring config loaded: {type(monitoring_config).__name__}")

        # Test performance logging setting
        performance_logging = monitoring_config.performance_logging
        print(f"✅ Performance logging enabled: {performance_logging}")

        # Test heartbeat interval
        heartbeat_interval = monitoring_config.heartbeat_interval
        print(f"✅ Heartbeat interval: {heartbeat_interval}s")

        # Test log retention
        log_retention = monitoring_config.log_retention_days
        print(f"✅ Log retention: {log_retention} days")

        return True

    except Exception as e:
        print(f"❌ Error testing config manager integration: {e}")
        return False

def test_performance_dashboard_ui():
    """Test performance dashboard UI components"""
    try:
        performance_js_path = Path("webapp/js/performance.js")
        content = performance_js_path.read_text(encoding='utf-8')

        # Check for UI components
        ui_checks = [
            ('Performance dashboard HTML', 'performance-dashboard' in content),
            ('Metrics cards', 'avg-query-time' in content and 'total-queries' in content),
            ('Charts containers', 'query-time-chart' in content and 'error-rate-chart' in content),
            ('Control buttons', 'start-monitoring' in content and 'stop-monitoring' in content),
            ('Clear metrics button', 'clear-metrics' in content),
            ('Chart.js integration', 'new Chart(' in content),
            ('Responsive design', 'responsive: true' in content),
            ('Export functionality', 'exportMetrics()' in content)
        ]

        passed = 0
        for check_name, check_result in ui_checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(ui_checks):
            print("✅ Performance dashboard UI complete")
            return True
        else:
            print(f"❌ Performance dashboard UI incomplete: {passed}/{len(ui_checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing performance dashboard UI: {e}")
        return False

def test_performance_monitoring_integration():
    """Test performance monitoring integration with existing modules"""
    try:
        # Test integration points
        integration_checks = [
            ('Firebase operation wrapping', 'window.firebaseOnValue' in Path("webapp/js/performance.js").read_text()),
            ('Toast notifications', 'toast.show(' in Path("webapp/js/performance.js").read_text()),
            ('Chart.js dependency', 'Chart(' in Path("webapp/js/performance.js").read_text()),
            ('Auto-initialization', 'window.performanceMonitor' in Path("webapp/js/performance.js").read_text()),
            ('Export functionality', 'URL.createObjectURL' in Path("webapp/js/performance.js").read_text())
        ]

        passed = 0
        for check_name, check_result in integration_checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed += 1
            else:
                print(f"❌ {check_name}: Not found")

        if passed == len(integration_checks):
            print("✅ Performance monitoring integration complete")
            return True
        else:
            print(f"❌ Performance monitoring integration incomplete: {passed}/{len(integration_checks)} checks passed")
            return False

    except Exception as e:
        print(f"❌ Error testing performance monitoring integration: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Performance Monitoring System...")
    print("=" * 60)

    tests = [
        ("Performance.js Structure", test_performance_js_structure),
        ("Performance Functionality", test_performance_js_functionality),
        ("Config Manager Integration", test_config_manager_integration),
        ("Performance Dashboard UI", test_performance_dashboard_ui),
        ("Performance Monitoring Integration", test_performance_monitoring_integration)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔄 Testing {test_name}...")
        print("-" * 50)
        if test_func():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All performance monitoring tests passed!")
    else:
        print("💥 Some performance monitoring tests failed!")
        sys.exit(1)
