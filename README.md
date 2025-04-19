# Web Fetcher

A Python application that fetches content from web pages with playwright headless chromium and returns either HTML, text or markdown.

Can be used as for LLM agents through MCP or bash, allowing them to fetch data from web pages with JavaScript.

- Fetch HTML content from any web URL using Playwright
- Extract readable text/markdown content from HTML

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Installation

```bash
uv sync
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run playwright install chromium
```

## Usage

```bash
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers uv run main.py -o md https://example.com
```

## Options

- `url`: The URL to fetch content from (required)
- `--output`, `-o`: Output type, either `html`, `text` or `md` (default: `text`)
