# telegram_logger.py - Optional Telegram notifications
import os
import requests
from pathlib import Path
from typing import Dict, Optional

try:
    from logging_manager import get_logger
    logger = get_logger('main')
except Exception:
    import logging
    logger = logging.getLogger(__name__)

# Fill these and rebuild, or set as environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'PUT_YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'PUT_YOUR_CHAT_ID_HERE')

class TelegramLogger:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)

    def _send(self, text: str):
        if not self.enabled:
            return
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            resp = requests.post(url, json={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.debug(f"Telegram send failed: {e}")

    def send_detection(self, path: str, fingerprint: Dict):
        msg = (
            "\u2705 <b>Phát hiện file fake</b>\n"
            f"\n<b>File</b>: {path}"
            f"\n<b>MST</b>: {fingerprint.get('mst')}"
            f"\n<b>Mã tờ khai</b>: {fingerprint.get('maTKhai')}"
            f"\n<b>Kỳ</b>: {fingerprint.get('kyKKhai')}"
            f"\n<b>Số lần</b>: {fingerprint.get('soLan')}"
        )
        self._send(msg)

    def send_text(self, text: str):
        self._send(text)

telegram_logger = TelegramLogger()
