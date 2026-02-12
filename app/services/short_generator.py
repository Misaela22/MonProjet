from __future__ import annotations

import re
import subprocess
import uuid
from pathlib import Path

import yt_dlp
from gtts import gTTS

from app.services.summarizer import SummaryService
from app.services.youtube_service import YouTubeService


class ShortGenerationError(Exception):
    pass


class ShortGenerator:
    def __init__(self, output_dir: Path, summary_service: SummaryService):
        self.output_dir = output_dir
        self.summary_service = summary_service
        self.youtube_service = YouTubeService()

    def _slug(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "video"

    def create_short_package(
        self,
        video_url: str,
        include_narration: bool = True,
        custom_summary: str | None = None,
    ) -> dict:
        meta = self.youtube_service.get_video_metadata(video_url)
        duration = meta["duration"]

        summary = custom_summary.strip() if custom_summary else self.summary_service.summarize(meta["description"])
        if len(summary) < 40:
            summary = f"Résumé: {summary}"

        base = f"{self._slug(meta['title'])}-{uuid.uuid4().hex[:8]}"
        source_file = self.output_dir / f"{base}-source.mp4"
        short_file = self.output_dir / f"{base}-short.mp4"
        summary_file = self.output_dir / f"{base}-resume.txt"
        narration_file = self.output_dir / f"{base}-narration.mp3"

        self._download_video(video_url, source_file)

        target_len = min(58, max(35, duration // 5))
        start = max(0, (duration // 2) - (target_len // 2))

        try:
            self._render_vertical_short(source_file, short_file, start, target_len)
            if include_narration:
                gTTS(summary, lang="fr").save(str(narration_file))
                self._replace_audio(short_file, narration_file)
            summary_file.write_text(summary, encoding="utf-8")
        except Exception as exc:
            raise ShortGenerationError(f"Erreur lors de la création du Short: {exc}") from exc
        finally:
            if source_file.exists():
                source_file.unlink(missing_ok=True)

        return {
            "title": meta["title"],
            "summary": summary,
            "short_download": f"/downloads/{short_file.name}",
            "summary_download": f"/downloads/{summary_file.name}",
            "narration_download": f"/downloads/{narration_file.name}" if include_narration else None,
        }

    def _download_video(self, video_url: str, output_file: Path) -> None:
        options = {
            "format": "best[ext=mp4]/best",
            "outtmpl": str(output_file),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])

        if not output_file.exists():
            raise ShortGenerationError("Téléchargement vidéo échoué.")

    def _render_vertical_short(self, source: Path, target: Path, start: int, duration: int) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start),
            "-i",
            str(source),
            "-t",
            str(duration),
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-c:a",
            "aac",
            str(target),
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def _replace_audio(self, target_video: Path, narration_audio: Path) -> None:
        out = target_video.with_name(target_video.stem + "-narrated.mp4")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(target_video),
            "-i",
            str(narration_audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-shortest",
            str(out),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        out.replace(target_video)
