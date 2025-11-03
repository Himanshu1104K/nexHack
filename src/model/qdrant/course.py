from datetime import datetime
from pydantic import BaseModel, Field


class Course(BaseModel):
    """Course Qdrant Model"""

    course_id: str = Field(..., description="Course ID")
    teacher_id: str = Field(..., description="Teacher ID")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    total_lectures: int = Field(..., description="Total lectures")
    enrolled_users: list[str] = Field(..., description="Enrolled users")
    created_at: datetime = Field(..., description="Created at")
