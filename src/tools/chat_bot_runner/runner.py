import json
from typing import cast, Any
from src import get_logger
from src.models.chat.chatstate import ChatState

logger = get_logger(__name__)


async def run_graph(user_input: str, user_id: str):
    from main import chat_graph

    state = cast(
        ChatState,
        {
            "user_input": user_input,
            "response": "",
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

            else:
                continue
    except Exception as e:
        logger.error(f"Error running graph: {e}")
        raise e
