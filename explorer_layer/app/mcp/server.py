from typing import Dict, List, Any

from mcp.server.fastmcp import FastMCP

# Import tool logic (NOT decorators)
from app.mcp.tools.search import LinkScout
from app.mcp.tools.crawler import PolicyExtractor
from app.mcp.tools.validator import SiteValidator


# 1. Initialize ONE MCP Server
mcp = FastMCP("ExplorerTools", host="0.0.0.0", port=8008)


# 2. Register Scout Tool
@mcp.tool()
async def discover_regulatory_links(url: str) -> Dict[str, Any]:
    """
    Scans a website and returns a categorized map of legal/regulatory links.
    """
    scout = LinkScout()
    try:
        # Call the logic
        results = await scout.find_regulatory_suite(url)
        
        # DEBUG: Check if we actually have data before returning to MCP
        has_data = any(len(links) > 0 for links in results.values())
        print(f"--- DEBUG: MCP Tool Final Check - Data Found: {has_data} ---")
        
        # Ensure we return a clean dict that MCP can serialize
        return {
            "status": "success" if has_data else "no_links_found",
            "url": url,
            "categories": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "categories": {}}


# 3. Register Extractor Tool
@mcp.tool()
async def extract_policy_content(url: str) -> str:
    """
    Performs a high-fidelity crawl of a specific legal URL and 
    returns a clean Markdown version of the text content.
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