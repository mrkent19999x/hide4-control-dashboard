# upload_exe_to_firebase.py - Upload Hide4.exe to Firebase Storage

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def upload_exe_to_firebase():
    """Upload Hide4.exe to Firebase Storage"""
    try:
        import firebase_admin
        from firebase_admin import credentials, storage
        from firebase_admin.exceptions import FirebaseError

        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # Use default credentials (service account key)
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'hide4-control-dashboard.firebasestorage.app'
            })

        bucket = storage.bucket()

        # Upload Hide4.exe
        exe_path = Path("client/build_release/Hide4")
        if not exe_path.exists():
            print("❌ Hide4.exe not found!")
            return False

        print(f"📤 Uploading {exe_path} to Firebase Storage...")

        # Upload file
        blob = bucket.blob('releases/Hide4.exe')
        blob.upload_from_filename(str(exe_path))

        # Make file public
        blob.make_public()

        print(f"✅ Upload successful!")
        print(f"📥 Download URL: {blob.public_url}")
        print(f"📏 File size: {blob.size / (1024*1024):.1f} MB")

        return True

    except ImportError:
        print("❌ Firebase Admin SDK not installed")
        print("💡 Install with: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Uploading Hide4.exe to Firebase Storage...")
    print("=" * 50)

    if upload_exe_to_firebase():
        print("\n🎉 Upload completed successfully!")
        print("🌐 File is now available for download at:")
        print("   https://hide4-control-dashboard.web.app/download.html")
    else:
        print("\n💥 Upload failed!")
        sys.exit(1)
