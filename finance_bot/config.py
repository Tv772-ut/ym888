# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# 自动加载 .env 文件（仅本地开发用，线上环境变量优先）
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()  # 默认行为，兼容其它位置

def get_env(key, default=None, cast_type=None):
    """通用环境变量读取函数，支持类型转换。"""
    val = os.getenv(key, default)
    if cast_type and val is not None:
        try:
            return cast_type(val)
        except Exception:
            raise ValueError(f"环境变量 {key} 类型转换失败: {val}")
    return val

# 基础配置
BOT_TOKEN   = get_env("BOT_TOKEN", "")
DB_URI      = get_env("DB_URI", "sqlite:///ym888.db")
DEBUG       = get_env("DEBUG", "0", lambda v: str(v).lower() in ("1", "true", "yes"))
WEB_HOST    = get_env("WEB_HOST", "0.0.0.0")
WEB_PORT    = get_env("WEB_PORT", 8000, int)
ADMINS      = [i.strip() for i in get_env("ADMINS", "").split(",") if i.strip()]

# API和第三方相关（可按需扩展）
EXCHANGE_API_KEY = get_env("EXCHANGE_API_KEY", "")
WALLET_API_URL   = get_env("WALLET_API_URL", "")

# 日志与安全
LOG_LEVEL   = get_env("LOG_LEVEL", "INFO")
SECRET_KEY  = get_env("SECRET_KEY", os.urandom(24).hex())

# 其它可扩展配置
# SENTRY_DSN = get_env("SENTRY_DSN", "")
# REDIS_URL = get_env("REDIS_URL", "")

# 配置检查（可选，启动时校验关键配置）
if not BOT_TOKEN:
    raise RuntimeError("必须设置 BOT_TOKEN 环境变量才能运行机器人！")

# 打印关键配置信息（仅DEBUG模式显示，防止泄漏敏感信息）
if DEBUG:
    print(f"[Config] DB_URI: {DB_URI}")
    print(f"[Config] ADMINS: {ADMINS}")
    print(f"[Config] WEB_HOST: {WEB_HOST}:{WEB_PORT}")
    print(f"[Config] LOG_LEVEL: {LOG_LEVEL}")
