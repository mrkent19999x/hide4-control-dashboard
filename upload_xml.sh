#!/bin/bash
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
        curl -X POST \
            -H "Content-Type: application/xml" \
            --data-binary @"$file" \
            "https://firebasestorage.googleapis.com/v0/b/$BUCKET/o?name=templates/$filename&uploadType=media"
        
        echo "✅ Uploaded: $filename"
    fi
done

echo "🎉 Upload completed!"
echo "🌐 Check at: https://hide4-control-dashboard.web.app/templates.html"
