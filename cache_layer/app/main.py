from fastapi import FastAPI
from app.telemetry import init_telemetry
from api.routes import router


app = FastAPI(
    title="Cache Service",
    description="Redis-backed caching layer for SiteProfile storage and retrieval",
    version="1.0.0"
)

init_telemetry(app, "privacy-guardian-cache")

# Register routes
app.include_router(router, prefix="/cache")


@app.get("/")
def root():
    return {
        "service": "cache-service",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007, reload=False)