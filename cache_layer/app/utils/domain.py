import re
from urllib.parse import urlparse


def normalize_domain(url: str) -> str:
    """
    Extracts and normalizes a domain from a full URL.
    Ensures consistent cache keys across all services.
    """

    if not url:
        raise ValueError("URL cannot be empty")

    # If it's already just a domain, handle it
    if "://" not in url:
        domain = url
    else:
        parsed = urlparse(url)
        domain = parsed.netloc

    # Remove common prefixes
    domain = domain.lower().strip()
    domain = domain.replace("www.", "")

    # Remove port if present (e.g. localhost:3000)
    domain = domain.split(":")[0]

    # Final cleanup (defensive)
    domain = re.sub(r"^https?://", "", domain)

    if not domain:
        raise ValueError(f"Invalid domain extracted from: {url}")

    return domain


def normalize_url_to_domain(url: str) -> str:
    """
    Alias for clarity in services.
    Same behavior, clearer intent depending on context.
    """
    return normalize_domain(url)