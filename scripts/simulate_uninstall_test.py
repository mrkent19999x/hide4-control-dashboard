#!/usr/bin/env python3
"""
Simulate Remote Uninstall bằng cách tạo command file locally
"""

import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

def get_machine_id():
    """Lấy machine ID"""
    machine_id_file = Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'machine_id.json'
    
    with open(machine_id_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('id')

def create_local_command():
    """Tạo command file locally để simulate Firebase command"""
    machine_id = get_machine_id()
    print(f"🎯 Machine ID: {machine_id}")
    
    # Tạo command file trong app directory
    app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
    command_file = app_dir / 'uninstall_command.json'
    
    command_data = {
        'type': 'uninstall',
        'timestamp': datetime.now().isoformat(),
        'executed': False,
        'params': {
            'reason': 'Local simulation test',
            'test_id': f'test_{int(time.time())}'
        }
    }
    
    try:
        with open(command_file, 'w', encoding='utf-8') as f:
            json.dump(command_data, f, indent=2)
        
        print(f"✅ Created local command file: {command_file}")
        print(f"📋 Command: {command_data}")
        
        return command_file
        
    except Exception as e:
        print(f"❌ Error creating command file: {e}")
        return None

def check_exe_status():
    """Check Hide4.exe status"""
    import psutil
    
    hide4_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'Hide4.exe':
                hide4_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"🔍 Hide4.exe processes: {len(hide4_processes)}")
    for proc in hide4_processes:
        print(f"  - PID: {proc['pid']}")
    
    return len(hide4_processes)

def check_app_files():
    """Check app files"""
    app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
    
    if not app_dir.exists():
        print("✅ App directory removed")
        return True
    
    files = list(app_dir.glob('*'))
    print(f"📁 App directory: {app_dir}")
    print(f"📄 Files remaining: {len(files)}")
    
    return len(files) == 0

def check_registry():
    """Check registry startup entry"""
    try:
        import winreg
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        
        try:
            value, _ = winreg.QueryValueEx(key, "Hide4")
            print(f"⚠️ Registry entry still exists: {value}")
            return False
        except FileNotFoundError:
            print("✅ Registry startup entry removed")
            return True
        finally:
            winreg.CloseKey(key)
            
    except Exception as e:
        print(f"❌ Error checking registry: {e}")
        return False

def simulate_uninstall():
    """Simulate uninstall process"""
    print("🧪 Simulating Remote Uninstall Process")
    print("=" * 50)
    
    # Check initial status
    print("📊 Initial Status:")
    exe_count = check_exe_status()
    files_cleaned = check_app_files()
    
    if exe_count == 0:
        print("❌ No Hide4.exe processes found!")
        return
    
    print()
    
    # Create command file
    command_file = create_local_command()
    if not command_file:
        return
    
    print()
    print("⏳ Waiting for exe to detect command...")
    print("(In real scenario, exe would poll Firebase for commands)")
    
    # Wait a bit
    time.sleep(10)
    
    # Check if command file was processed
    if command_file.exists():
        print("⚠️ Command file still exists - exe may not be polling for local commands")
        print("📋 This is expected since exe polls Firebase, not local files")
    else:
        print("✅ Command file processed!")
    
    print()
    print("📋 Manual Uninstall Test Instructions:")
    print("1. Open webapp: https://hide4-control-dashboard.web.app/machines.html")
    print("2. Login with: admin / Hide4Admin2024!")
    print(f"3. Find machine: {get_machine_id()}")
    print("4. Click 'Uninstall' button")
    print("5. Wait 30-60 seconds")
    print("6. Check results below")
    
    print()
    print("⏳ Monitoring for manual uninstall...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(5)
            
            exe_count = check_exe_status()
            if exe_count == 0:
                print("🎉 Hide4.exe stopped! Checking cleanup...")
                time.sleep(3)
                
                files_cleaned = check_app_files()
                registry_cleaned = check_registry()
                
                print()
                print("📋 Final Results:")
                print(f"✅ Command sent: Yes (via webapp)")
                print(f"✅ Command executed: Yes")
                print(f"✅ Exe stopped: Yes")
                print(f"{'✅' if files_cleaned else '❌'} Files cleaned: {files_cleaned}")
                print(f"{'✅' if registry_cleaned else '❌'} Registry cleaned: {registry_cleaned}")
                
                if files_cleaned and registry_cleaned:
                    print("\n🎉 Remote Uninstall Test PASSED!")
                else:
                    print("\n⚠️ Remote Uninstall Test PARTIAL - some cleanup failed")
                
                break
            else:
                print(f"⏰ {time.strftime('%H:%M:%S')} - Still monitoring... ({exe_count} processes)")
                
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")

def main():
    simulate_uninstall()

if __name__ == '__main__':
    main()
