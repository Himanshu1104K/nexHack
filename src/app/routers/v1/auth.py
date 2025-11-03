from ctypes import cast
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from src.core.configs import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.core.utility.logging_utils import get_logger
from src.model.routes.auth_models import AuthRequest, AuthResponse
from src.services.auth.create_jwt import create_jwt_token
from src.model.firestore.state import User, Teacher

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
                user_data = cast(
                    User,
                    {
                        "user_id": user_id,
                        "user_email": user_email,
                        "user_name": user_record.display_name or "Apple User",
                        "fcm_tokens": fcm_tokens,
                        "timezone": request.device_data.timezone or "Asia/Kolkata",
                        "profile_url": user_record.photo_url
                        or "https://avatar.iran.liara.run/public",
                    },
                )

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
                teacher_data = cast(
                    Teacher,
                    {
                        "user_id": user_id,
                        "user_email": user_email,
                        "user_name": user_record.display_name or "Apple User",
                        "fcm_tokens": fcm_tokens,
                        "timezone": request.device_data.timezone or "Asia/Kolkata",
                        "profile_url": user_record.photo_url
                        or "https://avatar.iran.liara.run/public",
                        "access_token": "",
                        "refresh_token": "",
                    },
                )

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
