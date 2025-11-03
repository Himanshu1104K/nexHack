from langgraph.types import Command
from src.models.desc_agent.descstate import DESCSTATE
from src.tools.youtube_transcriber.transcriber import *


async def yt_extracter(state: DESCSTATE):
    """
    YT extracter node for the chat bot.
    """

    state.yt_desc = await get_transcript(state.yt_link)

    return Command(goto="desc_gen_node", update=state)
