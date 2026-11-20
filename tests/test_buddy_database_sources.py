from __future__ import annotations
import sqlite3
import tempfile
import unittest
from pathlib import Path
from buddy.datasets.database_sources import DatabaseSourceError, query_hash, snapshot_sqlite

class DatabaseSourceTests(unittest.TestCase):
    def test_sqlite_read_only_snapshot_requires_exact_allowlisted_query(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); db=root/"source.db"
            connection=sqlite3.connect(db)
            connection.execute("CREATE TABLE examples (id INTEGER, text TEXT)")
            connection.executemany("INSERT INTO examples VALUES (?,?)",[(1,"one"),(2,"two")])
            connection.commit(); connection.close()
            sql="SELECT id, text FROM examples LIMIT 10"
            result=snapshot_sqlite(db,sql,authorization_ref="consent-fixture-1",
                approved_query_sha256=query_hash(sql),output_path=root/"snapshot.jsonl")
            self.assertEqual(result["rows_exported"],2)
            self.assertTrue(result["query_only"])
            self.assertEqual(len((root/"snapshot.jsonl").read_text().splitlines()),2)

    def test_write_queries_and_unapproved_queries_are_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            db=Path(temp)/"source.db"; sqlite3.connect(db).close()
            with self.assertRaises(DatabaseSourceError):
                snapshot_sqlite(db,"DELETE FROM users LIMIT 1",authorization_ref="x",
                    approved_query_sha256=query_hash("DELETE FROM users LIMIT 1"),output_path=Path(temp)/"out.jsonl")
            sql="SELECT * FROM users LIMIT 10"
            with self.assertRaises(DatabaseSourceError):
                snapshot_sqlite(db,sql,authorization_ref="x",approved_query_sha256="bad",output_path=Path(temp)/"out.jsonl")

if __name__=="__main__":
    unittest.main()
