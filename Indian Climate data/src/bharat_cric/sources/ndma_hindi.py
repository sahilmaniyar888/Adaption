"""NDMA Hindi heatwave guidance + PIB/AIR/State Hindi extracts.

Combines NDMA Hindi curated items, PIB Hindi press release summaries,
AIR Hindi bulletin fragments, and state government (Bihar, Rajasthan, UP)
Hindi advisories.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Optional
from . import SourceExtract, utc_now

logger = logging.getLogger(__name__)

NDMA_HINDI_URL = "https://ndma.gov.in/Natural-Hazards/Heat-Wave"
PIB_HINDI_URL = "https://pib.gov.in/indexd.aspx"
AIR_HINDI_URL = "https://newsonair.com/"

_NDMA_HINDI_BEAT_HEAT: List[str] = [
    "ऑल इंडिया रेडियो सुनें, स्थानीय टीवी देखें और अखबार में हीटवेव कलर कोड (पीला, नारंगी, लाल) पढ़ें।",
    "धूप में बाहर जाते समय हल्के रंग के, ढीले, सूती कपड़े, छाता, टोपी और चप्पल पहनें।",
    "दोपहर 12 से 3 बजे के बीच धूप में बाहर जाने से बचें।",
    "बाहर का तापमान ज़्यादा होने पर कठिन शारीरिक गतिविधि से बचें।",
    "यात्रा करते समय अपने साथ पानी रखें।",
    "शराब, चाय, कॉफ़ी और कोल्ड ड्रिंक से बचें, ये शरीर से पानी कम करते हैं।",
    "ज़्यादा प्रोटीन वाला और बासी भोजन न खाएं।",
    "बाहर काम करें तो टोपी या छाता इस्तेमाल करें और सिर, गर्दन पर गीला कपड़ा रखें।",
    "बच्चों या पालतू जानवरों को पार्क की हुई गाड़ी में न छोड़ें।",
    "लू के लक्षण पहचानें: चक्कर, सिरदर्द, ज़्यादा पसीना, कमज़ोरी, उल्टी, ऐंठन।",
    "घर पर ओआरएस बनाएं: एक लीटर पानी में छह चम्मच चीनी और आधा चम्मच नमक मिलाएं।",
    "बीमार लगे तो तुरंत डॉक्टर से मिलें या 108 पर कॉल करें।",
]

_PIB_HINDI_ITEMS: List[str] = [
    "स्वास्थ्य मंत्रालय ने गर्मी में लू से संबंधित बीमारियों पर राष्ट्रीय कार्य योजना का पालन करने की सलाह दी है।",
    "लू प्रभावित राज्यों के सरकारी अस्पतालों में हीटस्ट्रोक उपचार कक्ष बनाने के निर्देश दिए गए हैं।",
    "ऑल इंडिया रेडियो अप्रैल-जून में दिन में कई बार क्षेत्रीय भाषाओं में IMD हीटवेव बुलेटिन प्रसारित करता है।",
    "श्रम मंत्रालय ने लू के दिनों में बाहरी काम को सुबह या शाम में करने की सिफारिश की है।",
    "आशा कार्यकर्ता कमज़ोर ज़िलों में घर-घर जाकर ओआरएस बांट रही हैं और लू से बचाव की जानकारी दे रही हैं।",
    "कई लू प्रभावित राज्यों में स्कूलों की समय-सारणी केवल सुबह की कर दी गई है।",
    "भारतीय रेलवे यात्रियों को पानी साथ रखने और लंबे स्टॉप पर पानी की व्यवस्था करने की सलाह देता है।",
    "बिजली मंत्रालय ने लू के चरम घंटों में अस्पतालों को निर्बाध बिजली आपूर्ति सुनिश्चित करने का निर्देश दिया है।",
    "किसी भी लू राहत योजना की पुष्टि केवल PIB की आधिकारिक सूची से करें; फ़ोन पर पैसे बांटने का कोई योजना नहीं है।",
    "PIB नियमित रूप से अपने फैक्ट चेक हैंडल पर व्हाट्सएप पर फैले फ़र्ज़ी लू संदेशों का खंडन करता है।",
]

_AIR_HINDI_ITEMS: List[str] = [
    "[उद्घोषक] श्रोताओं, भारत मौसम विज्ञान विभाग ने आज लू का रेड अलर्ट जारी किया है। दोपहर 12 से 4 बजे तक बाहर न निकलें। आपातकाल में 108 पर कॉल करें।",
    "[उद्घोषक] IMD के अनुसार अगले 48 घंटों में तापमान 45 डिग्री से ऊपर रहेगा। बुज़ुर्गों और बच्चों का विशेष ध्यान रखें। हेल्पलाइन 104 पर संपर्क करें।",
    "[उद्घोषक] राष्ट्रीय आपदा प्रबंधन प्राधिकरण की सलाह: ओआरएस पिएं, हल्के कपड़े पहनें, छाया में रहें। ज़िला नियंत्रण कक्ष: 1077।",
    "[उद्घोषक] श्रमिक भाइयों, लू के दिनों में दोपहर का काम बंद रखें। MGNREGA में सुबह की शिफ्ट का अनुरोध करें। स्वास्थ्य हेल्पलाइन: 104।",
]

_STATE_HINDI_BIHAR: List[str] = [
    "बिहार SDMA: पटना और आसपास के ज़िलों में दोपहर की गर्मी से बचने के लिए खिड़की पर गीली सूती चादर लगाएं।",
    "बिहार में लू से संदिग्ध मौत की सूचना ज़िला नियंत्रण कक्ष 1077 पर दें।",
    "मध्य बिहार के ईंट भट्टा मज़दूर सुबह 7 बजे से पहले काम शुरू करें और 11 बजे तक रुक जाएं।",
    "बिहार स्वास्थ्य हेल्पलाइन 104 लू से बीमारी की कॉल लेती है और एम्बुलेंस भेजती है।",
]

_STATE_HINDI_RAJASTHAN: List[str] = [
    "राजस्थान में लू के दौरान सार्वजनिक जल कूलर बस अड्डों और रेलवे स्टेशनों पर चालू रखे जाएं।",
    "जोधपुर, बीकानेर और जैसलमेर में तापमान 48 डिग्री तक पहुंच सकता है। बाहर काम करने वाले हर घंटे छाया में आराम करें।",
    "राजस्थान सरकार की लू हेल्पलाइन 1070 पर आपातकालीन मदद लें।",
    "पशुपालकों को दिन में चार बार पशुओं को पानी पिलाना चाहिए और छाया की व्यवस्था करनी चाहिए।",
]

_STATE_HINDI_UP: List[str] = [
    "UP SDMA प्रभावित ज़िलों में मोबाइल पर हिंदी में लू अलर्ट SMS भेजता है।",
    "अवध और बुंदेलखंड में बार-बार लू चलती है; नगर निगम बस स्टेशनों पर सार्वजनिक कूलर चालू रखें।",
    "पूर्वी UP में पशु मालिक लू के दौरान पशुओं को दिन में कम से कम चार बार पानी पिलाएं।",
    "UP निवासी किसी भी लू संबंधी सरकारी योजना की पुष्टि 1070 (राज्य EOC) पर करें।",
]

# Glosses
_GLOSSES_NDMA = [
    "Listen to All India Radio, watch local TV, read newspaper for heatwave colour code.",
    "Wear light, loose cotton clothes, umbrella, hat and chappals when going out.",
    "Avoid going out between 12 noon and 3 PM.",
    "Avoid strenuous physical activity when outside temperature is high.",
    "Carry water with you while travelling.",
    "Avoid alcohol, tea, coffee and cold drinks — they dehydrate the body.",
    "Do not eat high-protein or stale food.",
    "Use hat or umbrella outdoors; keep wet cloth on head and neck.",
    "Do not leave children or pets in parked vehicles.",
    "Recognize heatstroke signs: dizziness, headache, heavy sweating, weakness, vomiting, cramps.",
    "Make ORS at home: six spoons sugar and half spoon salt in one litre water.",
    "If feeling unwell, see doctor immediately or call 108.",
]
_GLOSSES_PIB = [
    "Health Ministry advises following National Action Plan on heat-related illnesses.",
    "Govt hospitals directed to set up heatstroke treatment rooms in affected states.",
    "AIR broadcasts IMD heatwave bulletins multiple times daily in regional languages during Apr-Jun.",
    "Labour Ministry recommends rescheduling outdoor work to morning/evening on heatwave days.",
    "ASHA workers distributing ORS door-to-door in vulnerable districts.",
    "Schools shifted to morning-only timings in heatwave-affected states.",
    "Railways advises passengers to carry water and arrange hydration during long stops.",
    "Power Ministry directs uninterrupted power supply to hospitals during peak heatwave hours.",
    "Verify heat-relief claims only through official PIB list; no scheme distributes cash via phone.",
    "PIB regularly debunks fake heatwave forwards on its Fact Check handle.",
]
_GLOSSES_AIR = [
    "IMD has issued red alert for heatwave today. Do not go out 12-4 PM. Emergency: 108.",
    "Temperature to stay above 45°C for next 48 hours. Take special care of elderly and children. Helpline: 104.",
    "NDMA advice: Drink ORS, wear light clothes, stay in shade. District control room: 1077.",
    "Workers: stop afternoon work on heatwave days. Request morning shift under MGNREGA. Health helpline: 104.",
]
_GLOSSES_BIHAR = [
    "Bihar SDMA: hang wet cotton sheet on window to cool air in Patna districts.",
    "Report suspected heatstroke deaths to district control room 1077 in Bihar.",
    "Brick kiln workers in central Bihar should start before 7 AM, stop by 11 AM.",
    "Bihar health helpline 104 takes heat illness calls and dispatches ambulances.",
]
_GLOSSES_RAJASTHAN = [
    "Keep public water coolers operational at bus/railway stations in Rajasthan during heatwave.",
    "Temperature can reach 48°C in Jodhpur/Bikaner/Jaisalmer. Outdoor workers rest in shade hourly.",
    "Get emergency help on Rajasthan heatwave helpline 1070.",
    "Livestock owners should water animals four times daily and provide shade.",
]
_GLOSSES_UP = [
    "UP SDMA sends Hindi heatwave alert SMS to mobiles in affected districts.",
    "Awadh and Bundelkhand face repeated heatwaves; keep public coolers operational at bus stations.",
    "Eastern UP cattle owners should water livestock at least four times daily during heatwave.",
    "UP residents verify heat-related govt schemes by calling 1070 (state EOC).",
]


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    """Return Hindi NDMA/PIB/AIR/state extracts with English glosses."""
    extracts: List[SourceExtract] = []
    now = utc_now()
    sources = [
        (_NDMA_HINDI_BEAT_HEAT, _GLOSSES_NDMA, NDMA_HINDI_URL, "hindi_ndma_beat_heat", "ndma_hindi_curated", "high"),
        (_PIB_HINDI_ITEMS, _GLOSSES_PIB, PIB_HINDI_URL, "hindi_pib_advisory", "pib_hindi_curated", "high"),
        (_AIR_HINDI_ITEMS, _GLOSSES_AIR, AIR_HINDI_URL, "hindi_air_bulletin", "air_hindi_curated", "high"),
        (_STATE_HINDI_BIHAR, _GLOSSES_BIHAR, "https://bsdma.org/", "hindi_sdma_bihar", "sdma_bihar_hindi", "high"),
        (_STATE_HINDI_RAJASTHAN, _GLOSSES_RAJASTHAN, "https://sdmraj.rajasthan.gov.in/", "hindi_sdma_rajasthan", "sdma_rajasthan_hindi", "high"),
        (_STATE_HINDI_UP, _GLOSSES_UP, "https://upsdma.up.gov.in/", "hindi_sdma_up", "sdma_up_hindi", "high"),
    ]
    for items, glosses, url, section, src_name, quality in sources:
        extracts.append(SourceExtract(
            raw_text="\n".join(items),
            url=url,
            fetched_at=now,
            language_hint="hin",
            doc_type="guideline",
            section=section,
            items=list(items),
            metadata={
                "source": src_name,
                "english_glosses": glosses,
                "source_quality": quality,
                "extraction_method": "manual_curation",
            },
        ))
    return extracts
