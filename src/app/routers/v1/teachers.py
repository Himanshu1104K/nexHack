from typing import cast
from fastapi import APIRouter, HTTPException, Depends
from src.core.utility.logging_utils import get_logger
from src.services.auth.verify_token import verify_token
from src.services.qdrant.course import add_course_to_qdrant
from src.models.desc_agent.descstate import DESCSTATE

logger = get_logger(__name__)

router = APIRouter(tags=["Teachers"])


@router.post("/create-course")
async def create_course(
    course_title: str,
    course_description: str,
    token_data: dict = Depends(verify_token),
):
    """Create a new course"""
    user_type = token_data.get("user_type")
    if user_type != "teacher":
        raise HTTPException(status_code=403, detail="Forbidden")
    teacher_id = token_data.get("sub")

    try:
        course_id = await add_course_to_qdrant(
            course_title=course_title,
            course_description=course_description,
            teacher_id=teacher_id,
        )

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
