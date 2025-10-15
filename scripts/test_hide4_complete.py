#!/usr/bin/env python3
"""
Hide4 XML Monitor - Complete Test Suite
Test đầy đủ chức năng phát hiện và ghi đè file fake của Hide4.exe
"""

import os
import sys
import time
import json
import shutil
import subprocess
import threading
import tempfile
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import xml.etree.ElementTree as ET

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'client'))

from client.xml_fingerprint import XMLFingerprint

class Hide4CompleteTestSuite:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.test_results = []
        self.start_time = datetime.now()
        self.exe_path = None
        self.exe_process = None
        self.test_files = []
        self.log_file = None
        self.templates_dir = project_root / 'templates'
        self.xml_fp = None
        
        # Test configuration
        self.config = {
            'exe_name': 'Hide4.exe',
            'exe_path': project_root / 'client' / 'build_release' / 'Hide4.exe',
            'test_dir': project_root / 'test_results',
            'fake_files_dir': project_root / 'test_fake_files',
            'log_file': Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite' / 'xml_overwrite.log',
            'desktop_path': Path.home() / 'Desktop',
            'documents_path': Path.home() / 'Documents',
            'downloads_path': Path.home() / 'Downloads'
        }
        
        # Create test directories
        self.config['test_dir'].mkdir(exist_ok=True)
        self.config['fake_files_dir'].mkdir(exist_ok=True)
        
        self.log(f"🚀 Hide4 Complete Test Suite initialized")
        self.log(f"📁 Test directory: {self.config['test_dir']}")
        self.log(f"📁 Fake files directory: {self.config['fake_files_dir']}")
        self.log(f"📁 Log file: {self.config['log_file']}")

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

    def check_environment(self) -> bool:
        """Kiểm tra môi trường test"""
        self.log("🔍 Checking test environment...", "TEST")
        
        # Check Hide4.exe
        if not self.config['exe_path'].exists():
            self.log(f"❌ Hide4.exe not found at {self.config['exe_path']}", "ERROR")
            return False
        else:
            size_mb = self.config['exe_path'].stat().st_size / (1024 * 1024)
            self.log(f"✅ Found Hide4.exe: {self.config['exe_path']} ({size_mb:.1f} MB)")
        
        # Check templates
        if not self.templates_dir.exists():
            self.log(f"❌ Templates directory not found: {self.templates_dir}", "ERROR")
            return False
        
        template_files = list(self.templates_dir.glob('*.xml'))
        if not template_files:
            self.log(f"❌ No XML templates found in {self.templates_dir}", "ERROR")
            return False
        
        self.log(f"✅ Found {len(template_files)} templates")
        
        # Initialize XML fingerprint
        try:
            self.xml_fp = XMLFingerprint(str(self.templates_dir))
            templates = self.xml_fp.get_all_templates()
            self.log(f"✅ XML Fingerprint initialized with {len(templates)} templates")
            
            # Show sample fingerprint
            sample_template = templates[0]
            sample_fp = self.xml_fp.get_template_info(sample_template)
            self.log(f"📋 Sample fingerprint: MST={sample_fp['mst']}, maTKhai={sample_fp['maTKhai']}, kieuKy={sample_fp['kieuKy']}, kyKKhai={sample_fp['kyKKhai']}")
            
        except Exception as e:
            self.log(f"❌ Failed to initialize XML fingerprint: {e}", "ERROR")
            return False
        
        return True

    def create_fake_xml(self, template_name: str, modifications: Dict[str, str] = None) -> Path:
        """Tạo fake XML file với cùng fingerprint nhưng khác nội dung financial"""
        template_path = self.templates_dir / f"{template_name}.xml"
        fake_path = self.config['fake_files_dir'] / f"fake_{template_name}_{int(time.time())}.xml"
        
        if not template_path.exists():
            self.log(f"❌ Template file not found: {template_path}", "ERROR")
            return None
            
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply modifications (chỉ thay đổi financial data, giữ nguyên fingerprint)
        if modifications:
            for old_value, new_value in modifications.items():
                content = content.replace(old_value, new_value)
        else:
            # Default modifications để tạo fake data
            content = content.replace('<ct23>3354565834</ct23>', '<ct23>9999999999</ct23>')
            content = content.replace('<ct24>268365267</ct24>', '<ct24>888888888</ct24>')
            content = content.replace('<ct32>3958957398</ct32>', '<ct32>7777777777</ct32>')
        
        # Write fake file
        with open(fake_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.log(f"✅ Created fake XML: {fake_path.name}")
        self.test_files.append(fake_path)
        return fake_path

    def place_fake_file(self, fake_path: Path, target_location: Path) -> Path:
        """Đặt fake file vào vị trí target"""
        target_path = target_location / fake_path.name
        
        try:
            # Ensure target directory exists
            target_location.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(fake_path, target_path)
            self.log(f"✅ Placed fake file at: {target_path}")
            return target_path
        except Exception as e:
            self.log(f"❌ Error placing fake file: {e}", "ERROR")
            return None

    def start_hide4(self) -> bool:
        """Start Hide4.exe process"""
        if self.is_hide4_running():
            self.log("⚠️ Hide4.exe already running")
            return True
            
        if not self.config['exe_path'].exists():
            self.log("❌ Cannot start exe - file not found", "ERROR")
            return False
            
        try:
            self.log("🚀 Starting Hide4.exe...")
            self.exe_process = subprocess.Popen(
                [str(self.config['exe_path'])],
                cwd=self.config['exe_path'].parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(5)
            
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

    def is_hide4_running(self) -> bool:
        """Check if Hide4.exe is running"""
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] == 'Hide4.exe':
                    self.log(f"✅ Hide4.exe is running (PID: {proc.info['pid']})")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.log("❌ Hide4.exe is not running", "WARNING")
        return False

    def stop_hide4(self) -> bool:
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

    def monitor_file_changes(self, file_path: Path, timeout: int = 15) -> Tuple[bool, str]:
        """Monitor file changes để detect overwrite"""
        self.log(f"👀 Monitoring file: {file_path.name}")
        
        if not file_path.exists():
            return False, "File does not exist"
        
        # Read original content
        original_content = file_path.read_text(encoding='utf-8')
        original_size = len(original_content)
        
        start_time = time.time()
        last_modified = file_path.stat().st_mtime
        
        while time.time() - start_time < timeout:
            if not file_path.exists():
                return False, "File disappeared"
            
            current_mtime = file_path.stat().st_mtime
            if current_mtime > last_modified:
                # File was modified, check content
                try:
                    current_content = file_path.read_text(encoding='utf-8')
                    if current_content != original_content:
                        detection_time = time.time() - start_time
                        self.log(f"✅ File content changed after {detection_time:.2f}s")
                        return True, f"Content changed after {detection_time:.2f}s"
                except Exception as e:
                    self.log(f"⚠️ Error reading file: {e}", "WARNING")
            
            time.sleep(0.5)
        
        return False, f"Timeout after {timeout}s"

    def verify_file_overwrite(self, file_path: Path, template_name: str) -> bool:
        """Verify file đã được ghi đè bằng template"""
        template_path = self.templates_dir / f"{template_name}.xml"
        
        if not file_path.exists() or not template_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            if file_content == template_content:
                self.log(f"✅ File overwrite verified: {file_path.name}")
                return True
            else:
                self.log(f"❌ File content does not match template: {file_path.name}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error verifying file: {e}", "ERROR")
            return False

    def check_log_entries(self, expected_patterns: List[str]) -> Dict[str, bool]:
        """Check log file for expected entries"""
        log_file = self.config['log_file']
        
        if not log_file.exists():
            self.log(f"⚠️ Log file not found: {log_file}", "WARNING")
            return {pattern: False for pattern in expected_patterns}
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            results = {}
            for pattern in expected_patterns:
                found = pattern in log_content
                results[pattern] = found
                if found:
                    self.log(f"✅ Found log entry: {pattern}")
                else:
                    self.log(f"❌ Missing log entry: {pattern}", "ERROR")
            
            return results
            
        except Exception as e:
            self.log(f"❌ Error reading log file: {e}", "ERROR")
            return {pattern: False for pattern in expected_patterns}

    def test_single_file_detection(self) -> bool:
        """Test 1: Single File Detection"""
        self.log("🧪 TEST 1: Single File Detection", "TEST")
        
        try:
            # Get first template
            templates = self.xml_fp.get_all_templates()
            template_name = templates[0]
            
            # Create fake file
            fake_path = self.create_fake_xml(template_name)
            if not fake_path:
                return False
            
            # Place in Desktop
            target_path = self.place_fake_file(fake_path, self.config['desktop_path'])
            if not target_path:
                return False
            
            # Monitor for changes
            detected, message = self.monitor_file_changes(target_path, timeout=15)
            
            if detected:
                # Verify overwrite
                if self.verify_file_overwrite(target_path, template_name):
                    self.log("✅ Single file detection test passed")
                    return True
                else:
                    self.log("❌ File overwrite verification failed", "ERROR")
                    return False
            else:
                self.log(f"❌ File detection failed: {message}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Single file detection test failed: {e}", "ERROR")
            return False

    def test_multiple_locations(self) -> bool:
        """Test 2: Multiple Locations"""
        self.log("🧪 TEST 2: Multiple Locations", "TEST")
        
        try:
            templates = self.xml_fp.get_all_templates()
            test_locations = [
                self.config['desktop_path'],
                self.config['documents_path'],
                self.config['downloads_path']
            ]
            
            success_count = 0
            
            for i, location in enumerate(test_locations):
                if i >= len(templates):
                    break
                    
                template_name = templates[i]
                self.log(f"📍 Testing location {i+1}: {location.name}")
                
                # Create fake file
                fake_path = self.create_fake_xml(template_name)
                if not fake_path:
                    continue
                
                # Place file
                target_path = self.place_fake_file(fake_path, location)
                if not target_path:
                    continue
                
                # Monitor for changes
                detected, message = self.monitor_file_changes(target_path, timeout=15)
                
                if detected and self.verify_file_overwrite(target_path, template_name):
                    success_count += 1
                    self.log(f"✅ Location {i+1} test passed")
                else:
                    self.log(f"❌ Location {i+1} test failed: {message}", "ERROR")
            
            if success_count >= len(test_locations) * 0.8:  # 80% success rate
                self.log(f"✅ Multiple locations test passed ({success_count}/{len(test_locations)})")
                return True
            else:
                self.log(f"❌ Multiple locations test failed ({success_count}/{len(test_locations)})", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Multiple locations test failed: {e}", "ERROR")
            return False

    def test_log_verification(self) -> bool:
        """Test 3: Log Verification"""
        self.log("🧪 TEST 3: Log Verification", "TEST")
        
        try:
            expected_patterns = [
                "Analyzing file:",
                "Found matching template:",
                "File overwritten successfully",
                "Ghi de thanh cong"
            ]
            
            results = self.check_log_entries(expected_patterns)
            
            success_count = sum(results.values())
            total_count = len(expected_patterns)
            
            if success_count >= total_count * 0.75:  # 75% success rate
                self.log(f"✅ Log verification test passed ({success_count}/{total_count})")
                return True
            else:
                self.log(f"❌ Log verification test failed ({success_count}/{total_count})", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Log verification test failed: {e}", "ERROR")
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
        
        report_path = self.config['test_dir'] / f"complete_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Calculate test duration
        duration = datetime.now() - self.start_time
        
        # Count test results
        total_tests = len([r for r in self.test_results if r['message'].startswith('🧪 TEST')])
        passed_tests = len([r for r in self.test_results if '✅' in r['message'] and 'TEST' in r['message']])
        
        # Environment info
        exe_size = self.config['exe_path'].stat().st_size / (1024 * 1024) if self.config['exe_path'].exists() else 0
        templates_count = len(self.xml_fp.get_all_templates()) if self.xml_fp else 0
        
        html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hide4 Complete Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
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
        .environment {{ background: #e9ecef; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕵️ Hide4 XML Monitor - Complete Test Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="environment">
            <h3>🔧 Environment Info</h3>
            <p><strong>Hide4.exe:</strong> {self.config['exe_path']} ({exe_size:.1f} MB)</p>
            <p><strong>Templates:</strong> {templates_count} files in {self.templates_dir}</p>
            <p><strong>Log file:</strong> {self.config['log_file']}</p>
            <p><strong>Test duration:</strong> {duration.total_seconds():.1f}s</p>
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
            <p>Hide4 XML Monitor Complete Test Suite v1.0</p>
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
        self.log("🚀 Starting Hide4 Complete Test Suite", "TEST")
        
        # Check environment
        if not self.check_environment():
            self.log("❌ Environment check failed", "ERROR")
            return False
        
        # Start Hide4.exe
        if not self.start_hide4():
            self.log("❌ Cannot start Hide4.exe", "ERROR")
            return False
        
        # Wait for Hide4 to initialize
        self.log("⏳ Waiting for Hide4 to initialize...")
        time.sleep(10)
        
        # Run tests
        tests = [
            self.test_single_file_detection,
            self.test_multiple_locations,
            self.test_log_verification
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(3)  # Brief pause between tests
            except Exception as e:
                self.log(f"❌ Test {test_func.__name__} crashed: {e}", "ERROR")
        
        # Cleanup
        self.cleanup_test_files()
        self.stop_hide4()
        
        # Generate report
        report_path = self.generate_report()
        
        # Final summary
        self.log(f"🏁 Test Suite Complete: {passed}/{total} tests passed", "SUCCESS" if passed == total else "WARNING")
        self.log(f"📊 Report saved to: {report_path}")
        
        return passed == total

def main():
    """Main test execution"""
    print("🎯 HIDE4 COMPLETE TEST SUITE")
    print("=" * 50)
    
    test_suite = Hide4CompleteTestSuite(verbose=True)
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Hide4.exe is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("Check the HTML report for details.")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
