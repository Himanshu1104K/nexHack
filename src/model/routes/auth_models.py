from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class DeviceData(BaseModel):
    """Device data schema for authentication."""

    fcm_token: Optional[str] = Field("", description="Firebase Cloud Messaging token")
    timezone: Optional[str] = Field("Asia/Kolkata", description="User's timezone")


class AuthRequest(BaseModel):
    """Request body for `POST /auth/user`."""

    firebase_token: str = Field(..., description="Firebase authentication token")
    device_data: DeviceData = Field(
        default_factory=DeviceData, description="Device and user configuration data"
    )


class AuthResponse(BaseModel):
    """Response schema for `POST /auth/user`."""

    status: str = Field(..., description="Authentication status")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (bearer)")
    expires_in: int = Field(..., description="Token expiration time in seconds")
