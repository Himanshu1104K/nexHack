from langgraph.types import Command
from src.models.desc_agent.descstate import DESCSTATE
from src.domain.desc_agent.tool.get_yt_desc import get_yt_description


async def yt_extracter(state: DESCSTATE):
    """
    YT extracter node for the chat bot.
    """

    state.yt_desc = await get_yt_description(state.yt_link)

    return Command(goto="desc_gen_node", update=state)
