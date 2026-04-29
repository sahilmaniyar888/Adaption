"""Print per-language, per-disaster_type, per-surface_format counts for the seed.

Day 2 additions:
  - Rows per language
  - Helpline grounding ratio per language
  - Script consistency ratio
  - English gloss coverage
  - Instruction type distribution
  - Source quality distribution
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from _paths import SEED_DIR


def main(path: str | None = None) -> None:
    target = Path(path) if path else SEED_DIR / "seed_v2_multilingual.jsonl"
    if not target.exists():
        # Fallback to v1
        target = SEED_DIR / "seed_v1_en.jsonl"
    if not target.exists():
        print(f"no seed file at {target}")
        sys.exit(1)

    by_lang = Counter()
    by_dtype = Counter()
    by_sfmt = Counter()
    by_vstatus = Counter()
    by_intent = Counter()
    by_itype = Counter()
    by_squality = Counter()
    helpline_types = Counter()
    format_lengths = defaultdict(list)
    tokens_by_lang = defaultdict(Counter)
    
    helpline_count = 0
    helpline_by_lang = defaultdict(int)
    lang_total = defaultdict(int)
    gloss_present = 0
    non_eng_total = 0
    non_eng_non_translation = 0
    total = 0

    LANG_SCRIPT = {"bho": "Deva", "mai": "Deva", "sat": "Olck", "hin": "Deva", "eng": "Latn"}
    script_ok = 0

    with target.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            total += 1
            lang = row["language"]
            by_lang[lang] += 1
            by_dtype[row["disaster_type"]] += 1
            by_sfmt[row["surface_format"]] += 1
            by_vstatus[row["validation_status"]] += 1
            by_intent[row["intent_label"]] += 1
            by_itype[row.get("instruction_type", "unspecified")] += 1
            by_squality[row.get("source_quality", "unspecified")] += 1

            lang_total[lang] += 1
            if row.get("helplines_mentioned"):
                helpline_count += 1
                helpline_by_lang[lang] += 1
                for hl in row["helplines_mentioned"]:
                    helpline_types[hl] += 1

            if LANG_SCRIPT.get(lang) == row.get("script"):
                script_ok += 1
                
            # Collect lengths
            format_lengths[row["surface_format"]].append(len(row["completion"]))
            
            # Collect tokens
            import re
            words = [w for w in re.findall(r"\w+", row["completion"].lower()) if len(w) > 2]
            for w in words:
                tokens_by_lang[lang][w] += 1

            if lang != "eng":
                non_eng_total += 1
                if row.get("english_gloss"):
                    gloss_present += 1
                itype = row.get("instruction_type")
                if itype and itype != "translation":
                    non_eng_non_translation += 1

    grounding = helpline_count / total if total else 0.0
    script_ratio = script_ok / total if total else 1.0
    gloss_coverage = gloss_present / non_eng_total if non_eng_total else 1.0
    diversity_ratio = non_eng_non_translation / non_eng_total if non_eng_total else 1.0

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
    print()
    print("--- Day 2 Metrics ---")
    print(f"  script consistency ratio   : {script_ratio:.2%}")
    print(f"  english gloss coverage     : {gloss_coverage:.2%} (non-English rows)")
    print(f"  instruction diversity      : {diversity_ratio:.2%} (non-translation in non-English)")
    print()
    print("helpline grounding by language:")
    for lang in sorted(lang_total.keys()):
        ratio = helpline_by_lang[lang] / lang_total[lang] if lang_total[lang] else 0
        print(f"  {lang}: {helpline_by_lang[lang]}/{lang_total[lang]} ({ratio:.1%})")
    print()
    print("by source_quality         :", dict(by_squality))
    print()
    print("--- Detailed Distributions ---")
    print("helpline types            :", dict(helpline_types))
    print("avg completion length by format:")
    for fmt, lengths in format_lengths.items():
        avg = sum(lengths) / len(lengths) if lengths else 0
        print(f"  {fmt}: {avg:.1f} chars (from {len(lengths)} rows)")
    print()
    print("Top 10 tokens by language:")
    for lang, counter in tokens_by_lang.items():
        top = counter.most_common(10)
        try:
            print(f"  {lang}: {top}")
        except UnicodeEncodeError:
            print(f"  {lang}: [contains unprintable characters]")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
