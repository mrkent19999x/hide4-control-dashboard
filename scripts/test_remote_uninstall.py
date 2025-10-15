#!/usr/bin/env python3
"""
Manual test script cho Remote Uninstall functionality
"""

import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime

class RemoteUninstallTester:
    def __init__(self):
        self.firebase_url = "https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedb.app"
        self.machine_id = None
        self.test_results = []
        
    def get_machine_id(self):
        """Lấy machine ID từ file"""
        machine_id_file = Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'machine_id.json'
        
        if not machine_id_file.exists():
            print("❌ Machine ID file not found!")
            return None
            
        try:
            with open(machine_id_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.machine_id = data.get('id')
                print(f"✅ Machine ID: {self.machine_id}")
                return self.machine_id
        except Exception as e:
            print(f"❌ Error reading machine ID: {e}")
            return None
    
    def check_exe_running(self):
        """Check xem exe có đang chạy không"""
        import psutil
        
        hide4_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == 'Hide4.exe':
                    hide4_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"🔍 Found {len(hide4_processes)} Hide4.exe processes")
        return len(hide4_processes) > 0
    
    def send_uninstall_command(self):
        """Gửi lệnh uninstall qua Firebase"""
        if not self.machine_id:
            print("❌ No machine ID available")
            return False
            
        command_data = {
            'type': 'uninstall',
            'timestamp': datetime.now().isoformat(),
            'executed': False,
            'params': {
                'reason': 'Manual test from debug script',
                'test_id': f'test_{int(time.time())}'
            }
        }
        
        url = f"{self.firebase_url}/machines/{self.machine_id}/commands.json"
        
        try:
            response = requests.post(url, json=command_data, timeout=10)
            response.raise_for_status()
            
            command_id = response.json()['name']
            print(f"✅ Uninstall command sent successfully")
            print(f"📋 Command ID: {command_id}")
            print(f"📋 Command data: {command_data}")
            
            return command_id
            
        except Exception as e:
            print(f"❌ Error sending uninstall command: {e}")
            return None
    
    def monitor_command_execution(self, command_id, timeout=60):
        """Monitor xem command có được execute không"""
        print(f"⏳ Monitoring command execution for {timeout} seconds...")
        
        url = f"{self.firebase_url}/machines/{self.machine_id}/commands/{command_id}.json"
        
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
                
                print(f"⏳ Command not executed yet... ({time.time() - start_time:.1f}s)")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Error monitoring command: {e}")
                time.sleep(5)
        
        print(f"❌ Command not executed within {timeout}s")
        return False
    
    def check_exe_stopped(self):
        """Check xem exe có dừng không"""
        import psutil
        
        hide4_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == 'Hide4.exe':
                    hide4_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if len(hide4_processes) == 0:
            print("✅ Hide4.exe stopped successfully")
            return True
        else:
            print(f"⚠️ Hide4.exe still running ({len(hide4_processes)} processes)")
            return False
    
    def check_files_cleaned(self):
        """Check xem files có được clean up không"""
        app_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite'
        
        if not app_dir.exists():
            print("✅ App directory removed completely")
            return True
        
        remaining_files = list(app_dir.glob('*'))
        if len(remaining_files) == 0:
            print("✅ All files cleaned up")
            return True
        else:
            print(f"⚠️ {len(remaining_files)} files still remain:")
            for file in remaining_files:
                print(f"  - {file.name}")
            return False
    
    def check_registry_cleaned(self):
        """Check xem registry startup entry có được xóa không"""
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
    
    def run_test(self):
        """Chạy toàn bộ test"""
        print("🧪 Remote Uninstall Test")
        print("=" * 50)
        
        # Step 1: Get machine ID
        if not self.get_machine_id():
            return False
        
        # Step 2: Check exe is running
        if not self.check_exe_running():
            print("❌ Hide4.exe not running - cannot test uninstall")
            return False
        
        # Step 3: Send uninstall command
        command_id = self.send_uninstall_command()
        if not command_id:
            return False
        
        # Step 4: Monitor command execution
        if not self.monitor_command_execution(command_id, timeout=60):
            print("❌ Command execution timeout")
            return False
        
        # Step 5: Check exe stopped
        time.sleep(5)  # Wait a bit more
        exe_stopped = self.check_exe_stopped()
        
        # Step 6: Check files cleaned
        files_cleaned = self.check_files_cleaned()
        
        # Step 7: Check registry cleaned
        registry_cleaned = self.check_registry_cleaned()
        
        # Summary
        print("\n📊 Test Results:")
        print(f"✅ Command sent: Yes")
        print(f"✅ Command executed: Yes")
        print(f"{'✅' if exe_stopped else '❌'} Exe stopped: {exe_stopped}")
        print(f"{'✅' if files_cleaned else '❌'} Files cleaned: {files_cleaned}")
        print(f"{'✅' if registry_cleaned else '❌'} Registry cleaned: {registry_cleaned}")
        
        success = exe_stopped and files_cleaned and registry_cleaned
        
        if success:
            print("\n🎉 Remote Uninstall Test PASSED!")
        else:
            print("\n❌ Remote Uninstall Test FAILED!")
        
        return success

def main():
    tester = RemoteUninstallTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n⚠️ Some tests failed - check logs above")
    
    return success

if __name__ == '__main__':
    main()
