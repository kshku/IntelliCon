from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Skill:
    name: str
    description: str
    triggers: list[str] = field(default_factory=list)
    tools_required: list[str] = field(default_factory=list)
    category: str = "general"
    content: str = ""
    path: Path | None = None


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_skill_file(file_path: Path) -> Skill | None:
    if not file_path.exists() or not file_path.suffix == ".md":
        return None

    raw = file_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        return None

    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(meta, dict) or "name" not in meta:
        return None

    content = raw[match.end() :]

    category = file_path.parent.name
    if category == "skills":
        category = "general"

    return Skill(
        name=meta["name"],
        description=meta.get("description", ""),
        triggers=meta.get("triggers", []),
        tools_required=meta.get("tools_required", []),
        category=category,
        content=content.strip(),
        path=file_path,
    )


def load_all_skills(skills_dir: Path) -> list[Skill]:
    skills: list[Skill] = []
    if not skills_dir.exists():
        return skills

    for md_file in sorted(skills_dir.rglob("*.md")):
        skill = parse_skill_file(md_file)
        if skill is not None:
            skills.append(skill)

    return skills


def get_skill_index(skills: list[Skill]) -> str:
    if not skills:
        return ""

    lines = ["## Available Skills", ""]
    by_category: dict[str, list[Skill]] = {}
    for skill in skills:
        by_category.setdefault(skill.category, []).append(skill)

    for category, cat_skills in sorted(by_category.items()):
        lines.append(f"### {category.replace('_', ' ').title()}")
        for skill in cat_skills:
            lines.append(f"- **{skill.name}**: {skill.description}")
        lines.append("")

    return "\n".join(lines)


def find_skill_by_query(skills: list[Skill], query: str) -> Skill | None:
    query_lower = query.lower()
    best_match: Skill | None = None
    best_score = 0

    for skill in skills:
        score = 0
        for trigger in skill.triggers:
            if trigger.lower() in query_lower:
                score += 2
        for word in skill.name.lower().split("-"):
            if word in query_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_match = skill

    return best_match if best_score > 0 else None
