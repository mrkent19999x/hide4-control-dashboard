# Import logging manager
try:
    from logging_manager import get_logger
    logger = get_logger('main')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# machine_manager.py

import os
import json
import uuid
import socket
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class MachineManager:
    """Class quản lý Machine ID và heartbeat"""

    def __init__(self):
        self.app_dir = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite'
        self.app_dir.mkdir(parents=True, exist_ok=True)

        self.machine_id_file = self.app_dir / 'machine_id.json'
        self.machine_id = None
        self.hostname = None
        self.install_date = None
        self.last_active = None

        self.heartbeat_thread = None
        self.heartbeat_running = False
        self.heartbeat_interval = 300  # 5 phút

        self._load_machine_id()

    def _load_machine_id(self):
        """Tải Machine ID từ file"""
        if self.machine_id_file.exists():
            try:
                with open(self.machine_id_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.machine_id = data.get('id')
                    self.hostname = data.get('hostname')
                    self.install_date = data.get('install_date')
                    self.last_active = data.get('last_active')

                logger.info(f"✅ Đã load Machine ID: {self.machine_id}")
            except Exception as e:
                logger.error(f"❌ Lỗi load Machine ID: {e}")
                self._create_new_machine_id()
        else:
            self._create_new_machine_id()

    def _create_new_machine_id(self):
        """Tạo Machine ID mới"""
        try:
            # Lấy hostname
            self.hostname = socket.gethostname()

            # Tạo UUID ngắn
            short_uuid = str(uuid.uuid4())[:8]

            # Tạo Machine ID: HOSTNAME-UUID
            self.machine_id = f"{self.hostname}-{short_uuid}"

            # Thời gian hiện tại
            now = datetime.now()
            self.install_date = now.strftime('%Y-%m-%d')
            self.last_active = now.strftime('%Y-%m-%d %H:%M:%S')

            # Lưu vào file
            self._save_machine_id()

            logger.info(f"✅ Đã tạo Machine ID mới: {self.machine_id}")

        except Exception as e:
            logger.error(f"❌ Lỗi tạo Machine ID: {e}")
            self.machine_id = f"UNKNOWN-{str(uuid.uuid4())[:8]}"

    def _save_machine_id(self):
        """Lưu Machine ID vào file"""
        try:
            data = {
                'id': self.machine_id,
                'hostname': self.hostname,
                'install_date': self.install_date,
                'last_active': self.last_active,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            with open(self.machine_id_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Lỗi lưu Machine ID: {e}")

    def get_machine_id(self) -> Optional[str]:
        """Lấy Machine ID"""
        return self.machine_id

    def get_machine_info(self) -> Dict:
        """Lấy thông tin đầy đủ của máy"""
        return {
            'id': self.machine_id,
            'hostname': self.hostname,
            'install_date': self.install_date,
            'last_active': self.last_active,
            'heartbeat_running': self.heartbeat_running,
            'heartbeat_interval': self.heartbeat_interval
        }

    def update_last_active(self):
        """Cập nhật thời gian hoạt động cuối"""
        self.last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._save_machine_id()

    def start_heartbeat(self, firebase_logger=None):
        """Bắt đầu heartbeat thread"""
        if self.heartbeat_running:
            logger.warning("⚠️ Heartbeat đã đang chạy")
            return

        self.heartbeat_running = True
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_worker,
            args=(firebase_logger,),
            daemon=True
        )
        self.heartbeat_thread.start()
        logger.info(f"✅ Đã bắt đầu heartbeat (interval: {self.heartbeat_interval}s)")

    def stop_heartbeat(self):
        """Dừng heartbeat thread"""
        self.heartbeat_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        logger.info("✅ Đã dừng heartbeat")

    def _heartbeat_worker(self, firebase_logger=None):
        """Worker thread cho heartbeat"""
        while self.heartbeat_running:
            try:
                # Cập nhật last_active
                self.update_last_active()

                # Gửi heartbeat về Firebase (nếu có)
                if firebase_logger and hasattr(firebase_logger, 'send_heartbeat'):
                    firebase_logger.send_heartbeat(self.get_machine_info())

                # Chờ interval
                for _ in range(self.heartbeat_interval):
                    if not self.heartbeat_running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"❌ Lỗi heartbeat: {e}")
                time.sleep(60)  # Chờ 1 phút rồi thử lại

    def set_heartbeat_interval(self, interval: int):
        """Thiết lập interval cho heartbeat (giây)"""
        if interval < 60:  # Tối thiểu 1 phút
            interval = 60
        self.heartbeat_interval = interval
        logger.info(f"✅ Đã cập nhật heartbeat interval: {interval}s")

    def uninstall_machine(self):
        """Gỡ cài đặt máy (xóa tất cả file)"""
        try:
            # Dừng heartbeat
            self.stop_heartbeat()

            # Xóa Machine ID file
            if self.machine_id_file.exists():
                os.remove(self.machine_id_file)

            # Xóa các file khác trong app_dir
            for file_path in self.app_dir.glob('*'):
                if file_path.is_file():
                    try:
                        os.remove(file_path)
                        logger.info(f"✅ Đã xóa file: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Không thể xóa file {file_path.name}: {e}")

            # Xóa registry startup (nếu có)
            self._remove_startup_registry()

            logger.info("✅ Đã gỡ cài đặt máy thành công")
            return True

        except Exception as e:
            logger.error(f"❌ Lỗi gỡ cài đặt: {e}")
            return False

    def _remove_startup_registry(self):
        """Xóa khỏi Windows Startup registry"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, "Hide4")
            winreg.CloseKey(key)
            logger.info("✅ Đã xóa khỏi Windows Startup")
        except Exception as e:
            logger.warning(f"⚠️ Không thể xóa registry: {e}")

    def get_status(self) -> Dict:
        """Lấy trạng thái máy"""
        return {
            'machine_id': self.machine_id,
            'hostname': self.hostname,
            'status': 'online' if self.heartbeat_running else 'offline',
            'install_date': self.install_date,
            'last_active': self.last_active,
            'uptime': self._calculate_uptime(),
            'files_processed': self._get_files_processed_count()
        }

    def _calculate_uptime(self) -> str:
        """Tính thời gian uptime"""
        if not self.install_date:
            return "Unknown"

        try:
            install_dt = datetime.strptime(self.install_date, '%Y-%m-%d')
            uptime_days = (datetime.now() - install_dt).days
            return f"{uptime_days} ngày"
        except:
            return "Unknown"

    def _get_files_processed_count(self) -> int:
        """Đếm số file đã xử lý"""
        try:
            processed_file = self.app_dir / 'processed_files.pkl'
            if processed_file.exists():
                import pickle
                with open(processed_file, 'rb') as f:
                    processed = pickle.load(f)
                return len(processed)
        except:
            pass
        return 0

# Global instance
machine_manager = MachineManager()

# Test function
def test_machine_manager():
    """Test MachineManager"""
    print("🧪 TEST MACHINE MANAGER")
    print("=" * 50)

    mm = MachineManager()

    print(f"🖥️ Machine ID: {mm.get_machine_id()}")
    print(f"📊 Machine Info: {mm.get_machine_info()}")
    print(f"📈 Status: {mm.get_status()}")

    # Test heartbeat (chạy 10 giây)
    print("\n🔄 Testing heartbeat...")
    mm.start_heartbeat()
    time.sleep(10)
    mm.stop_heartbeat()
    print("✅ Heartbeat test completed")

if __name__ == "__main__":
    test_machine_manager()
