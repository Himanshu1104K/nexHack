from langchain_openai import ChatOpenAI
from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


async def user_node(state: ChatState):
    """
    User node for the chat bot.
    """

    return Command(goto="response_node", update=state)

    
    if response.get("lecture_id"):
        return Command(goto="course_scrapper_node", update=state)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a user intent classifier that classifies the user's intent based on the query.
                The user's intent can be one of the following three literals:
                - "schedule": If the query is about scheduling a daily reminder or a one day reminder for a lecture or a course
                - "course_planner": If the query is about planning a course or a document for a study plan
                - "other": For any other query that doesn't fit the above categories
                
                Respond with a JSON object containing a field called "intent" with one of these three literal values: "schedule", "course_planner", or "other".
                """,
            ),
            ("user", "Query: {query}"),
        ]
    )
    chain = prompt | llm | JsonOutputParser()

    response = await chain.ainvoke({"query": state["query"]})

    value = response.get("intent")

    if value == "schedule":
        return Command(goto="scheduler_node", update=state)
    elif value == "course_planner":
        return Command(goto="course_planner_node", update=state)
    else:
        return Command(goto="response_node", update=state)
