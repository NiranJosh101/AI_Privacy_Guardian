from fastapi import FastAPI
from .api.evaluation import router as evaluation_router

app = FastAPI(
    title="Privacy Guardian - Judge Service",
    description="Rule engine for evaluating website privacy against user preferences.",
    version="1.0.0"
)

# Register the routes
app.include_router(evaluation_router)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "judge-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)