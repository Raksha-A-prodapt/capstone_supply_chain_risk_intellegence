"""
Main FastAPI Application Entrypoint
Configures CORS, registers API routers, and mounts static assets for the React UI.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config.settings import settings
from api.routes import router

app = FastAPI(
    title="AI-Powered Supply Chain Risk Intelligence Assistant",
    description="End-to-End Multi-Agent Supply Chain Risk Intelligence API with Deterministic Operations Research and Live Gateway LLM Synthesis",
    version="1.0.0"
)

# Enable CORS for local Vite development and frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)

# Mount HTML evaluation report directory
reports_dir = settings.REPORTS_DIR
if os.path.exists(reports_dir):
    app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")

# Serve Frontend static build if built
dist_dir = settings.BASE_DIR / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = dist_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.HOST, port=settings.PORT, reload=True)
