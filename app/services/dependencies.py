from __future__ import annotations

import importlib
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyStatus:
    fastapi: bool
    yt_dlp: bool
    gtts: bool

    @property
    def ready_for_full_pipeline(self) -> bool:
        return self.fastapi and self.yt_dlp and self.gtts


def has_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def get_dependency_status() -> DependencyStatus:
    return DependencyStatus(
        fastapi=has_module("fastapi"),
        yt_dlp=has_module("yt_dlp"),
        gtts=has_module("gtts"),
    )
