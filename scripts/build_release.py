# build_release.py - Build Release Script with Embedded Config

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_release():
    """Build release exe với embedded config"""
    print("🚀 BUILDING HIDE4 RELEASE")
    print("=" * 50)

    # Check if we're in the right directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    icon_script = project_root / 'client' / 'icon.py'

    if not icon_script.exists():
        print("❌ Không tìm thấy client/icon.py. Vui lòng chạy từ thư mục scripts/.")
        return False

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt. Đang cài đặt...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

    # Create build directory
    build_dir = project_root / 'client' / 'build_release'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single exe file
        '--windowed',  # No console window
        '--name', 'Hide4',
        '--distpath', str(build_dir),
        '--workpath', str(build_dir / 'work'),
        '--specpath', str(build_dir),
        '--add-data', f'{project_root / "client" / "config_embedded.py"}:.',
        '--add-data', f'{project_root / "client" / "firebase_logger.py"}:.',
        '--add-data', f'{project_root / "client" / "firebase_storage.py"}:.',
        '--add-data', f'{project_root / "client" / "machine_manager.py"}:.',
        '--add-data', f'{project_root / "client" / "xml_fingerprint.py"}:.',
        '--hidden-import', 'requests',
        '--hidden-import', 'watchdog',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'config_embedded',
        '--hidden-import', 'firebase_logger',
        '--hidden-import', 'firebase_storage',
        '--hidden-import', 'machine_manager',
        '--hidden-import', 'xml_fingerprint',
        str(icon_script)
    ]

    print("🔨 Đang build exe...")
    print(f"Command: {' '.join(cmd)}")

    try:
        # Change to project root directory for PyInstaller
        os.chdir(project_root)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build thành công!")

        # Check if exe was created (Linux creates without .exe extension)
        exe_path = build_dir / 'Hide4'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Exe created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")

            # Create release info
            create_release_info(build_dir, exe_path)

            return True
        else:
            print("❌ Exe không được tạo")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build thất bại: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_release_info(build_dir: Path, exe_path: Path):
    """Tạo thông tin release"""
    release_info = {
        "version": "3.0.0",
        "build_date": str(Path().cwd()),
        "exe_size": exe_path.stat().st_size,
        "features": [
            "Firebase Realtime Database integration",
            "Firebase Storage templates sync",
            "Web Dashboard control",
            "Auto-sync templates every 30 minutes",
            "No external config needed",
            "PWA Dashboard support"
        ],
        "requirements": {
            "os": "Windows 10/11",
            "admin": "Required for file monitoring",
            "internet": "Required for Firebase sync"
        },
        "installation": {
            "step1": "Download Hide4.exe",
            "step2": "Right-click → Run as Administrator",
            "step3": "Exe will auto-sync templates from Firebase",
            "step4": "Monitor via webapp: https://hide4-control-dashboard.web.app"
        }
    }

    import json
    info_file = build_dir / 'release_info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(release_info, f, indent=2, ensure_ascii=False)

    print(f"📋 Release info created: {info_file}")

def test_exe(exe_path: Path):
    """Test exe trên Windows (placeholder)"""
    print(f"🧪 Testing exe: {exe_path}")
    print("⚠️ Note: Exe testing requires Windows environment")
    print("   - Copy exe to Windows machine")
    print("   - Run as Administrator")
    print("   - Check Firebase Dashboard for logs")

def upload_to_firebase_storage(exe_path: Path):
    """Upload exe lên Firebase Storage (placeholder)"""
    print(f"☁️ Upload exe to Firebase Storage: {exe_path}")
    print("⚠️ Note: Firebase Storage upload requires:")
    print("   1. Enable Firebase Storage in console")
    print("   2. Configure storage rules")
    print("   3. Use Firebase CLI or web interface")

def main():
    """Main build process"""
    print("🎯 HIDE4 RELEASE BUILDER")
    print("=" * 50)

    # Build exe
    if not build_release():
        print("❌ Build failed!")
        return

    build_dir = Path('build_release')
    exe_path = build_dir / 'Hide4.exe'

    if exe_path.exists():
        print("\n🎉 BUILD SUCCESSFUL!")
        print("=" * 50)
        print(f"📦 Exe location: {exe_path.absolute()}")
        print(f"📏 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")

        print("\n📋 NEXT STEPS:")
        print("1. Test exe on Windows machine")
        print("2. Upload exe to Firebase Storage")
        print("3. Create download page on webapp")
        print("4. Send download link to customers")

        print("\n🌐 WEBAPP:")
        print("https://hide4-control-dashboard.web.app")
        print("- Upload XML templates")
        print("- Monitor all machines")
        print("- Remote control")

        print("\n✅ Release ready for distribution!")

if __name__ == "__main__":
    main()
