"""Tests for row + corpus validators."""
from __future__ import annotations

from bharat_cric.schema import BharatCRICRow
from bharat_cric.validators import (
    HELPLINE_GROUNDING_MIN_RATIO,
    validate_corpus,
    validate_helplines,
    validate_no_invented_schemes,
    validate_row,
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


def test_validate_row_accepts_clean_row():
    res = validate_row(_row())
    assert res.ok
    assert res.errors == []


def test_validate_row_rejects_unverified_helpline_number():
    row = _row(completion="If you feel faint, call 9999 right now.")
    res = validate_row(row)
    assert not res.ok
    assert any("9999" in e or "unverified" in e for e in res.errors)


def test_validate_row_accepts_registered_helpline():
    row = _row(completion="In an emergency call 108 immediately.",
                helplines_mentioned=["108"])
    res = validate_row(row)
    assert res.ok


def test_validate_helplines_function_directly():
    ok, invalid = validate_helplines(_row(completion="Call 7777 now."))
    assert not ok
    assert "7777" in invalid


def test_scheme_hallucination_flag():
    bad = _row(
        completion="Apply for the PM Heatwave Yojana 2026 to receive Rs 5000.",
    )
    ok, msg = validate_no_invented_schemes(bad)
    assert not ok
    assert msg


def test_scheme_check_passes_for_known_scheme():
    good = _row(completion="Workers can get jobs under MGNREGA during heatwave days.")
    ok, _ = validate_no_invented_schemes(good)
    assert ok


def test_scheme_check_skipped_for_scam_rows():
    scam = _row(
        disaster_type="disaster_scam_heat",
        intent_label="scam_alert",
        pair_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        completion="The SMS claims a fake 'PM Heat Relief Yojana 2026' — report on 1930.",
        helplines_mentioned=["1930"],
    )
    ok, _ = validate_no_invented_schemes(scam)
    assert ok


def test_corpus_helpline_grounding_below_threshold_flags_error():
    rows = [_row(completion=f"Plain advice number {i}.") for i in range(10)]
    report = validate_corpus(rows)
    assert not report.helpline_grounding_target_met
    assert any("helpline grounding" in e for e in report.errors)


def test_corpus_helpline_grounding_meets_threshold():
    grounded = [_row(completion="Call 108 for medical help.",
                       helplines_mentioned=["108"])
                for _ in range(3)]
    plain = [_row(completion=f"Heatwave advice item {i}.") for i in range(7)]
    report = validate_corpus(grounded + plain)
    assert report.helpline_grounding_ratio >= HELPLINE_GROUNDING_MIN_RATIO


def test_corpus_detects_exact_duplicates():
    a = _row(completion="Stay hydrated.", instruction="Tip?")
    b = _row(completion="Stay hydrated.", instruction="Tip?",
              helplines_mentioned=["108"], )
    # add helpline grounding to satisfy threshold
    grounded = _row(completion="Call 108.", helplines_mentioned=["108"])
    report = validate_corpus([a, b, grounded])
    assert report.duplicate_row_ids
