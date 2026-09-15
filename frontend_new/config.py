import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "cruise-admin-secret-key-change-me"
    DEBUG = True
    # Sau này sẽ trỏ về backend API
    API_BASE_URL = os.environ.get("API_BASE_URL") or "http://localhost:9999"
