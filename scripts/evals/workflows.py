"""Prepare isolated workspaces for model-neutral workflow evaluations."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


RUN_METADATA_FORMAT = {
    "model": "string",
    "reasoning_effort": "string",
    "capabilities": "string_list",
}
CASE_RESULT_FORMAT = {
    "skill_name": "string",
    "case_id": "integer",
    "status": ["passed", "failed", "skipped"],
    "reason": "string",
    "unmet_expectations": "string_list",
    "evidence": "string_list",
}


def load_cases(skill: Path, case_ids: list[int] | None) -> list[dict[str, Any]]:
    path = skill / "evals" / "evals.json"
    cases = json.loads(path.read_text(encoding="utf-8"))["evals"]
    if case_ids is None:
        return cases
    selected = [case for case in cases if case["id"] in case_ids]
    missing = sorted(set(case_ids) - {case["id"] for case in selected})
    if missing:
        raise RuntimeError(f"{skill.name}: unknown case ids: {', '.join(map(str, missing))}")
    return selected


def eval_resource(skill: Path, relative: str) -> Path:
    eval_root = (skill / "evals").resolve()
    resource = (eval_root / relative).resolve()
    if eval_root not in resource.parents:
        raise RuntimeError(f"resource must stay under {eval_root}: {relative!r}")
    return resource


def prepare_workspace(skill: Path, case: dict[str, Any], workspace: Path) -> None:
    fixture = case.get("fixture")
    if fixture is not None:
        source = eval_resource(skill, fixture)
        if not source.is_dir():
            raise RuntimeError(f"case {case['id']}: fixture directory was not found: {fixture}")
        shutil.copytree(source, workspace, dirs_exist_ok=True)

    setup = case.get("setup")
    if setup is None:
        return
    script = eval_resource(skill, setup[0])
    if not script.is_file():
        raise RuntimeError(f"case {case['id']}: setup script was not found: {setup[0]}")
    try:
        result = subprocess.run(
            [sys.executable, str(script), *setup[1:], str(workspace)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"case {case['id']}: fixture setup exceeded 60s") from error
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        raise RuntimeError(f"case {case['id']}: fixture setup failed: {detail}")


def fixture_commands(workspace: Path) -> dict[str, str]:
    fixture_bin = workspace / ".eval" / "bin"
    if not fixture_bin.is_dir():
        return {}
    return {
        path.name: str(path)
        for path in sorted(fixture_bin.iterdir())
        if path.is_file() and os.access(path, os.X_OK)
    }


def sandbox_writable_paths(workspace: Path) -> list[str]:
    """Return the workspace roots that a subject sandbox must permit."""
    paths = [str(workspace)]
    git_metadata = workspace / ".git"
    if git_metadata.exists():
        paths.append(str(git_metadata))
    return paths


def build_workflow_manifest(skills: list[Path], case_ids: list[int] | None) -> dict[str, Any]:
    cases = []
    workspaces = []
    try:
        for skill in skills:
            for case in load_cases(skill, case_ids):
                workspace = Path(tempfile.mkdtemp(prefix=f"agent-toolbelt-{skill.name}-"))
                workspaces.append(workspace)
                prepare_workspace(skill, case, workspace)
                cases.append(
                    {
                        "skill_name": skill.name,
                        "case_id": case["id"],
                        "workspace": str(workspace),
                        "subject": {
                            "skill_file": str(skill / "SKILL.md"),
                            "prompt": case["prompt"],
                            "fixture_commands": fixture_commands(workspace),
                            "required_capabilities": case.get("capabilities", []),
                            "sandbox_writable_paths": sandbox_writable_paths(workspace),
                        },
                        "judge": {
                            "expected_output": case["expected_output"],
                            "expectations": case["expectations"],
                        },
                    }
                )
    except Exception:
        for workspace in workspaces:
            shutil.rmtree(workspace, ignore_errors=True)
        raise

    return {
        "eval_type": "workflows",
        "instructions": [
            "Run each subject in its workspace and load subject.skill_file before working.",
            "Record the subject model, reasoning effort, and available capabilities once per run.",
            (
                "Before running a case, compare subject.required_capabilities with the available "
                "capabilities; record the case as skipped when any requirement is unavailable."
            ),
            "Give the subject only subject, workspace, and these instructions, never judge.",
            (
                "Keep all writes inside the workspace and configure every "
                "subject.sandbox_writable_paths entry as writable; Git workspaces require the explicit "
                ".git entry because ordinary workspace-write sandboxes may protect Git metadata."
            ),
            "When fixture_commands is non-empty, invoke those exact paths for matching commands.",
            "After the subject finishes, inspect its response, command evidence, and workspace.",
            "Pass only when every material judge expectation is satisfied.",
            "Remove every listed workspace after recording the result.",
        ],
        "run_metadata_format": RUN_METADATA_FORMAT,
        "case_result_format": CASE_RESULT_FORMAT,
        "cases": cases,
    }
