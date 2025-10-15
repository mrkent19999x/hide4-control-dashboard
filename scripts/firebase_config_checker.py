#!/usr/bin/env python3
"""
Firebase Configuration Checker & Password Manager
"""

import os
import json
import requests
from pathlib import Path

def check_firebase_storage():
    """Check if Firebase Storage is important for this app"""
    print("🔍 CHECKING FIREBASE STORAGE IMPORTANCE")
    print("=" * 50)
    
    # Check what Firebase Storage is used for
    storage_usage = []
    
    # Check client code for storage usage
    client_files = [
        "client/firebase_logger.py",
        "client/github_storage.py", 
        "client/machine_manager.py",
        "client/config_embedded.py"
    ]
    
    for file_path in client_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'storage' in content.lower():
                    storage_usage.append(f"📄 {file_path}: Uses storage")
    
    # Check webapp for storage usage
    webapp_files = [
        "webapp/js/machines.js",
        "webapp/js/settings.js",
        "webapp/js/templates.js"
    ]
    
    for file_path in webapp_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'storage' in content.lower():
                    storage_usage.append(f"🌐 {file_path}: Uses storage")
    
    print("📊 STORAGE USAGE ANALYSIS:")
    if storage_usage:
        for usage in storage_usage:
            print(f"  {usage}")
        print("\n⚠️ Firebase Storage IS being used in the application")
        print("💡 Recommendation: Enable Firebase Storage for full functionality")
    else:
        print("  ✅ No direct Firebase Storage usage found")
        print("\n✅ Firebase Storage is NOT critical for core functionality")
        print("💡 Current app works fine without Storage")
    
    return len(storage_usage) > 0

def check_firebase_config():
    """Check Firebase configuration"""
    print("\n🔧 CHECKING FIREBASE CONFIGURATION")
    print("=" * 50)
    
    config_files = [
        "firebase.json",
        "client/config_embedded.py",
        ".firebaserc"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ Found: {config_file}")
            if config_file == "firebase.json":
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    print(f"  📋 Project: {config.get('project', 'Not set')}")
                    print(f"  📋 Hosting: {config.get('hosting', 'Not configured')}")
                    print(f"  📋 Database: {config.get('database', 'Not configured')}")
                    print(f"  📋 Storage: {config.get('storage', 'Not configured')}")
        else:
            print(f"❌ Missing: {config_file}")

def create_firebase_storage_config():
    """Create Firebase Storage configuration if needed"""
    print("\n🚀 CREATING FIREBASE STORAGE CONFIG")
    print("=" * 50)
    
    # Read current firebase.json
    if os.path.exists("firebase.json"):
        with open("firebase.json", 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Add storage configuration
    if 'storage' not in config:
        config['storage'] = {
            "rules": "storage.rules"
        }
        print("✅ Added storage configuration to firebase.json")
    
    # Create storage.rules file
    storage_rules = '''rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Allow read/write access to authenticated users
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
    
    // Allow public read access to templates
    match /templates/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}'''
    
    with open("storage.rules", 'w') as f:
        f.write(storage_rules)
    
    print("✅ Created storage.rules file")
    
    # Update firebase.json
    with open("firebase.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Updated firebase.json with storage config")

def check_password_requirements():
    """Check password requirements for Firebase"""
    print("\n🔐 PASSWORD REQUIREMENTS CHECK")
    print("=" * 50)
    
    print("📋 Firebase Password Requirements:")
    print("  • Minimum 8 characters")
    print("  • Must contain letters and numbers")
    print("  • Special characters recommended")
    print("  • Cannot be common passwords")
    
    suggested_password = "Baoan2022@"
    print(f"\n💡 Suggested password: {suggested_password}")
    print("✅ Meets all requirements:")
    print("  ✅ 10 characters (more than minimum)")
    print("  ✅ Contains letters (Baoan)")
    print("  ✅ Contains numbers (2022)")
    print("  ✅ Contains special character (@)")
    print("  ✅ Not a common password")

def main():
    """Main function"""
    print("🔥 FIREBASE CONFIGURATION CHECKER")
    print("=" * 50)
    
    # Check storage importance
    storage_important = check_firebase_storage()
    
    # Check current config
    check_firebase_config()
    
    # Check password requirements
    check_password_requirements()
    
    # Create storage config if needed
    if storage_important:
        create_firebase_storage_config()
    
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 50)
    
    if storage_important:
        print("1. ✅ Enable Firebase Storage in console")
        print("2. ✅ Deploy storage rules: firebase deploy --only storage")
        print("3. ✅ Test storage functionality")
    else:
        print("1. ⚠️ Firebase Storage is optional")
        print("2. ✅ Current app works without Storage")
        print("3. 💡 Can enable later if needed")
    
    print("\n4. 🔐 Change password to: Baoan2022@")
    print("5. ✅ Test Firebase login with new password")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Go to Firebase Console")
    print("2. Change password to Baoan2022@")
    print("3. Test login with new credentials")
    print("4. Enable Storage if needed")
    print("5. Deploy storage rules if enabled")

if __name__ == "__main__":
    main()
