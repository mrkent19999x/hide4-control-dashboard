#!/usr/bin/env python3
"""
Simple manual test cho Remote Uninstall
"""

import os
import json
import time
from pathlib import Path

def get_machine_info():
    """Lấy thông tin machine"""
    machine_id_file = Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'machine_id.json'
    
    if not machine_id_file.exists():
        print("❌ Machine ID file not found!")
        return None
        
    try:
        with open(machine_id_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Machine ID: {data.get('id')}")
            print(f"✅ Hostname: {data.get('hostname')}")
            print(f"✅ Install Date: {data.get('install_date')}")
            return data
    except Exception as e:
        print(f"❌ Error reading machine ID: {e}")
        return None

def check_exe_processes():
    """Check Hide4.exe processes"""
    import psutil
    
    hide4_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'] == 'Hide4.exe':
                hide4_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"🔍 Found {len(hide4_processes)} Hide4.exe processes:")
    for proc in hide4_processes:
        print(f"  - PID: {proc['pid']}")
    
    return hide4_processes

def check_app_files():
    """Check app files"""
    app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
    
    if not app_dir.exists():
        print("❌ App directory not found!")
        return False
    
    files = list(app_dir.glob('*'))
    print(f"📁 App directory: {app_dir}")
    print(f"📄 Files ({len(files)}):")
    for file in files:
        if file.is_file():
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
        else:
            print(f"  - {file.name}/ (directory)")
    
    return True

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
            print(f"✅ Registry startup entry exists: {value}")
            return True
        except FileNotFoundError:
            print("❌ Registry startup entry not found")
            return False
        finally:
            winreg.CloseKey(key)
            
    except Exception as e:
        print(f"❌ Error checking registry: {e}")
        return False

def main():
    print("🔍 Hide4 Remote Uninstall Manual Test")
    print("=" * 50)
    
    # Get machine info
    machine_info = get_machine_info()
    if not machine_info:
        return
    
    print()
    
    # Check exe processes
    processes = check_exe_processes()
    
    print()
    
    # Check app files
    check_app_files()
    
    print()
    
    # Check registry
    check_registry()
    
    print()
    print("📋 Manual Test Instructions:")
    print("1. Open webapp: https://hide4-control-dashboard.web.app/machines.html")
    print("2. Login with: admin / Hide4Admin2024!")
    print(f"3. Find machine: {machine_info.get('hostname')} ({machine_info.get('id')})")
    print("4. Click 'Uninstall' button")
    print("5. Wait 30-60 seconds")
    print("6. Run this script again to check results")
    
    print()
    print("⏳ Waiting for manual test...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            time.sleep(10)
            print(f"⏰ {time.strftime('%H:%M:%S')} - Still monitoring...")
            
            # Check if exe stopped
            current_processes = check_exe_processes()
            if len(current_processes) == 0:
                print("🎉 Hide4.exe stopped! Checking cleanup...")
                time.sleep(5)
                
                # Check files
                check_app_files()
                
                # Check registry
                check_registry()
                
                print("✅ Manual test completed!")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")

if __name__ == '__main__':
    main()
