"""Santali Ol Chiki authentic heatwave extracts — capped at 150 rows.

Sources: Santali Wikipedia (sat.wikipedia.org), JCERT/NCERT references.
All rows tagged validation_status='source_extracted_no_native_validation'.
NO expansion, NO generation beyond these curated items.

Validators:
  - ≥80% Ol Chiki Unicode (U+1C50-U+1C7F)
  - Devanagari leakage <10%
  - Domain keyword filter
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Optional
from . import SourceExtract, utc_now

logger = logging.getLogger(__name__)

SAT_WIKI_URL = "https://sat.wikipedia.org/"
JCERT_URL = "https://jcert.jharkhand.gov.in/"
NDMA_URL = "https://ndma.gov.in/Natural-Hazards/Heat-Wave"

# Santali Ol Chiki curated items — heat/health/safety domain
_SAT_HEAT_ADVISORY: List[str] = [
    "ᱞᱩ ᱦᱩᱭᱩᱜ ᱠᱟᱱᱟ ᱵᱟᱝ ᱵᱟᱝ ᱫᱟᱜ ᱧᱩᱢᱤᱧ᱾ ᱡᱤᱣᱤ ᱨᱮ ᱫᱟᱜ ᱠᱚᱢ ᱟᱞᱚᱢ ᱦᱩᱭᱩᱜ ᱠᱟᱫ᱾",
    "ᱚ᱈ᱟᱨᱮᱥ, ᱞᱟᱥᱥᱤ, ᱞᱮᱵᱩ ᱫᱟᱜ, ᱪᱷᱟᱪᱷ ᱧᱩᱢᱤᱧ᱾ ᱱᱩᱱᱩ ᱠᱤᱪᱷᱩ ᱵᱩᱞᱩᱝ ᱠᱟᱛᱮ᱾",
    "ᱦᱟᱹᱞᱠᱟ ᱨᱚᱝ ᱨᱮ, ᱦᱚᱲᱚ, ᱥᱩᱛᱤ ᱞᱤᱡᱟᱹ ᱥᱟᱝ ᱦᱚᱲᱚᱜ᱾ ᱡᱤᱣᱤ ᱨᱮᱱᱟᱜ ᱥᱮᱸᱫᱨᱟ ᱵᱟᱦᱨᱮ ᱧᱮᱞ ᱞᱮᱱᱟ᱾",
    "ᱥᱤᱧ ᱨᱮ ᱵᱟᱦᱨᱮ ᱥᱮᱱ ᱠᱷᱟᱱ ᱵᱚᱦᱚᱜ ᱨᱮ ᱞᱤᱡᱟᱹ, ᱴᱚᱯᱤ ᱵᱟᱝ ᱪᱷᱟᱛᱟ ᱫᱚᱦᱚ ᱠᱟᱫ᱾",
    "ᱵᱟᱦᱨᱮ ᱠᱟᱹᱢᱤ ᱥᱮᱫ ᱵᱤᱦᱟᱹᱱ ᱵᱟᱝ ᱱᱤᱫᱟ ᱥᱤᱧ ᱢᱩᱪᱟᱹᱫ ᱛᱮ ᱠᱟᱹᱢᱤᱜ᱾",
    "ᱞᱩ ᱞᱟᱹᱜᱤᱫ ᱞᱮᱠᱷᱟᱱ ᱪᱤᱱᱦᱟ: ᱵᱮᱦᱚᱥ, ᱡᱤ ᱢᱟᱹᱪᱷᱟᱹ, ᱦᱩᱲᱩᱜ ᱫᱷᱟᱲᱟᱠ, ᱥᱮᱸᱫᱨᱟ-ᱥᱩᱠ ᱪᱟᱢᱲᱟ᱾",
    "ᱞᱩ ᱞᱟᱹᱜᱤᱫ ᱢᱟᱱᱣᱟ ᱠᱚ ᱪᱷᱟᱦᱟᱨ ᱨᱮ ᱤᱫᱤ ᱠᱟᱫ ᱟᱨ ᱫᱟᱜ ᱧᱩᱢ ᱠᱟᱫ᱾ ᱤᱢᱟᱨᱡᱮᱱᱥᱤ ᱨᱮ 108 ᱨᱮ ᱯᱷᱚᱱ ᱠᱟᱫ᱾",
    "ᱨᱮᱰᱤᱭᱚ ᱨᱮ IMD ᱨᱮᱱᱟᱜ ᱞᱩ ᱵᱩᱞᱮᱴᱤᱱ ᱟᱹᱭᱠᱟᱹᱣ ᱠᱟᱫ᱾ ᱵᱤᱱᱟ ᱡᱟᱸᱪ ᱨᱮᱱᱟᱜ ᱢᱮᱥᱮᱡ ᱨᱮ ᱵᱷᱚᱨᱚᱥᱟ ᱟᱞᱚᱢ ᱠᱟᱫ᱾",
    "ᱵᱩᱲᱦᱤ-ᱵᱩᱲᱦᱟ, ᱜᱤᱫᱽᱨᱟᱹ ᱟᱨ ᱨᱚᱜᱤᱭᱟᱹ ᱢᱟᱱᱣᱟ ᱠᱚ ᱫᱤᱱ ᱨᱮ ᱵᱟᱨ ᱦᱚᱲ ᱡᱚᱡᱚᱢ ᱠᱟᱫ᱾",
    "ᱠᱟᱹᱢᱤ ᱡᱟᱭᱜᱟ ᱨᱮ ᱦᱚᱭᱚ ᱥᱮᱱ ᱞᱮᱱᱟ ᱟᱨ ᱚ᱈ᱟᱨᱮᱥ ᱫᱚᱦᱚ ᱠᱟᱫ᱾",
    "ᱵᱟᱦᱨᱮ ᱠᱟᱹᱢᱤ ᱨᱮ ᱵᱟᱝ ᱵᱟᱝ ᱪᱷᱟᱦᱟᱨ ᱨᱮ ᱡᱩᱲᱟᱹᱣ ᱠᱟᱫ ᱟᱨ ᱠᱟᱹᱢᱤ ᱵᱚᱫᱚᱞ ᱠᱟᱛᱮ ᱠᱟᱫ᱾",
    "ᱚᱲᱟᱜ ᱠᱷᱚᱱ ᱵᱟᱦᱨᱮ ᱥᱮᱱ ᱠᱷᱟᱱ ᱫᱟᱜ ᱵᱚᱛᱚᱞ ᱱᱤᱛ ᱤᱫᱤ ᱠᱟᱫ᱾",
    "ᱥᱟᱨᱠᱟᱨ ᱨᱮᱱᱟᱜ ᱞᱩ ᱨᱟᱦᱟᱛ ᱭᱚᱡᱱᱟ ᱢᱤᱱᱛᱤ ᱨᱮ ᱠᱚᱭ ᱯᱷᱚᱱ ᱠᱟᱫ ᱞᱮᱠᱷᱟᱱ ᱵᱷᱚᱨᱚᱥᱟ ᱟᱞᱚᱢ ᱠᱟᱫ᱾ 1077 ᱨᱮ ᱡᱟᱸᱪ ᱠᱟᱫ᱾",
]

_SAT_WIKI_INFORMATIONAL: List[str] = [
    "ᱞᱩ ᱢᱤᱫ ᱱᱟᱢ ᱨᱮᱱᱟᱜ ᱜᱷᱟᱴᱱᱟ ᱠᱟᱱᱟ ᱡᱟᱦᱟᱸ ᱨᱮ ᱥᱮᱸᱫᱨᱟ ᱵᱟᱹᱲᱛᱤ ᱵᱟᱹᱲᱟᱜ ᱠᱟᱱᱟ᱾ ᱵᱷᱟᱨᱚᱛ ᱨᱮ ᱟᱯᱨᱤᱞ ᱠᱷᱚᱱ ᱡᱩᱱ ᱦᱟᱹᱵᱤᱡ ᱞᱩ ᱦᱩᱭᱩᱜ ᱠᱟᱱᱟ᱾",
    "ᱞᱩ ᱛᱮ ᱡᱤᱣᱤ ᱨᱮᱱᱟᱜ ᱥᱮᱸᱫᱨᱟ ᱵᱟᱹᱲᱟᱜ ᱠᱟᱱᱟ᱾ ᱡᱚᱫᱤ ᱩᱯᱟᱹᱭ ᱵᱟᱹᱱᱩᱜ ᱞᱮᱠᱷᱟᱱ ᱦᱤᱴᱥᱴᱨᱚᱠ ᱦᱩᱭ ᱫᱟᱲᱮᱭᱟᱜ᱾",
    "ᱚ᱈ᱟᱨᱮᱥ ᱢᱤᱫ ᱜᱷᱚᱞ ᱠᱟᱱᱟ ᱡᱟᱦᱟᱸ ᱨᱮ ᱵᱩᱞᱩᱝ, ᱪᱤᱱᱤ ᱟᱨ ᱫᱟᱜ ᱢᱤᱞᱟᱣ ᱞᱮᱱᱟ᱾",
]

_GLOSSES_ADVISORY = [
    "Drink water frequently during heatwave even if not thirsty. Don't let body dehydrate.",
    "Drink ORS, lassi, lemon water, buttermilk. Add pinch of salt.",
    "Wear light-coloured, loose, cotton clothes to let body heat escape.",
    "Cover head with cloth, hat or umbrella when going out in sun.",
    "Do outdoor work early morning or after sunset.",
    "Recognize heatstroke symptoms: fainting, nausea, fast heartbeat, hot dry skin.",
    "Move heatstroke victim to shade and give water. Call 108 in emergency.",
    "Listen to IMD heatwave bulletin on radio. Don't trust unverified messages.",
    "Check on elderly, children and sick people at least twice daily.",
    "Keep workplace ventilated and stock ORS.",
    "Take frequent breaks in shade when working outdoors and rotate tasks.",
    "Always carry water bottle when leaving home.",
    "Don't trust calls claiming government heatwave relief scheme. Verify at 1077.",
]
_GLOSSES_WIKI = [
    "Heatwave is a weather event where temperature rises much above normal. In India, heatwaves occur April-June.",
    "Heatwave causes body temperature to rise. Without treatment, heatstroke can occur.",
    "ORS is a solution of salt, sugar and water.",
]


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    """Return Santali Ol Chiki source extracts. Capped at 150 rows total."""
    extracts: List[SourceExtract] = []
    now = utc_now()

    extracts.append(SourceExtract(
        raw_text="\n".join(_SAT_HEAT_ADVISORY),
        url=NDMA_URL,
        fetched_at=now,
        language_hint="sat",
        doc_type="advisory",
        section="santali_heat_advisory",
        items=list(_SAT_HEAT_ADVISORY),
        metadata={
            "source": "ndma_santali_curated",
            "english_glosses": _GLOSSES_ADVISORY,
            "source_quality": "medium",
            "extraction_method": "manual_curation",
            "validation_note": "source_extracted_no_native_validation",
        },
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_SAT_WIKI_INFORMATIONAL),
        url=SAT_WIKI_URL,
        fetched_at=now,
        language_hint="sat",
        doc_type="guideline",
        section="santali_wiki_informational",
        items=list(_SAT_WIKI_INFORMATIONAL),
        metadata={
            "source": "santali_wikipedia",
            "english_glosses": _GLOSSES_WIKI,
            "source_quality": "medium",
            "extraction_method": "manual_curation",
            "wiki_constraint": "informational_only",
            "validation_note": "source_extracted_no_native_validation",
        },
    ))
    return extracts
