# config_manager.py - Centralized Configuration Management

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging

# Import logging manager
try:
    from logging_manager import get_logger
    logger = get_logger('config')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

@dataclass
class FirebaseConfig:
    """Firebase configuration settings"""
    database_url: str
    project_id: str
    storage_bucket: str
    api_key: str
    database_secret: Optional[str] = None

@dataclass
class StorageConfig:
    """Storage configuration settings"""
    cache_dir: str
    sync_interval: int = 1800  # 30 minutes
    max_cache_size: int = 100 * 1024 * 1024  # 100MB
    auto_sync: bool = True

@dataclass
class MonitoringConfig:
    """Monitoring configuration settings"""
    heartbeat_interval: int = 300  # 5 minutes
    log_retention_days: int = 30
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    performance_logging: bool = True

@dataclass
class AppConfig:
    """Application configuration settings"""
    app_name: str = "Hide4 Control Dashboard"
    version: str = "1.0.0"
    debug: bool = False
    auto_start: bool = True
    check_updates: bool = True

@dataclass
class XMLFingerprintConfig:
    """XML Fingerprint configuration settings"""
    required_fields: list = None
    templates_dir: str = "templates"
    cache_enabled: bool = True
    max_templates: int = 1000

    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = [
                'mst', 'maTKhai', 'kieuKy', 'kyKKhai',
                'soLan', 'tenTKhai', 'tenNNT'
            ]

class ConfigManager:
    """
    Centralized configuration management for Hide4 Control Dashboard.

    Supports multiple configuration sources with priority:
    1. Environment variables (highest priority)
    2. config.json file
    3. Embedded configuration (fallback)
    """

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config_cache: Dict[str, Any] = {}
        self.last_modified: Optional[float] = None

        # Initialize default configurations
        self.firebase_config = FirebaseConfig(
            database_url="",
            project_id="",
            storage_bucket="",
            api_key=""
        )

        self.storage_config = StorageConfig(
            cache_dir=str(Path.home() / "XMLOverwrite" / "cache")
        )

        self.monitoring_config = MonitoringConfig()

        self.app_config = AppConfig()

        self.xml_fingerprint_config = XMLFingerprintConfig()

        # Load configuration
        self.load_config()

        logger.info("✅ ConfigManager initialized")

    def load_config(self) -> None:
        """Load configuration from all sources"""
        try:
            # Load from embedded config first (fallback)
            self._load_embedded_config()

            # Load from config file if exists
            if self.config_file.exists():
                self._load_file_config()

            # Override with environment variables
            self._load_env_config()

            # Validate configuration
            self._validate_config()

            logger.info("✅ Configuration loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise

    def _load_embedded_config(self) -> None:
        """Load embedded configuration as fallback"""
        try:
            from config_embedded import (
                get_firebase_config,
                get_monitoring_config,
                get_storage_config,
                get_app_config,
                get_xml_fingerprint_config
            )

            # Load Firebase config
            firebase_data = get_firebase_config()
            if firebase_data:
                self.firebase_config = FirebaseConfig(**firebase_data)

            # Load other configs
            monitoring_data = get_monitoring_config()
            if monitoring_data:
                self.monitoring_config = MonitoringConfig(**monitoring_data)

            storage_data = get_storage_config()
            if storage_data:
                self.storage_config = StorageConfig(**storage_data)

            app_data = get_app_config()
            if app_data:
                self.app_config = AppConfig(**app_data)

            xml_data = get_xml_fingerprint_config()
            if xml_data:
                self.xml_fingerprint_config = XMLFingerprintConfig(**xml_data)

            logger.debug("✅ Embedded configuration loaded")

        except ImportError:
            logger.warning("⚠️ Embedded configuration not available")
        except Exception as e:
            logger.error(f"❌ Failed to load embedded config: {e}")

    def _load_file_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Update Firebase config
            if 'firebase' in config_data:
                firebase_data = config_data['firebase']
                self.firebase_config = FirebaseConfig(**firebase_data)

            # Update Storage config
            if 'storage' in config_data:
                storage_data = config_data['storage']
                self.storage_config = StorageConfig(**storage_data)

            # Update Monitoring config
            if 'monitoring' in config_data:
                monitoring_data = config_data['monitoring']
                self.monitoring_config = MonitoringConfig(**monitoring_data)

            # Update App config
            if 'app' in config_data:
                app_data = config_data['app']
                self.app_config = AppConfig(**app_data)

            # Update XML Fingerprint config
            if 'xml_fingerprint' in config_data:
                xml_data = config_data['xml_fingerprint']
                self.xml_fingerprint_config = XMLFingerprintConfig(**xml_data)

            # Cache the config data
            self.config_cache = config_data
            self.last_modified = self.config_file.stat().st_mtime

            logger.debug("✅ File configuration loaded")

        except Exception as e:
            logger.error(f"❌ Failed to load file config: {e}")

    def _load_env_config(self) -> None:
        """Load configuration from environment variables"""
        try:
            # Firebase environment variables
            if os.getenv('FIREBASE_DATABASE_URL'):
                self.firebase_config.database_url = os.getenv('FIREBASE_DATABASE_URL')

            if os.getenv('FIREBASE_PROJECT_ID'):
                self.firebase_config.project_id = os.getenv('FIREBASE_PROJECT_ID')

            if os.getenv('FIREBASE_STORAGE_BUCKET'):
                self.firebase_config.storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')

            if os.getenv('FIREBASE_API_KEY'):
                self.firebase_config.api_key = os.getenv('FIREBASE_API_KEY')

            if os.getenv('FIREBASE_DATABASE_SECRET'):
                self.firebase_config.database_secret = os.getenv('FIREBASE_DATABASE_SECRET')

            # Storage environment variables
            if os.getenv('STORAGE_CACHE_DIR'):
                self.storage_config.cache_dir = os.getenv('STORAGE_CACHE_DIR')

            if os.getenv('STORAGE_SYNC_INTERVAL'):
                self.storage_config.sync_interval = int(os.getenv('STORAGE_SYNC_INTERVAL'))

            # Monitoring environment variables
            if os.getenv('HEARTBEAT_INTERVAL'):
                self.monitoring_config.heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL'))

            if os.getenv('LOG_RETENTION_DAYS'):
                self.monitoring_config.log_retention_days = int(os.getenv('LOG_RETENTION_DAYS'))

            # App environment variables
            if os.getenv('APP_DEBUG'):
                self.app_config.debug = os.getenv('APP_DEBUG').lower() in ('true', '1', 'yes')

            if os.getenv('APP_AUTO_START'):
                self.app_config.auto_start = os.getenv('APP_AUTO_START').lower() in ('true', '1', 'yes')

            logger.debug("✅ Environment configuration loaded")

        except Exception as e:
            logger.error(f"❌ Failed to load environment config: {e}")

    def _validate_config(self) -> None:
        """Validate configuration settings"""
        errors = []

        # Only validate if we have actual configuration data
        if not self.firebase_config.database_url and not self.firebase_config.project_id:
            logger.warning("⚠️ Firebase configuration not available - using defaults")
            return

        # Validate Firebase config
        if not self.firebase_config.database_url:
            errors.append("Firebase database URL is required")

        if not self.firebase_config.project_id:
            errors.append("Firebase project ID is required")

        # Validate Storage config
        if not self.storage_config.cache_dir:
            errors.append("Storage cache directory is required")

        if self.storage_config.sync_interval < 60:
            errors.append("Storage sync interval must be at least 60 seconds")

        # Validate Monitoring config
        if self.monitoring_config.heartbeat_interval < 60:
            errors.append("Heartbeat interval must be at least 60 seconds")

        if self.monitoring_config.log_retention_days < 1:
            errors.append("Log retention days must be at least 1")

        if errors:
            error_msg = "Configuration validation failed: " + "; ".join(errors)
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        logger.debug("✅ Configuration validation passed")

    def get_firebase_config(self) -> FirebaseConfig:
        """Get Firebase configuration"""
        return self.firebase_config

    def get_storage_config(self) -> StorageConfig:
        """Get Storage configuration"""
        return self.storage_config

    def get_monitoring_config(self) -> MonitoringConfig:
        """Get Monitoring configuration"""
        return self.monitoring_config

    def get_app_config(self) -> AppConfig:
        """Get Application configuration"""
        return self.app_config

    def get_xml_fingerprint_config(self) -> XMLFingerprintConfig:
        """Get XML Fingerprint configuration"""
        return self.xml_fingerprint_config

    def get_config(self, section: str = None) -> Union[Dict[str, Any], Any]:
        """
        Get configuration data

        Args:
            section: Configuration section to get ('firebase', 'storage', 'monitoring', 'app', 'xml_fingerprint')
                    If None, returns all configuration

        Returns:
            Configuration data as dictionary or specific config object
        """
        if section is None:
            return {
                'firebase': asdict(self.firebase_config),
                'storage': asdict(self.storage_config),
                'monitoring': asdict(self.monitoring_config),
                'app': asdict(self.app_config),
                'xml_fingerprint': asdict(self.xml_fingerprint_config)
            }

        config_map = {
            'firebase': self.firebase_config,
            'storage': self.storage_config,
            'monitoring': self.monitoring_config,
            'app': self.app_config,
            'xml_fingerprint': self.xml_fingerprint_config
        }

        if section not in config_map:
            raise ValueError(f"Unknown configuration section: {section}")

        return config_map[section]

    def update_config(self, section: str, data: Dict[str, Any]) -> None:
        """
        Update configuration section

        Args:
            section: Configuration section to update
            data: New configuration data
        """
        try:
            if section == 'firebase':
                self.firebase_config = FirebaseConfig(**data)
            elif section == 'storage':
                self.storage_config = StorageConfig(**data)
            elif section == 'monitoring':
                self.monitoring_config = MonitoringConfig(**data)
            elif section == 'app':
                self.app_config = AppConfig(**data)
            elif section == 'xml_fingerprint':
                self.xml_fingerprint_config = XMLFingerprintConfig(**data)
            else:
                raise ValueError(f"Unknown configuration section: {section}")

            # Validate updated configuration
            self._validate_config()

            logger.info(f"✅ Configuration section '{section}' updated")

        except Exception as e:
            logger.error(f"❌ Failed to update configuration section '{section}': {e}")
            raise

    def save_config(self, file_path: str = None) -> None:
        """
        Save current configuration to file

        Args:
            file_path: Path to save configuration file (defaults to self.config_file)
        """
        try:
            save_path = Path(file_path) if file_path else self.config_file

            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            config_data = self.get_config()

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Configuration saved to {save_path}")

        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            raise

    def reload_config(self) -> None:
        """Reload configuration from all sources"""
        try:
            self.load_config()
            logger.info("✅ Configuration reloaded")
        except Exception as e:
            logger.error(f"❌ Failed to reload configuration: {e}")
            raise

    def is_config_valid(self) -> bool:
        """Check if current configuration is valid"""
        try:
            self._validate_config()
            return True
        except ValueError:
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging"""
        return {
            'firebase_configured': bool(self.firebase_config.database_url),
            'storage_configured': bool(self.storage_config.cache_dir),
            'monitoring_enabled': self.monitoring_config.performance_logging,
            'debug_mode': self.app_config.debug,
            'config_file_exists': self.config_file.exists(),
            'last_modified': self.last_modified,
            'is_valid': self.is_config_valid()
        }

# Global configuration manager instance
config_manager = ConfigManager()

# Convenience functions for backward compatibility
def get_firebase_config() -> FirebaseConfig:
    """Get Firebase configuration"""
    return config_manager.get_firebase_config()

def get_storage_config() -> StorageConfig:
    """Get Storage configuration"""
    return config_manager.get_storage_config()

def get_monitoring_config() -> MonitoringConfig:
    """Get Monitoring configuration"""
    return config_manager.get_monitoring_config()

def get_app_config() -> AppConfig:
    """Get Application configuration"""
    return config_manager.get_app_config()

def get_xml_fingerprint_config() -> XMLFingerprintConfig:
    """Get XML Fingerprint configuration"""
    return config_manager.get_xml_fingerprint_config()

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing ConfigManager...")
    print("=" * 50)

    # Test configuration loading
    try:
        config = config_manager.get_config()
        print("✅ Configuration loaded successfully")
        print(f"📊 Config summary: {config_manager.get_config_summary()}")

        # Test individual configs
        firebase_config = config_manager.get_firebase_config()
        print(f"🔥 Firebase configured: {bool(firebase_config.database_url)}")

        storage_config = config_manager.get_storage_config()
        print(f"💾 Storage cache dir: {storage_config.cache_dir}")

        monitoring_config = config_manager.get_monitoring_config()
        print(f"📊 Heartbeat interval: {monitoring_config.heartbeat_interval}s")

        app_config = config_manager.get_app_config()
        print(f"🚀 App name: {app_config.app_name}")

        xml_config = config_manager.get_xml_fingerprint_config()
        print(f"🔍 Required fields: {len(xml_config.required_fields)}")

        print("\n🎉 All configuration tests passed!")

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        exit(1)
