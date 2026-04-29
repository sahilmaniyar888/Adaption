"""Build seed_v1_en.jsonl: scrape -> instructions -> validate -> write."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from _paths import PROCESSED_DIR, RAW_DIR, SEED_DIR, ensure_on_path

ensure_on_path()

from bharat_cric.instruction_builder import source_extract_to_instruction_rows  # noqa: E402
from bharat_cric.sources import imd, ndma, pib, sdma  # noqa: E402
from bharat_cric.validators import validate_corpus, validate_row  # noqa: E402


logging.basicConfig(level=logging.INFO,
                     format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("build_seed")


def _gather_extracts():
    out = []
    for name, mod in (("imd", imd), ("ndma", ndma), ("pib", pib), ("sdma", sdma)):
        try:
            out.extend(mod.fetch_extracts(raw_dir=RAW_DIR))
        except Exception as exc:  # noqa: BLE001
            logger.warning("%s extracts failed: %s", name, exc)
    return out


def main() -> None:
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SEED_DIR / "seed_v1_en.jsonl"

    extracts = _gather_extracts()
    logger.info("gathered %d extracts", len(extracts))

    rows = []
    rejected = 0
    seen_signatures: set[str] = set()
    for ex in extracts:
        candidates = source_extract_to_instruction_rows(ex)
        for row in candidates:
            res = validate_row(row)
            if not res.ok:
                rejected += 1
                logger.warning("rejected row: %s", res.errors)
                continue
            sig = f"{row.instruction}||{row.completion}"
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            rows.append(row)

    report = validate_corpus(rows)
    logger.info("corpus errors: %d, warnings: %d", len(report.errors),
                 len(report.warnings))
    for err in report.errors[:10]:
        logger.warning("corpus error: %s", err)

    with out_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(row.model_dump_json() + "\n")

    logger.info("wrote %d rows -> %s (rejected %d)", len(rows), out_path, rejected)
    print(json.dumps({
        "rows_written": len(rows),
        "rejected": rejected,
        "helpline_grounding_ratio": report.helpline_grounding_ratio,
        "helpline_grounding_target_met": report.helpline_grounding_target_met,
        "by_surface_format": report.by_surface_format,
        "by_disaster_type": report.by_disaster_type,
        "by_validation_status": report.by_validation_status,
    }, indent=2))


if __name__ == "__main__":
    main()
