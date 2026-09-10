import os
from dotenv import load_dotenv

load_dotenv()


class FactoryConfig:

    @staticmethod
    def get_config(env: str):
        if env == "development":
            return DevelopmentConfig
        elif env == "testing":
            return TestingConfig
        elif env == "production":
            return ProductionConfig
        else:
            return Config


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "a_default_secret_key"

    DEBUG = os.environ.get(
        "DEBUG", "False"
    ).lower() in ["true", "1"]

    TESTING = os.environ.get(
        "TESTING", "False"
    ).lower() in ["true", "1"]

    DATABASE_URI = (
        os.environ.get("DATABASE_URI")
        or "sqlite:///default.db"
    )

    CORS_HEADERS = "Content-Type"


class DevelopmentConfig(Config):
    DEBUG = True

    DATABASE_URI = (
        os.environ.get("POSTGREE_DATABASE_URL")
        or os.environ.get("DATABASE_URI")
        or "sqlite:///default.db"
    )


class TestingConfig(Config):
    TESTING = True

    DATABASE_URI = (
        os.environ.get("DATABASE_URI")
        or "sqlite:///default.db"
    )


class ProductionConfig(Config):
    DATABASE_URI = (
        os.environ.get("DATABASE_URI")
        or "sqlite:///default.db"
    )


template = {
    "swagger": "2.0",
    "info": {
        "title": "Activity & Shore Excursion API",
        "description": "API for managing activities and shore excursions",
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

    template = template

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }