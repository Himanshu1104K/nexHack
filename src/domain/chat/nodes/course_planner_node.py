from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command


async def course_planner_node(state: ChatState):
    """
    Course planner node for the chat bot.
    """
    return Command(goto=END, update=state)
