from fastapi import FastAPI
from app.api.routes import router as evaluation_router
from telemetry import init_telemetry


app = FastAPI(
    title="Privacy Guardian - Judge Service",
    description="Rule engine for evaluating website privacy against user preferences.",
    version="1.0.0"
)


init_telemetry(app, "privacy-guardian-judge")



app.include_router(evaluation_router)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "judge-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8009, reload=True)