"""Runtime configuration, validated at startup."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    """Raised when a required configuration value is missing or invalid."""


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:  # fail fast rather than silently defaulting
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    """Application settings.

    Every value has a safe default so the prototype runs with no configuration and
    no API key, as the competition requires.
    """

    db_path: Path
    data_dir: Path
    # k-anonymity floor: an aggregated cell is suppressed below this many reports.
    k_anonymity_floor: int
    # Minimum cosine similarity for a claim match to be shown at all.
    match_min_similarity: float
    # Below this, the matcher abstains instead of guessing.
    match_abstain_below: float
    # Confidence floor below which the assistive classifier abstains.
    classifier_abstain_below: float
    # Requests per minute per client for write endpoints.
    write_rate_limit_per_minute: int
    # Maximum characters accepted for a free-text report body.
    max_report_chars: int


def _default_data_dir() -> Path:
    """Find the project data directory.

    The API is launched either from ``backend/`` or from the repository root, so we probe a
    short, explicit list of candidates and pick the first that exists. Failing that, we fall
    back to ``<repo>/data`` and create it.
    """
    here = Path(__file__).resolve()
    candidates = [
        Path(os.environ["SHAIDA_DATA_DIR"]) if os.environ.get("SHAIDA_DATA_DIR") else None,
        here.parents[2] / "data",  # <repo>/data when running from <repo>/backend/shdaida
        here.parents[1] / "data",  # <repo>/backend/data
        Path.cwd() / "data",
        Path.cwd().parent / "data",
    ]
    for candidate in candidates:
        if candidate is not None and (candidate / "official-synthetic").is_dir():
            return candidate
    for candidate in candidates:
        if candidate is not None and candidate.is_dir():
            return candidate
    return here.parents[2] / "data"


def load_settings() -> Settings:
    data_dir = _default_data_dir()
    db_path = Path(os.environ.get("SHAIDA_DB", data_dir / "shaida.sqlite3"))
    data_dir.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        db_path=db_path,
        data_dir=data_dir,
        k_anonymity_floor=_env_int("SHAIDA_K_ANONYMITY", 5),
        match_min_similarity=_env_float("SHAIDA_MATCH_MIN", 0.35),
        match_abstain_below=_env_float("SHAIDA_MATCH_ABSTAIN", 0.45),
        classifier_abstain_below=_env_float("SHAIDA_CLASSIFIER_ABSTAIN", 0.55),
        write_rate_limit_per_minute=_env_int("SHAIDA_WRITE_RATE_LIMIT", 60),
        max_report_chars=_env_int("SHAIDA_MAX_REPORT_CHARS", 2000),
    )

    if settings.k_anonymity_floor < 2:
        raise ConfigError("SHAIDA_K_ANONYMITY must be >= 2 to be meaningful")
    if not (0.0 < settings.match_abstain_below <= 1.0):
        raise ConfigError("SHAIDA_MATCH_ABSTAIN must be in (0, 1]")
    if settings.max_report_chars < 100:
        raise ConfigError("SHAIDA_MAX_REPORT_CHARS is implausibly small")

    return settings
