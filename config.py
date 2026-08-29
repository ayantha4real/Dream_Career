import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = "sqlite:///dreamcareer.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = str(BASE_DIR / "app" / "static" / "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {"pdf"}
