import os
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Import from the local main.py file using relative imports
# This ensures it works both when run directly and as a module
try:
    from .main import fetch_content, search_and_extract_results
except ImportError:
    from main import fetch_content, search_and_extract_results

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = ".playwright-browsers"

mcp = FastMCP("Web Search")


@mcp.tool()
async def search_internet(query: str, num_results: int = 8) -> List[Dict]:
    """
    Search DuckDuckGo for the given query and return a list of results.
    """
    results = await search_and_extract_results(query, num_results)
    return [
        {
            "url": r.url,
            "title": r.title,
            "description": r.description,
            "date": r.date,
        }
        for r in results
    ]


@mcp.tool()
async def fetch(url: str) -> Optional[str]:
    """Fetch a webpage using browser and convert it to markdown content.

    Args:
        url: URL of the webpage to fetch

    Returns:
        The webpage content in markdown format, or None if an error occurred
    """
    try:
        content = await fetch_content(url, "md")
        if not content:
            return "Could not extract content from the provided URL."
        return content
    except Exception as e:
        return f"Error fetching content: {str(e)}"


if __name__ == "__main__":
    mcp.run()
