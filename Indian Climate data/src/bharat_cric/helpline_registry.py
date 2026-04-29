"""Hard-coded registry of validated Indian emergency helpline numbers.

Any number appearing in a row's `completion` that pattern-matches a helpline
(short, 3-5 digit) is rejected unless it appears here. This stops the LLM
adaptation step from coining plausible-but-fake numbers.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Set

import requests


logger = logging.getLogger(__name__)


VALIDATED_HELPLINES: Dict[str, str] = {
    "112": "Unified Emergency Response (Police/Fire/Medical)",
    "108": "Medical Emergency Ambulance",
    "1077": "District Disaster Control Room",
    "1930": "Cyber-Crime Helpline (frauds, online scams)",
    "14416": "Tele-MANAS Mental Health Helpline",
    "104": "State Health Helpline (heat illness reporting in many states)",
    "1070": "State Emergency Operations Centre",
    "100": "Police (legacy, still active)",
    "101": "Fire (legacy)",
    "102": "Ambulance (legacy)",
    "1078": "National Emergency Operations Centre (NEOC, NDMA)",
    "1098": "CHILDLINE — Child Helpline",
    "181": "Women Helpline",
}


_HELPLINE_NUMBER_PATTERN = re.compile(r"\b\d{3,5}\b")

# 24-hour-clock times like "0830" or "1730" written with "IST" or "hrs".
_MILITARY_TIME_RE = re.compile(
    r"\b(\d{3,4})\s*(IST|UTC|GMT|hrs|hours)\b",
    flags=re.IGNORECASE,
)
# Money references like "Rs 5000" / "Rs. 5000" / "INR 5000".
_MONEY_RE = re.compile(
    r"\b(?:Rs\.?|INR|₹)\s*(\d{3,5})\b",
    flags=re.IGNORECASE,
)
# Year tokens — numeric tokens that are actually years are not helplines.
_NON_HELPLINE_DIGIT_ALLOWLIST: Set[str] = {
    str(y) for y in range(1900, 2100)
}


def is_valid_helpline(num: str) -> bool:
    """Return True if `num` is in the validated registry."""
    return num.strip() in VALIDATED_HELPLINES


def _strip_known_non_helpline_contexts(text: str) -> str:
    """Remove substrings whose digits look like helplines but aren't."""
    cleaned = _MILITARY_TIME_RE.sub(" ", text)
    cleaned = _MONEY_RE.sub(" ", cleaned)
    return cleaned


def extract_helpline_candidates(text: str) -> List[str]:
    """Pull out all 3-5 digit numeric tokens that look like helplines."""
    cleaned = _strip_known_non_helpline_contexts(text)
    return [m for m in _HELPLINE_NUMBER_PATTERN.findall(cleaned)
            if m not in _NON_HELPLINE_DIGIT_ALLOWLIST]


def find_invalid_helplines(text: str) -> List[str]:
    """Helpline-shaped numbers in `text` that are NOT in the registry."""
    return [n for n in extract_helpline_candidates(text) if not is_valid_helpline(n)]


def find_valid_helplines(text: str) -> List[str]:
    """Helpline-shaped numbers in `text` that ARE in the registry."""
    return [n for n in extract_helpline_candidates(text) if is_valid_helpline(n)]


NDMA_HELPLINE_PAGE = "https://www.ndma.gov.in/Response/Emergency-Helpline-Numbers"


def cross_check_with_ndma(timeout: float = 10.0,
                          user_agent: Optional[str] = None) -> Dict[str, bool]:
    """Fetch the NDMA helpline page and warn about any registry mismatches.

    Returns a dict mapping each registry number to whether NDMA's page mentions it.
    Network failure is non-fatal — we log a warning and return an empty dict.
    """
    headers = {"User-Agent": user_agent or "BharatCRIC/0.1 (research dataset)"}
    try:
        resp = requests.get(NDMA_HELPLINE_PAGE, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("NDMA helpline cross-check failed: %s", exc)
        return {}

    body = resp.text
    found = {num: (num in body) for num in VALIDATED_HELPLINES}
    missing = [n for n, ok in found.items() if not ok]
    if missing:
        logger.warning(
            "NDMA helpline page did not mention registry entries: %s "
            "(this may be a page-format change, not necessarily an error)",
            ", ".join(missing),
        )
    return found
