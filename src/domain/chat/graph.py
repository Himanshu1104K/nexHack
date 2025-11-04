from langgraph.graph import StateGraph, START
from src.model.chat.state import ChatState
from src.domain.chat.nodes import *


async def get_chat_graph():
    graph = StateGraph(ChatState)

    def start_router(state: ChatState) -> str:
        """
        Route the workflow to the response node.
        """
        if state["user_type"] == "user":
            return "user_node"
        else:
            return "teacher_node"

    graph.add_node("user_node", user_node)
    graph.add_node("teacher_node", teacher_node)
    graph.add_node("scheduler_node", scheduler_node)
    graph.add_node("course_scrapper_node", course_scrapper_node)
    graph.add_node("calendar_node", calendar_node)
    graph.add_node("response_node", response_node)
    graph.add_node("quiz_node", quiz_node)
    graph.add_node("course_planner_node", course_planner_node)

    graph.add_conditional_edges(
        START,
        start_router,
        {
            "user_node": "user_node",
            "teacher_node": "teacher_node",
        },
    )
    compiled_graph = graph.compile()

    return compiled_graph
