# app/mcp/tools/validator.py

import time
import logging
from typing import Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from app.mcp.registry import mcp

logger = logging.getLogger(__name__)

class SiteValidator:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # Keywords that MIGHT indicate a block
        self.block_indicators = [
            "captcha",
            "access denied",
            "forbidden",
            "verify you are human",
            "cloudflare",
            "blocked",
            "bot detection",
        ]

        self.min_content_length = 800  # Increased slightly to ensure we have real data

    def _detect_blocks(self, html: str, status_code: int) -> Dict[str, Any]:
        """
        Analyze rendered HTML for blocking signals with high tolerance for Status 200.
        """
        content_lower = html.lower()
        has_block_keywords = any(k in content_lower for k in self.block_indicators)
        is_empty = len(content_lower.strip()) < self.min_content_length

        # --- THE CRITICAL LOGIC ---
        # If status is 200 and we have content, it's NOT a block.
        # We only flag 'is_blocked' if it's a hard error (403/429) 
        # or a 200 that is clearly a "Challenge/Empty" page.
        actually_blocked = (status_code in [403, 429, 503]) or (status_code == 200 and is_empty and has_block_keywords)

        return {
            "is_blocked": actually_blocked, 
            "has_captcha": "captcha" in content_lower,
            "js_required": "javascript" in content_lower and is_empty,
            "is_empty": is_empty,
            "block_detected": has_block_keywords,
            "status_block": status_code in [403, 429, 503]
        }

    async def validate(self, url: str) -> Dict[str, Any]:
        browser_config = BrowserConfig(
            headless=True,
            enable_stealth=True, 
            user_agent=self.user_agent
        )

        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="networkidle",
            magic=True, 
        )

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                start_time = time.time()
                result = await crawler.arun(url=url, config=run_config)
                elapsed = time.time() - start_time

                html_content = result.html if result.html else ""
                signals = self._detect_blocks(html_content, result.status_code)

                # Proceed if we got a 200 and it doesn't look like a tiny "Access Denied" page
                can_proceed = result.success and not signals["is_blocked"]

                return {
                    "status_code": result.status_code,
                    "final_url": str(result.url),
                    "redirected": str(result.url) != url,
                    "response_time": round(elapsed, 2),
                    "can_proceed": can_proceed,
                    **signals,
                }

        except Exception as e:
            logger.error(f"Validation Error: {str(e)}")
            return {"can_proceed": False, "error": str(e), "is_blocked": True}

@mcp.tool()
async def validate_site_access(url: str) -> Dict[str, Any]:
    validator = SiteValidator()
    return await validator.validate(url)