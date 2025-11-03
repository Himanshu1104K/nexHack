from langchain.agents import AgentExecutor, create_tool_calling_agent
import pytz
from datetime import datetime
from src.domain.chat.tools import (
    create_scheduled_action_tools,
)

from src.model.chat.state import ChatState
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from src.core.utility.logging_utils import get_logger
from langchain_core.prompts import ChatPromptTemplate

logger = get_logger(__name__)


SCHEDULED_ACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
ROLE:
You are **Scheduler Agent**, specialized in helping users manage reminders and scheduled actions. You have access to exactly two tools:

1. create_scheduled_action_tool
   • Purpose: Create a new scheduled action/reminder.
   • Required parameters:
     - title (str)
     - description (str)
     - timestamp (str) — ISO 8601 with timezone for one-time events or HH:MM for recurring events.
     - Optional: days_of_week (list[str]) — ONLY for recurring events on specific days.
     - user_id (str)
   • Returns: true on success, false on failure.

2. delete_scheduled_action_tool
   • Purpose: Delete an existing scheduled action.
   • Required parameters:
     - action_id (str)
     - user_id (str)
   • Returns: true on success, false on failure.

IMPORTANT RULES:
• Use **create_scheduled_action_tool** only when the user explicitly asks to add/schedule/remind something.
• Use **delete_scheduled_action_tool** only when the user explicitly wants to cancel / delete a reminder.
• For one-time schedules: DO NOT include days_of_week.
• For recurring schedules:
  – If the user wants all 7 days, DO NOT include days_of_week (time alone is enough).
  – If the user specifies particular days, INCLUDE days_of_week with full English day names, e.g. ["Monday", "Wednesday"].
• Always validate timestamps and day names before calling a tool. If validation fails, reply in natural language explaining the problem — DO NOT call a tool.

OUTPUT FORMAT:
If a tool call is required respond with **only** a JSON object in the form:
{{
  "tool": "<tool_name>",
  "arguments": {{ /* parameters */ }}
}}
Otherwise respond with helpful natural-language feedback.
""",
        ),
        (
            "user",
            """
User ID: {user_id}
Current Time: {current_time}
Query: {query}
""",
        ),
        ("assistant", "{agent_scratchpad}"),
    ]
)


async def scheduler_node(state: ChatState) -> Command:
    """Enhanced Scheduled action node with proper error handling."""

    try:
        tools = create_scheduled_action_tools()

        # 3. Initialize LLM
        llm = ChatOpenAI(model="gpt-4o", streaming=False, temperature=0)

        # 5. Create and execute agent
        agent = create_tool_calling_agent(llm, tools, SCHEDULED_ACTION_PROMPT)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            early_stopping_method="force",
            handle_parsing_errors=True,
            max_execution_time=60,
        )

        try:
            user_tz = pytz.timezone(state.get("timezone", "UTC"))
            utc_dt = datetime.fromisoformat(
                state.get("timestamp").replace("Z", "+00:00")
            )
            local_dt = utc_dt.astimezone(user_tz)
            current_timestamp_local = local_dt.isoformat()
        except Exception:
            current_timestamp_local = ""

        inputs = {
            "query": state["query"],
            "user_id": state.get("user_id", ""),
            "current_time": current_timestamp_local,
        }

        try:
            result = await executor.ainvoke(inputs)
        except Exception as exec_error:
            logger.error(f"Scheduled action node execution failed: {exec_error}")
            state["scheduled_action_result"] = {
                "status": "error",
                "output": f"Scheduled action node operation failed: {str(exec_error)}",
                "intermediate_steps": [],
            }
            return Command(goto="response_generator", update=state)

        # 6. Enhanced result processing
        if result.get("output"):
            state["scheduled_action_result"] = {
                "status": "success",
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
            }
        else:
            state["scheduled_action_result"] = {
                "status": "partial",
                "output": "Scheduled action node operation completed but no specific output generated.",
                "intermediate_steps": result.get("intermediate_steps", []),
            }

        return Command(goto="response_generator", update=state)

    except Exception as e:
        logger.error(
            f"Scheduled action node error: {str(e)}",
            extra={
                "user_id": state.get("user_id"),
                "query": state.get("query"),
                "error_type": type(e).__name__,
            },
        )

        state["error"] = f"Scheduled action node operation failed: {str(e)}"
        return Command(goto="response_generator", update=state)
