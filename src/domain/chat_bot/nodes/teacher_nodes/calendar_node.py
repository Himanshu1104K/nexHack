from datetime import datetime
import pytz
from src.domain.chat_bot.tools.calendar_tools import create_calendar_tools
from src.models.chat.chatstate import ChatState
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.utility.logging_utils import get_logger
from src.services.calendar.calendar_service_provider import get_calendar_service
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.services.qdrant.users import get_emails

logger = get_logger(__name__)


async def calendar_node(state: ChatState) -> Command:
    """Calendar Node"""
    try:
        service = await get_calendar_service(state)
        if not service:
            state.error = "Failed to get calendar service"
            return Command(goto="response_node", update=state)

        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            streaming=True,
        )
        tools = create_calendar_tools(service)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that creates calendar events. Your task is to:

1. Parse the user's query to extract:
   - Event title/summary
   - Start time and end time (relative to current_timestamp if needed)
   - Event description
   - Location (if mentioned)
   - Whether to add Google Meet (if requested)

2. Use the current_timestamp and user_timezone to accurately calculate event times.

3. Add the provided attendee emails to the event.

4. Call the create_calendar_event_tool with the structured event data.

IMPORTANT:
- Times must be in ISO 8601 format (e.g., "2024-01-15T14:30:00" or "2024-01-15T14:30:00+05:30")
- If user mentions "tomorrow", "next week", etc., calculate the actual date based on current_timestamp
- If time is mentioned without date, assume it's for today unless context suggests otherwise
- Always use the timezone provided (user_timezone) when creating events
- Include all attendee emails in the attendees list
- Set conferenceData=True if user wants a video meeting/Google Meet link

Tool signature:
create_calendar_event_tool(event_details: {{
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: list[str] = [],
    timezone: str = "UTC",
    conferenceData: bool = False
}}) -> dict
""",
                ),
                (
                    "user",
                    """User Query: {user_query}

Current Timestamp (in user's local timezone): {current_timestamp}
User Timezone: {user_timezone}
Attendee Emails: {mails}

Extract event details from the user query and create the calendar event.""",
                ),
            ]
        )
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=4,
            early_stopping_method="force",
            handle_parsing_errors=True,
            max_execution_time=60,
            return_intermediate_steps=True,
        )
        mails = get_mails(state)
        inputs = {
            "user_query": state["user_input"],
            "current_timestamp": state.get(
                "current_timestamp", datetime.utcnow().isoformat()
            ),
            "user_timezone": state.get("timezone", "UTC"),
            "mails": mails if mails else [],
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
            return Command(goto="response_generator", update=state)

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

        return Command(goto="response_generator", update=state)

    except Exception as e:
        logger.error(f"Error in calendar node: {e}")
        state.error = f"Error in calendar node: {e}"
        return Command(goto="response_node", update=state)
