import uvicorn
from fastapi import FastAPI
from api.routes import router as interpreter_router

app = FastAPI(
    title="Privacy Guardian: Semantic Interpreter",
    description="RAG-based privacy policy analysis service",
    version="1.0.0"
)

# Include our modular routes
app.include_router(interpreter_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Liveness probe for Kubernetes/Docker."""
    return {"status": "healthy", "service": "interpreter"}

if __name__ == "__main__":
    # In production, you'd use a gunicorn/uvicorn worker setup
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)