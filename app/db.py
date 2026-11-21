from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
database_url = settings.database_url

engine_options: dict = {"pool_pre_ping": True}
if database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    # Serverless functions should not retain a large per-instance connection pool.
    # Supabase transaction-pooler users must also disable prepared statements.
    engine_options["poolclass"] = NullPool
    if "pooler.supabase.com" in database_url or ":6543/" in database_url:
        engine_options["connect_args"] = {"prepare_threshold": None}

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
