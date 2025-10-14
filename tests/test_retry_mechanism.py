# tests/test_retry_mechanism.py - Test retry mechanism

import sys
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_firebase_logger_retry():
    """Test Firebase Logger retry mechanism"""
    try:
        from client.firebase_logger import FirebaseLogger

        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        # Mock requests to fail first 2 times, succeed on 3rd
        mock_responses = [
            Mock(side_effect=Exception("Network error")),
            Mock(side_effect=Exception("Network error")),
            Mock(json=lambda: {'success': True}, content=b'{"success": true}')
        ]

        with patch('requests.get') as mock_get:
            mock_get.side_effect = mock_responses

            with patch('time.sleep'):  # Skip actual sleep
                result = fl._make_request_with_retry('GET', 'test/path', max_retries=3)

                if result and result.get('success'):
                    print("✅ Firebase Logger retry mechanism working")
                    return True
                else:
                    print(f"❌ Firebase Logger retry failed: {result}")
                    return False

    except Exception as e:
        print(f"❌ Firebase Logger retry test failed: {e}")
        return False

def test_firebase_storage_retry():
    """Test Firebase Storage retry mechanism"""
    try:
        from client.firebase_storage import FirebaseStorageSync

        fs = FirebaseStorageSync()

        # Mock requests to fail first 2 times, succeed on 3rd
        mock_responses = [
            Mock(side_effect=Exception("Network error")),
            Mock(side_effect=Exception("Network error")),
            Mock(json=lambda: {'items': []}, content=b'{"items": []}')
        ]

        with patch('requests.get') as mock_get:
            mock_get.side_effect = mock_responses

            with patch('time.sleep'):  # Skip actual sleep
                result = fs._make_request_with_retry('https://test.com', 'GET', max_retries=3)

                if result and hasattr(result, 'json'):
                    print("✅ Firebase Storage retry mechanism working")
                    return True
                else:
                    print(f"❌ Firebase Storage retry failed: {result}")
                    return False

    except Exception as e:
        print(f"❌ Firebase Storage retry test failed: {e}")
        return False

def test_retry_exponential_backoff():
    """Test exponential backoff timing"""
    try:
        from client.firebase_logger import FirebaseLogger

        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        sleep_times = []

        def mock_sleep(seconds):
            sleep_times.append(seconds)

        with patch('requests.get', side_effect=Exception("Network error")):
            with patch('time.sleep', side_effect=mock_sleep):
                result = fl._make_request_with_retry('GET', 'test/path', max_retries=3)

                # Check exponential backoff: 1s, 2s
                expected_times = [1, 2]  # 2^0, 2^1
                if sleep_times == expected_times:
                    print("✅ Exponential backoff timing correct")
                    return True
                else:
                    print(f"❌ Exponential backoff timing incorrect: {sleep_times}")
                    return False

    except Exception as e:
        print(f"❌ Exponential backoff test failed: {e}")
        return False

def test_retry_max_attempts():
    """Test retry max attempts"""
    try:
        from client.firebase_logger import FirebaseLogger

        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        call_count = 0

        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("Network error")

        with patch('requests.get', side_effect=mock_get):
            with patch('time.sleep'):  # Skip actual sleep
                result = fl._make_request_with_retry('GET', 'test/path', max_retries=3)

                if call_count == 3 and result is None:
                    print("✅ Max retry attempts working correctly")
                    return True
                else:
                    print(f"❌ Max retry attempts failed: {call_count} calls, result: {result}")
                    return False

    except Exception as e:
        print(f"❌ Max retry attempts test failed: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Retry Mechanism...")
    print("=" * 50)

    tests = [
        test_firebase_logger_retry,
        test_firebase_storage_retry,
        test_retry_exponential_backoff,
        test_retry_max_attempts
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
        print("🎉 All retry mechanism tests passed!")
    else:
        print("💥 Some retry mechanism tests failed!")
        sys.exit(1)
