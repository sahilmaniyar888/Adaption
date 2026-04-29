"""Validate an existing JSONL seed file and print a corpus report."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path

ensure_on_path()

from bharat_cric.schema import BharatCRICRow  # noqa: E402
from bharat_cric.validators import validate_corpus  # noqa: E402


def main(path: str | None = None) -> None:
    target = Path(path) if path else SEED_DIR / "seed_v1_en.jsonl"
    if not target.exists():
        print(f"no seed file at {target} — run scripts/build_seed.py first")
        sys.exit(1)

    rows = []
    with target.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(BharatCRICRow.model_validate_json(line))

    report = validate_corpus(rows)
    print(json.dumps(report.as_dict(), indent=2, default=str))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
