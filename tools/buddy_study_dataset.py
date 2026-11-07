"""Study an authorized local CSV/JSONL dataset without retaining raw values."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.learning.data_study import (  # noqa: E402
    DataStudyError,
    create_data_use_record,
    position_on_dataset_study,
    study_local_tabular_dataset,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Local UTF-8 CSV, JSONL, or NDJSON file")
    parser.add_argument("--owner-id", required=True)
    parser.add_argument("--buddy-id", required=True)
    parser.add_argument("--source-url", required=True, help="Credential-free HTTPS dataset card or source page")
    parser.add_argument("--source-family", required=True, help="For example hugging_face, government, research, or user_created")
    parser.add_argument("--license", required=True, dest="license_id")
    parser.add_argument("--rights-reviewed", action="store_true", help="Confirm rights for this exact data and requested private study")
    parser.add_argument("--terms-checked", action="store_true", help="Confirm source and repository terms were checked")
    parser.add_argument("--private-study", action="store_true", help="Explicitly authorize this local data quality study")
    parser.add_argument("--owner-created", action="store_true", help="Attest that the user created/owns the supplied dataset")
    parser.add_argument("--consent-receipt", default="", help="Local consent receipt identifier; required for user-created data")
    args = parser.parse_args()
    if not args.private_study:
        parser.error("--private-study is required; no dataset is read without an explicit study grant")
    try:
        if args.dataset.is_symlink() or not args.dataset.is_file():
            raise DataStudyError("Choose a regular local dataset file, not a symlink or directory.")
        if args.dataset.stat().st_size > 20_000_000:
            raise DataStudyError("Dataset exceeds the configured 20 MB limit.")
        checksum = hashlib.sha256()
        with args.dataset.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                checksum.update(chunk)
        digest = checksum.hexdigest()
        grant = create_data_use_record(
            owner_user_id=args.owner_id, buddy_instance_id=args.buddy_id,
            dataset_sha256=digest, source_url=args.source_url, source_family=args.source_family,
            license_id=args.license_id, user_created=args.owner_created,
            rights_reviewed=args.rights_reviewed, terms_checked=args.terms_checked,
            requested_scopes=["private_study"],
            consent_scopes=["private_study"] if args.owner_created else [],
            license_scopes=[] if args.owner_created else ["private_study"],
            consent_receipt_id=args.consent_receipt,
        )
        result = study_local_tabular_dataset(args.dataset, grant)
    except (DataStudyError, OSError, ValueError) as error:
        parser.error(str(error))
    result["buddy_position"] = position_on_dataset_study(result, grant)
    result["use_record"] = grant
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
