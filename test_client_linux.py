#!/usr/bin/env python3
# test_client_linux.py - Test Hide4 Client on Linux

import sys
import os
from pathlib import Path

# Add client to path
sys.path.insert(0, str(Path(__file__).parent / 'client'))

def test_imports():
    """Test import các module"""
    print("1. Testing imports...")
    try:
        from machine_manager import MachineManager
        from xml_fingerprint import XMLFingerprint
        from firebase_logger import FirebaseLogger
        from github_storage import GitHubStorageSync
        print("   ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_machine_manager():
    """Test Machine Manager"""
    print("\n2. Testing Machine Manager...")
    from machine_manager import MachineManager
    
    mm = MachineManager()
    print(f"   Machine ID: {mm.get_machine_id()}")
    print(f"   Hostname: {mm.hostname}")
    print(f"   Status: {mm.get_status()}")
    print("   ✅ Machine Manager OK")

def test_github_storage():
    """Test GitHub Storage Sync"""
    print("\n3. Testing GitHub Storage...")
    from github_storage import GitHubStorageSync
    
    gss = GitHubStorageSync()
    print(f"   Repo: {gss.owner}/{gss.repo}")
    print(f"   Cache: {gss.cache_dir}")
    
    print("   Syncing templates...")
    success = gss.sync_templates()
    
    if success:
        templates = gss.get_local_templates()
        print(f"   ✅ Synced {len(templates)} templates")
        for t in templates:
            print(f"      - {t.name}")
    else:
        print("   ⚠️ Sync failed (check internet/GitHub)")

def test_xml_fingerprint():
    """Test XML Fingerprint"""
    print("\n4. Testing XML Fingerprint...")
    from xml_fingerprint import XMLFingerprint
    from github_storage import GitHubStorageSync
    
    gss = GitHubStorageSync()
    templates_dir = str(gss.cache_dir)
    
    fp = XMLFingerprint(templates_dir)
    print(f"   Loaded {len(fp.templates_fingerprints)} templates")
    print("   ✅ XML Fingerprint OK")

def test_firebase_logger():
    """Test Firebase Logger"""
    print("\n5. Testing Firebase Logger...")
    from firebase_logger import FirebaseLogger
    
    fl = FirebaseLogger()
    print(f"   Configured: {fl.is_configured()}")
    print(f"   Firebase URL: {fl.firebase_url}")
    print("   ✅ Firebase Logger OK")

def main():
    print("="*60)
    print("🧪 HIDE4 CLIENT TEST ON LINUX")
    print("="*60)
    
    if not test_imports():
        print("\n❌ Tests failed at import stage")
        return
    
    test_machine_manager()
    test_github_storage()
    test_xml_fingerprint()
    test_firebase_logger()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("\n📋 Next steps:")
    print("   1. Check templates in: ~/.config/XMLOverwrite/templates/")
    print("   2. Create fake XML file with matching MST")
    print("   3. Run icon.py to test full workflow")

if __name__ == "__main__":
    main()
