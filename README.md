# 📩 Evaluación Técnica para Desarrollador Backend

## 📖 Descripción

Esta API permite manejar mensajes de usuarios y sistemas, con funcionalidades como:

- 📝 **Procesamiento de mensajes**
- 🚫 **Censura de palabras prohibidas**
- 🔑 **Autenticación vía API Key**
- 🗄️ **Almacenamiento en base de datos SQLite**
- ✅ **Pruebas unitarias e integración** con cobertura mínima del 80%

El proyecto está desarrollado en **Python 3.11+** usando **FastAPI**.

---
## 📂 Estructura del proyecto

```
evaluacion_backend/
├── __init__.py
├── main.py          # Entrypoint de la API
├── services.py      # Lógica de negocio y censura
├── repositories.py  # Interacción con la base de datos
├── models.py        # Modelos de datos Pydantic
├── auth.py          # Gestión de API Key
├── exception.py     # Manejo de errores y excepciones
├── database.py      # Conexión a SQLite
├── requirements.txt # Dependencias del proyecto
├── README.md        # Documentación del proyecto
│
├── tests/
│   ├── __init__.py
│   ├── unit/            # Pruebas unitarias
│   │   ├── __init__.py
│   │   └── test_unit.py
│   │
│   └── integration/     # Pruebas de integración
│       ├── __init__.py
│       └── test_api.py
```

---

## ⚙️ Requisitos

- Python **3.11** o superior  
- **pip**  
- Sistema operativo: Windows / Linux / macOS  

---

## 🚀 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repo>
   cd evaluacion_backend
   ```

2. **Crear un entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Linux/Mac
   venv\Scripts\activate      # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la API**
   ```bash
   uvicorn main:app --reload
   ```

---

## 📑 Documentación de la API

Una vez ejecutada, puedes acceder a:

- 📘 Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📗 ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔐 Autenticación

Todas las peticiones requieren un API Key en el header:

```http
x-api-key: mi-api-key-secreta
```

Si no se envía, se devuelve:

- **401 Unauthorized** → API Key faltante
- **403 Forbidden** → API Key inválida

---

## 📬 Endpoints principales

### ➕ Crear mensaje
```http
POST /api/messages
```
**Descripción:** Crea un nuevo mensaje en la base de datos.

**Body ejemplo:**
```json
{
  "message_id": "uuid",
  "session_id": "session-123",
  "content": "Hola mundo",
  "sender": "user"
}
```

**Respuesta ejemplo:**
```json
{
  "status": "success",
  "data": {
    "message_id": "uuid",
    "session_id": "session-123",
    "content": "Hola mundo",
    "sender": "user",
    "processed_at": "2025-09-26T12:00:00Z"
  }
}
```

---

### 📥 Obtener mensajes de sesión
```http
GET /api/messages/{session_id}
```
**Descripción:** Obtiene todos los mensajes de una sesión específica.

**Parámetros:**
- `session_id` (string): ID de la sesión.
- `limit` (int, opcional): Número máximo de resultados (default: 10).
- `offset` (int, opcional): Número de resultados a omitir (default: 0).
- `sender` (string, opcional): Filtrar por tipo de emisor (`user` o `system`).

**Respuesta ejemplo:**
```json
{
  "status": "success",
  "results": [
    {
      "message_id": "uuid",
      "session_id": "session-123",
      "content": "Hola mundo",
      "sender": "user",
      "processed_at": "2025-09-26T12:00:00Z"
    }
  ]
}
```

---

### 🔎 Buscar mensajes
```http
GET /api/messages/{session_id}/search
```
**Descripción:** Busca mensajes en una sesión específica filtrando por contenido textual.

**Parámetros:**
- `session_id` (string): ID de la sesión.
- `q` (string): Texto a buscar dentro del contenido de los mensajes.
- `limit` (int, opcional): Número máximo de resultados (default: 10).
- `offset` (int, opcional): Número de resultados a omitir (default: 0).

**Respuesta ejemplo:**
```json
{
  "status": "success",
  "results": [
    {
      "message_id": "uuid",
      "session_id": "session-123",
      "content": "Hola mundo",
      "sender": "user",
      "processed_at": "2025-09-26T12:00:00Z"
    }
  ]
}
```

---

## ✅ Respuestas de la API

- **200 OK** → Operación exitosa
- **422 Unprocessable Entity** → Error de validación
- **500 Internal Server Error** → Error interno del servidor

---

## 🧪 Pruebas

Ejecutar todas las pruebas (unitarias + integración):
```bash
pytest --maxfail=1 -v
```

Generar reporte de cobertura:
```bash
pytest --cov=. --cov-report=term-missing
```

Ejemplo de cobertura mínima esperada:
```text
TOTAL                              314     18    94%
```

---

## 📝 Notas finales

- El sistema censura automáticamente palabras prohibidas (tonto, idiota, estupido, burro).
- La base de datos utilizada es SQLite, simple y portable.
- El proyecto está diseñado para ser extensible y fácil de mantener.