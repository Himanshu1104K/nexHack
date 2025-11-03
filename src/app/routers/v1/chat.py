from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.core.utility.logging_utils import get_logger
from src.tools.chat_runner.runner import run_graph
from src.services.auth.verify_token import verify_token

logger = get_logger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat")
async def chat(
    query: str,
    lecture_id: Optional[str] = None,
    token_data: dict = Depends(verify_token),
):
    """Chat with the chat bot"""
    user_id = token_data.get("sub")
    user_type = token_data.get("user_type")
    try:
        return StreamingResponse(
            run_graph(
                user_id=user_id,
                query=query,
                lecture_id=lecture_id,
                user_type=user_type,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Transfer-Encoding": "chunked",
            },
        )
    except Exception as e:
        logger.error(f"Error chatting: {e}")
        raise HTTPException(status_code=500, detail=f"Error chatting: {e}")
