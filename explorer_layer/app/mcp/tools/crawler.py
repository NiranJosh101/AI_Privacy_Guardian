import json
import asyncio
import logging
import re
from typing import Optional, Dict, Any

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from app.mcp.registry import mcp
from app.config.config_manager import settings

logger = logging.getLogger(__name__)

class PolicyExtractor:
    def __init__(self):
        # Handle potential version differences in crawl4ai arguments
        try:
            self.content_filter = PruningContentFilter(
                threshold=0.6,
                min_word_threshold=80,
                threshold_type="fixed"
            )
        except TypeError:
            self.content_filter = PruningContentFilter(
                threshold=0.6,
                min_words=80
            )

        self.md_generator = DefaultMarkdownGenerator(
            content_filter=self.content_filter,
        )

    def remove_special_characters(self, text: str) -> str:
        """Cleans noise and ensures the string is safe for transport."""
        cleaned = re.sub(r"[^\w\s\.\,\:\;\-\?\!\n#]", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)
        return cleaned.strip()

    async def extract_markdown(self, url: str) -> Optional[str]:
        browser_config = BrowserConfig(
            headless=settings.browser.headless,
            user_agent=settings.browser.user_agent,
            enable_stealth=True,
        )

        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            markdown_generator=self.md_generator,
            wait_for_images=False,
            page_timeout=45000,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            print(f"\n [EXTRACTOR START] {url}")
            logger.info(f"[PolicyExtractor] Crawling: {url}")

            result = await crawler.arun(url=url, config=run_config)

            if result.success:
                print(f" [EXTRACTOR SUCCESS] {url}")
                
                # Extract markdown safely based on object structure
                if result.markdown:
                    raw = (result.markdown.raw_markdown 
                           if hasattr(result.markdown, "raw_markdown") 
                           else str(result.markdown))

                    cleaned = self.remove_special_characters(raw)
                    
                    print(f" [CLEANED LENGTH]: {len(cleaned)}")
                    return cleaned
                else:
                    print(f" [NO MARKDOWN RETURNED]: {url}")
            else:
                logger.error(f"[PolicyExtractor] Failed: {url} | {result.error_message}")

            return None

@mcp.tool()
async def extract_policy_content(url: str) -> Dict[str, Any]:
    """
    Extracts policy content from a URL and returns a structured dictionary.
    The MCP SDK will automatically serialize this to the client.
    """
    extractor = PolicyExtractor()

    print(f"\n[MCP TOOL CALLED] URL: {url}")

    try:
        content = await extractor.extract_markdown(url)

        if not content:
            print("[NO CONTENT AFTER EXTRACTION]")
            return {
                "status": "error",
                "url": url,
                "message": "No content extracted"
            }

        print(f"🎯 [FINAL CONTENT LENGTH]: {len(content)}")
        print("[MCP RETURN SUCCESS]\n")

        # Return the dictionary directly. Do NOT use json.dumps() here.
        return {
            "status": "success",
            "url": url,
            "content": content
        }

    except Exception as e:
        print(f"[EXTRACTION CRASH]: {str(e)}")
        logger.error(f"[PolicyExtractor] Crash for {url}: {str(e)}")

        return {
            "status": "error",
            "url": url,
            "message": f"Extraction Tool Error: {str(e)}"
        }