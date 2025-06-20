# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging

# 从 config.py 读取数据库 URI
from config import DB_URI, DEBUG

# 日志配置
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("db")

# ORM 基类
Base = declarative_base()

# 创建数据库引擎
engine = create_engine(
    DB_URI,
    echo=DEBUG,            # DEBUG模式下输出SQL日志
    pool_pre_ping=True,    # 连接池自动回收失效连接
    future=True
)

# 会话工厂，使用 scoped_session 支持多线程
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

@contextmanager
def db_session():
    """
    上下文管理器，自动提交或回滚事务，自动关闭 session。
    用法示例：
        with db_session() as session:
            session.add(obj)
            ...
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("数据库操作异常: %s", e)
        raise
    finally:
        session.close()

def init_db():
    """
    初始化数据库：自动建表
    在主入口首次启动时调用一次即可
    """
    import models  # 确保models已import，Base能找到所有模型
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表已初始化")

# 可选：数据库健康检查
def check_db_connection():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("数据库连接正常")
        return True
    except Exception as e:
        logger.error("数据库连接失败: %s", e)
        return False
