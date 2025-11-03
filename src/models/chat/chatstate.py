from typing import Annotated, TypedDict


class ChatState(TypedDict):
    user_input: str = Annotated[str, "User input"]
    response: str = Annotated[str, "Response"]
