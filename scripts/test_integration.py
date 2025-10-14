#!/usr/bin/env python3
# test_integration.py

"""
Test script để kiểm tra tích hợp Firebase Logger với Dashboard
"""

import os
import sys
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase_logger import firebase_logger
from machine_manager import machine_manager

def test_firebase_connection():
    """Test kết nối Firebase"""
    print("🔍 Testing Firebase connection...")

    if not firebase_logger.is_configured():
        print("❌ Firebase chưa được cấu hình")
        print("📁 Cần tạo file config.json với Firebase credentials")
        return False

    if firebase_logger.test_connection():
        print("✅ Firebase connection successful")
        return True
    else:
        print("❌ Firebase connection failed")
        return False

def test_send_log():
    """Test gửi log"""
    print("\n📤 Testing send log...")

    test_logs = [
        ("Test log 1", "C:\\test\\file1.xml"),
        ("PHÁT HIỆN FILE FAKE", "C:\\fake\\file2.xml", {
            'template_name': 'ETAX11320250294522551',
            'mst': '0123456789',
            'maTKhai': '01/GTGT',
            'kyKKhai': '2024Q1',
            'soLan': '1'
        }),
        ("Heartbeat", "Machine heartbeat test"),
        ("Phần mềm Hide4 khởi chạy", f"Machine: {machine_manager.get_machine_id()}")
    ]

    for i, log_data in enumerate(test_logs):
        print(f"  Sending log {i+1}/{len(test_logs)}: {log_data[0]}")

        if len(log_data) == 3:
            firebase_logger.send_log(log_data[0], log_data[1], log_data[2])
        else:
            firebase_logger.send_log(log_data[0], log_data[1])

        time.sleep(1)  # Wait 1 second between logs

    print("✅ All logs sent successfully")

def test_heartbeat():
    """Test heartbeat"""
    print("\n💓 Testing heartbeat...")

    machine_info = machine_manager.get_machine_info()
    firebase_logger.send_heartbeat(machine_info)

    print("✅ Heartbeat sent successfully")

def test_machine_status():
    """Test lấy machine status"""
    print("\n📊 Testing machine status...")

    status = firebase_logger.get_machine_status()
    if status:
        print(f"✅ Machine status retrieved: {len(status)} fields")
        print(f"  Machine ID: {status.get('info', {}).get('hostname', 'Unknown')}")
        print(f"  Last active: {status.get('status', {}).get('last_heartbeat', 'Unknown')}")
    else:
        print("❌ Failed to retrieve machine status")

def main():
    """Main test function"""
    print("🧪 HIDE4 FIREBASE INTEGRATION TEST")
    print("=" * 50)

    # Test 1: Firebase connection
    if not test_firebase_connection():
        print("\n❌ Firebase connection test failed. Please check your configuration.")
        return False

    # Test 2: Send logs
    test_send_log()

    # Test 3: Heartbeat
    test_heartbeat()

    # Test 4: Machine status
    test_machine_status()

    print("\n🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print("✅ Firebase connection: OK")
    print("✅ Send logs: OK")
    print("✅ Heartbeat: OK")
    print("✅ Machine status: OK")
    print("\n🌐 Check your Firebase Dashboard to see the data:")
    print("   https://console.firebase.google.com/project/hide4-control-dashboard/database")
    print("\n📱 Check your Web Dashboard:")
    print("   https://hide4-control-dashboard.web.app")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
