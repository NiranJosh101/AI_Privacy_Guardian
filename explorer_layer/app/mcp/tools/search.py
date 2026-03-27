import asyncio
from typing import Dict, List, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from app.mcp.registry import mcp
from app.config.config_manager import settings

class LinkScout:
    def __init__(self):
        self.categories = settings.search.document_categories
        self.max_links = settings.search.max_links_to_analyze
        # Precision-matched User-Agent
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

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
            # 1. BROWSER UPGRADE: Stealth + Fingerprint Masking
            browser_config = BrowserConfig(
                headless=settings.browser.headless,
                enable_stealth=True,
                user_agent=self.user_agent,
                # Avoid common 'automation' flags in the browser binary itself
                extra_args=["--disable-blink-features=AutomationControlled"]
            )

            # 2. RUN UPGRADE: MAGIC MODE
            # magic=True: Automates human-like scrolling and interaction
            # wait_for: Adds a small hard sleep to allow JS to settle even after networkidle
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="networkidle",
                magic=True,               # <--- CRITICAL FOR BYPASSING BLOCKS
                page_timeout=45000,       # Increased for slow-loading media sites
                remove_overlay_elements=True,
                scan_full_page=True       # Ensures links in footers are triggered
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=base_url, config=config)

                # Internal link extraction
                internal_links = (result.links or {}).get("internal", [])
                
                print(f"--- DEBUG: Crawl Success: {result.success} ---")
                print(f"--- DEBUG: Status Code: {result.status_code} ---")
                print(f"--- DEBUG: HTML Length: {len(result.html) if result.html else 0} ---")
                print(f"--- DEBUG: Internal Links Found: {len(internal_links)} ---")
                
                # Check for "Soft Blocks"
                if not result.success or not internal_links:
                    print(f"--- DEBUG: Soft block detected for {base_url}. No links extracted. ---")
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
                        suite[best_cat].append({
                            "url": href,
                            "anchor_text": text,
                            "confidence": category_scores[best_cat]
                        })

                # Deduplicate + sort
                for cat in suite:
                    unique_links = {l["url"]: l for l in suite[cat]}.values()
                    suite[cat] = sorted(
                        unique_links,
                        key=lambda x: x["confidence"],
                        reverse=True
                    )[: self.max_links]

                return suite

        except Exception as e:
            print(f"--- DEBUG: LinkScout logic error: {str(e)} ---")
            return {cat: [] for cat in self.categories.keys()}

@mcp.tool()
async def discover_regulatory_links(url: str) -> Dict[str, Any]:
    """
    Scans a website and returns a categorized map of legal/regulatory links.
    """
    scout = LinkScout()
    return await scout.find_regulatory_suite(url)