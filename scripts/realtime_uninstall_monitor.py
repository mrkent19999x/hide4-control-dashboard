#!/usr/bin/env python3
"""
Real-time monitor cho Remote Uninstall test
"""

import os
import time
import json
from pathlib import Path
import psutil

def get_machine_info():
    """Lấy thông tin machine"""
    machine_id_file = Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'machine_id.json'
    
    if not machine_id_file.exists():
        return None
        
    with open(machine_id_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_exe_processes():
    """Check Hide4.exe processes"""
    hide4_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'] == 'Hide4.exe':
                hide4_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return hide4_processes

def check_app_files():
    """Check app files"""
    app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
    
    if not app_dir.exists():
        return True, 0  # Cleaned
    
    files = list(app_dir.glob('*'))
    return False, len(files)  # Not cleaned, file count

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
            return False, value  # Not cleaned
        except FileNotFoundError:
            return True, None  # Cleaned
        finally:
            winreg.CloseKey(key)
            
    except Exception as e:
        return False, str(e)  # Error

def main():
    print("🔍 Real-time Remote Uninstall Monitor")
    print("=" * 50)
    
    # Get initial info
    machine_info = get_machine_info()
    if machine_info:
        print(f"🎯 Machine ID: {machine_info.get('id')}")
        print(f"🎯 Hostname: {machine_info.get('hostname')}")
    else:
        print("❌ Machine info not found")
        return
    
    print()
    print("📋 Instructions:")
    print("1. Open webapp: https://hide4-control-dashboard.web.app/machines.html")
    print("2. Login with: admin / Hide4Admin2024!")
    print(f"3. Find machine: {machine_info.get('hostname')}")
    print("4. Click 'Uninstall' button")
    print("5. Watch this monitor for results")
    print()
    
    # Initial status
    processes = check_exe_processes()
    files_cleaned, file_count = check_app_files()
    registry_cleaned, registry_value = check_registry()
    
    print("📊 Initial Status:")
    print(f"🔍 Hide4.exe processes: {len(processes)}")
    print(f"📁 App files: {file_count} files")
    print(f"🔧 Registry entry: {'Removed' if registry_cleaned else 'Exists'}")
    print()
    
    print("⏳ Monitoring for changes...")
    print("Press Ctrl+C to stop")
    
    start_time = time.time()
    
    try:
        while True:
            time.sleep(2)
            
            # Check processes
            current_processes = check_exe_processes()
            
            # Check files
            current_files_cleaned, current_file_count = check_app_files()
            
            # Check registry
            current_registry_cleaned, current_registry_value = check_registry()
            
            # Detect changes
            process_changed = len(current_processes) != len(processes)
            files_changed = current_files_cleaned != files_cleaned or current_file_count != file_count
            registry_changed = current_registry_cleaned != registry_cleaned
            
            if process_changed or files_changed or registry_changed:
                elapsed = time.time() - start_time
                print(f"\n🎉 CHANGE DETECTED at {elapsed:.1f}s!")
                
                if process_changed:
                    print(f"🔍 Processes: {len(processes)} → {len(current_processes)}")
                    if len(current_processes) == 0:
                        print("✅ Hide4.exe STOPPED!")
                
                if files_changed:
                    print(f"📁 Files: {file_count} → {current_file_count}")
                    if current_files_cleaned:
                        print("✅ App files CLEANED!")
                
                if registry_changed:
                    print(f"🔧 Registry: {'Exists' if not registry_cleaned else 'Removed'} → {'Exists' if not current_registry_cleaned else 'Removed'}")
                    if current_registry_cleaned:
                        print("✅ Registry entry REMOVED!")
                
                # Update status
                processes = current_processes
                files_cleaned = current_files_cleaned
                file_count = current_file_count
                registry_cleaned = current_registry_cleaned
                
                # Check if uninstall complete
                if len(current_processes) == 0 and current_files_cleaned and current_registry_cleaned:
                    print("\n🎉 REMOTE UNINSTALL COMPLETED SUCCESSFULLY!")
                    print("✅ All components cleaned up")
                    break
                elif len(current_processes) == 0:
                    print("\n⚠️ Exe stopped but cleanup incomplete")
                    print("📋 Checking remaining files...")
                    
                    if not current_files_cleaned:
                        print(f"📁 {current_file_count} files still remain")
                    
                    if not current_registry_cleaned:
                        print(f"🔧 Registry entry still exists")
            
            # Show periodic status
            if int(time.time()) % 10 == 0:  # Every 10 seconds
                elapsed = time.time() - start_time
                print(f"⏰ {elapsed:.0f}s - Processes: {len(current_processes)}, Files: {current_file_count}")
                
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")
        
        # Final status
        print("\n📊 Final Status:")
        final_processes = check_exe_processes()
        final_files_cleaned, final_file_count = check_app_files()
        final_registry_cleaned, _ = check_registry()
        
        print(f"🔍 Hide4.exe processes: {len(final_processes)}")
        print(f"📁 App files: {final_file_count} files")
        print(f"🔧 Registry entry: {'Removed' if final_registry_cleaned else 'Exists'}")
        
        if len(final_processes) == 0 and final_files_cleaned and final_registry_cleaned:
            print("\n🎉 Remote Uninstall Test PASSED!")
        else:
            print("\n⚠️ Remote Uninstall Test INCOMPLETE")

if __name__ == '__main__':
    main()
