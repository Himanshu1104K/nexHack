from typing import cast
from fastapi import APIRouter, HTTPException, Depends
from src.core.utility.logging_utils import get_logger
from src.services.auth.verify_token import verify_token
from src.services.qdrant.course import add_course_to_qdrant
from src.models.desc_agent.descstate import DESCSTATE
from src.services.qdrant.course import add_lecture_to_qdrant

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


@router.post("/create-lecture")
async def create_lecture(
    lecture_title: str,
    lecture_description: str,
    lecture_video_url: str,
    course_id: str,
    token_data: dict = Depends(verify_token),
):
    """Create a new lecture"""
    user_type = token_data.get("user_type")
    if user_type != "teacher":
        raise HTTPException(status_code=403, detail="Forbidden")
    teacher_id = token_data.get("sub")

    lecture_id = await add_lecture_to_qdrant(
        lecture_title=lecture_title,
        lecture_description=lecture_description,
        lecture_video_url=lecture_video_url,
        course_id=course_id,
        teacher_id=teacher_id,
    )
    return {
        "message": "Lecture created successfully",
        "lecture_id": lecture_id,
    }
