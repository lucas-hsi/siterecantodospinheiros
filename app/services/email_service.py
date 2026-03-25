"""
Serviço de envio de emails via SMTP.
"""
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, html_body: str) -> bool:
    """
    Envia email usando Gmail API (se autenticado) ou SMTP fallback.
    """
    from app.services.google_auth_service import google_auth
    creds = google_auth.get_credentials()

    if creds:
        try:
            from googleapiclient.discovery import build
            import base64
            from email.mime.text import MIMEText

            service = build('gmail', 'v1', credentials=creds)
            message = MIMEText(html_body, 'html', 'utf-8')
            message['to'] = to
            message['from'] = 'me'
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            
            logger.info(f"Email enviado via Gmail API para {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar via Gmail API: {e}. Tentando SMTP...")

    if not settings.SMTP_USER or not settings.SMTP_PASS:
        logger.warning(f"[MOCK EMAIL] Para: {to} | Assunto: {subject}")
        return True

    try:
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart

        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_USER
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html", "utf-8"))

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS,
            use_tls=False,
            start_tls=True,
        )

        logger.info(f"Email enviado via SMTP para {to}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar via SMTP para {to}: {e}")
        return False


async def send_reservation_confirmation(
    nome: str,
    email: str,
    data_evento: str,
    tipo_evento: str,
    num_convidados: int,
) -> bool:
    """Envia email de confirmação de pré-reserva para o cliente."""
    subject = f"Pré-reserva recebida — {settings.SITE_NAME}"
    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;
                background: #faf8f5; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #1a3c2a, #2d5a3f); padding: 30px; text-align: center;">
            <h1 style="color: #c9a84c; margin: 0; font-size: 24px;">🌿 {settings.SITE_NAME}</h1>
        </div>
        <div style="padding: 30px;">
            <h2 style="color: #1a3c2a;">Olá, {nome}!</h2>
            <p style="color: #333; line-height: 1.6;">
                Recebemos sua pré-reserva e estamos muito felizes com seu interesse!
            </p>
            <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0;
                        border-left: 4px solid #c9a84c;">
                <p><strong>📅 Data:</strong> {data_evento}</p>
                <p><strong>🎉 Tipo:</strong> {tipo_evento}</p>
                <p><strong>👥 Convidados:</strong> {num_convidados}</p>
            </div>
            <p style="color: #333; line-height: 1.6;">
                Nossa equipe entrará em contato em até <strong>24 horas</strong> para confirmar
                os detalhes e finalizar sua reserva.
            </p>
            <p style="color: #666; font-size: 14px; margin-top: 30px;">
                Em caso de dúvidas, entre em contato pelo WhatsApp:
                <a href="https://wa.me/{settings.WHATSAPP_NUMBER}" style="color: #1a3c2a;">
                    clique aqui
                </a>
            </p>
        </div>
    </div>
    """
    return await send_email(email, subject, html)


async def send_admin_notification(
    nome: str,
    email: str,
    telefone: str,
    data_evento: str,
    tipo_evento: str,
    num_convidados: int,
    observacoes: str,
) -> bool:
    """Envia notificação de nova reserva para o admin."""
    if not settings.ADMIN_EMAIL:
        logger.warning("[MOCK] Notificação admin: nova reserva recebida")
        return True

    subject = f"🔔 Nova pré-reserva: {tipo_evento} em {data_evento}"
    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #1a3c2a;">Nova Pré-Reserva Recebida</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Nome:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{nome}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{email}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Telefone:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{telefone}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Data:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{data_evento}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Tipo:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{tipo_evento}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Convidados:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{num_convidados}</td></tr>
            <tr><td style="padding: 8px;"><strong>Observações:</strong></td>
                <td style="padding: 8px;">{observacoes or 'Nenhuma'}</td></tr>
        </table>
    </div>
    """
    return await send_email(settings.ADMIN_EMAIL, subject, html)


async def send_contact_notification(nome: str, email: str, mensagem: str) -> bool:
    """Envia notificação de mensagem de contato para o admin."""
    if not settings.ADMIN_EMAIL:
        logger.warning(f"[MOCK] Contato de {nome} ({email}): {mensagem[:100]}")
        return True

    subject = f"📩 Nova mensagem de contato: {nome}"
    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #1a3c2a;">Nova Mensagem de Contato</h2>
        <p><strong>Nome:</strong> {nome}</p>
        <p><strong>Email:</strong> {email}</p>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <p style="white-space: pre-wrap;">{mensagem}</p>
        </div>
    </div>
    """
    return await send_email(settings.ADMIN_EMAIL, subject, html)
