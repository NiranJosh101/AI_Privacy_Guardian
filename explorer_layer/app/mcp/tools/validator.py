# app/mcp/tools/validator.py

import time
import logging
import httpx
from typing import Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from app.mcp.registry import mcp

logger = logging.getLogger(__name__)

_crawler: Optional[AsyncWebCrawler] = None


async def _get_crawler() -> AsyncWebCrawler:
    """Return the shared crawler, starting it on first call."""
    global _crawler
    if _crawler is None:
        browser_config = BrowserConfig(
            headless=True,
            enable_stealth=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        _crawler = AsyncWebCrawler(config=browser_config)
        await _crawler.start()
        logger.info("Shared AsyncWebCrawler started.")
    return _crawler


class SiteValidator:
    def __init__(self):
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

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

        # Increased slightly to ensure we have real data
        self.min_content_length = 400
        self.fast_path_min_length = 5_000

    def _detect_blocks(self, html: str, status_code: int) -> Dict[str, Any]:
        """
        Analyze HTML for blocking signals with high tolerance for Status 200.

        THE CRITICAL LOGIC:
        If status is 200 and we have content, it's NOT a block.
        We only flag 'is_blocked' for hard errors (403/429/503)
        or a 200 that is clearly a "Challenge / Empty" page.
        """
        content_lower = html.lower()
        has_block_keywords = any(k in content_lower for k in self.block_indicators)
        is_empty = len(content_lower.strip()) < self.min_content_length

        actually_blocked = (status_code in [403, 429, 503]) or (
            status_code == 200 and is_empty and has_block_keywords
        )

        return {
            "is_blocked": actually_blocked,
            "has_captcha": "captcha" in content_lower,
            "js_required": "javascript" in content_lower and is_empty,
            "is_empty": is_empty,
            "block_detected": has_block_keywords,
            "status_block": status_code in [403, 429, 503],
        }

    async def _fast_path(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Phase 1 — httpx pre-check (~500 ms – 1.5 s).

        Returns a result dict if the site is clearly accessible, or None if we
        should fall through to the browser.

        We skip to the browser when:
          - httpx raises any exception (connection error, timeout, TLS issue)
          - Status code is not 200
          - Response body is too short to trust (likely a JS challenge page)
          - _detect_blocks signals a block even with good content length
        """
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=5.0,
            ) as client:
                start = time.time()
                resp = await client.get(url, headers={"User-Agent": self.user_agent})
                elapsed = round(time.time() - start, 2)

                # Only trust a clean 200 with substantial content
                if resp.status_code == 200 and len(resp.text) >= self.fast_path_min_length:
                    signals = self._detect_blocks(resp.text, resp.status_code)

                    if not signals["is_blocked"]:
                        logger.debug(f"[fast_path] {url} — OK in {elapsed}s")
                        return {
                            "status_code": resp.status_code,
                            "final_url": str(resp.url),
                            "redirected": str(resp.url) != url,
                            "response_time": elapsed,
                            "can_proceed": True,
                            "validation_method": "fast_path",
                            **signals,
                        }

                # Status wasn't 200, or content too short, or block detected —
                # fall through to browser.
                logger.debug(
                    f"[fast_path] {url} — skipping browser fallback "
                    f"(status={resp.status_code}, len={len(resp.text)})"
                )

        except Exception as exc:
            # Network error, TLS failure, timeout — let the browser try.
            logger.debug(f"[fast_path] {url} — httpx failed ({exc}), falling back.")

        return None

    async def _browser_path(self, url: str) -> Dict[str, Any]:
        """
        Phase 2 — full browser check, only reached when the fast path fails.

        Key changes vs original:
          - page_timeout dropped from 20 000 ms → 8 000 ms  (prevents 20 s hangs)
          - Uses the shared persistent crawler (no cold-start overhead)
        """
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="domcontentloaded",  # Don't wait for ads / trackers to settle
            page_timeout=8000,              # Hard cap: 8 s instead of 20 s
            magic=False,
        )

        crawler = await _get_crawler()

        start = time.time()
        result = await crawler.arun(url=url, config=run_config)
        elapsed = round(time.time() - start, 2)

        html_content = result.html if result.html else ""
        signals = self._detect_blocks(html_content, result.status_code)
        can_proceed = result.success and not signals["is_blocked"]

        logger.debug(f"[browser_path] {url} — done in {elapsed}s, can_proceed={can_proceed}")

        return {
            "status_code": result.status_code,
            "final_url": str(result.url),
            "redirected": str(result.url) != url,
            "response_time": elapsed,
            "can_proceed": can_proceed,
            "validation_method": "browser_path",
            **signals,
        }

    async def validate(self, url: str) -> Dict[str, Any]:
        """
        Two-phase validation:

          Phase 1 (fast_path)  — httpx, ~500 ms – 1.5 s, covers ~80 % of sites.
          Phase 2 (browser_path) — Chromium via crawl4ai, ~2 s – 8 s, for the rest.
        """
        # --- Phase 1 ---
        fast_result = await self._fast_path(url)
        if fast_result is not None:
            return fast_result

        # --- Phase 2 ---
        try:
            return await self._browser_path(url)
        except Exception as e:
            logger.error(f"Validation error for {url}: {e}")
            return {
                "can_proceed": False,
                "error": str(e),
                "is_blocked": True,
                "validation_method": "browser_path",
            }

_validator = SiteValidator()


@mcp.tool()
async def validate_site_access(url: str) -> Dict[str, Any]:
    return await _validator.validate(url)