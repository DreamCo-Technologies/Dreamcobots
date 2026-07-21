"""
dataset_normalizer.py — Dataset normalisation module.

Handles cleaning, schema harmonisation, and normalisation of raw datasets
ingested from multiple heterogeneous sources before they enter the
DreamCo learning pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NormalizedRecord:
    """A single record after normalisation."""

    source: str
    record_id: str
    features: Dict[str, Any] = field(default_factory=dict)
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatasetNormalizer:
    """
    Normalises raw datasets into a unified schema for the learning pipeline.

    Parameters
    ----------
    remove_nulls : bool
        When ``True``, records with any null feature are dropped.
    lowercase_keys : bool
        When ``True``, all feature keys are lower-cased during normalisation.
    """

    def __init__(self, remove_nulls: bool = True, lowercase_keys: bool = True):
        self.remove_nulls = remove_nulls
        self.lowercase_keys = lowercase_keys

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def normalize(self, raw_records: List[Dict[str, Any]], source: str) -> List[NormalizedRecord]:
        """
        Normalise a list of raw record dictionaries.

        Parameters
        ----------
        raw_records : list[dict]
            Raw data records to normalise.
        source : str
            Identifier of the originating data source.

        Returns
        -------
        list[NormalizedRecord]
        """
        normalised: List[NormalizedRecord] = []
        for idx, record in enumerate(raw_records):
            processed = self._process_record(record, source, idx)
            if processed is not None:
                normalised.append(processed)
        return normalised

    def normalize_schema(self, records: List[NormalizedRecord], schema: Dict[str, type]) -> List[NormalizedRecord]:
        """
        Coerce record features to the types specified in *schema*.

        Parameters
        ----------
        records : list[NormalizedRecord]
            Previously normalised records to coerce.
        schema : dict[str, type]
            Mapping of feature names to their expected Python types.

        Returns
        -------
        list[NormalizedRecord]
        """
        for record in records:
            for key, expected_type in schema.items():
                if key in record.features:
                    try:
                        record.features[key] = expected_type(record.features[key])
                    except (ValueError, TypeError):
                        record.features[key] = None
        return records

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_record(
        self,
        record: Dict[str, Any],
        source: str,
        idx: int,
    ) -> Optional[NormalizedRecord]:
        """Return a ``NormalizedRecord`` or ``None`` if the record is invalid."""
        features = {
            (k.lower() if self.lowercase_keys else k): v
            for k, v in record.items()
            if k not in ("label", "id", "_id")
        }

        if self.remove_nulls and any(v is None for v in features.values()):
            return None

        label = record.get("label")
        record_id = str(record.get("id") or record.get("_id") or f"{source}_{idx}")

        return NormalizedRecord(
            source=source,
            record_id=record_id,
            features=features,
            label=label,
            metadata={"original_index": idx},
        )
