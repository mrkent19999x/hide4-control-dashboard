# tests/__init__.py - Test Package Initialization

"""
Hide4 Control Dashboard Test Suite

This package contains all unit tests for the Hide4 Control Dashboard system.
Tests are organized by module and cover:
- XML Fingerprint functionality
- Firebase Logger operations
- Firebase Storage sync
- Machine Manager operations
- Integration tests
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
TEST_CONFIG = {
    'test_data_dir': Path(__file__).parent / 'test_data',
    'temp_dir': None,
    'mock_firebase': True,
    'mock_requests': True
}

def setup_test_environment():
    """Setup test environment with temporary directories and mocks"""
    # Create temporary directory for tests
    TEST_CONFIG['temp_dir'] = tempfile.mkdtemp(prefix='hide4_test_')

    # Create test data directory
    TEST_CONFIG['test_data_dir'].mkdir(exist_ok=True)

    return TEST_CONFIG['temp_dir']

def cleanup_test_environment():
    """Cleanup test environment"""
    if TEST_CONFIG['temp_dir'] and os.path.exists(TEST_CONFIG['temp_dir']):
        shutil.rmtree(TEST_CONFIG['temp_dir'])

def create_test_xml_file(content: str, filename: str = "test.xml") -> str:
    """Create a test XML file with given content"""
    test_file = Path(TEST_CONFIG['temp_dir']) / filename
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(test_file)

def create_test_config_file(config_data: dict) -> str:
    """Create a test config file"""
    config_file = Path(TEST_CONFIG['temp_dir']) / 'config.json'
    import json
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    return str(config_file)

def mock_firebase_response(data: dict = None, status_code: int = 200):
    """Create a mock Firebase response"""
    mock_response = Mock()
    mock_response.json.return_value = data or {}
    mock_response.status_code = status_code
    mock_response.raise_for_status.return_value = None
    mock_response.content = b'{}' if data is None else str(data).encode()
    return mock_response

def mock_firebase_storage_response(items: list = None):
    """Create a mock Firebase Storage response"""
    data = {
        'items': items or [
            {
                'name': 'templates/test1.xml',
                'size': 1024,
                'updated': '2024-01-01T00:00:00Z'
            },
            {
                'name': 'templates/test2.xml',
                'size': 2048,
                'updated': '2024-01-02T00:00:00Z'
            }
        ]
    }
    return mock_firebase_response(data)

# Sample XML content for testing
SAMPLE_XML_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <mst>0123456789</mst>
    <maTKhai>01/GTGT</maTKhai>
    <kieuKy>Q</kieuKy>
    <kyKKhai>2024Q1</kyKKhai>
    <soLan>1</soLan>
    <tenTKhai>Tờ khai thuế GTGT</tenTKhai>
    <tenNNT>Công ty ABC</tenNNT>
</root>'''

SAMPLE_XML_CONTENT_INVALID = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <mst>0123456789</mst>
    <!-- Missing required fields -->
</root>'''

SAMPLE_XML_CONTENT_MALFORMED = '''<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://kekhaithue.gdt.gov.vn/TKhaiThue">
    <mst>0123456789</mst>
    <maTKhai>01/GTGT</maTKhai>
    <kieuKy>Q</kieuKy>
    <kyKKhai>2024Q1</kyKKhai>
    <!-- Missing closing tag -->
'''

# Test fixtures (only define if pytest is available)
if pytest:
    @pytest.fixture
    def temp_dir():
        """Provide temporary directory for tests"""
        temp_dir = setup_test_environment()
        yield temp_dir
        cleanup_test_environment()

    @pytest.fixture
    def sample_xml_file(temp_dir):
        """Provide sample XML file for testing"""
        return create_test_xml_file(SAMPLE_XML_CONTENT, "sample.xml")

    @pytest.fixture
    def invalid_xml_file(temp_dir):
        """Provide invalid XML file for testing"""
        return create_test_xml_file(SAMPLE_XML_CONTENT_INVALID, "invalid.xml")

    @pytest.fixture
    def malformed_xml_file(temp_dir):
        """Provide malformed XML file for testing"""
        return create_test_xml_file(SAMPLE_XML_CONTENT_MALFORMED, "malformed.xml")

    @pytest.fixture
    def mock_firebase():
        """Mock Firebase operations"""
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post, \
             patch('requests.put') as mock_put, \
             patch('requests.patch') as mock_patch, \
             patch('requests.delete') as mock_delete:

            # Default successful responses
            mock_get.return_value = mock_firebase_response()
            mock_post.return_value = mock_firebase_response()
            mock_put.return_value = mock_firebase_response()
            mock_patch.return_value = mock_firebase_response()
            mock_delete.return_value = mock_firebase_response()

            yield {
                'get': mock_get,
                'post': mock_post,
                'put': mock_put,
                'patch': mock_patch,
                'delete': mock_delete
            }

    @pytest.fixture
    def mock_firebase_storage():
        """Mock Firebase Storage operations"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_firebase_storage_response()
            yield mock_get

    @pytest.fixture
    def mock_logging():
        """Mock logging operations"""
        with patch('logging_manager.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.info = Mock()
            mock_logger.error = Mock()
            mock_logger.warning = Mock()
            mock_logger.debug = Mock()
            mock_get_logger.return_value = mock_logger
            yield mock_logger

# Import pytest for fixtures
try:
    import pytest
except ImportError:
    pytest = None

# Export test utilities
__all__ = [
    'setup_test_environment',
    'cleanup_test_environment',
    'create_test_xml_file',
    'create_test_config_file',
    'mock_firebase_response',
    'mock_firebase_storage_response',
    'SAMPLE_XML_CONTENT',
    'SAMPLE_XML_CONTENT_INVALID',
    'SAMPLE_XML_CONTENT_MALFORMED',
    'TEST_CONFIG'
]
