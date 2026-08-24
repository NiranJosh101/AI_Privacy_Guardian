import uuid
from typing import Dict, Any, Optional
from enum import Enum
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
import httpx
import uvicorn

app = FastAPI(title="Privacy Guardian Gateway - HTTP Orchestrator")


# --- Configuration (Set Downstream Ports) ---
SERVICES = {
    "cache": "http://localhost:8007",
    "explorer": "http://localhost:8004",
    "interpreter": "http://localhost:8002",
    "judge": "http://localhost:8009",
}


# --- Schemas & Models ---
class ScanStage(str, Enum):
    IDLE = "IDLE"
    DISCOVERY = "DISCOVERY"
    REASONING = "REASONING"
    JUDGING = "JUDGING"
    COMPLETE = "COMPLETE"


class ScanRequest(BaseModel):
    userId: str = Field(..., example="user_123")
    url: str = Field(..., example="https://example.com")


class ScanStatusResponse(BaseModel):
    jobId: str
    status: ScanStage
    result: Optional[Dict[str, Any]] = None


jobs: Dict[str, Dict[str, Any]] = {}


def sanitize_url(url: str) -> str:
    if not url.startswith(('http://', 'https://')):
        return f"http://{url}"
    return url


# --- Background Pipeline Worker ---
async def run_orchestration_chain(job_id: str, user_id: str, url: str):
    clean_url = sanitize_url(url)

    # Use long timeouts so delayed mock responses are respected
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # --------------------------------------------------
            # 1. CACHE CHECK
            # --------------------------------------------------
            print(f"💾 [Job {job_id}] Checking cache for {clean_url}...")
            cache_resp = await client.get(
                f"{SERVICES['cache']}/cache/site-profile",
                params={"domain": clean_url}
            )

            if cache_resp.status_code == 200:
                cache_data = cache_resp.json()
                if cache_data.get("found") and cache_data.get("site_profile"):
                    print(f"⚡ [Job {job_id}] CACHE HIT!")
                    site_profile = cache_data["site_profile"]

                    jobs[job_id]["status"] = ScanStage.JUDGING
                    judge_resp = await client.post(
                        f"{SERVICES['judge']}/v1/evaluate",
                        json={"persona_id": user_id, "profile": site_profile}
                    )
                    jobs[job_id]["result"] = judge_resp.json()
                    jobs[job_id]["status"] = ScanStage.COMPLETE
                    return

            print(f"💨 [Job {job_id}] CACHE MISS - Starting discovery pipeline...")

            # --------------------------------------------------
            # 2. EXPLORER SERVICE
            # --------------------------------------------------
            jobs[job_id]["status"] = ScanStage.DISCOVERY
            print(f"🔍 [Job {job_id}] Calling Explorer Service ({SERVICES['explorer']})...")
            
            explorer_resp = await client.post(
                f"{SERVICES['explorer']}/explore",
                json={"url": clean_url}
            )
            explorer_resp.raise_for_status()
            explorer_data = explorer_resp.json()

            # --------------------------------------------------
            # 3. INTERPRETER / DNA SERVICE
            # --------------------------------------------------
            jobs[job_id]["status"] = ScanStage.REASONING
            print(f"🧬 [Job {job_id}] Calling Interpreter Service ({SERVICES['interpreter']})...")

            interpreter_resp = await client.post(
                f"{SERVICES['interpreter']}/v1/profile",
                json={
                    "base_url": explorer_data.get("base_url", clean_url),
                    "final_report": explorer_data.get("final_report", "")
                }
            )
            interpreter_resp.raise_for_status()
            site_profile = interpreter_resp.json()

            # Cache the newly generated profile
            await client.post(
                f"{SERVICES['cache']}/cache/site-profile",
                json={"domain": clean_url, "site_profile": site_profile}
            )

            # --------------------------------------------------
            # 4. JUDGE SERVICE
            # --------------------------------------------------
            jobs[job_id]["status"] = ScanStage.JUDGING
            print(f"⚖️ [Job {job_id}] Calling Judge Service ({SERVICES['judge']})...")

            judge_resp = await client.post(
                f"{SERVICES['judge']}/v1/evaluate",
                json={"persona_id": user_id, "profile": site_profile}
            )
            judge_resp.raise_for_status()
            final_verdict = judge_resp.json()

            # --------------------------------------------------
            # COMPLETE
            # --------------------------------------------------
            print(f"✅ [Job {job_id}] COMPLETE!")
            jobs[job_id]["result"] = final_verdict
            jobs[job_id]["status"] = ScanStage.COMPLETE

        except Exception as e:
            print(f"❌ [Job {job_id}] Pipeline Error: {str(e)}")
            jobs[job_id]["status"] = ScanStage.IDLE


# --- Routes ---
@app.post("/api/v1/scan", response_model=ScanStatusResponse)
async def start_scan(payload: ScanRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "jobId": job_id,
        "status": ScanStage.DISCOVERY,
        "result": None
    }

    background_tasks.add_task(
        run_orchestration_chain,
        job_id,
        payload.userId,
        payload.url
    )

    return jobs[job_id]


@app.get("/api/v1/status/{job_id}", response_model=ScanStatusResponse)
async def get_scan_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)