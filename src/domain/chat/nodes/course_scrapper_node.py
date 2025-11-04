from langchain_core.output_parsers import JsonOutputParser
from src.model.chat.state import ChatState
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.services.qdrant.course import get_youtube_url
from src.tools.youtube_transcriber.transcriber import get_transcript


async def course_scrapper_node(state: ChatState):
    """
    Calendar node for the chat bot.
    """
    llm = ChatOpenAI(
        model="gpt-5-nano",
        streaming=False,
    )

    if state["lecture_id"]:
        youtube_url = await get_youtube_url(state["lecture_id"])
    elif state["video_url"]:
        youtube_url = state["video_url"]
    else:
        return Command(goto="response_node", update=state)

    youtube_video_context = await get_transcript(youtube_url)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a context retrieval assistant that can retrieve the context of a given lecture based on the youtube url and user query. You will be returning a json Object with the following fields: 
                {{
                    "context": "The context of the lecture",
                    "need_quiz": "True if the user wants to take a quiz on the lecture, False otherwise"
                }}
                """,
            ),
            (
                "user",
                "Youtube Video Context : {youtube_video_context}\nUser Query: {query}",
            ),
        ]
    )
    chain = prompt | llm | JsonOutputParser()
    context = await chain.ainvoke(
        {
            "youtube_video_context": youtube_video_context,
            "query": state["query"],
        }
    )

    state["yt_scraped_data"] = context.get("context")
    state["need_quiz"] = context.get("need_quiz")

    if state["need_quiz"]:
        return Command(goto="quiz_node", update=state)
    else:
        return Command(goto="response_node", update=state)
