from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.short_generator import ShortGenerator, ShortGenerationError
from app.services.summarizer import SummaryService
from app.services.youtube_service import YouTubeService, YouTubeServiceError

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="YouTube Long2Short Studio")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

youtube_service = YouTubeService()
summary_service = SummaryService()
short_generator = ShortGenerator(output_dir=OUTPUT_DIR, summary_service=summary_service)


class AnalyzeRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=120)
    min_duration_minutes: int = Field(default=10, ge=1, le=300)
    max_results: int = Field(default=8, ge=1, le=20)


class CreateShortRequest(BaseModel):
    video_url: str
    include_narration: bool = True
    custom_summary: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    index = STATIC_DIR / "index.html"
    return HTMLResponse(index.read_text(encoding="utf-8"))


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        videos = youtube_service.search_long_trending_videos(
            topic=req.topic,
            min_duration_minutes=req.min_duration_minutes,
            max_results=req.max_results,
        )
    except YouTubeServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"videos": videos}


@app.post("/api/create-short")
def create_short(req: CreateShortRequest):
    try:
        package = short_generator.create_short_package(
            video_url=req.video_url,
            include_narration=req.include_narration,
            custom_summary=req.custom_summary,
        )
    except (YouTubeServiceError, ShortGenerationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return package


@app.get("/downloads/{filename}")
def download(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path)
