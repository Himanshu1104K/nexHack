from langchain.agents import AgentExecutor, create_tool_calling_agent

# from src.domain.graph_tools.calendar_tools.get_calendar_tools import (
#     create_calendar_tools,
# )

from src.services.auth.get_calendar_service import get_calendar_service
from src.model.chat.state import ChatState
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from src.core.utility.logging_utils import get_logger
from datetime import datetime
import pytz

logger = get_logger(__name__)


async def calendar_node(state: ChatState) -> Command:
    """Enhanced Calendar Agent with proper error handling and service injection."""

    try:
        # 1. Get calendar service first
        service = await get_calendar_service(state)
        if not service:
            return Command(goto="get_cred_node", update=state)

        # 2. Create tools with injected service
        # tools = create_calendar_tools(service)

        # 3. Initialize LLM
        llm = ChatOpenAI(model="gpt-4o", streaming=False, temperature=0)

        try:
            user_tz = pytz.timezone(state.get("timezone", "UTC"))
            utc_dt = datetime.fromisoformat(
                state.get("timestamp").replace("Z", "+00:00")
            )
            local_dt = utc_dt.astimezone(user_tz)
            current_timestamp_local = local_dt.isoformat()
        except Exception:
            current_timestamp_local = ""

        # 5. Create and execute agent
        # agent = create_tool_calling_agent(llm, tools, CALENDAR_AGENT_PROMPT)
        agent = create_tool_calling_agent(llm, [], "")
        executor = AgentExecutor(
            agent=agent,
            # tools=tools,
            verbose=True,
            max_iterations=2,
            early_stopping_method="force",
            handle_parsing_errors=True,
            max_execution_time=60,
            return_intermediate_steps=True,
        )

        inputs = {
            "query": state["query"],
            "timezone": state.get("timezone", "UTC"),
            "current_timestamp": state.get("timestamp", datetime.utcnow().isoformat()),
            "current_timestamp_local": current_timestamp_local,
        }

        try:
            result = await executor.ainvoke(inputs)
        except Exception as exec_error:
            logger.error(f"Calendar agent execution failed: {exec_error}")
            state["calendar_result"] = {
                "status": "error",
                "output": f"Calendar operation failed: {str(exec_error)}",
                "intermediate_steps": [],
            }
            return Command(goto="response_node", update=state)

        # 6. Enhanced result processing
        if result.get("output"):
            state["calendar_result"] = {
                "status": "success",
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
            }
        else:
            state["calendar_result"] = {
                "status": "partial",
                "output": "Calendar operation completed but no specific output generated.",
                "intermediate_steps": result.get("intermediate_steps", []),
            }

        return Command(goto="response_node", update=state)

    except Exception as e:
        logger.error(
            f"Calendar agent error: {str(e)}",
            extra={
                "user_id": state.get("user_id"),
                "query": state.get("query"),
                "error_type": type(e).__name__,
            },
        )

        state["error"] = f"Calendar operation failed: {str(e)}"
        return Command(goto="response_node", update=state)
