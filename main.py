#!/usr/bin/env python3

import asyncio
import argparse
from playwright.async_api import async_playwright
import trafilatura
from typing import Optional, Literal
import sys


async def fetch_html(url: str) -> Optional[str]:
    """Fetch HTML content from a URL using Playwright.

    Args:
        url: The URL to fetch content from

    Returns:
        The HTML content as a string, or None if an error occurred
    """
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(headless=True)

            # Create a new page
            page = await browser.new_page()

            # Navigate to the URL and wait until network is idle
            await page.goto(url, wait_until="networkidle")

            # Get the page content
            html = await page.content()

            # Close the browser
            await browser.close()
            return html
    except Exception as e:
        print(f"Error fetching HTML: {e}", file=sys.stderr)
        return None


def extract_text(html: str) -> Optional[str]:
    """Extract readable text content from HTML using Trafilatura.

    Args:
        html: The HTML content to extract text from

    Returns:
        The extracted text content as a string, or None if an error occurred
    """
    try:
        # Use trafilatura to extract the main content from HTML
        # This removes navigation, ads, and other non-content elements
        return trafilatura.extract(html)
    except Exception as e:
        print(f"Error extracting text: {e}", file=sys.stderr)
        return None


async def fetch_content(
    url: str, output_type: Literal["html", "text", "md"] = "text"
) -> Optional[str]:
    """Fetch content from URL and return either HTML or extracted text.

    Args:
        url: The URL to fetch content from
        output_type: The type of content to return ('html' or 'text')

    Returns:
        The requested content as a string, or None if an error occurred
    """
    # First, fetch the HTML content from the URL
    html = await fetch_html(url)

    if html is None:
        return None

    match output_type:
        case "html":
            return html
        case "text":
            return trafilatura.extract(html)
        case "md":
            # Extract and return only the markdown content
            return trafilatura.extract(html, output_format="markdown")
        case _:
            raise ValueError(f"Invalid output type: {output_type}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch web content and extract HTML or text."
    )
    parser.add_argument("url", help="URL to fetch content from")
    parser.add_argument(
        "--output",
        "-o",
        choices=["html", "text", "md"],
        default="text",
        help="Output type: html or text (default: text)",
    )
    return parser.parse_args()


def main():
    """Main entry point for the command line tool.

    Parses command line arguments, fetches content and prints the result.
    Exits with a non-zero status code if fetching fails.
    """
    # Parse command line arguments
    args = parse_args()

    # Run the async fetch operation
    result = asyncio.run(fetch_content(args.url, args.output))

    # Output the result or report failure
    if result:
        print(result)
    else:
        print(f"Failed to fetch content from {args.url}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
