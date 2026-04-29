"""Tests for schema cross-field invariants."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from bharat_cric.schema import BharatCRICRow


def _base_kwargs(**over):
    kw = dict(
        disaster_type="heatwave",
        language="eng",
        script="Latn",
        surface_format="community_post",
        instruction="Describe heatwave preparedness.",
        completion="Drink water and stay in shade.",
        source_reference="https://www.ndma.gov.in/Natural-Hazards/Heat-Wave",
        validation_status="source_authentic",
        intent_label="preparedness_advice",
    )
    kw.update(over)
    return kw


def test_minimal_eng_row_constructs():
    row = BharatCRICRow(**_base_kwargs())
    assert row.language == "eng"
    assert row.script == "Latn"
    assert row.english_gloss is None


def test_script_must_match_language_rejects_mismatch():
    with pytest.raises(ValidationError) as exc:
        BharatCRICRow(**_base_kwargs(language="hin", script="Latn"))
    assert "does not match language" in str(exc.value)


def test_script_must_match_language_olck_for_sat():
    row = BharatCRICRow(**_base_kwargs(
        language="sat", script="Olck",
        completion="ᱦᱟᱯᱨᱟᱢᱳᱜ",
        english_gloss="Drink water during the heatwave.",
    ))
    assert row.script == "Olck"


def test_english_gloss_required_for_non_english():
    with pytest.raises(ValidationError) as exc:
        BharatCRICRow(**_base_kwargs(
            language="hin", script="Deva",
            completion="गर्मी से बचें", english_gloss=None,
        ))
    assert "english_gloss is required" in str(exc.value)


def test_english_gloss_forbidden_for_english():
    with pytest.raises(ValidationError) as exc:
        BharatCRICRow(**_base_kwargs(english_gloss="redundant"))
    assert "english_gloss must be None" in str(exc.value)


def test_sms_length_cap_enforced():
    long_completion = "A" * 161
    with pytest.raises(ValidationError) as exc:
        BharatCRICRow(**_base_kwargs(
            surface_format="sms", completion=long_completion,
        ))
    assert "exceeds 160" in str(exc.value)


def test_scam_disaster_requires_pair_id():
    with pytest.raises(ValidationError) as exc:
        BharatCRICRow(**_base_kwargs(
            disaster_type="disaster_scam_heat",
            intent_label="scam_alert",
            pair_id=None,
        ))
    assert "pair_id is required" in str(exc.value)


def test_scam_disaster_with_pair_id_constructs():
    row = BharatCRICRow(**_base_kwargs(
        disaster_type="disaster_scam_heat",
        intent_label="scam_alert",
        pair_id="11111111-1111-1111-1111-111111111111",
    ))
    assert row.disaster_type == "disaster_scam_heat"


def test_source_reference_must_be_url_or_curated():
    with pytest.raises(ValidationError):
        BharatCRICRow(**_base_kwargs(source_reference="not-a-url"))


def test_internal_curated_source_reference_accepted():
    row = BharatCRICRow(**_base_kwargs(
        source_reference="internal_curated:imd_dos_2024_v1",
    ))
    assert row.source_reference.startswith("internal_curated:")


def test_length_constraint_satisfied_set_for_sms():
    row = BharatCRICRow(**_base_kwargs(
        surface_format="sms", completion="Short SMS body."
    ))
    assert row.length_constraint_satisfied is True


def test_intent_label_must_be_known_literal():
    with pytest.raises(ValidationError):
        BharatCRICRow(**_base_kwargs(intent_label="not_a_real_intent"))
