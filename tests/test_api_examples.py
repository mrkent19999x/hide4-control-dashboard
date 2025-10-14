# tests/test_api_examples.py - Test API examples from documentation

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_firebase_logger_example():
    """Test Firebase Logger example from API docs"""
    try:
        from client.firebase_logger import firebase_logger

        # Test send_log example
        firebase_logger.send_log("File processed", "/path/to/file.xml", {
            'mst': '0123456789',
            'maTKhai': '01/GTGT'
        })

        print("✅ Firebase Logger example working")
        return True

    except Exception as e:
        print(f"❌ Firebase Logger example failed: {e}")
        return False

def test_firebase_storage_example():
    """Test Firebase Storage example from API docs"""
    try:
        from client.firebase_storage import firebase_storage_sync

        # Test sync templates example
        templates = firebase_storage_sync.get_local_templates()
        print(f"✅ Firebase Storage example working, found {len(templates)} templates")
        return True

    except Exception as e:
        print(f"❌ Firebase Storage example failed: {e}")
        return False

def test_xml_fingerprint_example():
    """Test XML Fingerprint example from API docs"""
    try:
        from client.xml_fingerprint import XMLFingerprint
        import tempfile

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Create test XML file
        test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <mst>0123456789</mst>
    <maTKhai>01/GTGT</maTKhai>
    <kieuKy>Q</kieuKy>
    <kyKKhai>2024Q1</kyKKhai>
</root>'''

        test_file = Path(temp_dir) / "test.xml"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_xml)

        # Test XML fingerprint example
        fp = XMLFingerprint(temp_dir)
        fingerprint = fp.extract_fingerprint(str(test_file))

        if fingerprint and fingerprint['mst'] == '0123456789':
            print("✅ XML Fingerprint example working")
            return True
        else:
            print(f"❌ XML Fingerprint example failed: {fingerprint}")
            return False

    except Exception as e:
        print(f"❌ XML Fingerprint example failed: {e}")
        return False

def test_machine_manager_example():
    """Test Machine Manager example from API docs"""
    try:
        from client.machine_manager import machine_manager

        # Test get machine ID example
        machine_id = machine_manager.get_machine_id()
        print(f"✅ Machine Manager example working, ID: {machine_id}")
        return True

    except Exception as e:
        print(f"❌ Machine Manager example failed: {e}")
        return False

def test_logging_manager_example():
    """Test Logging Manager example from API docs"""
    try:
        from client.logging_manager import get_logger, log_performance

        # Test get logger example
        logger = get_logger('firebase')
        logger.info("Firebase operation completed")

        # Test performance logging example
        log_performance("template_sync", 2.5, {"templates": 10, "size": "5MB"})

        print("✅ Logging Manager example working")
        return True

    except Exception as e:
        print(f"❌ Logging Manager example failed: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing API Examples from Documentation...")
    print("=" * 60)

    tests = [
        test_firebase_logger_example,
        test_firebase_storage_example,
        test_xml_fingerprint_example,
        test_machine_manager_example,
        test_logging_manager_example
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n🔄 Running {test.__name__}...")
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All API examples working correctly!")
    else:
        print("💥 Some API examples failed!")
        sys.exit(1)
