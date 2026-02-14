import pathlib

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = None
SessionLocal = None

SQLITE_FALLBACK_URI = "sqlite:///instance/ads.db"


def _make_engine_and_tables(uri):
    if uri.startswith("sqlite"):
        pathlib.Path("instance").mkdir(exist_ok=True)
    eng = create_engine(
        uri,
        pool_pre_ping=not uri.startswith("sqlite"),
    )
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=eng)
    return eng


def init_db(app):
    global engine, SessionLocal
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    try:
        engine = _make_engine_and_tables(uri)
    except OperationalError:
        if uri.startswith("sqlite"):
            raise
        app.config["SQLALCHEMY_DATABASE_URI"] = SQLITE_FALLBACK_URI
        engine = _make_engine_and_tables(SQLITE_FALLBACK_URI)
        print(
            "PostgreSQL недоступен, используется SQLite:",
            SQLITE_FALLBACK_URI,
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    return SessionLocal()
