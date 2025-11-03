from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict
import requests
from firebase_admin import auth
from src.core.configs import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)
from src.core.utility.logging_utils import get_logger
from src.model.routes.auth_models import AuthRequest, AuthResponse
from src.services.auth.verify_token import verify_token
from src.services.auth.create_jwt import create_jwt_token

logger = get_logger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post(f"/auth", response_model=AuthResponse)
async def authenticate_user(user_type: str, request: AuthRequest):
    """Authenticate user with Firebase token, create/update user data in Firestore, and return JWT token"""

    if user_type not in ["user", "teacher"]:
        raise HTTPException(status_code=400, detail=f"Invalid user type: {user_type}")

    try:
        # Verify Firebase token
        decoded_token = auth.verify_id_token(request.firebase_token)
        user_id = decoded_token["uid"]
        user_record = auth.get_user(user_id)
        user_email = decoded_token.get("email", "")
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Firebase authentication failed: {str(e)}"
        )

    try:
        if user_type == "user":
            from main import db_user

            # Check if user exists in Firestore
            user_doc_ref = db_user.document(user_id)
            user_doc = user_doc_ref.get()
            is_old_user = user_doc.exists

            fcm_tokens = []
            if request.device_data.fcm_token not in [None, ""]:
                fcm_tokens.append(request.device_data.fcm_token)

            if not is_old_user:
                user_data = {
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_name": user_record.display_name or "Apple User",
                    "fcm_tokens": fcm_tokens,
                    "timezone": request.device_data.timezone or "Asia/Kolkata",
                    "profile_url": user_record.photo_url
                    or "https://avatar.iran.liara.run/public",
                }

                user_doc_ref.set(user_data)

            else:
                user_data = user_doc.to_dict()
                user_data["fcm_tokens"].extend(
                    token
                    for token in fcm_tokens
                    if token not in user_data["fcm_tokens"]
                )
                user_doc_ref.set(user_data)

        elif user_type == "teacher":
            from main import db_teacher

            # Check if user exists in Firestore
            teacher_doc_ref = db_teacher.document(user_id)
            teacher_doc = teacher_doc_ref.get()
            is_old_teacher = teacher_doc.exists

            fcm_tokens = []
            if request.device_data.fcm_token not in [None, ""]:
                fcm_tokens.append(request.device_data.fcm_token)

            if not is_old_teacher:
                teacher_data = {
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_name": user_record.display_name or "Apple User",
                    "fcm_tokens": fcm_tokens,
                    "timezone": request.device_data.timezone or "Asia/Kolkata",
                    "profile_url": user_record.photo_url
                    or "https://avatar.iran.liara.run/public",
                    "access_token": "",
                    "refresh_token": "",
                }

                teacher_doc_ref.set(teacher_data)

            else:
                teacher_data = teacher_doc.to_dict()
                teacher_data["fcm_tokens"].extend(
                    token
                    for token in fcm_tokens
                    if token not in teacher_data["fcm_tokens"]
                )
                teacher_doc_ref.set(teacher_data)

        token_data = {
            "sub": user_id,
            "email": user_email,
            "name": decoded_token.get("name", user_record.display_name or "Apple User"),
            "iat": datetime.utcnow(),
            "user_type": user_type,
        }

        # Create JWT access token
        access_token = create_jwt_token(
            data=token_data,
            expires_delta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {
            "status": "success",
            "user_type": user_type,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database operation failed: {str(e)}"
        )


class TokenRequest(BaseModel):
    """Request body for setting user token."""

    code: str = Field(..., description="Authorization code from Google OAuth")
    platform: Optional[str] = Field(None, description="Platform name")


@router.post("/user/token")
async def set_token(data: TokenRequest, token_data: dict = Depends(verify_token)):
    """Set user token"""
    code = data.code
    user_id = token_data.get("sub")

    if not code or not user_id:
        raise HTTPException(status_code=400, detail="Missing code or user_id")

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI if data.platform else "postmessage",
        "grant_type": "authorization_code",
    }
    try:
        token_response = requests.post(token_url, data=payload)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Token exchange request failed: {str(e)}"
        )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Failed to exchange code",
                "details": token_response.text,
            },
        )

    try:
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse token response: {str(e)}"
        )

    try:
        from main import db_teacher

        teacher_doc_ref = db_teacher.document(user_id)
        teacher_doc = teacher_doc_ref.get()
        teacher_data = teacher_doc.to_dict()
        teacher_data["access_token"] = access_token
        teacher_data["refresh_token"] = refresh_token
        teacher_doc_ref.set(teacher_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
    return JSONResponse(content={"message": "Token set successfully"})


@router.post("/user/reset/token")
async def reset_token(token_data: dict = Depends(verify_token)):
    try:
        from main import db_teacher

        user_id = token_data.get("sub")
        teacher_doc_ref = db_teacher.document(user_id)
        teacher_doc = teacher_doc_ref.get()
        teacher_data = teacher_doc.to_dict()
        teacher_data["access_token"] = ""
        teacher_data["refresh_token"] = ""
        teacher_doc_ref.set(teacher_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
    return JSONResponse(content={"message": "Token reset successfully"})


@router.get("/user/token/validate")
async def validate_token(token_data: Dict = Depends(verify_token)):
    user_id = token_data["sub"]

    from main import db_teacher

    teacher_doc_ref = db_teacher.document(user_id)
    teacher_doc = teacher_doc_ref.get()
    teacher_data = teacher_doc.to_dict()

    access_token = teacher_data.get("access_token")
    refresh_token = teacher_data.get("refresh_token")

    if not access_token or not refresh_token:
        return {"status": "error", "isValid": False, "message": "No tokens found"}

    # Validate the refresh token by attempting to use it
    is_refresh_token_valid = await validate_refresh_token(refresh_token)

    if not is_refresh_token_valid:
        return {
            "status": "error",
            "isValid": False,
            "message": "Refresh token is invalid or expired",
        }

    return {"status": "success", "isValid": True, "message": "Tokens are valid"}


async def validate_refresh_token(refresh_token: str) -> bool:
    """
    Validate refresh token by attempting to exchange it for a new access token.
    Returns True if the refresh token is valid, False otherwise.
    """
    if not refresh_token:
        return False

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()

        # If we get a successful response, the refresh token is valid
        return True

    except requests.exceptions.RequestException as e:
        # If we get an error (like invalid_grant), the refresh token is invalid
        return False
