# Configuration settings for the Flask application

import os
from dotenv import load_dotenv
load_dotenv()

class FactoryConfig:
    """Factory to get configuration based on environment."""
    @staticmethod
    def get_config(env: str):
        if env == 'development':
            return DevelopmentConfig
        elif env == 'testing':
            return TestingConfig
        elif env == 'production':
            return ProductionConfig
        else:
            return Config

class Config:
    """Base configuration.

    DATABASE_URI mặc định lấy từ POSTGREE_DATABASE_URL (connection string
    Supabase/Postgres, đặt trong file .env). Mọi environment (development,
    testing, production) đều kế thừa giá trị này trừ khi override riêng.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    TESTING = os.environ.get('TESTING', 'False').lower() in ['true', '1']
    DATABASE_URI = os.environ.get('DATABASE_URI') or os.environ.get('POSTGREE_DATABASE_URL')
    CORS_HEADERS = 'Content-Type'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = os.environ.get('POSTGREE_DATABASE_URL') or Config.DATABASE_URI


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = os.environ.get('TEST_POSTGREE_DATABASE_URL') or Config.DATABASE_URI


class ProductionConfig(Config):
    """Production configuration."""
    DATABASE_URI = os.environ.get('POSTGREE_DATABASE_URL') or Config.DATABASE_URI

    
template = {
    "swagger": "2.0",
    "info": {
        "title": "Todo API",
        "description": "API for managing todos",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ]
}
class SwaggerConfig:
    """Swagger configuration."""
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Todo API",
            "description": "API for managing todos",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ]
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }