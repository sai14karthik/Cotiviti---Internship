"""Policy text utilities."""

from __future__ import annotations

import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
CODE_PATTERN = re.compile(r"\b(\d{5}|[A-Z]\d{4})\b")
EDIT_ID_PATTERN = re.compile(r"Edit\s+(NCCI-PTP-\d+)", re.IGNORECASE)


def load_sample(name: str) -> str:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Sample not found: {path}")
    return path.read_text(encoding="utf-8")


def split_sentences(text: str) -> list[str]:
    chunks = SENTENCE_SPLIT.split(text.strip())
    return [c.strip() for c in chunks if c.strip()]


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def extract_metadata(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in text.splitlines()[:6]:
        if line.startswith("Effective Date:"):
            meta["effective_date"] = line.split(":", 1)[1].strip()
        elif line.startswith("Version:"):
            parts = line.split("|")
            if parts:
                meta["version"] = parts[-1].replace("Version:", "").strip()
    return meta
