#!/usr/bin/env python3
"""
Hide4 XML Monitor - Test Data Generator
Creates fake XML files for testing detection and overwrite functionality.
"""

import os
import sys
import random
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestDataGenerator:
    def __init__(self):
        self.template_path = project_root / 'templates' / 'ETAX11320250294522551.xml'
        self.output_dir = project_root / 'test_fake_files'
        self.output_dir.mkdir(exist_ok=True)
        
        # Financial fields that can be modified for testing
        self.financial_fields = {
            'ct23': 'Doanh thu bán hàng và cung cấp dịch vụ',
            'ct24': 'Các khoản giảm trừ doanh thu',
            'ct25': 'Doanh thu thuần về bán hàng và cung cấp dịch vụ',
            'ct26': 'Giá vốn hàng bán',
            'ct27': 'Lợi nhuận gộp về bán hàng và cung cấp dịch vụ',
            'ct28': 'Doanh thu hoạt động tài chính',
            'ct29': 'Chi phí tài chính',
            'ct30': 'Chi phí bán hàng',
            'ct31': 'Chi phí quản lý doanh nghiệp',
            'ct32': 'Lợi nhuận thuần từ hoạt động kinh doanh',
            'ct33': 'Thu nhập khác',
            'ct34': 'Chi phí khác',
            'ct35': 'Lợi nhuận khác',
            'ct36': 'Tổng lợi nhuận kế toán trước thuế',
            'ct37': 'Chi phí thuế thu nhập doanh nghiệp hiện hành',
            'ct38': 'Chi phí thuế thu nhập doanh nghiệp hoãn lại',
            'ct39': 'Lợi nhuận sau thuế thu nhập doanh nghiệp'
        }
        
        print(f"🧪 Test Data Generator initialized")
        print(f"📁 Template: {self.template_path}")
        print(f"📁 Output: {self.output_dir}")

    def read_template(self) -> Optional[str]:
        """Read the original template file"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Loaded template: {self.template_path.name}")
            return content
        except Exception as e:
            print(f"❌ Error reading template: {e}")
            return None

    def generate_random_amount(self, base_amount: int = 1000000) -> int:
        """Generate random financial amount"""
        # Generate amount between 50% and 500% of base amount
        multiplier = random.uniform(0.5, 5.0)
        return int(base_amount * multiplier)

    def modify_financial_data(self, content: str, modifications: Dict[str, int] = None) -> str:
        """Modify financial data in XML content"""
        if not modifications:
            # Generate random modifications
            modifications = {}
            for field in list(self.financial_fields.keys())[:5]:  # Modify first 5 fields
                modifications[field] = self.generate_random_amount()
        
        modified_content = content
        
        for field, new_value in modifications.items():
            # Find and replace field value
            old_pattern = f'<{field}>'
            new_pattern = f'<{field}>{new_value}</{field}>'
            
            # Find the field and replace its value
            import re
            pattern = f'<{field}>[^<]*</{field}>'
            replacement = f'<{field}>{new_value}</{field}>'
            modified_content = re.sub(pattern, replacement, modified_content)
        
        return modified_content

    def create_fake_file(self, filename: str, modifications: Dict[str, int] = None) -> Path:
        """Create a fake XML file with modifications"""
        content = self.read_template()
        if not content:
            return None
        
        # Apply modifications
        modified_content = self.modify_financial_data(content, modifications)
        
        # Write fake file
        fake_path = self.output_dir / filename
        try:
            with open(fake_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"✅ Created fake file: {filename}")
            return fake_path
        except Exception as e:
            print(f"❌ Error creating fake file: {e}")
            return None

    def create_test_scenario_1(self) -> List[Path]:
        """Test Scenario 1: Basic fake detection"""
        print("\n🧪 Creating Test Scenario 1: Basic Fake Detection")
        
        files = []
        
        # File 1: Slightly modified amounts
        modifications = {
            'ct23': 999999999,  # Doanh thu
            'ct24': 888888888,  # Giảm trừ
            'ct32': 777777777   # Lợi nhuận
        }
        file1 = self.create_fake_file('test_scenario_1_basic.xml', modifications)
        if file1:
            files.append(file1)
        
        # File 2: More dramatic changes
        modifications = {
            'ct23': 5000000000,  # Very high revenue
            'ct24': 1000000000,  # High deductions
            'ct32': 4000000000   # Very high profit
        }
        file2 = self.create_fake_file('test_scenario_1_extreme.xml', modifications)
        if file2:
            files.append(file2)
        
        return files

    def create_test_scenario_2(self) -> List[Path]:
        """Test Scenario 2: Multiple locations"""
        print("\n🧪 Creating Test Scenario 2: Multiple Locations")
        
        files = []
        
        # Create files for different locations
        locations = [
            'desktop',
            'documents', 
            'downloads',
            'temp',
            'root_c'
        ]
        
        for i, location in enumerate(locations):
            modifications = {
                'ct23': 1000000000 + (i * 100000000),  # Incremental amounts
                'ct24': 500000000 + (i * 50000000),
                'ct32': 500000000 + (i * 50000000)
            }
            
            filename = f'test_scenario_2_{location}.xml'
            file_path = self.create_fake_file(filename, modifications)
            if file_path:
                files.append(file_path)
        
        return files

    def create_test_scenario_3(self) -> List[Path]:
        """Test Scenario 3: Edge cases"""
        print("\n🧪 Creating Test Scenario 3: Edge Cases")
        
        files = []
        
        # File 1: Zero amounts
        modifications = {
            'ct23': 0,
            'ct24': 0,
            'ct32': 0
        }
        file1 = self.create_fake_file('test_scenario_3_zero.xml', modifications)
        if file1:
            files.append(file1)
        
        # File 2: Negative amounts (if allowed)
        modifications = {
            'ct23': -1000000,
            'ct24': -500000,
            'ct32': -500000
        }
        file2 = self.create_fake_file('test_scenario_3_negative.xml', modifications)
        if file2:
            files.append(file2)
        
        # File 3: Very large amounts
        modifications = {
            'ct23': 999999999999,
            'ct24': 888888888888,
            'ct32': 777777777777
        }
        file3 = self.create_fake_file('test_scenario_3_large.xml', modifications)
        if file3:
            files.append(file3)
        
        return files

    def create_test_scenario_4(self) -> List[Path]:
        """Test Scenario 4: Template variations"""
        print("\n🧪 Creating Test Scenario 4: Template Variations")
        
        files = []
        
        # Create files with different field combinations
        field_combinations = [
            ['ct23', 'ct24', 'ct25'],  # Revenue fields
            ['ct26', 'ct27', 'ct28'],  # Cost fields
            ['ct32', 'ct33', 'ct34'],  # Profit fields
            ['ct36', 'ct37', 'ct38', 'ct39']  # Tax fields
        ]
        
        for i, fields in enumerate(field_combinations):
            modifications = {}
            for field in fields:
                modifications[field] = self.generate_random_amount()
            
            filename = f'test_scenario_4_combo_{i+1}.xml'
            file_path = self.create_fake_file(filename, modifications)
            if file_path:
                files.append(file_path)
        
        return files

    def create_all_test_files(self) -> List[Path]:
        """Create all test files for all scenarios"""
        print("🚀 Creating all test files...")
        
        all_files = []
        
        # Create files for each scenario
        all_files.extend(self.create_test_scenario_1())
        all_files.extend(self.create_test_scenario_2())
        all_files.extend(self.create_test_scenario_3())
        all_files.extend(self.create_test_scenario_4())
        
        print(f"\n✅ Created {len(all_files)} test files")
        return all_files

    def create_placement_script(self, files: List[Path]) -> Path:
        """Create a script to place test files in monitored locations"""
        script_path = self.output_dir / 'place_test_files.py'
        
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated script to place test files in monitored locations
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import os
import shutil
from pathlib import Path

def place_files():
    """Place test files in various monitored locations"""
    
    # Test files to place
    test_files = {f.name: f for f in {[f"'{f.name}'" for f in files]}}
    
    # Locations to test
    locations = {{
        'Desktop': str(Path.home() / 'Desktop'),
        'Documents': str(Path.home() / 'Documents'),
        'Downloads': str(Path.home() / 'Downloads'),
        'Temp': str(Path(os.environ.get('TEMP', '/tmp'))),
        'Root C': 'C:\\\\'
    }}
    
    print("🚀 Placing test files in monitored locations...")
    
    for filename, source_path in test_files.items():
        for location_name, location_path in locations.items():
            try:
                target_path = Path(location_path) / filename
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_path, target_path)
                print(f"✅ Placed {{filename}} in {{location_name}}")
                
            except Exception as e:
                print(f"❌ Failed to place {{filename}} in {{location_name}}: {{e}}")
    
    print("✅ All test files placed!")

if __name__ == '__main__':
    place_files()
'''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Created placement script: {script_path}")
        return script_path

    def generate_summary(self, files: List[Path]) -> Path:
        """Generate a summary of created test files"""
        summary_path = self.output_dir / 'test_files_summary.md'
        
        summary_content = f"""# Hide4 Test Files Summary

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
Total test files created: {len(files)}

## Test Files

"""
        
        for file_path in files:
            summary_content += f"- `{file_path.name}`\n"
        
        summary_content += f"""
## Test Scenarios

### Scenario 1: Basic Fake Detection
- `test_scenario_1_basic.xml` - Slightly modified amounts
- `test_scenario_1_extreme.xml` - Dramatically modified amounts

### Scenario 2: Multiple Locations  
- `test_scenario_2_desktop.xml` - For Desktop testing
- `test_scenario_2_documents.xml` - For Documents testing
- `test_scenario_2_downloads.xml` - For Downloads testing
- `test_scenario_2_temp.xml` - For Temp folder testing
- `test_scenario_2_root_c.xml` - For C:\\ root testing

### Scenario 3: Edge Cases
- `test_scenario_3_zero.xml` - Zero amounts
- `test_scenario_3_negative.xml` - Negative amounts
- `test_scenario_3_large.xml` - Very large amounts

### Scenario 4: Template Variations
- `test_scenario_4_combo_1.xml` - Revenue fields modified
- `test_scenario_4_combo_2.xml` - Cost fields modified  
- `test_scenario_4_combo_3.xml` - Profit fields modified
- `test_scenario_4_combo_4.xml` - Tax fields modified

## Usage

1. Run the test suite: `python scripts/test_hide4.py`
2. Or place files manually: `python test_fake_files/place_test_files.py`
3. Monitor Firebase logs for detection events

## Expected Behavior

All fake files should be:
1. Detected within 2 seconds of creation
2. Overwritten with original template content
3. Logged in Firebase as "PHAT HIEN FILE FAKE"

## Fingerprint Fields (Unchanged)

The following fields remain unchanged to ensure proper matching:
- `mst` (Mã số thuế)
- `maTKhai` (Mã tờ khai)  
- `kieuKy` (Kiểu kỳ)
- `kyKKhai` (Kỳ khai)
- `soLan` (Số lần nộp)
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"✅ Created summary: {summary_path}")
        return summary_path

def main():
    generator = TestDataGenerator()
    
    # Create all test files
    files = generator.create_all_test_files()
    
    if files:
        # Create placement script
        generator.create_placement_script(files)
        
        # Generate summary
        generator.generate_summary(files)
        
        print(f"\n🎉 Test data generation complete!")
        print(f"📁 Files created in: {generator.output_dir}")
        print(f"📊 Total files: {len(files)}")
        
        return True
    else:
        print("❌ No test files created")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
