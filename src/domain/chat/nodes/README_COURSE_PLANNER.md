# Course Planner Node

## Overview
The course planner node creates comprehensive study plans by combining web search results and YouTube educational content. It's automatically triggered when users ask about learning new topics or creating study plans.

## Features

### 1. **Dual Source Research**
- **Web Search**: Searches for articles, tutorials, and learning resources
- **YouTube Videos**: Finds relevant educational videos with transcripts

### 2. **AI-Powered Study Plan Generation**
The node uses GPT-4o to create structured study plans with:
- **Learning Path**: Phased approach (Beginner → Intermediate → Advanced)
- **Duration Estimates**: Time required for each phase
- **Key Topics & Concepts**: Organized learning objectives
- **Recommended Resources**: Curated articles and videos
- **Practice Suggestions**: Hands-on exercises and projects
- **Learning Tips**: Study strategies and best practices

## Usage

### Trigger Examples
Users can trigger the course planner by asking:
- "Create a study plan for Python"
- "I want to learn machine learning"
- "Plan a course for web development"
- "Help me learn data structures"

The `user_node` automatically classifies the intent and routes to `course_planner_node`.

## Architecture

### Flow
```
User Query
    ↓
user_node (intent classification)
    ↓
course_planner_node
    ↓ (performs)
    ├── Topic Extraction
    ├── Web Search (DuckDuckGo API)
    ├── YouTube Video Search (yt-dlp)
    ├── Transcript Fetching (top video)
    └── Study Plan Generation (GPT-4o)
    ↓
response_node (formats and delivers plan)
```

### State Updates
The node updates these `ChatState` fields:
- `course_data`: Complete study plan structure
- `search_results`: Web search results
- `yt_scraped_data`: YouTube videos and transcript

## Components

### Web Search Tool (`src/tools/web_search/search.py`)
- **Function**: `web_search(query, max_results=5)`
- **API**: DuckDuckGo Instant Answer API (no key required)
- **Returns**: List of search results with title, URL, and snippet

### YouTube Search Tool
- **Function**: `search_youtube_videos(query, max_results=3)`
- **Backend**: yt-dlp search functionality
- **Returns**: Video metadata including title, URL, description, duration

### Transcript Fetcher
- **Function**: `get_transcript(video_url)`
- **Backend**: yt-dlp caption downloader
- **Returns**: Full video transcript (limited to 3000 chars for context)

## Configuration

### Dependencies
```python
# requirements.txt additions
httpx==0.27.2  # For web search
yt-dlp==2025.10.22  # For YouTube operations
```

### Models Used
- **Topic Extraction**: GPT-4o (low temperature for accuracy)
- **Study Plan Generation**: GPT-4o (temp=0.3 for creativity + structure)

## Error Handling
- Graceful fallbacks if web search fails
- Continues with available data if YouTube search fails
- Transcript fetching is optional (plan generated even if unavailable)
- All errors are logged for debugging

## Example Output Structure

```json
{
  "study_plan": {
    "topic": "Python Programming",
    "overview": "Comprehensive Python learning path from basics to advanced concepts",
    "learning_path": [
      {
        "phase": "Beginner",
        "duration": "2 weeks",
        "topics": ["Variables", "Data Types", "Control Flow"],
        "key_concepts": ["Syntax", "Basic Operations", "Conditionals"]
      }
    ],
    "recommended_resources": {
      "articles": ["Python.org Tutorial", "Real Python Basics"],
      "videos": ["Python Crash Course - YouTube"]
    },
    "practice_suggestions": [
      "Build a calculator",
      "Create a to-do list app"
    ],
    "learning_tips": [
      "Practice daily for 1 hour",
      "Build projects alongside learning"
    ]
  }
}
```

## Future Enhancements
- Add Tavily API integration for better search results
- Support for multiple video transcript analysis
- Interactive quiz generation from study plans
- Progress tracking and personalized recommendations

