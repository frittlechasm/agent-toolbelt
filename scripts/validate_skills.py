"""Discover skills and validate their required metadata."""

from __future__ import annotations

import re
from pathlib import Path


SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_METADATA = ("scope", "agents", "machines")


def skill_directories(skills_root: Path) -> list[Path]:
    """Return public and private skill directories in stable order."""
    roots = [skills_root]
    private = skills_root / "private"
    if private.is_dir():
        roots.append(private)

    skills = []
    for root in roots:
        skills.extend(
            path
            for path in root.iterdir()
            if path.is_dir() and path.name != "private" and (path / "SKILL.md").is_file()
        )
    return sorted(skills, key=lambda path: path.name)


def read_frontmatter(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Read the simple top-level fields used by this repository."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing YAML frontmatter delimiter") from error

    fields: dict[str, str] = {}
    metadata: dict[str, str] = {}
    in_metadata = False
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == "metadata:":
            in_metadata = True
            continue
        if in_metadata and line.startswith("  ") and ":" in line:
            key, value = line.strip().split(":", 1)
            metadata[key] = value.strip()
            continue
        if line.startswith(" "):
            continue
        in_metadata = False
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"invalid frontmatter line: {line}")
        fields[key] = value.strip()
    return fields, metadata


def validate_skills(repo_root: Path, skills_root: Path) -> tuple[list[Path], list[str]]:
    """Validate skill names and required SKILL.md fields."""
    errors: list[str] = []
    skills = skill_directories(skills_root)
    names = set()

    for skill in skills:
        relative = skill.relative_to(repo_root)
        if not SKILL_NAME.fullmatch(skill.name):
            errors.append(f"{relative}: invalid skill directory name")
        if skill.name in names:
            errors.append(f"{relative}: duplicate skill name")
        names.add(skill.name)

        try:
            fields, metadata = read_frontmatter(skill / "SKILL.md")
        except (OSError, ValueError) as error:
            errors.append(f"{relative}/SKILL.md: {error}")
            continue

        if fields.get("name") != skill.name:
            errors.append(f"{relative}/SKILL.md: name must be {skill.name!r}")
        if not fields.get("description"):
            errors.append(f"{relative}/SKILL.md: description is required")
        missing_metadata = [key for key in REQUIRED_METADATA if not metadata.get(key)]
        if missing_metadata:
            errors.append(f"{relative}/SKILL.md: missing metadata: {', '.join(missing_metadata)}")

    return skills, errors
