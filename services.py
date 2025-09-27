# services.py
from datetime import datetime, timezone
import re
from models import MessageORM

class MessageService:
    """
    Servicio que encapsula la lógica de negocio para manejar mensajes.

    Métodos principales:
    - Procesar mensajes: censura palabras prohibidas y agrega metadatos.
    - Guardar mensajes: valida, procesa y persiste mensajes en la base de datos.
    - Buscar mensajes: realiza búsquedas por contenido dentro de una sesión.
    """

    def __init__(self, repository):
        """
        Inicializa el servicio con un repositorio de mensajes.

        Args:
            repository (MessageRepository): Repositorio para interactuar con la base de datos.
        """
        self.repository = repository
        self.bad_words = {"tonto", "idiota"}

    def _ensure_dict(self, message):
        """
        Asegura que el mensaje sea un diccionario.

        Args:
            message (Union[BaseModel, dict]): Mensaje a procesar.

        Returns:
            dict: Representación del mensaje como diccionario.
        """
        if hasattr(message, "model_dump"):
            return message.model_dump()
        if isinstance(message, dict):
            return message
        return dict(message)

    def process_message(self, message):
        """
        Procesa un mensaje censurando palabras prohibidas y agregando metadatos.

        Args:
            message (dict): Datos del mensaje a procesar.

        Returns:
            dict: Mensaje procesado con contenido censurado y metadatos.
        """
        data = self._ensure_dict(message)
        original = data.get("content", "")
        pattern = re.compile(r"\b(" + "|".join(map(re.escape, self.bad_words)) + r")\b", re.IGNORECASE)
        found = {w.lower() for w in pattern.findall(original)}
        censored = pattern.sub("***", original)
        metadata = {"length": len(original), "bad_words": sorted(list(found))}
        result = data.copy()
        result["content"] = censored
        result["metadata"] = metadata
        result["processed_at"] = datetime.now(timezone.utc)
        return result

    def save_message(self, message_data):
        """
        Valida, procesa y guarda un mensaje en la base de datos.

        Args:
            message_data (dict): Datos del mensaje a guardar.

        Returns:
            dict: Mensaje guardado en la base de datos.
        """
        md = self._ensure_dict(message_data)
        processed = self.process_message(md)
        saved = self.repository.save(processed)
        return saved

    def get_messages(self, session_id: str, limit: int = 10, offset: int = 0, sender: str | None = None):
        """
        Obtiene mensajes de una sesión con soporte de paginación y filtro opcional por remitente.

        Args:
            session_id (str): ID de la sesión.
            limit (int): Número máximo de mensajes a devolver.
            offset (int): Desplazamiento inicial para la paginación.
            sender (str, opcional): Filtrar mensajes por remitente.

        Returns:
            list[dict]: Lista de mensajes encontrados.
        """
        return self.repository.get_by_session(session_id, limit, offset, sender)

    def search_messages(self, session_id: str, query: str, limit: int = 10, offset: int = 0):
        """
        Busca mensajes en una sesión filtrando por contenido.

        Args:
            session_id (str): ID de la sesión.
            query (str): Texto a buscar dentro del contenido de los mensajes.
            limit (int, opcional): Número máximo de resultados.
            offset (int, opcional): Desplazamiento inicial para la paginación.

        Returns:
            list[dict]: Lista de mensajes encontrados que coinciden con la búsqueda.
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("El término de búsqueda es demasiado corto")
        return self.repository.search_messages(session_id, query, limit, offset)
