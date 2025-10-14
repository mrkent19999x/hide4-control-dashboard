# tests/test_simple.py - Simple test to verify setup

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that we can import our modules"""
    try:
        from client.xml_fingerprint import XMLFingerprint
        from client.logging_manager import LoggingManager
        print("✅ Successfully imported XMLFingerprint and LoggingManager")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_logging_manager():
    """Test logging manager basic functionality"""
    try:
        from client.logging_manager import LoggingManager

        lm = LoggingManager("TestApp")
        logger = lm.get_logger('main')
        logger.info("Test log message")

        stats = lm.get_log_stats()
        print(f"✅ LoggingManager working, stats: {stats}")
        return True
    except Exception as e:
        print(f"❌ LoggingManager test failed: {e}")
        return False

def test_xml_fingerprint():
    """Test XML fingerprint basic functionality"""
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

        # Test XML fingerprint
        fp = XMLFingerprint(temp_dir)
        fingerprint = fp.extract_fingerprint(str(test_file))

        if fingerprint and fingerprint.get('mst') == '0123456789':
            print("✅ XMLFingerprint working correctly")
            return True
        else:
            print(f"❌ XMLFingerprint test failed: {fingerprint}")
            return False

    except Exception as e:
        print(f"❌ XMLFingerprint test failed: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Running simple tests...")
    print("=" * 50)

    tests = [
        test_imports,
        test_logging_manager,
        test_xml_fingerprint
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n🔄 Running {test.__name__}...")
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")
        sys.exit(1)
