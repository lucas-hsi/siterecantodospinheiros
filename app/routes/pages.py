"""
Rotas de páginas HTML — renderiza templates Jinja2.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


def _context(request: Request, **kwargs) -> dict:
    """Contexto base para todos os templates."""
    return {
        "request": request,
        "site_name": settings.SITE_NAME,
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        **kwargs,
    }


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", _context(request, page="home"))


@router.get("/sobre")
async def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", _context(request, page="sobre"))


@router.get("/eventos")
async def eventos(request: Request):
    return templates.TemplateResponse("eventos.html", _context(request, page="eventos"))


@router.get("/reservas")
async def reservas(request: Request):
    return templates.TemplateResponse("reservas.html", _context(request, page="reservas"))


@router.get("/galeria")
async def galeria(request: Request):
    return templates.TemplateResponse("galeria.html", _context(request, page="galeria"))


@router.get("/contato")
async def contato(request: Request):
    return templates.TemplateResponse("contato.html", _context(request, page="contato"))


@router.get("/confirmacao")
async def confirmacao(request: Request):
    return templates.TemplateResponse("confirmacao.html", _context(request, page="confirmacao"))
