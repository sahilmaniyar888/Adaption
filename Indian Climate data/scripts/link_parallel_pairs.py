"""Link cross-lingual parallel pairs across the multilingual seed.

Matching criteria:
  - same source URL
  - same disaster_type
  - same surface_format
  - length ±30%
  - keyword overlap ≥50%
  - helpline consistency (if present)

Does NOT force matches — only links high-confidence pairs.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from _paths import SEED_DIR, ensure_on_path

ensure_on_path()

from bharat_cric.schema import BharatCRICRow  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _extract_keywords(text: str) -> Set[str]:
    """Extract meaningful keywords from text (lowercase, ≥3 chars)."""
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) >= 3}


def _helpline_set(text: str) -> Set[str]:
    """Extract 3-5 digit numbers from text."""
    return set(re.findall(r"\b\d{3,5}\b", text))


def _keyword_overlap(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _length_ratio(a: str, b: str) -> float:
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return 0.0
    return min(la, lb) / max(la, lb)


def find_parallel_pairs(rows: List[Dict]) -> List[Tuple[str, str, float]]:
    """Find cross-lingual parallel pairs. Returns list of (row_id_a, row_id_b, score)."""
    # Group by (source_reference, disaster_type, surface_format)
    groups: Dict[Tuple, List[Dict]] = defaultdict(list)
    for row in rows:
        key = (
            row.get("source_reference", ""),
            row.get("disaster_type", ""),
            row.get("surface_format", ""),
        )
        groups[key].append(row)

    pairs: List[Tuple[str, str, float]] = []
    for key, group_rows in groups.items():
        # Split by language
        by_lang: Dict[str, List[Dict]] = defaultdict(list)
        for r in group_rows:
            by_lang[r["language"]].append(r)

        # Only try to link if multiple languages present
        langs = list(by_lang.keys())
        if len(langs) < 2:
            continue

        # Compare eng rows with each non-eng language
        if "eng" in by_lang:
            eng_rows = by_lang["eng"]
            for lang in langs:
                if lang == "eng":
                    continue
                for eng_r in eng_rows:
                    eng_kw = _extract_keywords(eng_r.get("completion", ""))
                    eng_gloss_kw = _extract_keywords(eng_r.get("english_gloss", "") or "")
                    eng_helplines = _helpline_set(eng_r.get("completion", ""))

                    for other_r in by_lang[lang]:
                        # Length check (±30%)
                        if _length_ratio(eng_r.get("completion", ""),
                                        other_r.get("completion", "")) < 0.70:
                            continue

                        # Keyword overlap using english_gloss of non-English row
                        other_gloss = other_r.get("english_gloss", "") or ""
                        other_kw = _extract_keywords(other_gloss) | _extract_keywords(
                            other_r.get("completion", ""))

                        overlap = _keyword_overlap(eng_kw | eng_gloss_kw, other_kw)
                        if overlap < 0.50:
                            continue

                        # Helpline consistency
                        other_helplines = _helpline_set(other_r.get("completion", ""))
                        if eng_helplines and other_helplines:
                            if not eng_helplines & other_helplines:
                                continue  # helplines don't match

                        score = overlap
                        pairs.append((eng_r["row_id"], other_r["row_id"], score))

    return pairs


def main(path: str | None = None) -> None:
    target = Path(path) if path else SEED_DIR / "seed_v2_multilingual.jsonl"
    if not target.exists():
        print(f"Seed file not found: {target}")
        sys.exit(1)

    rows = []
    with target.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    logger.info("Loaded %d rows for pair linking", len(rows))
    pairs = find_parallel_pairs(rows)
    logger.info("Found %d cross-lingual parallel pairs", len(pairs))

    # Write pair links
    out = SEED_DIR / "parallel_pairs.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for a, b, score in pairs:
            fh.write(json.dumps({"row_id_a": a, "row_id_b": b, "score": round(score, 3)}) + "\n")

    print(f"Wrote {len(pairs)} parallel pairs -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
