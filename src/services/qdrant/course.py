from datetime import datetime
import uuid
from src.model.qdrant.course import Course
from src.model.qdrant.lecture import Lecture
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


async def add_lecture_to_qdrant(
    lecture_title: str,
    lecture_description: str,
    lecture_video_url: str,
    course_id: str,
):
    """Add a lecture to qdrant"""
    from main import lecture_store

    try:

        last_index = 0

        lecture = Lecture(
            lecture_id=str(uuid.uuid4()),
            course_id=course_id,
            title=lecture_title,
            description=lecture_description,
            video_url=lecture_video_url,
            index=last_index + 1,
        )

        lecture_metadata = lecture.model_dump()
        lecture_metadata.pop("title")

        documents = Document(
            page_content=lecture_title,
            metadata=lecture_metadata,
        )
        await lecture_store.aadd_documents([documents])
        return lecture.lecture_id
    except Exception as e:
        logger.error(f"Error adding lecture to qdrant: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error adding lecture to qdrant: {e}"
        )
