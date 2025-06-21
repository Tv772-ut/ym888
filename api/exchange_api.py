# ym888/api/exchange_api.py
import requests

def get_usdt_cny():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        res = requests.get(url, timeout=5).json()
        return res["rates"]["CNY"]
    except Exception:
        return None
