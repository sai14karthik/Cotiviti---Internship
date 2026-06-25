"""Keyword-based policy summarization."""

from __future__ import annotations

import re

from .text_utils import extract_metadata, split_paragraphs, split_sentences

KEYWORD_WEIGHTS = {
    "ncci": 3,
    "edit": 3,
    "ptp": 3,
    "mue": 3,
    "modifier": 2,
    "deny": 2,
    "denied": 2,
    "prepay": 2,
    "claim": 2,
    "code": 1,
    "medicare": 1,
    "revised": 3,
    "new": 2,
}


def _score_sentence(sentence: str) -> float:
    lower = sentence.lower()
    score = 0.0
    for word, weight in KEYWORD_WEIGHTS.items():
        if word in lower:
            score += weight
    if re.search(r"\b\d{5}\b", sentence):
        score += 2
    if "column one" in lower or "column two" in lower:
        score += 2
    if len(sentence) < 40:
        score -= 1
    return score


def summarize_policy(text: str, max_bullets: int = 6) -> dict:
    """Return a short bullet summary using keyword scoring."""
    meta = extract_metadata(text)
    paragraphs = split_paragraphs(text)
    scored: list[tuple[float, str]] = []

    for para in paragraphs:
        if para.startswith("SECTION") or para.startswith("MEDICARE"):
            continue
        for sentence in split_sentences(para):
            if sentence.startswith("  "):
                continue
            scored.append((_score_sentence(sentence), sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    seen: set[str] = set()
    bullets: list[str] = []
    for _, sentence in scored:
        key = sentence[:60]
        if key in seen:
            continue
        seen.add(key)
        bullets.append(sentence)
        if len(bullets) >= max_bullets:
            break

    ptp_count = len(re.findall(r"Edit NCCI-PTP", text, re.I))
    mue_count = len(re.findall(r"Code \d{5} — MUE:", text))

    return {
        "metadata": meta,
        "bullets": bullets,
        "stats": {
            "ptp_edits": ptp_count,
            "mue_rules": mue_count,
            "characters": len(text),
        },
        "method": "extractive keyword scoring (offline)",
    }
