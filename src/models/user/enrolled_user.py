from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class EnrolledUser(BaseModel):
    """Enrolled user schema for Qdrant."""

    user_id: str = Field(..., description="User ID")
    enrolled_at: datetime | None = Field(None, description="Enrolled at")
