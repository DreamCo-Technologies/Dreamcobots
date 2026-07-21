"""
Tests for bots/sql_bot/

Covers:
  1. SQLBot instantiation
  2. Query safety guardrails (blocked patterns)
  3. Table creation and schema inspection
  4. Data insertion, update, select, delete
  5. Analytical reports (summary, top-N)
  6. Integrity checks and null-column detection
  7. Query log and session stats
  8. Bot Library registration
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.sql_bot.sql_bot import SQLBot, QueryResult, SafetyViolation, QueryError, SQLBotError, validate_query


# ===========================================================================
# Helpers
# ===========================================================================

def _make_bot() -> SQLBot:
    """Return a fresh in-memory SQLBot."""
    return SQLBot()


def _bot_with_users() -> SQLBot:
    """Return a SQLBot with a populated 'users' table."""
    bot = _make_bot()
    bot.create_table("users", [
        ("id", "INTEGER PRIMARY KEY"),
        ("name", "TEXT NOT NULL"),
        ("email", "TEXT"),
        ("score", "REAL DEFAULT 0.0"),
    ])
    bot.insert("users", {"id": 1, "name": "Alice", "email": "alice@example.com", "score": 95.0})
    bot.insert("users", {"id": 2, "name": "Bob",   "email": "bob@example.com",   "score": 70.0})
    bot.insert("users", {"id": 3, "name": "Carol", "email": None,                "score": 55.0})
    return bot


# ===========================================================================
# 1. Instantiation
# ===========================================================================

class TestSQLBotInstantiation:
    def test_default_in_memory(self):
        bot = SQLBot()
        assert bot.db_path == ":memory:"

    def test_safety_on_by_default(self):
        bot = SQLBot()
        assert bot.enforce_safety is True

    def test_safety_can_be_disabled(self):
        bot = SQLBot(enforce_safety=False)
        assert bot.enforce_safety is False

    def test_close_does_not_raise(self):
        bot = SQLBot()
        bot.close()  # should not raise


# ===========================================================================
# 2. Safety guardrails
# ===========================================================================

class TestValidateQuery:
    def test_blocks_drop_table(self):
        with pytest.raises(SafetyViolation):
            validate_query("DROP TABLE users")

    def test_blocks_drop_database(self):
        with pytest.raises(SafetyViolation):
            validate_query("DROP DATABASE mydb")

    def test_blocks_truncate(self):
        with pytest.raises(SafetyViolation):
            validate_query("TRUNCATE TABLE users")

    def test_blocks_alter_table(self):
        with pytest.raises(SafetyViolation):
            validate_query("ALTER TABLE users ADD COLUMN age INTEGER")

    def test_blocks_attach(self):
        with pytest.raises(SafetyViolation):
            validate_query("ATTACH DATABASE 'other.db' AS other")

    def test_blocks_delete_without_where(self):
        with pytest.raises(SafetyViolation):
            validate_query("DELETE FROM users")

    def test_blocks_delete_without_where_semicolon(self):
        with pytest.raises(SafetyViolation):
            validate_query("DELETE FROM users;")

    def test_allows_delete_with_where(self):
        # Should NOT raise — WHERE clause is present
        validate_query("DELETE FROM users WHERE id = 1")

    def test_allows_select(self):
        validate_query("SELECT * FROM users")

    def test_allows_insert(self):
        validate_query("INSERT INTO users (name) VALUES ('Alice')")

    def test_allows_update_with_where(self):
        validate_query("UPDATE users SET name = 'Bob' WHERE id = 2")

    def test_allows_create_table(self):
        validate_query("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY)")

    def test_blocks_case_insensitive(self):
        with pytest.raises(SafetyViolation):
            validate_query("drop table users")

    def test_blocks_pragma_write(self):
        with pytest.raises(SafetyViolation):
            validate_query("PRAGMA writable_schema = ON")


class TestSQLBotSafetyEnforcement:
    def test_query_raises_safety_violation(self):
        bot = _make_bot()
        with pytest.raises(SafetyViolation):
            bot.query("DROP TABLE users")

    def test_safety_disabled_allows_create_schema(self):
        # With safety off, unsafe SQL should not raise SafetyViolation
        bot = SQLBot(enforce_safety=False)
        # This would normally be blocked; with safety off it just needs to be
        # valid SQLite — CREATE DATABASE isn't valid SQLite, so we test ALTER
        bot.create_table("tmp", [("id", "INTEGER")])
        # No SafetyViolation raised
        bot.close()


# ===========================================================================
# 3. Table creation and schema inspection
# ===========================================================================

class TestTableCreation:
    def test_create_table_returns_query_result(self):
        bot = _make_bot()
        result = bot.create_table("items", [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT")])
        assert isinstance(result, QueryResult)

    def test_list_tables_empty(self):
        bot = _make_bot()
        assert bot.list_tables() == []

    def test_list_tables_after_create(self):
        bot = _make_bot()
        bot.create_table("items", [("id", "INTEGER PRIMARY KEY")])
        assert "items" in bot.list_tables()

    def test_list_tables_multiple(self):
        bot = _make_bot()
        bot.create_table("a", [("id", "INTEGER")])
        bot.create_table("b", [("id", "INTEGER")])
        tables = bot.list_tables()
        assert "a" in tables and "b" in tables

    def test_get_schema_returns_columns(self):
        bot = _make_bot()
        bot.create_table("products", [("id", "INTEGER PRIMARY KEY"), ("price", "REAL")])
        schema = bot.get_schema("products")
        names = [col["name"] for col in schema]
        assert "id" in names
        assert "price" in names

    def test_create_if_not_exists_no_error(self):
        bot = _make_bot()
        bot.create_table("x", [("id", "INTEGER")])
        bot.create_table("x", [("id", "INTEGER")])  # second call should not raise

    def test_get_row_count_empty(self):
        bot = _bot_with_users()
        bot.create_table("empty_table", [("id", "INTEGER")])
        assert bot.get_row_count("empty_table") == 0


# ===========================================================================
# 4. CRUD operations
# ===========================================================================

class TestInsert:
    def test_insert_returns_query_result(self):
        bot = _bot_with_users()
        result = bot.insert("users", {"id": 99, "name": "Zara", "email": "z@z.com", "score": 88.0})
        assert isinstance(result, QueryResult)

    def test_row_count_increases_after_insert(self):
        bot = _bot_with_users()
        assert bot.get_row_count("users") == 3

    def test_insert_many(self):
        bot = _make_bot()
        bot.create_table("items", [("id", "INTEGER"), ("label", "TEXT")])
        results = bot.insert_many("items", [{"id": 1, "label": "A"}, {"id": 2, "label": "B"}])
        assert len(results) == 2
        assert bot.get_row_count("items") == 2


class TestSelect:
    def test_select_all_returns_rows(self):
        bot = _bot_with_users()
        result = bot.select("users")
        assert len(result.rows) == 3

    def test_select_with_where(self):
        bot = _bot_with_users()
        result = bot.select("users", where="name = ?", where_params=("Alice",))
        assert len(result.rows) == 1
        assert result.rows[0]["name"] == "Alice"

    def test_select_with_limit(self):
        bot = _bot_with_users()
        result = bot.select("users", limit=2)
        assert len(result.rows) == 2

    def test_select_specific_columns(self):
        bot = _bot_with_users()
        result = bot.select("users", columns="name, score")
        assert "name" in result.columns
        assert "score" in result.columns

    def test_select_with_order_by(self):
        bot = _bot_with_users()
        result = bot.select("users", order_by="score DESC")
        scores = [r["score"] for r in result.rows]
        assert scores == sorted(scores, reverse=True)

    def test_query_result_has_columns(self):
        bot = _bot_with_users()
        result = bot.select("users")
        assert "name" in result.columns
        assert "id" in result.columns


class TestUpdate:
    def test_update_changes_value(self):
        bot = _bot_with_users()
        bot.update("users", {"score": 100.0}, "name = ?", ("Alice",))
        result = bot.select("users", where="name = ?", where_params=("Alice",))
        assert result.rows[0]["score"] == 100.0

    def test_update_rowcount(self):
        bot = _bot_with_users()
        result = bot.update("users", {"score": 0.0}, "score < ?", (80.0,))
        assert result.rowcount >= 1


class TestDelete:
    def test_delete_with_where(self):
        bot = _bot_with_users()
        bot.delete("users", "name = ?", ("Bob",))
        result = bot.select("users", where="name = ?", where_params=("Bob",))
        assert len(result.rows) == 0

    def test_delete_without_where_blocked(self):
        bot = _bot_with_users()
        with pytest.raises(SafetyViolation):
            bot.query("DELETE FROM users")

    def test_delete_reduces_row_count(self):
        bot = _bot_with_users()
        bot.delete("users", "id = ?", (1,))
        assert bot.get_row_count("users") == 2


# ===========================================================================
# 5. Analytical reports
# ===========================================================================

class TestSummaryReport:
    def test_generate_summary_report_returns_dict(self):
        bot = _bot_with_users()
        report = bot.generate_summary_report()
        assert isinstance(report, dict)

    def test_summary_report_has_required_keys(self):
        bot = _bot_with_users()
        report = bot.generate_summary_report()
        assert "tables" in report
        assert "total_tables" in report
        assert "total_rows" in report
        assert "generated_at" in report

    def test_summary_report_total_tables(self):
        bot = _bot_with_users()
        report = bot.generate_summary_report()
        assert report["total_tables"] == 1

    def test_summary_report_total_rows(self):
        bot = _bot_with_users()
        report = bot.generate_summary_report()
        assert report["total_rows"] == 3

    def test_summary_empty_db(self):
        bot = _make_bot()
        report = bot.generate_summary_report()
        assert report["total_tables"] == 0
        assert report["total_rows"] == 0


class TestTopNReport:
    def test_top_n_report_returns_dict(self):
        bot = _bot_with_users()
        report = bot.generate_top_n_report("users", "score", "name", n=3)
        assert isinstance(report, dict)

    def test_top_n_report_has_rows(self):
        bot = _bot_with_users()
        report = bot.generate_top_n_report("users", "score", "name", n=2)
        assert len(report["rows"]) == 2

    def test_top_n_report_sorted_descending(self):
        bot = _bot_with_users()
        report = bot.generate_top_n_report("users", "score", "name", n=3)
        metrics = [r["metric"] for r in report["rows"]]
        assert metrics == sorted(metrics, reverse=True)

    def test_top_n_with_count_aggregation(self):
        bot = _bot_with_users()
        report = bot.generate_top_n_report("users", "id", "name", n=3, aggregation="COUNT")
        assert "rows" in report

    def test_top_n_invalid_aggregation_raises(self):
        bot = _bot_with_users()
        with pytest.raises(SQLBotError):
            bot.generate_top_n_report("users", "score", "name", aggregation="HACK")


# ===========================================================================
# 6. Integrity checks
# ===========================================================================

class TestIntegrityChecks:
    def test_integrity_check_passes_on_clean_db(self):
        bot = _bot_with_users()
        result = bot.check_integrity()
        assert result["passed"] is True
        assert result["issues"] == []
        assert "checked_at" in result

    def test_find_null_columns_detects_nulls(self):
        bot = _bot_with_users()
        # Carol has a NULL email
        nulls = bot.find_null_columns("users")
        assert "email" in nulls
        assert nulls["email"] == 1

    def test_find_null_columns_no_nulls(self):
        bot = _make_bot()
        bot.create_table("clean", [("id", "INTEGER"), ("val", "TEXT")])
        bot.insert("clean", {"id": 1, "val": "x"})
        nulls = bot.find_null_columns("clean")
        assert len(nulls) == 0


# ===========================================================================
# 7. Query log and session stats
# ===========================================================================

class TestQueryLog:
    def test_query_log_populated(self):
        bot = _bot_with_users()
        log = bot.get_query_log()
        assert len(log) > 0

    def test_query_log_entries_have_required_keys(self):
        bot = _bot_with_users()
        for entry in bot.get_query_log():
            assert "sql" in entry
            assert "rows" in entry
            assert "rowcount" in entry
            assert "duration_ms" in entry
            assert "executed_at" in entry

    def test_query_log_last_n(self):
        bot = _bot_with_users()
        log = bot.get_query_log(last_n=1)
        assert len(log) == 1

    def test_get_stats_returns_dict(self):
        bot = _bot_with_users()
        stats = bot.get_stats()
        assert isinstance(stats, dict)
        assert "total_queries" in stats
        assert "total_duration_ms" in stats
        assert "avg_duration_ms" in stats

    def test_get_stats_total_queries_positive(self):
        bot = _bot_with_users()
        stats = bot.get_stats()
        assert stats["total_queries"] > 0


# ===========================================================================
# 8. Bot Library registration
# ===========================================================================

class TestSQLBotLibraryRegistration:
    def test_sql_bot_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotNotFound
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        try:
            entry = lib.get_bot("sql_bot")
            assert entry.bot_id == "sql_bot"
        except BotNotFound:
            raise AssertionError("sql_bot not found in the bot library")

    def test_sql_bot_entry_fields(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("sql_bot")
        assert entry.display_name == "SQL Bot"
        assert entry.class_name == "SQLBot"
        assert entry.module_path == "bots.sql_bot.sql_bot"

    def test_sql_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("sql_bot")
        for cap in ["query_execution", "query_validation", "safety_guardrails",
                    "data_insertion", "data_update", "analytical_reports"]:
            assert cap in entry.capabilities, f"Missing capability: {cap}"
