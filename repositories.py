# repositories.py
from datetime import datetime
from models import MessageORM
from sqlalchemy.orm import Session

def _parse_iso_to_dt(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = value
    if isinstance(s, str) and s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, message_data: dict) -> MessageORM:
        """Guarda un mensaje. Puede lanzar IntegrityError si ID duplicado."""
        ts = _parse_iso_to_dt(message_data.get("timestamp"))
        processed_at = _parse_iso_to_dt(message_data.get("processed_at"))
        obj = MessageORM(
            message_id=message_data["message_id"],
            session_id=message_data["session_id"],
            content=message_data["content"],
            timestamp=ts,
            sender=message_data["sender"],
            processed_at=processed_at,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_session(self, session_id: str, limit: int = 10, offset: int = 0, sender: str | None = None):
        """Obtiene mensajes por sesión, opcionalmente filtrados por sender."""
        query = self.db.query(MessageORM).filter(MessageORM.session_id == session_id)
        if sender:
            query = query.filter(MessageORM.sender == sender)
        results = (
            query.order_by(MessageORM.timestamp.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return results

    def search_messages(self, session_id: str, query: str, limit: int = 10, offset: int = 0):
        """Busca mensajes por texto (case-insensitive)."""
        results = (
            self.db.query(MessageORM)
            .filter(
                MessageORM.session_id == session_id,
                MessageORM.content.ilike(f"%{query}%"),
            )
            .order_by(MessageORM.timestamp.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return results
