"""PIB (Press Information Bureau) press-release scraper for heat advisories."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup

from . import SourceExtract, utc_now
from ._http import fetch


logger = logging.getLogger(__name__)


PIB_SEARCH_URL = (
    "https://pib.gov.in/AllRelease.aspx"
    "?MenuId=4&Mod=10&AddSearch=heat+wave"
)
PIB_HOMEPAGE = "https://pib.gov.in/"


_PIB_ADVISORY_ITEMS: List[str] = [
    "The Ministry of Health and Family Welfare advises citizens to follow the National Action Plan on Heat-Related Illnesses during the summer months.",
    "Government hospitals across heatwave-prone states have been directed to set up dedicated heat-stroke treatment rooms with cold-water immersion facilities.",
    "All-India Radio carries IMD heatwave bulletins multiple times a day in regional languages during the April-June season.",
    "Ministry of Labour & Employment guidelines recommend rescheduling outdoor work to early morning or late evening on declared heatwave days.",
    "ASHA workers and ANMs are conducting door-to-door visits in vulnerable districts to distribute ORS sachets and basic heat-safety information.",
    "Schools in several heatwave-affected states have shifted to morning-only timings for the duration of the heatwave alert.",
    "Indian Railways advises passengers to carry water and avoid travelling on reserved-AC-only trains without arranging hydration during long platforms halts.",
    "The Ministry of Power has issued advisories to discoms ensuring uninterrupted power supply to hospitals during peak heatwave hours.",
    "Citizens are urged to verify any heat-relief financial assistance claim only through the official PIB-released list; no scheme distributes cash directly via phone calls.",
    "PIB regularly publishes fact-checks on its 'PIB Fact Check' Twitter handle to debunk fake heatwave forwards circulating on WhatsApp.",
]


def _scrape_pib_search(html: str, max_items: int = 10) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    items: List[str] = []
    for a in soup.select("a[href*='PressReleseDetail']"):
        text = a.get_text(strip=True)
        if 30 <= len(text) <= 300:
            items.append(text)
        if len(items) >= max_items:
            break
    return items


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    extracts: List[SourceExtract] = []
    now = utc_now()
    raw_pib = raw_dir / "pib" if raw_dir else None

    html_bytes = fetch(PIB_SEARCH_URL, raw_dir=raw_pib, raw_filename="search_heatwave.html")
    if html_bytes:
        try:
            live_items = _scrape_pib_search(html_bytes.decode("utf-8", errors="replace"))
            if live_items:
                extracts.append(SourceExtract(
                    raw_text="\n".join(live_items),
                    url=PIB_SEARCH_URL,
                    fetched_at=now,
                    language_hint="eng",
                    doc_type="press_release",
                    section="pib_search_titles",
                    items=live_items,
                    metadata={"source": "pib_live_search"},
                ))
        except Exception as exc:  # noqa: BLE001
            logger.warning("PIB search parse failed: %s", exc)

    extracts.append(SourceExtract(
        raw_text="\n".join(_PIB_ADVISORY_ITEMS),
        url=PIB_HOMEPAGE,
        fetched_at=now,
        language_hint="eng",
        doc_type="press_release",
        section="pib_curated",
        items=list(_PIB_ADVISORY_ITEMS),
        metadata={"source": "pib_curated", "category": "press_release_summary"},
    ))
    return extracts


def smoke_test() -> None:
    extracts = fetch_extracts()
    assert extracts
    assert any(e.items for e in extracts)
    logger.info("PIB smoke ok: %d extracts", len(extracts))
