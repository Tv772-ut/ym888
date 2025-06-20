import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from contextlib import contextmanager
from config import DB_URI, DEBUG

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("db")

Base = declarative_base()
engine = create_engine(DB_URI, echo=DEBUG, future=True, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

@contextmanager
def db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("DB Error: %s", e)
        raise
    finally:
        session.close()

def init_db():
    import models  # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
