"""Run isolated Codex CLI calls for behavioral evals."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CodexError(RuntimeError):
    """Report a failed or malformed Codex eval call."""


@dataclass(frozen=True)
class CodexResult:
    final_response: str
    command_trace: str


def redact_command(command: str) -> str:
    """Remove common credential forms before a trace is sent to the judge."""
    command = re.sub(
        r"([A-Za-z][A-Za-z0-9+.-]*://[^:/\s]+:)[^@\s]+@",
        r"\1[REDACTED]@",
        command,
    )
    return re.sub(
        r"(?i)((?:token|password|secret|api[_-]?key)\s*[=:]\s*)\S+",
        r"\1[REDACTED]",
        command,
    )


def command_trace(output: str) -> str:
    """Keep completed command names and exit codes from Codex JSON events."""
    commands = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") != "item.completed" or item.get("type") != "command_execution":
            continue
        commands.append(
            f"exit={item.get('exit_code')} command={redact_command(item.get('command', ''))}"
        )
    return "\n".join(commands) or "No completed commands were recorded."


def invoke_with_trace(
    prompt: str,
    model: str,
    timeout: int,
    workspace: Path,
    sandbox: str,
    output_schema: dict[str, Any] | None = None,
    approve_for_me: bool = False,
) -> CodexResult:
    """Run one ephemeral Codex call and return its final message and command trace."""
    with tempfile.TemporaryDirectory(prefix="agent-toolbelt-eval-control-") as directory:
        control = Path(directory)
        output_path = control / "result.txt"
        command = [
            "codex",
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--color",
            "never",
            "--model",
            model,
        ]
        if approve_for_me:
            command.append("--approve-for-me")
        else:
            command.extend(("--sandbox", sandbox))
        if output_schema is not None:
            schema_path = control / "output-schema.json"
            schema_path.write_text(json.dumps(output_schema), encoding="utf-8")
            command.extend(("--output-schema", str(schema_path)))
        command.extend(("--output-last-message", str(output_path), "--cd", str(workspace), "-"))

        try:
            result = subprocess.run(
                command,
                input=prompt,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as error:
            raise CodexError(f"Codex exceeded the {timeout}s per-call timeout") from error
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
            raise CodexError(f"Codex exited {result.returncode}: {detail}")
        if not output_path.is_file():
            raise CodexError("Codex did not write a final response")
        return CodexResult(
            final_response=output_path.read_text(encoding="utf-8"),
            command_trace=command_trace(result.stdout),
        )


def invoke(
    prompt: str,
    model: str,
    timeout: int,
    workspace: Path,
    sandbox: str,
    output_schema: dict[str, Any] | None = None,
    approve_for_me: bool = False,
) -> str:
    """Run one ephemeral Codex call and return its final message."""
    return invoke_with_trace(
        prompt, model, timeout, workspace, sandbox, output_schema, approve_for_me
    ).final_response


def invoke_json(
    prompt: str,
    model: str,
    timeout: int,
    workspace: Path,
    sandbox: str,
    output_schema: dict[str, Any],
) -> dict[str, Any]:
    """Run one structured Codex call and decode its final response."""
    response = invoke(prompt, model, timeout, workspace, sandbox, output_schema)
    try:
        document = json.loads(response)
    except json.JSONDecodeError as error:
        raise CodexError(f"Codex returned invalid JSON: {error}") from error
    if not isinstance(document, dict):
        raise CodexError("Codex returned a non-object JSON response")
    return document
