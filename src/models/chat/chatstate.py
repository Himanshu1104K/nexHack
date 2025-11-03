from typing import Annotated, Optional, TypedDict, Dict, List, Any


def get_last_value(old_value, new_value):
    """Get the last value"""
    return new_value


class ChatState(TypedDict):
    user_input: str
    response: str
