import os
import unittest
from pathlib import Path
from unittest.mock import patch
from buddy.datasets.migrate_division_lifecycle import (
 DivisionMigrationError,apply_division_lifecycle_migrations,build_migration_plan,migration_sha256,schema_name)

class FakeCursor:
 def __init__(self): self.last_query="";self.last_params=();self.executed=[]
 def __enter__(self): return self
 def __exit__(self,*_args): return False
 def execute(self,query,params=None):
  self.last_query=query;self.last_params=params or ();self.executed.append((query,params))
 def fetchone(self):
  if "pg_namespace" in self.last_query:
   name=self.last_params[0]
   return (name,False,False,False,True)
  if "SELECT migration_sha256" in self.last_query: return None
  return None

class FakeConnection:
 def __init__(self): self.cursor_obj=FakeCursor()
 def __enter__(self): return self
 def __exit__(self,*_args): return False
 def cursor(self): return self.cursor_obj

class DivisionLifecycleMigrationTests(unittest.TestCase):
 def test_plan_covers_all_65_schemas_and_rls_tables(self):
  plan=build_migration_plan()
  self.assertEqual(plan["division_count"],65)
  self.assertEqual(plan["schemas"][0],"dreamco_division_001")
  self.assertEqual(plan["schemas"][-1],"dreamco_division_065")
  self.assertGreater(plan["ddl_statements_per_schema"],40)
  self.assertEqual(len(plan["migration_sha256"]),64)
  self.assertEqual(plan["execution_status"],"DRY_RUN_ONLY")
 def test_schema_name_rejects_invalid_ids(self):
  self.assertEqual(schema_name(7),"dreamco_division_007")
  for value in (0,66,True,"1"):
   with self.assertRaises(DivisionMigrationError): schema_name(value)
 def test_apply_requires_runtime_opt_in(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaisesRegex(DivisionMigrationError,"ALLOW_DIVISION_SCHEMA_MIGRATIONS"):
    apply_division_lifecycle_migrations("approval",migration_sha256(),dsn="postgresql://fake",connect=lambda *_a,**_k:None)
 def test_apply_requires_approval_and_exact_migration_hash(self):
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS":"1"},clear=True):
   with self.assertRaisesRegex(DivisionMigrationError,"approval_id"):
    apply_division_lifecycle_migrations("",migration_sha256(),dsn="postgresql://fake",connect=lambda *_a,**_k:None)
   with self.assertRaisesRegex(DivisionMigrationError,"sha256_mismatch"):
    apply_division_lifecycle_migrations("approval","0"*64,dsn="postgresql://fake",connect=lambda *_a,**_k:None)
 def test_apply_validates_all_schemas_and_writes_audit_evidence(self):
  connection=FakeConnection()
  def connect(_dsn,connect_timeout): self.assertEqual(connect_timeout,5);return connection
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS":"1"},clear=True):
   result=apply_division_lifecycle_migrations("owner-approved-change-001",migration_sha256(),
      dsn="postgresql://test",connect=connect)
  self.assertEqual(result["schemas_migrated"],65)
  self.assertEqual(result["status"],"APPLIED")
  audit_inserts=[(q,p) for q,p in connection.cursor_obj.executed if "audit_events" in q and "INSERT INTO" in q]
  self.assertEqual(len(audit_inserts),65)
  self.assertTrue(all(p[3]=="DIVISION_LIFECYCLE_SCHEMA_MIGRATION_APPLIED" for _q,p in audit_inserts))
  role_switches=[q for q,_p in connection.cursor_obj.executed if q.startswith("SET LOCAL ROLE")]
  role_resets=[q for q,_p in connection.cursor_obj.executed if q=="RESET ROLE"]
  self.assertEqual(len(role_switches),65)
  self.assertEqual(len(role_resets),65)
  self.assertFalse(result["credentials_emitted"])
 def test_missing_schema_aborts_transaction(self):
  connection=FakeConnection()
  original=connection.cursor_obj.fetchone
  def fetchone():
   if "pg_namespace" in connection.cursor_obj.last_query:
    name=connection.cursor_obj.last_params[0]
    if name=="dreamco_division_010": return None
   return original()
  connection.cursor_obj.fetchone=fetchone
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS":"1"},clear=True):
   with self.assertRaisesRegex(DivisionMigrationError,"schema_missing"):
    apply_division_lifecycle_migrations("approval",migration_sha256(),dsn="postgresql://test",connect=lambda *_a,**_k:connection)

if __name__=="__main__": unittest.main()
