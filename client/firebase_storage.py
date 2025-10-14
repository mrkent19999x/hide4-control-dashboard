# Import logging manager
try:
    from logging_manager import get_logger, log_performance
    logger = get_logger('storage')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_performance(operation, duration, details=None):
        logger.info(f"PERF - {operation}: {duration:.3f}s")

# firebase_storage.py - Firebase Storage Sync for Templates

import os
import json
import requests
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class FirebaseStorageSync:
    """Class để đồng bộ XML templates từ Firebase Storage"""

    def __init__(self):
        # Firebase Storage configuration
        self.project_id = "hide4-control-dashboard"
        self.bucket_name = "hide4-control-dashboard.firebasestorage.app"
        self.storage_url = f"https://firebasestorage.googleapis.com/v0/b/{self.bucket_name}/o"

        # Local cache directory
        self.cache_dir = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite' / 'templates'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Metadata file
        self.metadata_file = self.cache_dir / 'metadata.json'

        # Sync settings
        self.sync_interval = 1800  # 30 minutes
        self.sync_running = False
        self.sync_thread = None

        # Load cached metadata
        self.metadata = self.load_metadata()

        logger.info(f"✅ Firebase Storage Sync initialized")
        logger.info(f"📁 Cache directory: {self.cache_dir}")

    def load_metadata(self) -> Dict:
        """Tải metadata từ file cache"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Lỗi đọc metadata: {e}")

        return {
            'last_sync': None,
            'templates': {},
            'version': 1
        }

    def save_metadata(self):
        """Lưu metadata vào file cache"""
        try:
            self.metadata['last_sync'] = datetime.now().isoformat()
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Lỗi lưu metadata: {e}")

    def _make_request_with_retry(self, url: str, method: str = 'GET', data: Dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """
        Thực hiện request với retry mechanism

        Args:
            url: Request URL
            method: HTTP method
            data: Request data
            max_retries: Số lần thử lại tối đa

        Returns:
            Response object hoặc None nếu thất bại
        """
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, timeout=30)
                elif method.upper() == 'POST':
                    response = requests.post(url, json=data, timeout=30)
                else:
                    logger.error(f"❌ Method không hỗ trợ: {method}")
                    return None

                response.raise_for_status()
                logger.debug(f"✅ Storage request thành công (attempt {attempt + 1})")
                return response

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:  # Lần cuối cùng
                    logger.error(f"❌ Storage request thất bại sau {max_retries} lần thử: {e}")
                    return None
                else:
                    # Exponential backoff: 1s, 2s, 4s...
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️ Storage request thất bại (attempt {attempt + 1}/{max_retries}), thử lại sau {wait_time}s: {e}")
                    time.sleep(wait_time)

            except Exception as e:
                logger.error(f"❌ Lỗi Storage không mong đợi: {e}")
                return None

        return None

    def list_remote_templates(self) -> List[Dict]:
        """Lấy danh sách templates từ Firebase Storage với retry mechanism"""
        try:
            # Firebase Storage REST API để list files
            url = f"{self.storage_url}?prefix=templates%2F"
            response = self._make_request_with_retry(url)

            if not response:
                logger.error("❌ Không thể kết nối Firebase Storage")
                return []

            data = response.json()
            templates = []

            if 'items' in data:
                for item in data['items']:
                    if item['name'].endswith('.xml'):
                        template = {
                            'name': item['name'],
                            'size': item.get('size', 0),
                            'updated': item.get('updated', ''),
                            'download_url': self.get_download_url(item['name'])
                        }
                        templates.append(template)

            logger.info(f"📋 Tìm thấy {len(templates)} templates trên Firebase Storage")
            return templates

        except Exception as e:
            logger.error(f"❌ Lỗi lấy danh sách templates: {e}")
            return []

    def get_download_url(self, file_name: str) -> str:
        """Tạo download URL cho file"""
        encoded_name = file_name.replace('/', '%2F')
        return f"{self.storage_url}%2F{encoded_name}?alt=media"

    def download_template(self, template: Dict) -> bool:
        """Tải template về local cache với retry mechanism"""
        try:
            file_name = template['name'].split('/')[-1]  # Remove 'templates/' prefix
            local_path = self.cache_dir / file_name

            # Download file với retry mechanism
            response = self._make_request_with_retry(template['download_url'])

            if not response:
                logger.error(f"❌ Không thể tải template: {template['name']}")
                return False

            # Save to local cache
            with open(local_path, 'wb') as f:
                f.write(response.content)

            # Update metadata
            self.metadata['templates'][file_name] = {
                'size': template['size'],
                'updated': template['updated'],
                'downloaded_at': datetime.now().isoformat()
            }

            logger.info(f"✅ Đã tải template: {file_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Lỗi tải template {template['name']}: {e}")
            return False

    def sync_templates(self) -> bool:
        """Đồng bộ tất cả templates từ Firebase Storage"""
        try:
            logger.info("🔄 Bắt đầu đồng bộ templates...")

            # Lấy danh sách templates từ Firebase
            remote_templates = self.list_remote_templates()

            if not remote_templates:
                logger.warning("⚠️ Không tìm thấy templates trên Firebase Storage")
                return False

            # Kiểm tra templates cần tải/cập nhật
            downloaded_count = 0
            updated_count = 0

            for template in remote_templates:
                file_name = template['name'].split('/')[-1]
                local_path = self.cache_dir / file_name

                # Kiểm tra xem có cần tải/cập nhật không
                should_download = False

                if not local_path.exists():
                    should_download = True
                    logger.info(f"📥 Template mới: {file_name}")
                else:
                    # Kiểm tra metadata để xem có cập nhật không
                    cached_info = self.metadata['templates'].get(file_name, {})
                    if cached_info.get('updated', '') != template['updated']:
                        should_download = True
                        logger.info(f"🔄 Template cập nhật: {file_name}")

                if should_download:
                    if self.download_template(template):
                        if local_path.exists():
                            updated_count += 1
                        else:
                            downloaded_count += 1

            # Lưu metadata
            self.save_metadata()

            total_synced = downloaded_count + updated_count
            if total_synced > 0:
                logger.info(f"✅ Đồng bộ hoàn tất: {downloaded_count} mới, {updated_count} cập nhật")
            else:
                logger.info("✅ Templates đã được đồng bộ")

            return True

        except Exception as e:
            logger.error(f"❌ Lỗi đồng bộ templates: {e}")
            return False

    def get_local_templates(self) -> List[Path]:
        """Lấy danh sách templates trong cache local"""
        try:
            xml_files = list(self.cache_dir.glob('*.xml'))
            logger.info(f"📁 Tìm thấy {len(xml_files)} templates trong cache local")
            return xml_files
        except Exception as e:
            logger.error(f"❌ Lỗi đọc templates local: {e}")
            return []

    def start_auto_sync(self, interval: int = None):
        """Bắt đầu tự động đồng bộ trong background"""
        if self.sync_running:
            logger.warning("⚠️ Auto sync đã đang chạy")
            return

        if interval:
            self.sync_interval = interval

        self.sync_running = True
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()

        logger.info(f"✅ Đã bắt đầu auto sync (interval: {self.sync_interval}s)")

    def stop_auto_sync(self):
        """Dừng tự động đồng bộ"""
        self.sync_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)

        logger.info("⏹️ Đã dừng auto sync")

    def _sync_worker(self):
        """Worker thread cho auto sync"""
        while self.sync_running:
            try:
                self.sync_templates()

                # Chờ interval trước khi sync tiếp
                for _ in range(self.sync_interval):
                    if not self.sync_running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"❌ Lỗi trong sync worker: {e}")
                time.sleep(60)  # Chờ 1 phút trước khi thử lại

    def force_sync(self) -> bool:
        """Đồng bộ ngay lập tức (bỏ qua cache)"""
        logger.info("🔄 Force sync templates...")
        return self.sync_templates()

    def get_sync_status(self) -> Dict:
        """Lấy trạng thái đồng bộ"""
        local_templates = self.get_local_templates()

        return {
            'last_sync': self.metadata.get('last_sync'),
            'local_count': len(local_templates),
            'cache_dir': str(self.cache_dir),
            'sync_running': self.sync_running,
            'sync_interval': self.sync_interval
        }

    def clear_cache(self):
        """Xóa cache local"""
        try:
            for file_path in self.cache_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()

            # Reset metadata
            self.metadata = {
                'last_sync': None,
                'templates': {},
                'version': 1
            }
            self.save_metadata()

            logger.info("🗑️ Đã xóa cache templates")

        except Exception as e:
            logger.error(f"❌ Lỗi xóa cache: {e}")

# Global instance
firebase_storage_sync = FirebaseStorageSync()

# Test function
def test_firebase_storage_sync():
    """Test Firebase Storage Sync"""
    print("🧪 TEST FIREBASE STORAGE SYNC")
    print("=" * 50)

    fss = FirebaseStorageSync()

    print(f"📁 Cache directory: {fss.cache_dir}")
    print(f"🔄 Sync interval: {fss.sync_interval}s")

    # Test sync
    print("\n🔄 Testing sync...")
    success = fss.sync_templates()
    print(f"Sync result: {'✅ Success' if success else '❌ Failed'}")

    # Test local templates
    print("\n📁 Local templates:")
    local_templates = fss.get_local_templates()
    for template in local_templates:
        print(f"  - {template.name}")

    # Test status
    print("\n📊 Sync status:")
    status = fss.get_sync_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("✅ Firebase Storage Sync test completed")

if __name__ == "__main__":
    test_firebase_storage_sync()
