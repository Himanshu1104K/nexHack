from datetime import datetime
import uuid
from src.models.qdrant_models.course_collection import CourseCollection
from src.core.utility.logging_utils import get_logger
from fastapi import HTTPException
from src.services.firestore.instructor import get_instructor_from_firestore
from langchain_core.documents import Document

logger = get_logger(__name__)


async def add_course_to_qdrant(course: CourseCollection):
    from main import teacher_store

    try:
        course_id = str(uuid.uuid4())
        course._id = course_id
        course.created_at = datetime.now()
        course.updated_at = datetime.now()
        course.instructor = await get_instructor_from_firestore(course.instructor.id)
        course.total_lectures = 0
        course.total_duration = 0
        course.enrolled_users = []

        course_metadata = course.model_dump()
        course_metadata.pop("title")
        documents = Document(page_content=course.title, metadata=course_metadata)

        await teacher_store.aadd_documents([documents])

        return course_id
    except Exception as e:
        logger.error(f"Error adding course to qdrant: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error adding course to qdrant: {e}"
        )
