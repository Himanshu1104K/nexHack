"""
Async Google‑Calendar tools for Ova’s Calendar Agent
Drop this file into `src/domain/graph_tools/calendar_tools/calendar_tools.py`
and update your imports accordingly.
"""

from typing import Optional

import httpx
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from src.core.configs import (
    CALENDAR_SCOPES,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)
from src.core.utility.logging_utils import get_logger
from src.model.chat.state import ChatState

logger = get_logger(__name__)

# ─────────────────────  CALENDAR SERVICE  ─────────────────────


async def get_calendar_service(state: ChatState):
    """
    Return an authenticated Google Calendar service or ``None`` on failure.
    ``state`` MUST contain keys: user_id, refreshToken (and maybe accessToken).
    """
    try:
        user_id = state["user_id"]
        from main import db_teacher

        user = await db_teacher.document(user_id).get()
        if not user.exists:
            logger.error(f"User {user_id} not found")
            return None

        token = user.get("accessToken")
        refresh_token = user.get("refreshToken")

        creds = Credentials(
            token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=CALENDAR_SCOPES,
        )
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        logger.exception(
            f"Error building calendar service for user {user_id}: {str(e)}"
        )
        return None


async def validate_token(token: str) -> bool:
    """Check an access‑token with Google (non‑blocking)."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v1/tokeninfo",
            params={"access_token": token},
        )
    return resp.status_code == 200


async def get_new_token(refresh_token: str) -> Optional[str]:
    """Exchange a refresh‑token for a new access‑token."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "refresh_token",
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if resp.status_code == 200:
        access_token = resp.json().get("access_token")
        return access_token
    return None


async def update_user_tokens(user_id: str) -> None:
    """Clear invalid tokens in Firestore so user can re‑auth."""
    from main import db_teacher  # local import to avoid circularity
    from google.api_core.exceptions import NotFound

    try:
        db_teacher.document(user_id).update(
            {"access_token": "", "refresh_token": ""}
        )
        logger.info(f"Purged stale tokens for user {user_id}")
    except NotFound:
        logger.warning(
            f"User document {user_id} not found in Firestore, skipping token cleanup"
        )
    except Exception as e:
        logger.error(f"Failed to update tokens for user {user_id}: {str(e)}")
