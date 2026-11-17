"""Local dashboard and GORGON job API."""
import json
from pathlib import Path
import subprocess
import sys
from threading import Lock, Thread
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from frogger import now, run_frogger

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
VERSION = "1.0.0"
TERMINAL = {"completed", "completed_with_errors", "failed"}

app = FastAPI(title="FROGGER API", version=VERSION)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
jobs = {}
lock = Lock()
picker_lock = Lock()


class JobRequest(BaseModel):
    folder: str
    destination: str
    operations: list[Literal["sort", "background_removal"]] = ["sort", "background_removal"]


class FolderPickerRequest(BaseModel):
    kind: Literal["source", "destination"]
    current: str = ""


@app.post("/api/folder-picker")
def pick_folder(request: FolderPickerRequest):
    if not picker_lock.acquire(blocking=False):
        raise HTTPException(409, "A folder picker is already open.")
    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "folder_picker.py"), request.kind, request.current],
            capture_output=True, encoding="utf-8", check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return {"path": json.loads(result.stdout)}
    except (OSError, subprocess.CalledProcessError, ValueError):
        raise HTTPException(500, "Could not open the system folder picker.") from None
    finally:
        picker_lock.release()


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return dict(bot_id="frogger", status="online", version=VERSION, gorgon_compatible=True)


def execute_job(job_id, folder, destination, operations):
    def update(event):
        if event["event"] != "job.finished":
            with lock:
                jobs[job_id].update({k: event[k] for k in ("phase", "progress", "status")})

    started = now()
    try:
        result = run_frogger(folder, on_event=update, job_id=job_id,
                             destination_folder=destination, operations=operations)
    except Exception as exc:
        with lock:
            phase = jobs[job_id]["phase"]
            progress = jobs[job_id]["progress"]
        result = dict(schema_version="1.0", bot_id="frogger", job_id=job_id, status="failed",
                      started_at=started, finished_at=now(), root=str(folder), phase=phase,
                      progress=progress, sorted=[], generated=[], skipped=[],
                      errors=[dict(file=str(folder), phase=phase, error=str(exc))])
    error = result["errors"][0]["error"] if result["status"] == "failed" else None
    try:
        REPORTS.mkdir(exist_ok=True)
        report_file = REPORTS / f"{job_id}.json"
        temporary = report_file.with_suffix(".tmp")
        try:
            temporary.write_text(json.dumps(result, indent=2), encoding="utf-8")
            temporary.replace(report_file)
        finally:
            temporary.unlink(missing_ok=True)
    except OSError as exc:
        error = f"Could not save report: {exc}"
        result["errors"].append(dict(file=str(REPORTS), phase="reporting", error=error))
        if result["status"] == "completed":
            result["status"] = "completed_with_errors"
    with lock:
        jobs[job_id].update(status=result["status"], progress=result["progress"],
                            phase=result["phase"], result=result)
        if error:
            jobs[job_id]["error"] = error


@app.post("/api/jobs", status_code=202)
def create_job(request: JobRequest):
    if not request.folder.strip():
        raise HTTPException(400, "Enter a source directory.")
    try:
        folder = Path(request.folder.strip()).expanduser()
        if not folder.is_absolute() or not folder.is_dir():
            raise ValueError
        folder = folder.resolve()
    except (OSError, RuntimeError, ValueError):
        raise HTTPException(400, "Enter an existing absolute folder path.") from None
    if not request.operations:
        raise HTTPException(400, "Select at least one operation.")
    try:
        candidate = Path(request.destination.strip()).expanduser()
        if not candidate.is_absolute() or not candidate.is_dir():
            raise ValueError
        destination = candidate.resolve()
    except (OSError, RuntimeError, ValueError):
        raise HTTPException(400, "Enter an existing absolute destination folder path.") from None
    job_id = str(uuid4())
    job = dict(job_id=job_id, bot_id="frogger", status="queued", phase="waiting", progress=0)
    with lock:
        if any(item["status"] not in TERMINAL for item in jobs.values()):
            raise HTTPException(409, "A FROGGER job is already running.")
        jobs[job_id] = dict(job)
    try:
        Thread(target=execute_job, args=(job_id, folder, destination, request.operations), daemon=True).start()
    except RuntimeError:
        with lock:
            jobs.pop(job_id, None)
        raise HTTPException(503, "Could not start the job worker.") from None
    return job


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    with lock:
        if job_id not in jobs:
            raise HTTPException(404, "Job not found.")
        return dict(jobs[job_id])


@app.get("/api/gorgon/status")
def gorgon_status():
    with lock:
        return dict(bot_id="frogger", status="online", jobs=[dict(job) for job in jobs.values()])
