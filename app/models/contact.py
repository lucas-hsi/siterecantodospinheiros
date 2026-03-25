from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

from app.database import Base


class ContactMessage(Base):
    """Modelo de mensagem de contato recebida pelo site."""

    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    mensagem = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    lido = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<ContactMessage {self.id} - {self.nome} ({'lido' if self.lido else 'não lido'})>"
