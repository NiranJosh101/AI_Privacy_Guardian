import json
import asyncio
from typing import Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from app.mcp.registry import mcp
from app.config.config_manager import settings

class PolicyExtractor:
    """
    Converts messy legal pages into high-density Markdown using 
    modern Crawl4AI generation strategies.
    """

    def __init__(self):
        # 1. Define the Filter (Noise Removal)
        self.content_filter = PruningContentFilter(
            threshold=0.45,
            min_word_threshold=50
        )
        
        # 2. Define the Generator (Strategy Replacement for MarkdownGenerationConfig)
        self.md_generator = DefaultMarkdownGenerator(
            content_filter=self.content_filter,
        )

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
            result = await crawler.arun(url=url, config=run_config)

            if result.success:
                return (
                    result.markdown_v2.raw_markdown
                    if result.markdown_v2
                    else result.markdown
                )

            return None

# MCP Tool Wrapper
# Assuming 'mcp' is initialized in your server.py or imported here


@mcp.tool()
async def extract_policy_content(url: str) -> str:
    extractor = PolicyExtractor()

    try:
        content = await extractor.extract_markdown(url)

        if not content:
            return json.dumps({
                "status": "error",
                "url": url,
                "message": "No content extracted"
            })

        return json.dumps({
            "status": "success",
            "url": url,
            "content": content
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "url": url,
            "message": str(e)
        })