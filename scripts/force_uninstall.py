#!/usr/bin/env python3
"""
Force Uninstall Script - Clean up Hide4 completely
"""

import os
import time
import shutil
import subprocess
from pathlib import Path

def force_kill_hide4():
    """Force kill Hide4 processes"""
    import psutil
    
    print("💀 Force killing Hide4 processes...")
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'Hide4.exe':
                print(f"🔪 Killing PID: {proc.info['pid']}")
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    
    print(f"✅ Killed {killed_count} Hide4 processes")
    return killed_count > 0

def remove_registry_entry():
    """Remove registry startup entry"""
    try:
        import winreg
        
        print("🔧 Removing registry startup entry...")
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        
        try:
            winreg.DeleteValue(key, "Hide4")
            print("✅ Registry entry removed")
            return True
        except FileNotFoundError:
            print("ℹ️ Registry entry not found")
            return True
        finally:
            winreg.CloseKey(key)
            
    except Exception as e:
        print(f"❌ Error removing registry: {e}")
        return False

def remove_app_files():
    """Remove app files"""
    app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
    
    if not app_dir.exists():
        print("ℹ️ App directory not found")
        return True
    
    print(f"🗑️ Removing app directory: {app_dir}")
    
    try:
        shutil.rmtree(app_dir)
        print("✅ App directory removed")
        return True
    except Exception as e:
        print(f"❌ Error removing app directory: {e}")
        return False

def remove_exe_file():
    """Remove exe file"""
    exe_path = Path("client/build_release/Hide4.exe")
    
    if not exe_path.exists():
        print("ℹ️ Exe file not found")
        return True
    
    print(f"🗑️ Removing exe file: {exe_path}")
    
    try:
        exe_path.unlink()
        print("✅ Exe file removed")
        return True
    except Exception as e:
        print(f"❌ Error removing exe file: {e}")
        return False

def verify_cleanup():
    """Verify cleanup is complete"""
    import psutil
    
    print("\n🔍 Verifying cleanup...")
    
    # Check processes
    hide4_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'Hide4.exe':
                hide4_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    processes_cleaned = len(hide4_processes) == 0
    print(f"{'✅' if processes_cleaned else '❌'} Processes: {len(hide4_processes)}")
    
    # Check app files
    app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
    files_cleaned = not app_dir.exists()
    print(f"{'✅' if files_cleaned else '❌'} App files: {'Removed' if files_cleaned else 'Still exist'}")
    
    # Check registry
    registry_cleaned = True
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, "Hide4")
            registry_cleaned = False
        except FileNotFoundError:
            registry_cleaned = True
        finally:
            winreg.CloseKey(key)
    except Exception:
        registry_cleaned = True
    
    print(f"{'✅' if registry_cleaned else '❌'} Registry: {'Removed' if registry_cleaned else 'Still exists'}")
    
    # Check exe file
    exe_path = Path("client/build_release/Hide4.exe")
    exe_cleaned = not exe_path.exists()
    print(f"{'✅' if exe_cleaned else '❌'} Exe file: {'Removed' if exe_cleaned else 'Still exists'}")
    
    return processes_cleaned and files_cleaned and registry_cleaned and exe_cleaned

def main():
    print("🧹 Hide4 Force Uninstall")
    print("=" * 50)
    
    # Step 1: Force kill processes
    if not force_kill_hide4():
        print("⚠️ No Hide4 processes found")
    
    time.sleep(2)
    
    # Step 2: Remove registry entry
    remove_registry_entry()
    
    # Step 3: Remove app files
    remove_app_files()
    
    # Step 4: Remove exe file
    remove_exe_file()
    
    # Step 5: Verify cleanup
    if verify_cleanup():
        print("\n🎉 Force uninstall completed successfully!")
        print("✅ All Hide4 components removed")
    else:
        print("\n⚠️ Force uninstall completed with some issues")
        print("📋 Check the verification results above")

if __name__ == '__main__':
    main()
