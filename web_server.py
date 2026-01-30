from fastapi import FastAPI, HTTPException, Body, Depends, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import subprocess
from pathlib import Path
from typing import List, Optional
import uvicorn
import secrets

app = FastAPI()

# Configuration
# AUTH_TOKEN = secrets.token_hex(16) # In a real app, generate once and save
AUTH_TOKEN = "nurali_dev_2026" # Simple token for now
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = BASE_DIR

# --- SECURITY ---
def verify_token(x_token: str = Header(...)):
    if x_token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/", response_class=HTMLResponse)
async def get_ide():
    ide_path = BASE_DIR / "assets" / "ide_index.html"
    if ide_path.exists():
        return ide_path.read_text(encoding="utf-8")
    return "<h1>IDE Frontend not found!</h1>"

@app.get("/api/files")
async def list_files(token: str = Depends(verify_token)):
    files = []
    for f in PROJECT_DIR.glob("**/*"):
        if ".git" in str(f) or "__pycache__" in str(f) or "build" in str(f) or "dist" in str(f):
            continue
        if f.is_file():
            files.append(str(f.relative_to(PROJECT_DIR)))
    return sorted(files)

@app.get("/api/file/{path:path}")
async def read_file(path: str, token: str = Depends(verify_token)):
    full_path = PROJECT_DIR / path
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        return {"content": full_path.read_text(encoding="utf-8")}
    except Exception as e:
        return {"content": f"Binary or unreadable file: {str(e)}"}

@app.post("/api/save")
async def save_file(path: str = Body(...), content: str = Body(...), token: str = Depends(verify_token)):
    full_path = PROJECT_DIR / path
    try:
        full_path.write_text(content, encoding="utf-8")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/git/push")
async def git_push(message: str = Body(...), token: str = Depends(verify_token)):
    try:
        # Check for git
        subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True)
        result = subprocess.run(["git", "push"], cwd=PROJECT_DIR, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr or str(e)}

@app.get("/api/system/logs")
async def get_logs(token: str = Depends(verify_token)):
    # Assuming logs are kept in a local file or we just return some status for now
    # In a real app we'd read from SystemBot logs
    log_file = PROJECT_DIR / "system_manager.log"
    if log_file.exists():
        return {"logs": log_file.read_text(encoding="utf-8")[-5000:]} # Last 5000 chars
    return {"logs": "Hozircha loglar mavjud emas."}

@app.get("/api/system/status")
async def system_status(token: str = Depends(verify_token)):
    import psutil
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "time": os.popen("time /t").read().strip()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
