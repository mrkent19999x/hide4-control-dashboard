# tests/test_xml_fingerprint.py - Unit Tests for XML Fingerprint

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Import the module under test
from client.xml_fingerprint import XMLFingerprint
from tests import (
    setup_test_environment,
    cleanup_test_environment,
    create_test_xml_file,
    SAMPLE_XML_CONTENT,
    SAMPLE_XML_CONTENT_INVALID,
    SAMPLE_XML_CONTENT_MALFORMED
)

class TestXMLFingerprint:
    """Test cases for XMLFingerprint class"""

    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = setup_test_environment()
        self.templates_dir = Path(self.temp_dir) / 'templates'
        self.templates_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Cleanup after each test method"""
        cleanup_test_environment()

    def test_init_with_nonexistent_directory(self):
        """Test initialization with non-existent directory"""
        with patch('client.xml_fingerprint.logger') as mock_logger:
            fp = XMLFingerprint('/nonexistent/directory')
            mock_logger.error.assert_called_once()
            assert len(fp.templates_fingerprints) == 0

    def test_init_with_empty_directory(self):
        """Test initialization with empty directory"""
        with patch('client.xml_fingerprint.logger') as mock_logger:
            fp = XMLFingerprint(str(self.templates_dir))
            mock_logger.info.assert_called_with("📊 Đã load 0 templates")
            assert len(fp.templates_fingerprints) == 0

    def test_extract_fingerprint_valid_xml(self):
        """Test extracting fingerprint from valid XML"""
        xml_file = create_test_xml_file(SAMPLE_XML_CONTENT, "valid.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        fingerprint = fp.extract_fingerprint(xml_file)

        assert fingerprint is not None
        assert fingerprint['mst'] == '0123456789'
        assert fingerprint['maTKhai'] == '01/GTGT'
        assert fingerprint['kieuKy'] == 'Q'
        assert fingerprint['kyKKhai'] == '2024Q1'
        assert fingerprint['soLan'] == '1'
        assert fingerprint['tenTKhai'] == 'Tờ khai thuế GTGT'
        assert fingerprint['tenNNT'] == 'Công ty ABC'

    def test_extract_fingerprint_invalid_xml(self):
        """Test extracting fingerprint from invalid XML"""
        xml_file = create_test_xml_file(SAMPLE_XML_CONTENT_INVALID, "invalid.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        with patch('client.xml_fingerprint.logger') as mock_logger:
            fingerprint = fp.extract_fingerprint(xml_file)

            assert fingerprint is None
            mock_logger.warning.assert_called_once()

    def test_extract_fingerprint_malformed_xml(self):
        """Test extracting fingerprint from malformed XML"""
        xml_file = create_test_xml_file(SAMPLE_XML_CONTENT_MALFORMED, "malformed.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        with patch('client.xml_fingerprint.logger') as mock_logger:
            fingerprint = fp.extract_fingerprint(xml_file)

            assert fingerprint is None
            mock_logger.error.assert_called_once()

    def test_extract_fingerprint_nonexistent_file(self):
        """Test extracting fingerprint from non-existent file"""
        fp = XMLFingerprint(str(self.templates_dir))

        with patch('client.xml_fingerprint.logger') as mock_logger:
            fingerprint = fp.extract_fingerprint('/nonexistent/file.xml')

            assert fingerprint is None
            mock_logger.error.assert_called_once()

    def test_load_templates_fingerprints(self):
        """Test loading templates fingerprints"""
        # Create test XML files
        create_test_xml_file(SAMPLE_XML_CONTENT, "template1.xml")
        create_test_xml_file(SAMPLE_XML_CONTENT.replace('0123456789', '9876543210'), "template2.xml")

        with patch('client.xml_fingerprint.logger') as mock_logger:
            fp = XMLFingerprint(str(self.templates_dir))

            assert len(fp.templates_fingerprints) == 2
            assert 'template1' in fp.templates_fingerprints
            assert 'template2' in fp.templates_fingerprints

            # Check that info logs were called
            assert mock_logger.info.call_count >= 2  # At least 2 templates loaded

    def test_find_matching_template_success(self):
        """Test finding matching template successfully"""
        # Create template
        template_file = create_test_xml_file(SAMPLE_XML_CONTENT, "template.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        # Create target XML with same fingerprint
        target_file = create_test_xml_file(SAMPLE_XML_CONTENT, "target.xml")

        with patch('client.xml_fingerprint.logger') as mock_logger:
            result = fp.find_matching_template(target_file)

            assert result is not None
            template_name, fingerprint = result
            assert template_name == 'template'
            assert fingerprint['mst'] == '0123456789'
            mock_logger.info.assert_called_with("✅ Tìm thấy template khớp: template")

    def test_find_matching_template_no_match(self):
        """Test finding matching template when no match exists"""
        # Create template
        create_test_xml_file(SAMPLE_XML_CONTENT, "template.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        # Create target XML with different fingerprint
        different_xml = SAMPLE_XML_CONTENT.replace('0123456789', '9999999999')
        target_file = create_test_xml_file(different_xml, "target.xml")

        with patch('client.xml_fingerprint.logger') as mock_logger:
            result = fp.find_matching_template(target_file)

            assert result is None
            mock_logger.info.assert_called_with("ℹ️ Không tìm thấy template khớp cho: " + target_file)

    def test_find_matching_template_invalid_target(self):
        """Test finding matching template with invalid target XML"""
        create_test_xml_file(SAMPLE_XML_CONTENT, "template.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        target_file = create_test_xml_file(SAMPLE_XML_CONTENT_INVALID, "target.xml")

        with patch('client.xml_fingerprint.logger') as mock_logger:
            result = fp.find_matching_template(target_file)

            assert result is None
            mock_logger.warning.assert_called_once()

    def test_compare_fingerprints_identical(self):
        """Test comparing identical fingerprints"""
        fp = XMLFingerprint(str(self.templates_dir))

        fp1 = {
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1',
            'soLan': '1'
        }

        fp2 = fp1.copy()

        assert fp._compare_fingerprints(fp1, fp2) is True

    def test_compare_fingerprints_different_required_fields(self):
        """Test comparing fingerprints with different required fields"""
        fp = XMLFingerprint(str(self.templates_dir))

        fp1 = {
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1'
        }

        fp2 = {
            'mst': '9876543210',  # Different MST
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1'
        }

        assert fp._compare_fingerprints(fp1, fp2) is False

    def test_compare_fingerprints_different_soLan(self):
        """Test comparing fingerprints with different soLan"""
        fp = XMLFingerprint(str(self.templates_dir))

        fp1 = {
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1',
            'soLan': '1'
        }

        fp2 = {
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1',
            'soLan': '2'  # Different soLan
        }

        assert fp._compare_fingerprints(fp1, fp2) is False

    def test_compare_fingerprints_one_missing_soLan(self):
        """Test comparing fingerprints where one is missing soLan"""
        fp = XMLFingerprint(str(self.templates_dir))

        fp1 = {
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1'
            # Missing soLan
        }

        fp2 = {
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kieuKy': 'Q',
            'kyKKhai': '2024Q1',
            'soLan': '1'
        }

        assert fp._compare_fingerprints(fp1, fp2) is True

    def test_get_template_path_existing(self):
        """Test getting path for existing template"""
        create_test_xml_file(SAMPLE_XML_CONTENT, "template.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        path = fp.get_template_path('template')

        assert path is not None
        assert os.path.exists(path)
        assert path.endswith('template.xml')

    def test_get_template_path_nonexistent(self):
        """Test getting path for non-existent template"""
        fp = XMLFingerprint(str(self.templates_dir))

        with patch('client.xml_fingerprint.logger') as mock_logger:
            path = fp.get_template_path('nonexistent')

            assert path is None
            mock_logger.error.assert_called_once()

    def test_get_all_templates(self):
        """Test getting all template names"""
        create_test_xml_file(SAMPLE_XML_CONTENT, "template1.xml")
        create_test_xml_file(SAMPLE_XML_CONTENT, "template2.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        templates = fp.get_all_templates()

        assert len(templates) == 2
        assert 'template1' in templates
        assert 'template2' in templates

    def test_get_template_info(self):
        """Test getting template info"""
        create_test_xml_file(SAMPLE_XML_CONTENT, "template.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        info = fp.get_template_info('template')

        assert info is not None
        assert info['mst'] == '0123456789'
        assert info['maTKhai'] == '01/GTGT'

    def test_get_template_info_nonexistent(self):
        """Test getting info for non-existent template"""
        fp = XMLFingerprint(str(self.templates_dir))

        info = fp.get_template_info('nonexistent')

        assert info is None

    def test_debug_fingerprint(self):
        """Test debug fingerprint functionality"""
        xml_file = create_test_xml_file(SAMPLE_XML_CONTENT, "debug.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        debug_info = fp.debug_fingerprint(xml_file)

        assert "FINGERPRINT DEBUG" in debug_info
        assert "0123456789" in debug_info
        assert "01/GTGT" in debug_info
        assert "Q" in debug_info
        assert "2024Q1" in debug_info

    def test_debug_fingerprint_invalid(self):
        """Test debug fingerprint with invalid XML"""
        xml_file = create_test_xml_file(SAMPLE_XML_CONTENT_INVALID, "debug.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        debug_info = fp.debug_fingerprint(xml_file)

        assert "❌ Không thể extract fingerprint" in debug_info

    def test_namespace_handling(self):
        """Test XML namespace handling"""
        xml_with_namespace = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <mst>0123456789</mst>
    <maTKhai>01/GTGT</maTKhai>
    <kieuKy>Q</kieuKy>
    <kyKKhai>2024Q1</kyKKhai>
</root>'''

        xml_file = create_test_xml_file(xml_with_namespace, "namespace.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        fingerprint = fp.extract_fingerprint(xml_file)

        assert fingerprint is not None
        assert fingerprint['mst'] == '0123456789'

    def test_empty_xml_elements(self):
        """Test handling of empty XML elements"""
        xml_with_empty = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <mst>0123456789</mst>
    <maTKhai></maTKhai>
    <kieuKy>Q</kieuKy>
    <kyKKhai>2024Q1</kyKKhai>
</root>'''

        xml_file = create_test_xml_file(xml_with_empty, "empty.xml")
        fp = XMLFingerprint(str(self.templates_dir))

        with patch('client.xml_fingerprint.logger') as mock_logger:
            fingerprint = fp.extract_fingerprint(xml_file)

            assert fingerprint is None
            mock_logger.warning.assert_called_once()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
