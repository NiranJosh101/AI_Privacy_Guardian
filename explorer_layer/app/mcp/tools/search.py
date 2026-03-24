import asyncio
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from app.mcp.registry import mcp
from app.config.config_manager import settings  



class LinkScout:
    def __init__(self):
        self.categories = settings.search.document_categories
        self.max_links = settings.search.max_links_to_analyze

    def _classify_link(self, text: str, href: str) -> Dict[str, float]:
        combined = (str(text) + " " + str(href)).lower()
        scores = {cat: 0.0 for cat in self.categories.keys()}
        
        for cat, keywords in self.categories.items():
            for kw in keywords:
                if kw in combined:
                    scores[cat] += 0.4 
        
        return {cat: min(score, 1.0) for cat, score in scores.items()}

    async def find_regulatory_suite(self, base_url: str) -> Dict[str, List[Dict]]:
        # Fast crawl for discovery - we don't need heavy markdown here
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            headless=settings.browser.headless
        )

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=base_url, config=config)
            
            if not result.success:
                return {}

            suite = {cat: [] for cat in self.categories.keys()}
            
            # result.links is a dict containing 'internal' and 'external' lists
            all_links = result.links.get("internal", [])

            for link in all_links:
                href = link.get("href", "")
                text = link.get("text", "")
                
                # Basic cleaning to avoid fragments/crashes
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue

                category_scores = self._classify_link(text, href)
                best_cat = max(category_scores, key=category_scores.get)
                
                if category_scores[best_cat] > 0.3:
                    suite[best_cat].append({
                        "url": href,
                        "anchor_text": text,
                        "confidence": category_scores[best_cat]
                    })

            # Sort and deduplicate (by URL)
            for cat in suite:
                unique_links = {l["url"]: l for l in suite[cat]}.values()
                suite[cat] = sorted(unique_links, key=lambda x: x["confidence"], reverse=True)[:3]
                
            return suite

@mcp.tool()
async def discover_regulatory_links(url: str) -> Dict[str, List[Dict]]:
    """
    Scans a website and returns a categorized map of legal/regulatory links.
    """
    scout = LinkScout()
    return await scout.find_regulatory_suite(url)