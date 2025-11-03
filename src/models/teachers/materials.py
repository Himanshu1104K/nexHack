from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class Material(BaseModel):
    """Material schema for Qdrant."""

    id: str = Field(..., description="Material ID")
    type: str = Field(..., description="Material type")
    title: str = Field(..., description="Material title")
    url: str = Field(..., description="Material URL")
    created_at: datetime = Field(..., description="Created at")


class Materials(BaseModel):
    """Materials schema for Qdrant."""

    materials: List[Material] = Field(..., description="Materials")
