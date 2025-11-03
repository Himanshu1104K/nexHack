from pydantic import BaseModel, Field


class User(BaseModel):
    """User Firestore State"""

    user_id: str = Field(..., description="User ID")
    user_email: str = Field(..., description="User email")
    user_name: str = Field(..., description="User name")
    fcm_tokens: list[str] = Field(..., description="FCM tokens")
    timezone: str = Field(..., description="User timezone")
    profile_url: str = Field(..., description="User profile URL")


class Teacher(BaseModel):
    """Teacher Firestore State"""

    user_id: str = Field(..., description="User ID")
    user_email: str = Field(..., description="User email")
    user_name: str = Field(..., description="User name")
    fcm_tokens: list[str] = Field(..., description="FCM tokens")
    timezone: str = Field(..., description="User timezone")
    profile_url: str = Field(..., description="User profile URL")
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
