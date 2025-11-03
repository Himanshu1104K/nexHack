from pydantic import BaseModel, Field


class Lecture(BaseModel):
    """Lecture Qdrant Model"""

    lecture_id: str = Field(..., description="Lecture ID")
    course_id: str = Field(..., description="Course ID")
    title: str = Field(..., description="Lecture title")
    description: str = Field(..., description="Lecture description")
    duration: int = Field(..., description="Lecture duration in seconds")
    video_url: str = Field(..., description="Lecture video URL")
    index: int = Field(..., description="Lecture index")
