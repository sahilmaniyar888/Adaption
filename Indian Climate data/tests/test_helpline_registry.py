"""Tests for the helpline registry helpers."""
from __future__ import annotations

from bharat_cric.helpline_registry import (
    VALIDATED_HELPLINES,
    extract_helpline_candidates,
    find_invalid_helplines,
    find_valid_helplines,
    is_valid_helpline,
)


def test_known_helplines_validate():
    assert is_valid_helpline("108")
    assert is_valid_helpline("112")
    assert is_valid_helpline("1077")
    assert is_valid_helpline("1930")


def test_unknown_helpline_rejected():
    assert not is_valid_helpline("9999")
    assert not is_valid_helpline("1234")


def test_extract_candidates_filters_year_tokens():
    text = "In 2026 the IMD bulletin says call 108 if needed."
    cands = extract_helpline_candidates(text)
    assert "108" in cands
    assert "2026" not in cands


def test_find_invalid_flags_only_unknown():
    text = "Call 108 not 9999."
    invalid = find_invalid_helplines(text)
    assert invalid == ["9999"]


def test_find_valid_returns_registered():
    text = "Dial 112 or 108 for emergencies."
    valid = find_valid_helplines(text)
    assert set(valid) == {"112", "108"}


def test_registry_has_minimum_required_entries():
    for required in ("112", "108", "1077", "1930", "104"):
        assert required in VALIDATED_HELPLINES
