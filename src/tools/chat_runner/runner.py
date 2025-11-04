import json
from typing import cast, Any, Literal, Optional
from src import get_logger
from src.model.chat.state import ChatState

logger = get_logger(__name__)


async def run_graph(
    query: str,
    user_id: str,
    user_type: Literal["user", "teacher"],
    lecture_id: Optional[str] = None,
    video_url: Optional[str] = None,
):
    from main import chat_graph

    state = cast(
        ChatState,
        {
            "user_id": user_id,
            "query": query,
            "user_type": user_type,
            "lecture_id": lecture_id,
            "video_url": video_url,
            "yt_scraped_data": None,
            "search_results": None,
            "response": "",
            "need_quiz": False,
        },
    )

    config = {
        "thread_id": user_id,
    }

    try:
        events = chat_graph.astream_events(
            state, config=cast(Any, config), version="v2", stream_mode="updates"
        )
        async for event in events:
            event_type = event.get("event")
            if (
                event_type == "on_chat_model_stream"
                and event.get("metadata").get("langgraph_node") == "response_node"
            ):
                json_data = json.dumps(
                    {
                        "type": "response",
                        "content": f"{event.get('data').get('chunk').content}",
                    }
                )

                yield f"data: {json_data}\n\n"

            elif (
                event_type == "on_chat_model_stream"
                and event.get("metadata").get("langgraph_node") == "quiz_node"
            ):
                json_data = json.dumps(
                    {
                        "type": "quiz",
                        "content": f"{event.get('data').get('chunk').content}",
                    }
                )

                yield f"data: {json_data}\n\n"

            else:
                continue
    except Exception as e:
        logger.error(f"Error running graph: {e}")
        raise e
