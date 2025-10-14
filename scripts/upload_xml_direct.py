# upload_xml_direct.py - Upload XML files directly to Firebase Storage

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

def upload_xml_direct():
    """Upload XML files directly to Firebase Storage"""
    try:
        templates_dir = Path("templates")
        xml_files = list(templates_dir.glob("*.xml"))

        if not xml_files:
            print("❌ No XML files found!")
            return False

        print(f"📁 Found {len(xml_files)} XML files to upload")

        # Firebase Storage configuration
        storage_bucket = "hide4-control-dashboard.firebasestorage.app"

        print("\n🌐 Uploading to Firebase Storage...")
        print(f"📦 Bucket: {storage_bucket}")

        uploaded_files = []

        for xml_file in xml_files:
            try:
                print(f"\n📤 Uploading: {xml_file.name}")

                # Read file content
                with open(xml_file, 'rb') as f:
                    file_content = f.read()

                # Create upload URL
                upload_url = f"https://firebasestorage.googleapis.com/v0/b/{storage_bucket}/o"

                # Upload parameters
                params = {
                    'name': f'templates/{xml_file.name}',
                    'uploadType': 'media'
                }

                # Upload file
                response = requests.post(
                    upload_url,
                    params=params,
                    data=file_content,
                    headers={
                        'Content-Type': 'application/xml'
                    }
                )

                if response.status_code == 200:
                    print(f"   ✅ Uploaded successfully: {xml_file.name}")
                    uploaded_files.append(xml_file.name)
                else:
                    print(f"   ❌ Upload failed: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"   ❌ Error uploading {xml_file.name}: {e}")

        print(f"\n📊 Upload Summary:")
        print(f"   - Total files: {len(xml_files)}")
        print(f"   - Uploaded: {len(uploaded_files)}")
        print(f"   - Failed: {len(xml_files) - len(uploaded_files)}")

        if uploaded_files:
            print(f"\n✅ Successfully uploaded files:")
            for file_name in uploaded_files:
                print(f"   - {file_name}")

            print(f"\n🌐 Check templates at:")
            print(f"   https://hide4-control-dashboard.web.app/templates.html")

        return len(uploaded_files) > 0

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def create_upload_script():
    """Create a simple upload script for manual use"""
    script_content = '''#!/bin/bash
# upload_xml.sh - Upload XML files to Firebase Storage

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
'''

    with open("upload_xml.sh", "w") as f:
        f.write(script_content)

    os.chmod("upload_xml.sh", 0o755)
    print("📝 Created upload_xml.sh script")

if __name__ == "__main__":
    print("🚀 Direct Upload XML Templates to Firebase Storage...")
    print("=" * 60)

    # Try direct upload first
    if upload_xml_direct():
        print("\n🎉 Direct upload completed!")
    else:
        print("\n💡 Direct upload failed, creating manual script...")
        create_upload_script()
        print("\n📋 Manual Upload Instructions:")
        print("1. Run: chmod +x upload_xml.sh")
        print("2. Run: ./upload_xml.sh")
        print("3. Check templates page")

    print("\n🌐 Templates Page: https://hide4-control-dashboard.web.app/templates.html")
