"""Build seed_v2_multilingual.jsonl: English seed + multilingual extracts.

Steps:
1. Load English seed (457 rows)
2. Run multilingual extractors (Hindi, Bhojpuri, Maithili, Santali)
3. Apply domain filtering before instruction creation
4. Deduplicate (exact + simhash ≥0.9)
5. Validate
6. Write output
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import List

from _paths import PROCESSED_DIR, RAW_DIR, SEED_DIR, REPORTS_DIR, ensure_on_path

ensure_on_path()

from bharat_cric.multilingual_builder import multilingual_extract_to_rows  # noqa: E402
from bharat_cric.sources import SourceExtract  # noqa: E402
from bharat_cric.sources import imd_hindi, ndma_hindi  # noqa: E402
from bharat_cric.sources import bhojpuri_authentic, maithili_authentic, santali_authentic  # noqa: E402
from bharat_cric.validators import validate_corpus, validate_row  # noqa: E402
from bharat_cric.schema import BharatCRICRow  # noqa: E402

logging.basicConfig(level=logging.INFO,
                     format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("build_seed_v2")


def _simhash(text: str, hashbits: int = 64) -> int:
    """Simple simhash for near-duplicate detection."""
    tokens = re.findall(r"\w+", text.lower())
    v = [0] * hashbits
    for t in tokens:
        h = int(hashlib.md5(t.encode()).hexdigest(), 16)
        for i in range(hashbits):
            if h & (1 << i):
                v[i] += 1
            else:
                v[i] -= 1
    return sum(1 << i for i in range(hashbits) if v[i] > 0)


def _simhash_similarity(h1: int, h2: int, hashbits: int = 64) -> float:
    diff = bin(h1 ^ h2).count("1")
    return 1 - diff / hashbits


def _gather_multilingual_extracts():
    """Gather all non-English source extracts."""
    extracts = []
    sources = [
        ("imd_hindi", imd_hindi),
        ("ndma_hindi", ndma_hindi),
        ("bhojpuri", bhojpuri_authentic),
        ("maithili", maithili_authentic),
        ("santali", santali_authentic),
    ]
    for name, mod in sources:
        try:
            exts = mod.fetch_extracts(raw_dir=RAW_DIR)
            extracts.extend(exts)
            logger.info("  %s: %d extracts, %d items total",
                       name, len(exts), sum(len(e.items) for e in exts))
        except Exception as exc:
            logger.warning("%s extracts failed: %s", name, exc)
    return extracts


def _lang_from_hint(hint: str) -> str:
    return {"hin": "hin", "bho": "bho", "mai": "mai", "sat": "sat"}.get(hint, hint)


def _script_from_lang(lang: str) -> str:
    return {"hin": "Deva", "bho": "Deva", "mai": "Deva", "sat": "Olck"}.get(lang, "Latn")


def main() -> None:
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load English seed
    eng_seed = SEED_DIR / "seed_v1_en.jsonl"
    eng_rows: List[BharatCRICRow] = []
    if eng_seed.exists():
        with eng_seed.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    # Add Day 2 defaults for Day 1 rows
                    data.setdefault("source_corpus", None)
                    data.setdefault("extraction_method", None)
                    data.setdefault("source_quality", None)
                    data.setdefault("generation_method", "source")
                    data.setdefault("instruction_type", None)
                    try:
                        eng_rows.append(BharatCRICRow(**data))
                    except Exception as exc:
                        logger.warning("Skipping English row: %s", exc)
        logger.info("Loaded %d English rows from %s", len(eng_rows), eng_seed)
    else:
        logger.warning("English seed not found at %s", eng_seed)

    # Step 2: Run multilingual extractors
    logger.info("Gathering multilingual extracts...")
    ml_extracts = _gather_multilingual_extracts()
    logger.info("Total multilingual extracts: %d", len(ml_extracts))

    # Step 3: Apply domain filtering + create instruction rows
    ml_rows: List[BharatCRICRow] = []
    for ext in ml_extracts:
        lang = _lang_from_hint(ext.language_hint)
        script = _script_from_lang(lang)
        glosses = ext.metadata.get("english_glosses")
        quality = ext.metadata.get("source_quality", "medium")
        method = ext.metadata.get("extraction_method", "manual_curation")

        # Santali special handling
        if lang == "sat":
            vstatus = "source_extracted_no_native_validation"
        else:
            vstatus = "source_authentic"

        rows = multilingual_extract_to_rows(
            ext, lang=lang, script=script,
            source_quality=quality,
            extraction_method=method,
            validation_status=vstatus,
            english_glosses=glosses,
        )
        ml_rows.extend(rows)

    logger.info("Generated %d multilingual rows", len(ml_rows))

    # Step 4: Deduplicate (exact + simhash per-language)
    all_rows = eng_rows + ml_rows
    seen_sigs: set = set()
    seen_hashes_by_lang: dict = {}  # {lang: {hash: row_id}}
    deduped: List[BharatCRICRow] = []
    dup_count = 0

    for row in all_rows:
        sig = f"{row.language}|{row.instruction}||{row.completion}"
        if sig in seen_sigs:
            dup_count += 1
            continue
        seen_sigs.add(sig)

        # Simhash near-dup (per-language only)
        lang = row.language
        if lang not in seen_hashes_by_lang:
            seen_hashes_by_lang[lang] = {}
        sh = _simhash(row.completion)
        is_near_dup = False
        for prev_hash in seen_hashes_by_lang[lang]:
            if _simhash_similarity(sh, prev_hash) >= 0.92:
                is_near_dup = True
                dup_count += 1
                break
        if not is_near_dup:
            seen_hashes_by_lang[lang][sh] = row.row_id
            deduped.append(row)

    logger.info("After dedup: %d rows (removed %d duplicates)", len(deduped), dup_count)

    # Step 5: Validate
    rejected = 0
    valid_rows: List[BharatCRICRow] = []
    for row in deduped:
        res = validate_row(row)
        if not res.ok:
            rejected += 1
            if rejected <= 10:
                logger.warning("Rejected row %s: %s", row.row_id, res.errors)
            continue
        valid_rows.append(row)

    logger.info("After validation: %d rows (rejected %d)", len(valid_rows), rejected)

    report = validate_corpus(valid_rows)
    logger.info("Corpus errors: %d, warnings: %d",
                len(report.errors), len(report.warnings))
    for err in report.errors[:10]:
        logger.warning("Corpus error: %s", err)

    # Step 6: Write output
    out_path = SEED_DIR / "seed_v2_multilingual.jsonl"
    with out_path.open("w", encoding="utf-8") as fh:
        for row in valid_rows:
            fh.write(row.model_dump_json() + "\n")

    logger.info("Wrote %d rows -> %s", len(valid_rows), out_path)

    # Write stats report
    stats = report.as_dict()
    stats_path = REPORTS_DIR / "day2_stats.txt"
    with stats_path.open("w", encoding="utf-8") as fh:
        fh.write("BharatCRIC Day 2 — Multilingual Seed Statistics\n")
        fh.write("=" * 50 + "\n\n")
        fh.write(f"Total rows: {stats['total_rows']}\n\n")
        fh.write("By language:\n")
        for k, v in sorted(stats["by_language"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write(f"\nHelpline grounding ratio: {stats['helpline_grounding_ratio']:.2%}\n")
        fh.write(f"Helpline target met: {stats['helpline_grounding_target_met']}\n")
        fh.write("\nHelpline grounding by language:\n")
        for k, v in sorted(stats["helpline_grounding_by_lang"].items()):
            fh.write(f"  {k}: {v:.2%}\n")
        fh.write(f"\nScript consistency ratio: {stats['script_consistency_ratio']:.2%}\n")
        fh.write(f"English gloss coverage (non-English): {stats['english_gloss_coverage']:.2%}\n")
        fh.write(f"Instruction diversity ratio: {stats['instruction_diversity_ratio']:.2%}\n")
        fh.write("\nBy disaster_type:\n")
        for k, v in sorted(stats["by_disaster_type"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write("\nBy surface_format:\n")
        for k, v in sorted(stats["by_surface_format"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write("\nBy validation_status:\n")
        for k, v in sorted(stats["by_validation_status"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write("\nBy instruction_type:\n")
        for k, v in sorted(stats["by_instruction_type"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write("\nBy source_quality:\n")
        for k, v in sorted(stats["by_source_quality"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write("\nBy source_host:\n")
        for k, v in sorted(stats["by_source_host"].items()):
            fh.write(f"  {k}: {v}\n")
        fh.write(f"\nDuplicate row IDs: {len(stats['duplicate_row_ids'])}\n")
        fh.write(f"Near-duplicate pairs: {len(stats['near_duplicate_pairs'])}\n")
        fh.write(f"Errors: {len(stats['errors'])}\n")
        fh.write(f"Warnings: {len(stats['warnings'])}\n")
        if stats["errors"]:
            fh.write("\nError details:\n")
            for e in stats["errors"][:20]:
                fh.write(f"  - {e}\n")

    logger.info("Stats written to %s", stats_path)

    # Write source gaps report
    gaps_path = REPORTS_DIR / "day2_source_gaps.md"
    with gaps_path.open("w", encoding="utf-8") as fh:
        fh.write("# Day 2 — Source Gaps Report\n\n")
        fh.write("## Sources Used\n\n")
        fh.write("| Language | Source | Status | Rows |\n")
        fh.write("|----------|--------|--------|------|\n")
        lang_counts = stats["by_language"]
        fh.write(f"| eng | IMD/NDMA/PIB/SDMA (Day 1) | ✓ curated | {lang_counts.get('eng', 0)} |\n")
        fh.write(f"| hin | IMD Hindi/NDMA Hindi/PIB Hindi/AIR/State | ✓ curated | {lang_counts.get('hin', 0)} |\n")
        fh.write(f"| bho | NDMA Bhojpuri/Wikipedia | ✓ curated | {lang_counts.get('bho', 0)} |\n")
        fh.write(f"| mai | NDMA Maithili/Wikipedia | ✓ curated | {lang_counts.get('mai', 0)} |\n")
        fh.write(f"| sat | NDMA Santali/Wikipedia | ✓ curated (no native validation) | {lang_counts.get('sat', 0)} |\n")
        fh.write("\n## Known Gaps\n\n")
        fh.write("| Source | Issue | Fallback | Priority |\n")
        fh.write("|--------|-------|----------|----------|\n")
        fh.write("| bh.wikipedia.org (Bhojpuri) | Limited heat-specific articles | Used NDMA paraphrases | Low |\n")
        fh.write("| mai.wikipedia.org (Maithili) | Limited heat-specific articles | Used NDMA paraphrases | Low |\n")
        fh.write("| sat.wikipedia.org (Santali) | Very few articles | Used NDMA paraphrases in Ol Chiki | Medium |\n")
        fh.write("| AdiBhashaa corpus | Not publicly accessible | Curated manually | Medium |\n")
        fh.write("| Videha.org.in | Site availability uncertain | Used NDMA paraphrases | Low |\n")
        fh.write("| Anjoria.com | No heat-specific content found | Used NDMA paraphrases | Low |\n")
        fh.write("| JCERT/NCERT Santali | Textbook content, not heat-specific | Curated heat items | Low |\n")

    logger.info("Source gaps written to %s", gaps_path)

    # Print summary
    print(json.dumps({
        "rows_written": len(valid_rows),
        "rejected": rejected,
        "duplicates_removed": dup_count,
        "by_language": stats["by_language"],
        "helpline_grounding_ratio": stats["helpline_grounding_ratio"],
        "script_consistency_ratio": stats["script_consistency_ratio"],
        "english_gloss_coverage": stats["english_gloss_coverage"],
        "instruction_diversity_ratio": stats["instruction_diversity_ratio"],
    }, indent=2))


if __name__ == "__main__":
    main()
