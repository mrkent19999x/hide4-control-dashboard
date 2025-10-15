#!/usr/bin/env python3
"""
Hide4 Issues Fix Script
Fix các vấn đề phát hiện trong test suite
"""

import os
import sys
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'client'))

def fix_logging_level():
    """Fix logging level để capture debug messages"""
    print("🔧 Fixing logging level...")
    
    icon_file = project_root / 'client' / 'icon.py'
    
    # Read current content
    with open(icon_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace logging level from INFO to DEBUG
    old_config = """logging.basicConfig(
    filename=str(LOG_FILE),
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)"""
    
    new_config = """logging.basicConfig(
    filename=str(LOG_FILE),
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)"""
    
    if old_config in content:
        content = content.replace(old_config, new_config)
        
        with open(icon_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Logging level changed from INFO to DEBUG")
        return True
    else:
        print("⚠️ Logging config not found or already changed")
        return False

def fix_template_matching_debug():
    """Add debug logging to template matching"""
    print("🔧 Adding debug logging to template matching...")
    
    icon_file = project_root / 'client' / 'icon.py'
    
    # Read current content
    with open(icon_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add debug logging to try_overwrite method
    debug_additions = """
        logger.debug(f"🔍 DEBUG: Analyzing file: {dest}")
        logger.debug(f"🔍 DEBUG: File exists: {os.path.exists(dest)}")
        logger.debug(f"🔍 DEBUG: File size: {os.path.getsize(dest) if os.path.exists(dest) else 'N/A'}")
"""
    
    # Find the try_overwrite method and add debug logging
    if "def try_overwrite(self, dest):" in content:
        # Add debug logging after the method starts
        old_start = """def try_overwrite(self, dest):
        # Không xử lý các file nằm trong _MEIPASS/templates"""
        
        new_start = """def try_overwrite(self, dest):
        # Không xử lý các file nằm trong _MEIPASS/templates""" + debug_additions
        
        if old_start in content:
            content = content.replace(old_start, new_start)
            
            with open(icon_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added debug logging to template matching")
            return True
    
    print("⚠️ Could not find try_overwrite method to modify")
    return False

def create_enhanced_test_script():
    """Create enhanced test script with better debugging"""
    print("🔧 Creating enhanced test script...")
    
    enhanced_script = '''#!/usr/bin/env python3
"""
Hide4 Enhanced Test Script - Fixed Issues
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

class Hide4EnhancedTestSuite:
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
        
        self.log(f"🚀 Hide4 Enhanced Test Suite initialized")

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

    def test_specific_template(self, template_name: str, target_folder: str) -> bool:
        """Test specific template in specific folder"""
        self.log(f"🧪 Testing template {template_name} in {target_folder}", "TEST")
        
        try:
            # Initialize XML fingerprint
            if not self.xml_fp:
                self.xml_fp = XMLFingerprint(str(self.templates_dir))
            
            # Get template info
            template_info = self.xml_fp.get_template_info(template_name)
            if not template_info:
                self.log(f"❌ Template {template_name} not found", "ERROR")
                return False
            
            self.log(f"📋 Template fingerprint: MST={template_info['mst']}, maTKhai={template_info['maTKhai']}, kieuKy={template_info['kieuKy']}, kyKKhai={template_info['kyKKhai']}")
            
            # Create fake file
            fake_path = self.create_fake_xml(template_name)
            if not fake_path:
                return False
            
            # Place in target folder
            target_path = Path(target_folder)
            target_file = self.place_fake_file(fake_path, target_path)
            if not target_file:
                return False
            
            # Monitor for changes
            detected, message = self.monitor_file_changes(target_file, timeout=20)
            
            if detected:
                # Verify overwrite
                if self.verify_file_overwrite(target_file, template_name):
                    self.log(f"✅ Template {template_name} test passed in {target_folder}")
                    return True
                else:
                    self.log(f"❌ Template {template_name} overwrite verification failed in {target_folder}", "ERROR")
                    return False
            else:
                self.log(f"❌ Template {template_name} detection failed in {target_folder}: {message}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Template {template_name} test failed: {e}", "ERROR")
            return False

    def create_fake_xml(self, template_name: str) -> Path:
        """Create fake XML file with same fingerprint but different financial data"""
        template_path = self.templates_dir / f"{template_name}.xml"
        fake_path = self.config['fake_files_dir'] / f"fake_{template_name}_{int(time.time())}.xml"
        
        if not template_path.exists():
            self.log(f"❌ Template file not found: {template_path}", "ERROR")
            return None
            
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply modifications (only financial data, keep fingerprint)
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
        """Place fake file in target location"""
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

    def monitor_file_changes(self, file_path: Path, timeout: int = 20) -> Tuple[bool, str]:
        """Monitor file changes to detect overwrite"""
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
        """Verify file has been overwritten with template"""
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

    def run_enhanced_tests(self) -> bool:
        """Run enhanced test scenarios"""
        self.log("🚀 Starting Hide4 Enhanced Test Suite", "TEST")
        
        # Initialize XML fingerprint
        self.xml_fp = XMLFingerprint(str(self.templates_dir))
        templates = self.xml_fp.get_all_templates()
        
        self.log(f"📋 Available templates: {templates}")
        
        # Test scenarios
        test_scenarios = [
            # (template_name, folder_path, expected_result)
            ("ETAX11320250294522551", str(self.config['desktop_path']), True),  # Should work
            ("ETAX11320250307811609", str(self.config['documents_path']), True),  # Test the problematic one
            ("ETAX11320250320038129", str(self.config['downloads_path']), True),  # Test Downloads
        ]
        
        passed = 0
        total = len(test_scenarios)
        
        for template_name, folder_path, expected in test_scenarios:
            try:
                result = self.test_specific_template(template_name, folder_path)
                if result == expected:
                    passed += 1
                time.sleep(3)  # Brief pause between tests
            except Exception as e:
                self.log(f"❌ Test {template_name} crashed: {e}", "ERROR")
        
        # Cleanup
        self.cleanup_test_files()
        
        # Final summary
        self.log(f"🏁 Enhanced Test Suite Complete: {passed}/{total} tests passed", "SUCCESS" if passed == total else "WARNING")
        
        return passed == total

def main():
    """Main test execution"""
    print("🎯 HIDE4 ENHANCED TEST SUITE")
    print("=" * 50)
    
    test_suite = Hide4EnhancedTestSuite(verbose=True)
    success = test_suite.run_enhanced_tests()
    
    if success:
        print("\\n🎉 ALL ENHANCED TESTS PASSED!")
    else:
        print("\\n⚠️ SOME ENHANCED TESTS FAILED!")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
'''
    
    script_path = project_root / 'scripts' / 'test_hide4_enhanced.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_script)
    
    print(f"✅ Enhanced test script created: {script_path}")
    return True

def rebuild_exe():
    """Rebuild Hide4.exe with fixes"""
    print("🔧 Rebuilding Hide4.exe with fixes...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 'scripts/build_release.py'
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Hide4.exe rebuilt successfully")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def main():
    """Main fix process"""
    print("🔧 HIDE4 ISSUES FIX SCRIPT")
    print("=" * 50)
    
    fixes_applied = []
    
    # Fix 1: Logging level
    if fix_logging_level():
        fixes_applied.append("Logging level changed to DEBUG")
    
    # Fix 2: Template matching debug
    if fix_template_matching_debug():
        fixes_applied.append("Added debug logging to template matching")
    
    # Fix 3: Enhanced test script
    if create_enhanced_test_script():
        fixes_applied.append("Created enhanced test script")
    
    # Fix 4: Rebuild exe
    if rebuild_exe():
        fixes_applied.append("Rebuilt Hide4.exe with fixes")
    
    print("\\n🎯 FIXES APPLIED:")
    for i, fix in enumerate(fixes_applied, 1):
        print(f"{i}. {fix}")
    
    print("\\n📋 NEXT STEPS:")
    print("1. Run enhanced test: python scripts/test_hide4_enhanced.py")
    print("2. Check log file for debug messages")
    print("3. Verify all templates work correctly")
    
    print("\\n✅ Fix script completed!")

if __name__ == '__main__':
    main()
