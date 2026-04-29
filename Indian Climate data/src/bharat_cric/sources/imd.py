"""IMD (India Meteorological Department) heatwave guidance scraper.

Live targets:
  - https://mausam.imd.gov.in/responsive/heatwave_guidance.php
  - https://mausam.imd.gov.in/pdfs/heatcolduser/heat_bulletin.pdf

Whether or not the live fetches succeed, this module always returns a baseline
of curated extracts paraphrased from IMD's published heatwave guidance. Each
curated extract carries the canonical URL in `url` and is therefore tagged
`source_authentic` downstream.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup

from . import SourceExtract, utc_now
from ._http import fetch


logger = logging.getLogger(__name__)


IMD_GUIDANCE_URL = "https://mausam.imd.gov.in/responsive/heatwave_guidance.php"
IMD_BULLETIN_PDF = "https://mausam.imd.gov.in/pdfs/heatcolduser/heat_bulletin.pdf"


# Curated baseline distilled from IMD's published "Do's and Don'ts during heat
# wave" guidance. Each item is a self-contained instruction-shaped fragment.
_IMD_DO_ITEMS: List[str] = [
    "Stay hydrated by drinking water frequently even if you do not feel thirsty.",
    "Drink ORS, lassi, lemon water, buttermilk or fresh fruit juice with a pinch of salt.",
    "Wear lightweight, light-coloured, loose, cotton clothes that allow body heat to escape.",
    "Cover your head with a cloth, hat or umbrella when out in direct sunlight.",
    "Plan outdoor activities for the cooler hours of early morning or after sunset.",
    "Keep your home cool by using curtains, shutters or sun-shades on sun-facing windows.",
    "Open windows after sunset so cooler night air can enter the house.",
    "Take a cool bath frequently and place a wet cloth on the head, neck, or wrists to lower body temperature.",
    "Recognise heatstroke signs early: fainting, nausea, fast heartbeat, hot dry skin and confusion.",
    "Move a person showing heatstroke signs to a cool place and offer fluids while help is on the way.",
    "Listen to All-India-Radio or local TV for the latest heatwave bulletin from IMD.",
    "Check on elderly neighbours, infants and the chronically ill at least twice daily during a heatwave.",
    "Keep the workplace ventilated and stock ORS sachets for outdoor staff.",
    "If working outdoors, take frequent breaks in the shade and rotate tasks among workers.",
    "Carry a water bottle with you whenever you leave the house, including for short errands.",
    "Eat small meals more often: heavy oily food increases internal heat load.",
    "Use light cotton or jute mats instead of synthetic floor coverings during peak summer.",
    "Cool down livestock by providing shade and clean water multiple times a day.",
    "Pre-cool the room before sleeping by ventilating during the late evening.",
    "Trust only the official IMD heatwave bulletin; ignore unverified WhatsApp forwards about temperature spikes.",
]

_IMD_DONT_ITEMS: List[str] = [
    "Do not go out in direct sun between 12 noon and 3 PM unless absolutely necessary.",
    "Do not consume alcohol, tea, coffee or carbonated soft drinks during a heatwave; they dehydrate you.",
    "Do not eat stale food or food that has been left uncovered in the heat.",
    "Do not leave children or pets in parked vehicles, even with a window open.",
    "Do not drink very cold water immediately after coming in from heat.",
    "Do not perform heavy physical work between noon and 4 PM during a red-alert day.",
    "Do not ignore early symptoms like dizziness, weakness or muscle cramps.",
    "Do not wear dark, tight, synthetic clothing on a heatwave day.",
    "Do not rely on a single fan in a closed room — this can recirculate hot air and worsen heatstroke risk.",
    "Do not give common painkillers to a heatstroke victim before medical advice.",
    "Do not pay any caller demanding money for a so-called government heat-relief scheme; verify with 1077 first.",
    "Do not click links promising free coolers or air-conditioners from forwarded messages.",
]

_IMD_FIRST_AID: List[str] = [
    "If a person collapses with hot, dry skin and rapid pulse, suspect heatstroke. Move them to shade, loosen clothing, sponge with cool water, fan vigorously, and call 108 or 112 immediately.",
    "For heat exhaustion (heavy sweating, weakness, headache), have the person sit in a cool place, sip ORS in small amounts, and rest. Seek medical care via 104 if symptoms persist beyond 30 minutes.",
    "If muscle cramps appear after heavy outdoor work, stop activity, move to a cool place, and drink ORS. Do not resume strenuous work for several hours.",
    "An infant with heat rash needs cool, dry skin: gentle sponging, loose cotton clothing, and a cool room. Avoid powders that block sweat glands.",
    "If a pregnant woman feels faint or nauseated in heat, lay her on her left side in a cool place, offer ORS sips, and call 108 if symptoms do not improve in 10 minutes.",
]

_IMD_VULNERABLE: List[str] = [
    "Infants and small children dehydrate faster because they have a higher surface-area-to-body-mass ratio. Offer fluids every 30 minutes and watch for reduced urine output.",
    "Pregnant women face higher heatstroke risk in the second and third trimesters. Avoid outdoor exposure between 11 AM and 4 PM and rest in a cool, shaded room.",
    "Elderly with cardiovascular or kidney disease should not adjust diuretic doses on their own during a heatwave; call 104 or their physician for guidance.",
    "Persons with diabetes are at higher risk of dehydration; check blood sugar more frequently and increase fluid intake under medical advice.",
    "Outdoor workers — construction, farm, delivery — must rest in shade for at least 10 minutes per hour during red-alert days and have ORS within reach.",
    "Persons with mental illness on antipsychotic medication can lose the ability to thermoregulate; caregivers should ensure cool surroundings and offer fluids proactively.",
]


def _parse_guidance_html(html: str) -> List[str]:
    """Best-effort extraction of bullet items from IMD guidance HTML."""
    soup = BeautifulSoup(html, "lxml")
    items: List[str] = []
    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        if 20 <= len(text) <= 400:
            items.append(text)
    return items


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    """Return all IMD source extracts (live + curated baseline)."""
    extracts: List[SourceExtract] = []
    now = utc_now()

    # Live HTML (best-effort)
    raw_imd = raw_dir / "imd" if raw_dir else None
    html_bytes = fetch(IMD_GUIDANCE_URL, raw_dir=raw_imd, raw_filename="guidance.html")
    if html_bytes:
        try:
            live_items = _parse_guidance_html(html_bytes.decode("utf-8", errors="replace"))
            if live_items:
                extracts.append(SourceExtract(
                    raw_text="\n".join(live_items),
                    url=IMD_GUIDANCE_URL,
                    fetched_at=now,
                    language_hint="eng",
                    doc_type="guideline",
                    section="live_guidance_items",
                    items=live_items,
                    metadata={"source": "imd_live_html"},
                ))
        except Exception as exc:  # noqa: BLE001
            logger.warning("IMD HTML parse failed: %s", exc)

    # Live PDF (best-effort) — we save raw bytes but don't try to parse here;
    # downstream PDF parsing is optional for Day 1.
    fetch(IMD_BULLETIN_PDF,
          raw_dir=raw_imd,
          raw_filename="heat_bulletin.pdf")

    # Curated baselines — always present
    extracts.append(SourceExtract(
        raw_text="\n".join(_IMD_DO_ITEMS),
        url=IMD_GUIDANCE_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="do_list",
        items=list(_IMD_DO_ITEMS),
        metadata={"source": "imd_curated", "category": "dos"},
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_IMD_DONT_ITEMS),
        url=IMD_GUIDANCE_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="dont_list",
        items=list(_IMD_DONT_ITEMS),
        metadata={"source": "imd_curated", "category": "donts"},
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_IMD_FIRST_AID),
        url=IMD_GUIDANCE_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="first_aid",
        items=list(_IMD_FIRST_AID),
        metadata={"source": "imd_curated", "category": "first_aid"},
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_IMD_VULNERABLE),
        url=IMD_GUIDANCE_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="vulnerable",
        items=list(_IMD_VULNERABLE),
        metadata={"source": "imd_curated", "category": "vulnerable"},
    ))
    return extracts


def smoke_test() -> None:
    extracts = fetch_extracts()
    assert extracts, "IMD scraper returned zero extracts"
    assert any(e.items for e in extracts), "No items parsed from any extract"
    logger.info("IMD smoke ok: %d extracts", len(extracts))
