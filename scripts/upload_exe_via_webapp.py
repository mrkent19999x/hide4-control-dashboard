# upload_exe_via_webapp.py - Upload Hide4.exe via webapp

import os
import sys
import requests
from pathlib import Path

def upload_exe_via_webapp():
    """Upload Hide4.exe via webapp templates page"""
    try:
        exe_path = Path("client/build_release/Hide4")
        if not exe_path.exists():
            print("❌ Hide4.exe not found!")
            return False

        print(f"📤 Uploading {exe_path} via webapp...")
        print("🌐 Open: https://hide4-control-dashboard.web.app/templates.html")
        print("📋 Instructions:")
        print("1. Go to Templates page")
        print("2. Click 'Chọn Files' button")
        print("3. Select Hide4.exe from your local machine")
        print("4. Wait for upload to complete")
        print("5. Go to Download page to test")

        # Copy file to a more accessible location
        import shutil
        desktop_path = Path.home() / "Desktop" / "Hide4.exe"
        shutil.copy2(exe_path, desktop_path)
        print(f"📁 File copied to Desktop: {desktop_path}")

        return True

    except Exception as e:
        print(f"❌ Upload preparation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Preparing Hide4.exe for Web Upload...")
    print("=" * 50)

    if upload_exe_via_webapp():
        print("\n🎉 Preparation completed!")
        print("📱 You can now upload Hide4.exe via the webapp")
    else:
        print("\n💥 Preparation failed!")
        sys.exit(1)
