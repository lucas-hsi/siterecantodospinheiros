import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum

from app.database import Base


class Reservation(Base):
    """Modelo de pré-reserva de evento."""

    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    telefone = Column(String(20), nullable=False)
    data_evento = Column(String(10), nullable=False)  # YYYY-MM-DD
    tipo_evento = Column(String(100), nullable=False)
    num_convidados = Column(Integer, nullable=False)
    horario_inicio = Column(String(5), nullable=False)  # HH:MM
    horario_fim = Column(String(5), nullable=False)      # HH:MM
    servicos_adicionais = Column(Text, default="[]")      # JSON array
    observacoes = Column(Text, default="")
    status = Column(
        String(20),
        default="pendente",
        nullable=False,
    )  # pendente | confirmado | cancelado
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def servicos_list(self) -> list:
        """Retorna serviços adicionais como lista Python."""
        try:
            return json.loads(self.servicos_adicionais) if self.servicos_adicionais else []
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self):
        return f"<Reservation {self.id} - {self.nome} - {self.data_evento} ({self.status})>"
