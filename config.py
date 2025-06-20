import os
from dotenv import load_dotenv

# 自动加载.env环境变量文件（如有）
load_dotenv()

# 机器人Token，强烈建议用环境变量管理
BOT_TOKEN = os.getenv("BOT_TOKEN", "替换为你的本地测试Token")

# 数据库配置
DB_URI = os.getenv("DB_URI", "sqlite:///ym888.db")  # 本地sqlite，生产可用mysql/postgres等

# 是否开启DEBUG模式
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# 汇率API Key（如有多API可扩展）
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "")

# 默认汇率、费率
DEFAULT_RATE = float(os.getenv("DEFAULT_RATE", 0))  # 默认费率%
DEFAULT_EXCHANGE = float(os.getenv("DEFAULT_EXCHANGE", 0))  # 默认汇率

# web服务配置
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8000))

# 其他可扩展配置
ADMINS = os.getenv("ADMINS", "").split(",") if os.getenv("ADMINS") else []

# 群组功能相关
GROUP_BILLING_CUTOFF_HOUR = int(os.getenv("GROUP_BILLING_CUTOFF_HOUR", 6))  # 账单日切时间（小时，0-23）

# 广告推送间隔(秒)
AD_INTERVAL = int(os.getenv("AD_INTERVAL", 600))

# 其他第三方API密钥（如钱包、短信等）
WALLET_API_KEY = os.getenv("WALLET_API_KEY", "")

# 日志等级
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 示例：如需更多配置直接按需扩展
