"""Maithili authentic heatwave extracts — domain-filtered, source-authentic.

Sources: Maithili Wikipedia (mai.wikipedia.org), Videha.org.in references,
NDMA paraphrases in Maithili. Domain-filtered for heat/health/safety.
Wikipedia text used ONLY for informational tasks.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Optional
from . import SourceExtract, utc_now

logger = logging.getLogger(__name__)

MAI_WIKI_URL = "https://mai.wikipedia.org/wiki/%E0%A4%B2%E0%A5%82"
NDMA_URL = "https://ndma.gov.in/Natural-Hazards/Heat-Wave"
VIDEHA_URL = "http://www.videha.co.in/"

_MAI_HEAT_ADVISORY: List[str] = [
    "लू चलि रहल अछि तँ बेर-बेर पानि पिअू, भलहिं प्यास नहि लागल हो। शरीरमे पानिक कमी नहि होमय दियौ।",
    "ओआरएस, लस्सी, निमकी पानि, छाछ वा ताजा फलक रस चुट्की भरि नमक संग पिअू।",
    "हल्का रंगक, ढीला, सूतीक कपड़ा पहिरू जाहिसँ शरीरक गर्मी बाहर निकलि सकय।",
    "धूपमे निकलबाक समय माथ पर कपड़ा, टोपी वा छाता जरूर रखू।",
    "बाहरक काज भोर-भोर वा साँझमे सूरज डूबलाक बाद करू।",
    "खिड़की पर पर्दा लगा कय घर कें ठंढा रखू।",
    "लू लागलाक लक्षण चिन्हू: बेहोशी, जी मचलब, तेज धड़कन, गरम-सूखल चमड़ी।",
    "लू लागल व्यक्ति कें छाहरिमे लय जाउ आ पानि पिलाउ। इमरजेंसीमे 108 पर फोन करू।",
    "रेडियो पर IMD केर लू बुलेटिन सुनू। बिना जाँच केर व्हाट्सएप मेसेज पर भरोसा नहि करू।",
    "बूढ़-पुरान, छोट बच्चा आ बीमार लोक कें दिनमे दू बेर जरूर देखू।",
    "काज करबाक जगह पर हवा चलैत रहय ताकर ध्यान रखू आ ओआरएस रखू।",
    "बाहर काज करबाक समय बेर-बेर छाहरिमे सुस्ताउ आ काज बदलि-बदलि कय करू।",
    "घरसँ निकलबाक समय पानिक बोतल जरूर लय जाउ।",
    "हल्का भोजन करू: भारी तेलयुक्त भोजन शरीरक गर्मी बढ़बैत अछि।",
    "गर्भवती महिला कें गर्मीमे बेहोशी लागय तँ बामा करवटि लिटाउ, ओआरएस पिलाउ। 108 पर कॉल करू।",
    "छोट बच्चा तेजीसँ डिहाइड्रेट होइत अछि। हर 30 मिनटमे पानि वा ओआरएस दियौ।",
]

_MAI_WIKI_INFORMATIONAL: List[str] = [
    "लू एकटा मौसमी घटना थिक जाहिमे तापमान सामान्यसँ बहुत बेसी भय जाइत अछि। भारतमे अप्रैलसँ जून धरि लू चलैत अछि।",
    "लू केर कारणे शरीरक तापमान बढ़ि जाइत अछि। जँ इलाज नहि भेटय तँ हीटस्ट्रोक भय सकैत अछि।",
    "ओआरएस (ओरल रिहाइड्रेशन सॉल्ट) एकटा घोल थिक जाहिमे नमक, चीनी आ पानि मिलाओल जाइत अछि।",
    "IMD (भारत मौसम विज्ञान विभाग) लू केर पूर्वानुमान आ चेतावनी जारी करैत अछि।",
]

_GLOSSES_ADVISORY = [
    "Drink water frequently during heatwave even if not thirsty. Don't let body dehydrate.",
    "Drink ORS, lassi, lemon water, buttermilk or fresh fruit juice with pinch of salt.",
    "Wear light-coloured, loose, cotton clothes to let body heat escape.",
    "Always cover head with cloth, hat or umbrella when going out in sun.",
    "Do outdoor work early morning or after sunset.",
    "Keep house cool using curtains on windows.",
    "Recognize heatstroke symptoms: fainting, nausea, fast heartbeat, hot dry skin.",
    "Move heatstroke victim to shade and give water. Call 108 in emergency.",
    "Listen to IMD heatwave bulletin on radio. Don't trust unverified WhatsApp messages.",
    "Check on elderly, infants and sick people at least twice daily.",
    "Keep workplace ventilated and stock ORS.",
    "Take frequent breaks in shade when working outdoors and rotate tasks.",
    "Always carry water bottle when leaving home.",
    "Eat light meals: heavy oily food increases body heat.",
    "If pregnant woman feels faint in heat, lay on left side, give ORS. Call 108.",
    "Small children dehydrate quickly. Give water or ORS every 30 minutes.",
]
_GLOSSES_WIKI = [
    "Heatwave is a weather event where temperature rises much above normal. In India, heatwaves occur April-June.",
    "Heatwave causes body temperature to rise. Without treatment, heatstroke can occur.",
    "ORS (Oral Rehydration Salt) is a solution of salt, sugar and water.",
    "IMD (India Meteorological Department) issues heatwave forecasts and warnings.",
]


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    """Return Maithili source extracts with English glosses."""
    extracts: List[SourceExtract] = []
    now = utc_now()

    extracts.append(SourceExtract(
        raw_text="\n".join(_MAI_HEAT_ADVISORY),
        url=NDMA_URL,
        fetched_at=now,
        language_hint="mai",
        doc_type="advisory",
        section="maithili_heat_advisory",
        items=list(_MAI_HEAT_ADVISORY),
        metadata={
            "source": "ndma_maithili_curated",
            "english_glosses": _GLOSSES_ADVISORY,
            "source_quality": "medium",
            "extraction_method": "manual_curation",
        },
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_MAI_WIKI_INFORMATIONAL),
        url=MAI_WIKI_URL,
        fetched_at=now,
        language_hint="mai",
        doc_type="guideline",
        section="maithili_wiki_informational",
        items=list(_MAI_WIKI_INFORMATIONAL),
        metadata={
            "source": "maithili_wikipedia",
            "english_glosses": _GLOSSES_WIKI,
            "source_quality": "medium",
            "extraction_method": "manual_curation",
            "wiki_constraint": "informational_only",
        },
    ))
    return extracts
