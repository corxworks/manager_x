import os
from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()


class Config:

    # -------------------------
    # FLASK
    # -------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "manager-x-development-secret"
    )


    # -------------------------
    # DATABASE
    # -------------------------

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///manager_x.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # -------------------------
    # GOOGLE OAUTH
    # -------------------------

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5000/auth/google/callback"
    )


    # -------------------------
    # OPENAI
    # -------------------------

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


    # -------------------------
    # REDIS
    # -------------------------

    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )


    # -------------------------
    # FRONTEND
    # -------------------------

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )