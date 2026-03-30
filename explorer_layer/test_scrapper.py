import asyncio
import json
import logging
from typing import Dict, List, Any
from urllib.parse import urljoin

# Mocking the Crawler and Settings to match your production environment
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode

# 1. SETUP LOGGING (Mimics your app logger)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("LinkScout_Test")

# 2. CONFIGURATION (Your exact search_discovery suite)
MOCK_CONFIG = {
    "max_links_to_analyze": 3,
    "document_categories": {
        "privacy": ["privacy", "data protection", "gdpr", "privacy-policy"],
        "terms": ["terms of use", "tos", "conditions", "agreement"],
        "legal": ["disclaimer", "legal notice", "compliance", "dmca"]
    }
}

class LinkScout:
    def __init__(self):
        self.categories = MOCK_CONFIG["document_categories"]
        self.max_links = MOCK_CONFIG["max_links_to_analyze"]
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
                    scores[cat] += 0.4 # Each keyword match adds 0.4

        return {cat: min(score, 1.0) for cat, score in scores.items()}

    async def find_regulatory_suite(self, base_url: str) -> Dict[str, List[Dict]]:
        try:
            # Real Browser Config (Headless for test)
            browser_config = BrowserConfig(
                headless=True,
                enable_stealth=True,
                user_agent=self.user_agent
            )

            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="networkidle",
                magic=True,
                scan_full_page=True,
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                print(f"--- DEBUG: Crawling {base_url} ---")
                result = await crawler.arun(url=base_url, config=config)
                
                # Extract internal links like the real tool does
                internal_links = (result.links or {}).get("internal", [])
                logger.debug(f"Total Internal Links Scanned: {len(internal_links)}")

                suite = {cat: [] for cat in self.categories.keys()}

                for link in internal_links:
                    href = link.get("href", "")
                    text = link.get("text", "")

                    if not href or href.startswith(("#", "javascript:")):
                        continue

                    # THE CLASSIFICATION LOGIC
                    category_scores = self._classify_link(text, href)
                    # Find the highest scoring category
                    best_cat = max(category_scores, key=category_scores.get)

                    if category_scores[best_cat] > 0.3:
                        suite[best_cat].append({
                            "url": urljoin(base_url, href), # Normalized!
                            "anchor_text": text,
                            "confidence": category_scores[best_cat],
                        })

                # Deduplicate and sort by confidence
                for cat in suite:
                    unique_links = {l["url"]: l for l in suite[cat]}.values()
                    suite[cat] = sorted(
                        unique_links,
                        key=lambda x: x["confidence"],
                        reverse=True
                    )[: self.max_links]

                return suite

        except Exception as e:
            logger.exception(f"LinkScout isolation error: {str(e)}")
            return {cat: [] for cat in self.categories.keys()}

# 3. THE MCP MOCK RUNNER
async def run_isolation_test(target_url: str):
    print(f"\n{'='*50}\nTESTING URL: {target_url}\n{'='*50}")
    
    scout = LinkScout()
    
    # Run the actual logic
    results = await scout.find_regulatory_suite(target_url)
    
    # Construct the final JSON payload exactly like the MCP @tool
    has_data = any(len(links) > 0 for links in results.values())
    
    payload = {
        "status": "success" if has_data else "no_links_found",
        "url": target_url,
        "categories": results,
    }

    print("\n--- FINAL MCP JSON OUTPUT ---")
    print(json.dumps(payload, indent=2))
    print(f"\nSuccess Status: {payload['status']}")
    
    if payload['status'] == "success":
        for cat, links in results.items():
            print(f"Category '{cat}': Found {len(links)} links")
    else:
        print("!!! WARNING: No links were identified. Check if keywords match site content.")

if __name__ == "__main__":
    # Change this URL to the one giving you trouble!
    TEST_URL = "https://o2tvseries4u.com/" 
    asyncio.run(run_isolation_test(TEST_URL))