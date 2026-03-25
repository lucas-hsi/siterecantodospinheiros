"""
Endpoints da API JSON — reservas, contato e disponibilidade.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contact import ContactMessage
from app.services import calendar_service, reservation_service, email_service

from fastapi.responses import RedirectResponse
from app.services.google_auth_service import google_auth
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])


# ─── Schemas ────────────────────────────────────────────────────

class ReservationCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    telefone: str = Field(..., min_length=10, max_length=20)
    data_evento: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    tipo_evento: str = Field(..., min_length=2, max_length=100)
    num_convidados: int = Field(..., ge=1, le=1000)
    horario_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    horario_fim: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    servicos_adicionais: list[str] = Field(default=[])
    observacoes: str = Field(default="", max_length=2000)


class ContactCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    mensagem: str = Field(..., min_length=10, max_length=5000)


class ReservationResponse(BaseModel):
    id: int
    status: str
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str


# ─── Endpoints ──────────────────────────────────────────────────

@router.post("/reservas", response_model=ReservationResponse)
async def criar_reserva(data: ReservationCreate, db: Session = Depends(get_db)):
    """Cria uma pré-reserva de evento."""
    try:
        # Validar data no futuro
        event_date = datetime.strptime(data.data_evento, "%Y-%m-%d").date()
        if event_date <= datetime.now().date():
            raise HTTPException(status_code=400, detail="A data do evento deve ser no futuro.")

        reservation = await reservation_service.create_reservation(
            db=db,
            nome=data.nome,
            email=data.email,
            telefone=data.telefone,
            data_evento=data.data_evento,
            tipo_evento=data.tipo_evento,
            num_convidados=data.num_convidados,
            horario_inicio=data.horario_inicio,
            horario_fim=data.horario_fim,
            servicos_adicionais=data.servicos_adicionais,
            observacoes=data.observacoes,
        )

        return ReservationResponse(
            id=reservation.id,
            status="pendente",
            message="Pré-reserva criada com sucesso! Entraremos em contato em breve.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar reserva: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar reserva.")


@router.get("/disponibilidade")
async def verificar_disponibilidade(year: int, month: int):
    """Retorna datas indisponíveis para o mês/ano especificado."""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Mês inválido.")
    if year < 2024 or year > 2030:
        raise HTTPException(status_code=400, detail="Ano inválido.")

    unavailable = calendar_service.get_unavailable_dates(year, month)
    return {"year": year, "month": month, "unavailable_dates": unavailable}


@router.post("/contato", response_model=ContactResponse)
async def enviar_contato(data: ContactCreate, db: Session = Depends(get_db)):
    """Recebe mensagem de contato e envia notificação ao admin."""
    try:
        # Persistir no banco
        message = ContactMessage(
            nome=data.nome,
            email=data.email,
            mensagem=data.mensagem,
        )
        db.add(message)
        db.commit()

        logger.info(f"Mensagem de contato recebida de {data.nome} ({data.email})")

        # Notificar admin
        await email_service.send_contact_notification(
            nome=data.nome,
            email=data.email,
            mensagem=data.mensagem,
        )

        return ContactResponse(
            success=True,
            message="Mensagem enviada com sucesso! Retornaremos em breve.",
        )

    except Exception as e:
        logger.error(f"Erro ao processar contato: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar mensagem.")

# ─── Google OAuth ───────────────────────────────────────────────

@router.get("/google/auth")
async def google_login():
    """Inicia o fluxo de autenticação do Google."""
    redirect_uri = f"{settings.SITE_URL}/api/google/callback"
    flow = google_auth.get_auth_flow(redirect_uri)
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return RedirectResponse(auth_url)


@router.get("/google/callback")
async def google_callback(code: str):
    """Recebe o código do Google e salva o token."""
    redirect_uri = f"{settings.SITE_URL}/api/google/callback"
    success = google_auth.save_credentials_from_code(code, redirect_uri)
    
    if success:
        # Redireciona para a página de reservas com alerta de sucesso
        return RedirectResponse(url="/reservas?auth=success")
    else:
        raise HTTPException(status_code=400, detail="Falha ao autenticar com Google.")


@router.get("/google/status")
async def google_status():
    """Verifica se o sistema está conectado ao Google."""
    creds = google_auth.get_credentials()
    return {
        "connected": creds is not None and creds.valid,
        "email": creds.extra_data.get('email') if creds and hasattr(creds, 'extra_data') else None
    }
