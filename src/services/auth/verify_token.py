from datetime import datetime
from fastapi import HTTPException, Header
from jose import JWTError, jwt
from typing import Optional, Dict
from src.core.configs import JWT_SECRET_KEY, JWT_ALGORITHM


async def verify_token(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Verify JWT token from Authorization header

    Args:
        authorization: The Authorization header value

    Returns:
        Dict: The decoded token payload

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Remove 'Bearer ' prefix if present
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
        else:
            token = authorization

        # Decode and validate the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Check if token has expired
        if "exp" in payload and datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401, detail=f"Invalid authentication token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")
