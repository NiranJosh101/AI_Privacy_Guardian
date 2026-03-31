import json
import asyncio
import logging
import re
from typing import Optional

# We assume these are available in your environment
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Setup basic logging to see what's happening in isolation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyExtractor:
    """
    Standalone Mock of the PolicyExtractor logic.
    Includes post-processing to remove unwanted special characters.
    """

    def __init__(self):
        self.content_filter = PruningContentFilter(
            threshold=0.6,
            min_word_threshold=80,
            threshold_type="fixed"
        )
        
        self.md_generator = DefaultMarkdownGenerator(
            content_filter=self.content_filter,
        )

    def remove_special_characters(self, text: str) -> str:
        """
        Remove unwanted special characters while preserving readable structure.
        """
        # Keep letters, numbers, whitespace, and useful punctuation
        cleaned = re.sub(r"[^\w\s\.\,\:\;\-\?\!\n#]", "", text)

        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)

        return cleaned.strip()

    async def extract_markdown(self, url: str) -> Optional[str]:
        browser_config = BrowserConfig(
            headless=True,
            enable_stealth=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=self.md_generator,
            wait_for_images=False,
            page_timeout=45000,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            logger.info(f"Starting crawl for: {url}")
            result = await crawler.arun(url=url, config=run_config)

            if result.success:
                logger.info(f"Crawl successful for {url}")

                if result.markdown:
                    # Extract raw markdown
                    if hasattr(result.markdown, 'raw_markdown'):
                        raw = result.markdown.raw_markdown
                    else:
                        raw = str(result.markdown)

                    # 🔥 Apply cleaning here
                    cleaned = self.remove_special_characters(raw)
                    return cleaned

            else:
                logger.error(f"Crawl failed for {url}: {result.error_message}")

            return None


async def test_extraction():
    extractor = PolicyExtractor()
    test_url = "https://o2tvseries4u.com/pages/privacy-policy"
    
    print(f"\n--- Testing Extraction for: {test_url} ---")
    try:
        content = await extractor.extract_markdown(test_url)
        if content:
            print(f"SUCCESS! Extracted {len(content)} characters.")
            print("\nPreview of content (first 1000 chars):")
            print("-" * 40)
            print(content[:5000])
            print("-" * 40)
        else:
            print("FAILED: No content returned.")
    except Exception as e:
        print(f"CRASHED with error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_extraction())