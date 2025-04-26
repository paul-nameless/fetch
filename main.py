#!/usr/bin/env python3

import argparse
import asyncio
import re
import sys
import urllib.parse
from dataclasses import dataclass
from typing import Literal, Optional

import trafilatura
from playwright.async_api import async_playwright


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


@dataclass
class SearchResult:
    url: str
    title: str
    description: str
    date: Optional[str] = None


async def search_and_extract_results(
    query: str, num_results: int = 4
) -> list[SearchResult]:
    """
    Search DuckDuckGo for the given query and extract the first N search results.

    Args:
        query: The search query
        num_results: Number of results to extract

    Returns:
        List of SearchResult objects containing url, title, description and date
    """
    # Encode the query for the URL
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_"

    results = []
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)

            # Create a new page
            page = await browser.new_page()

            # Navigate to the search URL
            await page.goto(search_url, wait_until="networkidle")

            # Wait for search results to load
            await page.wait_for_selector("[data-testid='result']")

            # Extract the first N search results
            result_elements = await page.query_selector_all("[data-testid='result']")

            for i, result in enumerate(result_elements):
                if i >= num_results:
                    break

                # Extract URL
                url_element = await result.query_selector(
                    "[data-testid='result-extras-url-link']"
                )
                url = await url_element.get_attribute("href") if url_element else None

                # If URL is relative, make it absolute
                if url and url.startswith("/"):
                    url = f"https://duckduckgo.com{url}"
                elif not url:
                    continue

                # Extract title
                title_element = await result.query_selector(
                    "[data-testid='result-title-a'] span"
                )
                title = (
                    await title_element.inner_text() if title_element else "No title"
                )

                # Extract description
                desc_element = await result.query_selector(".kY2IgmnCmOGjharHErah")
                desc_text = (
                    await desc_element.inner_text()
                    if desc_element
                    else "No description"
                )

                # Try to extract date if present
                date_match = re.search(r"(\w+ \d+, \d{4})", desc_text)
                date = date_match.group(1) if date_match else None

                # Clean up description (remove date if found)
                description = desc_text
                if date:
                    description = description.replace(date, "").strip()

                results.append(
                    SearchResult(
                        url=url, title=title, description=description, date=date
                    )
                )

            await browser.close()

    except Exception as e:
        print(f"Error during search: {e}", file=sys.stderr)

    return results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch web content and extract HTML or text, or search the web."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", help="URL to fetch content from")
    group.add_argument("--query", "-q", help="Search query for DuckDuckGo")

    parser.add_argument(
        "--output",
        "-o",
        choices=["html", "text", "md"],
        default="text",
        help="Output type for URL content: html, text, or md (default: text)",
    )
    parser.add_argument(
        "--results",
        "-r",
        type=int,
        default=4,
        help="Number of search results to return (default: 4)",
    )
    return parser.parse_args()


def main():
    """Main entry point for the command line tool.

    Parses command line arguments, fetches content and prints the result.
    Exits with a non-zero status code if fetching fails.
    """
    # Parse command line arguments
    args = parse_args()

    if args.url:
        # Run the async fetch operation for a specific URL
        result = asyncio.run(fetch_content(args.url, args.output))

        # Output the result or report failure
        if result:
            print(result)
        else:
            print(f"Failed to fetch content from {args.url}", file=sys.stderr)
            sys.exit(1)
    elif args.query:
        # Run the search operation
        search_results = asyncio.run(
            search_and_extract_results(args.query, args.results)
        )

        if not search_results:
            print(f"No results found for query: {args.query}", file=sys.stderr)
            sys.exit(1)

        # Print the search results
        for i, result in enumerate(search_results, 1):
            print(f"Result {i}:")
            print(f"URL: {result.url}")
            print(f"Title: {result.title}")
            print(f"Description: {result.description}")
            if result.date:
                print(f"Date: {result.date}")
            print()


if __name__ == "__main__":
    main()
