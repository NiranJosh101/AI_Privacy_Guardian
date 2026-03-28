import asyncio
import json
import logging
from typing import Dict, List, Any

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from app.mcp.registry import mcp
from app.config.config_manager import settings

logger = logging.getLogger(__name__)


class LinkScout:
    def __init__(self):
        self.categories = settings.search.document_categories
        self.max_links = settings.search.max_links_to_analyze

        # Precision-matched User-Agent
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
                wait_until="networkidle",
                magic=True,
                page_timeout=45000,
                remove_overlay_elements=True,
                scan_full_page=True,
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=base_url, config=config)

                internal_links = (result.links or {}).get("internal", [])

                logger.debug(f"Crawl Success: {result.success}")
                logger.debug(f"Status Code: {result.status_code}")
                logger.debug(f"HTML Length: {len(result.html) if result.html else 0}")
                logger.debug(f"Internal Links Found: {len(internal_links)}")

                # Soft block detection
                if not result.success:
                    logger.warning(f"Crawl failed for {base_url}")
                    return {cat: [] for cat in self.categories.keys()}

                if not internal_links:
                    logger.warning(f"No internal links found (possible soft block): {base_url}")
                    return {cat: [] for cat in self.categories.keys()}

                suite = {cat: [] for cat in self.categories.keys()}

                for link in internal_links:
                    href = link.get("href", "")
                    text = link.get("text", "")

                    if not href or href.startswith(("#", "javascript:")):
                        continue

                    category_scores = self._classify_link(text, href)
                    best_cat = max(category_scores, key=category_scores.get)

                    if category_scores[best_cat] > 0.3:
                        suite[best_cat].append(
                            {
                                "url": href,
                                "anchor_text": text,
                                "confidence": category_scores[best_cat],
                            }
                        )

                # Deduplicate + sort
                for cat in suite:
                    unique_links = {l["url"]: l for l in suite[cat]}.values()
                    suite[cat] = sorted(
                        unique_links,
                        key=lambda x: x["confidence"],
                        reverse=True,
                    )[: self.max_links]

                return suite

        except Exception as e:
            logger.exception(f"LinkScout logic error: {str(e)}")
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
        logger.debug(f"MCP Tool Final Check - Data Found: {has_data}")

        payload = {
            "status": "success" if has_data else "no_links_found",
            "url": url,
            "categories": results,
        }

        # 🔥 CRITICAL FIX: Always return string for MCP
        return json.dumps(payload)

    except Exception as e:
        logger.exception(f"MCP tool error for {url}: {str(e)}")

        error_payload = {
            "status": "error",
            "url": url,
            "message": str(e),
            "categories": {},
        }

        return json.dumps(error_payload)