"""Convert raw lexicon + contextual rows into instruction-tuning samples.

For every lexical term we select a category-aware template, substitute the
medical concept, and emit one row that satisfies:
    * text_en is 8-20 words
    * gloss_sequence is 5-12 uppercase tokens following ISL grammar
    * category / intent / urgency / difficulty are populated
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .contextual import all_contextual
from .lexicon import all_lexical
from .schema import Category, Difficulty, Intent, Urgency

# Category buckets — different medical concepts need different prompt shapes.
BODY_PART_CATS = {Category.ANATOMY}
SYMPTOM_CATS = {Category.SYMPTOMS}
DISEASE_CATS = {
    Category.CARDIOLOGY, Category.PULMONOLOGY, Category.NEUROLOGY,
    Category.ONCOLOGY, Category.ENDOCRINOLOGY, Category.GASTROENTEROLOGY,
    Category.NEPHROLOGY, Category.ORTHOPEDICS, Category.DERMATOLOGY,
    Category.OPHTHALMOLOGY, Category.ENT, Category.REPRODUCTIVE,
}
MED_CATS = {Category.PHARMACY}
DIAG_CATS = {Category.DIAGNOSTICS}
VACC_CATS = {Category.VACCINATION}
EMER_CATS = {Category.FIRST_AID}
MATERNAL_CATS = {Category.MATERNAL}
PEDIATRIC_CATS = {Category.PEDIATRICS}
PSYCH_CATS = {Category.PSYCHIATRY}
ANES_CATS = {Category.ANESTHESIOLOGY}
PUBHEALTH_CATS = {Category.PUBLIC_HEALTH}
HOSPITAL_CATS = {Category.HOSPITAL}
DENTAL_CATS = {Category.DENTISTRY}


@dataclass(frozen=True)
class Template:
    en: str        # uses {en} placeholder
    hi: str        # uses {hi} placeholder
    gloss: str     # uses {gloss} placeholder; must produce 5-12 uppercase tokens
    intent: Intent


# --- Templates per concept type -----------------------------------------
BODY_PART_TEMPLATES: list[Template] = [
    Template(
        "The patient is experiencing pain in the {en} for two days now.",
        "मरीज़ को {hi} में दो दिन से दर्द हो रहा है।",
        "{gloss} PAIN, TWO-DAY, DOCTOR CONSULT MUST",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Doctor is examining the {en} for swelling and signs of infection.",
        "डॉक्टर {hi} में सूजन और संक्रमण की जांच कर रहे हैं।",
        "DOCTOR {gloss} CHECK, SWELL INFECT FIND",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Patient injured their {en} during a fall and needs immediate care.",
        "मरीज़ ने गिरने पर {hi} में चोट लगाई और उन्हें तुरंत देखभाल चाहिए।",
        "FALL TIME, {gloss} INJURE, IMMEDIATE CARE NEED",
        Intent.EMERGENCY,
    ),
    Template(
        "Examine the patient's {en} carefully for any visible abnormality today.",
        "आज मरीज़ के {hi} की किसी भी असामान्यता के लिए सावधानी से जांच करें।",
        "TODAY {gloss} CAREFUL CHECK, ABNORMAL FIND",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Patient seeks medical advice about the {en} from the family physician today carefully.",
        "मरीज़ आज पारिवारिक चिकित्सक से {hi} के बारे में सावधानी से चिकित्सा सलाह लेते हैं।",
        "TODAY PATIENT, FAMILY DOCTOR {gloss} ADVICE SEEK",
        Intent.DIAGNOSIS,
    ),
]

SYMPTOM_TEMPLATES: list[Template] = [
    Template(
        "Patient is experiencing severe {en} for the past three days now.",
        "मरीज़ को पिछले तीन दिनों से तेज {hi} हो रहा है।",
        "THREE-DAY, {gloss} SEVERE, DOCTOR CONSULT MUST",
        Intent.DIAGNOSIS,
    ),
    Template(
        "How can the patient relieve {en} at home with simple safe remedies?",
        "मरीज़ घर पर सरल और सुरक्षित उपायों से {hi} कैसे कम कर सकते हैं?",
        "{gloss} HOME REMEDY, SIMPLE SAFE, HOW",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Patient complains of persistent {en}, what advice should the doctor give?",
        "मरीज़ लगातार {hi} की शिकायत कर रहे हैं, डॉक्टर को क्या सलाह देनी चाहिए?",
        "{gloss} CONTINUE, DOCTOR ADVICE WHAT",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Sudden {en} appeared after meals, the patient needs urgent diagnosis now.",
        "खाने के बाद अचानक {hi} शुरू हुआ, मरीज़ को अभी तत्काल जांच चाहिए।",
        "FOOD AFTER, {gloss} SUDDEN, URGENT CHECK",
        Intent.DIAGNOSIS,
    ),
]

DISEASE_TEMPLATES: list[Template] = [
    Template(
        "Patient is diagnosed with {en}, what is the recommended treatment plan?",
        "मरीज़ को {hi} का पता चला है, अनुशंसित उपचार योजना क्या है?",
        "{gloss} DIAGNOSE, TREATMENT PLAN WHAT",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Explain to the patient how to manage {en} in their daily life.",
        "मरीज़ को समझाएं कि वे रोज़मर्रा की ज़िंदगी में {hi} कैसे संभालें।",
        "DAILY LIFE, {gloss} MANAGE, EXPLAIN PATIENT",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "What lifestyle changes should be advised for someone living with {en}?",
        "{hi} से पीड़ित व्यक्ति को जीवनशैली में क्या बदलाव की सलाह दें?",
        "{gloss} HAVE, LIFESTYLE CHANGE ADVICE WHAT",
        Intent.PREVENTION,
    ),
    Template(
        "Discuss the long term complications of untreated {en} with the patient.",
        "मरीज़ के साथ बिना इलाज {hi} के दीर्घकालिक खतरों पर चर्चा करें।",
        "{gloss} TREATMENT NOT, LONG-TIME RISK DISCUSS",
        Intent.PREVENTION,
    ),
    Template(
        "How does {en} affect the daily routine of an elderly patient typically?",
        "{hi} एक बुज़ुर्ग मरीज़ की रोज़मर्रा की दिनचर्या को कैसे प्रभावित करता है?",
        "OLD PATIENT, {gloss} DAILY ROUTINE EFFECT HOW",
        Intent.DIAGNOSIS,
    ),
]

MED_TEMPLATES: list[Template] = [
    Template(
        "Doctor prescribed {en} to the patient, how and when should it be taken?",
        "डॉक्टर ने मरीज़ को {hi} दी है, इसे कब और कैसे लेना चाहिए?",
        "{gloss} GIVE, WHEN HOW TAKE",
        Intent.MEDICATION,
    ),
    Template(
        "Inform the patient about possible side effects of taking {en} regularly.",
        "नियमित {hi} लेने के संभावित दुष्प्रभावों के बारे में मरीज़ को बताएं।",
        "{gloss} REGULAR TAKE, SIDE-EFFECT INFORM",
        Intent.MEDICATION,
    ),
    Template(
        "Patient missed a dose of {en} this morning, what should they do?",
        "मरीज़ आज सुबह {hi} की एक खुराक लेना भूल गए, अब क्या करें?",
        "MORNING, {gloss} DOSE FORGET, NOW WHAT",
        Intent.MEDICATION,
    ),
    Template(
        "Pharmacist explains the correct dosage and storage of {en} carefully.",
        "फार्मासिस्ट {hi} की सही खुराक और भंडारण के बारे में सावधानी से समझा रहे हैं।",
        "PHARMACY, {gloss} DOSE STORAGE EXPLAIN",
        Intent.MEDICATION,
    ),
]

DIAG_TEMPLATES: list[Template] = [
    Template(
        "Patient needs a {en} tomorrow, how should they prepare for it?",
        "कल मरीज़ को {hi} करानी है, इसकी तैयारी कैसे करें?",
        "TOMORROW {gloss} NEED, PREPARE HOW",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Explain to the patient what happens during a {en} procedure step by step.",
        "मरीज़ को समझाएं कि {hi} के दौरान चरण-दर-चरण क्या होता है।",
        "{gloss} DURING, STEP-BY-STEP EXPLAIN PATIENT",
        Intent.DIAGNOSIS,
    ),
    Template(
        "The {en} report came negative, doctor wants to repeat the test next week.",
        "{hi} की रिपोर्ट नेगेटिव आई है, डॉक्टर अगले हफ्ते दोबारा जांच कराना चाहते हैं।",
        "{gloss} REPORT NEGATIVE, NEXT-WEEK AGAIN TEST",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Why is the doctor advising a {en} for this particular patient now?",
        "डॉक्टर इस विशेष मरीज़ को अभी {hi} क्यों कराने की सलाह दे रहे हैं?",
        "DOCTOR {gloss} ADVISE, REASON WHY",
        Intent.DIAGNOSIS,
    ),
]

VACC_TEMPLATES: list[Template] = [
    Template(
        "Schedule the {en} vaccine for the child as per the national vaccination calendar.",
        "बच्चे के लिए राष्ट्रीय टीकाकरण कैलेंडर अनुसार {hi} टीका का समय तय करें।",
        "CHILD, {gloss} VACCINE SCHEDULE, NATIONAL CALENDAR FOLLOW",
        Intent.PREVENTION,
    ),
    Template(
        "Inform the parent about possible mild reactions after the {en} vaccine dose today.",
        "आज {hi} टीके की खुराक के बाद संभावित हल्की प्रतिक्रियाओं के बारे में अभिभावक को बताएं।",
        "TODAY {gloss} VACCINE DOSE, MILD REACTION INFORM PARENT",
        Intent.PREVENTION,
    ),
    Template(
        "Why is the {en} vaccine important for the long term health of every child?",
        "हर बच्चे के दीर्घकालिक स्वास्थ्य के लिए {hi} टीका क्यों ज़रूरी है?",
        "CHILD LONG-TIME HEALTH, {gloss} VACCINE WHY IMPORTANT",
        Intent.PREVENTION,
    ),
]

EMER_TEMPLATES: list[Template] = [
    Template(
        "What immediate first aid steps must be taken when {en} occurs at home?",
        "घर पर {hi} की स्थिति में तुरंत क्या प्राथमिक उपचार कदम उठाने चाहिए?",
        "HOME, {gloss} HAPPEN, FIRST-AID IMMEDIATE STEP",
        Intent.EMERGENCY,
    ),
    Template(
        "How to handle a patient suffering from {en} until ambulance arrives safely?",
        "एम्बुलेंस के सुरक्षित आने तक {hi} से पीड़ित मरीज़ को कैसे संभालें?",
        "AMBULANCE ARRIVE BEFORE, {gloss} PATIENT MANAGE HOW",
        Intent.EMERGENCY,
    ),
    Template(
        "Explain the danger signs of {en} every household helper must recognise.",
        "हर घरेलू सहायक को {hi} के खतरे के संकेत पहचानने आने चाहिए।",
        "{gloss} DANGER SIGN, EVERY HELPER RECOGNISE",
        Intent.EMERGENCY,
    ),
]

MATERNAL_TEMPLATES: list[Template] = [
    Template(
        "Pregnant patient is asking about {en}, what advice should the doctor give?",
        "गर्भवती मरीज़ {hi} के बारे में पूछ रही है, डॉक्टर क्या सलाह दें?",
        "PREGNANT, {gloss} ASK, DOCTOR ADVICE WHAT",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Guide the mother about {en} during the third trimester of her pregnancy.",
        "मां को गर्भावस्था के तीसरे त्रैमासिक के दौरान {hi} के बारे में मार्गदर्शन दें।",
        "THIRD TRIMESTER, {gloss} MOTHER GUIDE",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Why is regular check up for {en} important throughout the pregnancy journey?",
        "गर्भावस्था के दौरान {hi} की नियमित जांच क्यों ज़रूरी है?",
        "PREGNANT TIME, {gloss} REGULAR CHECK WHY IMPORTANT",
        Intent.PREVENTION,
    ),
]

PEDIATRIC_TEMPLATES: list[Template] = [
    Template(
        "Infant patient has {en}, what is the safe pediatric care for them?",
        "शिशु मरीज़ को {hi} है, उनके लिए सुरक्षित बाल देखभाल क्या है?",
        "BABY, {gloss} HAVE, SAFE CARE WHAT",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Parent is concerned about {en} in their toddler, what guidance is appropriate?",
        "अभिभावक अपने नन्हे बच्चे में {hi} को लेकर चिंतित हैं, उचित मार्गदर्शन क्या है?",
        "TODDLER, {gloss} PARENT WORRY, GUIDE APPROPRIATE",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "What pediatric dosage should be given to a five year old having {en}?",
        "{hi} से ग्रसित पांच साल के बच्चे को कितनी बाल खुराक दें?",
        "FIVE YEAR CHILD, {gloss} HAVE, DOSE HOW-MUCH",
        Intent.MEDICATION,
    ),
]

PSYCH_TEMPLATES: list[Template] = [
    Template(
        "Patient is experiencing {en} symptoms, how to provide mental health support?",
        "मरीज़ को {hi} के लक्षण हैं, मानसिक स्वास्थ्य सहायता कैसे दें?",
        "{gloss} SYMPTOM, MENTAL HEALTH SUPPORT HOW",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Counsellor is helping a young patient cope with {en} in daily life.",
        "काउंसलर एक युवा मरीज़ को रोज़मर्रा की ज़िंदगी में {hi} से निपटने में मदद कर रहे हैं।",
        "COUNSELLOR, YOUNG PATIENT {gloss} COPE HELP",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Why should a person with {en} avoid alcohol and irregular sleep cycles?",
        "{hi} से पीड़ित व्यक्ति को शराब और अनियमित नींद से क्यों बचना चाहिए?",
        "{gloss} HAVE, ALCOHOL IRREGULAR-SLEEP AVOID WHY",
        Intent.PREVENTION,
    ),
]

ANES_TEMPLATES: list[Template] = [
    Template(
        "Anesthetist is explaining {en} risks to the patient before surgery starts.",
        "सर्जरी से पहले संज्ञाहरण विशेषज्ञ मरीज़ को {hi} के जोखिम समझा रहे हैं।",
        "SURGERY BEFORE, ANESTHETIST {gloss} RISK EXPLAIN",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Why is fasting required when {en} will be administered to the patient?",
        "मरीज़ को {hi} दी जाएगी तो उपवास क्यों ज़रूरी है?",
        "{gloss} GIVE TIME, FAST WHY NEED",
        Intent.MEDICATION,
    ),
]

PUBHEALTH_TEMPLATES: list[Template] = [
    Template(
        "Community awareness program is teaching {en} importance to local rural residents.",
        "सामुदायिक जागरूकता कार्यक्रम स्थानीय ग्रामीण निवासियों को {hi} का महत्व सिखा रहा है।",
        "VILLAGE, COMMUNITY PROGRAM {gloss} IMPORTANT TEACH",
        Intent.PREVENTION,
    ),
    Template(
        "How does proper {en} reduce common infectious disease spread in the community?",
        "उचित {hi} समुदाय में आम संक्रामक बीमारियों का प्रसार कैसे कम करता है?",
        "COMMUNITY, {gloss} GOOD, INFECT DISEASE SPREAD REDUCE",
        Intent.PREVENTION,
    ),
    Template(
        "What public health steps prevent {en} outbreaks in densely populated city slums?",
        "घनी आबादी वाले शहरी झुग्गियों में {hi} के प्रकोप को कौन से कदम रोकते हैं?",
        "CITY SLUM, {gloss} OUTBREAK PREVENT STEP WHAT",
        Intent.PREVENTION,
    ),
]

HOSPITAL_TEMPLATES: list[Template] = [
    Template(
        "Patient is asking about the {en} process during their hospital admission today.",
        "मरीज़ आज अस्पताल में भर्ती के दौरान {hi} प्रक्रिया के बारे में पूछ रहे हैं।",
        "TODAY HOSPITAL ADMIT, {gloss} PROCESS ASK",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Receptionist is explaining the {en} requirement to a visiting elderly attendant.",
        "रिसेप्शनिस्ट एक बुज़ुर्ग तीमारदार को {hi} की ज़रूरत समझा रहे हैं।",
        "RECEPTION, OLD ATTENDER {gloss} NEED EXPLAIN",
        Intent.TREATMENT_ADVICE,
    ),
]

PHARMACY_META_TEMPLATES: list[Template] = [
    Template(
        "Pharmacist explains the importance of {en} on every medical prescription label carefully.",
        "फार्मासिस्ट हर चिकित्सा पर्ची लेबल पर {hi} के महत्व की सावधानी से व्याख्या करते हैं।",
        "PHARMACY EXPLAIN, MEDICAL LABEL {gloss} IMPORTANT CAREFUL",
        Intent.MEDICATION,
    ),
    Template(
        "Why does the doctor record {en} so carefully on every patient's prescription form daily?",
        "डॉक्टर हर मरीज़ की पर्ची फॉर्म पर {hi} इतनी सावधानी से रोज़ क्यों दर्ज करते हैं?",
        "DAILY DOCTOR PATIENT FORM, {gloss} RECORD CAREFUL WHY",
        Intent.MEDICATION,
    ),
    Template(
        "Patient asks the pharmacist about {en} before starting the prescribed medicine course today.",
        "मरीज़ आज दवा का कोर्स शुरू करने से पहले फार्मासिस्ट से {hi} के बारे में पूछते हैं।",
        "TODAY MEDICINE COURSE BEFORE, PATIENT PHARMACY {gloss} ASK",
        Intent.MEDICATION,
    ),
]


DEVICE_TEMPLATES: list[Template] = [
    Template(
        "Hospital training program covers the importance of {en} for all medical staff today carefully.",
        "अस्पताल का प्रशिक्षण कार्यक्रम आज सभी चिकित्सा कर्मचारियों के लिए {hi} के महत्व को सावधानी से कवर करता है।",
        "TODAY HOSPITAL TRAIN, ALL STAFF {gloss} IMPORTANT COVER",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Doctor explains the role of {en} in modern healthcare delivery to the new patient today.",
        "डॉक्टर आज नए मरीज़ को आधुनिक स्वास्थ्य सेवा में {hi} की भूमिका समझाते हैं।",
        "TODAY DOCTOR NEW PATIENT, MODERN HEALTHCARE {gloss} ROLE EXPLAIN",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Why is {en} considered essential in the daily workflow of every health worker?",
        "हर स्वास्थ्य कार्यकर्ता के दैनिक कार्य में {hi} को क्यों आवश्यक माना जाता है?",
        "HEALTH-WORKER DAILY WORK, {gloss} ESSENTIAL WHY",
        Intent.TREATMENT_ADVICE,
    ),
]


DENTAL_TEMPLATES: list[Template] = [
    Template(
        "Patient has {en} and is asking for treatment options at the dental clinic.",
        "मरीज़ को {hi} है और वे डेंटल क्लिनिक में उपचार विकल्प पूछ रहे हैं।",
        "DENTAL CLINIC, {gloss} HAVE, TREATMENT OPTION ASK",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "Explain proper oral hygiene to prevent {en} from worsening over time.",
        "{hi} को बिगड़ने से रोकने के लिए उचित मौखिक स्वच्छता समझाएं।",
        "{gloss} WORSE PREVENT, MOUTH CLEAN EXPLAIN",
        Intent.PREVENTION,
    ),
]


def _templates_for(category: Category) -> list[Template]:
    if category in BODY_PART_CATS: return BODY_PART_TEMPLATES
    if category in SYMPTOM_CATS: return SYMPTOM_TEMPLATES
    if category in DISEASE_CATS: return DISEASE_TEMPLATES
    if category in MED_CATS: return MED_TEMPLATES
    if category in DIAG_CATS: return DIAG_TEMPLATES
    if category in VACC_CATS: return VACC_TEMPLATES
    if category in EMER_CATS: return EMER_TEMPLATES
    if category in MATERNAL_CATS: return MATERNAL_TEMPLATES
    if category in PEDIATRIC_CATS: return PEDIATRIC_TEMPLATES
    if category in PSYCH_CATS: return PSYCH_TEMPLATES
    if category in ANES_CATS: return ANES_TEMPLATES
    if category in PUBHEALTH_CATS: return PUBHEALTH_TEMPLATES
    if category in HOSPITAL_CATS: return HOSPITAL_TEMPLATES
    if category in DENTAL_CATS: return DENTAL_TEMPLATES
    return DISEASE_TEMPLATES  # safe fallback


# --- Patient-voice templates (first-person, real consultation feel) ----
NATURAL_BODY_PART: list[Template] = [
    Template(
        "Doctor said I have lot of pain in my {en}. What should I do at home?",
        "डॉक्टर ने कहा मुझे {hi} में बहुत दर्द है। मुझे घर पर क्या करना चाहिए?",
        "DOCTOR TELL, ME {gloss} PAIN MUCH, HOME WHAT-DO?",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "I hurt my {en} yesterday after a fall. Should I be worried about it now?",
        "कल गिरने के बाद मुझे {hi} में चोट लगी। क्या मुझे चिंता करनी चाहिए?",
        "YESTERDAY FALL ME, {gloss} INJURE, ME WORRY NEED?",
        Intent.EMERGENCY,
    ),
]

NATURAL_SYMPTOM: list[Template] = [
    Template(
        "I have been having severe {en} for the last three days. Is this serious for me?",
        "मुझे पिछले तीन दिनों से तेज {hi} हो रहा है। क्या यह गंभीर है?",
        "THREE-DAY ME {gloss} HAVE, SERIOUS QUESTION?",
        Intent.DIAGNOSIS,
    ),
    Template(
        "Whenever I eat oily food my {en} starts. What can I do at home for relief?",
        "जब भी मैं तेल वाला खाना खाता हूं, मुझे {hi} होने लगता है। घर पर क्या करूं?",
        "OIL-FOOD EAT TIME, ME {gloss} START, HOME WHAT-DO?",
        Intent.TREATMENT_ADVICE,
    ),
]

NATURAL_DISEASE: list[Template] = [
    Template(
        "Doctor told me I have {en}. What should I do to manage it in daily life?",
        "डॉक्टर ने मुझे बताया कि मुझे {hi} है। रोज़ाना ज़िंदगी में मैं इसे कैसे संभालूं?",
        "DOCTOR TELL ME, {gloss} HAVE, DAILY MANAGE HOW?",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "My father has been suffering from {en} for many years. How can I take care of him?",
        "मेरे पिता को कई सालों से {hi} है। मैं उनकी देखभाल कैसे करूं?",
        "MY FATHER, MANY-YEAR {gloss} HAVE, ME CARE HOW?",
        Intent.TREATMENT_ADVICE,
    ),
]

NATURAL_MED: list[Template] = [
    Template(
        "I forgot to take my {en} dose this morning. What should I do now please?",
        "मैं आज सुबह अपनी {hi} की खुराक लेना भूल गया। मुझे अब क्या करना चाहिए?",
        "TODAY MORNING ME {gloss} DOSE FORGET, NOW WHAT-DO?",
        Intent.MEDICATION,
    ),
    Template(
        "Pharmacist gave me {en} for my problem today. Is it safe to take with food?",
        "फार्मासिस्ट ने आज मुझे मेरी समस्या के लिए {hi} दी। क्या इसे खाने के साथ लेना सुरक्षित है?",
        "TODAY PHARMACY ME {gloss} GIVE, FOOD WITH SAFE?",
        Intent.MEDICATION,
    ),
]

NATURAL_DIAG: list[Template] = [
    Template(
        "Doctor advised me to do a {en} this week. How should I prepare for it properly?",
        "डॉक्टर ने मुझे इस हफ्ते {hi} कराने को कहा। मैं इसकी ठीक से तैयारी कैसे करूं?",
        "THIS-WEEK DOCTOR ME {gloss} ADVISE, PREPARE HOW?",
        Intent.DIAGNOSIS,
    ),
    Template(
        "My {en} report came today and I am nervous. What should I expect from it?",
        "आज मेरी {hi} की रिपोर्ट आई और मैं घबराया हूं। मुझे क्या उम्मीद रखनी चाहिए?",
        "TODAY MY {gloss} REPORT ARRIVE, ME WORRY, EXPECT WHAT?",
        Intent.DIAGNOSIS,
    ),
]

NATURAL_VACC: list[Template] = [
    Template(
        "My child is six months old now. When should I get the {en} vaccine for him?",
        "मेरा बच्चा अब छह महीने का है। मुझे उसे {hi} टीका कब लगवाना चाहिए?",
        "MY CHILD SIX-MONTH, ME {gloss} VACCINE WHEN DO?",
        Intent.PREVENTION,
    ),
    Template(
        "After the {en} vaccine dose my baby had mild fever last night. Is this normal?",
        "{hi} टीके की खुराक के बाद कल रात मेरे बच्चे को हल्का बुखार था। क्या यह सामान्य है?",
        "{gloss} VACCINE DOSE AFTER, MY BABY MILD FEVER, NORMAL?",
        Intent.PREVENTION,
    ),
]

NATURAL_EMER: list[Template] = [
    Template(
        "What should I do first if my friend suddenly has {en} right in front of me?",
        "अगर मेरे दोस्त को अचानक {hi} हो जाए तो मुझे पहले क्या करना चाहिए?",
        "MY FRIEND SUDDEN {gloss} HAPPEN, FIRST WHAT-DO?",
        Intent.EMERGENCY,
    ),
    Template(
        "My elderly neighbour just collapsed with {en}. How can I help him until help arrives?",
        "मेरे बुज़ुर्ग पड़ोसी अभी {hi} से गिर गए। मदद आने तक मैं उनकी कैसे मदद करूं?",
        "MY OLD NEIGHBOUR {gloss} FALL, HELP ARRIVE BEFORE, HOW HELP?",
        Intent.EMERGENCY,
    ),
]

NATURAL_MATERNAL: list[Template] = [
    Template(
        "I am six months pregnant and my doctor mentioned {en}. What does this mean for me?",
        "मैं छह महीने की गर्भवती हूं, और डॉक्टर ने {hi} बताया। मेरे लिए इसका क्या मतलब है?",
        "ME PREGNANT SIX-MONTH, DOCTOR {gloss} TELL, MEANING WHAT?",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "My wife is in her third trimester now. Should we worry about {en} at this stage?",
        "मेरी पत्नी अब तीसरे त्रैमासिक में हैं। क्या हमें इस समय {hi} की चिंता करनी चाहिए?",
        "MY WIFE THIRD-TRIMESTER, NOW {gloss} WORRY NEED?",
        Intent.PREVENTION,
    ),
]

NATURAL_PEDIATRIC: list[Template] = [
    Template(
        "My toddler has {en} since this morning. Can I treat this safely at home today?",
        "मेरे नन्हे बच्चे को आज सुबह से {hi} है। क्या मैं घर पर सुरक्षित इलाज कर सकता हूं?",
        "MY TODDLER MORNING-FROM {gloss} HAVE, HOME SAFE TREAT?",
        Intent.TREATMENT_ADVICE,
    ),
    Template(
        "My five year old shows symptoms of {en}. Should I take him to a doctor today?",
        "मेरे पांच साल के बच्चे में {hi} के लक्षण हैं। क्या मुझे आज डॉक्टर के पास ले जाना चाहिए?",
        "MY FIVE-YEAR CHILD {gloss} SYMPTOM, TODAY DOCTOR TAKE NEED?",
        Intent.DIAGNOSIS,
    ),
]

NATURAL_PSYCH: list[Template] = [
    Template(
        "I have been feeling {en} for many weeks now. Should I see a counsellor about it?",
        "मुझे कई हफ्तों से {hi} महसूस हो रहा है। क्या मुझे काउंसलर से मिलना चाहिए?",
        "MANY-WEEK ME {gloss} FEEL, COUNSELLOR MEET NEED?",
        Intent.TREATMENT_ADVICE,
    ),
]

NATURAL_ANES: list[Template] = [
    Template(
        "My surgery is tomorrow morning and they will give me {en}. Should I be worried about that?",
        "कल सुबह मेरी सर्जरी है और मुझे {hi} दी जाएगी। क्या मुझे चिंता करनी चाहिए?",
        "TOMORROW MORNING SURGERY, ME {gloss} GIVE, WORRY NEED?",
        Intent.TREATMENT_ADVICE,
    ),
]

NATURAL_PUBHEALTH: list[Template] = [
    Template(
        "Our village school is teaching about {en}. Why is this important for our community everyone?",
        "हमारे गांव का स्कूल {hi} के बारे में सिखा रहा है। यह हमारे समुदाय के लिए क्यों ज़रूरी है?",
        "VILLAGE SCHOOL {gloss} TEACH, COMMUNITY WHY IMPORTANT?",
        Intent.PREVENTION,
    ),
]

NATURAL_HOSPITAL: list[Template] = [
    Template(
        "I came to the hospital today and they asked about {en}. What does this involve for me?",
        "मैं आज अस्पताल आया और उन्होंने {hi} के बारे में पूछा। मेरे लिए इसमें क्या शामिल है?",
        "TODAY HOSPITAL ARRIVE, {gloss} ASK, ME INVOLVE WHAT?",
        Intent.TREATMENT_ADVICE,
    ),
]

NATURAL_DENTAL: list[Template] = [
    Template(
        "I have had {en} for two weeks now. Will the dentist need to extract a tooth?",
        "मुझे दो हफ्ते से {hi} है। क्या डेंटिस्ट को दांत निकालना पड़ेगा?",
        "TWO-WEEK ME {gloss} HAVE, DENTIST TOOTH EXTRACT NEED?",
        Intent.TREATMENT_ADVICE,
    ),
]


def _natural_for(category: Category) -> list[Template]:
    if category in BODY_PART_CATS: return NATURAL_BODY_PART
    if category in SYMPTOM_CATS: return NATURAL_SYMPTOM
    if category in DISEASE_CATS: return NATURAL_DISEASE
    if category in MED_CATS: return NATURAL_MED
    if category in DIAG_CATS: return NATURAL_DIAG
    if category in VACC_CATS: return NATURAL_VACC
    if category in EMER_CATS: return NATURAL_EMER
    if category in MATERNAL_CATS: return NATURAL_MATERNAL
    if category in PEDIATRIC_CATS: return NATURAL_PEDIATRIC
    if category in PSYCH_CATS: return NATURAL_PSYCH
    if category in ANES_CATS: return NATURAL_ANES
    if category in PUBHEALTH_CATS: return NATURAL_PUBHEALTH
    if category in HOSPITAL_CATS: return NATURAL_HOSPITAL
    if category in DENTAL_CATS: return NATURAL_DENTAL
    return NATURAL_DISEASE


# --- urgency / difficulty rules -----------------------------------------
HIGH_URGENCY = {Category.FIRST_AID, Category.CARDIOLOGY, Category.ANESTHESIOLOGY,
                Category.NEUROLOGY, Category.ONCOLOGY}
LOW_URGENCY = {Category.PUBLIC_HEALTH, Category.HOSPITAL, Category.DENTISTRY,
               Category.ANATOMY, Category.VACCINATION}

HARD_CATS = {Category.ONCOLOGY, Category.NEUROLOGY, Category.CARDIOLOGY,
             Category.ANESTHESIOLOGY, Category.NEPHROLOGY}
EASY_CATS = {Category.PUBLIC_HEALTH, Category.HOSPITAL, Category.HOSPITAL,
             Category.SYMPTOMS}


def _urgency(cat: Category) -> Urgency:
    if cat in HIGH_URGENCY: return Urgency.HIGH
    if cat in LOW_URGENCY: return Urgency.LOW
    return Urgency.MEDIUM


def _difficulty(cat: Category, term_word_count: int) -> Difficulty:
    if cat in HARD_CATS or term_word_count >= 3: return Difficulty.HARD
    if cat in EASY_CATS and term_word_count == 1: return Difficulty.EASY
    return Difficulty.MEDIUM


# --- term-level intent override (for contextual rows that already exist) -
def _intent_for_existing(cat: Category) -> Intent:
    if cat in EMER_CATS: return Intent.EMERGENCY
    if cat in MED_CATS: return Intent.MEDICATION
    if cat in DIAG_CATS: return Intent.DIAGNOSIS
    if cat in VACC_CATS or cat in PUBHEALTH_CATS: return Intent.PREVENTION
    if cat in SYMPTOM_CATS or cat in BODY_PART_CATS: return Intent.DIAGNOSIS
    return Intent.TREATMENT_ADVICE


def _stable_pick(text: str, n: int) -> int:
    """Deterministic template selection so re-runs are reproducible."""
    h = hashlib.md5(text.encode("utf-8")).digest()
    return h[0] % n


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "sample"


def _gloss_token(en: str) -> str:
    """Convert an English term into a single gloss-friendly token (no spaces)."""
    return re.sub(r"[^A-Z0-9+]", "", en.upper().replace(" ", "+").replace("'", ""))


_GLOSS_PAD_POOL = ["DOCTOR", "ADVICE", "CAREFUL", "PATIENT", "HOSPITAL", "TODAY",
                   "MUST", "NEED", "PLEASE", "INFORM", "EXPLAIN", "FOLLOW"]


def _split_tokens(g: str) -> list[str]:
    return [t for t in re.split(r"[,\.\?\!\s]+", g) if t]


def _enforce_word_range(text_en: str) -> str:
    words = text_en.split()
    if len(words) > 20:
        text_en = " ".join(words[:20])
        if not text_en.endswith((".", "?", "!")):
            text_en += "."
    return text_en


def _enforce_gloss_range(gloss: str) -> str:
    tokens = _split_tokens(gloss)
    if len(tokens) > 12:
        end_punct = gloss[-1] if gloss[-1:] in ".?!" else ""
        return " ".join(tokens[:12]) + end_punct
    if len(tokens) < 5:
        end_punct = gloss[-1] if gloss[-1:] in ".?!" else ""
        existing = set(tokens)
        pool = [p for p in _GLOSS_PAD_POOL if p not in existing]
        need = 5 - len(tokens)
        core = gloss.rstrip(",.?! ")
        return core + " " + " ".join(pool[:need]) + end_punct
    return gloss


# --- Wrapping short hand-curated contextuals into instruction form ------
_PRONOUN_STARTERS = {
    "you", "your", "we", "they", "i", "this", "that", "the",
    "a", "an", "he", "she", "it",
}
_TIME_CLAUSE_STARTERS = {"after", "before", "since", "if", "when", "while", "until"}

_CATEGORY_WRAPPERS: dict[Category, tuple[str, str, str]] = {
    # (declarative_wrap, imperative_wrap, question_wrap)  — each contains {body}
    Category.FIRST_AID: (
        "In a medical emergency the rule is that {body} without any delay.",
        "In an emergency situation you must {body} to save the life.",
        "During an emergency the responder asks: {body} immediately on arrival.",
    ),
    Category.PHARMACY: (
        "The doctor informs the patient that {body} as part of the prescription.",
        "Instruct the patient at the pharmacy to {body} for full medical recovery.",
        "Pharmacist asks the patient: {body} during the medicine counselling session.",
    ),
    Category.DIAGNOSTICS: (
        "Doctor tells the patient that {body} based on the latest investigation report.",
        "Before the diagnostic test starts the patient is told to {body} carefully.",
        "Technician asks the patient: {body} before starting the diagnostic procedure today.",
    ),
    Category.MATERNAL: (
        "Doctor advises the pregnant patient that {body} during routine antenatal care.",
        "During antenatal counselling the pregnant patient is told to {body} every day.",
        "Obstetrician asks the pregnant patient: {body} at the prenatal appointment.",
    ),
    Category.CARDIOLOGY: (
        "Cardiologist informs the patient that {body} after the cardiac evaluation today.",
        "To control heart problems the patient is told to {body} every single day.",
        "Cardiologist asks the patient: {body} during the routine heart check up.",
    ),
    Category.ENDOCRINOLOGY: (
        "Endocrinologist informs the patient that {body} for blood sugar level control.",
        "To manage diabetes properly the patient is told to {body} every single day.",
        "Diabetologist asks the patient: {body} during the routine sugar review visit.",
    ),
    Category.PULMONOLOGY: (
        "Pulmonologist informs the patient that {body} based on the chest examination.",
        "For better breathing the patient is told to {body} every single day strictly.",
        "Pulmonologist asks the patient: {body} during the routine respiratory check up.",
    ),
    Category.NEUROLOGY: (
        "Neurologist informs the patient that {body} after the neurological examination today.",
        "For nerve health the patient is told to {body} every day without skipping.",
        "Neurologist asks the patient: {body} during the routine neurology follow up.",
    ),
    Category.PEDIATRICS: (
        "Pediatrician tells the parent that {body} as part of routine child care.",
        "For the baby's safety the parent is instructed to {body} every single day.",
        "Pediatrician asks the parent: {body} during the routine baby check up.",
    ),
    Category.PSYCHIATRY: (
        "Counsellor reassures the patient that {body} during the mental health support session.",
        "For better mental wellbeing the patient is encouraged to {body} every day.",
        "Counsellor asks the patient: {body} during the regular mental health consultation.",
    ),
    Category.ANESTHESIOLOGY: (
        "Anesthetist informs the patient that {body} before the scheduled surgical procedure today.",
        "Before surgery starts the patient is strictly told to {body} without exception.",
        "Anesthetist asks the patient: {body} during the pre operative assessment visit.",
    ),
    Category.ORTHOPEDICS: (
        "Orthopedic surgeon tells the patient that {body} after the bone examination today.",
        "For bone healing the patient is instructed to {body} every single day strictly.",
        "Orthopedic surgeon asks the patient: {body} during the fracture review consultation.",
    ),
    Category.DERMATOLOGY: (
        "Dermatologist informs the patient that {body} after the skin examination today carefully.",
        "For skin care the patient is instructed to {body} every single day strictly.",
        "Dermatologist asks the patient: {body} during the routine skin review consultation.",
    ),
    Category.OPHTHALMOLOGY: (
        "Eye doctor informs the patient that {body} after the eye examination today carefully.",
        "For eye care the patient is instructed to {body} every single day strictly.",
        "Eye doctor asks the patient: {body} during the routine eye review consultation.",
    ),
    Category.ENT: (
        "ENT specialist informs the patient that {body} after the examination today carefully.",
        "For ear care the patient is instructed to {body} every single day strictly.",
        "ENT specialist asks the patient: {body} during the routine ENT review.",
    ),
    Category.VACCINATION: (
        "Health worker informs the parent that {body} as part of routine immunization.",
        "For child protection the parent is told to {body} on the scheduled date.",
        "Health worker asks the parent: {body} during the immunization clinic visit today.",
    ),
    Category.PUBLIC_HEALTH: (
        "Health worker explains to the community that {body} for better public health.",
        "For preventing disease the resident is told to {body} every single day strictly.",
        "Public health worker asks the resident: {body} during the awareness program today.",
    ),
    Category.HOSPITAL: (
        "Hospital staff informs the patient that {body} during the admission process today.",
        "At the hospital reception the patient is told to {body} for smooth admission.",
        "Hospital receptionist asks the patient: {body} during the admission counter visit.",
    ),
    Category.DENTISTRY: (
        "Dentist informs the patient that {body} after the dental examination today carefully.",
        "For dental health the patient is instructed to {body} every single day strictly.",
        "Dentist asks the patient: {body} during the routine oral health consultation.",
    ),
    Category.SYMPTOMS: (
        "Doctor records that the patient reports {body} during this consultation visit.",
        "Doctor tells the patient: {body} as part of the treatment advice today.",
        "Doctor asks the patient: {body} during the symptom assessment consultation today.",
    ),
    Category.ANATOMY: (
        "Doctor explains to the patient that {body} as a part of basic anatomy.",
        "For body awareness the patient is told to understand that {body} works carefully.",
        "Doctor asks the patient: {body} during the anatomy education session today.",
    ),
}

_DEFAULT_WRAP = (
    "Doctor informs the patient that {body} during today's consultation visit.",
    "The doctor advises the patient to {body} during today's consultation visit.",
    "Doctor asks the patient: {body} during today's consultation visit.",
)


def _wrap_short_contextual(orig: str, category: Category) -> str:
    """Wrap a short imperative/declarative/question into 8-20 words."""
    s = orig.strip()
    is_question = s.endswith("?")
    body = s.rstrip(".?! ").strip()
    body_lower = body[0].lower() + body[1:] if body else body

    # Negative imperatives ("Do not X" / "Don't X" / "Avoid X-ing") need a
    # different scaffold so we don't end up with "you must do not X".
    is_negative = body_lower.startswith(("do not ", "don't ", "avoid "))
    if is_negative:
        wrapped = f"It is important that you remember: {body_lower} when caring for the patient."
        return _enforce_word_range(wrapped)

    decl, imp, q = _CATEGORY_WRAPPERS.get(category, _DEFAULT_WRAP)
    first = (body.split()[0] if body else "").lower().rstrip(",.")
    is_time_clause = first in _TIME_CLAUSE_STARTERS
    is_declarative = first in _PRONOUN_STARTERS

    if is_question:
        wrapped = q.format(body=body_lower)
    elif is_time_clause:
        # Subordinate-clause-led sentences ("After surgery, rest for two weeks.")
        # don't fit declarative or imperative wraps — quote them verbatim.
        wrapped = f"The doctor's instruction to the patient is: {body_lower} as part of treatment."
    elif is_declarative:
        wrapped = decl.format(body=body_lower)
    else:
        wrapped = imp.format(body=body_lower)
    return _enforce_word_range(wrapped)


_DEVICE_TERMS = {
    "Otoscope", "Endoscope", "Audiometry", "Cerumen Removal", "Spirometer",
    "Pulse Oximeter", "Glucometer", "Defibrillator", "Pacemaker", "Stent",
    "Holter Monitor", "Holter", "Tonometry", "Slit Lamp", "Eye Patch",
    "Hearing Aid", "Cochlear Implant", "Inhaler", "Nebulizer",
    "Oxygen Mask", "Ventilator", "Catheter", "Stretcher", "Wheelchair",
    "Walker", "Crutch", "Sling", "Splint", "Cast", "Plaster",
    "Tourniquet", "EpiPen", "AED", "First Aid Kit", "Bandage", "Gauze",
    "Cotton", "Antiseptic", "Oxygen Cylinder", "Cervical Collar",
    "Plate and Screw", "Bone Graft", "Eye Drops", "Spectacles",
    "Contact Lens", "IV Line", "Saline", "Syringe", "Vial",
    "Pill Box", "Glucometer", "Snellen Chart", "Pulse Oximeter",
    "Echocardiogram", "Doppler", "Stress Test", "Lumbar Puncture",
    "Bone Marrow", "FDG PET", "Stress Echo",
}


_PHARMACY_META_TERMS = {
    "Tablet", "Capsule", "Syrup", "Injection", "Drops", "Ointment", "Cream",
    "Lotion", "Spray", "Inhaler", "Suppository", "Powder", "Sachet", "Lozenge",
    "Patch", "Pill Box", "Prescription", "Generic", "Brand Name", "Dose",
    "Dosage", "Side Effect", "Allergy", "Interaction", "Expiry Date",
    "Manufacturing Date", "Storage", "Refrigerate", "Generic Drug", "OTC",
    "Multivitamin",
}

_DENTAL_NON_CONDITION_TERMS = {
    "Dentist", "Dental Clinic", "Toothbrush", "Toothpaste", "Floss", "Mouthwash",
    "Filling", "Crown", "Bridge", "Implant", "Root Canal", "Extraction",
    "Wisdom Tooth", "Braces", "Aligner", "Denture",
}

_VACCINE_META_TERMS = {
    "Booster", "Cold Chain", "Herd Immunity", "Mission Indradhanush",
    "Vaccine Schedule", "Inactivated Vaccine", "Live Vaccine",
    "Adverse Event Following Immunization", "AEFI", "mRNA Vaccine",
    "Immunization", "Vaccination",
}


_NATURAL_DENY_CATEGORIES = {Category.ANESTHESIOLOGY, Category.HOSPITAL,
                            Category.PUBLIC_HEALTH}
_NATURAL_DENY_TERMS = {
    # devices / places / abbreviations that don't fit "feeling X" / "given X" patterns
    "AED", "EpiPen", "Tourniquet", "First Aid Kit", "Stretcher", "Bandage",
    "Gauze", "Cotton", "Oxygen Cylinder", "Triage", "Resuscitation",
    "Ventilator", "Catheter", "IV Line", "Saline", "Cross Match",
    "Recovery Room", "Operating Room", "ICU", "HDU", "Ward", "Bed",
    "Theatre Sister", "Scrub", "Sterilization", "Asepsis", "Suture",
    "Stitch", "Dressing", "Drain", "Incision", "Surgical Site",
    "Consent Form", "NPO", "Surgeon", "Anesthetist", "Nurse",
    "Pulse Oximeter", "Glucometer", "Otoscope", "Endoscope",
    "Reception", "Counter", "Bill", "Receipt", "Estimate",
    "Visitor Pass", "Aadhaar Card", "Health Card", "Insurance",
    "Cashless", "Reimbursement", "Medical Record", "Prescription Pad",
}


def _is_natural_eligible(en: str, category: Category) -> bool:
    if category in _NATURAL_DENY_CATEGORIES:
        return False
    if en in _NATURAL_DENY_TERMS:
        return False
    # short all-caps acronyms (OCD, ADHD, BPH, MRI, ECG…) don't fit patient voice
    if en.isupper() and len(en) <= 6:
        return False
    return True


_VACC_NAME_RE = re.compile(r"\s*\b(vaccine|vaccination|shot|jab|immunization|immunisation)\s*$", re.I)
_VACC_HI_RE = re.compile(r"\s*(टीका|टीकाकरण|शॉट)\s*$")


def _strip_vaccine_suffix(s: str) -> str:
    return _VACC_NAME_RE.sub("", s).strip()


def _strip_vaccine_suffix_hi(s: str) -> str:
    return _VACC_HI_RE.sub("", s).strip()


def _dedup_repeated_word(text: str, words: list[str]) -> str:
    """Collapse 'vaccine vaccine' / 'टीका टीका' that emerge after substitution."""
    for w in words:
        text = re.sub(rf"\b({re.escape(w)})\s+\1\b", r"\1", text, flags=re.I)
    return text


def transform_lexical(en: str, hi: str, category: Category) -> dict | None:
    """Return one Sample-shaped dict (un-validated) from a lexical term.

    Routing priority:
        1. Devices / equipment / non-condition dental items / vaccine-meta concepts
           -> DEVICE_TEMPLATES (avoids "diagnosed with endoscope" / "prevent dentist")
        2. Pharmacy meta-terms (Tablet, Dose, Side Effect, …) -> PHARMACY_META_TEMPLATES
        3. Eligible terms with 25% chance -> patient-voice NATURAL_* pool
        4. Default -> standard category pool
    Vaccination substitutions use vaccine-aware stripping + dedup.
    """
    is_device = (
        en in _DEVICE_TERMS
        or (category == Category.DENTISTRY and en in _DENTAL_NON_CONDITION_TERMS)
        or (category == Category.VACCINATION and en in _VACCINE_META_TERMS)
    )
    is_pharma_meta = category == Category.PHARMACY and en in _PHARMACY_META_TERMS

    eligible = False
    use_natural = False
    if is_device:
        pool = DEVICE_TEMPLATES
        suffix = "dev"
    elif is_pharma_meta:
        pool = PHARMACY_META_TEMPLATES
        suffix = "meta"
    else:
        eligible = _is_natural_eligible(en, category)
        use_natural = eligible and (_stable_pick(en + "-natural", 4) == 0)
        pool = _natural_for(category) if use_natural else _templates_for(category)
        suffix = "nat" if use_natural else "tpl"
    template = pool[_stable_pick(en, len(pool))]

    # vaccine-aware substitution: strip any pre-existing "vaccine/शॉट/टीका"
    # suffix so "{en} vaccine" → "Polio vaccine" not "Polio Vaccine vaccine"
    en_sub = en.lower()
    hi_sub = hi
    if category == Category.VACCINATION and not is_device:
        en_sub = _strip_vaccine_suffix(en).lower()
        hi_sub = _strip_vaccine_suffix_hi(hi)

    text_en = template.en.format(en=en_sub)
    text_hi = template.hi.format(hi=hi_sub)
    gloss = template.gloss.format(gloss=_gloss_token(en))

    text_en = _dedup_repeated_word(text_en, ["vaccine", "shot", "vaccination"])
    text_hi = _dedup_repeated_word(text_hi, ["टीका", "टीकाकरण"])

    text_en = _enforce_word_range(text_en)
    gloss = _enforce_gloss_range(gloss)

    return {
        "id": f"isl-med-lex2ctx-{suffix}-{_slug(en)}",
        "text_en": text_en,
        "text_hi": text_hi,
        "gloss_sequence": gloss,
        "category": category.value,
        "intent": template.intent.value,
        "urgency": _urgency(category).value,
        "difficulty": _difficulty(category, len(en.split())).value,
        "source": "synthetic_curated",
    }


def enrich_existing_contextual(en: str, hi: str, gloss: str, category: Category) -> dict | None:
    """Wrap short rows into instruction form; attach intent/urgency/difficulty."""
    if len(en.split()) < 8:
        text_en = _wrap_short_contextual(en, category)
    else:
        text_en = _enforce_word_range(en)
    gloss_seq = _enforce_gloss_range(gloss)
    return {
        "id": f"isl-med-ctx-{_slug(en)}",
        "text_en": text_en,
        "text_hi": hi,
        "gloss_sequence": gloss_seq,
        "category": category.value,
        "intent": _intent_for_existing(category).value,
        "urgency": _urgency(category).value,
        "difficulty": _difficulty(category, len(en.split()) // 4 + 1).value,
        "source": "synthetic_curated",
    }


def build_records() -> list[dict]:
    rows: list[dict] = []
    seen_text_en: set[str] = set()
    seen_ids: set[str] = set()

    # 1. enrich the 100 existing contextual rows
    for en, gloss, hi, cat_v01 in all_contextual():
        cat = Category(cat_v01.value)
        rec = enrich_existing_contextual(en, hi, gloss, cat)
        if not rec or rec["text_en"] in seen_text_en or rec["id"] in seen_ids:
            continue
        seen_text_en.add(rec["text_en"])
        seen_ids.add(rec["id"])
        rows.append(rec)

    # 2. convert lexical terms into contextual instructions
    for en, _gloss, hi, cat_v01 in all_lexical():
        cat = Category(cat_v01.value)
        rec = transform_lexical(en, hi, cat)
        if not rec or rec["text_en"] in seen_text_en or rec["id"] in seen_ids:
            continue
        seen_text_en.add(rec["text_en"])
        seen_ids.add(rec["id"])
        rows.append(rec)

    return rows


def sample_balanced(rows: list[dict], per_category: int = 30, seed: int = 42) -> list[dict]:
    """Take up to `per_category` rows from each category with stable shuffling.

    Within each category we deterministically interleave so patient-voice and
    template-voice rows both end up in the final set.
    """
    import random
    from collections import defaultdict

    rng = random.Random(seed)
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r)

    out: list[dict] = []
    for cat in sorted(by_cat.keys()):
        items = list(by_cat[cat])
        # interleave nat/tpl ids before shuffling so each category mixes both styles
        nat = [r for r in items if "-nat-" in r["id"]]
        tpl = [r for r in items if "-nat-" not in r["id"]]
        rng.shuffle(nat)
        rng.shuffle(tpl)
        # keep ~30% natural per category if available
        n_nat_target = max(1, per_category // 3) if nat else 0
        n_nat_take = min(n_nat_target, len(nat))
        chosen = nat[:n_nat_take] + tpl[: per_category - n_nat_take]
        # fall back to filling from whichever has more if needed
        if len(chosen) < per_category:
            extras = [r for r in items if r not in chosen]
            chosen.extend(extras[: per_category - len(chosen)])
        out.extend(chosen[:per_category])
    return out
