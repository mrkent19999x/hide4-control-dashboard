# Import logging manager
try:
    from logging_manager import get_logger
    logger = get_logger('main')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# xml_fingerprint.py

import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class XMLFingerprint:
    """Class để extract và so khớp dấu vân tay XML"""

    # Namespace cho XML thuế
    NAMESPACE = {'ns': 'http://kekhaithue.gdt.gov.vn/TKhaiThue'}

    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        self.templates_fingerprints = {}
        self._load_templates_fingerprints()

    def _load_templates_fingerprints(self):
        """Tải và parse tất cả templates để tạo fingerprint database"""
        if not os.path.exists(self.templates_dir):
            logger.error(f"❌ Thư mục templates không tồn tại: {self.templates_dir}")
            return

        template_files = [f for f in os.listdir(self.templates_dir) if f.endswith('.xml')]

        for template_file in template_files:
            template_path = os.path.join(self.templates_dir, template_file)
            try:
                fingerprint = self.extract_fingerprint(template_path)
                if fingerprint:
                    # Sử dụng tên file làm key
                    template_name = os.path.splitext(template_file)[0]
                    self.templates_fingerprints[template_name] = fingerprint
                    logger.info(f"✅ Đã load template: {template_file}")
                else:
                    logger.warning(f"⚠️ Không thể parse template: {template_file}")
            except Exception as e:
                logger.error(f"❌ Lỗi load template {template_file}: {e}")

        logger.info(f"📊 Đã load {len(self.templates_fingerprints)} templates")

    def extract_fingerprint(self, xml_path: str) -> Optional[Dict]:
        """Extract dấu vân tay từ file XML"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Extract các trường quan trọng
            fingerprint = {}

            # MST (Mã số thuế)
            mst_elem = root.find('.//ns:mst', self.NAMESPACE)
            fingerprint['mst'] = mst_elem.text if mst_elem is not None and mst_elem.text else None

            # Mã tờ khai
            maTKhai_elem = root.find('.//ns:maTKhai', self.NAMESPACE)
            fingerprint['maTKhai'] = maTKhai_elem.text if maTKhai_elem is not None and maTKhai_elem.text else None

            # Kiểu kỳ (Q=Quý, Y=Năm, M=Tháng)
            kieuKy_elem = root.find('.//ns:kieuKy', self.NAMESPACE)
            fingerprint['kieuKy'] = kieuKy_elem.text if kieuKy_elem is not None and kieuKy_elem.text else None

            # Kỳ khai
            kyKKhai_elem = root.find('.//ns:kyKKhai', self.NAMESPACE)
            fingerprint['kyKKhai'] = kyKKhai_elem.text if kyKKhai_elem is not None and kyKKhai_elem.text else None

            # Số lần nộp
            soLan_elem = root.find('.//ns:soLan', self.NAMESPACE)
            fingerprint['soLan'] = soLan_elem.text if soLan_elem is not None and soLan_elem.text else None

            # Tên tờ khai (để debug)
            tenTKhai_elem = root.find('.//ns:tenTKhai', self.NAMESPACE)
            fingerprint['tenTKhai'] = tenTKhai_elem.text if tenTKhai_elem is not None and tenTKhai_elem.text else None

            # Tên NNT (Người nộp thuế)
            tenNNT_elem = root.find('.//ns:tenNNT', self.NAMESPACE)
            fingerprint['tenNNT'] = tenNNT_elem.text if tenNNT_elem is not None and tenNNT_elem.text else None

            # Kiểm tra xem có đủ thông tin không
            required_fields = ['mst', 'maTKhai', 'kieuKy', 'kyKKhai']
            if all(fingerprint.get(field) for field in required_fields):
                return fingerprint
            else:
                logger.warning(f"⚠️ XML thiếu thông tin quan trọng: {xml_path}")
                return None

        except ET.ParseError as e:
            logger.error(f"❌ Lỗi parse XML {xml_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi extract fingerprint {xml_path}: {e}")
            return None

    def find_matching_template(self, xml_path: str) -> Optional[Tuple[str, Dict]]:
        """Tìm template khớp với file XML"""
        try:
            # Extract fingerprint từ file mới
            new_fingerprint = self.extract_fingerprint(xml_path)
            if not new_fingerprint:
                logger.warning(f"⚠️ Không thể extract fingerprint từ: {xml_path}")
                return None

            # So sánh với từng template
            for template_name, template_fingerprint in self.templates_fingerprints.items():
                if self._compare_fingerprints(new_fingerprint, template_fingerprint):
                    logger.info(f"✅ Tìm thấy template khớp: {template_name}")
                    return template_name, template_fingerprint

            logger.info(f"ℹ️ Không tìm thấy template khớp cho: {xml_path}")
            return None

        except Exception as e:
            logger.error(f"❌ Lỗi tìm template khớp: {e}")
            return None

    def _compare_fingerprints(self, fp1: Dict, fp2: Dict) -> bool:
        """So sánh 2 fingerprint"""
        # Các trường bắt buộc phải khớp
        required_fields = ['mst', 'maTKhai', 'kieuKy', 'kyKKhai']

        for field in required_fields:
            if fp1.get(field) != fp2.get(field):
                return False

        # Số lần có thể khác nhau (fp1 có thể là 0, fp2 có thể là 1,2,3...)
        # Nhưng nếu cả hai đều có giá trị thì phải khớp
        soLan1 = fp1.get('soLan')
        soLan2 = fp2.get('soLan')

        if soLan1 is not None and soLan2 is not None:
            if soLan1 != soLan2:
                return False

        return True

    def get_template_path(self, template_name: str) -> Optional[str]:
        """Lấy đường dẫn file template"""
        template_file = f"{template_name}.xml"
        template_path = os.path.join(self.templates_dir, template_file)

        if os.path.exists(template_path):
            return template_path
        else:
            logger.error(f"❌ Template không tồn tại: {template_path}")
            return None

    def get_all_templates(self) -> List[str]:
        """Lấy danh sách tất cả templates"""
        return list(self.templates_fingerprints.keys())

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết của template"""
        return self.templates_fingerprints.get(template_name)

    def debug_fingerprint(self, xml_path: str) -> str:
        """Debug: hiển thị fingerprint của file XML"""
        fingerprint = self.extract_fingerprint(xml_path)
        if not fingerprint:
            return "❌ Không thể extract fingerprint"

        info = f"""🔍 FINGERPRINT DEBUG - {os.path.basename(xml_path)}

📋 Thông tin:
  • MST: {fingerprint.get('mst', 'N/A')}
  • Mã tờ khai: {fingerprint.get('maTKhai', 'N/A')}
  • Kiểu kỳ: {fingerprint.get('kieuKy', 'N/A')}
  • Kỳ khai: {fingerprint.get('kyKKhai', 'N/A')}
  • Số lần: {fingerprint.get('soLan', 'N/A')}
  • Tên tờ khai: {fingerprint.get('tenTKhai', 'N/A')[:50]}...
  • Tên NNT: {fingerprint.get('tenNNT', 'N/A')[:50]}...

🔍 Templates có sẵn: {len(self.templates_fingerprints)}"""

        return info

# Test function
def test_xml_fingerprint():
    """Test XML fingerprint với templates hiện có"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    fp = XMLFingerprint(templates_dir)

    print("🧪 TEST XML FINGERPRINT")
    print("=" * 50)

    # Test với từng template
    for template_name in fp.get_all_templates():
        template_path = fp.get_template_path(template_name)
        if template_path:
            print(f"\n📄 Template: {template_name}")
            print(fp.debug_fingerprint(template_path))

            # Test matching
            match = fp.find_matching_template(template_path)
            if match:
                print(f"✅ Match: {match[0]}")
            else:
                print("❌ No match")

if __name__ == "__main__":
    test_xml_fingerprint()
