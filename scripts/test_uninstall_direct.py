#!/usr/bin/env python3
"""
Direct Firebase API test cho Remote Uninstall
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

def get_machine_id():
    """Lấy machine ID"""
    machine_id_file = Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'machine_id.json'
    
    with open(machine_id_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('id')

def send_uninstall_command():
    """Gửi lệnh uninstall qua Firebase API"""
    machine_id = get_machine_id()
    print(f"🎯 Machine ID: {machine_id}")
    
    # Firebase URL (sử dụng URL công khai)
    firebase_url = "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedb.app"
    
    command_data = {
        'type': 'uninstall',
        'timestamp': datetime.now().isoformat(),
        'executed': False,
        'params': {
            'reason': 'Direct API test from script',
            'test_id': f'test_{int(time.time())}'
        }
    }
    
    url = f"{firebase_url}/machines/{machine_id}/commands.json"
    
    try:
        print(f"📤 Sending uninstall command...")
        print(f"📋 URL: {url}")
        print(f"📋 Command: {command_data}")
        
        response = requests.post(url, json=command_data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        command_id = result['name']
        
        print(f"✅ Command sent successfully!")
        print(f"📋 Command ID: {command_id}")
        
        return command_id
        
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        return None

def monitor_execution(command_id, timeout=60):
    """Monitor command execution"""
    machine_id = get_machine_id()
    firebase_url = "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedb.app"
    url = f"{firebase_url}/machines/{machine_id}/commands/{command_id}.json"
    
    print(f"⏳ Monitoring command execution for {timeout} seconds...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            command_data = response.json()
            
            if command_data.get('executed', False):
                execution_time = time.time() - start_time
                print(f"✅ Command executed in {execution_time:.2f}s!")
                return True
            
            elapsed = time.time() - start_time
            print(f"⏳ Command not executed yet... ({elapsed:.1f}s)")
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error monitoring: {e}")
            time.sleep(3)
    
    print(f"❌ Command not executed within {timeout}s")
    return False

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

def main():
    print("🧪 Remote Uninstall Direct API Test")
    print("=" * 50)
    
    # Check initial status
    print("📊 Initial Status:")
    exe_count = check_exe_status()
    files_cleaned = check_app_files()
    
    if exe_count == 0:
        print("❌ No Hide4.exe processes found!")
        return
    
    print()
    
    # Send uninstall command
    command_id = send_uninstall_command()
    if not command_id:
        return
    
    print()
    
    # Monitor execution
    if monitor_execution(command_id, timeout=60):
        print()
        
        # Check final status
        print("📊 Final Status:")
        time.sleep(5)  # Wait a bit more
        
        exe_count = check_exe_status()
        files_cleaned = check_app_files()
        
        print()
        print("📋 Test Results:")
        print(f"✅ Command sent: Yes")
        print(f"✅ Command executed: Yes")
        print(f"{'✅' if exe_count == 0 else '❌'} Exe stopped: {exe_count == 0}")
        print(f"{'✅' if files_cleaned else '❌'} Files cleaned: {files_cleaned}")
        
        if exe_count == 0 and files_cleaned:
            print("\n🎉 Remote Uninstall Test PASSED!")
        else:
            print("\n⚠️ Remote Uninstall Test PARTIAL - some cleanup failed")
    else:
        print("\n❌ Remote Uninstall Test FAILED - command not executed")

if __name__ == '__main__':
    main()
