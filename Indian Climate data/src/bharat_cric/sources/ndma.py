"""NDMA 'Beat the Heat' guidance scraper with curated baseline."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup

from . import SourceExtract, utc_now
from ._http import fetch


logger = logging.getLogger(__name__)


NDMA_HEAT_URL = "https://ndma.gov.in/Natural-Hazards/Heat-Wave"
NDMA_BEAT_THE_HEAT_PDF = "https://ndma.gov.in/sites/default/files/PDF/Reports/Heat_Wave_Booklet.pdf"


_NDMA_BEAT_THE_HEAT: List[str] = [
    "Listen to All-India Radio, watch local TV news, and read newspapers for the heatwave colour code (yellow, orange, red).",
    "Wear lightweight, light-coloured, loose, porous cotton clothes and protective goggles, an umbrella or hat, shoes or chappals while going out in the sun.",
    "Avoid going out in the sun, especially between 12 noon and 3 PM.",
    "Avoid strenuous activities when the outside temperature is high. Avoid working outside between 12 noon and 3 PM.",
    "While travelling, carry water with you.",
    "Avoid alcohol, tea, coffee and carbonated soft drinks, which dehydrate the body.",
    "Avoid high-protein food and do not eat stale food.",
    "If you work outside, use a hat or an umbrella and use a damp cloth on your head, neck, face and limbs.",
    "Do not leave children or pets in parked vehicles.",
    "Recognise the signs of heat stress: dizziness, headache, heavy sweating, weakness, nausea, vomiting, cramps and fast heartbeat.",
    "Drink homemade drinks like lemon water, buttermilk and lassi or ORS to rehydrate the body.",
    "If you feel faint or ill, see a doctor or call 108 immediately.",
]

_NDMA_ORS_RECIPE: List[str] = [
    "To make a basic ORS at home, dissolve six level teaspoons of sugar and half a level teaspoon of salt in one litre of safe drinking water. Drink small sips frequently.",
    "Commercial ORS sachets from a registered pharmacist are preferred for children with diarrhoea or for elderly with chronic illness; follow the dosage on the packet.",
    "Do not use only sugar water without salt; the body needs both glucose and electrolytes to recover from heat exhaustion.",
    "Boil and cool the water before mixing ORS if its safety is uncertain. Do not use ice-cold water for ORS preparation.",
]

_NDMA_WORKER_SAFETY: List[str] = [
    "Construction, farm and brick-kiln workers should rotate tasks to share exposure and rest in shaded areas every hour.",
    "Employers should provide cool drinking water at the worksite and ORS sachets during heatwave alert days.",
    "Outdoor workers should report symptoms of heat exhaustion to the supervisor immediately and stop work.",
    "MGNREGA workers can request a change in work timings during a declared heatwave; the rural employment guidelines allow morning-only shifts.",
    "Delivery and gig workers should plan routes to include shaded rest stops and hydration breaks every 60 to 90 minutes.",
    "Pregnant outdoor workers should request a transfer to indoor or shaded duties during red-alert heatwave days.",
]

_NDMA_FRAUD_AWARENESS: List[str] = [
    "Government heat-relief assistance is never collected over a phone call. If you receive a call asking for OTP or bank details, hang up and call 1930 to report it.",
    "There is no centralised 'PM Heat Relief Yojana' as of 2026. Verify any such claim with your district control room on 1077 before forwarding.",
    "Real heatwave alerts come from IMD via the public bulletin and from your district administration; they never ask for money or bank details.",
    "Beware of WhatsApp forwards offering free coolers, fans or air-conditioners 'sponsored by the government' — these are usually phishing attempts.",
    "If you suspect a scam linked to a disaster announcement, report on the cyber-crime helpline 1930 and to the local police on 112.",
]


def _parse_ndma_html(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    items: List[str] = []
    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        if 20 <= len(text) <= 400:
            items.append(text)
    return items


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    extracts: List[SourceExtract] = []
    now = utc_now()
    raw_ndma = raw_dir / "ndma" if raw_dir else None

    html_bytes = fetch(NDMA_HEAT_URL, raw_dir=raw_ndma, raw_filename="heatwave.html")
    if html_bytes:
        try:
            live_items = _parse_ndma_html(html_bytes.decode("utf-8", errors="replace"))
            if live_items:
                extracts.append(SourceExtract(
                    raw_text="\n".join(live_items),
                    url=NDMA_HEAT_URL,
                    fetched_at=now,
                    language_hint="eng",
                    doc_type="guideline",
                    section="live_ndma_items",
                    items=live_items,
                    metadata={"source": "ndma_live_html"},
                ))
        except Exception as exc:  # noqa: BLE001
            logger.warning("NDMA HTML parse failed: %s", exc)

    fetch(NDMA_BEAT_THE_HEAT_PDF,
          raw_dir=raw_ndma,
          raw_filename="beat_the_heat.pdf")

    extracts.append(SourceExtract(
        raw_text="\n".join(_NDMA_BEAT_THE_HEAT),
        url=NDMA_HEAT_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="beat_the_heat",
        items=list(_NDMA_BEAT_THE_HEAT),
        metadata={"source": "ndma_curated", "category": "general"},
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_NDMA_ORS_RECIPE),
        url=NDMA_HEAT_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="ors_recipe",
        items=list(_NDMA_ORS_RECIPE),
        metadata={"source": "ndma_curated", "category": "ors"},
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_NDMA_WORKER_SAFETY),
        url=NDMA_HEAT_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="worker_safety",
        items=list(_NDMA_WORKER_SAFETY),
        metadata={"source": "ndma_curated", "category": "worker"},
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_NDMA_FRAUD_AWARENESS),
        url=NDMA_HEAT_URL,
        fetched_at=now,
        language_hint="eng",
        doc_type="guideline",
        section="fraud_awareness",
        items=list(_NDMA_FRAUD_AWARENESS),
        metadata={"source": "ndma_curated", "category": "fraud"},
    ))
    return extracts


def smoke_test() -> None:
    extracts = fetch_extracts()
    assert extracts
    assert any(e.items for e in extracts)
    logger.info("NDMA smoke ok: %d extracts", len(extracts))
