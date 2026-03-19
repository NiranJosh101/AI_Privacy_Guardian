import asyncio
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from explorer_layer.app.config.config_manager import ConfigManager  

class LinkScout:
    def __init__(self):
        # Accessing categorized keywords from config.yaml
        settings = ConfigManager().config
        self.categories = settings.search.document_categories
        self.max_links = settings.search.max_links_to_analyze

    def _classify_link(self, text: str, href: str) -> Dict[str, float]:
        """
        Calculates a score for each category.
        Example output: {"privacy": 0.9, "terms": 0.1, "legal": 0.0}
        """
        combined = (text + " " + href).lower()
        scores = {cat: 0.0 for cat in self.categories.keys()}
        
        for cat, keywords in self.categories.items():
            for kw in keywords:
                if kw in combined:
                    scores[cat] += 0.4 # Cumulative score for matches
        
        # Normalize and cap at 1.0
        return {cat: min(score, 1.0) for cat, score in scores.items()}

    async def find_regulatory_suite(self, base_url: str) -> Dict[str, List[Dict]]:
        """
        Scans the site and returns links grouped by category.
        """
        config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=base_url, config=config)
            
            if not result.success:
                return {}

            # Structure: {"privacy": [], "terms": [], "legal": []}
            suite = {cat: [] for cat in self.categories.keys()}
            
            # Use Crawl4AI's extracted internal links
            internal_links = result.media.get("links", {}).get("internal", [])
            
            for link in internal_links:
                href = link.get("href", "")
                text = link.get("text", "")
                
                category_scores = self._classify_link(text, href)
                
                # Assign to the highest scoring category if it's above a threshold
                best_cat = max(category_scores, key=category_scores.get)
                if category_scores[best_cat] > 0.3:
                    suite[best_cat].append({
                        "url": href,
                        "anchor_text": text,
                        "confidence": category_scores[best_cat]
                    })

            # Sort each category by confidence and limit results
            for cat in suite:
                suite[cat] = sorted(suite[cat], key=lambda x: x["confidence"], reverse=True)[:3]
                
            return suite

# MCP Tool Wrapper
@mcp.tool()
async def discover_regulatory_links(url: str) -> Dict[str, List[Dict]]:
    """
    Scans a website and returns a categorized map of legal/regulatory links 
    (Privacy, Terms, Cookies, etc.).
    """
    scout = LinkScout()
    return await scout.find_regulatory_suite(url)