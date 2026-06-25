"""Compare two policy versions."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass


@dataclass
class PolicyChange:
    change_type: str
    detail: str
    old_value: str | None = None
    new_value: str | None = None


def line_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="previous_policy",
        tofile="updated_policy",
        lineterm="",
    )
    return "\n".join(diff)


def detect_structured_changes(old_text: str, new_text: str) -> list[PolicyChange]:
    changes: list[PolicyChange] = []

    old_edits = set(re.findall(r"Edit (NCCI-PTP-\d+)", old_text, re.I))
    new_edits = set(re.findall(r"Edit (NCCI-PTP-\d+)", new_text, re.I))
    for edit_id in sorted(new_edits - old_edits):
        changes.append(
            PolicyChange("NEW_PTP_EDIT", f"Added {edit_id}", None, edit_id)
        )
    for edit_id in sorted(old_edits - new_edits):
        changes.append(
            PolicyChange("REMOVED_PTP_EDIT", f"Removed {edit_id}", edit_id, None)
        )

    mue_pattern = re.compile(
        r"Code (\d{5}) — MUE: (\d+) unit[s]? per date of service[^(\n]*(?:\(REVISED from (\d+) unit[s]?\))?",
        re.I,
    )
    old_mues = {m.group(1): m.group(2) for m in mue_pattern.finditer(old_text)}
    new_mues = {m.group(1): m.group(2) for m in mue_pattern.finditer(new_text)}

    for code in sorted(set(old_mues) | set(new_mues)):
        old_val = old_mues.get(code)
        new_val = new_mues.get(code)
        if old_val != new_val:
            changes.append(
                PolicyChange(
                    "MUE_CHANGE",
                    f"MUE limit changed for CPT/HCPCS {code}",
                    f"{old_val} units/day" if old_val else None,
                    f"{new_val} units/day" if new_val else None,
                )
            )

    if "XE, XP, XS, or XU" in new_text and "XE, XP, XS, or XU" not in old_text:
        changes.append(
            PolicyChange(
                "MODIFIER_GUIDANCE",
                "Expanded modifier list (added XP, XS, XU)",
                "Modifier 59 or XE",
                "Modifier 59, XE, XP, XS, or XU",
            )
        )

    old_version = _extract_version(old_text)
    new_version = _extract_version(new_text)
    if old_version and new_version and old_version != new_version:
        changes.append(
            PolicyChange(
                "VERSION_BUMP",
                "Policy version updated",
                old_version,
                new_version,
            )
        )

    return changes


def _extract_version(text: str) -> str | None:
    for line in text.splitlines()[:5]:
        if "Version:" in line:
            return line.split("Version:")[-1].strip()
    return None
