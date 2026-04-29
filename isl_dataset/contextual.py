"""Contextual medical instruction phrases.

Each tuple: (text_en, gloss_sequence, text_hi, category)

ISL gloss conventions used:
  * UPPERCASE tokens; articles & copulas dropped.
  * Time-Subject-Verb / Topic-Comment ordering (OSV).
  * '+' joins compound signs (e.g. BLOOD+TEST).
  * '++' marks repetition / plural / continuous aspect.
  * '?' question marker stays at end (matches non-manual brow raise).
  * Negation follows the verb (EAT NOT).
"""

from __future__ import annotations

from .schema import MedicalCategory as C

CONTEXTUAL: list[tuple[str, str, str, C]] = [
    # --- First Aid / Emergency (1-10) ---------------------------------------
    ("Call the ambulance immediately.",
     "AMBULANCE CALL NOW",
     "तुरंत एम्बुलेंस बुलाओ।", C.FIRST_AID),

    ("Do not move the injured person.",
     "INJURE PERSON MOVE NOT",
     "घायल व्यक्ति को मत हिलाओ।", C.FIRST_AID),

    ("Apply pressure on the wound to stop bleeding.",
     "WOUND PRESS, BLOOD STOP",
     "खून रोकने के लिए घाव पर दबाव डालो।", C.FIRST_AID),

    ("If the person is unconscious, check their breathing.",
     "PERSON FAINT, BREATH CHECK",
     "अगर व्यक्ति बेहोश है, उसकी सांस जांचो।", C.FIRST_AID),

    ("Lay the patient flat and raise their legs.",
     "PATIENT LIE-FLAT, LEG UP",
     "मरीज़ को सीधा लिटाओ और पैर ऊपर उठाओ।", C.FIRST_AID),

    ("Do not give water to an unconscious patient.",
     "FAINT PATIENT, WATER GIVE NOT",
     "बेहोश मरीज़ को पानी मत दो।", C.FIRST_AID),

    ("Cover the burn with a clean cloth.",
     "BURN PLACE, CLEAN CLOTH COVER",
     "जले हुए स्थान को साफ कपड़े से ढको।", C.FIRST_AID),

    ("If choking, perform the Heimlich manoeuvre.",
     "CHOKE IF, HEIMLICH DO",
     "अगर गला रुक रहा है, हाइमलिक तकनीक करो।", C.FIRST_AID),

    ("Stay with the patient until help arrives.",
     "HELP ARRIVE FINISH, PATIENT WITH STAY",
     "मदद आने तक मरीज़ के साथ रहो।", C.FIRST_AID),

    ("Note the time the symptoms started.",
     "SYMPTOM START TIME, REMEMBER WRITE",
     "लक्षण शुरू होने का समय याद रखो।", C.FIRST_AID),

    # --- Pharmacy / Medication (11-22) --------------------------------------
    ("Take this tablet after dinner.",
     "NIGHT DINNER FINISH, TABLET ONE EAT",
     "रात के खाने के बाद यह गोली लो।", C.PHARMACY),

    ("Take one capsule twice a day with water.",
     "DAY TWICE, CAPSULE ONE WATER WITH SWALLOW",
     "एक कैप्सूल दिन में दो बार पानी के साथ लो।", C.PHARMACY),

    ("Apply this ointment three times daily.",
     "DAY THREE-TIMES, OINTMENT APPLY",
     "यह मरहम दिन में तीन बार लगाओ।", C.PHARMACY),

    ("Do not take this medicine on an empty stomach.",
     "STOMACH EMPTY, MEDICINE TAKE NOT",
     "खाली पेट यह दवा मत लो।", C.PHARMACY),

    ("Finish the full course of antibiotics.",
     "ANTIBIOTIC COURSE FULL FINISH MUST",
     "एंटीबायोटिक का पूरा कोर्स खत्म करो।", C.PHARMACY),

    ("Shake the syrup well before use.",
     "SYRUP USE BEFORE, SHAKE WELL",
     "उपयोग से पहले सिरप अच्छे से हिलाओ।", C.PHARMACY),

    ("Store this medicine in the refrigerator.",
     "MEDICINE FRIDGE INSIDE KEEP",
     "यह दवा फ्रिज में रखो।", C.PHARMACY),

    ("Do not share your medicine with others.",
     "MEDICINE YOUR, OTHER PERSON GIVE NOT",
     "अपनी दवा किसी और को मत दो।", C.PHARMACY),

    ("Avoid alcohol while taking this medication.",
     "MEDICINE TAKE TIME, ALCOHOL DRINK NOT",
     "यह दवा लेते समय शराब मत पियो।", C.PHARMACY),

    ("If you miss a dose, take it as soon as you remember.",
     "DOSE FORGET IF, REMEMBER TIME, TAKE",
     "अगर खुराक भूल जाओ, याद आते ही लो।", C.PHARMACY),

    ("Do not double the dose to make up.",
     "DOSE DOUBLE TAKE NOT",
     "छूटी खुराक की भरपाई के लिए दोगुनी मत लो।", C.PHARMACY),

    ("Two drops in each eye, morning and night.",
     "EYE EACH, DROP TWO, MORNING NIGHT",
     "हर आंख में दो बूंद, सुबह और रात।", C.PHARMACY),

    # --- Diagnostics / Procedures (23-32) -----------------------------------
    ("You need a blood test tomorrow.",
     "TOMORROW, BLOOD+TEST YOU NEED",
     "कल आपको रक्त जांच करानी है।", C.DIAGNOSTICS),

    ("Do not eat for 12 hours before your blood test.",
     "BLOOD+TEST BEFORE, HOUR TWELVE, EAT NOT",
     "रक्त जांच से 12 घंटे पहले कुछ मत खाओ।", C.DIAGNOSTICS),

    ("The X-ray will take about ten minutes.",
     "X-RAY TIME, MINUTE TEN ABOUT",
     "एक्स-रे लगभग दस मिनट का होगा।", C.DIAGNOSTICS),

    ("Please remove all metal objects before the MRI.",
     "MRI BEFORE, METAL ALL REMOVE",
     "MRI से पहले सारी धातु की चीजें निकाल दो।", C.DIAGNOSTICS),

    ("Your reports will be ready by evening.",
     "EVENING TIME, REPORT YOUR READY",
     "आपकी रिपोर्ट शाम तक तैयार होगी।", C.DIAGNOSTICS),

    ("We need a urine sample.",
     "URINE+SAMPLE WE NEED",
     "हमें मूत्र का नमूना चाहिए।", C.DIAGNOSTICS),

    ("This is a routine ECG.",
     "ECG NORMAL+CHECK ONLY",
     "यह सामान्य ईसीजी है।", C.DIAGNOSTICS),

    ("Lie still during the scan.",
     "SCAN DURING, STILL LIE",
     "स्कैन के दौरान स्थिर लेटे रहो।", C.DIAGNOSTICS),

    ("The biopsy result is negative.",
     "BIOPSY RESULT NEGATIVE",
     "बायोप्सी का परिणाम नेगेटिव है।", C.DIAGNOSTICS),

    ("We will repeat the test next week.",
     "NEXT-WEEK, TEST AGAIN DO",
     "अगले हफ्ते जांच दोबारा करेंगे।", C.DIAGNOSTICS),

    # --- Maternal Health (33-40) --------------------------------------------
    ("You are six weeks pregnant.",
     "PREGNANT YOU, WEEK SIX",
     "आप छह सप्ताह की गर्भवती हैं।", C.MATERNAL),

    ("The baby's heartbeat is normal.",
     "BABY HEART+BEAT NORMAL",
     "बच्चे की धड़कन सामान्य है।", C.MATERNAL),

    ("Take folic acid every day until delivery.",
     "FOLIC+ACID DAILY, DELIVERY UNTIL TAKE",
     "प्रसव तक रोज़ फोलिक एसिड लो।", C.MATERNAL),

    ("Avoid lifting heavy objects.",
     "HEAVY THING LIFT NOT",
     "भारी सामान मत उठाओ।", C.MATERNAL),

    ("You should sleep on your left side.",
     "SLEEP TIME, LEFT SIDE BETTER",
     "बाईं करवट सोना बेहतर है।", C.MATERNAL),

    ("Come for a check-up every month.",
     "MONTH EACH, CHECK-UP COME",
     "हर महीने जांच के लिए आओ।", C.MATERNAL),

    ("If you feel less movement, contact us immediately.",
     "BABY MOVE LESS IF, CALL NOW",
     "बच्चे की हलचल कम हो तो तुरंत बताओ।", C.MATERNAL),

    ("Breastfeed the baby within one hour of birth.",
     "BABY BORN FINISH, HOUR ONE INSIDE, BREASTFEED",
     "जन्म के एक घंटे के अंदर स्तनपान कराओ।", C.MATERNAL),

    # --- Cardiology (41-46) -------------------------------------------------
    ("Your blood pressure is high.",
     "BLOOD+PRESSURE YOUR HIGH",
     "आपका रक्तचाप अधिक है।", C.CARDIOLOGY),

    ("Reduce salt in your food.",
     "FOOD INSIDE, SALT LESS",
     "खाने में नमक कम करो।", C.CARDIOLOGY),

    ("Walk thirty minutes every day.",
     "DAILY, WALK MINUTE THIRTY",
     "रोज़ तीस मिनट टहलो।", C.CARDIOLOGY),

    ("If you feel chest pain, call the doctor.",
     "CHEST PAIN FEEL IF, DOCTOR CALL",
     "सीने में दर्द हो तो डॉक्टर को बुलाओ।", C.CARDIOLOGY),

    ("Take this aspirin once a day.",
     "DAY ONCE, ASPIRIN TAKE",
     "रोज़ एक एस्पिरिन लो।", C.CARDIOLOGY),

    ("Avoid smoking and oily food.",
     "SMOKE OIL+FOOD AVOID",
     "धूम्रपान और तले हुए खाने से बचो।", C.CARDIOLOGY),

    # --- Diabetes / Endocrinology (47-50) -----------------------------------
    ("Check your sugar level twice daily.",
     "DAY TWICE, SUGAR+LEVEL CHECK",
     "दिन में दो बार शुगर जांचो।", C.ENDOCRINOLOGY),

    ("Inject insulin before breakfast.",
     "BREAKFAST BEFORE, INSULIN INJECT",
     "नाश्ते से पहले इंसुलिन लगाओ।", C.ENDOCRINOLOGY),

    ("Do not eat sweets and rice together.",
     "SWEET RICE TOGETHER EAT NOT",
     "मिठाई और चावल एक साथ मत खाओ।", C.ENDOCRINOLOGY),

    ("Drink water often.",
     "WATER OFTEN++ DRINK",
     "बार-बार पानी पियो।", C.ENDOCRINOLOGY),

    # --- Pulmonology (51-56) ------------------------------------------------
    ("Use your inhaler when you feel breathless.",
     "BREATH+SHORT FEEL TIME, INHALER USE",
     "सांस फूलने पर इनहेलर लो।", C.PULMONOLOGY),

    ("Cover your mouth when you cough.",
     "COUGH TIME, MOUTH COVER",
     "खांसते समय मुंह ढको।", C.PULMONOLOGY),

    ("Stop smoking immediately.",
     "SMOKE STOP NOW",
     "धूम्रपान तुरंत बंद करो।", C.PULMONOLOGY),

    ("Stay away from dusty places.",
     "DUST PLACE AVOID",
     "धूल भरी जगह से दूर रहो।", C.PULMONOLOGY),

    ("Take steam twice a day.",
     "DAY TWICE, STEAM INHALE",
     "दिन में दो बार भाप लो।", C.PULMONOLOGY),

    ("Your TB test is positive — start treatment today.",
     "TB+TEST POSITIVE, TODAY TREATMENT START",
     "आपका टीबी टेस्ट पॉज़िटिव है — आज से इलाज शुरू।", C.PULMONOLOGY),

    # --- Vaccination / Public Health (57-62) --------------------------------
    ("Bring the child for vaccination next week.",
     "NEXT-WEEK, CHILD VACCINE+INJECT BRING",
     "अगले हफ्ते बच्चे को टीका लगवाने लाओ।", C.VACCINATION),

    ("This vaccine protects against polio.",
     "VACCINE THIS, POLIO PROTECT",
     "यह टीका पोलियो से बचाता है।", C.VACCINATION),

    ("After the injection some fever is normal.",
     "INJECT FINISH, FEVER LITTLE NORMAL",
     "इंजेक्शन के बाद हल्का बुखार सामान्य है।", C.VACCINATION),

    ("Wash your hands often.",
     "HAND OFTEN++ WASH",
     "बार-बार हाथ धोओ।", C.PUBLIC_HEALTH),

    ("Wear a mask in crowded places.",
     "CROWD PLACE, MASK WEAR",
     "भीड़ वाली जगह पर मास्क पहनो।", C.PUBLIC_HEALTH),

    ("Boil drinking water before use.",
     "WATER DRINK BEFORE, BOIL",
     "पीने का पानी पहले उबालो।", C.PUBLIC_HEALTH),

    # --- Pediatrics (63-66) -------------------------------------------------
    ("Feed the baby every two hours.",
     "HOUR TWO EACH, BABY FEED",
     "हर दो घंटे में बच्चे को दूध पिलाओ।", C.PEDIATRICS),

    ("If the baby has fever above 102, come to hospital.",
     "BABY FEVER 102 ABOVE IF, HOSPITAL COME",
     "बच्चे को 102 से ऊपर बुखार हो तो अस्पताल आओ।", C.PEDIATRICS),

    ("Do not give honey to babies under one year.",
     "BABY YEAR ONE BELOW, HONEY GIVE NOT",
     "एक साल से छोटे बच्चे को शहद मत दो।", C.PEDIATRICS),

    ("The child's growth is normal.",
     "CHILD GROW NORMAL",
     "बच्चे की वृद्धि सामान्य है।", C.PEDIATRICS),

    # --- Mental Health (67-70) ----------------------------------------------
    ("It is okay to ask for help.",
     "HELP ASK, OK",
     "मदद मांगना सही है।", C.PSYCHIATRY),

    ("Try to sleep eight hours every night.",
     "NIGHT EACH, SLEEP HOUR EIGHT TRY",
     "हर रात आठ घंटे सोने की कोशिश करो।", C.PSYCHIATRY),

    ("Take this medicine even if you feel better.",
     "FEEL BETTER IF ALSO, MEDICINE CONTINUE",
     "बेहतर महसूस होने पर भी दवा लेते रहो।", C.PSYCHIATRY),

    ("Talk to a counsellor when you feel anxious.",
     "ANXIOUS FEEL TIME, COUNSELLOR TALK",
     "घबराहट हो तो काउंसलर से बात करो।", C.PSYCHIATRY),

    # --- Surgery / Anesthesia (71-74) ---------------------------------------
    ("Do not eat or drink after midnight before surgery.",
     "SURGERY BEFORE, MIDNIGHT-AFTER, EAT DRINK NOT",
     "सर्जरी से पहले आधी रात के बाद कुछ मत खाओ-पियो।", C.ANESTHESIOLOGY),

    ("You will get anesthesia before the operation.",
     "OPERATION BEFORE, ANESTHESIA GIVE",
     "ऑपरेशन से पहले बेहोशी की दवा देंगे।", C.ANESTHESIOLOGY),

    ("Tell the doctor about all your allergies.",
     "ALLERGY ALL, DOCTOR INFORM",
     "डॉक्टर को सभी एलर्जी बताओ।", C.ANESTHESIOLOGY),

    ("After surgery, rest for two weeks.",
     "SURGERY AFTER, WEEK TWO REST",
     "सर्जरी के बाद दो हफ्ते आराम करो।", C.ANESTHESIOLOGY),

    # --- Orthopedics / Dermatology / ENT / Eye (75-86) ----------------------
    ("Apply ice on the swelling for ten minutes.",
     "SWELL PLACE, ICE MINUTE TEN APPLY",
     "सूजन पर दस मिनट बर्फ लगाओ।", C.ORTHOPEDICS),

    ("Wear the cast for six weeks.",
     "CAST WEAR, WEEK SIX",
     "छह हफ्ते तक प्लास्टर पहनो।", C.ORTHOPEDICS),

    ("Do physiotherapy every day.",
     "DAILY, PHYSIO+THERAPY DO",
     "रोज़ फिज़ियोथेरेपी करो।", C.ORTHOPEDICS),

    ("Do not scratch the rash.",
     "RASH SCRATCH NOT",
     "दाने को मत खुजाओ।", C.DERMATOLOGY),

    ("Apply sunscreen before going outside.",
     "OUTSIDE GO BEFORE, SUNSCREEN APPLY",
     "बाहर जाने से पहले सनस्क्रीन लगाओ।", C.DERMATOLOGY),

    ("Keep the wound dry and clean.",
     "WOUND DRY CLEAN KEEP",
     "घाव सूखा और साफ रखो।", C.DERMATOLOGY),

    ("Do not put cotton buds inside your ear.",
     "EAR INSIDE, COTTON+BUD PUT NOT",
     "कान के अंदर रुई की तीली मत डालो।", C.ENT),

    ("Gargle with warm salt water.",
     "WATER WARM SALT, GARGLE",
     "गर्म नमक पानी से गरारे करो।", C.ENT),

    ("Read this chart from line one.",
     "CHART, LINE ONE FROM READ",
     "यह चार्ट पहली पंक्ति से पढ़ो।", C.OPHTHALMOLOGY),

    ("Wear glasses for reading.",
     "READ TIME, GLASSES WEAR",
     "पढ़ते समय चश्मा पहनो।", C.OPHTHALMOLOGY),

    ("Do not rub your eyes.",
     "EYE RUB NOT",
     "आंख मत मलो।", C.OPHTHALMOLOGY),

    ("Visit the eye doctor once a year.",
     "YEAR ONCE, EYE+DOCTOR VISIT",
     "साल में एक बार आंखों के डॉक्टर से मिलो।", C.OPHTHALMOLOGY),

    # --- Hospital / Admin / Consent (87-92) ---------------------------------
    ("Please sign the consent form.",
     "CONSENT+FORM SIGN PLEASE",
     "कृपया सहमति पत्र पर हस्ताक्षर करो।", C.HOSPITAL),

    ("Bring your Aadhaar card and previous reports.",
     "AADHAAR-CARD REPORT OLD, BRING",
     "आधार कार्ड और पुरानी रिपोर्ट लाओ।", C.HOSPITAL),

    ("The doctor will see you in fifteen minutes.",
     "MINUTE FIFTEEN, DOCTOR SEE YOU",
     "डॉक्टर पंद्रह मिनट में आपको देखेंगे।", C.HOSPITAL),

    ("Visiting hours are five to seven in the evening.",
     "EVENING, FIVE-SEVEN, VISIT TIME",
     "मिलने का समय शाम पांच से सात है।", C.HOSPITAL),

    ("The bill will be ready at the counter.",
     "BILL COUNTER READY",
     "बिल काउंटर पर तैयार है।", C.HOSPITAL),

    ("Use the wheelchair to go to the X-ray room.",
     "WHEELCHAIR USE, X-RAY+ROOM GO",
     "व्हीलचेयर से एक्स-रे कक्ष जाओ।", C.HOSPITAL),

    # --- Symptom checks / Q-A (93-100) --------------------------------------
    ("Where does it hurt?",
     "PAIN PLACE WHERE?",
     "दर्द कहाँ हो रहा है?", C.SYMPTOMS),

    ("Since when do you have this pain?",
     "PAIN, WHEN-FROM HAVE?",
     "यह दर्द कब से है?", C.SYMPTOMS),

    ("Are you allergic to any medicine?",
     "MEDICINE ANY, ALLERGY YOU?",
     "क्या आपको किसी दवा से एलर्जी है?", C.SYMPTOMS),

    ("Have you taken your medicine today?",
     "TODAY, MEDICINE TAKE FINISH YOU?",
     "क्या आज आपने दवा ली?", C.SYMPTOMS),

    ("Show me on a scale of one to ten how bad the pain is.",
     "PAIN, SCALE ONE-TEN, HOW-MUCH SHOW",
     "दर्द को 1 से 10 के पैमाने पर दिखाओ।", C.SYMPTOMS),

    ("Do you feel dizzy when you stand up?",
     "STAND-UP TIME, DIZZY FEEL YOU?",
     "खड़े होने पर चक्कर आता है क्या?", C.SYMPTOMS),

    ("Have you eaten anything in the last six hours?",
     "HOUR SIX BEFORE, FOOD ANY EAT YOU?",
     "पिछले छह घंटे में कुछ खाया?", C.SYMPTOMS),

    ("Are you taking any other medicines?",
     "OTHER MEDICINE ANY, TAKE YOU?",
     "क्या और कोई दवा ले रहे हो?", C.SYMPTOMS),
]


def all_contextual() -> list[tuple[str, str, str, C]]:
    """Return the full contextual list (currently 100; extend as ISLRTC data lands)."""
    return list(CONTEXTUAL)
