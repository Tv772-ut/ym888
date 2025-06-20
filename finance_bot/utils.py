# utils.py
import re
import ast
import operator
import requests

# 1. 指令解析：识别+100、-50U、转账、修正等
def parse_command(text):
    """解析文本指令，返回命令类型与参数"""
    text = text.strip()
    if text.startswith('+') or text.startswith('-'):
        amount, currency = parse_amount(text)
        return {"cmd": "record", "amount": amount, "currency": currency}
    elif text.lower().startswith('转账') or text.lower().startswith('transfer'):
        # 例：转账100U @user
        m = re.match(r'转账\s*([\d.]+)\s*([a-zA-Z]*)\s*@?([^\s]+)?', text)
        if m:
            return {"cmd": "transfer", "amount": float(m.group(1)), "currency": m.group(2).upper(), "to": m.group(3)}
    # 可扩展更多命令
    return {"cmd": "unknown"}

# 2. 金额与币种解析
def parse_amount(text):
    """从文本中解析金额和币种, 例: 100U, -50usd, +88"""
    m = re.match(r'([+-]?\d+(?:\.\d+)?)([a-zA-Z]*)', text.strip())
    if m:
        amount = float(m.group(1))
        currency = m.group(2).upper() if m.group(2) else 'CNY'
        return amount, currency
    return 0.0, "CNY"

# 3. 安全数学表达式计算（防止代码注入）
def safe_eval(expr):
    """只允许简单四则运算，拒绝其它表达式"""
    allowed_operators = {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub}
    def _eval(node):
        if isinstance(node, ast.Num):  # 兼容Python3.7+
            return node.n
        elif isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            return _eval(node.left) + _eval(node.right) if isinstance(node.op, ast.Add) \
                else _eval(node.left) - _eval(node.right) if isinstance(node.op, ast.Sub) \
                else _eval(node.left) * _eval(node.right) if isinstance(node.op, ast.Mult) \
                else _eval(node.left) / _eval(node.right)
        elif isinstance(node, ast.UnaryOp) and type(node.op) == ast.USub:
            return -_eval(node.operand)
        else:
            raise ValueError("非法表达式")
    try:
        node = ast.parse(expr, mode='eval').body
        return round(_eval(node), 8)
    except Exception:
        raise ValueError("无法计算该表达式")

# 4. 汇率转换（本地或云API）
def convert_currency(amount, from_currency, to_currency, rate=None):
    """币种转换，可传入汇率，否则自动查API"""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    if from_currency == to_currency:
        return amount
    if rate is not None:
        return round(amount * rate, 2)
    # 默认调用免费汇率API
    rate_api = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    try:
        resp = requests.get(rate_api, timeout=5)
        data = resp.json()
        out_rate = data['rates'][to_currency]
        return round(amount * out_rate, 2)
    except Exception:
        raise RuntimeError(f"汇率转换失败：{from_currency} -> {to_currency}")

# 5. 金额格式化
def format_amount(amount, currency="CNY"):
    """格式化金额显示"""
    return f"{amount:.2f} {currency}"

# 6. 快捷判断是否为数字
def is_number(val):
    try:
        float(val)
        return True
    except Exception:
        return False

# 其它常用工具函数可扩展
