"""
Modelos de datos y ORM para la aplicación de mensajes.
"""

from sqlalchemy import Column, String, DateTime
from datetime import datetime
from pydantic import BaseModel, field_validator
from database import Base as SQLBase  # alias para evitar colisiones


class MessageORM(SQLBase):
    """
    Modelo ORM que representa la tabla de mensajes en la base de datos.
    """
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    content = Column(String)
    timestamp = Column(DateTime)
    sender = Column(String)
    processed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """
        Convierte la instancia ORM a un diccionario serializable.
        """
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "sender": self.sender,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class MessageIn(BaseModel):
    """
    Modelo de entrada (request) para crear un mensaje.
    """
    message_id: str
    session_id: str
    content: str
    timestamp: datetime
    sender: str

    @field_validator("sender")
    def validate_sender(cls, v):
        if v not in {"user", "system"}:
            raise ValueError("Sender inválido, debe ser 'user' o 'system'")
        return v


class MessageOut(MessageIn):
    """
    Modelo de salida (response) para devolver un mensaje.
    processed_at se añade en el procesamiento.
    """
    processed_at: datetime | None = None
