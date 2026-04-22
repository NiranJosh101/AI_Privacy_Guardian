from fastapi import FastAPI
from api.endpoints import scan, user
from fastapi.middleware.cors import CORSMiddleware
from telemetry import init_telemetry

# Rate Limiting Imports
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from security import limiter 

app = FastAPI(title="Privacy Guardian Gateway")

# Initialize Telemetry
init_telemetry(app, "privacy-guardian-gateway")

# Setup Rate Limiting State & Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Standard Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(scan.router, prefix="/api/v1", tags=["Scanning"])
# app.include_router(user.router, prefix="/api/v1", tags=["User"])

@app.get("/health")
async def health():
    return {"status": "healthy"}