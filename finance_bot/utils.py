# finance_bot/utils.py
import re
from typing import List

def parse_amount(text: str) -> float:
    match = re.search(r"(-?\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else 0.0

def is_admin(user_id: int, admin_list: List[int]) -> bool:
    return user_id in admin_list
