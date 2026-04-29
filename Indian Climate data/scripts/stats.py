"""Print per-language, per-disaster_type, per-surface_format counts for the seed."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from _paths import SEED_DIR


def main(path: str | None = None) -> None:
    target = Path(path) if path else SEED_DIR / "seed_v1_en.jsonl"
    if not target.exists():
        print(f"no seed file at {target}")
        sys.exit(1)

    by_lang = Counter()
    by_dtype = Counter()
    by_sfmt = Counter()
    by_vstatus = Counter()
    by_intent = Counter()
    helpline_count = 0
    total = 0

    with target.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            total += 1
            by_lang[row["language"]] += 1
            by_dtype[row["disaster_type"]] += 1
            by_sfmt[row["surface_format"]] += 1
            by_vstatus[row["validation_status"]] += 1
            by_intent[row["intent_label"]] += 1
            if row.get("helplines_mentioned"):
                helpline_count += 1

    grounding = helpline_count / total if total else 0.0
    print(f"BharatCRIC seed file: {target}")
    print(f"  total rows                 : {total}")
    print(f"  rows with helpline grounding: {helpline_count} "
          f"({grounding:.1%}; target >=20%) "
          f"{'OK' if grounding >= 0.20 else 'BELOW'}")
    print()
    print("by language               :", dict(by_lang))
    print("by disaster_type          :", dict(by_dtype))
    print("by surface_format         :", dict(by_sfmt))
    print("by validation_status      :", dict(by_vstatus))
    print("by intent_label           :", dict(by_intent))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
