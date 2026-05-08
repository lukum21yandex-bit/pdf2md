#!/usr/bin/env python3
"""
LlamaCloud PDF Parser Backend
Пакетная обработка PDF файлов через LlamaCloud API
"""

import os
import time
import asyncio
import json
import hashlib
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_cloud import LlamaCloud, AsyncLlamaCloud

# === Конфигурация ===
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
STATUS_FILE = BASE_DIR / "status.json"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Global state
client = None
async_client = None
jobs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler."""
    global client, async_client, jobs
    
    # Startup
    LLAMA_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not LLAMA_API_KEY:
        api_key_file = Path.home() / ".openclaw" / "llama-cloud-api-key.txt"
        if api_key_file.exists():
            LLAMA_API_KEY = api_key_file.read_text().strip()
    
    if not LLAMA_API_KEY:
        raise RuntimeError("LLAMA_CLOUD_API_KEY not set")
    
    client = LlamaCloud(api_key=LLAMA_API_KEY)
    async_client = AsyncLlamaCloud(api_key=LLAMA_API_KEY)
    load_status()
    
    yield
    
    # Shutdown
    save_status()


app = FastAPI(title="LlamaCloud PDF Parser", lifespan=lifespan, root_path="/parce", root_path_in_servers=False)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def process_file_async(file_path: Path, file_hash: str):
    """Process a single PDF file through LlamaParse."""
    global jobs
    
    try:
        # Update status: uploading
        jobs[file_hash]["status"] = "uploading"
        jobs[file_hash]["progress"] = 10
        jobs[file_hash]["message"] = "Загрузка файла на сервер..."
        save_status()

        # Upload file
        file_obj = await async_client.files.create(
            file=str(file_path),
            purpose="parse"
        )
        
        # Update status: parsing
        jobs[file_hash]["status"] = "parsing"
        jobs[file_hash]["progress"] = 30
        jobs[file_hash]["message"] = "Обработка документа..."
        save_status()

        # Parse document
        job = await async_client.parsing.create(
            tier="agentic",
            version="latest",
            file_id=file_obj.id,
        )

        # Wait for job completion
        max_wait = 300  # 5 minutes
        poll_interval = 5
        elapsed = 0
        
        while elapsed < max_wait:
            job_status = await async_client.parsing.get(job.id)
            
            if job_status.job.status == "SUCCESS":
                break
            elif job_status.job.status in ["FAILURE", "ERROR"]:
                error_msg = job_status.job.error_message or "Unknown error"
                raise Exception(f"Job failed: {error_msg}")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            # Update progress based on elapsed time
            progress = min(30 + int(elapsed / max_wait * 70), 95)
            jobs[file_hash]["progress"] = progress
            jobs[file_hash]["message"] = f"Обработка документа... {elapsed}s"
            save_status()

        # Get parsed result using parse with expand
        result = await async_client.parsing.parse(
            file_id=file_obj.id,
            tier="agentic",
            version="latest",
            expand=["markdown"]
        )

        # Save markdown output
        output_file = OUTPUT_DIR / f"{file_hash}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            # Combine all pages
            full_markdown = ""
            if result.markdown and hasattr(result.markdown, 'pages'):
                for page in result.markdown.pages:
                    full_markdown += page.markdown + "\n\n---\n\n"
            f.write(full_markdown)

        # Update status: completed
        jobs[file_hash]["status"] = "completed"
        jobs[file_hash]["progress"] = 100
        jobs[file_hash]["message"] = "Готово!"
        jobs[file_hash]["result"] = {
            "output_file": str(output_file),
            "page_count": len(result.markdown.pages) if result.markdown else 0,
            "timestamp": time.time()
        }
        save_status()

    except Exception as e:
        jobs[file_hash]["status"] = "error"
        jobs[file_hash]["progress"] = 0
        jobs[file_hash]["error"] = str(e)
        save_status()


def save_status():
    """Save current job status to file."""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def load_status():
    """Load job status from file."""
    global jobs
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
        except:
            jobs = {}


@app.get("/")
async def root():
    """Root endpoint - return status."""
    return {
        "service": "LlamaCloud PDF Parser",
        "version": "1.0",
        "jobs": len(jobs),
        "upload_dir": str(UPLOAD_DIR),
        "output_dir": str(OUTPUT_DIR)
    }


@app.get("/status")
async def get_status():
    """Get status of all jobs."""
    return {"jobs": jobs}


@app.get("/status/{file_hash}")
async def get_job_status(file_hash: str):
    """Get status of a specific job."""
    if file_hash not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[file_hash]


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a PDF file."""
    # Calculate hash before saving
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file with shortened filename
    safe_filename = file.filename
    if len(safe_filename) > 100:
        # Keep extension and truncate the name
        name_part = safe_filename.rsplit('.', 1)[0][:80]  # 80 chars for name
        ext = f'.{safe_filename.rsplit(".", 1)[1]}' if '.' in safe_filename else '.pdf'
        safe_filename = f"{name_part}{ext}"
    
    file_path = UPLOAD_DIR / f"{file_hash}_{safe_filename}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Use original filename for display, but save shortened version
    display_filename = file.filename
    
    # Create job entry with original filename
    jobs[file_hash] = {
        "filename": display_filename,
        "file_hash": file_hash,
        "status": "pending",
        "progress": 0,
        "message": "Ожидание обработки...",
        "timestamp": time.time()
    }
    save_status()
    
    # Process file asynchronously
    asyncio.create_task(process_file_async(file_path, file_hash))
    
    return {
        "file_hash": file_hash,
        "filename": file.filename,
        "status": "queued"
    }


@app.get("/download/{file_hash}")
async def download_result(file_hash: str):
    """Download processed markdown file."""
    if file_hash not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[file_hash]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="File not ready yet")
    
    output_file = Path(job["result"]["output_file"])
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_file,
        media_type="text/markdown",
        filename=f"{file_hash}.md"
    )


@app.delete("/cancel/{file_hash}")
async def cancel_job(file_hash: str):
    """Cancel a pending job."""
    if file_hash not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[file_hash]
    if job["status"] in ["completed", "error"]:
        raise HTTPException(status_code=400, detail="Job already completed or errored")
    
    job["status"] = "cancelled"
    job["progress"] = 0
    save_status()
    
    return {"status": "cancelled"}


@app.get("/ui", response_class=HTMLResponse)
async def ui():
    """Serve the HTML interface."""
    return HTMLResponse(content=open(BASE_DIR / "index.html").read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, proxy_headers=True, forwarded_allow_ips="*")
