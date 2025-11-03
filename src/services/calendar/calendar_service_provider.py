def get_calendar_service():
    """Get the calendar service."""
    return build("calendar", "v3", credentials=credentials)
