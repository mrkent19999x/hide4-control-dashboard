# tests/test_firebase_logger.py - Unit Tests for Firebase Logger

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
from datetime import datetime

# Import the module under test
from client.firebase_logger import FirebaseLogger
from tests import (
    setup_test_environment,
    cleanup_test_environment,
    create_test_config_file,
    mock_firebase_response
)

class TestFirebaseLogger:
    """Test cases for FirebaseLogger class"""

    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = setup_test_environment()

    def teardown_method(self):
        """Cleanup after each test method"""
        cleanup_test_environment()

    def test_init_with_embedded_config(self):
        """Test initialization with embedded config"""
        with patch('client.firebase_logger.FIREBASE_CONFIG', {'database_url': 'https://test.firebase.com'}):
            with patch('client.firebase_logger.USE_EMBEDDED_CONFIG', True):
                with patch('client.firebase_logger.logger') as mock_logger:
                    fl = FirebaseLogger()

                    assert fl.firebase_url == 'https://test.firebase.com'
                    assert fl.firebase_secret is None
                    mock_logger.info.assert_called_with("✅ Sử dụng embedded Firebase config")

    def test_init_with_file_config(self):
        """Test initialization with file config"""
        config_data = {
            'firebase': {
                'database_url': 'https://test.firebase.com',
                'database_secret': 'test_secret'
            }
        }
        config_file = create_test_config_file(config_data)

        with patch('client.firebase_logger.USE_EMBEDDED_CONFIG', False):
            with patch('client.firebase_logger.CONFIG_FILE', Path(config_file)):
                with patch('client.firebase_logger.logger') as mock_logger:
                    fl = FirebaseLogger()

                    assert fl.firebase_url == 'https://test.firebase.com'
                    assert fl.firebase_secret == 'test_secret'

    def test_init_without_config(self):
        """Test initialization without config"""
        with patch('client.firebase_logger.USE_EMBEDDED_CONFIG', False):
            with patch('client.firebase_logger.CONFIG_FILE', Path('/nonexistent/config.json')):
                with patch('client.firebase_logger.logger') as mock_logger:
                    fl = FirebaseLogger()

                    assert fl.firebase_url is None
                    assert fl.firebase_secret is None
                    mock_logger.warning.assert_called_with("⚠️ File config.json không tồn tại")

    def test_load_machine_id_success(self):
        """Test loading machine ID successfully"""
        machine_data = {
            'id': 'test-machine-123',
            'hostname': 'test-host',
            'install_date': '2024-01-01'
        }

        with patch('client.firebase_logger.MACHINE_ID_FILE', Path(self.temp_dir) / 'machine_id.json'):
            with open(Path(self.temp_dir) / 'machine_id.json', 'w') as f:
                json.dump(machine_data, f)

            fl = FirebaseLogger()
            fl.load_machine_id()

            assert fl.machine_id == 'test-machine-123'

    def test_load_machine_id_file_not_found(self):
        """Test loading machine ID when file doesn't exist"""
        with patch('client.firebase_logger.MACHINE_ID_FILE', Path('/nonexistent/machine_id.json')):
            fl = FirebaseLogger()
            fl.load_machine_id()

            assert fl.machine_id is None

    def test_load_machine_id_invalid_json(self):
        """Test loading machine ID with invalid JSON"""
        with patch('client.firebase_logger.MACHINE_ID_FILE', Path(self.temp_dir) / 'machine_id.json'):
            with open(Path(self.temp_dir) / 'machine_id.json', 'w') as f:
                f.write('invalid json')

            with patch('client.firebase_logger.logger') as mock_logger:
                fl = FirebaseLogger()
                fl.load_machine_id()

                mock_logger.error.assert_called_once()

    def test_is_configured_true(self):
        """Test is_configured returns True when properly configured"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        assert fl.is_configured() is True

    def test_is_configured_false_missing_url(self):
        """Test is_configured returns False when URL is missing"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = 'test-machine-123'

        assert fl.is_configured() is False

    def test_is_configured_false_missing_machine_id(self):
        """Test is_configured returns False when machine ID is missing"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = None

        assert fl.is_configured() is False

    def test_make_request_with_retry_success(self):
        """Test successful request with retry mechanism"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        mock_response = mock_firebase_response({'test': 'data'})

        with patch('requests.get', return_value=mock_response) as mock_get:
            with patch('client.firebase_logger.logger') as mock_logger:
                result = fl._make_request_with_retry('GET', 'test/path')

                assert result == {'test': 'data'}
                mock_get.assert_called_once()
                mock_logger.debug.assert_called_with("✅ Firebase request thành công (attempt 1)")

    def test_make_request_with_retry_failure_then_success(self):
        """Test request that fails then succeeds on retry"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        mock_response = mock_firebase_response({'test': 'data'})

        with patch('requests.get') as mock_get:
            # First call fails, second call succeeds
            mock_get.side_effect = [
                Mock(side_effect=Exception("Network error")),
                mock_response
            ]

            with patch('client.firebase_logger.logger') as mock_logger:
                with patch('time.sleep'):  # Skip actual sleep
                    result = fl._make_request_with_retry('GET', 'test/path')

                    assert result == {'test': 'data'}
                    assert mock_get.call_count == 2
                    mock_logger.warning.assert_called_once()

    def test_make_request_with_retry_all_failures(self):
        """Test request that fails all retries"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        with patch('requests.get', side_effect=Exception("Network error")) as mock_get:
            with patch('client.firebase_logger.logger') as mock_logger:
                with patch('time.sleep'):  # Skip actual sleep
                    result = fl._make_request_with_retry('GET', 'test/path', max_retries=2)

                    assert result is None
                    assert mock_get.call_count == 2
                    mock_logger.error.assert_called_once()

    def test_make_request_with_retry_not_configured(self):
        """Test request when not configured"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = None

        with patch('client.firebase_logger.logger') as mock_logger:
            result = fl._make_request_with_retry('GET', 'test/path')

            assert result is None
            mock_logger.warning.assert_called_with("⚠️ Firebase chưa được cấu hình")

    def test_send_log_success(self):
        """Test successful log sending"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        mock_response = mock_firebase_response()

        with patch.object(fl, '_make_request', return_value=mock_response) as mock_request:
            with patch('client.firebase_logger.logger') as mock_logger:
                fl.send_log("Test event", "test/path", {"key": "value"})

                mock_request.assert_called_once()
                mock_logger.info.assert_called_with("✅ Đã gửi log Firebase: Test event")

    def test_send_log_not_configured(self):
        """Test log sending when not configured"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = None

        with patch('client.firebase_logger.logger') as mock_logger:
            fl.send_log("Test event")

            mock_logger.warning.assert_called_with("⚠️ Firebase chưa được cấu hình - cần tạo config.json")

    def test_send_log_failure(self):
        """Test log sending failure"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        with patch.object(fl, '_make_request', return_value=None) as mock_request:
            with patch('client.firebase_logger.logger') as mock_logger:
                fl.send_log("Test event")

                mock_logger.error.assert_called_with("❌ Gửi log Firebase thất bại: Test event")

    def test_update_status_success(self):
        """Test successful status update"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        mock_response = mock_firebase_response()

        with patch.object(fl, '_make_request', return_value=mock_response) as mock_request:
            with patch('client.firebase_logger.logger') as mock_logger:
                machine_info = {
                    'hostname': 'test-host',
                    'install_date': '2024-01-01',
                    'files_processed': 10,
                    'uptime': '5 days'
                }

                fl.update_status(machine_info)

                mock_request.assert_called_once()
                mock_logger.debug.assert_called_with("✅ Đã cập nhật status Firebase")

    def test_update_status_not_configured(self):
        """Test status update when not configured"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = None

        machine_info = {'hostname': 'test-host'}
        fl.update_status(machine_info)

        # Should return without doing anything
        assert True  # No exception should be raised

    def test_send_heartbeat(self):
        """Test sending heartbeat"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        with patch.object(fl, 'update_status') as mock_update:
            with patch.object(fl, 'send_log') as mock_send_log:
                machine_info = {'hostname': 'test-host'}

                fl.send_heartbeat(machine_info)

                mock_update.assert_called_once_with(machine_info)
                mock_send_log.assert_called_once_with("Heartbeat", f"Machine: {fl.machine_id}")

    def test_test_connection_success(self):
        """Test successful connection test"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        mock_response = mock_firebase_response()

        with patch.object(fl, '_make_request', return_value=mock_response):
            result = fl.test_connection()

            assert result is True

    def test_test_connection_failure(self):
        """Test connection test failure"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        with patch.object(fl, '_make_request', return_value=None):
            result = fl.test_connection()

            assert result is False

    def test_test_connection_not_configured(self):
        """Test connection test when not configured"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = None

        result = fl.test_connection()

        assert result is False

    def test_get_machine_status_success(self):
        """Test getting machine status successfully"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        status_data = {
            'info': {'hostname': 'test-host'},
            'status': {'online': True}
        }

        with patch.object(fl, '_make_request', return_value=status_data):
            result = fl.get_machine_status()

            assert result == status_data

    def test_get_machine_status_failure(self):
        """Test getting machine status failure"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        with patch.object(fl, '_make_request', return_value=None):
            with patch('client.firebase_logger.logger') as mock_logger:
                result = fl.get_machine_status()

                assert result == {}
                mock_logger.error.assert_called_once()

    def test_get_machine_status_not_configured(self):
        """Test getting machine status when not configured"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = None

        result = fl.get_machine_status()

        assert result == {}

    def test_listen_commands_not_configured(self):
        """Test listen commands when not configured"""
        fl = FirebaseLogger()
        fl.firebase_url = None
        fl.machine_id = None

        callback = Mock()
        fl.listen_commands(callback)

        # Should return without doing anything
        assert True  # No exception should be raised

    def test_listen_commands_configured(self):
        """Test listen commands when configured"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        callback = Mock()

        with patch.object(fl, '_make_request') as mock_request:
            # Mock commands response
            commands_data = {
                'cmd1': {'type': 'uninstall', 'executed': False, 'params': {}}
            }
            mock_request.side_effect = [commands_data, None]  # First call returns commands, second call marks as executed

            with patch('client.firebase_logger.logger') as mock_logger:
                with patch('threading.Thread') as mock_thread:
                    fl.listen_commands(callback)

                    mock_logger.info.assert_called_with("✅ Đã bắt đầu lắng nghe commands Firebase")

    def test_make_request_backward_compatibility(self):
        """Test _make_request backward compatibility"""
        fl = FirebaseLogger()
        fl.firebase_url = 'https://test.firebase.com'
        fl.machine_id = 'test-machine-123'

        mock_response = mock_firebase_response({'test': 'data'})

        with patch.object(fl, '_make_request_with_retry', return_value=mock_response) as mock_retry:
            result = fl._make_request('GET', 'test/path')

            assert result == mock_response
            mock_retry.assert_called_once_with('GET', 'test/path', None)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
