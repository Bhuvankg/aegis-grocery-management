
import os
from pathlib import Path
from dotenv import load_dotenv

# Locate and load .env from the backend directory or working directory
backend_dir = Path(__file__).resolve().parent.parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from backend/.env")

APP_NAME = os.getenv("APP_NAME", "AEGIS AI API")
APP_ENV = os.getenv("APP_ENV", "development")
API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# Security & Authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aegis-ai-super-secret-key-change-in-production-2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))


