# api/endpoints/scan.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.schemas import ScanRequest, ScanStatusResponse, ScanStage
from services.explorer_client import ExplorerClient
from services.interpreter_client import InterpreterClient
from services.judge_client import JudgeClient
from utils.db import db  # Direct DB lookup for Persona
import uuid

router = APIRouter()

# Clients Instance
explorer = ExplorerClient()
interpreter = InterpreterClient()
judge = JudgeClient()

# In-memory job store (Use Redis for K8s deployments)
jobs = {}

@router.post("/scan", response_model=ScanStatusResponse)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Initialize the job state
    jobs[job_id] = {
        "jobId": job_id,
        "status": ScanStage.DISCOVERY,
        "result": None
    }
    
    # Fire and forget the orchestration chain
    background_tasks.add_task(
        run_orchestration_chain, 
        job_id, 
        request.userId, 
        request.url
    )
    
    return jobs[job_id]

async def run_orchestration_chain(job_id: str, user_id: str, url: str):
    try:
        # 1. Identity Check (Local DB)
        persona = await db.get_persona_by_id(user_id)
        if not persona:
            jobs[job_id]["status"] = ScanStage.IDLE
            return

        # 2. Explorer (Discovery)
        jobs[job_id]["status"] = ScanStage.DISCOVERY
        explorer_data = await explorer.discover_site_content(url)

        # 3. Interpreter (Reasoning)
        jobs[job_id]["status"] = ScanStage.REASONING
        site_profile = await interpreter.extract_site_profile(explorer_data)

        # 4. Judge (Judging)
        jobs[job_id]["status"] = ScanStage.JUDGING
        final_verdict = await judge.generate_verdict(persona, site_profile)

        # 5. Complete
        jobs[job_id]["result"] = final_verdict
        jobs[job_id]["status"] = ScanStage.COMPLETE

    except Exception as e:
        print(f"Pipeline Error for job {job_id}: {str(e)}")
        jobs[job_id]["status"] = ScanStage.IDLE # Or add a FAILED stage

@router.get("/status/{job_id}", response_model=ScanStatusResponse)
async def get_scan_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]