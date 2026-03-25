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
        Obtém credenciais válidas da Variável de Ambiente ou arquivo.
        """
        creds = None
        import json
        
        # 1. Tenta carregar da Variável de Ambiente (Vercel Prod)
        if settings.GOOGLE_TOKEN_JSON:
            try:
                token_data = json.loads(settings.GOOGLE_TOKEN_JSON)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            except Exception as e:
                logger.error(f"Erro ao carregar token do Env Var: {e}")
        # 2. Tenta carregar do arquivo físico (Local Dev)
        elif os.path.exists(settings.GOOGLE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_FILE, SCOPES)
        
        # Se não houver credenciais válidas, tenta dar refresh
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                token_json = creds.to_json()
                
                # Só escreve no arquivo se LOCAL
                if not settings.GOOGLE_TOKEN_JSON:
                    with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                        token.write(token_json)
                else:
                    logger.warning(f"Vercel: Token atualizado em memória. Novo token a ser salvo no Vercel (opcionalmente): {token_json}")
            except Exception as e:
                logger.error(f"Erro ao atualizar token Google: {e}")
                creds = None
        
        return creds

    @staticmethod
    def get_auth_flow(redirect_uri: str) -> Flow:
        """Cria o fluxo de autenticação OAuth2 (suporta Vercel Env Vars)."""
        import json
        if settings.GOOGLE_CLIENT_SECRET_JSON:
            client_config = json.loads(settings.GOOGLE_CLIENT_SECRET_JSON)
            return Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
        else:
            return Flow.from_client_secrets_file(
                settings.GOOGLE_CLIENT_SECRET_FILE,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )

    @staticmethod
    def save_credentials_from_code(code: str, redirect_uri: str) -> tuple[bool, str]:
        """Troca o código pelo token e salva no token.json (se local). Retorna (Sucesso, Json)"""
        try:
            flow = GoogleAuthService.get_auth_flow(redirect_uri)
            flow.fetch_token(code=code)
            creds = flow.credentials
            token_json = creds.to_json()
            
            # Tenta salvar em arquivo (funciona apenas Local)
            try:
                with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                    token.write(token_json)
                logger.info("Token Google OAuth2 salvo em arquivo com sucesso.")
            except Exception as e:
                logger.warning(f"Read-only FS, não salvou arquivo (Normal na Vercel).")
                
            return True, token_json
        except Exception as e:
            logger.error(f"Erro ao processar auth Google: {e}")
            return False, ""

google_auth = GoogleAuthService()
