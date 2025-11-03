from src.models.chat.chatstate import ChatState


def get_emails(state: ChatState) -> list[str]:
    """Get emails from the state."""
    return state.get("mails", [])
