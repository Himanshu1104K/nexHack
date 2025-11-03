from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from src.models.user.enrolled_user import EnrolledUser
from src.models.teachers.instructor import Instructor
from typing import List
from datetime import datetime


class CourseCollection(BaseModel):
    """Course collection schema for Qdrant."""

    _id: str = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    teacher_id: str = Field(..., description="Teacher ID")
    instructor: Instructor = Field(..., description="Instructor")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    total_lectures: int = Field(..., description="Total lectures")
    total_duration: int = Field(..., description="Total duration in seconds")
    enrolled_users: List[EnrolledUser] = Field(..., description="Enrolled users")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
