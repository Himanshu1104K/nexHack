# from src.domain.chat.tools.scheduled_action_tools import (
#     cancel_scheduled_action_endpoint,
#     add_scheduled_actions,
# )
# from langchain_core.tools import tool
# from pydantic import BaseModel, Field
# from typing import List, Optional


# # ---------- Pydantic input models ----------


# class ScheduledActionInput(BaseModel):
#     title: Optional[str] = Field(None, description="Action title")
#     description: Optional[str] = Field(None, description="Action description")
#     timestamp: Optional[str] = Field(
#         None,
#         description="Scheduled time in HH:MM format for daily recurring or ISO format with timezone for one-time scheduling",
#     )
#     days_of_week: Optional[List[str]] = Field(
#         None,
#         description="List of days of the week (e.g., ['Monday', 'Tuesday', 'Wednesday']) for recurring scheduling",
#     )
#     user_id: str = Field(..., description="Unique identifier of the user")


# class ActionIDInput(BaseModel):
#     action_id: str = Field(..., description="Unique identifier of the scheduled action")
#     user_id: str = Field(..., description="Unique identifier of the user")


# class UserIDInput(BaseModel):
#     user_id: str = Field(..., description="Unique identifier of the user")


# class UpdateActionInput(ScheduledActionInput):
#     action_id: str = Field(
#         ..., description="Unique identifier of the scheduled action to update"
#     )


# # ---------- Wrapper factory ----------


# def create_scheduled_action_tools():
#     """Return LangChain tools for scheduled action operations."""

#     @tool(
#         args_schema=ActionIDInput,
#         description="Cancel a scheduled action and remove it from user's database permanently.",
#     )
#     async def delete_scheduled_action_tool(**kwargs) -> bool:
#         action_id = kwargs["action_id"]
#         user_id = kwargs["user_id"]

#         return await cancel_scheduled_action_endpoint(action_id, user_id)

#     @tool(
#         args_schema=ScheduledActionInput,
#         description="Add a new scheduled action for a user with auto-generated ID. Supports daily recurring (with days_of_week) or one-time scheduling.",
#     )
#     async def create_scheduled_action_tool(**kwargs) -> bool:

#         user_id = kwargs.pop("user_id")

#         request = ScheduledActionInput(**kwargs)
#         return await add_scheduled_actions(request, user_id)

#     return [
#         delete_scheduled_action_tool,
#         create_scheduled_action_tool,
#     ]
