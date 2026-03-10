from fastapi import FastAPI
from api.endpoints import scan, user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Privacy Guardian Gateway")

# Essential for Chrome Extensions!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your extension ID
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api/v1", tags=["Scanning"])
# app.include_router(user.router, prefix="/api/v1", tags=["User"])

@app.get("/health")
async def health():
    return {"status": "healthy"}