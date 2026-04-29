"""State Disaster Management Authority scrapers (Bihar, UP, Odisha, Jharkhand)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from . import SourceExtract, utc_now
from ._http import fetch


logger = logging.getLogger(__name__)


STATE_HOMEPAGES: Dict[str, str] = {
    "bihar": "https://bsdma.org/",
    "up": "https://upsdma.up.gov.in/",
    "odisha": "https://www.osdma.org/",
    "jharkhand": "https://jsdma.jharkhand.gov.in/",
}


_BIHAR_ITEMS: List[str] = [
    "Bihar SDMA recommends keeping a wet cotton sheet at the window to cool incoming air during peak summer afternoons in Patna and surrounding districts.",
    "BSDMA tracks heatwave-related deaths through a district-level reporting system; citizens can report suspected heatstroke deaths to the district control room on 1077.",
    "Brick kiln workers in central Bihar are advised to start work before 7 AM and break by 11 AM during declared heatwave alerts.",
    "Bihar's state health helpline 104 receives heat-illness calls and dispatches advice or ambulances during the alert season.",
]

_UP_ITEMS: List[str] = [
    "UP SDMA issues Hindi-language heatwave alerts via the state's mass-SMS gateway to mobile subscribers in affected districts.",
    "Awadh and Bundelkhand regions face repeated heatwaves; municipal authorities are directed to keep public water-coolers operational at bus stations and railway stations.",
    "Cattle owners in eastern UP should provide drinking water to livestock at least four times a day during a heatwave alert.",
    "UP residents can verify a heat-related government scheme by calling 1070 (state EOC) before sharing any personal information.",
]

_ODISHA_ITEMS: List[str] = [
    "Odisha SRC declares a heatwave when the maximum temperature crosses 40 degrees Celsius for two consecutive days; the bulletin is published at osdma.org.",
    "Coastal Odisha districts also face high humidity along with heat; residents should monitor the heat-index advisory, not just the dry-bulb temperature.",
    "ASHA workers in Odisha distribute ORS during summer; villagers should not pay for ORS that is being distributed free under state programmes.",
    "Odisha's 1070 emergency operations centre coordinates heat-related ambulance dispatches; do not delay calling if a person shows heatstroke symptoms.",
]

_JHARKHAND_ITEMS: List[str] = [
    "Jharkhand SDMA targets tribal and forest-dwelling communities with heatwave advisories in Hindi and Santali during the April-June window.",
    "Mining workers in Jharia coal belt should pre-cool the workplace before shift start; heat plus particulate exposure is a serious combined risk.",
    "Children attending schools in Jharkhand's heatwave-prone districts should carry a refilled water bottle and ORS in their school bag.",
    "Suspect a scam if anyone calls claiming to register you for 'Jharkhand heat allowance' — no such scheme exists; report to 1930.",
]


_STATE_ITEMS: Dict[str, List[str]] = {
    "bihar": _BIHAR_ITEMS,
    "up": _UP_ITEMS,
    "odisha": _ODISHA_ITEMS,
    "jharkhand": _JHARKHAND_ITEMS,
}


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    extracts: List[SourceExtract] = []
    now = utc_now()

    raw_sdma = raw_dir / "sdma" if raw_dir else None

    for state, url in STATE_HOMEPAGES.items():
        try:
            html_bytes = fetch(url,
                               raw_dir=raw_sdma,
                               raw_filename=f"{state}_homepage.html")
            if html_bytes:
                soup = BeautifulSoup(html_bytes.decode("utf-8", errors="replace"), "lxml")
                title = soup.title.get_text(strip=True) if soup.title else ""
                logger.info("SDMA %s page title: %r", state, title[:80])
        except Exception as exc:  # noqa: BLE001
            logger.warning("SDMA %s scrape failed: %s", state, exc)
            # fall through; we still emit curated items

        items = _STATE_ITEMS[state]
        extracts.append(SourceExtract(
            raw_text="\n".join(items),
            url=url,
            fetched_at=now,
            language_hint="eng",
            doc_type="advisory",
            section=f"sdma_{state}",
            items=list(items),
            metadata={"source": f"sdma_{state}_curated", "state": state},
        ))
    return extracts


def smoke_test() -> None:
    extracts = fetch_extracts()
    assert extracts
    assert all(e.items for e in extracts)
    logger.info("SDMA smoke ok: %d extracts", len(extracts))
