from pathlib import Path

from app.skills.manager import SkillManager

SKILLS_DIR = Path(__file__).parent.parent.parent / "app" / "skills"


class TestSkillManager:
    def setup_method(self) -> None:
        self.manager = SkillManager(SKILLS_DIR)

    def test_loads_skills(self) -> None:
        assert len(self.manager.skills) >= 10

    def test_index_not_empty(self) -> None:
        assert "Available Skills" in self.manager.index

    def test_get_skill_by_name(self) -> None:
        skill = self.manager.get_skill("crime-statistics-by-district")
        assert skill is not None
        assert skill.name == "crime-statistics-by-district"

    def test_get_nonexistent_skill(self) -> None:
        assert self.manager.get_skill("nonexistent") is None

    def test_find_for_query(self) -> None:
        skill = self.manager.find_for_query("crime statistics")
        assert skill is not None

    def test_list_categories(self) -> None:
        categories = self.manager.list_categories()
        assert "query" in categories
        assert "analysis" in categories
        assert "network" in categories
        assert "reporting" in categories
