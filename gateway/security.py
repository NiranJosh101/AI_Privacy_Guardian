import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# The Strategy: 
# If REDIS_URL is in your environment, use it for shared rate limiting.
# Otherwise, use In-Memory (lean for development).
redis_url = os.getenv("REDIS_URL")

if redis_url:
    # Production/Scale mode
    limiter = Limiter(key_func=get_remote_address, storage_uri=redis_url)
else:
    # Lean Development mode
    limiter = Limiter(key_func=get_remote_address)