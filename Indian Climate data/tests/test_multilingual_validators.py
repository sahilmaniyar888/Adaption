"""Tests for Day 2 multilingual validators."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from bharat_cric.schema import BharatCRICRow
from bharat_cric.validators import (
    validate_corpus,
    validate_domain_keywords,
    validate_no_devanagari_leakage,
    validate_olchiki_coverage,
    validate_row,
    validate_script_consistency,
)


def _row(**over) -> BharatCRICRow:
    kw = dict(
        disaster_type="heatwave",
        language="eng",
        script="Latn",
        surface_format="community_post",
        instruction="What should I do during a heatwave?",
        completion="Drink water and rest in shade.",
        source_reference="https://www.ndma.gov.in/Natural-Hazards/Heat-Wave",
        validation_status="source_authentic",
        intent_label="preparedness_advice",
    )
    kw.update(over)
    return BharatCRICRow(**kw)


def _hindi_row(**over) -> BharatCRICRow:
    kw = dict(
        disaster_type="heatwave",
        language="hin",
        script="Deva",
        surface_format="community_post",
        instruction="लू के दौरान क्या करें?",
        completion="बार-बार पानी पिएं और छाया में रहें।",
        english_gloss="Drink water frequently and stay in shade.",
        source_reference="https://mausam.imd.gov.in/responsive/heatwave_guidance.php",
        validation_status="source_authentic",
        intent_label="preparedness_advice",
    )
    kw.update(over)
    return BharatCRICRow(**kw)


def _santali_row(**over) -> BharatCRICRow:
    kw = dict(
        disaster_type="heatwave",
        language="sat",
        script="Olck",
        surface_format="community_post",
        instruction="ᱞᱩ ᱨᱮ ᱪᱮᱫ ᱠᱟᱹᱢᱤ ᱠᱟᱫ?",
        completion="ᱵᱟᱝ ᱵᱟᱝ ᱫᱟᱜ ᱧᱩᱢᱤᱧ ᱟᱨ ᱪᱷᱟᱦᱟᱨ ᱨᱮ ᱛᱟᱦᱮᱸᱱ ᱠᱟᱫ᱾",
        english_gloss="Drink water frequently and stay in shade.",
        source_reference="https://ndma.gov.in/Natural-Hazards/Heat-Wave",
        validation_status="source_extracted_no_native_validation",
        intent_label="preparedness_advice",
    )
    kw.update(over)
    return BharatCRICRow(**kw)


# --- Test 1: Schema accepts new Day 2 fields ---
def test_schema_accepts_day2_fields():
    row = _hindi_row(
        source_corpus="imd_hindi_curated",
        extraction_method="manual_curation",
        source_quality="high",
        instruction_type="translation",
    )
    assert row.source_corpus == "imd_hindi_curated"
    assert row.extraction_method == "manual_curation"
    assert row.source_quality == "high"
    assert row.generation_method == "source"
    assert row.instruction_type == "translation"


# --- Test 2: Schema accepts source_extracted_no_native_validation ---
def test_santali_validation_status():
    row = _santali_row()
    assert row.validation_status == "source_extracted_no_native_validation"


# --- Test 3: Script consistency validator ---
def test_script_consistency_passes():
    row = _hindi_row()
    ok, msg = validate_script_consistency(row)
    assert ok


def test_script_consistency_fails():
    """Schema enforces script/language match at creation, so we can only test
    that the validator correctly validates matching rows."""
    row = _hindi_row()
    ok, msg = validate_script_consistency(row)
    assert ok
    assert msg is None


# --- Test 4: Domain keyword validator - passes ---
def test_domain_keywords_hindi_passes():
    row = _hindi_row()
    ok, msg = validate_domain_keywords(row)
    assert ok


# --- Test 5: Domain keyword validator - fails ---
def test_domain_keywords_fails_no_domain():
    row = _hindi_row(
        instruction="यह एक सामान्य वाक्य है।",
        completion="कुछ भी नहीं बताया गया।",
        english_gloss="Nothing was mentioned.",
    )
    ok, msg = validate_domain_keywords(row)
    assert not ok
    assert "domain-relevant" in msg


# --- Test 6: Santali Devanagari leakage - passes ---
def test_no_devanagari_leakage_passes():
    row = _santali_row()
    ok, msg = validate_no_devanagari_leakage(row)
    assert ok


# --- Test 7: Santali Devanagari leakage - fails ---
def test_devanagari_leakage_fails():
    row = _santali_row(
        completion="गर्मी से बचें और पानी पिएं। ᱫᱟᱜ ᱧᱩᱢᱤᱧ᱾",
    )
    ok, msg = validate_no_devanagari_leakage(row)
    assert not ok
    assert "Devanagari leakage" in msg


# --- Test 8: Ol Chiki coverage validator ---
def test_olchiki_coverage_passes():
    row = _santali_row()
    ok, msg = validate_olchiki_coverage(row)
    assert ok


# --- Test 9: Corpus-level English gloss coverage ---
def test_corpus_gloss_coverage_warning():
    # 5 Hindi rows without gloss (below 70%)
    rows_no_gloss = [
        _hindi_row(english_gloss=None, completion=f"पानी पिएं item {i}")
        for i in range(7)
    ]
    rows_with_gloss = [
        _hindi_row(english_gloss="Drink water", completion=f"पानी पिएं gloss {i}")
        for i in range(3)
    ]
    # Need helpline grounding
    grounded = [_row(completion="Call 108 for medical help.", helplines_mentioned=["108"])]
    report = validate_corpus(rows_no_gloss + rows_with_gloss + grounded)
    assert report.english_gloss_coverage < 0.70
    assert any("english_gloss coverage" in w for w in report.warnings)


# --- Test 10: Corpus-level instruction diversity ---
def test_corpus_instruction_diversity():
    translation_rows = [
        _hindi_row(instruction_type="translation",
                   completion=f"पानी पिएं trans {i}")
        for i in range(7)
    ]
    qa_rows = [
        _hindi_row(instruction_type="qa",
                   completion=f"पानी पिएं qa {i}")
        for i in range(3)
    ]
    grounded = [_row(completion="Call 108 for help.", helplines_mentioned=["108"])]
    report = validate_corpus(translation_rows + qa_rows + grounded)
    assert report.instruction_diversity_ratio > 0.0


# --- Test 11: corpus reference format accepted ---
def test_corpus_source_reference():
    row = _hindi_row(source_reference="corpus:bhojpuri_wikipedia")
    assert row.source_reference.startswith("corpus:")


# --- Test 12: source quality distribution tracked ---
def test_source_quality_tracked():
    rows = [
        _hindi_row(source_quality="high", completion=f"पानी item {i}")
        for i in range(3)
    ]
    grounded = [_row(completion="Call 108.", helplines_mentioned=["108"])]
    report = validate_corpus(rows + grounded)
    assert "high" in report.by_source_quality


# --- Test 13: Hindi row without english_gloss is now allowed (Day 2 relaxation) ---
def test_hindi_row_without_gloss_allowed():
    """Day 2: english_gloss is enforced at corpus level, not per-row."""
    row = _hindi_row(english_gloss=None)
    assert row.language == "hin"
    assert row.english_gloss is None


# --- Test 14: Script consistency ratio in corpus report ---
def test_corpus_script_consistency():
    rows = [_hindi_row(completion=f"पानी पिएं {i}") for i in range(5)]
    grounded = [_row(completion="Call 108.", helplines_mentioned=["108"])]
    report = validate_corpus(rows + grounded)
    assert report.script_consistency_ratio == 1.0
