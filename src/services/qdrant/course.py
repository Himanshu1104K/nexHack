from datetime import datetime
import uuid
from src.model.qdrant.course import Course
from src.core.utility.logging_utils import get_logger
from fastapi import HTTPException
from langchain_core.documents import Document

logger = get_logger(__name__)


async def add_course_to_qdrant(
    course_title: str,
    course_description: str,
    teacher_id: str,
):
    """Add a course to qdrant"""
    from main import teacher_store

    try:
        course = Course(
            course_id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            title=course_title,
            description=course_description,
            total_lectures=0,
            enrolled_users=[],
            created_at=datetime.now(),
        )

        course_metadata = course.model_dump()
        course_metadata.pop("title")

        documents = Document(
            page_content=course_title,
            metadata=course_metadata,
        )
        await teacher_store.aadd_documents([documents])

        return course.course_id
    except Exception as e:
        logger.error(f"Error adding course to qdrant: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error adding course to qdrant: {e}"
        )
