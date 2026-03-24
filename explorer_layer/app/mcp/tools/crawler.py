import asyncio
from typing import Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
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
            min_word_count=50
        )
        
        # 2. Define the Generator (Strategy Replacement for MarkdownGenerationConfig)
        self.md_generator = DefaultMarkdownGenerator(
            content_filter=self.content_filter,
            options={
                "ignore_links": True,
                "ignore_images": True,
                "skip_internal_links": True
            }
        )

    async def extract_markdown(self, url: str) -> Optional[str]:
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            markdown_generator=self.md_generator, # Strategy injected here
            wait_for_images=False,
            headless=settings.browser.headless,
            user_agent=settings.browser.user_agent
        )

        async with AsyncWebCrawler() as crawler:
            # Note: Ensure you've run 'python -m crawl4ai.setup' to install Playwright
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                # In modern Crawl4AI, markdown_v2 is a structured object
                return result.markdown_v2.raw_markdown if result.markdown_v2 else result.markdown
            
            return None

# MCP Tool Wrapper
# Assuming 'mcp' is initialized in your server.py or imported here
@mcp.tool()
async def extract_policy_content(url: str) -> str:
    """
    Performs a high-fidelity crawl of a specific legal URL and 
    returns a clean Markdown version of the text content.
    """
    extractor = PolicyExtractor()
    content = await extractor.extract_markdown(url)
    
    if not content:
        return f"Error: Could not extract content from {url}"
    
    return content