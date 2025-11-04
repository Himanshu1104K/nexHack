from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command
import json


async def response_node(state: ChatState):
    """
    Response node for the chat bot.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        streaming=True,
    )

    system_prompt = """
    You are Vellora, a placement assistant coach and a personal helping assistant.
    """

    inputs = {
        "query": state["query"],
    }
    if state["search_results"] is not None:
        system_prompt += """
        This are the search results for the user's query: {search_results}
        Use this information to answer the user's query.
        If the user's query is not related to the search results, say that you are not sure about the answer.
        """
        inputs["search_results"] = state["search_results"]

    if state["yt_scraped_data"] is not None:
        system_prompt += """
        This is the context of the lecture that the user is interested in: {yt_scraped_data}
        Use this information to answer the user's query.
        If the user's query is not related to the lecture, say that you are not sure about the answer.
        """
        inputs["yt_scraped_data"] = state["yt_scraped_data"]

    if state["course_data"] is not None:
        system_prompt += """
        This is the course data for the user's query: {course_data}
        Use this information to answer the user's query.
        If the user's query is not related to the course, say that you are not sure about the answer.
        """
        inputs["course_data"] = state["course_data"]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{query}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke(
        inputs,
    )
    state["response"] = response
    return Command(goto=END, update=state)
