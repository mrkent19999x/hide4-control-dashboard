# create_sample_data.py - Create sample data for testing

import sys
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_sample_data():
    """Create sample data for Firebase Database"""
    try:
        from firebase_admin import credentials, initialize_app, db
        from firebase_admin.exceptions import FirebaseError

        # Initialize Firebase Admin SDK
        if not initialize_app._apps:
            # Use default credentials
            cred = credentials.ApplicationDefault()
            initialize_app(cred, {
                'databaseURL': 'https://hide4-control-dashboard-default-rtdb.asia-southeast1.firebasedatabase.app'
            })

        # Create sample machines data
        machines_data = {
            'machine-001': {
                'info': {
                    'hostname': 'DESKTOP-ABC123',
                    'os': 'Windows 10',
                    'version': '10.0.19041',
                    'arch': 'x64',
                    'install_date': '2024-01-15T10:30:00Z',
                    'last_active': datetime.now().isoformat()
                },
                'status': {
                    'online': True,
                    'last_heartbeat': datetime.now().isoformat(),
                    'cpu_usage': random.randint(20, 80),
                    'memory_usage': random.randint(30, 90),
                    'disk_usage': random.randint(40, 95)
                },
                'stats': {
                    'total_files_processed': random.randint(100, 1000),
                    'files_today': random.randint(5, 50),
                    'errors_count': random.randint(0, 10),
                    'uptime_hours': random.randint(1, 720)
                }
            },
            'machine-002': {
                'info': {
                    'hostname': 'LAPTOP-XYZ789',
                    'os': 'Windows 11',
                    'version': '11.0.22000',
                    'arch': 'x64',
                    'install_date': '2024-02-20T14:15:00Z',
                    'last_active': (datetime.now() - timedelta(minutes=5)).isoformat()
                },
                'status': {
                    'online': True,
                    'last_heartbeat': (datetime.now() - timedelta(minutes=2)).isoformat(),
                    'cpu_usage': random.randint(15, 70),
                    'memory_usage': random.randint(25, 85),
                    'disk_usage': random.randint(35, 90)
                },
                'stats': {
                    'total_files_processed': random.randint(50, 800),
                    'files_today': random.randint(3, 40),
                    'errors_count': random.randint(0, 5),
                    'uptime_hours': random.randint(1, 500)
                }
            },
            'machine-003': {
                'info': {
                    'hostname': 'SERVER-DEF456',
                    'os': 'Windows Server 2022',
                    'version': '10.0.20348',
                    'arch': 'x64',
                    'install_date': '2024-03-10T09:00:00Z',
                    'last_active': (datetime.now() - timedelta(hours=2)).isoformat()
                },
                'status': {
                    'online': False,
                    'last_heartbeat': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'disk_usage': 0
                },
                'stats': {
                    'total_files_processed': random.randint(200, 1500),
                    'files_today': 0,
                    'errors_count': random.randint(0, 15),
                    'uptime_hours': random.randint(1, 1000)
                }
            }
        }

        # Create sample logs data
        logs_data = {}

        for machine_id, machine_data in machines_data.items():
            logs_data[machine_id] = {}

            # Create logs for the last 7 days
            for i in range(7):
                date = datetime.now() - timedelta(days=i)

                # Create 5-15 logs per day
                num_logs = random.randint(5, 15)
                for j in range(num_logs):
                    log_time = date + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59)
                    )

                    log_types = [
                        'FILE_PROCESSED',
                        'TEMPLATE_SYNCED',
                        'ERROR_OCCURRED',
                        'HEARTBEAT',
                        'STARTUP',
                        'SHUTDOWN'
                    ]

                    log_type = random.choice(log_types)

                    log_data = {
                        'event': log_type,
                        'timestamp': log_time.isoformat(),
                        'message': f'Sample {log_type.lower()} event',
                        'level': random.choice(['INFO', 'WARNING', 'ERROR']),
                        'details': {
                            'file_path': f'/path/to/file_{j}.xml',
                            'file_size': random.randint(1024, 1024*1024),
                            'processing_time': random.randint(100, 5000)
                        }
                    }

                    logs_data[machine_id][log_time.isoformat()] = log_data

        # Upload to Firebase
        print("📤 Uploading sample machines data...")
        db.reference('machines').set(machines_data)

        print("📤 Uploading sample logs data...")
        db.reference('logs').set(logs_data)

        print("✅ Sample data created successfully!")
        print(f"📊 Created {len(machines_data)} machines")

        total_logs = sum(len(machine_logs) for machine_logs in logs_data.values())
        print(f"📝 Created {total_logs} log entries")

        return True

    except ImportError:
        print("❌ Firebase Admin SDK not installed")
        return False
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Creating Sample Data for Testing...")
    print("=" * 50)

    if create_sample_data():
        print("\n🎉 Sample data created successfully!")
        print("🌐 Check your dashboard at:")
        print("   https://hide4-control-dashboard.web.app")
    else:
        print("\n💥 Failed to create sample data!")
        sys.exit(1)
