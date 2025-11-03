from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.core.utility.logging_utils import get_logger
from src.tools.chat_bot_runner.runner import run_graph

logger = get_logger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat")
async def chat(user_input: str, user_id: str):
    """Chat with the chat bot"""
    try:
        return StreamingResponse(
            run_graph(
                user_id=user_id,
                user_input=user_input,
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
