from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.types import Command
from src.model.chat.state import ChatState
from src.core.utility.logging_utils import get_logger
from langgraph.graph import END

logger = get_logger(__name__)


async def quiz_node(state: ChatState) -> Command:
    """Quiz node for the chat bot."""
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        streaming=True,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant that can generate a quiz for a given topic.
                The quiz should be in the following format:
                {{
                    "questions": [
                        {{
                            "question": "The question",
                            "options": ["The options"],
                            "answer": "The answer",
                        }}
                    ]
                }}
                """,
            ),
            (
                "user",
                """
                Query: {query}
                Course data: {course_data}
                """,
            ),
        ]
    )
    chain = prompt | llm | JsonOutputParser()
    response = await chain.ainvoke(
        {
            "query": state["query"],
            "course_data": state["course_data"],
        }
    )

    return Command(goto=END, update=state)
