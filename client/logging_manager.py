# logging_manager.py - Advanced Logging Management

import os
import logging
import glob
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any

class LoggingManager:
    """
    Advanced logging manager với rotation và cleanup

    Features:
    - RotatingFileHandler với maxBytes=10MB
    - Cleanup logs cũ hơn 30 ngày
    - Multiple log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - Separate logs theo module
    - Performance logging
    """

    def __init__(self, app_name: str = "Hide4"):
        self.app_name = app_name
        self.app_dir = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite'
        self.app_dir.mkdir(parents=True, exist_ok=True)

        # Log directories
        self.log_dir = self.app_dir / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Log files configuration
        self.log_configs = {
            'main': {
                'file': self.log_dir / 'main.log',
                'level': logging.INFO,
                'max_bytes': 10 * 1024 * 1024,  # 10MB
                'backup_count': 5
            },
            'firebase': {
                'file': self.log_dir / 'firebase.log',
                'level': logging.DEBUG,
                'max_bytes': 10 * 1024 * 1024,
                'backup_count': 5
            },
            'storage': {
                'file': self.log_dir / 'storage.log',
                'level': logging.DEBUG,
                'max_bytes': 10 * 1024 * 1024,
                'backup_count': 5
            },
            'performance': {
                'file': self.log_dir / 'performance.log',
                'level': logging.INFO,
                'max_bytes': 5 * 1024 * 1024,  # 5MB
                'backup_count': 3
            },
            'error': {
                'file': self.log_dir / 'error.log',
                'level': logging.ERROR,
                'max_bytes': 5 * 1024 * 1024,
                'backup_count': 10
            }
        }

        # Loggers cache
        self.loggers: Dict[str, logging.Logger] = {}

        # Setup cleanup
        self.setup_cleanup()

        logging.info(f"✅ LoggingManager initialized for {app_name}")
        logging.info(f"📁 Log directory: {self.log_dir}")

    def get_logger(self, module_name: str) -> logging.Logger:
        """
        Lấy logger cho module cụ thể

        Args:
            module_name: Tên module (main, firebase, storage, performance, error)

        Returns:
            Logger instance
        """
        if module_name in self.loggers:
            return self.loggers[module_name]

        # Tạo logger mới
        logger = logging.getLogger(f"{self.app_name}.{module_name}")
        logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers sẽ filter

        # Clear existing handlers
        logger.handlers.clear()

        # Setup handlers
        self._setup_handlers(logger, module_name)

        # Prevent propagation to root logger
        logger.propagate = False

        # Cache logger
        self.loggers[module_name] = logger

        return logger

    def _setup_handlers(self, logger: logging.Logger, module_name: str):
        """Setup handlers cho logger"""
        config = self.log_configs.get(module_name, self.log_configs['main'])

        # File handler với rotation
        file_handler = RotatingFileHandler(
            filename=config['file'],
            maxBytes=config['max_bytes'],
            backupCount=config['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(config['level'])

        # Console handler (chỉ ERROR và CRITICAL)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # Formatters
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_format = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )

        file_handler.setFormatter(file_format)
        console_handler.setFormatter(console_format)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    def setup_cleanup(self):
        """Setup automatic cleanup cho logs cũ"""
        try:
            # Cleanup logs cũ hơn 30 ngày
            cutoff_date = datetime.now() - timedelta(days=30)

            # Tìm tất cả log files
            log_patterns = [
                str(self.log_dir / '*.log'),
                str(self.log_dir / '*.log.*'),  # Rotated files
            ]

            files_deleted = 0
            for pattern in log_patterns:
                for file_path in glob.glob(pattern):
                    file_path = Path(file_path)
                    if file_path.is_file():
                        # Check file modification time
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_date:
                            try:
                                file_path.unlink()
                                files_deleted += 1
                                logging.info(f"🗑️ Đã xóa log file cũ: {file_path.name}")
                            except Exception as e:
                                logging.warning(f"⚠️ Không thể xóa {file_path.name}: {e}")

            if files_deleted > 0:
                logging.info(f"✅ Đã cleanup {files_deleted} log files cũ")

        except Exception as e:
            logging.error(f"❌ Lỗi cleanup logs: {e}")

    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """
        Log performance metrics

        Args:
            operation: Tên operation
            duration: Thời gian thực hiện (seconds)
            details: Chi tiết bổ sung
        """
        perf_logger = self.get_logger('performance')

        message = f"PERF - {operation}: {duration:.3f}s"
        if details:
            details_str = ', '.join([f"{k}={v}" for k, v in details.items()])
            message += f" | {details_str}"

        if duration > 5.0:  # Slow operations
            perf_logger.warning(message)
        elif duration > 1.0:  # Medium operations
            perf_logger.info(message)
        else:  # Fast operations
            perf_logger.debug(message)

    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """
        Log error với context chi tiết

        Args:
            error: Exception object
            context: Context information
        """
        error_logger = self.get_logger('error')

        message = f"ERROR - {type(error).__name__}: {str(error)}"
        if context:
            context_str = ', '.join([f"{k}={v}" for k, v in context.items()])
            message += f" | Context: {context_str}"

        error_logger.error(message, exc_info=True)

    def get_log_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về logs"""
        stats = {
            'log_dir': str(self.log_dir),
            'loggers': len(self.loggers),
            'files': {},
            'total_size': 0
        }

        try:
            for config_name, config in self.log_configs.items():
                file_path = config['file']
                if file_path.exists():
                    size = file_path.stat().st_size
                    stats['files'][config_name] = {
                        'path': str(file_path),
                        'size_bytes': size,
                        'size_mb': round(size / (1024 * 1024), 2),
                        'exists': True
                    }
                    stats['total_size'] += size
                else:
                    stats['files'][config_name] = {
                        'path': str(file_path),
                        'size_bytes': 0,
                        'size_mb': 0,
                        'exists': False
                    }

            stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)

        except Exception as e:
            stats['error'] = str(e)

        return stats

    def cleanup_old_logs(self, days: int = 30):
        """
        Manual cleanup logs cũ

        Args:
            days: Số ngày để giữ lại logs
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            files_deleted = 0

            for file_path in self.log_dir.glob('*.log*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        files_deleted += 1

            logging.info(f"✅ Manual cleanup: đã xóa {files_deleted} files cũ hơn {days} ngày")
            return files_deleted

        except Exception as e:
            logging.error(f"❌ Lỗi manual cleanup: {e}")
            return 0

# Global instance
logging_manager = LoggingManager()

# Convenience functions
def get_logger(module_name: str) -> logging.Logger:
    """Lấy logger cho module"""
    return logging_manager.get_logger(module_name)

def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    """Log performance metrics"""
    logging_manager.log_performance(operation, duration, details)

def log_error_with_context(error: Exception, context: Dict[str, Any] = None):
    """Log error với context"""
    logging_manager.log_error_with_context(error, context)

# Test function
def test_logging_manager():
    """Test LoggingManager"""
    print("🧪 TEST LOGGING MANAGER")
    print("=" * 50)

    lm = LoggingManager("TestApp")

    # Test different loggers
    main_logger = lm.get_logger('main')
    firebase_logger = lm.get_logger('firebase')
    perf_logger = lm.get_logger('performance')

    # Test logging
    main_logger.info("Test main logger")
    firebase_logger.debug("Test firebase logger")
    perf_logger.warning("Test performance logger")

    # Test performance logging
    lm.log_performance("test_operation", 1.5, {"items": 100, "cache_hit": True})

    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        lm.log_error_with_context(e, {"user_id": "test", "action": "test_action"})

    # Test stats
    stats = lm.get_log_stats()
    print(f"📊 Log stats: {stats}")

    print("✅ LoggingManager test completed")

if __name__ == "__main__":
    test_logging_manager()
