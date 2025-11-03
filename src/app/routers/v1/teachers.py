from typing import cast
from fastapi import APIRouter, HTTPException
from src.core.utility.logging_utils import get_logger
from src.models.qdrant_models.course_collection import CourseCollection
from src.services.qdrant.course import add_course_to_qdrant
from src.models.desc_agent.descstate import DESCSTATE

logger = get_logger(__name__)

router = APIRouter(tags=["Teachers"])


@router.post("/create-course")
async def create_course(course: CourseCollection):
    """Create a new course"""
    try:
        course_id = await add_course_to_qdrant(course)

        return {
            "message": "Course created successfully",
            "course_id": course_id,
        }
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating course: {e}")


@router.post("/create-desc")
async def create_desc(yt_link: str):
    """Create a new description"""
    from main import desc_graph

    try:
        state = cast(
            DESCSTATE,
            {
                "yt_link": yt_link,
                "yt_desc": "",
            },
        )
        return await desc_graph.ainvoke(state)
    except Exception as e:
        logger.error(f"Error creating description: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating description: {e}")
