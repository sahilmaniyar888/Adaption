# BharatCRIC — Bharat Climate Resilience Instruction Corpus

A multilingual instruction-format dataset for heatwave preparedness, heat-illness
response, vulnerable population safety, and disaster-fraud detection across five
languages. Built for the **Adaption Uncharted Data Challenge** (submission window
closes 2026-05-01).

## Abstract

BharatCRIC pairs source-authentic guidance from IMD, NDMA, PIB and state SDMAs with
LLM-adapted variants over five surface formats (SMS, WhatsApp, official bulletin,
radio script, community post). Each row carries a strict provenance tag and is
re-grounded against a hard-coded helpline registry to suppress hallucinated numbers.
The genuine ↔ scam pair structure plus an Ol Chiki Santali slice make the corpus a
useful adversarial benchmark for climate-resilience instruction tuning in
under-served Indian languages.

**Locked specs**: target 2,000 rows; Santali capped at 150 (no Adaption expansion); ≥20% of rows must include validated helpline grounding.

## Challenge criteria addressed

| Criterion | How BharatCRIC addresses it |
|---|---|
| **Novel / underserved data** | Heatwave-centric instructions in Bhojpuri, Maithili, and Ol Chiki Santali — almost absent from existing instruction corpora. |
| **Quality and faithfulness** | Two-tier validation: source_authentic rows are extracted from named IMD/NDMA/PIB documents; LLM-adapted rows are eye-scan reviewed by a North-Indian native speaker. Helplines are only accepted from a curated registry. |
| **Practical impact** | Direct downstream use for climate-resilience SLM tuning in regions where heat mortality is rising fastest (Bihar, eastern UP, Jharkhand, Odisha). |

## Languages

| Code | Script | Notes |
|---|---|---|
| `bho` | `Deva` | Bhojpuri (Devanagari) |
| `mai` | `Deva` | Maithili (Devanagari) |
| `sat` | `Olck` | Santali (Ol Chiki) — capped 150 rows, no expansion |
| `hin` | `Deva` | Hindi |
| `eng` | `Latn` | English (seed source for adaptation) |

## Schema preview

`row_id`, `pair_id`, `disaster_type`, `language`, `script`, `surface_format`,
`instruction`, `completion`, `english_gloss`, `source_reference`,
`validation_status`, `intent_label`, `length_constraint_satisfied`,
`helplines_mentioned`, `metadata_json`, `created_at`, `adaption_recipes_applied`.

## validation_status taxonomy

- `source_authentic` — text extracted directly from a named IMD/NDMA/PIB/SDMA document.
- `source_extracted_unverified_native_review_pending` — extracted from corpora/papers, awaiting native review (default for Santali Day-1 rows).
- `llm_adapted_eyescan_reviewed` — produced via Adaption recipes and eye-scan reviewed by a fluent reader.
- `llm_adapted_unreviewed` — produced via Adaption recipes, not yet reviewed (transient state).
- `native_validated` — verified by a fluent native speaker against a checklist.

## Ethical considerations

- **Disaster-information accuracy**: every helpline number is rejected unless it appears in `helpline_registry.VALIDATED_HELPLINES`; "PM/Pradhan Mantri/Yojana" mentions are flagged unless the scheme name matches a hard-coded validated list.
- **Scam corpora**: scam-variant rows are paired (`pair_id`) with a genuine counterpart and tagged `intent_label="scam_attempt"`; the dataset card warns downstream users not to redistribute scam variants without the genuine pair.
- **Attribution**: source_authentic rows carry the originating URL in `source_reference`; raw scrapes are stored under `data/raw/` and never edited.
- **Native speaker effort**: Santali rows ship at `source_extracted_unverified_native_review_pending` until an Ol Chiki reader confirms.

## Citation

```bibtex
@dataset{bharatcric_2026,
  title  = {BharatCRIC: Bharat Climate Resilience Instruction Corpus},
  author = {Maniyar, Sahil},
  year   = {2026},
  doi    = {TBD-zenodo-doi},
  note   = {Adaption Uncharted Data Challenge submission}
}
```
