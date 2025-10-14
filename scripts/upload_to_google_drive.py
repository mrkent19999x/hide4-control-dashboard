# upload_to_google_drive.py - Upload Hide4.exe to Google Drive

import os
import sys
import json
from pathlib import Path

def upload_to_google_drive():
    """Upload Hide4.exe to Google Drive"""
    try:
        exe_path = Path("client/build_release/Hide4.exe")

        if not exe_path.exists():
            print("❌ Hide4.exe not found!")
            return False

        print(f"📁 Found Hide4.exe: {exe_path}")
        print(f"📊 File size: {exe_path.stat().st_size / 1024 / 1024:.1f}MB")

        print("\n📋 Google Drive Upload Instructions:")
        print("1. Go to: https://drive.google.com")
        print("2. Click 'New' → 'File upload'")
        print("3. Select Hide4.exe from client/build_release/")
        print("4. Right-click uploaded file → 'Get link'")
        print("5. Set sharing to 'Anyone with the link'")
        print("6. Copy the sharing link")
        print("7. Update download.html with the new link")

        # Copy to Desktop for easy access
        desktop_path = Path.home() / "Desktop" / "Hide4.exe"
        import shutil
        shutil.copy2(exe_path, desktop_path)
        print(f"\n📁 File copied to Desktop: {desktop_path}")

        return True

    except Exception as e:
        print(f"❌ Upload preparation failed: {e}")
        return False

def create_download_instructions():
    """Create download instructions"""
    print("\n📋 Alternative Download Methods:")
    print("1. **Google Drive**: Upload Hide4.exe to Google Drive and share")
    print("2. **GitHub Releases**: Create release and upload asset")
    print("3. **Firebase Storage**: Upload via webapp templates page")
    print("4. **Direct Transfer**: Copy file directly to target machine")

    print("\n🌐 Current Download Page:")
    print("   https://hide4-control-dashboard.web.app/download.html")

if __name__ == "__main__":
    print("🚀 Preparing Hide4.exe for Google Drive Upload...")
    print("=" * 60)

    if upload_to_google_drive():
        print("\n🎉 Preparation completed!")
        create_download_instructions()
    else:
        print("\n💥 Preparation failed!")
        sys.exit(1)
