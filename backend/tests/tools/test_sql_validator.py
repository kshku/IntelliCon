import pytest

from app.tools.sql_validator import SqlValidationError, validate_sql


class TestValidateSql:
    def test_valid_select(self):
        sql = "SELECT * FROM case_master"
        result = validate_sql(sql)
        assert result == "SELECT * FROM case_master"

    def test_select_with_join(self):
        sql = (
            "SELECT cm.case_no, u.unit_name "
            "FROM case_master cm "
            "JOIN unit u ON cm.police_station_id = u.unit_id"
        )
        result = validate_sql(sql)
        assert "JOIN" in result

    def test_select_with_where(self):
        sql = "SELECT case_no FROM case_master WHERE crime_no = 'Cr.No.123/2024'"
        result = validate_sql(sql)
        assert "WHERE" in result

    def test_select_with_aggregate(self):
        sql = "SELECT COUNT(*) FROM case_master"
        result = validate_sql(sql)
        assert "COUNT" in result

    def test_select_with_limit(self):
        sql = "SELECT * FROM case_master LIMIT 10"
        result = validate_sql(sql)
        assert "LIMIT 10" in result

    def test_reject_insert(self):
        with pytest.raises(SqlValidationError, match="Only SELECT"):
            validate_sql("INSERT INTO case_master (case_no) VALUES ('x')")

    def test_reject_update(self):
        with pytest.raises(SqlValidationError, match="Only SELECT"):
            validate_sql("UPDATE case_master SET case_no = 'x'")

    def test_reject_delete(self):
        with pytest.raises(SqlValidationError, match="Only SELECT"):
            validate_sql("DELETE FROM case_master")

    def test_reject_drop(self):
        with pytest.raises(SqlValidationError, match="Only SELECT"):
            validate_sql("DROP TABLE case_master")

    def test_reject_unknown_table(self):
        with pytest.raises(SqlValidationError, match="Unknown tables"):
            validate_sql("SELECT * FROM secret_data")

    def test_reject_comment_double_dash(self):
        with pytest.raises(SqlValidationError, match="comments"):
            validate_sql("SELECT * FROM case_master -- sneaky")

    def test_reject_comment_block(self):
        with pytest.raises(SqlValidationError, match="comments"):
            validate_sql("SELECT * FROM case_master /* sneaky */")

    def test_reject_semicolon(self):
        with pytest.raises(SqlValidationError, match="semicolons"):
            validate_sql("SELECT * FROM case_master; DROP TABLE case_master")

    def test_reject_empty(self):
        with pytest.raises(SqlValidationError, match="Empty"):
            validate_sql("")

    def test_reject_whitespace_only(self):
        with pytest.raises(SqlValidationError, match="Empty"):
            validate_sql("   ")

    def test_strips_trailing_semicolon(self):
        result = validate_sql("SELECT * FROM case_master;")
        assert result == "SELECT * FROM case_master"

    def test_multiple_tables_join(self):
        sql = (
            "SELECT cm.case_no, cc.category_name, u.unit_name "
            "FROM case_master cm "
            "JOIN case_category cc ON cm.case_category_id = cc.case_category_id "
            "JOIN unit u ON cm.police_station_id = u.unit_id"
        )
        result = validate_sql(sql)
        assert "case_category" in result
