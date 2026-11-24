"""Approval-gated PostgreSQL migrations for the 65 division lifecycle schemas."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
from typing import Any,Callable

ROOT=Path(__file__).resolve().parents[2]
MIGRATION_PATH=ROOT/"database/migrations/001_division_model_lifecycle.sql"
MIGRATION_VERSION="001_division_model_lifecycle"

class DivisionMigrationError(RuntimeError):
    """A migration was blocked or could not be safely applied."""

def migration_sha256(path:Path=MIGRATION_PATH)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def schema_name(masterbot_id:int)->str:
    if isinstance(masterbot_id,bool) or not isinstance(masterbot_id,int) or not 1<=masterbot_id<=65:
        raise DivisionMigrationError("masterbot_id_must_be_between_1_and_65")
    return f"dreamco_division_{masterbot_id:03d}"

def build_migration_plan(path:Path=MIGRATION_PATH)->dict[str,Any]:
    template=path.read_text(encoding="utf-8")
    digest=migration_sha256(path)
    divisions=[]
    for masterbot_id in range(1,66):
        name=schema_name(masterbot_id)
        divisions.append({"masterbot_id":masterbot_id,"schema":name,
            "sql":template.replace("{schema}",f'"{name}"')})
    return {"schema":"dreamco.division_lifecycle_migration_plan.v1",
        "migration_version":MIGRATION_VERSION,"migration_sha256":digest,
        "division_count":65,"schemas":[x["schema"] for x in divisions],
        "ddl_statement_count":len(divisions),"execution_status":"DRY_RUN_ONLY",
        "production_database_changed":False}

def apply_division_lifecycle_migrations(approval_id:str,expected_migration_sha256:str,*,
        dsn:str|None=None,connect:Callable[...,Any]|None=None,path:Path=MIGRATION_PATH)->dict[str,Any]:
    if os.environ.get("DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS")!="1":
        raise DivisionMigrationError("set_DREAMCO_ALLOW_DIVISION_SCHEMA_MIGRATIONS=1_to_enable_migrations")
    if not approval_id.strip(): raise DivisionMigrationError("migration_approval_id_required")
    actual_hash=migration_sha256(path)
    if expected_migration_sha256!=actual_hash:
        raise DivisionMigrationError("expected_migration_sha256_mismatch")
    database_dsn=dsn or os.environ.get("DREAMCO_POSTGRES_DSN") or os.environ.get("DATABASE_URL")
    if not database_dsn: raise DivisionMigrationError("DREAMCO_POSTGRES_DSN_or_DATABASE_URL_required")
    if connect is None:
        try:
            import psycopg
        except ImportError as exc:
            raise DivisionMigrationError("install_psycopg_to_apply_postgres_migrations") from exc
        connect=psycopg.connect
    plan=build_migration_plan(path)
    applied=0;skipped=0
    try:
        with connect(database_dsn,connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                for masterbot_id in range(1,66):
                    schema=schema_name(masterbot_id)
                    cursor.execute("""SELECT r.rolname,r.rolcanlogin,r.rolsuper,
                        pg_has_role(current_user,r.oid,'MEMBER')
                        FROM pg_namespace n JOIN pg_roles r ON r.oid=n.nspowner
                        WHERE n.nspname=%s""",(schema,))
                    owner=cursor.fetchone()
                    if owner is None: raise DivisionMigrationError(f"division_schema_missing:{schema}")
                    if owner[0]!=schema or owner[1] is not False or owner[2] is not False or owner[3] is not True:
                        raise DivisionMigrationError(f"division_schema_owner_or_membership_invalid:{schema}")
                    quoted=f'"{schema}"'
                    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {quoted}.schema_migrations (
                        version text PRIMARY KEY,migration_sha256 char(64) NOT NULL,
                        applied_at timestamptz NOT NULL DEFAULT now())""")
                    cursor.execute(f"SELECT migration_sha256 FROM {quoted}.schema_migrations WHERE version=%s",(MIGRATION_VERSION,))
                    existing=cursor.fetchone()
                    if existing:
                        if str(existing[0]).strip()!=actual_hash:
                            raise DivisionMigrationError(f"migration_hash_conflict:{schema}")
                        skipped+=1
                        continue
                    sql=plan["schemas"] # schema list is evidence, not executable SQL
                    template=path.read_text(encoding="utf-8").replace("{schema}",quoted)
                    cursor.execute(template)
                    cursor.execute(f"""INSERT INTO {quoted}.schema_migrations
                        (version,migration_sha256) VALUES (%s,%s)""",(MIGRATION_VERSION,actual_hash))
                    applied+=1
    except DivisionMigrationError:
        raise
    except Exception as exc:
        raise DivisionMigrationError(f"postgres_migration_failed:{type(exc).__name__}") from None
    return {"schema":"dreamco.division_lifecycle_migration_evidence.v1",
        "migration_version":MIGRATION_VERSION,"migration_sha256":actual_hash,
        "approval_id":approval_id,"division_count":65,"schemas_migrated":applied,
        "schemas_already_current":skipped,"status":"APPLIED" if applied else "ALREADY_CURRENT",
        "credentials_emitted":False,"production_tables_created":bool(applied)}

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply",action="store_true",help="Apply the migration; default is a read-only plan.")
    parser.add_argument("--approval-id",default="")
    parser.add_argument("--expected-migration-sha256",default="")
    args=parser.parse_args()
    if not args.apply:
        print(json.dumps(build_migration_plan(),indent=2));return 0
    result=apply_division_lifecycle_migrations(args.approval_id,args.expected_migration_sha256)
    print(json.dumps(result,indent=2));return 0

if __name__=="__main__": raise SystemExit(main())
