from langgraph.graph import StateGraph, START, END
from src.domain.chat_bot.nodes.response_node import response
from src.models.chat.chatstate import ChatState


async def get_chat_graph():
    graph = StateGraph(ChatState)

    graph.add_node("response_node", response)

    graph.add_edge(START, "response_node")

    return graph
