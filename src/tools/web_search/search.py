"""Web search tool for course planning and research."""

import os
from typing import Optional
import httpx


async def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Perform web search using DuckDuckGo API (free, no key required).
    Falls back to a simple implementation if external API unavailable.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of search results with title, url, and snippet
    """
    try:
        # Try using DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []

            # Get Abstract if available
            if data.get("Abstract"):
                results.append(
                    {
                        "title": data.get("Heading", query),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data.get("Abstract", ""),
                    }
                )

            # Get Related Topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(
                        {
                            "title": topic.get("Text", "").split(" - ")[0],
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                        }
                    )

            # Filter out empty results
            results = [r for r in results if r["snippet"]]

            return results[:max_results]

    except Exception as e:
        # Fallback: return empty list or mock data
        from src import get_logger

        logger = get_logger(__name__)
        logger.warning(f"Web search failed: {e}. Returning empty results.")
        return []


async def search_youtube_videos(query: str, max_results: int = 3) -> list[dict]:
    """
    Search for YouTube videos related to the query.
    Returns video URLs and metadata.

    Args:
        query: Search query
        max_results: Max videos to return

    Returns:
        List of video data with url, title, description
    """
    try:
        # Use YouTube Data API or yt-dlp search
        search_query = f"ytsearch{max_results}:{query}"

        import yt_dlp

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)

            if not result or "entries" not in result:
                return []

            videos = []
            for entry in result["entries"][:max_results]:
                if entry:
                    videos.append(
                        {
                            "title": entry.get("title", "Unknown"),
                            "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            "description": entry.get("description", "")[
                                :200
                            ],  # Truncate
                            "duration": entry.get("duration", 0),
                        }
                    )

            return videos

    except Exception as e:
        from src import get_logger

        logger = get_logger(__name__)
        logger.warning(f"YouTube search failed: {e}")
        return []


__all__ = ["web_search", "search_youtube_videos"]
