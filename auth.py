from fastapi import Header, HTTPException

EXPECTED_API_KEY = "mi-api-key-secreta"

def require_api_key(x_api_key: str = Header(None)):
    """
    Valida API Key en encabezado 'x-api-key'.
    - Si falta: 401
    - Si es incorrecta: 403
    """
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="API key requerida")
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="API key inválida")
    return x_api_key
