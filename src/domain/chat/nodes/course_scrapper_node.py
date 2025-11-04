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
        model="gpt-4o",
        streaming=False,
    )

    if state["lecture_id"]:
        youtube_url = await get_youtube_url(state["lecture_id"])
    elif state["video_url"]:
        youtube_url = state["video_url"]
    else:
        return Command(goto="response_node", update=state)

    try:
        youtube_video_context = await get_transcript(
            "https://youtu.be/" + str(youtube_url)
        )
    except Exception as e:
        # Log and fallback to default flow without context
        from src import get_logger

        logger = get_logger(__name__)
        logger.error(f"Failed to fetch captions: {e}")

        state["yt_scraped_data"] = None
        # Continue without video context → normal response node
        return Command(goto="response_node", update=state)

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
                "Youtube Video Context : {youtube_video_context}\nUser Query: {query} # Give Priority to the User Query for the verification of the quiz.",
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
