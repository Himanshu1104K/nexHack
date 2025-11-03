from typing import Annotated, TypedDict


class DESCSTATE(TypedDict):
    yt_link: str = Annotated[str, "YouTube link"]
    yt_desc: str = Annotated[str, "YouTube description"]
