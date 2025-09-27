from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import MessageIn, MessageOut
from repositories import MessageRepository
from services import MessageService
from auth import require_api_key

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Message API", version="1.0")


@app.post("/api/messages", response_model=dict)
async def create_message(
    message: MessageIn,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """
    Crea un nuevo mensaje en la base de datos.

    Args:
        message (MessageIn): Datos del mensaje a crear.
        db (Session): Sesión de base de datos.
        api_key (str): Clave API validada por dependencia.

    Returns:
        dict: Diccionario con la forma:
            {
                "status": "success",
                "data": { ...mensaje guardado... }
            }

    Errores:
        400: Si el `message_id` ya existe en la base de datos.
        500: Si ocurre un error inesperado al guardar el mensaje.
    """
    repo = MessageRepository(db)
    service = MessageService(repo)
    try:
        saved = service.save_message(message)

        # Normalizar salida: siempre bajo "data"
        if hasattr(saved, "to_dict"):
            saved_dict = saved.to_dict()
        else:
            saved_dict = dict(saved) if not isinstance(saved, dict) else saved

        return {"status": "success", "data": saved_dict}
    except Exception as e:
        import sqlalchemy
        if isinstance(e.__cause__, sqlalchemy.exc.IntegrityError) or isinstance(
            e, sqlalchemy.exc.IntegrityError
        ):
            raise HTTPException(status_code=400, detail="ID duplicado")
        raise HTTPException(status_code=500, detail="Error al guardar el mensaje")


@app.get("/api/messages/{session_id}", response_model=dict)
async def get_messages(
    session_id: str,
    limit: int = 10,
    offset: int = 0,
    sender: str | None = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """
    Obtiene todos los mensajes de una sesión, con soporte para paginación
    y filtro opcional por tipo de emisor (`sender`).

    Args:
        session_id (str): ID de la sesión a consultar.
        limit (int, opcional): Número máximo de resultados (default: 10).
        offset (int, opcional): Número de resultados a omitir (default: 0).
        sender (str | None, opcional): Filtrar por tipo de emisor ("user" o "system").
        db (Session): Sesión de base de datos.
        api_key (str): Clave API validada por dependencia.

    Returns:
        dict: Diccionario con la forma:
            {
                "status": "success",
                "results": [ ...lista de mensajes... ]
            }

    Errores:
        500: Si ocurre un error inesperado en la consulta.
    """
    repo = MessageRepository(db)
    service = MessageService(repo)
    results = service.get_messages(session_id, limit, offset, sender)
    return {"status": "success", "results": [r.to_dict() for r in results]}


@app.get("/api/messages/{session_id}/search", response_model=dict)
async def search_messages(
    session_id: str,
    q: str = Query(..., min_length=2, description="Texto a buscar"),
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    """
    Busca mensajes en una sesión filtrando por texto dentro del contenido.

    Args:
        session_id (str): ID de la sesión a consultar.
        q (str): Texto a buscar dentro del contenido de los mensajes.
        limit (int, opcional): Número máximo de resultados (default: 10).
        offset (int, opcional): Número de resultados a omitir (default: 0).
        db (Session): Sesión de base de datos.
        api_key (str): Clave de API validada por dependencia.

    Returns:
        dict: Respuesta con la forma:
            {
                "status": "success",
                "results": [ { "message_id": str, "session_id": str, ... }, ... ]
            }

    Raises:
        HTTPException(400): Si el término de búsqueda es demasiado corto (<2).
        HTTPException(500): Si ocurre un error inesperado durante la búsqueda.
    """
    repo = MessageRepository(db)
    service = MessageService(repo)
    results = service.search_messages(session_id, q, limit, offset)
    return {"status": "success", "results": [r.to_dict() for r in results]}
