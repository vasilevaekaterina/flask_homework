import os


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "postgresql://localhost:5432/ads_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
