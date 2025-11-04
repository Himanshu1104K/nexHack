from src.model.chat.state import ChatState
from langgraph.graph import END
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.tools.web_search import web_search, search_youtube_videos
from src.tools.youtube_transcriber.transcriber import get_transcript
from src.core.utility.logging_utils import get_logger

logger = get_logger(__name__)


async def course_planner_node(state: ChatState):
    """
    Course planner node that creates a comprehensive study plan.
    Uses web search and YouTube resources to gather information.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        streaming=False,
    )

    query = state["query"]

    # Step 1: Extract topic and search intent
    topic_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract the main topic/subject the user wants to learn about. Return only the topic name.",
            ),
            ("user", "{query}"),
        ]
    )
    topic_chain = topic_prompt | llm
    topic_response = await topic_chain.ainvoke({"query": query})
    topic = topic_response.content.strip()

    logger.info(f"Extracted topic: {topic}")

    # Step 2: Perform web search for course resources
    try:
        search_results = await web_search(
            f"{topic} tutorial course learning resources", max_results=5
        )
        logger.info(f"Found {len(search_results)} web search results")
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        search_results = []

    # Step 3: Search for YouTube videos
    try:
        youtube_results = await search_youtube_videos(
            f"{topic} tutorial course", max_results=3
        )
        logger.info(f"Found {len(youtube_results)} YouTube videos")
    except Exception as e:
        logger.error(f"YouTube search failed: {e}")
        youtube_results = []

    # Step 4: Optionally fetch transcript from top video
    video_context = None
    if youtube_results and len(youtube_results) > 0:
        try:
            top_video_url = youtube_results[0]["url"]
            logger.info(f"Fetching transcript from: {top_video_url}")
            video_context = await get_transcript(top_video_url)
            # Limit context length
            if video_context and len(video_context) > 3000:
                video_context = video_context[:3000] + "..."
        except Exception as e:
            logger.warning(f"Could not fetch video transcript: {e}")
            video_context = None

    # Step 5: Generate comprehensive study plan
    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert course planner and educational advisor.
        Create a comprehensive, structured study plan based on available resources.
        
        Return a JSON object with the following structure:
        {{
            "study_plan": {{
                "topic": "Main topic name",
                "overview": "Brief overview of what will be learned",
                "learning_path": [
                    {{
                        "phase": "Phase name (e.g., Beginner, Intermediate, Advanced)",
                        "duration": "Estimated time (e.g., 2 weeks)",
                        "topics": ["Topic 1", "Topic 2", ...],
                        "key_concepts": ["Concept 1", "Concept 2", ...]
                    }}
                ],
                "recommended_resources": {{
                    "articles": ["Resource 1", "Resource 2"],
                    "videos": ["Video 1", "Video 2"]
                }},
                "practice_suggestions": ["Suggestion 1", "Suggestion 2"],
                "learning_tips": ["Tip 1", "Tip 2"]
            }}
        }}
        """,
            ),
            (
                "user",
                """Create a study plan for: {topic}
        
        User Query: {query}
        
        Available Web Resources:
        {web_resources}
        
        Available YouTube Videos:
        {youtube_videos}
        
        {video_context_section}
        
        Create a detailed, actionable study plan that incorporates these resources.
        """,
            ),
        ]
    )

    # Format resources
    web_resources_text = (
        "\n".join(
            [
                f"- {r['title']}: {r['snippet'][:150]}... ({r['url']})"
                for r in search_results
            ]
        )
        if search_results
        else "No web resources found."
    )

    youtube_videos_text = (
        "\n".join(
            [
                f"- {v['title']} ({v['url']}) - Duration: {v.get('duration', 'Unknown')}s"
                for v in youtube_results
            ]
        )
        if youtube_results
        else "No YouTube videos found."
    )

    video_context_section = ""
    if video_context:
        video_context_section = f"Sample Video Content (from {youtube_results[0]['title']}):\n{video_context}"

    # Generate study plan
    planner_chain = planner_prompt | llm | JsonOutputParser()

    try:
        course_data = await planner_chain.ainvoke(
            {
                "topic": topic,
                "query": query,
                "web_resources": web_resources_text,
                "youtube_videos": youtube_videos_text,
                "video_context_section": video_context_section,
            }
        )

        # Store all relevant data in state
        state["course_data"] = course_data
        state["search_results"] = search_results
        state["yt_scraped_data"] = {
            "videos": youtube_results,
            "transcript": video_context,
        }

        logger.info("Course plan generated successfully")

    except Exception as e:
        logger.error(f"Failed to generate course plan: {e}")
        state["course_data"] = {
            "error": "Failed to generate study plan",
            "topic": topic,
            "resources": {"web": search_results, "videos": youtube_results},
        }

    return Command(goto="response_node", update=state)
