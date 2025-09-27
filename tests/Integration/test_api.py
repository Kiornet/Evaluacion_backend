"""
Tests de integración para la API FastAPI.

Estos tests validan:
- Creación de mensajes vía POST.
- Manejo de malas palabras.
- Validación de campos y sender.
- Detección de mensajes duplicados.
- Autenticación mediante API Key.
- Recuperación de mensajes por sesión.
- Paginación y búsqueda de mensajes.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# API Key definida en auth.py
VALID_API_KEY = "mi-api-key-secreta"
INVALID_API_KEY = "clave-mala"

# Headers de autenticación
HEADERS_VALID = {"x-api-key": VALID_API_KEY}
HEADERS_INVALID = {"x-api-key": INVALID_API_KEY}


def test_create_message_success():
    """
    Verifica que se pueda crear un mensaje válido correctamente.
    """
    message = {
        "message_id": str(uuid4()),
        "session_id": "session-test",
        "content": "Hola mundo",
        "timestamp": "2025-09-23T14:30:00Z",
        "sender": "user"
    }
    response = client.post("/api/messages", json=message, headers=HEADERS_VALID)
    assert response.status_code == 200


def test_create_message_success_with_bad_word():
    """
    Verifica que las malas palabras sean censuradas al crear un mensaje.
    """
    message = {
        "message_id": str(uuid4()),
        "session_id": "session-test",
        "content": "Hola mundo tonto idiota",
        "timestamp": "2025-09-23T14:30:00Z",
        "sender": "user"
    }
    response = client.post("/api/messages", json=message, headers=HEADERS_VALID)
    assert response.status_code == 200
    data = response.json()
    assert "***" in data["data"]["content"]


def test_create_message_missing_field():
    """
    Verifica que falten campos obligatorios genera un error 422.
    """
    message = {
        "message_id": str(uuid4()),
        "session_id": "session-test",
        "content": "Hola mundo",
        "timestamp": "2025-09-23T14:30:00Z"
    }
    response = client.post("/api/messages", json=message, headers=HEADERS_VALID)
    assert response.status_code == 422


def test_create_message_invalid_sender():
    """
    Verifica que un sender inválido genere un error 422 o 400.
    """
    message = {
        "message_id": str(uuid4()),
        "session_id": "session-test",
        "content": "Hola mundo",
        "timestamp": "2025-09-23T14:30:00Z",
        "sender": "robot"
    }
    response = client.post("/api/messages", json=message, headers=HEADERS_VALID)
    assert response.status_code in (422, 400)


def test_create_message_duplicate_id():
    """
    Verifica que dos mensajes con el mismo ID
    generen error 400 en la API.
    """
    msg_id = str(uuid4())
    message = {
        "message_id": msg_id,
        "session_id": "session-test",
        "content": "Mensaje único",
        "timestamp": "2025-09-23T14:30:00Z",
        "sender": "user"
    }
    client.post("/api/messages", json=message, headers=HEADERS_VALID)
    response2 = client.post("/api/messages", json=message, headers=HEADERS_VALID)
    assert response2.status_code == 400


def test_get_messages_by_session_with_pagination():
    """
    Verifica que los mensajes puedan recuperarse
    con límite y desplazamiento (limit/offset).
    """
    session_id = "session-pag"
    for i in range(5):
        message = {
            "message_id": str(uuid4()),
            "session_id": session_id,
            "content": f"mensaje {i}",
            "timestamp": "2025-09-23T14:30:00Z",
            "sender": "user"
        }
        client.post("/api/messages", json=message, headers=HEADERS_VALID)

    response = client.get(f"/api/messages/{session_id}?limit=2&offset=1", headers=HEADERS_VALID)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 2


def test_auth_missing_key():
    """
    Verifica que si no se envía API Key,
    la API responda con 401.
    """
    response = client.get("/api/messages/session-test")
    assert response.status_code == 401


def test_auth_invalid_key():
    """
    Verifica que una API Key incorrecta devuelva error 403.
    """
    response = client.get("/api/messages/session-test", headers=HEADERS_INVALID)
    assert response.status_code == 403


def test_auth_valid_key():
    """
    Verifica que una API Key válida permita acceder a la API.
    """
    response = client.get("/api/messages/session-test", headers=HEADERS_VALID)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_search_messages():
    """
    Verifica que la búsqueda devuelva los mensajes correctos
    cuando se consulta por una palabra clave.
    """
    message1 = {
        "message_id": str(uuid4()),
        "session_id": "search-session",
        "content": "Probando busqueda de mensajes",
        "timestamp": "2025-09-23T14:30:00Z",
        "sender": "user"
    }

    # Guardar mensaje
    response = client.post("/api/messages", json=message1, headers=HEADERS_VALID)
    assert response.status_code == 200

    # Buscar mensaje
    response = client.get("/api/messages/search-session/search?q=busqueda", headers=HEADERS_VALID)
    assert response.status_code == 200

    data = response.json()

    # Validar que la clave exista
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0

    # Validar que el mensaje encontrado contenga la palabra
    assert any("busqueda" in msg["content"].lower() for msg in data["results"])


def test_search_query_too_short():
    """
    Verifica que una query demasiado corta (len < 2)
    sea rechazada con error 422 (validación FastAPI).
    """
    response = client.get("/api/messages/session-test/search?q=a", headers=HEADERS_VALID)
    assert response.status_code == 422
