# Web Fetcher

A Python application that fetches content from web pages with playwright headless chromium and returns either HTML, text or markdown. It can also search the web using DuckDuckGo.

Can be used as for LLM agents through MCP or bash, allowing them to fetch data from web pages with JavaScript.

- Fetch HTML content from any web URL using Playwright
- Extract readable text/markdown content from HTML
- Search the web using DuckDuckGo and get results

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Installation

```bash
uv sync
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run playwright install chromium
```

## Usage

### Fetching content from a URL

```bash
# Fetch content from a URL as markdown
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run main.py --url https://example.com --output md

# Short form
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run main.py -u https://example.com -o md
```

### Searching the web

```bash
# Search the web for "python playwright"
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run main.py --query "python playwright"

# Short form with custom number of results
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run main.py -q "python playwright" -r 6
```

## MCP Integration

To use with MCP (for AI tools):

```bash
# Add tool to search the web
claude mcp add-json search '{"type": "stdio", "command":"uv","args":["--directory", "/path/to/fetch", "run", "python", "webmcp.py"]}'

# Direct command
uv --direcotry /Users/paul/Downloads/fetch run python webmcp.py
```

## Options

- `--url`, `-u`: The URL to fetch content from
- `--query`, `-q`: Search query for DuckDuckGo
- `--output`, `-o`: Output type for URL content: `html`, `text` or `md` (default: `text`)
- `--results`, `-r`: Number of search results to return (default: 4)
