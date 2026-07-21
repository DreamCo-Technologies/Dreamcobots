"""
DataEntry plugin for Buddy.

Provides data management capabilities:
  - In-memory record storage (rows with named fields)
  - CSV import / export
  - Basic search and filter

Register with the TaskEngine via ``register(engine)``.
"""

import csv
import io
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataStore:
    """Lightweight in-memory table of records.

    Records are stored as dicts with arbitrary string keys.
    """

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._records: List[Dict[str, Any]] = []
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record and return it (with auto-assigned ``_id``)."""
        record = {"_id": self._next_id, **data}
        self._records.append(record)
        self._next_id += 1
        logger.info("Inserted record _id=%d into '%s'", record["_id"], self.name)
        return record

    def all(self) -> List[Dict[str, Any]]:
        """Return all records."""
        return list(self._records)

    def find(self, **filters: Any) -> List[Dict[str, Any]]:
        """Return records matching all *filters* (AND semantics).

        Example::

            store.find(status="open", priority="high")
        """
        results = []
        for record in self._records:
            if all(str(record.get(k, "")).lower() == str(v).lower()
                   for k, v in filters.items()):
                results.append(record)
        return results

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Return records where *query* appears in any string field value."""
        q = query.lower()
        return [
            r for r in self._records
            if any(q in str(v).lower() for v in r.values())
        ]

    def update(self, record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update the record with *record_id* and return it, or ``None``."""
        for record in self._records:
            if record["_id"] == record_id:
                record.update(data)
                logger.info("Updated record _id=%d in '%s'", record_id, self.name)
                return record
        return None

    def delete(self, record_id: int) -> bool:
        """Delete the record with *record_id*. Returns ``True`` on success."""
        before = len(self._records)
        self._records = [r for r in self._records if r["_id"] != record_id]
        removed = before - len(self._records)
        if removed:
            logger.info("Deleted record _id=%d from '%s'", record_id, self.name)
        return bool(removed)

    def count(self) -> int:
        """Return the total number of records."""
        return len(self._records)

    # ------------------------------------------------------------------
    # CSV import / export
    # ------------------------------------------------------------------

    def to_csv(self) -> str:
        """Export all records to a CSV string."""
        if not self._records:
            return ""
        fieldnames = list(self._records[0].keys())
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(self._records)
        return buf.getvalue()

    def from_csv(self, csv_text: str) -> int:
        """Import records from a CSV string. Returns the number imported."""
        reader = csv.DictReader(io.StringIO(csv_text))
        count = 0
        for row in reader:
            self.insert(dict(row))
            count += 1
        logger.info("Imported %d records into '%s' from CSV.", count, self.name)
        return count


# ---------------------------------------------------------------------------
# Shared store registry
# ---------------------------------------------------------------------------

_stores: Dict[str, DataStore] = {}


def _get_store(name: str = "default") -> DataStore:
    if name not in _stores:
        _stores[name] = DataStore(name)
    return _stores[name]


# ---------------------------------------------------------------------------
# Task handlers
# ---------------------------------------------------------------------------


def handle_data_insert(params: Dict[str, Any]) -> Dict[str, Any]:
    store_name = params.get("store", "default")
    record_data = {k: v for k, v in params.items() if k != "store"}
    if not record_data:
        return {"success": False, "message": "No data fields provided."}
    store = _get_store(store_name)
    record = store.insert(record_data)
    return {
        "success": True,
        "message": f"Record inserted with id={record['_id']}.",
        "record": record,
    }


def handle_data_list(params: Dict[str, Any]) -> Dict[str, Any]:
    store_name = params.get("store", "default")
    store = _get_store(store_name)
    records = store.all()
    return {
        "success": True,
        "message": f"{len(records)} record(s) in store '{store_name}'.",
        "records": records,
    }


def handle_data_search(params: Dict[str, Any]) -> Dict[str, Any]:
    store_name = params.get("store", "default")
    query = params.get("query", "")
    store = _get_store(store_name)
    results = store.search(query)
    return {
        "success": True,
        "message": f"Found {len(results)} matching record(s).",
        "records": results,
    }


def handle_data_export_csv(params: Dict[str, Any]) -> Dict[str, Any]:
    store_name = params.get("store", "default")
    store = _get_store(store_name)
    csv_text = store.to_csv()
    return {
        "success": True,
        "message": f"Exported {store.count()} record(s) as CSV.",
        "csv": csv_text,
    }


def handle_data_import_csv(params: Dict[str, Any]) -> Dict[str, Any]:
    store_name = params.get("store", "default")
    csv_text = params.get("csv", "")
    if not csv_text:
        return {"success": False, "message": "No CSV data provided."}
    store = _get_store(store_name)
    count = store.from_csv(csv_text)
    return {"success": True, "message": f"Imported {count} record(s) from CSV."}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(engine: Any) -> None:
    """Register data entry capabilities with *engine*.

    Args:
        engine: :class:`~BuddyAI.task_engine.TaskEngine` instance.
    """
    engine.register_capability("data_insert", handle_data_insert)
    engine.register_capability("data_list", handle_data_list)
    engine.register_capability("data_search", handle_data_search)
    engine.register_capability("data_export_csv", handle_data_export_csv)
    engine.register_capability("data_import_csv", handle_data_import_csv)
    logger.info("DataEntry plugin registered.")
