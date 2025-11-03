from langgraph.types import Command
from src.models.desc_agent.descstate import DESCSTATE
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import END


async def desc_gen_node(state: DESCSTATE):
    """
    Description generation node for the chat bot.
    """

    llm = ChatOpenAI(
        model="gpt-5-mini",
        temperature=0.7,
        streaming=True,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant that can generate a description for a YouTube video.
                It should be in the following format:q
                {{
                    "title": "The title of the YouTube video in 10-20 words",
                    "description": "The description of the YouTube video",
                }}
                """,
            ),
            ("user", "YouTube description: {yt_desc}"),
        ]
    )
    chain = prompt | llm | JsonOutputParser()

    response = await chain.ainvoke(
        {"yt_desc": state.yt_desc},
    )
    state.yt_desc = response
    return Command(goto=END, state=state)
