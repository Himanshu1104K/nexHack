from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command


async def user_node(state: ChatState):
    """
    User node for the chat bot.
    """
    return Command(goto=END, update=state)
