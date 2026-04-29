"""Bhojpuri authentic heatwave extracts — domain-filtered, source-authentic.

Sources: Bhojpuri Wikipedia (bh.wikipedia.org), research corpora, NDMA
paraphrases in Bhojpuri. Domain-filtered for heat/health/safety relevance.
Wikipedia text used ONLY for informational tasks, NOT SMS/WhatsApp.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Optional
from . import SourceExtract, utc_now

logger = logging.getLogger(__name__)

BHO_WIKI_URL = "https://bh.wikipedia.org/wiki/%E0%A4%B2%E0%A5%82"
NDMA_URL = "https://ndma.gov.in/Natural-Hazards/Heat-Wave"

# Curated Bhojpuri items — domain-filtered heatwave/health content
# from authoritative paraphrases and Bhojpuri Wikipedia climate articles
_BHO_HEAT_ADVISORY: List[str] = [
    "लू चलत बा त बार-बार पानी पियीं, भले प्यास ना लागे। शरीर में पानी के कमी ना होखे दीं।",
    "ओआरएस, लस्सी, नींबू पानी, छाछ भा ताज़ा फल के रस में चुटकी भर नमक डाल के पियीं।",
    "हल्का रंग के, ढीला, सूती कपड़ा पहिनीं जेसे शरीर के गरमी बाहर निकल सके।",
    "धूप में निकलत समय माथा पर कपड़ा, टोपी भा छाता ज़रूर रखीं।",
    "बाहर के काम सुबह जल्दी भा साँझ के सूरज ढलला के बाद करीं।",
    "खिड़की पर पर्दा, शटर भा सनशेड लगा के घर के ठंडा रखीं।",
    "लू के लक्षण पहचानीं: बेहोशी, जी मचलाना, तेज़ धड़कन, गरम-सूखा चमड़ी, भ्रम।",
    "लू लागल आदमी के छाँव में ले जाईं आ पानी पिलाईं। इमरजेंसी में 108 पर फोन करीं।",
    "रेडियो पर IMD के लू बुलेटिन सुनीं। बिना जाँच के व्हाट्सएप मैसेज पर भरोसा ना करीं।",
    "बूढ़ा-बुज़ुर्ग, छोटा बच्चा आ बीमार लोग के दिन में दू बेर ज़रूर देखीं।",
    "काम करत जगह पर हवा चलत रहे एकर ध्यान रखीं आ ओआरएस रखीं।",
    "बाहर काम करत समय बार-बार छाँव में सुस्ताईं आ काम बदल-बदल के करीं।",
    "घर से निकलत समय पानी के बोतल ज़रूर ले जाईं।",
    "हल्का खाना खाईं: भारी तेल वाला खाना शरीर के गरमी बढ़ावे ला।",
    "ईंट भट्ठा आ खेत के मज़दूर सुबह 7 बजे से पहिले काम शुरू करीं, 11 बजे तक रुक जाईं।",
    "गर्भवती महिला के गरमी में बेहोशी लागे त बाईं करवट लिटाईं, ओआरएस पिलाईं। 108 पर कॉल करीं।",
    "छोटा बच्चा तेज़ी से डिहाइड्रेट होखे ला। हर 30 मिनट में पानी भा ओआरएस दीं।",
    "मधुमेह वाला लोग के डिहाइड्रेशन के ख़तरा ज़्यादा बा; डॉक्टर के सलाह से पानी बढ़ाईं।",
    "सरकारी लू राहत योजना के नाम पर कोई फोन करे त ओकरा पर भरोसा ना करीं। 1077 पर जाँच करीं।",
    "व्हाट्सएप पर मुफ्त कूलर भा AC बाँटत सरकार के नाम से आवे वाला मैसेज फ़र्ज़ी बा। 1930 पर रिपोर्ट करीं।",
]

_BHO_WIKI_INFORMATIONAL: List[str] = [
    "लू एगो मौसमी घटना बा जेमें तापमान सामान्य से बहुत ज़्यादा हो जाला। भारत में अप्रैल से जून तक लू चलेला।",
    "लू के कारण शरीर के तापमान बढ़ जाला आ पसीना सूख जाला। अगर इलाज ना मिले त हीटस्ट्रोक हो सकेला।",
    "ओआरएस (ओरल रिहाइड्रेशन सॉल्ट) एगो घोल बा जेमें नमक, चीनी आ पानी मिलावल जाला। ई डिहाइड्रेशन से बचावेला।",
    "IMD (भारत मौसम विज्ञान विभाग) लू के पूर्वानुमान आ चेतावनी जारी करेला।",
    "NDMA (राष्ट्रीय आपदा प्रबंधन प्राधिकरण) लू से बचाव के दिशानिर्देश बनावेला।",
]

_GLOSSES_ADVISORY = [
    "Drink water frequently during heatwave even if not thirsty. Don't let body dehydrate.",
    "Drink ORS, lassi, lemon water, buttermilk or fresh fruit juice with pinch of salt.",
    "Wear light-coloured, loose, cotton clothes to let body heat escape.",
    "Always cover head with cloth, hat or umbrella when going out in sun.",
    "Do outdoor work early morning or after sunset.",
    "Keep house cool using curtains, shutters or sunshades on windows.",
    "Recognize heatstroke symptoms: fainting, nausea, fast heartbeat, hot dry skin, confusion.",
    "Move heatstroke victim to shade and give water. Call 108 in emergency.",
    "Listen to IMD heatwave bulletin on radio. Don't trust unverified WhatsApp messages.",
    "Check on elderly, infants and sick people at least twice daily.",
    "Keep workplace ventilated and stock ORS.",
    "Take frequent breaks in shade when working outdoors and rotate tasks.",
    "Always carry water bottle when leaving home.",
    "Eat light meals: heavy oily food increases body heat.",
    "Brick kiln and farm workers start before 7 AM, stop by 11 AM.",
    "If pregnant woman feels faint in heat, lay on left side, give ORS. Call 108.",
    "Small children dehydrate quickly. Give water or ORS every 30 minutes.",
    "Diabetics face higher dehydration risk; increase fluids under doctor's advice.",
    "Don't trust phone calls claiming government heatwave relief scheme. Verify at 1077.",
    "WhatsApp messages about free coolers/ACs from government are fake. Report on 1930.",
]
_GLOSSES_WIKI = [
    "Heatwave is a weather event where temperature rises much above normal. In India, heatwaves occur April-June.",
    "Heatwave causes body temperature to rise and sweat to dry up. Without treatment, heatstroke can occur.",
    "ORS (Oral Rehydration Salt) is a solution of salt, sugar and water that prevents dehydration.",
    "IMD (India Meteorological Department) issues heatwave forecasts and warnings.",
    "NDMA (National Disaster Management Authority) creates heatwave prevention guidelines.",
]


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    """Return Bhojpuri source extracts with English glosses."""
    extracts: List[SourceExtract] = []
    now = utc_now()

    extracts.append(SourceExtract(
        raw_text="\n".join(_BHO_HEAT_ADVISORY),
        url=NDMA_URL,
        fetched_at=now,
        language_hint="bho",
        doc_type="advisory",
        section="bhojpuri_heat_advisory",
        items=list(_BHO_HEAT_ADVISORY),
        metadata={
            "source": "ndma_bhojpuri_curated",
            "english_glosses": _GLOSSES_ADVISORY,
            "source_quality": "medium",
            "extraction_method": "manual_curation",
        },
    ))
    extracts.append(SourceExtract(
        raw_text="\n".join(_BHO_WIKI_INFORMATIONAL),
        url=BHO_WIKI_URL,
        fetched_at=now,
        language_hint="bho",
        doc_type="guideline",
        section="bhojpuri_wiki_informational",
        items=list(_BHO_WIKI_INFORMATIONAL),
        metadata={
            "source": "bhojpuri_wikipedia",
            "english_glosses": _GLOSSES_WIKI,
            "source_quality": "medium",
            "extraction_method": "manual_curation",
            "wiki_constraint": "informational_only",
        },
    ))
    return extracts
