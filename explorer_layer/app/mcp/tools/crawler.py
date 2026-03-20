import asyncio
from typing import Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, MarkdownGenerationConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from app.core.config_manager import settings

class PolicyExtractor:
    """
    The 'Surgical' tool of the Explorer. 
    Converts messy legal pages into high-density Markdown.
    """

    def __init__(self):
        # We use a Pruning filter to strip navbars, footers, and scripts
        self.content_filter = PruningContentFilter(
            threshold=0.45,       # Higher = stricter removal of 'noise'
            min_word_count=50     # Ignore small text blocks (links/footers)
        )
        
        # Configure how the Markdown is generated
        self.md_config = MarkdownGenerationConfig(
            content_filter=self.content_filter,
            ignore_links=True,    # We don't need links inside the policy text
            ignore_images=True    # Legal docs don't need images
        )

    async def extract_markdown(self, url: str) -> Optional[str]:
        """
        Executes a deep crawl and returns clean Markdown.
        """
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED, # Cache legal docs to save compute
            markdown_generator=self.md_config,
            wait_for_images=False,
            headless=settings.browser.headless,
            user_agent=settings.browser.user_agent
        )

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                # result.markdown_v2 provides structured, filtered text
                return result.markdown_v2.raw_markdown
            
            return None

# MCP Tool Wrapper
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