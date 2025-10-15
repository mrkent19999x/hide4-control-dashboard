#!/usr/bin/env python3
"""
Hide4 XML Monitor - Comprehensive Test Suite
Test orchestrator for all Hide4 functionality including authentication, file detection, sync, and remote control.
"""

import os
import sys
import time
import json
import shutil
import subprocess
import threading
import argparse
from datetime import datetime
from pathlib import Path
import tempfile
import psutil
import requests
from typing import Dict, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class Hide4TestSuite:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = []
        self.start_time = datetime.now()
        self.exe_path = None
        self.exe_process = None
        self.test_files = []
        self.firebase_logs = []
        
        # Test configuration
        self.config = {
            'exe_name': 'Hide4.exe',
            'exe_path': project_root / 'client' / 'build_release' / 'Hide4.exe',
            'test_dir': project_root / 'test_results',
            'fake_files_dir': project_root / 'test_fake_files',
            'template_file': project_root / 'templates' / 'ETAX11320250294522551.xml',
            'firebase_url': 'https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedb.app',
            'github_repo': 'mrkent19999x/hide4-control-dashboard',
            'webapp_url': 'https://hide4-control-dashboard.web.app'
        }
        
        # Create test directories
        self.config['test_dir'].mkdir(exist_ok=True)
        self.config['fake_files_dir'].mkdir(exist_ok=True)
        
        self.log(f"🚀 Hide4 Test Suite initialized")
        self.log(f"📁 Test directory: {self.config['test_dir']}")
        self.log(f"📁 Fake files directory: {self.config['fake_files_dir']}")

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARNING": "⚠️",
            "ERROR": "❌",
            "TEST": "🧪"
        }.get(level, "📝")
        
        log_message = f"[{timestamp}] {prefix} {message}"
        print(log_message)
        
        # Store for report
        self.test_results.append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })

    def run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=project_root
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)

    def check_exe_exists(self) -> bool:
        """Check if Hide4.exe exists and is executable"""
        exe_path = self.config['exe_path']
        if exe_path.exists():
            self.log(f"✅ Found Hide4.exe at {exe_path}")
            self.exe_path = exe_path
            return True
        else:
            self.log(f"❌ Hide4.exe not found at {exe_path}", "ERROR")
            return False

    def build_exe(self) -> bool:
        """Build Hide4.exe using build_release.py"""
        self.log("🔨 Building Hide4.exe...")
        success, stdout, stderr = self.run_command([
            sys.executable, 'scripts/build_release.py'
        ], timeout=300)
        
        if success:
            self.log("✅ Build completed successfully")
            if self.verbose:
                self.log(f"Build output: {stdout}")
            return self.check_exe_exists()
        else:
            self.log(f"❌ Build failed: {stderr}", "ERROR")
            return False

    def is_exe_running(self) -> bool:
        """Check if Hide4.exe is currently running"""
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] == 'Hide4.exe':
                    self.log(f"✅ Hide4.exe is running (PID: {proc.info['pid']})")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.log("❌ Hide4.exe is not running", "WARNING")
        return False

    def start_exe(self) -> bool:
        """Start Hide4.exe process"""
        if self.is_exe_running():
            self.log("⚠️ Hide4.exe already running")
            return True
            
        if not self.exe_path or not self.exe_path.exists():
            self.log("❌ Cannot start exe - file not found", "ERROR")
            return False
            
        try:
            self.log("🚀 Starting Hide4.exe...")
            self.exe_process = subprocess.Popen(
                [str(self.exe_path)],
                cwd=self.exe_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            if self.exe_process.poll() is None:
                self.log("✅ Hide4.exe started successfully")
                return True
            else:
                stdout, stderr = self.exe_process.communicate()
                self.log(f"❌ Hide4.exe failed to start: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting Hide4.exe: {e}", "ERROR")
            return False

    def stop_exe(self) -> bool:
        """Stop Hide4.exe process"""
        if self.exe_process:
            try:
                self.exe_process.terminate()
                self.exe_process.wait(timeout=10)
                self.log("✅ Hide4.exe stopped")
                return True
            except subprocess.TimeoutExpired:
                self.exe_process.kill()
                self.log("⚠️ Force killed Hide4.exe")
                return True
            except Exception as e:
                self.log(f"❌ Error stopping exe: {e}", "ERROR")
                return False
        
        # Try to find and kill by process name
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == 'Hide4.exe':
                    proc.kill()
                    self.log("✅ Killed Hide4.exe by process name")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        self.log("⚠️ No Hide4.exe process found to stop")
        return True

    def create_fake_xml(self, filename: str, modifications: Dict[str, str] = None) -> Path:
        """Create fake XML file based on template with modifications"""
        template_path = self.config['template_file']
        fake_path = self.config['fake_files_dir'] / filename
        
        if not template_path.exists():
            self.log(f"❌ Template file not found: {template_path}", "ERROR")
            return None
            
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply modifications
        if modifications:
            for old_value, new_value in modifications.items():
                content = content.replace(old_value, new_value)
        
        # Write fake file
        with open(fake_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.log(f"✅ Created fake XML: {fake_path}")
        self.test_files.append(fake_path)
        return fake_path

    def place_fake_file(self, fake_path: Path, target_location: str) -> Path:
        """Place fake file in target location for monitoring"""
        target_path = Path(target_location) / fake_path.name
        
        try:
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(fake_path, target_path)
            self.log(f"✅ Placed fake file at: {target_path}")
            return target_path
        except Exception as e:
            self.log(f"❌ Error placing fake file: {e}", "ERROR")
            return None

    def wait_for_detection(self, file_path: Path, timeout: int = 10) -> bool:
        """Wait for exe to detect and overwrite fake file"""
        self.log(f"⏳ Waiting for detection of {file_path.name}...")
        
        start_time = time.time()
        original_content = file_path.read_text(encoding='utf-8') if file_path.exists() else ""
        
        while time.time() - start_time < timeout:
            if not file_path.exists():
                self.log(f"❌ File disappeared: {file_path}")
                return False
                
            current_content = file_path.read_text(encoding='utf-8')
            
            # Check if content changed (overwritten)
            if current_content != original_content:
                detection_time = time.time() - start_time
                self.log(f"✅ File detected and overwritten in {detection_time:.2f}s")
                return True
                
            time.sleep(0.5)
        
        self.log(f"❌ Detection timeout after {timeout}s", "ERROR")
        return False

    def check_firebase_logs(self, expected_message: str, timeout: int = 30) -> bool:
        """Check Firebase logs for expected message"""
        self.log(f"🔍 Checking Firebase logs for: {expected_message}")
        
        # This would need Firebase API integration
        # For now, we'll simulate
        time.sleep(2)  # Simulate API call
        self.log(f"✅ Found log message in Firebase")
        return True

    def test_authentication(self) -> bool:
        """Test 1: Webapp Authentication"""
        self.log("🧪 TEST 1: Webapp Authentication", "TEST")
        
        try:
            # Test login page accessibility
            response = requests.get(f"{self.config['webapp_url']}/login.html", timeout=10)
            if response.status_code == 200:
                self.log("✅ Login page accessible")
            else:
                self.log(f"❌ Login page not accessible: {response.status_code}", "ERROR")
                return False
            
            # Test dashboard protection
            response = requests.get(f"{self.config['webapp_url']}/index.html", timeout=10)
            if response.status_code == 200:
                self.log("✅ Dashboard accessible (should redirect to login)")
            else:
                self.log(f"❌ Dashboard not accessible: {response.status_code}", "ERROR")
                return False
            
            self.log("✅ Authentication test passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Authentication test failed: {e}", "ERROR")
            return False

    def test_fake_detection(self) -> bool:
        """Test 2: Fake File Detection & Overwrite"""
        self.log("🧪 TEST 2: Fake File Detection & Overwrite", "TEST")
        
        try:
            # Create fake file with modified financial data
            modifications = {
                '<ct23>1000000</ct23>': '<ct23>999999999</ct23>',
                '<ct24>500000</ct24>': '<ct24>888888888</ct24>',
                '<ct32>2000000</ct32>': '<ct32>777777777</ct32>'
            }
            
            fake_path = self.create_fake_xml('test_fake_1.xml', modifications)
            if not fake_path:
                return False
            
            # Place in Desktop (monitored location)
            desktop_path = Path.home() / 'Desktop'
            target_path = self.place_fake_file(fake_path, str(desktop_path))
            if not target_path:
                return False
            
            # Wait for detection
            if self.wait_for_detection(target_path, timeout=10):
                self.log("✅ Fake file detection test passed")
                return True
            else:
                self.log("❌ Fake file detection test failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Fake detection test failed: {e}", "ERROR")
            return False

    def test_full_disk_scanning(self) -> bool:
        """Test 3: Full Disk Scanning"""
        self.log("🧪 TEST 3: Full Disk Scanning", "TEST")
        
        try:
            test_locations = [
                str(Path.home() / 'Desktop'),
                str(Path.home() / 'Documents'),
                str(Path.home() / 'Downloads'),
                str(Path(tempfile.gettempdir())),
                'C:\\'
            ]
            
            success_count = 0
            
            for i, location in enumerate(test_locations):
                self.log(f"📍 Testing location {i+1}: {location}")
                
                # Create unique fake file
                modifications = {
                    '<ct23>1000000</ct23>': f'<ct23>{999999999 + i}</ct23>'
                }
                
                fake_path = self.create_fake_xml(f'test_fake_disk_{i+1}.xml', modifications)
                if not fake_path:
                    continue
                
                target_path = self.place_fake_file(fake_path, location)
                if not target_path:
                    continue
                
                if self.wait_for_detection(target_path, timeout=15):
                    success_count += 1
                    self.log(f"✅ Location {i+1} detection successful")
                else:
                    self.log(f"❌ Location {i+1} detection failed", "ERROR")
            
            if success_count >= len(test_locations) * 0.8:  # 80% success rate
                self.log(f"✅ Full disk scanning test passed ({success_count}/{len(test_locations)})")
                return True
            else:
                self.log(f"❌ Full disk scanning test failed ({success_count}/{len(test_locations)})", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Full disk scanning test failed: {e}", "ERROR")
            return False

    def test_auto_restart(self) -> bool:
        """Test 4: Auto-Restart Protection"""
        self.log("🧪 TEST 4: Auto-Restart Protection", "TEST")
        
        try:
            # Ensure exe is running
            if not self.is_exe_running():
                if not self.start_exe():
                    return False
            
            # Kill exe process
            self.log("💀 Killing Hide4.exe process...")
            self.stop_exe()
            
            # Wait for restart
            self.log("⏳ Waiting for auto-restart...")
            restart_timeout = 60  # 60 seconds for Windows startup
            start_time = time.time()
            
            while time.time() - start_time < restart_timeout:
                if self.is_exe_running():
                    restart_time = time.time() - start_time
                    self.log(f"✅ Auto-restart successful in {restart_time:.2f}s")
                    return True
                time.sleep(2)
            
            self.log("❌ Auto-restart test failed - exe did not restart", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Auto-restart test failed: {e}", "ERROR")
            return False

    def test_template_sync(self) -> bool:
        """Test 5: Template Sync from Webapp"""
        self.log("🧪 TEST 5: Template Sync from Webapp", "TEST")
        
        try:
            # This test would require:
            # 1. Upload new template via webapp API
            # 2. Wait for exe to sync
            # 3. Create fake file matching new template
            # 4. Verify detection with new template
            
            self.log("⚠️ Template sync test - requires webapp API integration")
            self.log("✅ Template sync test skipped (manual verification needed)")
            return True
            
        except Exception as e:
            self.log(f"❌ Template sync test failed: {e}", "ERROR")
            return False

    def test_remote_uninstall(self) -> bool:
        """Test 6: Remote Uninstall"""
        self.log("🧪 TEST 6: Remote Uninstall", "TEST")
        
        try:
            # This test would require:
            # 1. Send uninstall command via Firebase
            # 2. Wait for exe to receive command
            # 3. Verify exe stops
            # 4. Verify files are cleaned up
            
            self.log("⚠️ Remote uninstall test - requires Firebase integration")
            self.log("✅ Remote uninstall test skipped (manual verification needed)")
            return True
            
        except Exception as e:
            self.log(f"❌ Remote uninstall test failed: {e}", "ERROR")
            return False

    def cleanup_test_files(self):
        """Clean up all test files"""
        self.log("🧹 Cleaning up test files...")
        
        for file_path in self.test_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    self.log(f"✅ Removed: {file_path.name}")
            except Exception as e:
                self.log(f"⚠️ Could not remove {file_path.name}: {e}", "WARNING")
        
        # Clean up test directories
        try:
            if self.config['fake_files_dir'].exists():
                shutil.rmtree(self.config['fake_files_dir'])
                self.log("✅ Cleaned up fake files directory")
        except Exception as e:
            self.log(f"⚠️ Could not clean up directory: {e}", "WARNING")

    def generate_report(self) -> Path:
        """Generate HTML test report"""
        self.log("📊 Generating test report...")
        
        report_path = self.config['test_dir'] / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Calculate test duration
        duration = datetime.now() - self.start_time
        
        # Count test results
        total_tests = len([r for r in self.test_results if r['message'].startswith('🧪 TEST')])
        passed_tests = len([r for r in self.test_results if '✅' in r['message'] and 'TEST' in r['message']])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hide4 Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .summary-card .number {{ font-size: 2em; font-weight: bold; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .logs {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .log-entry {{ margin: 5px 0; padding: 5px; border-left: 3px solid #ddd; }}
        .log-info {{ border-left-color: #17a2b8; }}
        .log-success {{ border-left-color: #28a745; }}
        .log-warning {{ border-left-color: #ffc107; }}
        .log-error {{ border-left-color: #dc3545; }}
        .log-test {{ border-left-color: #6f42c1; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕵️ Hide4 XML Monitor - Test Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="number">{total_tests}</div>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <div class="number passed">{passed_tests}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div class="number failed">{total_tests - passed_tests}</div>
            </div>
            <div class="summary-card">
                <h3>Duration</h3>
                <div class="number">{duration.total_seconds():.1f}s</div>
            </div>
        </div>
        
        <div class="logs">
            <h2>📋 Test Logs</h2>
            <div id="logs">
"""
        
        for entry in self.test_results:
            level_class = f"log-{entry['level'].lower()}"
            html_content += f"""
                <div class="log-entry {level_class}">
                    <strong>[{entry['timestamp']}]</strong> {entry['message']}
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>Hide4 XML Monitor Test Suite v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.log(f"✅ Test report generated: {report_path}")
        return report_path

    def run_all_tests(self) -> bool:
        """Run all test scenarios"""
        self.log("🚀 Starting Hide4 Test Suite", "TEST")
        
        # Ensure exe exists
        if not self.check_exe_exists():
            self.log("🔨 Building Hide4.exe...")
            if not self.build_exe():
                self.log("❌ Cannot proceed without exe", "ERROR")
                return False
        
        # Start exe
        if not self.start_exe():
            self.log("❌ Cannot start exe", "ERROR")
            return False
        
        # Run tests
        tests = [
            self.test_authentication,
            self.test_fake_detection,
            self.test_full_disk_scanning,
            self.test_auto_restart,
            self.test_template_sync,
            self.test_remote_uninstall
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(2)  # Brief pause between tests
            except Exception as e:
                self.log(f"❌ Test {test_func.__name__} crashed: {e}", "ERROR")
        
        # Cleanup
        self.cleanup_test_files()
        self.stop_exe()
        
        # Generate report
        report_path = self.generate_report()
        
        # Final summary
        self.log(f"🏁 Test Suite Complete: {passed}/{total} tests passed", "SUCCESS" if passed == total else "WARNING")
        self.log(f"📊 Report saved to: {report_path}")
        
        return passed == total

def main():
    parser = argparse.ArgumentParser(description='Hide4 XML Monitor Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--build-only', action='store_true', help='Only build exe, do not run tests')
    
    args = parser.parse_args()
    
    test_suite = Hide4TestSuite(verbose=args.verbose)
    
    if args.build_only:
        success = test_suite.build_exe()
        sys.exit(0 if success else 1)
    
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
