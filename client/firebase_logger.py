# firebase_logger.py

import os
import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Import logging manager
try:
    from logging_manager import get_logger, log_error_with_context
    logger = get_logger('firebase')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_error_with_context(error, context=None):
        logger.error(f"Error: {error}, Context: {context}")

# Import embedded config
try:
    from config_embedded import get_firebase_config, get_monitoring_config
    FIREBASE_CONFIG = get_firebase_config()
    MONITORING_CONFIG = get_monitoring_config()
    USE_EMBEDDED_CONFIG = True
except ImportError:
    USE_EMBEDDED_CONFIG = False

# --- Config --- #
CONFIG_FILE = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite' / 'config.json'
MACHINE_ID_FILE = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite' / 'machine_id.json'

class FirebaseLogger:
    """Class để gửi logs và heartbeat lên Firebase Realtime Database"""

    def __init__(self, verbose: bool = False):
        self.firebase_url = None
        self.firebase_secret = None
        self.machine_id = None
        self.verbose = verbose  # Enhanced logging mode

        if USE_EMBEDDED_CONFIG:
            self.load_embedded_config()
        else:
            self.load_config()

        self.load_machine_id()
        
        if self.verbose:
            logger.info("FirebaseLogger initialized in VERBOSE mode")

    def load_embedded_config(self):
        """Tải cấu hình từ embedded config"""
        self.firebase_url = FIREBASE_CONFIG.get('database_url')
        self.firebase_secret = None  # No secret needed for public access
        logger.info("✅ Sử dụng embedded Firebase config")

    def load_config(self):
        """Tải cấu hình Firebase từ file config.json (fallback)"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    firebase_config = config.get('firebase', {})
                    self.firebase_url = firebase_config.get('database_url')
                    self.firebase_secret = firebase_config.get('database_secret')
            except Exception as e:
                logger.error(f"❌ Lỗi đọc config: {e}")
        else:
            logger.warning("⚠️ File config.json không tồn tại")

    def load_machine_id(self):
        """Tải Machine ID từ file machine_id.json"""
        if MACHINE_ID_FILE.exists():
            try:
                with open(MACHINE_ID_FILE, 'r', encoding='utf-8') as f:
                    machine_data = json.load(f)
                    self.machine_id = machine_data.get('id')
            except Exception as e:
                logger.error(f"❌ Lỗi đọc machine_id: {e}")

    def is_configured(self) -> bool:
        """Kiểm tra xem Firebase đã được cấu hình chưa"""
        return bool(self.firebase_url and self.machine_id)

    def _make_request_with_retry(self, method: str, path: str, data: Dict = None, max_retries: int = 3) -> Optional[Dict]:
        """
        Thực hiện request đến Firebase REST API với retry mechanism

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: Firebase path
            data: Request data (for POST/PUT/PATCH)
            max_retries: Số lần thử lại tối đa

        Returns:
            Response data hoặc None nếu thất bại
        """
        if not self.is_configured():
            logger.warning("⚠️ Firebase chưa được cấu hình")
            return None

        url = f"{self.firebase_url.rstrip('/')}/{path.lstrip('/')}.json"
        params = {}
        if self.firebase_secret:
            params['auth'] = self.firebase_secret

        for attempt in range(max_retries):
            try:
                # Thực hiện request
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, timeout=10)
                elif method.upper() == 'POST':
                    response = requests.post(url, params=params, json=data, timeout=10)
                elif method.upper() == 'PUT':
                    response = requests.put(url, params=params, json=data, timeout=10)
                elif method.upper() == 'PATCH':
                    response = requests.patch(url, params=params, json=data, timeout=10)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, params=params, timeout=10)
                else:
                    logger.error(f"Method khong ho tro: {method}")
                    return None

                response.raise_for_status()
                if self.verbose:
                    logger.info(f"Firebase {method} request successful (attempt {attempt + 1})")
                else:
                    logger.debug(f"Firebase request thanh cong (attempt {attempt + 1})")
                return response.json() if response.content else {}

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:  # Lần cuối cùng
                    logger.error(f"Firebase request that bai sau {max_retries} lan thu: {e}")
                    return None
                else:
                    # Exponential backoff: 1s, 2s, 4s...
                    wait_time = 2 ** attempt
                    logger.warning(f"Firebase request that bai (attempt {attempt + 1}/{max_retries}), thu lai sau {wait_time}s: {e}")
                    time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Loi Firebase khong mong doi: {e}")
                return None

        return None

    def _make_request(self, method: str, path: str, data: Dict = None) -> Optional[Dict]:
        """Thực hiện request đến Firebase REST API (backward compatibility)"""
        return self._make_request_with_retry(method, path, data)

    def send_log(self, event: str, path: str = None, fingerprint: Dict = None, once: bool = False):
        """Gửi log lên Firebase"""
        if not self.is_configured():
            logger.warning("Firebase chua duoc cau hinh - can tao config.json")
            print(f"Firebase chua duoc cau hinh")
            print(f"Can tao file: {CONFIG_FILE}")
            print(f"Copy tu: config.json.example")
            return

        try:
            timestamp = datetime.now().isoformat()

            # Tạo log data
            log_data = {
                'event': event,
                'timestamp': timestamp,
                'machine_id': self.machine_id,
                'path': path,
                'fingerprint': fingerprint or {}
            }

            if self.verbose:
                logger.info(f"Sending log: {event} | Path: {path} | Fingerprint: {fingerprint}")

            # Gửi lên Firebase
            path = f"logs/{self.machine_id}/{timestamp.replace(':', '-').replace('.', '-')}"
            result = self._make_request('PUT', path, log_data)

            if result is not None:
                if self.verbose:
                    logger.info(f"Log sent successfully: {event}")
                else:
                    logger.info(f"Da gui log Firebase: {event}")
                print(f"Da gui log Firebase: {event}")
            else:
                logger.error(f"Gui log Firebase that bai: {event}")
                print(f"Gui log Firebase that bai: {event}")

        except Exception as e:
            logger.error(f"Gui Firebase that bai: {e}")
            print(f"Gui Firebase that bai: {e}")

    def update_status(self, machine_info: Dict):
        """Cập nhật trạng thái máy lên Firebase"""
        if not self.is_configured():
            return

        try:
            timestamp = datetime.now().isoformat()

            # Cập nhật machine info
            machine_data = {
                'info': {
                    'hostname': machine_info.get('hostname'),
                    'install_date': machine_info.get('install_date'),
                    'last_active': timestamp
                },
                'status': {
                    'online': True,
                    'last_heartbeat': timestamp,
                    'heartbeat_interval': machine_info.get('heartbeat_interval', 300)
                },
                'stats': {
                    'files_processed': machine_info.get('files_processed', 0),
                    'uptime': machine_info.get('uptime', 'Unknown')
                }
            }

            path = f"machines/{self.machine_id}"
            result = self._make_request('PATCH', path, machine_data)

            if result is not None:
                if self.verbose:
                    logger.info(f"Machine status updated successfully")
                else:
                    logger.debug(f"Da cap nhat status Firebase")
            else:
                logger.error(f"Cap nhat status Firebase that bai")

        except Exception as e:
            logger.error(f"Cap nhat Firebase status that bai: {e}")

    def send_heartbeat(self, machine_info: Dict):
        """Gửi heartbeat lên Firebase"""
        self.update_status(machine_info)

        # Gửi heartbeat log
        self.send_log("Heartbeat", f"Machine: {self.machine_id}")

    def listen_commands(self, callback):
        """Lắng nghe commands từ Firebase (simplified version)"""
        if not self.is_configured():
            return

        try:
            # Kiểm tra commands mỗi 30 giây
            import threading
            import time

            def check_commands():
                while True:
                    try:
                        path = f"machines/{self.machine_id}/commands"
                        result = self._make_request('GET', path)

                        if result:
                            for command_id, command_data in result.items():
                                if not command_data.get('executed', False):
                                    # Thực hiện command
                                    command_type = command_data.get('type')
                                    if self.verbose:
                                        logger.info(f"Received command: {command_type}")
                                    
                                    if command_type == 'uninstall':
                                        if self.verbose:
                                            logger.info(f"Executing uninstall command")
                                        callback('uninstall', command_data.get('params', {}))

                                    # Đánh dấu đã thực hiện
                                    self._make_request('PATCH', f"{path}/{command_id}", {'executed': True})
                                    if self.verbose:
                                        logger.info(f"Command {command_id} marked as executed")

                    except Exception as e:
                        logger.error(f"Loi check commands: {e}")

                    time.sleep(30)  # Check every 30 seconds

            thread = threading.Thread(target=check_commands, daemon=True)
            thread.start()
            logger.info("Da bat dau lang nghe commands Firebase")

        except Exception as e:
            logger.error(f"Loi setup commands listener: {e}")

    def get_machine_status(self) -> Dict:
        """Lấy trạng thái máy từ Firebase"""
        if not self.is_configured():
            return {}

        try:
            path = f"machines/{self.machine_id}"
            result = self._make_request('GET', path)
            return result or {}
        except Exception as e:
            logger.error(f"❌ Lỗi lấy machine status: {e}")
            return {}

    def test_connection(self) -> bool:
        """Test kết nối Firebase"""
        if not self.is_configured():
            return False

        try:
            result = self._make_request('GET', 'test')
            return True
        except:
            return False

# Global instance
firebase_logger = FirebaseLogger()

# Test function
def test_firebase_logger():
    """Test Firebase Logger"""
    print("🧪 TEST FIREBASE LOGGER")
    print("=" * 50)

    fl = FirebaseLogger()

    print(f"🖥️ Machine ID: {fl.get_machine_id()}")
    print(f"🔗 Firebase URL: {fl.firebase_url}")
    print(f"⚙️ Configured: {fl.is_configured()}")

    if fl.is_configured():
        print(f"🔍 Test connection: {fl.test_connection()}")

        # Test send log
        fl.send_log("Test từ Firebase Logger", "test_path")

        # Test update status
        machine_info = {
            'hostname': 'test-machine',
            'install_date': '2024-01-01',
            'files_processed': 0,
            'uptime': '1 ngày'
        }
        fl.update_status(machine_info)

    print("✅ Firebase Logger test completed")

if __name__ == "__main__":
    test_firebase_logger()
