import asyncio
from datetime import datetime
from googleapiclient.discovery import build
from langchain_core.tools import tool
import pytz
from typing import Dict

from src.core.utility.logging_utils import get_logger

logger = get_logger(__name__)


async def create_calendar_event(params: Dict, service: build) -> Dict:
    """Create a single calendar event."""
    try:
        event_details = params.get("event_details", {})

        tz_str = event_details.timezone if hasattr(event_details, "timezone") else "UTC"

        try:
            user_tz = pytz.timezone(tz_str)

            # Normalize start_time - treat input as local time
            start_dt_iso = event_details.start_time
            if (
                "T" in start_dt_iso
                and not start_dt_iso.endswith("Z")
                and "+" not in start_dt_iso
                and "-" not in start_dt_iso[-6:]
            ):
                # Input is local time without timezone info, treat as local
                start_dt = datetime.fromisoformat(start_dt_iso)
                start_local = user_tz.localize(start_dt).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                # Input has timezone info, parse and convert
                start_dt = datetime.fromisoformat(start_dt_iso.replace("Z", "+00:00"))
                start_local = start_dt.astimezone(user_tz).strftime("%Y-%m-%dT%H:%M:%S")

            # Normalize end_time - treat input as local time
            end_dt_iso = event_details.end_time
            if (
                "T" in end_dt_iso
                and not end_dt_iso.endswith("Z")
                and "+" not in end_dt_iso
                and "-" not in end_dt_iso[-6:]
            ):
                # Input is local time without timezone info, treat as local
                end_dt = datetime.fromisoformat(end_dt_iso)
                end_local = user_tz.localize(end_dt).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                # Input has timezone info, parse and convert
                end_dt = datetime.fromisoformat(end_dt_iso.replace("Z", "+00:00"))
                end_local = end_dt.astimezone(user_tz).strftime("%Y-%m-%dT%H:%M:%S")
        except Exception:
            # Fallback if time parsing fails
            start_local = event_details.start_time.replace("Z", "")
            end_local = event_details.end_time.replace("Z", "")

        # ─────────────  All-day vs date-time detection  ─────────────
        is_all_day = (
            "T" not in event_details.start_time and "T" not in event_details.end_time
        )

        if is_all_day:
            # Google API expects 'date' not 'dateTime' for all-day events
            event_body = {
                "summary": event_details.summary,
                "location": (
                    event_details.location if hasattr(event_details, "location") else ""
                ),
                "description": (
                    event_details.description
                    if hasattr(event_details, "description")
                    else ""
                ),
                "start": {"date": start_local.split("T")[0]},
                "end": {"date": end_local.split("T")[0]},
            }
        else:
            event_body = {
                "summary": event_details.summary,
                "location": (
                    event_details.location if hasattr(event_details, "location") else ""
                ),
                "description": (
                    event_details.description
                    if hasattr(event_details, "description")
                    else ""
                ),
                "start": {"dateTime": start_local, "timeZone": tz_str},
                "end": {"dateTime": end_local, "timeZone": tz_str},
            }

        # ─────────────  Add Google Meet Conference Data  ─────────────
        add_meet = (
            event_details.conferenceData
            if hasattr(event_details, "conferenceData")
            else False
        )

        if add_meet and not is_all_day:
            import time

            request_id = f"meet-{int(time.time() * 1000)}"

            event_body["conferenceData"] = {
                "createRequest": {
                    "requestId": request_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }

        logger.info(f"[DEBUG] Event payload: {event_body}")

        # Attendees
        attendees = []
        if hasattr(event_details, "attendees") and event_details.attendees:
            attendees = [{"email": e.strip()} for e in event_details.attendees if e]
        if attendees:
            event_body["attendees"] = attendees

        # Create the event
        # IMPORTANT: Add conferenceDataVersion=1 when creating Meet links
        insert_request = service.events().insert(
            calendarId="primary",
            body=event_body,
            conferenceDataVersion=1 if add_meet and not is_all_day else 0,
            sendUpdates="all" if attendees else "none",
        )
        new_event = await asyncio.to_thread(insert_request.execute)

        # Extract Google Meet link if available
        meet_link = None
        if (
            "conferenceData" in new_event
            and "entryPoints" in new_event["conferenceData"]
        ):
            for entry in new_event["conferenceData"]["entryPoints"]:
                if entry.get("entryPointType") == "video":
                    meet_link = entry.get("uri")
                    break

        result = {
            "status": "success",
            "event_id": new_event["id"],
            "event_link": new_event["htmlLink"],
            "summary": event_details.summary,
        }

        # Add meet link if available
        if meet_link:
            result["meet_link"] = meet_link

        return result

    except Exception as e:
        logger.exception("Calendar event creation failed.")
        return {
            "status": "error",
            "message": f"Failed to create calendar event: {str(e)}",
            "summary": getattr(params.get("event_details", {}), "summary", "N/A"),
        }


def create_calendar_tools(service):
    """Return LangChain tools pre‑bound to the Google service."""

    @tool
    async def create_calendar_event_tool(**kwargs) -> dict:
        return await create_calendar_event(kwargs, service)

    return [
        create_calendar_event_tool,
    ]
