#!/usr/bin/env python3
"""
Hide4 Simple Test - Verify Hide4.exe is working
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def test_hide4_simple():
    """Simple test to verify Hide4.exe is working"""
    print("🧪 HIDE4 SIMPLE TEST")
    print("=" * 50)
    
    # Check if Hide4.exe exists
    exe_path = Path("client/build_release/Hide4.exe")
    if not exe_path.exists():
        print("❌ Hide4.exe not found!")
        return False
    
    print(f"✅ Hide4.exe found: {exe_path}")
    
    # Start Hide4.exe
    try:
        print("🚀 Starting Hide4.exe...")
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a bit
        time.sleep(3)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Hide4.exe is running!")
            
            # Create a simple test file
            test_file = Path.home() / "Desktop" / "test_hide4.xml"
            test_content = '''<?xml version="1.0" encoding="UTF-8"?>
<HSoThueDTu xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
  <HSoKhaiThue id="ID_1">
    <TTinChung>
      <TTinTKhaiThue>
        <TKhaiThue>
          <maTKhai>842</maTKhai>
          <tenTKhai>TỜ KHAI THUẾ GIÁ TRỊ GIA TĂNG</tenTKhai>
          <soLan>0</soLan>
          <KyKKhaiThue>
            <kieuKy>Q</kieuKy>
            <kyKKhai>4/2024</kyKKhai>
          </KyKKhaiThue>
        </TKhaiThue>
        <NNT>
          <mst>4000982949</mst>
          <tenNNT>CÔNG TY TNHH MTV MỸ THUẬT ỨNG DỤNG ĐỨC NGUYỄN</tenNNT>
        </NNT>
      </TTinTKhaiThue>
    </TTinChung>
  </HSoKhaiThue>
</HSoThueDTu>'''
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            print(f"✅ Created test file: {test_file}")
            
            # Monitor for changes
            print("👀 Monitoring for changes...")
            original_content = test_content
            
            for i in range(20):  # 20 seconds
                time.sleep(1)
                if test_file.exists():
                    with open(test_file, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                    
                    if current_content != original_content:
                        print(f"✅ File changed after {i+1}s!")
                        print("✅ Hide4.exe is working!")
                        
                        # Cleanup
                        try:
                            test_file.unlink()
                            print("✅ Cleaned up test file")
                        except:
                            pass
                        
                        # Kill process
                        process.terminate()
                        return True
                
                print(f"⏳ Waiting... {i+1}/20s")
            
            print("❌ No changes detected after 20s")
            
            # Cleanup
            try:
                test_file.unlink()
            except:
                pass
            
            # Kill process
            process.terminate()
            return False
            
        else:
            print("❌ Hide4.exe exited immediately!")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Hide4.exe: {e}")
        return False

if __name__ == "__main__":
    success = test_hide4_simple()
    if success:
        print("\n🎉 HIDE4.EXE IS WORKING!")
    else:
        print("\n❌ HIDE4.EXE HAS ISSUES!")
    
    sys.exit(0 if success else 1)
