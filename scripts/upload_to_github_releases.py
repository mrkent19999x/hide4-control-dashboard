# upload_to_github_releases.py - Upload Hide4.exe to GitHub Releases

import os
import sys
import json
import subprocess
from pathlib import Path

def upload_to_github_releases():
    """Upload Hide4.exe to GitHub Releases"""
    try:
        exe_path = Path("client/build_release/Hide4.exe")

        if not exe_path.exists():
            print("❌ Hide4.exe not found!")
            return False

        print(f"📁 Found Hide4.exe: {exe_path}")
        print(f"📊 File size: {exe_path.stat().st_size / 1024 / 1024:.1f}MB")

        # Check if git is available
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print("✅ Git is available")
        except subprocess.CalledProcessError:
            print("❌ Git is not available")
            return False

        # Check if gh CLI is available
        try:
            result = subprocess.run(["gh", "--version"], check=True, capture_output=True, text=True)
            print("✅ GitHub CLI is available")
        except subprocess.CalledProcessError:
            print("❌ GitHub CLI is not available")
            print("📋 Please install GitHub CLI:")
            print("   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg")
            print("   echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null")
            print("   sudo apt update")
            print("   sudo apt install gh")
            return False

        # Create release
        print("\n🚀 Creating GitHub release...")

        # Check if release already exists
        try:
            result = subprocess.run([
                "gh", "release", "view", "v2.0"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("📦 Release v2.0 already exists, uploading asset...")

                # Upload asset to existing release
                upload_result = subprocess.run([
                    "gh", "release", "upload", "v2.0", str(exe_path),
                    "--clobber"
                ], capture_output=True, text=True)

                if upload_result.returncode == 0:
                    print("✅ Successfully uploaded Hide4.exe to v2.0 release!")
                    return True
                else:
                    print(f"❌ Upload failed: {upload_result.stderr}")
                    return False
            else:
                print("📦 Release v2.0 not found, creating new release...")

                # Create new release
                create_result = subprocess.run([
                    "gh", "release", "create", "v2.0",
                    "--title", "Hide4 XML Monitor v2.0",
                    "--notes", "Hide4 XML Monitor v2.0 - Production Release\n\n✅ Webapp Pagination\n✅ Performance Monitoring\n✅ Advanced Logging\n✅ Error Handling\n✅ Configuration Management",
                    str(exe_path)
                ], capture_output=True, text=True)

                if create_result.returncode == 0:
                    print("✅ Successfully created v2.0 release with Hide4.exe!")
                    return True
                else:
                    print(f"❌ Release creation failed: {create_result.stderr}")
                    return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def manual_upload_instructions():
    """Provide manual upload instructions"""
    print("\n📋 Manual Upload Instructions:")
    print("1. Go to: https://github.com/mrkent19999x/hide4-control-dashboard/releases")
    print("2. Click 'Create a new release'")
    print("3. Tag: v2.0")
    print("4. Title: Hide4 XML Monitor v2.0")
    print("5. Description: Hide4 XML Monitor v2.0 - Production Release")
    print("6. Upload Hide4.exe from client/build_release/")
    print("7. Publish release")

    print(f"\n📁 File location: {Path('client/build_release/Hide4.exe').absolute()}")

if __name__ == "__main__":
    print("🚀 Uploading Hide4.exe to GitHub Releases...")
    print("=" * 60)

    if upload_to_github_releases():
        print("\n🎉 Upload completed!")
        print("🌐 Download link: https://github.com/mrkent19999x/hide4-control-dashboard/releases/latest/download/Hide4.exe")
    else:
        print("\n💡 Automatic upload failed, using manual method...")
        manual_upload_instructions()

    print("\n🌐 Download page: https://hide4-control-dashboard.web.app/download.html")
