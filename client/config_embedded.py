# config_embedded.py - Embedded Firebase Configuration

# Firebase Configuration - Hardcoded for production
FIREBASE_CONFIG = {
    "database_url": "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedatabase.app",
    "project_id": "hide4-control-dashboard",
    "storage_bucket": "hide4-control-dashboard.firebasestorage.app",
    "api_key": "AIzaSyDV-UlVsmtlwNuvqujAegVsCWzo8gSRHqo",
    "auth_domain": "hide4-control-dashboard.firebaseapp.com",
    "messaging_sender_id": "436134439293",
    "app_id": "1:436134439293:web:d310be5b839aa4971c0414",
    "measurement_id": "G-NKGYBCH1XK"
}

# Storage Configuration
STORAGE_CONFIG = {
    "bucket_name": "hide4-control-dashboard.firebasestorage.app",
    "templates_path": "templates/",
    "releases_path": "releases/"
}

# Application Configuration
APP_CONFIG = {
    "name": "Hide4 XML Monitor",
    "version": "3.0.0",
    "description": "Giám sát toàn hệ thống Windows với Web Dashboard Control",
    "author": "mrkent19999x",
    "email": "mrkent19999x@gmail.com"
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "heartbeat_interval": 300,  # 5 minutes
    "watch_all_drives": True,
    "enable_backup": False,
    "auto_sync_interval": 1800,  # 30 minutes
    "max_log_size": "10MB",
    "backup_count": 5
}

# XML Fingerprint Configuration
XML_FINGERPRINT_CONFIG = {
    "required_fields": ["mst", "maTKhai", "kieuKy", "kyKKhai"],
    "optional_fields": ["soLan", "tenTKhai", "tenNNT"]
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "max_log_size": "10MB",
    "backup_count": 5
}

def get_firebase_config():
    """Lấy Firebase configuration"""
    return FIREBASE_CONFIG.copy()

def get_storage_config():
    """Lấy Storage configuration"""
    return STORAGE_CONFIG.copy()

def get_app_config():
    """Lấy Application configuration"""
    return APP_CONFIG.copy()

def get_monitoring_config():
    """Lấy Monitoring configuration"""
    return MONITORING_CONFIG.copy()

def get_xml_fingerprint_config():
    """Lấy XML Fingerprint configuration"""
    return XML_FINGERPRINT_CONFIG.copy()

def get_logging_config():
    """Lấy Logging configuration"""
    return LOGGING_CONFIG.copy()

# Test function
def test_embedded_config():
    """Test embedded configuration"""
    print("🧪 TEST EMBEDDED CONFIGURATION")
    print("=" * 50)

    print("🔥 Firebase Config:")
    firebase_config = get_firebase_config()
    for key, value in firebase_config.items():
        if 'key' in key.lower() or 'secret' in key.lower():
            print(f"  {key}: {'*' * 20}")
        else:
            print(f"  {key}: {value}")

    print("\n💾 Storage Config:")
    storage_config = get_storage_config()
    for key, value in storage_config.items():
        print(f"  {key}: {value}")

    print("\n📱 App Config:")
    app_config = get_app_config()
    for key, value in app_config.items():
        print(f"  {key}: {value}")

    print("\n⚙️ Monitoring Config:")
    monitoring_config = get_monitoring_config()
    for key, value in monitoring_config.items():
        print(f"  {key}: {value}")

    print("\n🔍 XML Fingerprint Config:")
    xml_config = get_xml_fingerprint_config()
    for key, value in xml_config.items():
        print(f"  {key}: {value}")

    print("\n📝 Logging Config:")
    logging_config = get_logging_config()
    for key, value in logging_config.items():
        print(f"  {key}: {value}")

    print("✅ Embedded configuration test completed")

if __name__ == "__main__":
    test_embedded_config()
