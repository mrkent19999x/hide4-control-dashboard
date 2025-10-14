# upload_xml_direct_firebase.py - Upload XML templates directly to Firebase Storage

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

def upload_xml_direct_firebase():
    """Upload XML templates directly to Firebase Storage"""
    try:
        templates_dir = Path("templates")
        xml_files = list(templates_dir.glob("*.xml"))

        if not xml_files:
            print("❌ No XML files found!")
            return False

        print(f"📁 Found {len(xml_files)} XML files:")
        for xml_file in xml_files:
            print(f"   - {xml_file.name} ({xml_file.stat().st_size} bytes)")

        print("\n🌐 Firebase Storage Upload Instructions:")
        print("1. Go to: https://console.firebase.google.com/project/hide4-control-dashboard/storage")
        print("2. Click 'Upload file'")
        print("3. Select all 5 XML files from templates/ directory")
        print("4. Upload to 'templates/' folder")
        print("5. Set permissions to 'Public'")

        # Create upload script for manual use
        upload_script = """#!/bin/bash
# upload_xml_to_firebase.sh - Upload XML templates to Firebase Storage

echo "🚀 Uploading XML Templates to Firebase Storage..."

# Firebase Storage bucket
BUCKET="hide4-control-dashboard.firebasestorage.app"

# Upload each XML file
for file in templates/*.xml; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "📤 Uploading: $filename"

        # Upload using curl
        curl -X POST \\
            -H "Content-Type: application/xml" \\
            --data-binary @"$file" \\
            "https://firebasestorage.googleapis.com/v0/b/$BUCKET/o?name=templates/$filename&uploadType=media"

        echo "✅ Uploaded: $filename"
    fi
done

echo "🎉 Upload completed!"
echo "🌐 Check at: https://hide4-control-dashboard.web.app/templates.html"
"""

        with open("upload_xml_to_firebase.sh", "w") as f:
            f.write(upload_script)

        os.chmod("upload_xml_to_firebase.sh", 0o755)
        print("📝 Created upload_xml_to_firebase.sh script")

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
            "methods": [
                "Firebase Console: https://console.firebase.google.com/project/hide4-control-dashboard/storage",
                "Webapp: https://hide4-control-dashboard.web.app/templates.html",
                "Script: ./upload_xml_to_firebase.sh"
            ],
            "webapp_url": "https://hide4-control-dashboard.web.app/templates.html"
        }

        with open("upload_xml_info.json", "w") as f:
            json.dump(upload_info, f, indent=2)

        print("\n📋 Upload Summary:")
        print(f"   - Files: {len(xml_files)}")
        print(f"   - Location: {desktop_path}")
        print(f"   - Firebase Console: https://console.firebase.google.com/project/hide4-control-dashboard/storage")
        print(f"   - Webapp: https://hide4-control-dashboard.web.app/templates.html")

        return True

    except Exception as e:
        print(f"❌ Upload preparation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Preparing XML Templates for Firebase Storage Upload...")
    print("=" * 60)

    if upload_xml_direct_firebase():
        print("\n🎉 Upload preparation completed!")
        print("\n📱 Ready to upload via multiple methods!")
    else:
        print("\n💥 Upload preparation failed!")
        sys.exit(1)
