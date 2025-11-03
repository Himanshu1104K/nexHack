from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from src.models.chat.chatstate import ChatState
from langgraph.graph import END
from langgraph.types import Command


async def response(state: ChatState):
    """
    Response node for the chat bot.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        streaming=True,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that can answer questions and help with tasks.",
            ),
            ("user", "User: {user_input}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke(
        {"user_input": state.user_input},
    )
    state.response = response
    return Command(goto=END, update=state)
