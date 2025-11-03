from src.core.utility.logging_utils import get_logger
from fastapi import HTTPException
from src.models.teachers.instructor import Instructor

logger = get_logger(__name__)


async def get_instructor_from_firestore(instructor_id: str):
    from main import db_teacher

    try:
        instructor_doc_ref = db_teacher.document(instructor_id)
        instructor_doc = instructor_doc_ref.get()
        instructor = Instructor(**instructor_doc.to_dict())
        return instructor
    except Exception as e:
        logger.error(f"Error getting instructor from firestore: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting instructor from firestore: {e}"
        )
