from typing import Any, Dict
from pydantic import BaseModel, Field


class User(BaseModel):
    """User Qdrant Model"""

    user_id: str = Field(..., description="User ID")
    courses: list[Dict[str, Any]] = Field(
        ..., description="Courses with their particular lecture index"
    )
