from mcp.server.fastmcp import FastMCP

# Import tool logic (NOT decorators)
from app.mcp.tools.search import LinkScout
from app.mcp.tools.crawler import PolicyExtractor
from app.mcp.tools.validator import SiteValidator


# 1. Initialize ONE MCP Server
mcp = FastMCP("ExplorerTools", host="0.0.0.0", port=8002)


# 2. Register Scout Tool
@mcp.tool()
async def scout_regulatory_links(url: str) -> dict:
    """
    Finds and categorizes regulatory links (Privacy, Terms, Legal) 
    on a given landing page.
    """
    scout = LinkScout()
    return await scout.find_regulatory_suite(url)


# 3. Register Extractor Tool
@mcp.tool()
async def extract_content(url: str) -> str:
    """
    Performs a high-fidelity crawl of a specific URL to extract 
    noise-free, legal-focused Markdown.
    """
    extractor = PolicyExtractor()
    content = await extractor.extract_markdown(url)

    if not content:
        return f"Error: Could not extract content from {url}"

    return content


# 4. Register Validator Tool (Class-based now)
@mcp.tool()
async def validate_site_access(url: str) -> dict:
    """
    Validates if a site is accessible and safe to crawl.
    """
    validator = SiteValidator()
    return await validator.validate(url)


# 5. Run Server
if __name__ == "__main__":
    mcp.run(transport="sse")