import uvicorn
from fastapi import FastAPI
from api.routes import router as interpreter_router
from telemetry import init_telemetry

app = FastAPI(
    title="Privacy Guardian: Semantic Interpreter",
    description="RAG-based privacy policy analysis service",
    version="1.0.0"
)

init_telemetry(app, "privacy-guardian-interpreter")

# Include our modular routes
app.include_router(interpreter_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Liveness probe for Kubernetes/Docker."""
    return {"status": "healthy", "service": "interpreter"}


if __name__ == "__main__":
    import os
    # Render provides the PORT environment variable. 
    # We must bind to it, or the service will fail the health check.
    port = int(os.environ.get("PORT", 8002)) 
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False, 
        workers=1
    )