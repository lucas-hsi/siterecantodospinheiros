"""
Serviço de integração com Google Calendar API.
Gerencia a verificação de disponibilidade e criação de eventos.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Flag para indicar se a integração está configurada
_calendar_configured = False
_service = None


def _get_calendar_service():
    """Inicializa o serviço do Google Calendar se credenciais estiverem disponíveis."""
    global _calendar_configured, _service

    if _service is not None:
        return _service

    from app.services.google_auth_service import google_auth
    creds = google_auth.get_credentials()

    if not creds:
        logger.warning("Google OAuth2 não autenticado. Usando dados mock.")
        _calendar_configured = False
        return None

    try:
        from googleapiclient.discovery import build
        _service = build("calendar", "v3", credentials=creds)
        _calendar_configured = True
        logger.info("Google Calendar API conectada com sucesso via OAuth2.")
        return _service
    except Exception as e:
        logger.warning(f"Falha ao conectar Google Calendar: {e}. Usando dados mock.")
        _calendar_configured = False
        return None


def get_unavailable_dates(year: int, month: int) -> list[str]:
    """
    Retorna lista de datas indisponíveis (YYYY-MM-DD) para o mês/ano.
    Se Google Calendar não estiver configurado, retorna dados mock.
    """
    service = _get_calendar_service()

    if service is None:
        return _get_mock_unavailable_dates(year, month)

    try:
        start = datetime(year, month, 1).isoformat() + "Z"
        if month == 12:
            end = datetime(year + 1, 1, 1).isoformat() + "Z"
        else:
            end = datetime(year, month + 1, 1).isoformat() + "Z"

        events_result = service.events().list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        unavailable = set()

        for event in events:
            start_date = event["start"].get("date", event["start"].get("dateTime", "")[:10])
            end_date = event["end"].get("date", event["end"].get("dateTime", "")[:10])

            current = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            while current < end_dt:
                unavailable.add(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)

        return sorted(list(unavailable))

    except Exception as e:
        logger.error(f"Erro ao consultar Google Calendar: {e}")
        return _get_mock_unavailable_dates(year, month)


def create_calendar_event(
    summary: str,
    description: str,
    date: str,
    start_time: str,
    end_time: str,
) -> Optional[str]:
    """
    Cria um evento no Google Calendar.
    Retorna o ID do evento ou None em caso de falha.
    """
    service = _get_calendar_service()

    if service is None:
        logger.info(f"[MOCK] Evento criado: {summary} em {date} {start_time}-{end_time}")
        return "mock-event-id"

    try:
        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": f"{date}T{start_time}:00",
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": f"{date}T{end_time}:00",
                "timeZone": "America/Sao_Paulo",
            },
        }

        result = service.events().insert(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            body=event,
        ).execute()

        logger.info(f"Evento criado no Calendar: {result.get('id')}")
        return result.get("id")

    except Exception as e:
        logger.error(f"Erro ao criar evento no Calendar: {e}")
        return None


def _get_mock_unavailable_dates(year: int, month: int) -> list[str]:
    """Retorna lista vazia em vez de dados mock para evitar confusão no front-end."""
    return []
