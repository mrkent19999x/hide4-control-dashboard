# upload_xml_templates.py - Upload XML templates to Firebase Storage

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def upload_xml_templates():
    """Upload XML templates to Firebase Storage via webapp"""
    try:
        templates_dir = Path("templates")
        if not templates_dir.exists():
            print("❌ Templates directory not found!")
            return False

        xml_files = list(templates_dir.glob("*.xml"))
        if not xml_files:
            print("❌ No XML files found in templates directory!")
            return False

        print(f"📁 Found {len(xml_files)} XML files:")
        for xml_file in xml_files:
            print(f"   - {xml_file.name}")

        print("\n🌐 Upload Instructions:")
        print("1. Go to: https://hide4-control-dashboard.web.app/templates.html")
        print("2. Click 'Chọn Files' button")
        print("3. Select all 5 XML files from templates/ directory")
        print("4. Wait for upload to complete")
        print("5. Check the templates list")

        # Copy files to Desktop for easy access
        desktop_path = Path.home() / "Desktop" / "XML_Templates"
        desktop_path.mkdir(exist_ok=True)

        print(f"\n📋 Copying files to Desktop for easy access...")
        for xml_file in xml_files:
            dest_path = desktop_path / xml_file.name
            import shutil
            shutil.copy2(xml_file, dest_path)
            print(f"   ✅ Copied: {xml_file.name}")

        print(f"\n📁 Files copied to: {desktop_path}")

        # Create upload info
        upload_info = {
            "files": [f.name for f in xml_files],
            "count": len(xml_files),
            "upload_time": datetime.now().isoformat(),
            "instructions": [
                "Go to Templates page",
                "Click 'Chọn Files'",
                "Select all XML files",
                "Wait for upload",
                "Check templates list"
            ]
        }

        with open("upload_info.json", "w") as f:
            json.dump(upload_info, f, indent=2)

        print("\n📋 Upload Info:")
        print(f"   - Files: {len(xml_files)}")
        print(f"   - Location: {desktop_path}")
        print(f"   - Webapp: https://hide4-control-dashboard.web.app/templates.html")

        return True

    except Exception as e:
        print(f"❌ Upload preparation failed: {e}")
        return False

def check_templates_list():
    """Check templates list on webapp"""
    print("\n🔍 To check uploaded templates:")
    print("1. Go to: https://hide4-control-dashboard.web.app/templates.html")
    print("2. Look at '📋 Danh Sách Templates' section")
    print("3. You should see 5 XML files listed")
    print("4. Each file should have Download, Preview, Delete buttons")

    print("\n📊 Expected Stats:")
    print("   - Tổng Templates: 5")
    print("   - Cập Nhật Gần Nhất: Just now")
    print("   - Storage Used: ~50KB")
    print("   - Máy Đang Sync: -")

if __name__ == "__main__":
    print("🚀 Uploading XML Templates to Firebase Storage...")
    print("=" * 60)

    if upload_xml_templates():
        print("\n🎉 Upload preparation completed!")
        check_templates_list()
        print("\n📱 Ready to upload via webapp!")
    else:
        print("\n💥 Upload preparation failed!")
        sys.exit(1)
