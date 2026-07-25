from pathlib import Path

from app.skills.loader import (
    find_skill_by_query,
    get_skill_index,
    load_all_skills,
    parse_skill_file,
)

SKILLS_DIR = Path(__file__).parent.parent.parent / "app" / "skills"


class TestParseSkillFile:
    def test_parse_valid_skill(self, tmp_path: Path) -> None:
        skill_file = tmp_path / "test-skill.md"
        skill_file.write_text(
            "---\n"
            "name: test-skill\n"
            "description: A test skill\n"
            "triggers:\n"
            "  - test\n"
            "  - demo\n"
            "tools_required:\n"
            "  - sql_query\n"
            "---\n"
            "# Test Skill\n\nThis is the content.\n"
        )
        skill = parse_skill_file(skill_file)
        assert skill is not None
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.triggers == ["test", "demo"]
        assert skill.tools_required == ["sql_query"]
        assert "Test Skill" in skill.content

    def test_parse_nonexistent_file(self, tmp_path: Path) -> None:
        skill_file = tmp_path / "nonexistent.md"
        assert parse_skill_file(skill_file) is None

    def test_parse_non_md_file(self, tmp_path: Path) -> None:
        skill_file = tmp_path / "test.txt"
        skill_file.write_text("---\nname: test\n---\n")
        assert parse_skill_file(skill_file) is None

    def test_parse_no_frontmatter(self, tmp_path: Path) -> None:
        skill_file = tmp_path / "no-frontmatter.md"
        skill_file.write_text("# Just a heading\n\nNo frontmatter here.\n")
        assert parse_skill_file(skill_file) is None

    def test_parse_invalid_yaml(self, tmp_path: Path) -> None:
        skill_file = tmp_path / "invalid.md"
        skill_file.write_text("---\ninvalid: yaml: content:\n---\n")
        assert parse_skill_file(skill_file) is None

    def test_parse_missing_name(self, tmp_path: Path) -> None:
        skill_file = tmp_path / "no-name.md"
        skill_file.write_text("---\ndescription: No name here\n---\n")
        assert parse_skill_file(skill_file) is None


class TestLoadAllSkills:
    def test_loads_skills_from_real_directory(self) -> None:
        skills = load_all_skills(SKILLS_DIR)
        assert len(skills) >= 10
        names = {s.name for s in skills}
        assert "crime-statistics-by-district" in names
        assert "trace-accused-network" in names
        assert "find-repeat-offenders" in names

    def test_loads_empty_directory(self, tmp_path: Path) -> None:
        skills = load_all_skills(tmp_path)
        assert skills == []

    def test_loads_nonexistent_directory(self, tmp_path: Path) -> None:
        skills = load_all_skills(tmp_path / "nonexistent")
        assert skills == []


class TestGetSkillIndex:
    def test_index_contains_skills(self) -> None:
        skills = load_all_skills(SKILLS_DIR)
        index = get_skill_index(skills)
        assert "Available Skills" in index
        assert "crime-statistics-by-district" in index

    def test_index_empty_for_no_skills(self) -> None:
        index = get_skill_index([])
        assert index == ""


class TestFindSkillByQuery:
    def setup_method(self) -> None:
        self.skills = load_all_skills(SKILLS_DIR)

    def test_finds_matching_skill(self) -> None:
        skill = find_skill_by_query(self.skills, "crime statistics in district")
        assert skill is not None
        assert skill.name == "crime-statistics-by-district"

    def test_returns_none_for_no_match(self) -> None:
        skill = find_skill_by_query(self.skills, "zzz no match xyz")
        assert skill is None

    def test_finds_network_skill(self) -> None:
        skill = find_skill_by_query(self.skills, "who is connected to John")
        assert skill is not None
        assert skill.name == "trace-accused-network"
