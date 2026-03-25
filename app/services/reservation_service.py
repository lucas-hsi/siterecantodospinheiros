"""
Serviço de lógica de negócio para reservas.
Orquestra: validação → persistência → calendar → emails.
"""
import json
import logging

from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.services import calendar_service, email_service

logger = logging.getLogger(__name__)


async def create_reservation(
    db: Session,
    nome: str,
    email: str,
    telefone: str,
    data_evento: str,
    tipo_evento: str,
    num_convidados: int,
    horario_inicio: str,
    horario_fim: str,
    servicos_adicionais: list[str],
    observacoes: str = "",
) -> Reservation:
    """
    Cria uma pré-reserva completa:
    1. Salva no banco com status 'pendente'
    2. Cria evento no Google Calendar
    3. Envia email de confirmação para o cliente
    4. Envia notificação para o admin
    """
    # 1. Persistir no banco
    reservation = Reservation(
        nome=nome,
        email=email,
        telefone=telefone,
        data_evento=data_evento,
        tipo_evento=tipo_evento,
        num_convidados=num_convidados,
        horario_inicio=horario_inicio,
        horario_fim=horario_fim,
        servicos_adicionais=json.dumps(servicos_adicionais),
        observacoes=observacoes,
        status="pendente",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    logger.info(f"Reserva #{reservation.id} criada: {nome} - {data_evento} ({tipo_evento})")

    # 2. Criar evento no Google Calendar (fire-and-forget, não bloqueia)
    try:
        servicos_texto = ", ".join(servicos_adicionais) if servicos_adicionais else "Nenhum"
        descricao_evento = (
            f"Reserva #{reservation.id}\n"
            f"Cliente: {nome}\n"
            f"Email: {email}\n"
            f"Telefone: {telefone}\n"
            f"Tipo: {tipo_evento}\n"
            f"Convidados: {num_convidados}\n"
            f"Serviços: {servicos_texto}\n"
            f"Obs: {observacoes or 'Nenhuma'}"
        )
        calendar_service.create_calendar_event(
            summary=f"[RESERVA] {tipo_evento} - {nome}",
            description=descricao_evento,
            date=data_evento,
            start_time=horario_inicio,
            end_time=horario_fim,
        )
    except Exception as e:
        logger.error(f"Erro ao criar evento no Calendar para reserva #{reservation.id}: {e}")

    # 3. Email de confirmação para o cliente
    try:
        await email_service.send_reservation_confirmation(
            nome=nome,
            email=email,
            data_evento=data_evento,
            tipo_evento=tipo_evento,
            num_convidados=num_convidados,
        )
    except Exception as e:
        logger.error(f"Erro ao enviar email de confirmação para {email}: {e}")

    # 4. Notificação para o admin
    try:
        await email_service.send_admin_notification(
            nome=nome,
            email=email,
            telefone=telefone,
            data_evento=data_evento,
            tipo_evento=tipo_evento,
            num_convidados=num_convidados,
            observacoes=observacoes,
        )
    except Exception as e:
        logger.error(f"Erro ao enviar notificação para admin: {e}")

    return reservation
