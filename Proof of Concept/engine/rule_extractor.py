"""Pull structured rules from policy text."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass


@dataclass
class PTPRule:
    rule_id: str
    column_one: str
    column_two: str
    modifier_allowed: bool
    source_excerpt: str


@dataclass
class MUERule:
    code: str
    max_units_per_day: int
    source_excerpt: str


def extract_ptp_rules(text: str) -> list[PTPRule]:
    blocks = re.split(r"(?=Edit NCCI-PTP-\d+)", text, flags=re.I)
    rules: list[PTPRule] = []

    for block in blocks:
        id_match = re.search(r"Edit (NCCI-PTP-\d+)", block, re.I)
        if not id_match:
            continue
        col1 = re.search(r"Column One Code:\s*(\S+)", block, re.I)
        col2 = re.search(r"Column Two Code:\s*(\S+)", block, re.I)
        mod = re.search(r"Modifier Indicator:\s*(\d+)", block, re.I)
        if not (col1 and col2):
            continue
        excerpt = " ".join(block.split())[:220]
        rules.append(
            PTPRule(
                rule_id=id_match.group(1),
                column_one=col1.group(1),
                column_two=col2.group(1),
                modifier_allowed=bool(mod and mod.group(1) == "1"),
                source_excerpt=excerpt,
            )
        )
    return rules


def extract_mue_rules(text: str) -> list[MUERule]:
    rules: list[MUERule] = []
    pattern = re.compile(
        r"Code (\d{5}) — MUE: (\d+) unit[s]? per date of service[^\n]*",
        re.I,
    )
    for match in pattern.finditer(text):
        rules.append(
            MUERule(
                code=match.group(1),
                max_units_per_day=int(match.group(2)),
                source_excerpt=match.group(0).strip(),
            )
        )
    return rules


def rules_to_json(text: str) -> str:
    payload = {
        "ptp_edits": [asdict(r) for r in extract_ptp_rules(text)],
        "mue_edits": [asdict(r) for r in extract_mue_rules(text)],
    }
    return json.dumps(payload, indent=2)
