from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command
from langchain_openai import ChatOpenAI


async def course_scrapper_node(state: ChatState):
    """
    Calendar node for the chat bot.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        streaming=True,
    )

    
    return Command(goto="quiz_node", update=state)
