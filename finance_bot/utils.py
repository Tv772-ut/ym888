# ym888/utils.py
import re
from decimal import Decimal

def parse_amount(text):
    try:
        return float(Decimal(re.sub(r"[^\d\.\-]", "", text)))
    except Exception:
        return None

def parse_command_args(text):
    return text.strip().split()

def format_currency(amount, symbol="¥"):
    return f"{symbol}{amount:.2f}"
