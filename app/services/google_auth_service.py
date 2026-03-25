import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from app.config import settings

logger = logging.getLogger(__name__)

# Scopes necessários: Calendário e envio de Gmail
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

class GoogleAuthService:
    @staticmethod
    def get_credentials() -> Credentials:
        """
        Obtém credenciais válidas do token.json.
        Se o token não existir ou for inválido, retorna None.
        """
        creds = None
        if os.path.exists(settings.GOOGLE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_FILE, SCOPES)
        
        # Se não houver credenciais válidas, tenta dar refresh
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Salva o token atualizado
                with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Erro ao atualizar token Google: {e}")
                creds = None
        
        return creds

    @staticmethod
    def get_auth_flow(redirect_uri: str) -> Flow:
        """Cria o fluxo de autenticação OAuth2."""
        return Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

    @staticmethod
    def save_credentials_from_code(code: str, redirect_uri: str) -> bool:
        """Troca o código pelo token e salva no token.json."""
        try:
            flow = GoogleAuthService.get_auth_flow(redirect_uri)
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            
            logger.info("Token Google OAuth2 salvo com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar token Google: {e}")
            return False

google_auth = GoogleAuthService()
