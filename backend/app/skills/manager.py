from __future__ import annotations

from pathlib import Path

from app.skills.loader import Skill, get_skill_index, load_all_skills

SKILLS_DIR = Path(__file__).parent


class SkillManager:
    def __init__(self, skills_dir: Path | None = None) -> None:
        self._dir = skills_dir or SKILLS_DIR
        self._skills: list[Skill] = []
        self._index: str = ""
        self.load()

    def load(self) -> None:
        self._skills = load_all_skills(self._dir)
        self._index = get_skill_index(self._skills)

    @property
    def index(self) -> str:
        return self._index

    @property
    def skills(self) -> list[Skill]:
        return list(self._skills)

    def get_skill(self, name: str) -> Skill | None:
        for skill in self._skills:
            if skill.name == name:
                return skill
        return None

    def find_for_query(self, query: str) -> Skill | None:
        from app.skills.loader import find_skill_by_query

        return find_skill_by_query(self._skills, query)

    def list_categories(self) -> list[str]:
        return sorted({s.category for s in self._skills})


skill_manager = SkillManager()
