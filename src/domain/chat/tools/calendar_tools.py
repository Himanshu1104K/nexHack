import asyncio
import time
from datetime import datetime
from googleapiclient.discovery import build
from langchain_core.tools import tool
import pytz
from typing import Dict

from src.core.utility.logging_utils import get_logger

logger = get_logger(__name__)


def _normalize_time(dt_iso: str, user_tz: pytz.BaseTzInfo) -> str:
    """Normalize datetime string to local timezone format."""
    if (
        "T" in dt_iso
        and not dt_iso.endswith("Z")
        and "+" not in dt_iso
        and "-" not in dt_iso[-6:]
    ):
        # Input is local time without timezone info, treat as local
        dt = datetime.fromisoformat(dt_iso)
        return user_tz.localize(dt).strftime("%Y-%m-%dT%H:%M:%S")
    else:
        # Input has timezone info, parse and convert
        dt = datetime.fromisoformat(dt_iso.replace("Z", "+00:00"))
        return dt.astimezone(user_tz).strftime("%Y-%m-%dT%H:%M:%S")


def _safe_getattr(obj, attr: str, default=None):
    """Safely get attribute from object."""
    return getattr(obj, attr, default) if hasattr(obj, attr) else default


async def create_calendar_event(params: Dict, service: build) -> Dict:
    """Create a single calendar event."""
    try:
        event_details = params.get("event_details", {})

        tz_str = _safe_getattr(event_details, "timezone", "UTC")

        try:
            user_tz = pytz.timezone(tz_str)
            start_local = _normalize_time(event_details.start_time, user_tz)
            end_local = _normalize_time(event_details.end_time, user_tz)
        except Exception:
            # Fallback if time parsing fails
            start_local = event_details.start_time.replace("Z", "")
            end_local = event_details.end_time.replace("Z", "")

        # All-day vs date-time detection
        is_all_day = (
            "T" not in event_details.start_time and "T" not in event_details.end_time
        )

        # Build common event body fields
        event_body = {
            "summary": event_details.summary,
            "location": _safe_getattr(event_details, "location", ""),
            "description": _safe_getattr(event_details, "description", ""),
        }

        # Add start/end times based on event type
        if is_all_day:
            event_body["start"] = {"date": start_local.split("T")[0]}
            event_body["end"] = {"date": end_local.split("T")[0]}
        else:
            event_body["start"] = {"dateTime": start_local, "timeZone": tz_str}
            event_body["end"] = {"dateTime": end_local, "timeZone": tz_str}

        # Add Google Meet Conference Data
        add_meet = _safe_getattr(event_details, "conferenceData", False)
        if add_meet and not is_all_day:
            request_id = f"meet-{int(time.time() * 1000)}"
            event_body["conferenceData"] = {
                "createRequest": {
                    "requestId": request_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }

        # Add attendees
        attendees = []
        if _safe_getattr(event_details, "attendees"):
            attendees = [{"email": e.strip()} for e in event_details.attendees if e]
            if attendees:
                event_body["attendees"] = attendees

        logger.info(f"[DEBUG] Event payload: {event_body}")

        # Create the event
        insert_request = service.events().insert(
            calendarId="primary",
            body=event_body,
            conferenceDataVersion=1 if add_meet and not is_all_day else 0,
            sendUpdates="all" if attendees else "none",
        )
        new_event = await asyncio.to_thread(insert_request.execute)

        # Extract Google Meet link if available
        meet_link = None
        conference_data = new_event.get("conferenceData", {})
        if conference_data.get("entryPoints"):
            for entry in conference_data["entryPoints"]:
                if entry.get("entryPointType") == "video":
                    meet_link = entry.get("uri")
                    break

        result = {
            "status": "success",
            "event_id": new_event["id"],
            "event_link": new_event["htmlLink"],
            "summary": event_details.summary,
        }

        if meet_link:
            result["meet_link"] = meet_link

        return result

    except Exception as e:
        logger.exception("Calendar event creation failed.")
        return {
            "status": "error",
            "message": f"Failed to create calendar event: {str(e)}",
            "summary": _safe_getattr(params.get("event_details", {}), "summary", "N/A"),
        }


def create_calendar_tools(service):
    """Return LangChain tools pre‑bound to the Google service."""

    @tool
    async def create_calendar_event_tool(**kwargs) -> dict:
        return await create_calendar_event(kwargs, service)

    return [
        create_calendar_event_tool,
    ]
