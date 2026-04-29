"""Run all source scrapers; persist raw bytes and processed JSONL extracts."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from _paths import PROCESSED_DIR, RAW_DIR, ensure_on_path

ensure_on_path()

from bharat_cric.sources import imd, ndma, pib, sdma  # noqa: E402


logging.basicConfig(level=logging.INFO,
                     format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("scrape_all")


def _persist(extracts, source_name: str) -> int:
    out = PROCESSED_DIR / source_name
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{source_name}_extracts.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for e in extracts:
            fh.write(json.dumps(e.to_dict(), ensure_ascii=False) + "\n")
    return len(extracts)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    totals = {}
    for name, mod in (("imd", imd), ("ndma", ndma), ("pib", pib), ("sdma", sdma)):
        try:
            extracts = mod.fetch_extracts(raw_dir=RAW_DIR)
            n = _persist(extracts, name)
            totals[name] = n
            logger.info("%s: %d extracts persisted", name, n)
        except Exception as exc:  # noqa: BLE001
            totals[name] = 0
            logger.exception("%s scraper crashed: %s", name, exc)

    logger.info("DONE — extract counts per source: %s", totals)


if __name__ == "__main__":
    main()
