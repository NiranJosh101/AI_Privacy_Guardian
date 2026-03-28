import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://o2tvseries4u.com/")
        print(f"Success: {result.success}")
        print(f"Content Length: {len(result.html)}")

if __name__ == "__main__":
    asyncio.run(main())