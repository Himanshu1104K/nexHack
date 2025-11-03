from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from src.models.teachers.materials import Materials


class LectureCollection(BaseModel):
    """Course collection schema for Qdrant."""

    _id: str = Field(..., description="Lecture Id")
    course_id: str = Field(..., description="Course Id")
    title: str = Field(..., description="lecture title")
    description: str = Field(..., description="Course description")
    duration: int = Field(..., description="Duration in seconds")
    video_url: str = Field(..., description="Video URL")
    order: int = Field(..., description="Order")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
    materials: Materials = Field(..., description="Materials")
