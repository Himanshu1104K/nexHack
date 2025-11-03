from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class Instructor(BaseModel):
    """Instructor schema for Qdrant."""

    id: str = Field(..., description="Instructor ID")
    name: str = Field(..., description="Instructor name")
    avatar: Optional[str] = Field(None, description="Avatar URL")
