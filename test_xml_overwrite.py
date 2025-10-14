#!/usr/bin/env python3
# test_xml_overwrite.py - Test XML detection và ghi đè

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'client'))

from xml_fingerprint import XMLFingerprint
from github_storage import GitHubStorageSync

def create_fake_xml(mst, ma_tkhai, kieu_ky, ky_kkhai):
    """Tạo file XML fake để test"""
    fake_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<TKhai xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <TTChung>
        <mst>{mst}</mst>
        <maTKhai>{ma_tkhai}</maTKhai>
        <kieuKy>{kieu_ky}</kieuKy>
        <kyKKhai>{ky_kkhai}</ky_kkhai>
    </TTChung>
</TKhai>'''
    
    # Tạo file trong temp
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8')
    temp_file.write(fake_content)
    temp_file.close()
    
    return temp_file.name

def test_xml_matching():
    print("="*60)
    print("🧪 TEST XML FINGERPRINT MATCHING")
    print("="*60)
    
    # Load templates
    gss = GitHubStorageSync()
    templates_dir = str(gss.cache_dir)
    
    fp = XMLFingerprint(templates_dir)
    print(f"\n✅ Loaded {len(fp.templates_fingerprints)} templates")
    
    # Hiển thị templates
    print("\n📋 Available templates:")
    for name, fingerprint in fp.templates_fingerprints.items():
        print(f"   - {name}:")
        print(f"     MST: {fingerprint.get('mst')}")
        print(f"     maTKhai: {fingerprint.get('maTKhai')}")
        print(f"     kyKKhai: {fingerprint.get('kyKKhai')}")
    
    # Test với fake file
    if fp.templates_fingerprints:
        first_template = list(fp.templates_fingerprints.values())[0]
        print(f"\n🧪 Testing with fake file matching first template...")
        
        fake_file = create_fake_xml(
            first_template.get('mst'),
            first_template.get('maTKhai'),
            first_template.get('kieuKy'),
            first_template.get('kyKKhai')
        )
        
        print(f"   Created fake file: {fake_file}")
        
        # Test matching
        match = fp.find_matching_template(fake_file)
        
        if match:
            template_name, template_fp = match
            print(f"   ✅ MATCH FOUND: {template_name}")
            print(f"   Template will overwrite the fake file!")
        else:
            print(f"   ❌ NO MATCH - Check fingerprint logic")
        
        # Clean up
        os.unlink(fake_file)
        print(f"   Cleaned up fake file")

if __name__ == "__main__":
    test_xml_matching()
