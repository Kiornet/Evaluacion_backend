from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

# Manejo de validaciones de Pydantic (campos faltantes, formato inválido, etc.)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "errors": exc.errors()},
    )

# Manejo de HTTPException personalizado
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.detail},
    )

# Manejo de errores de servidor
async def server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "Error interno del servidor"},
    )