from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import yt_dlp


class YouTubeServiceError(Exception):
    pass


class YouTubeService:
    def __init__(self) -> None:
        self._base_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

    def _score(self, views: int, age_days: float, duration: int) -> float:
        freshness = 1 / max(age_days, 1)
        duration_bonus = min(duration / 3600, 3)
        return math.log10(max(views, 1)) * freshness * (1 + duration_bonus)

    def search_long_trending_videos(
        self,
        topic: str,
        min_duration_minutes: int = 10,
        max_results: int = 8,
    ) -> list[dict[str, Any]]:
        search_url = f"ytsearch{max_results * 4}:{topic}"
        with yt_dlp.YoutubeDL(self._base_opts) as ydl:
            try:
                data = ydl.extract_info(search_url, download=False)
            except Exception as exc:
                raise YouTubeServiceError(f"Erreur YouTube: {exc}") from exc

        now = datetime.now(timezone.utc)
        candidates: list[dict[str, Any]] = []
        for entry in data.get("entries", []):
            duration = entry.get("duration") or 0
            if duration < min_duration_minutes * 60:
                continue

            timestamp = entry.get("timestamp") or now.timestamp()
            published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            age_days = max((now - published_at).days, 1)

            views = entry.get("view_count") or 0
            score = self._score(views=views, age_days=age_days, duration=duration)
            candidates.append(
                {
                    "title": entry.get("title"),
                    "url": entry.get("webpage_url"),
                    "channel": entry.get("uploader"),
                    "duration_minutes": round(duration / 60, 1),
                    "views": views,
                    "published": published_at.date().isoformat(),
                    "score": round(score, 4),
                    "thumbnail": entry.get("thumbnail"),
                    "description": (entry.get("description") or "")[:1200],
                }
            )

        if not candidates:
            raise YouTubeServiceError("Aucune vidéo longue trouvée avec ces critères.")

        candidates.sort(key=lambda item: item["score"], reverse=True)
        return candidates[:max_results]

    def get_video_metadata(self, video_url: str) -> dict[str, Any]:
        with yt_dlp.YoutubeDL(self._base_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
            except Exception as exc:
                raise YouTubeServiceError(f"Impossible de charger la vidéo: {exc}") from exc

        duration = info.get("duration") or 0
        if duration < 60:
            raise YouTubeServiceError("La vidéo est trop courte pour générer un Short utile.")

        return {
            "title": info.get("title", "video"),
            "duration": duration,
            "description": info.get("description") or "",
            "url": info.get("webpage_url") or video_url,
        }
