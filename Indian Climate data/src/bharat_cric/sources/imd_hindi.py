"""IMD Hindi heatwave guidance — curated authoritative extracts.

Source: IMD publishes Hindi versions of heatwave Do's/Don'ts on mausam.imd.gov.in.
Each item below is paraphrased from the official Hindi bulletin.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Optional
from . import SourceExtract, utc_now
from ._http import fetch

logger = logging.getLogger(__name__)

IMD_HINDI_URL = "https://mausam.imd.gov.in/responsive/heatwave_guidance.php"

_IMD_HINDI_DOS: List[str] = [
    "बार-बार पानी पिएं, भले ही प्यास न लगे। शरीर में पानी की कमी न होने दें।",
    "ओआरएस, लस्सी, नींबू पानी, छाछ या ताज़ा फलों का रस चुटकी भर नमक के साथ पिएं।",
    "हल्के रंग के, ढीले, सूती कपड़े पहनें जिससे शरीर की गर्मी बाहर निकल सके।",
    "धूप में निकलते समय सिर पर कपड़ा, टोपी या छाता ज़रूर रखें।",
    "बाहरी काम सुबह जल्दी या शाम को सूरज ढलने के बाद करें।",
    "खिड़कियों पर पर्दे, शटर या सनशेड लगाकर घर को ठंडा रखें।",
    "शाम को खिड़कियां खोलें ताकि ठंडी हवा अंदर आ सके।",
    "बार-बार ठंडे पानी से नहाएं और सिर, गर्दन या कलाई पर गीला कपड़ा रखें।",
    "लू लगने के लक्षणों को पहचानें: बेहोशी, जी मिचलाना, तेज़ धड़कन, गर्म-सूखी त्वचा और भ्रम।",
    "लू लगे व्यक्ति को छाया में ले जाएं और मदद आने तक पानी पिलाएं। आपातकाल में 108 पर कॉल करें।",
    "ऑल इंडिया रेडियो या स्थानीय टीवी पर IMD का ताज़ा हीटवेव बुलेटिन सुनें।",
    "बुज़ुर्ग पड़ोसियों, शिशुओं और लंबे समय से बीमार लोगों की दिन में कम से कम दो बार जांच करें।",
    "कार्यस्थल को हवादार रखें और बाहरी कर्मचारियों के लिए ओआरएस रखें।",
    "बाहर काम करते समय बार-बार छाया में आराम करें और काम बदल-बदल कर करें।",
    "घर से निकलते समय हमेशा पानी की बोतल साथ रखें, छोटे कामों के लिए भी।",
    "छोटे-छोटे भोजन करें: भारी तैलीय भोजन शरीर की गर्मी बढ़ाता है।",
    "गर्मी में सिंथेटिक की जगह सूती या जूट की चटाई इस्तेमाल करें।",
    "पशुओं को छाया में रखें और दिन में कई बार साफ पानी पिलाएं।",
    "सोने से पहले शाम को कमरे को हवादार करके ठंडा करें।",
    "केवल आधिकारिक IMD बुलेटिन पर भरोसा करें; तापमान बढ़ने के अपुष्ट व्हाट्सएप फॉरवर्ड पर ध्यान न दें।",
]

_IMD_HINDI_DONTS: List[str] = [
    "दोपहर 12 बजे से 3 बजे के बीच बिना ज़रूरत के धूप में बाहर न जाएं।",
    "लू के दौरान शराब, चाय, कॉफ़ी या कार्बोनेटेड ड्रिंक न पिएं; ये शरीर को निर्जलित करती हैं।",
    "बासी या खुला रखा भोजन न खाएं जो गर्मी में ख़राब हो सकता है।",
    "बच्चों या पालतू जानवरों को खड़ी गाड़ी में न छोड़ें, भले ही खिड़की खुली हो।",
    "गर्मी से आने के तुरंत बाद बहुत ठंडा पानी न पिएं।",
    "रेड अलर्ट वाले दिन दोपहर 12 से 4 बजे के बीच भारी शारीरिक काम न करें।",
    "चक्कर, कमज़ोरी या मांसपेशियों में ऐंठन जैसे शुरुआती लक्षणों को नज़रअंदाज़ न करें।",
    "हीटवेव के दिन काले, टाइट, सिंथेटिक कपड़े न पहनें।",
    "बंद कमरे में एक अकेले पंखे पर निर्भर न रहें — यह गर्म हवा को घुमाता रहता है।",
    "लू लगे व्यक्ति को बिना चिकित्सक की सलाह के दर्दनिवारक दवा न दें।",
]

_IMD_HINDI_FIRST_AID: List[str] = [
    "अगर कोई गर्म-सूखी त्वचा और तेज़ नब्ज़ के साथ गिर जाए तो लू का संदेह करें। उसे छाया में ले जाएं, कपड़े ढीले करें, ठंडे पानी से स्पंज करें और तुरंत 108 या 112 पर कॉल करें।",
    "हीट एग्ज़ॉशन (भारी पसीना, कमज़ोरी, सिरदर्द) होने पर व्यक्ति को ठंडी जगह बिठाएं, ओआरएस पिलाएं। 30 मिनट में सुधार न हो तो 104 पर कॉल करें।",
    "बाहरी काम के बाद मांसपेशियों में ऐंठन हो तो काम बंद करें, ठंडी जगह जाएं और ओआरएस पिएं।",
    "शिशु को हीट रैश हो तो हल्के सूती कपड़े पहनाएं, धीरे से स्पंज करें और ठंडे कमरे में रखें।",
    "गर्भवती महिला को गर्मी में बेहोशी या जी मिचलाए तो उसे बाईं करवट लिटाएं, ओआरएस पिलाएं। 10 मिनट में सुधार न हो तो 108 पर कॉल करें।",
]

_IMD_HINDI_VULNERABLE: List[str] = [
    "शिशु और छोटे बच्चे तेज़ी से डिहाइड्रेट होते हैं। हर 30 मिनट में तरल पदार्थ दें और पेशाब कम होने पर सतर्क हों।",
    "गर्भवती महिलाओं को दूसरी और तीसरी तिमाही में लू का ख़तरा ज़्यादा होता है। सुबह 11 से शाम 4 बजे तक बाहर न जाएं।",
    "हृदय या गुर्दे की बीमारी वाले बुज़ुर्ग लू के दौरान अपनी दवा की खुराक खुद न बदलें; 104 पर डॉक्टर से सलाह लें।",
    "मधुमेह रोगियों को डिहाइड्रेशन का ख़तरा अधिक है; ब्लड शुगर बार-बार जांचें और डॉक्टर की सलाह से पानी बढ़ाएं।",
    "बाहरी कामगार — निर्माण, खेत, डिलीवरी — रेड अलर्ट के दिन हर घंटे कम से कम 10 मिनट छाया में आराम करें।",
    "मानसिक रोगी जो एंटीसाइकोटिक दवा ले रहे हैं उनकी थर्मोरेग्युलेशन क्षमता कम होती है; देखभालकर्ता ठंडा वातावरण सुनिश्चित करें।",
    "विकलांग व्यक्ति जो बिस्तर पर हैं उन्हें लू में पर्याप्त पानी मिलना चाहिए; 104 पर चिकित्सा सहायता उपलब्ध है।",
    "स्कूल जाने वाले बच्चों को पानी की बोतल और ओआरएस स्कूल बैग में रखना चाहिए।",
]

_IMD_HINDI_WORKER_SAFETY: List[str] = [
    "निर्माण, खेत और ईंट भट्टा मज़दूरों को हर घंटे काम बदलना चाहिए और छाया में आराम करना चाहिए।",
    "नियोक्ता को कार्यस्थल पर ठंडा पानी और ओआरएस सैशे उपलब्ध कराने चाहिए।",
    "बाहरी कामगारों को लू के लक्षण दिखने पर तुरंत सुपरवाइज़र को बताना चाहिए और काम बंद करना चाहिए।",
    "MGNREGA मज़दूर लू घोषित होने पर काम के समय में बदलाव का अनुरोध कर सकते हैं; सुबह की शिफ्ट की अनुमति है।",
    "डिलीवरी और गिग कर्मचारी अपने रूट में छायादार विश्राम स्थल शामिल करें और हर 60-90 मिनट में पानी पिएं।",
    "गर्भवती बाहरी कामगार रेड अलर्ट हीटवेव दिनों में अंदर या छायादार ड्यूटी का अनुरोध करें।",
    "खदान मज़दूरों को शिफ्ट शुरू होने से पहले कार्यस्थल को पहले ठंडा करना चाहिए; गर्मी और धूल का संयोजन गंभीर ख़तरा है।",
    "लू के दिनों में रात की शिफ्ट को प्राथमिकता दें जहां संभव हो। दोपहर 12 से 4 बजे तक बाहरी काम बंद रखें।",
]

_IMD_HINDI_FRAUD: List[str] = [
    "सरकारी लू राहत सहायता कभी फ़ोन कॉल पर नहीं ली जाती। OTP या बैंक विवरण मांगने वाले कॉल पर 1930 पर रिपोर्ट करें।",
    "2026 तक कोई केंद्रीय 'पीएम हीट रिलीफ योजना' नहीं है। ऐसे दावे की पुष्टि 1077 पर करें।",
    "असली हीटवेव अलर्ट IMD और ज़िला प्रशासन से आते हैं; वे कभी पैसे या बैंक विवरण नहीं मांगते।",
    "व्हाट्सएप पर 'सरकार प्रायोजित' मुफ्त कूलर, पंखे या एसी बांटने के मैसेज फ़िशिंग हो सकते हैं।",
    "आपदा घोषणा से जुड़े स्कैम का शक हो तो 1930 (साइबर-क्राइम हेल्पलाइन) और 112 पर रिपोर्ट करें।",
    "किसी भी अज्ञात लिंक पर क्लिक न करें जो लू से संबंधित मुआवज़ा या राहत का वादा करता है।",
]

_IMD_HINDI_ORS: List[str] = [
    "घर पर ओआरएस बनाने के लिए एक लीटर सुरक्षित पीने के पानी में छह चम्मच चीनी और आधा चम्मच नमक घोलें। बार-बार छोटी घूंट पिएं।",
    "बच्चों और बुज़ुर्गों के लिए रजिस्टर्ड फार्मेसी से मिलने वाले ओआरएस सैशे पसंद करें; पैकेट पर लिखी खुराक का पालन करें।",
    "केवल चीनी का पानी बिना नमक के न पिएं; शरीर को ग्लूकोज़ और इलेक्ट्रोलाइट्स दोनों चाहिए।",
    "ओआरएस बनाने से पहले पानी की सुरक्षा अनिश्चित हो तो पहले उबालकर ठंडा करें। बर्फ़ जैसा ठंडा पानी न इस्तेमाल करें।",
    "ओआरएस बनाने के बाद 24 घंटे के भीतर पी लें; बचा हुआ ओआरएस फ़ेंक दें।",
    "लू में दस्त होने पर ओआरएस के साथ-साथ ज़िंक की गोली भी डॉक्टर की सलाह से लें।",
]

_GLOSSES_VULNERABLE = [
    "Infants dehydrate faster. Offer fluids every 30 minutes and watch for reduced urine.",
    "Pregnant women face higher heatstroke risk in 2nd/3rd trimester. Avoid outdoor exposure 11 AM-4 PM.",
    "Elderly with heart/kidney disease should not adjust medications during heatwave; consult doctor via 104.",
    "Diabetics face higher dehydration risk; check blood sugar frequently and increase fluids under medical advice.",
    "Outdoor workers — construction, farm, delivery — rest in shade at least 10 min per hour on red alert days.",
    "Patients on antipsychotic medication lose thermoregulation ability; caregivers ensure cool surroundings.",
    "Bedridden disabled persons must receive adequate water during heatwave; medical help available at 104.",
    "School children should carry water bottle and ORS in school bag.",
]
_GLOSSES_WORKER = [
    "Construction, farm and brick kiln workers should rotate tasks hourly and rest in shade.",
    "Employers should provide cool drinking water and ORS sachets at worksite.",
    "Outdoor workers should report heat exhaustion symptoms to supervisor immediately and stop work.",
    "MGNREGA workers can request work timing change during declared heatwave; morning shifts allowed.",
    "Delivery and gig workers should plan routes with shaded rest stops and hydration breaks every 60-90 min.",
    "Pregnant outdoor workers should request transfer to indoor/shaded duties on red alert days.",
    "Mine workers should pre-cool workplace before shift; heat plus particulate is a serious combined risk.",
    "Prioritize night shifts where possible during heatwave days. Stop outdoor work noon to 4 PM.",
]
_GLOSSES_FRAUD = [
    "Govt heat-relief is never collected over phone. Report calls asking OTP/bank details to 1930.",
    "No centralized PM Heat Relief Yojana exists as of 2026. Verify claims at 1077.",
    "Real heatwave alerts come from IMD and district admin; they never ask for money or bank details.",
    "WhatsApp messages about free govt-sponsored coolers/fans/ACs may be phishing attempts.",
    "Report disaster-related scams to 1930 (cyber-crime helpline) and 112.",
    "Do not click unknown links promising heatwave-related compensation or relief.",
]
_GLOSSES_ORS = [
    "Make ORS at home: dissolve 6 spoons sugar and half spoon salt in 1 litre safe water. Sip frequently.",
    "For children/elderly, prefer commercial ORS from registered pharmacy; follow dosage on packet.",
    "Do not use sugar water without salt; body needs both glucose and electrolytes.",
    "Boil and cool water before mixing ORS if safety uncertain. Don't use ice-cold water.",
    "Consume ORS within 24 hours of preparation; discard leftover.",
    "For diarrhea during heatwave, take zinc tablet along with ORS under doctor's advice.",
]

# English glosses for all Hindi items (parallel text)
_GLOSSES_DOS = [
    "Drink water frequently even if not thirsty. Do not let the body get dehydrated.",
    "Drink ORS, lassi, lemon water, buttermilk or fresh fruit juice with a pinch of salt.",
    "Wear light-coloured, loose, cotton clothes to let body heat escape.",
    "Always cover your head with cloth, hat or umbrella when going out in sunlight.",
    "Do outdoor work early morning or after sunset.",
    "Keep the house cool using curtains, shutters or sunshades on windows.",
    "Open windows in the evening to let cool air in.",
    "Bathe frequently with cool water and keep a wet cloth on head, neck or wrists.",
    "Recognize heatstroke symptoms: fainting, nausea, rapid heartbeat, hot dry skin, confusion.",
    "Move heatstroke victim to shade and give fluids while help arrives. Call 108 in emergency.",
    "Listen to All India Radio or local TV for IMD's latest heatwave bulletin.",
    "Check on elderly neighbours, infants and chronically ill people at least twice daily.",
    "Keep the workplace ventilated and stock ORS for outdoor staff.",
    "Take frequent breaks in shade when working outdoors and rotate tasks.",
    "Always carry a water bottle when leaving home, even for short errands.",
    "Eat small meals: heavy oily food increases body heat.",
    "Use cotton or jute mats instead of synthetic floor coverings in summer.",
    "Provide shade and clean water to livestock multiple times a day.",
    "Cool the room before sleeping by ventilating in the evening.",
    "Trust only official IMD bulletin; ignore unverified WhatsApp forwards about temperature spikes.",
]
_GLOSSES_DONTS = [
    "Do not go out in direct sun between 12 noon and 3 PM unless necessary.",
    "Do not consume alcohol, tea, coffee or carbonated drinks during heatwave; they dehydrate.",
    "Do not eat stale or uncovered food that may spoil in heat.",
    "Do not leave children or pets in parked vehicles even with window open.",
    "Do not drink very cold water immediately after coming from heat.",
    "Do not do heavy physical work between noon and 4 PM on red alert days.",
    "Do not ignore early symptoms like dizziness, weakness or muscle cramps.",
    "Do not wear dark, tight, synthetic clothing on heatwave days.",
    "Do not rely on a single fan in closed room — it recirculates hot air.",
    "Do not give painkillers to heatstroke victim without medical advice.",
]
_GLOSSES_FIRST_AID = [
    "If someone collapses with hot dry skin and rapid pulse, suspect heatstroke. Move to shade, loosen clothes, sponge with cool water, call 108 or 112.",
    "For heat exhaustion (heavy sweating, weakness, headache), sit in cool place, sip ORS. Call 104 if no improvement in 30 minutes.",
    "For muscle cramps after outdoor work, stop activity, go to cool place, drink ORS.",
    "For infant heat rash, use loose cotton clothes, gentle sponging, keep in cool room.",
    "If pregnant woman feels faint in heat, lay on left side, give ORS sips. Call 108 if no improvement in 10 minutes.",
]


def fetch_extracts(raw_dir: Optional[Path] = None) -> List[SourceExtract]:
    """Return Hindi IMD source extracts with English glosses."""
    extracts: List[SourceExtract] = []
    now = utc_now()

    for items, glosses, section, category in [
        (_IMD_HINDI_DOS, _GLOSSES_DOS, "hindi_do_list", "dos"),
        (_IMD_HINDI_DONTS, _GLOSSES_DONTS, "hindi_dont_list", "donts"),
        (_IMD_HINDI_FIRST_AID, _GLOSSES_FIRST_AID, "hindi_first_aid", "first_aid"),
        (_IMD_HINDI_VULNERABLE, _GLOSSES_VULNERABLE, "hindi_vulnerable", "vulnerable"),
        (_IMD_HINDI_WORKER_SAFETY, _GLOSSES_WORKER, "hindi_worker_safety", "worker_safety"),
        (_IMD_HINDI_FRAUD, _GLOSSES_FRAUD, "hindi_fraud_awareness", "fraud"),
        (_IMD_HINDI_ORS, _GLOSSES_ORS, "hindi_ors_recipe", "ors"),
    ]:
        extracts.append(SourceExtract(
            raw_text="\n".join(items),
            url=IMD_HINDI_URL,
            fetched_at=now,
            language_hint="hin",
            doc_type="guideline",
            section=section,
            items=list(items),
            metadata={
                "source": "imd_hindi_curated",
                "category": category,
                "english_glosses": glosses,
                "source_quality": "high",
                "extraction_method": "manual_curation",
            },
        ))
    return extracts

