from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from src.model.chat.state import ChatState
from langgraph.types import Command
from langchain_openai import ChatOpenAI


async def teacher_node(state: ChatState):
    """
    Teacher node for the chat bot.
    """

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0.1,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an assistant that analyzes user queries to determine if they require calendar-related actions.
Calendar actions include:
- Scheduling meetings, classes, or events
Analyze the query and respond with a JSON object containing a boolean field 'need_calendar_action'.
Set it to true if the query requires calendar action, false otherwise.
                """,
            ),
            ("user", "Query: {query}"),
        ]
    )
    chain = prompt | llm | JsonOutputParser()

    response = await chain.ainvoke({"query": state["query"]})

    if response.get("need_calendar_action"):
        return Command(goto="calendar_node", update=state)
    else:
        return Command(goto="response_node", update=state)
