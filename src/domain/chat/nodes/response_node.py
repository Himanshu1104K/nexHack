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
        model="gpt-4o-mini",
        temperature=0.7,
        streaming=True,
    )

    # Build context sections based on available data
    context_parts = []

    if state.get("yt_scraped_data") and state["yt_scraped_data"] not in [None, {}]:
        context_parts.append(
            "## YouTube Scraped Data\n" + json.dumps(state["yt_scraped_data"], indent=2)
        )

    if state.get("search_results") and state["search_results"] not in [None, []]:
        context_parts.append(
            "## Search Results\n" + json.dumps(state["search_results"], indent=2)
        )

    context_section = (
        "\n\n".join(context_parts)
        if context_parts
        else "No additional context provided."
    )

    system_prompt = """You are a helpful assistant that provides responses based on the given query and available context data.
        Your response should be formatted in markdown.
        Use the provided context data (YouTube scraped data and/or search results) to enhance your answer when available.
        If context data is provided, reference it appropriately in your response.
        Format your response using markdown syntax for better readability.
    """

    user_prompt = """Query: {query}

            {context}

            Please provide a comprehensive response to the query based on the information above. Format your response in markdown."""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke(
        {
            "query": state["query"],
            "context": context_section,
        }
    )
    state["response"] = response
    return Command(goto=END, update=state)
