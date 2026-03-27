import io
import os
from fpdf import FPDF
from app.config import settings
from itsdangerous import URLSafeSerializer
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

# Secret key fall-back for itsdangerous 
SECRET_KEY = getattr(settings, "SECRET_KEY", "recantos-secret-key-super-safe")
serializer = URLSafeSerializer(SECRET_KEY)

class PDFGenerator(FPDF):
    def header(self):
        # Background or Logo
        logo_path = os.path.join(settings.IMAGES_DIR, "logo.png")
        try:
            # Add logo at the top center
            # fpdf2 allows image path as string
            if os.path.exists(logo_path):
                self.image(logo_path, x=85, y=10, w=40)
        except Exception as e:
            logger.error(f"Erro ao carregar logo no PDF: {e}")
        
        self.set_y(55)
        # Font: Arial bold 15
        self.set_font("helvetica", "B", 18)
        self.set_text_color(26, 60, 42) # Verde escuro
        # Title
        self.cell(0, 10, "DOCUMENTO DE PRÉ-RESERVA", align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Subtitle / Address
        self.set_font("helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Chácara Recanto dos Pinheiros | Seu Evento dos Sonhos", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Rua Dr. Leocádio José Corrêa, 1 - Roseira - Colombo, PR", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, f"WhatsApp: {settings.WHATSAPP_NUMBER} | Seg-Sex: 8h às 19h", align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, "Este documento é uma pré-reserva oficial sujeita a confirmação de disponibilidade e validação de pagamento.", align="C")

class PDFService:
    @staticmethod
    def generate_token(form_data: dict) -> str:
        """Codifica de forma segura os dados do formulário em uma String"""
        return serializer.dumps(form_data)

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica com segurança garantindo que ninguém alterou o JSON."""
        try:
            return serializer.loads(token)
        except Exception:
            return None

    @staticmethod
    def generate_pdf_from_token(token: str) -> io.BytesIO:
        """Cria o PDF baseado no Token em memória."""
        data = PDFService.decode_token(token)
        if not data:
            raise ValueError("Token de reserva inválido, expirado ou corrompido.")

        pdf = PDFGenerator()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        def add_row(label, value):
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(26, 60, 42)
            # Label box
            pdf.cell(50, 8, label, border=0)
            
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(0, 0, 0)
            # multi_cell to handle long text properly
            pdf.multi_cell(0, 8, str(value), border=0, new_x="LMARGIN", new_y="NEXT")

        # Sessão 1: Dados do Cliente
        pdf.set_font("helvetica", "B", 14)
        pdf.set_fill_color(240, 245, 241)
        pdf.cell(0, 10, "  Dados do Contratante", border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        add_row("Nome Completo:", data.get("nome", ""))
        add_row("E-mail:", data.get("email", ""))
        add_row("WhatsApp:", data.get("telefone", ""))
        pdf.ln(8)

        # Sessão 2: Dados do Evento
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "  Detalhes do Evento", border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        try:
            data_evento = datetime.strptime(data.get("data_evento", ""), "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            data_evento = data.get("data_evento", "")

        add_row("Tipo de Evento:", data.get("tipo_evento", ""))
        add_row("Data Escolhida:", data_evento)
        add_row("Horário:", f"{data.get('horario_inicio', '')} às {data.get('horario_fim', '')}")
        add_row("Nº de Convidados:", data.get("num_convidados", ""))
        pdf.ln(8)

        # Sessão 3: Serviços e Observações
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "  Serviços e Observações", border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        servicos = data.get("servicos_adicionais", [])
        if not servicos:
            add_row("Serviços Adicionais:", "Nenhum selecionado.")
        else:
            add_row("Serviços Adicionais:", ", ".join(servicos))
            
        obs = data.get("observacoes", "")
        if obs:
            add_row("Observações:", obs)

        pdf.ln(8)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(200, 30, 30)
        pdf.cell(0, 10, "Mensagem do Sistema:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        
        warn_text = "Esta é uma demonstração automatizada. O administrador entrará em contato " \
                    "em breve para alinhar os valores, assinatura de contrato e confirmação da data."
        pdf.multi_cell(0, 6, warn_text, new_x="LMARGIN", new_y="NEXT")

        # Export to ByteStream
        pdf_bytes = pdf.output()
        return io.BytesIO(pdf_bytes)

pdf_service = PDFService()
