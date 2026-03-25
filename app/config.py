import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Configurações centrais da aplicação."""

    # Banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./recantos.db")

    # SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")

    # Google OAuth / Calendar / Gmail
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    GOOGLE_CLIENT_SECRET_FILE: str = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
    GOOGLE_TOKEN_FILE: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    GOOGLE_CLIENT_SECRET_JSON: str = os.getenv("GOOGLE_CLIENT_SECRET_JSON", "")
    GOOGLE_TOKEN_JSON: str = os.getenv("GOOGLE_TOKEN_JSON", "")

    # WhatsApp
    WHATSAPP_NUMBER: str = os.getenv("WHATSAPP_NUMBER", "5541988881186")

    # Site
    SITE_NAME: str = os.getenv("SITE_NAME", "Chácara Recanto dos Pinheiros")
    SITE_URL: str = os.getenv("SITE_URL", "https://www.chacararecantodospinheiros.com")

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "app" / "templates"
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    IMAGES_DIR: Path = STATIC_DIR / "images"


settings = Settings()
