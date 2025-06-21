# ym888/config.py
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your-telegram-token")
DB_URL = os.getenv("DB_URL", "sqlite:///data.db")
ADMIN_USER_IDS = [int(uid) for uid in os.getenv("ADMIN_USER_IDS", "123456789").split(",")]
DEBUG = bool(int(os.getenv("DEBUG", "1")))
