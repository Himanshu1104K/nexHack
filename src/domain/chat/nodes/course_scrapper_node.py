from langchain_core.output_parsers import StrOutputParser
from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.services.qdrant.course import get_youtube_url


async def course_scrapper_node(state: ChatState):
    """
    Calendar node for the chat bot.
    """
    llm = ChatOpenAI(
        model="gpt-5-nano",
        streaming=False,
    )

    youtube_url = await get_youtube_url(state["lecture_id"])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that can extract the YouTube URL from the given text.",
            ),
            ("user", "Text: {text}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    context = await chain.ainvoke({"text": youtube_url})

    state["yt_scraped_data"] = context

    if state["need_quiz"]:
        return Command(goto="quiz_node", update=state)
    else:
        return Command(goto="response_node", update=state)
