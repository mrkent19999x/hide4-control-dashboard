#!/usr/bin/env python3
"""
Debug script để kiểm tra Hide4.exe file detection
"""

import os
import time
import shutil
from pathlib import Path

def create_debug_fake_file():
    """Tạo fake file với giá trị khác biệt rõ ràng"""
    template_path = Path("templates/ETAX11320250294522551.xml")
    fake_content = template_path.read_text(encoding='utf-8')
    
    # Thay đổi giá trị ct23 để khác biệt rõ ràng
    fake_content = fake_content.replace('<ct23>3354565834</ct23>', '<ct23>FAKE_VALUE_123456789</ct23>')
    
    # Ghi file fake
    fake_path = Path.home() / 'Desktop' / 'debug_fake_final.xml'
    fake_path.write_text(fake_content, encoding='utf-8')
    
    print(f"✅ Created fake file: {fake_path}")
    print(f"📋 Fake ct23 value: FAKE_VALUE_123456789")
    
    return fake_path

def check_file_overwrite(file_path, timeout=30):
    """Check xem file có bị overwrite không"""
    print(f"⏳ Monitoring file for {timeout} seconds...")
    
    start_time = time.time()
    original_content = file_path.read_text(encoding='utf-8')
    
    while time.time() - start_time < timeout:
        try:
            current_content = file_path.read_text(encoding='utf-8')
            
            if current_content != original_content:
                detection_time = time.time() - start_time
                print(f"✅ File detected and overwritten in {detection_time:.2f}s!")
                
                # Check ct23 value
                if 'FAKE_VALUE_123456789' in current_content:
                    print("❌ File still contains fake value - overwrite failed")
                else:
                    print("✅ File contains original template value - overwrite successful")
                
                return True
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
            
        time.sleep(1)
    
    print(f"❌ No detection after {timeout}s")
    return False

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
        print(f"  - PID: {proc['pid']}, Exe: {proc['exe']}")
    
    return len(hide4_processes) > 0

def check_templates():
    """Check templates directory"""
    templates_dir = Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return False
    
    template_files = list(templates_dir.glob('*.xml'))
    print(f"✅ Found {len(template_files)} template files:")
    for template in template_files:
        print(f"  - {template.name}")
    
    return len(template_files) > 0

def main():
    print("🔍 Hide4 File Detection Debug")
    print("=" * 50)
    
    # Check exe processes
    if not check_exe_processes():
        print("❌ No Hide4.exe processes found!")
        return
    
    # Check templates
    if not check_templates():
        print("❌ No templates found!")
        return
    
    # Create fake file
    fake_path = create_debug_fake_file()
    
    # Monitor for overwrite
    success = check_file_overwrite(fake_path, timeout=30)
    
    if success:
        print("🎉 File detection working!")
    else:
        print("❌ File detection not working - need further debugging")
        
        # Additional debug info
        print("\n🔍 Additional Debug Info:")
        print(f"📁 Fake file path: {fake_path}")
        print(f"📁 Template path: {Path(os.environ['APPDATA']) / 'XMLOverwrite' / 'templates'}")
        
        # Check if file is accessible
        try:
            content = fake_path.read_text(encoding='utf-8')
            print(f"📄 File readable: Yes ({len(content)} chars)")
        except Exception as e:
            print(f"❌ File not readable: {e}")

if __name__ == '__main__':
    main()
