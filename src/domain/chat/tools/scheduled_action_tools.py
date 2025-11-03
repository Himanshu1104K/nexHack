# import uuid
# from src.core.utility.scheduled_action_utils import (
#     cancel_scheduled_action,
#     schedule_action,
#     get_all_scheduled_actions,
# )

# # Schemas
# from src.model.chat.scheduled_actions_models import (
#     UpdateActionRequest,
# )
# from src.core.utility.logging_utils import get_logger

# logger = get_logger(__name__)


# async def update_scheduled_actions(
#     action_id: str,
#     request: UpdateActionRequest,
#     user_id: str,
# ) -> bool:
#     """
#     Update or create a scheduled action for a user.

#     Args:
#         action_id (str): Unique identifier for the scheduled action
#         request (UpdateActionRequest): Request containing action details
#         user_id (str): Unique identifier of the user

#     Returns:
#         bool: True if successful, False otherwise
#     """
#     from main import db_user

#     try:
#         # Get user document
#         user_doc_ref = db_user.document(user_id)
#         user_doc = user_doc_ref.get()

#         if not user_doc.exists:
#             return False

#         data = user_doc.to_dict()
#         scheduled_actions = data.get("scheduledActions", [])

#         # Find action by action_id
#         action_index = None
#         for i, action in enumerate(scheduled_actions):
#             if action.get("action_id") == action_id:
#                 action_index = i
#                 break

#         if action_index is not None:
#             # Update existing action
#             existing_action = scheduled_actions[action_index]
#             updated_action = {
#                 "title": (
#                     request.title
#                     if request.title is not None
#                     else existing_action.get("title", "")
#                 ),
#                 "description": (
#                     request.description
#                     if request.description is not None
#                     else existing_action.get("description", "")
#                 ),
#                 "timestamp": (
#                     request.timestamp
#                     if request.timestamp is not None
#                     else existing_action.get("timestamp", "")
#                 ),
#                 "days_of_week": (
#                     request.days_of_week
#                     if request.days_of_week is not None
#                     else existing_action.get("days_of_week", [])
#                 ),
#                 "action_id": action_id,
#             }
#             scheduled_actions[action_index] = updated_action

#             # Cancel existing scheduled job if timestamp changed
#             if (
#                 request.timestamp is not None
#                 and request.timestamp != existing_action.get("timestamp", "")
#             ):
#                 cancel_scheduled_action(user_id, action_id)
#         else:
#             # Create new action if it doesn't exist
#             new_action = {
#                 "title": request.title or "",
#                 "description": request.description or "",
#                 "timestamp": request.timestamp or "",
#                 "days_of_week": request.days_of_week or [],
#                 "action_id": action_id,
#             }
#             scheduled_actions.append(new_action)
#             updated_action = new_action

#         # Update the document
#         data["scheduledActions"] = scheduled_actions
#         user_doc_ref.update({"scheduledActions": scheduled_actions})

#         # Schedule the action if timestamp is provided
#         if updated_action.get("timestamp"):
#             user_timezone = data.get("timezone", "Asia/Kolkata")
#             days_of_week = updated_action.get("days_of_week", [])
#             schedule_success = await schedule_action(
#                 user_id,
#                 action_id,
#                 updated_action["timestamp"],
#                 user_timezone,
#                 days_of_week,
#             )
#             if not schedule_success:
#                 logger.warning(
#                     f"Failed to schedule action {action_id} for user {user_id}"
#                 )
#         return True

#     except Exception as e:
#         logger.error(f"Error updating scheduled action: {e}")
#         return False


# async def cancel_scheduled_action_endpoint(
#     action_id: str,
#     user_id: str,
# ) -> bool:
#     """
#     Cancel a scheduled action and remove it from user's database.

#     Args:
#         action_id (str): Unique identifier of the scheduled action to cancel
#         user_id (str): Unique identifier of the user

#     Returns:
#         bool: True if successful, False otherwise
#     """
#     from main import db_user

#     try:
#         # Get user document
#         user_doc_ref = db_user.document(user_id)
#         user_doc = user_doc_ref.get()

#         if not user_doc.exists:
#             return False

#         data = user_doc.to_dict()
#         scheduled_actions = data.get("scheduledActions", [])

#         # Find and remove the action from the array
#         action_found = False
#         updated_actions = []
#         for action in scheduled_actions:
#             if action.get("action_id") == action_id:
#                 action_found = True
#             else:
#                 updated_actions.append(action)

#         if not action_found:
#             return False

#         # Update the document with the filtered actions
#         data["scheduledActions"] = updated_actions
#         user_doc_ref.update({"scheduledActions": updated_actions})

#         return True

#     except Exception as e:
#         logger.error(f"Error cancelling scheduled action: {str(e)}")
#         return False


# async def get_scheduled_actions(
#     user_id: str,
# ) -> list:
#     """
#     Get all scheduled actions for a user.

#     Args:
#         user_id (str): Unique identifier of the user

#     Returns:
#         list: List of scheduled actions, empty list if none found or error
#     """
#     try:
#         actions = await get_all_scheduled_actions(user_id)
#         return actions
#     except Exception as e:
#         logger.error(f"Error getting all scheduled actions: {str(e)}")
#         return []


# async def add_scheduled_actions(
#     request: UpdateActionRequest,
#     user_id: str,
# ) -> bool:
#     """
#     Add a new scheduled action for a user with auto-generated ID.

#     Args:
#         request (UpdateActionRequest): Request containing action details
#         user_id (str): Unique identifier of the user

#     Returns:
#         bool: True if successful, False otherwise
#     """
#     return await update_scheduled_actions(
#         action_id=str(uuid.uuid4()),
#         request=request,
#         user_id=user_id,
#     )
