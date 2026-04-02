import json
import logging
from typing import Dict, List, Any
from urllib.parse import urljoin

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from app.mcp.registry import mcp
from app.config.config_manager import settings

logger = logging.getLogger(__name__)

class LinkScout:
    def __init__(self):
        # Maps the config values to the class
        self.categories = settings.search.document_categories
        self.max_links = settings.search.max_links_to_analyze
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _classify_link(self, text: str, href: str) -> Dict[str, float]:
        combined = (str(text) + " " + str(href)).lower()
        scores = {cat: 0.0 for cat in self.categories.keys()}

        for cat, keywords in self.categories.items():
            for kw in keywords:
                if kw in combined:
                    scores[cat] += 0.4 

        return {cat: min(score, 1.0) for cat, score in scores.items()}

    async def find_regulatory_suite(self, base_url: str) -> Dict[str, List[Dict]]:
        try:
            browser_config = BrowserConfig(
                headless=settings.browser.headless,
                enable_stealth=True,
                user_agent=self.user_agent,
                extra_args=["--disable-blink-features=AutomationControlled"],
            )

            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="domcontentloaded",
                wait_for="footer, [class*='footer'], #footer",
                js_code="window.scrollTo(0, document.body.scrollHeight);",
                magic=True,
                page_timeout=30000,
                remove_overlay_elements=True,
                scan_full_page=True,
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"LinkScout: Starting crawl for {base_url}")
                result = await crawler.arun(url=base_url, config=config)

                if not result.success:
                    logger.warning(f"LinkScout: Crawl failed for {base_url}")
                    return {cat: [] for cat in self.categories.keys()}
                
                all_found_links = []
                
                for link_group in result.links.values():
                    if isinstance(link_group, list):
                        all_found_links.extend(link_group)

                logger.debug(f"LinkScout: Analyzing {len(all_found_links)} total links")

                suite = {cat: [] for cat in self.categories.keys()}

                for link in all_found_links:
                    href = link.get("href", "")
                    text = link.get("text", "").strip()

                    if not href or href.startswith(("#", "javascript:")):
                        continue

                    category_scores = self._classify_link(text, href)
                    # Get the category with the highest score
                    best_cat = max(category_scores, key=category_scores.get)

                    # Only add if the score is above threshold
                    if category_scores[best_cat] > 0.3:
                        suite[best_cat].append({
                            "url": urljoin(base_url, href),
                            "anchor_text": text,
                            "confidence": category_scores[best_cat],
                        })

                # Deduplicate and sort
                for cat in suite:
                    unique_links = {l["url"]: l for l in suite[cat]}.values()
                    suite[cat] = sorted(
                        unique_links,
                        key=lambda x: x["confidence"],
                        reverse=True
                    )[: self.max_links]

                return suite

        except Exception as e:
            logger.exception(f"LinkScout Error: {str(e)}")
            return {cat: [] for cat in self.categories.keys()}

@mcp.tool()
async def discover_regulatory_links(url: str) -> str:
    """
    Scans a website and returns a categorized map of legal/regulatory links.
    MCP-SAFE: Always returns a JSON string.
    """
    scout = LinkScout()

    try:
        results = await scout.find_regulatory_suite(url)

        has_data = any(len(links) > 0 for links in results.values())
        
        payload = {
            "status": "success" if has_data else "no_links_found",
            "url": url,
            "categories": results,
        }

        # The JSON string that the Discovery Node will receive
        return json.dumps(payload)

    except Exception as e:
        logger.exception(f"MCP Tool Exception for {url}: {str(e)}")
        return json.dumps({
            "status": "error",
            "url": url,
            "message": str(e),
            "categories": {},
        })