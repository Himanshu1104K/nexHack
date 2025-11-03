from typing import Annotated, Optional, TypedDict


class ChatState(TypedDict):
    user_input: str = Annotated[str, "User input"]
    response: str = Annotated[str, "Response"]
    error: str = Annotated[Optional[str], "Error"]
