"""Build model-neutral trigger evaluation manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from checks.validate_skills import read_frontmatter


POLICY_PATTERN = re.compile(r"^\s+allow_implicit_invocation:\s*(true|false)\s*$", re.MULTILINE)


def allows_implicit_invocation(skill: Path) -> bool:
    path = skill / "agents" / "openai.yaml"
    if not path.is_file():
        return True
    match = POLICY_PATTERN.search(path.read_text(encoding="utf-8"))
    return match is None or match.group(1) == "true"


def load_cases(skill: Path) -> list[dict[str, Any]]:
    path = skill / "evals" / "trigger-evals.json"
    return json.loads(path.read_text(encoding="utf-8"))["evals"]


def build_trigger_manifest(skills: list[Path]) -> dict[str, Any]:
    cases = []
    for skill in skills:
        fields, _ = read_frontmatter(skill / "SKILL.md")
        for case in load_cases(skill):
            cases.append(
                {
                    "skill": {
                        "name": skill.name,
                        "description": fields["description"],
                        "allow_implicit_invocation": allows_implicit_invocation(skill),
                    },
                    "subject_input": {
                        "id": case["id"],
                        "prompt": case["prompt"],
                    },
                    "expected": {"should_trigger": case["should_trigger"]},
                }
            )

    return {
        "eval_type": "triggers",
        "instructions": [
            "Use an isolated subject model when available.",
            "Give the subject only skill and subject_input, never expected.",
            "Ask whether the skill should be loaded before answering; do not answer the prompt.",
            "Compare each subject decision with expected and report every mismatch.",
        ],
        "result_format": {
            "id": "integer",
            "should_trigger": "boolean",
            "reason": "string",
        },
        "cases": cases,
    }
