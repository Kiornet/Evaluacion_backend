"""
Tests unitarios para la capa de servicios y repositorios.

Incluye validaciones de:
- Modelo Pydantic (sender válido/ inválido).
- Servicio (censura de malas palabras y metadata).
- Repositorio ORM (CRUD completo, unicidad, búsqueda insensible, filtros y paginación).
"""

import pytest
from uuid import uuid4
from models import MessageIn as Message
from services import MessageService
from repositories import MessageRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from datetime import datetime
import sqlalchemy


# ---------- FIXTURES ----------
@pytest.fixture
def repo():
    """Crea un repositorio con base de datos SQLite en memoria."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield MessageRepository(db)
    finally:
        db.close()


@pytest.fixture
def service(repo: MessageRepository):
    """Devuelve un MessageService con el repositorio de pruebas."""
    return MessageService(repo)


# ---------- TESTS DE MODELO ----------
def test_valid_sender_raises():
    """Sender inválido debe disparar excepción en modelo Pydantic."""
    with pytest.raises(Exception):
        Message(
            message_id=str(uuid4()),
            session_id="test-session",
            content="Hola",
            timestamp=datetime.fromisoformat("2025-09-23T14:30:00+00:00"),
            sender="robot"  # inválido
        )


# ---------- TESTS DE SERVICIO ----------
def test_censorship(service: MessageService):
    """Servicio debe censurar malas palabras y añadir metadata."""
    message = Message(
        message_id=str(uuid4()),
        session_id="test-session",
        content="Hola tonto idiota",
        timestamp=datetime.fromisoformat("2025-09-23T14:30:00+00:00"),
        sender="user"
    )
    resultat = service.process_message(message)

    assert "***" in resultat["content"]
    assert resultat["metadata"]["length"] == len("Hola tonto idiota")
    assert set(resultat["metadata"]["bad_words"]) == {"tonto", "idiota"}


def test_search_short_term(service: MessageService):
    """Query muy corta (<2) debe lanzar ValueError."""
    with pytest.raises(ValueError):
        service.search_messages("sess", "a")


# ---------- TESTS DE REPOSITORIO ----------
def test_duplicate_id(repo: MessageRepository):
    """Dos mensajes con el mismo ID deben generar IntegrityError."""
    msg_id = str(uuid4())
    message = {
        "message_id": msg_id,
        "session_id": "unit-session",
        "content": "Test mensaje",
        "timestamp": datetime.utcnow(),
        "sender": "user",
        "processed_at": datetime.utcnow()
    }
    repo.save(message)

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        repo.save(message)


def test_search(repo: MessageRepository):
    """Buscar debe devolver resultados insensible a mayúsculas."""
    msg1 = {
        "message_id": str(uuid4()),
        "session_id": "search-sess",
        "content": "Buscar esto",
        "timestamp": datetime.utcnow(),
        "sender": "user",
        "processed_at": datetime.utcnow()
    }
    msg2 = {
        "message_id": str(uuid4()),
        "session_id": "search-sess",
        "content": "No coincide",
        "timestamp": datetime.utcnow(),
        "sender": "user",
        "processed_at": datetime.utcnow()
    }
    repo.save(msg1)
    repo.save(msg2)

    results = repo.search_messages("search-sess", "buscar")
    assert any("buscar" in m.content.lower() for m in results)


def test_get_by_session_with_sender(repo: MessageRepository):
    """Filtrar por sender debe devolver solo mensajes de ese tipo."""
    msg_user = {
        "message_id": str(uuid4()),
        "session_id": "filter-sess",
        "content": "mensaje user",
        "timestamp": datetime.utcnow(),
        "sender": "user",
        "processed_at": datetime.utcnow()
    }
    msg_system = {
        "message_id": str(uuid4()),
        "session_id": "filter-sess",
        "content": "mensaje system",
        "timestamp": datetime.utcnow(),
        "sender": "system",
        "processed_at": datetime.utcnow()
    }
    repo.save(msg_user)
    repo.save(msg_system)

    results_user = repo.get_by_session("filter-sess", limit=10, offset=0, sender="user")
    assert all(m.sender == "user" for m in results_user)
    assert len(results_user) == 1


# ---------- TESTS ROBUSTOS EXTRA ----------
def test_crud_message(repo: MessageRepository):
    """Validar ciclo completo CRUD con ORM."""
    msg_id = str(uuid4())
    message = {
        "message_id": msg_id,
        "session_id": "crud-sess",
        "content": "Mensaje inicial",
        "timestamp": datetime.utcnow(),
        "sender": "user",
        "processed_at": datetime.utcnow()
    }

    # Crear
    repo.save(message)
    results = repo.get_by_session("crud-sess")
    assert any(m.message_id == msg_id for m in results)

    # Actualizar
    obj = results[0]
    obj.content = "Mensaje actualizado"
    repo.db.commit()
    repo.db.refresh(obj)
    assert obj.content == "Mensaje actualizado"

    # Eliminar
    repo.db.delete(obj)
    repo.db.commit()
    results_after = repo.get_by_session("crud-sess")
    assert not any(m.message_id == msg_id for m in results_after)


def test_pagination(repo: MessageRepository):
    """La paginación debe devolver subconjuntos correctos."""
    session_id = "pag-sess"
    for i in range(5):
        repo.save({
            "message_id": str(uuid4()),
            "session_id": session_id,
            "content": f"msg {i}",
            "timestamp": datetime.utcnow(),
            "sender": "user",
            "processed_at": datetime.utcnow()
        })

    results_page1 = repo.get_by_session(session_id, limit=2, offset=0)
    results_page2 = repo.get_by_session(session_id, limit=2, offset=2)

    assert len(results_page1) == 2
    assert len(results_page2) == 2
    assert results_page1[0].message_id != results_page2[0].message_id


def test_search_case_insensitive(repo: MessageRepository):
    """Búsqueda debe ser insensible a mayúsculas/minúsculas."""
    msg = {
        "message_id": str(uuid4()),
        "session_id": "case-sess",
        "content": "Texto de Prueba",
        "timestamp": datetime.utcnow(),
        "sender": "user",
        "processed_at": datetime.utcnow()
    }
    repo.save(msg)

    results_lower = repo.search_messages("case-sess", "texto")
    results_upper = repo.search_messages("case-sess", "TEXTO")

    assert results_lower
    assert results_upper
    assert results_lower[0].message_id == results_upper[0].message_id
