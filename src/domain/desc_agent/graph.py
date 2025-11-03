from langgraph.graph import StateGraph, START
from src.models.desc_agent.descstate import DESCSTATE
from src.domain.desc_agent.nodes import yt_extracter, desc_gen_node


async def get_desc_graph():
    """
    Description agent graph for the chat bot.
    """

    graph = StateGraph(DESCSTATE)

    graph.add_node("yt_extracter", yt_extracter.yt_extracter)
    graph.add_node("desc_gen_node", desc_gen_node.desc_gen_node)

    graph.add_edge(START, "yt_extracter")

    return graph
