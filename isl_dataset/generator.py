"""Build the ISL-Medical instruction-tuning dataset (v1.0) → JSONL.

Pipeline:
    raw lexicon + contextual rows
        -> transform.build_records (templated expansion)
        -> Sample schema validation
        -> deduped JSONL
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import Sample, json_schema
from .transform import build_records, sample_balanced


def build_dataset(output_path: Path, per_category: int = 30) -> dict:
    """Validate every row against `Sample`, write JSONL, return stats."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    by_category: dict[str, int] = {}
    by_intent: dict[str, int] = {}
    by_urgency: dict[str, int] = {}
    by_difficulty: dict[str, int] = {}
    word_counts: list[int] = []
    gloss_token_counts: list[int] = []

    raw_rows = build_records()
    raw_total = len(raw_rows)
    rows = sample_balanced(raw_rows, per_category=per_category)
    sampled_total = len(rows)

    valid_rows: list[Sample] = []
    rejected: list[tuple[str, str]] = []

    for row in rows:
        try:
            valid_rows.append(Sample(**row))
        except Exception as exc:
            rejected.append((row.get("id", "?"), str(exc)[:300]))

    with output_path.open("w", encoding="utf-8") as f:
        for r in valid_rows:
            f.write(r.model_dump_json() + "\n")
            by_category[r.category.value] = by_category.get(r.category.value, 0) + 1
            by_intent[r.intent.value] = by_intent.get(r.intent.value, 0) + 1
            by_urgency[r.urgency.value] = by_urgency.get(r.urgency.value, 0) + 1
            by_difficulty[r.difficulty.value] = by_difficulty.get(r.difficulty.value, 0) + 1
            word_counts.append(len(r.text_en.split()))
            gloss_token_counts.append(
                len([t for t in r.gloss_sequence.replace(",", " ").replace(".", " ")
                       .replace("?", " ").replace("!", " ").split() if t])
            )

    natural_count = sum(1 for r in valid_rows if "-nat-" in r.id)
    return {
        "raw_pool": raw_total,
        "sampled": sampled_total,
        "total_valid": len(valid_rows),
        "total_rejected": len(rejected),
        "natural_voice_rows": natural_count,
        "by_category": by_category,
        "by_intent": by_intent,
        "by_urgency": by_urgency,
        "by_difficulty": by_difficulty,
        "avg_text_en_words": (sum(word_counts) / len(word_counts)) if word_counts else 0,
        "avg_gloss_tokens": (sum(gloss_token_counts) / len(gloss_token_counts)) if gloss_token_counts else 0,
        "rejection_samples": rejected[:10],
    }


def write_schema(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_schema(), indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_dataset_card(path: Path, stats: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_cat = "\n".join(f"- **{k}**: {v}" for k, v in sorted(stats["by_category"].items()))
    by_intent = "\n".join(f"- **{k}**: {v}" for k, v in sorted(stats["by_intent"].items()))
    by_urg = "\n".join(f"- **{k}**: {v}" for k, v in sorted(stats["by_urgency"].items()))
    by_diff = "\n".join(f"- **{k}**: {v}" for k, v in sorted(stats["by_difficulty"].items()))

    card = f"""---
language:
  - en
  - hi
license: cc-by-4.0
pretty_name: ISL-Medical Instruction Tuning v1.0
size_categories:
  - 1K<n<10K
task_categories:
  - text-generation
  - translation
tags:
  - sign-language
  - indian-sign-language
  - isl
  - low-resource
  - medical
  - healthcare
  - instruction-tuning
  - adaption
  - adaptive-data
---

# ISL-Medical Instruction-Tuning Dataset (v1.0)

The first open Indian Sign Language (ISL) instruction-tuning benchmark
focused on healthcare. Built for the **Adaption Uncharted Data Challenge**.

## Attribution

Powered by Adaptive Data by Adaption — https://adaptionlabs.ai

License: CC-BY-4.0. Please retain attribution in any derivative work.

## Statistics

- **Total valid rows**: {stats['total_valid']}
- **Avg text_en words**: {stats['avg_text_en_words']:.1f}
- **Avg gloss tokens**: {stats['avg_gloss_tokens']:.1f}

### By category
{by_cat}

### By intent
{by_intent}

### By urgency
{by_urg}

### By difficulty
{by_diff}

## Schema

| field | description |
| ----- | ----------- |
| `id` | stable identifier `isl-med-{{ctx|lex2ctx}}-slug` |
| `text_en` | English healthcare instruction (8-20 words) |
| `text_hi` | Hindi translation (Devanagari) |
| `gloss_sequence` | ISL gloss, uppercase, 5-12 tokens, OSV grammar |
| `category` | medical specialty |
| `intent` | `treatment_advice` / `diagnosis` / `medication` / `emergency` / `prevention` |
| `urgency` | `low` / `medium` / `high` |
| `difficulty` | `easy` / `medium` / `hard` |
| `source` | `synthetic` |

## Usage in Adaption

- **Prompt** → `text_en`
- **Completion** → `gloss_sequence`
- **Context** → `category`

## ISL gloss conventions

- UPPERCASE tokens; articles & copulas dropped.
- Time-Subject-Verb / Topic-Comment ordering.
- `+` joins compound signs (e.g. `BLOOD+PRESSURE`).
- `++` marks repetition.
- Comma marks discourse boundary; `?` stays at end.

## Citation

```
@dataset{{maniyar2026islmedical,
  title  = {{ISL-Medical Instruction-Tuning Dataset v1.0}},
  author = {{Maniyar, Sahil}},
  year   = {{2026}},
  note   = {{Powered by Adaptive Data by Adaption}}
}}
```
"""
    path.write_text(card, encoding="utf-8")
