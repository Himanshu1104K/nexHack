from typing import Annotated, Literal, Optional, TypedDict


class ChatState(TypedDict):
    user_id: str = Annotated[str, "User ID"]
    query: str = Annotated[str, "Query"]
    response: str = Annotated[str, "Response"]
    user_type: Literal["user", "teacher"] = Annotated[
        Literal["user", "teacher"], "User type"
    ]
    lecture_id: Optional[str] = Annotated[Optional[str], "Lecture ID"]
    yt_scraped_data: Optional[dict] = Annotated[Optional[dict], "YouTube scraped data"]
    search_results: Optional[list[dict]] = Annotated[
        Optional[list[dict]], "Search results"
    ]
    course_data: Optional[dict] = Annotated[Optional[dict], "Course data"]
    need_quiz: Optional[bool] = Annotated[Optional[bool], "Need quiz"]
