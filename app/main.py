"""
Recantos dos Pinheiros — Aplicação FastAPI principal.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routes import pages, api

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação — cria tabelas no startup."""
    # Import dos modelos para registrar no metadata
    from app.models import Reservation, ContactMessage  # noqa: F401

    logger.info("Criando tabelas do banco de dados...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Aplicação {settings.SITE_NAME} iniciada com sucesso!")
    except Exception as e:
        logger.warning(f"Tabelas não criadas (ambiente read-only provável): {e}")

    yield

    logger.info("Aplicação encerrada.")


# Instância FastAPI
app = FastAPI(
    title=settings.SITE_NAME,
    description="Site institucional para chácara de eventos",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
else:
    logger.warning("Pasta /static não encontrada. FastAPI rodará em modo API only.")

# Rotas
app.include_router(api.router)
app.include_router(pages.router)
