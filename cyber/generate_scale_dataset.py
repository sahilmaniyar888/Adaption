from __future__ import annotations

import csv
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).parent
DATASET = ROOT / "dataset_v0.csv"
PATTERNS = ROOT / "pattern_library.csv"
ANCHORS = ROOT / "genuine_anchors.csv"

SCAMS = ["digital_arrest", "upi_collect_request", "fake_courier_parcel", "fake_kyc"]
LANGS = ["English", "Hindi", "Marathi", "Hinglish"]
LANG_CODE = {"English": "EN", "Hindi": "HI", "Marathi": "MR", "Hinglish": "HIN"}
SCAM_CODE = {
    "digital_arrest": "DA",
    "upi_collect_request": "UPI",
    "fake_courier_parcel": "FC",
    "fake_kyc": "KYC",
}
SCRIPT = {"English": "Latin", "Hindi": "Devanagari", "Marathi": "Devanagari", "Hinglish": "Latin"}
VALIDATION = {
    "English": "machine_generated",
    "Hinglish": "machine_generated",
    "Hindi": "needs_human_review",
    "Marathi": "needs_human_review",
}

TARGET_TRIPLETS = {
    "digital_arrest": {"English": 2, "Hindi": 4, "Marathi": 2, "Hinglish": 2},
    "upi_collect_request": {"English": 2, "Hindi": 2, "Marathi": 2, "Hinglish": 4},
    "fake_courier_parcel": {"English": 2, "Hindi": 2, "Marathi": 4, "Hinglish": 2},
    "fake_kyc": {"English": 4, "Hindi": 2, "Marathi": 2, "Hinglish": 2},
}

POOLS = {
    "digital_arrest": {
        "patterns": ["PAT-DA-001", "PAT-DA-002", "PAT-DA-003", "PAT-DA-004", "PAT-DA-005", "PAT-DA-007", "PAT-DA-008"],
        "genuine_pattern": "PAT-DA-006",
        "anchors": ["ANC-CYBER-002", "ANC-CYBER-003", "ANC-SBI-005", "ANC-HDFC-003"],
    },
    "upi_collect_request": {
        "patterns": ["PAT-UPI-001", "PAT-UPI-002", "PAT-UPI-003", "PAT-UPI-004", "PAT-UPI-007", "PAT-UPI-008"],
        "genuine_pattern": "PAT-UPI-008",
        "anchors": ["ANC-SMS-001", "ANC-SMS-002", "ANC-SMS-003", "ANC-SMS-005", "ANC-NPCI-003", "ANC-SBI-003"],
    },
    "fake_courier_parcel": {
        "patterns": ["PAT-FC-001", "PAT-FC-002", "PAT-FC-003", "PAT-FC-004", "PAT-FC-005", "PAT-FC-007", "PAT-FC-008"],
        "genuine_pattern": "PAT-FC-006",
        "anchors": ["ANC-SMS-021", "ANC-SMS-022", "ANC-SMS-023", "ANC-SMS-028", "ANC-SMS-030", "ANC-SMS-031"],
    },
    "fake_kyc": {
        "patterns": ["PAT-KYC-001", "PAT-KYC-002", "PAT-KYC-003", "PAT-KYC-004", "PAT-KYC-005", "PAT-KYC-007", "PAT-KYC-008"],
        "genuine_pattern": "PAT-KYC-001",
        "anchors": ["ANC-SMS-013", "ANC-SMS-014", "ANC-SMS-015", "ANC-SMS-017", "ANC-SMS-018", "ANC-SMS-019", "ANC-RBI-001"],
    },
}

BANKS = ["BOI", "SBI", "HDFC Bank", "ICICI Bank", "Bank of Maharashtra", "Axis Bank"]
COURIERS = ["Blue Dart", "FedEx", "Shiprocket", "Xpressbees", "India Post", "Delhivery"]
AGENCIES = ["CBI", "Mumbai Crime Branch", "Cyber Crime Branch", "Narcotics Control Bureau", "RBI", "ED"]
MERCHANTS = ["KIRAN SNACKS", "CITY CAFE", "RAJ MEDICAL", "MAULI FOODS", "GREEN MART", "BOOKS INDIA"]
BANK_SHORT = {
    "Bank of Maharashtra": "MAHABANK",
    "Bank of India": "BOI",
    "HDFC Bank": "HDFC",
    "ICICI Bank": "ICICI",
    "Axis Bank": "AXIS",
    "SBI": "SBI",
    "BOI": "BOI",
}
LINKS = {
    "fake_kyc": ["kyc-boi-secure[.]xyz", "sbi-kyc-update[.]info", "hdfc-secure-verify[.]xyz", "axis-kycfast[.]site"],
    "fake_courier_parcel": ["track-bluedart-help[.]xyz", "fedex-case-clear[.]site", "shiprocket-verify[.]xyz"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pick(items: list[str], idx: int) -> str:
    return items[idx % len(items)]


def rrn(idx: int) -> str:
    return str(731482905164 + idx * 9173)[-12:]


def acct(idx: int) -> str:
    return f"X{(4821 + idx * 137) % 9000 + 1000}"


def amount(idx: int) -> int:
    return [49, 75, 125, 240, 300, 499, 850, 999, 1850, 1999][idx % 10]


def date(idx: int) -> str:
    day = [4, 7, 12, 16, 21, 23, 27][idx % 7]
    mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"][idx % 6]
    return f"{day:02d}-{mon}-26"


def institution_for(scam: str, idx: int) -> str:
    if scam == "fake_courier_parcel":
        return pick(COURIERS, idx)
    if scam == "digital_arrest":
        return pick(AGENCIES, idx)
    return pick(BANKS, idx)


CYBERDOST_VARIANTS = {
    "English": [
        "CyberDost: No police, CBI or RBI officer conducts inquiry or arrest on video call. Disconnect and report on 1930.",
        "CyberDost: Beware of scammers posing as CBI/ED/Customs over video call. Hang up and dial 1930 or visit cybercrime.gov.in.",
        "I4C-CyberDost: 'Digital arrest' is a scam. No genuine officer keeps you on video call to verify Aadhaar or bank. Report on 1930.",
        "CyberDost: Got a threat call claiming case against you? Disconnect, do not pay, do not share OTP. Helpline 1930.",
    ],
    "Hindi": [
        "CyberDost: कोई police/CBI/RBI officer video call पर पूछताछ या arrest नहीं करता. Call काटें और 1930 पर report करें.",
        "CyberDost: Digital arrest एक scam है. किसी भी officer के नाम पर video call आए तो call काट दें और 1930 पर शिकायत करें.",
        "I4C-CyberDost: किसी भी एजेंसी के नाम पर पैसे, OTP या Aadhaar मांगा जाए तो 1930 पर report करें. cybercrime.gov.in पर जाएं.",
        "CyberDost: सरकारी एजेंसी कभी video call पर arrest या जांच नहीं करती. डरें नहीं, call disconnect करें, 1930 dial करें.",
    ],
    "Marathi": [
        "CyberDost: कोणतीही police/CBI/RBI agency video call वर arrest किंवा चौकशी करत नाही. Call कट करा आणि 1930 वर report करा.",
        "CyberDost: Digital arrest हा scam आहे. कोणत्याही एजेंसीच्या नावाने video call आल्यास call कट करा, 1930 वर तक्रार द्या.",
        "I4C-CyberDost: सरकारी अधिकारी video call वर पैसे, OTP किंवा Aadhaar कधीही मागत नाहीत. 1930 dial करा.",
        "CyberDost: घाबरू नका, video call वर कोणतीही चौकशी होत नाही. Call disconnect करा आणि cybercrime.gov.in वर तक्रार नोंदवा.",
    ],
    "Hinglish": [
        "CyberDost: Police/CBI/RBI video call pe arrest ya inquiry nahi karti. Call cut karo aur 1930 par report karo.",
        "CyberDost: Digital arrest ek scam hai. Kisi bhi officer ke naam se video call aaye to disconnect karo, 1930 dial karo.",
        "I4C-CyberDost: Sarkari agency kabhi OTP, Aadhaar ya paise video call pe nahi mangti. cybercrime.gov.in pe report karo.",
        "CyberDost: Dare mat, video call pe inquiry nahi hoti. Call cut karo, 1930 par complaint do.",
    ],
}


def genuine_message(scam: str, lang: str, idx: int, tidx: int = 0) -> tuple[str, str]:
    merchant = pick(MERCHANTS, idx)
    amt = amount(idx)
    account = acct(idx)
    ref = rrn(idx)
    txn_date = date(idx)
    courier = institution_for("fake_courier_parcel", idx)

    if scam == "digital_arrest":
        return "SMS", pick(CYBERDOST_VARIANTS[lang], tidx)

    if scam == "upi_collect_request":
        otp = f"{(123456 + idx * 4583) % 900000 + 100000}"
        upi_g = {
            "English": [
                f"A/c {account} debited by Rs. {amt}.00 for UPI payment to {merchant} on {txn_date}. RRN: {ref} if not you, call bank. -MAHABANK",
                f"Rs.{amt}.00 credited to A/c {account} on {txn_date} from {merchant}. UPI Ref {ref}. Avl Bal Rs.{amt*7+150}.00 -MAHABANK",
                f"OTP {otp} for UPI txn of Rs.{amt} to {merchant}. Valid 5 min. Do not share. -MAHABANK",
            ],
            "Hindi": [
                f"A/c {account} से Rs.{amt}.00 UPI payment {merchant} को debit हुआ on {txn_date}. RRN: {ref}. Not you? bank को call करें. -MAHABANK",
                f"Rs.{amt}.00 A/c {account} में {merchant} से credit हुआ on {txn_date}. UPI Ref {ref}. Avl Bal Rs.{amt*7+150}.00 -MAHABANK",
                f"OTP {otp} UPI txn Rs.{amt} {merchant} के लिए. 5 min valid. किसी से share न करें. -MAHABANK",
            ],
            "Marathi": [
                f"A/c {account} मधून Rs.{amt}.00 UPI payment {merchant} ला debit झाला on {txn_date}. RRN: {ref}. Not you? bank ला call करा. -MAHABANK",
                f"Rs.{amt}.00 A/c {account} मध्ये {merchant} कडून credit झाले on {txn_date}. UPI Ref {ref}. Avl Bal Rs.{amt*7+150}.00 -MAHABANK",
                f"OTP {otp} UPI txn Rs.{amt} {merchant} साठी. 5 min valid. कोणालाही share करू नका. -MAHABANK",
            ],
            "Hinglish": [
                f"A/c {account} se Rs.{amt}.00 UPI payment {merchant} ko debit hua on {txn_date}. RRN: {ref}. Not you? call bank. -MAHABANK",
                f"Rs.{amt}.00 A/c {account} me {merchant} se credit hua on {txn_date}. UPI Ref {ref}. Avl Bal Rs.{amt*7+150}.00 -MAHABANK",
                f"OTP {otp} UPI txn Rs.{amt} {merchant} ke liye. 5 min valid. Kisi ko share mat karo. -MAHABANK",
                f"IMPS Rs.{amt}.00 transfer to {merchant} A/c successful. UPI Ref {ref}. Charge Rs.5.00 deducted. -MAHABANK",
            ],
        }
        return "SMS", pick(upi_g[lang], tidx)

    if scam == "fake_courier_parcel":
        track_id = f"{courier[:2].upper()}{482916 + idx * 17}"
        slot = ["10AM-1PM", "1PM-4PM", "4PM-7PM"][idx % 3]
        fc_g = {
            "English": [
                f"{courier}: Your shipment will be delivered today. Track ID {track_id}. Avoid links or info requests from unknown numbers. -{courier}",
                f"{courier}: Out for delivery — slot {slot}. AWB {track_id}. Live track on app only. Unknown links se beware. -{courier}",
                f"{courier}: Parcel {track_id} delivered to recipient at door. Thank you. Report wrongly marked items via in-app chat. -{courier}",
            ],
            "Hindi": [
                f"{courier}: आपका parcel आज deliver होगा. Track ID {track_id}. Unknown numbers से आए links न खोलें, info share न करें. -{courier}",
                f"{courier}: Out for delivery — slot {slot}. AWB {track_id}. App पर ही live track देखें. -{courier}",
                f"{courier}: Parcel {track_id} दरवाजे पर deliver हो गया. Wrongly marked हो तो in-app chat पर report करें. -{courier}",
            ],
            "Marathi": [
                f"{courier}: तुमची shipment आज deliver होईल. Track ID {track_id}. अनोळखी नंबरवरून आलेल्या links उघडू नका, माहिती शेअर करू नका. -{courier}",
                f"{courier}: Out for delivery — slot {slot}. AWB {track_id}. App वरच live track बघा. -{courier}",
                f"{courier}: Parcel {track_id} दरवाजावर deliver झाले. चुकीचे marked असल्यास in-app chat वर report करा. -{courier}",
                f"{courier}: Pickup scheduled for AWB {track_id}, slot {slot}. Rider संपर्क App मध्ये. -{courier}",
            ],
            "Hinglish": [
                f"{courier}: Aapka parcel aaj deliver hoga. Track ID {track_id}. Unknown number ke links open mat karo, info share mat karo. -{courier}",
                f"{courier}: Out for delivery — slot {slot}. AWB {track_id}. App pe hi live track dekho. -{courier}",
                f"{courier}: Parcel {track_id} darwaze pe deliver ho gaya. Galat marked ho to in-app chat pe report karo. -{courier}",
            ],
        }
        return "SMS", pick(fc_g[lang], tidx)

    bank = pick(["BOI", "SBI", "HDFC", "ICICI", "AXIS"], idx)
    end = str((4187 + idx * 233) % 9000 + 1000)
    kyc_g = {
        "English": [
            f"{bank}-Your A/C No XXXX{end} is inactive since 15-02-2026,Please contact Branch with Fresh KYC Document for verification.",
            f"{bank}: Re-KYC due for A/c XXXX{end}. Update via {bank} mobile app (Service > Re-KYC) or visit any branch by 30-Jun-26.",
            f"{bank}: Periodic KYC pending for A/c XXXX{end}. No action needed if updated in last 6 months. Verify via official app. -{bank}",
            f"Dear {bank} customer, your A/c XXXX{end} CKYC ID has been generated. Quote it for any future onboarding. Helpline 1800-XXX. -{bank}",
        ],
        "Hindi": [
            f"प्रिय {bank} ग्राहक, आपका A/C XXXX{end} inactive है. KYC update के लिए branch में Fresh KYC Document लेकर जाएं. -{bank}",
            f"{bank}: A/c XXXX{end} के लिए Re-KYC due है. {bank} mobile app (Service > Re-KYC) से या 30-Jun-26 तक किसी भी branch में update करें.",
            f"{bank}: A/c XXXX{end} के लिए periodic KYC pending. पिछले 6 महीने में update हुआ हो तो कुछ करने की जरूरत नहीं. Official app से verify करें. -{bank}",
        ],
        "Marathi": [
            f"प्रिय {bank} ग्राहक, तुमचे A/C XXXX{end} inactive आहे. KYC update साठी branch मध्ये Fresh KYC Document घेऊन भेट द्या. -{bank}",
            f"{bank}: A/c XXXX{end} साठी Re-KYC due आहे. {bank} mobile app (Service > Re-KYC) मधून किंवा 30-Jun-26 पर्यंत कोणत्याही branch मध्ये update करा.",
            f"{bank}: A/c XXXX{end} साठी periodic KYC pending. गेल्या 6 महिन्यात update केले असल्यास काही करायची गरज नाही. Official app वरून verify करा. -{bank}",
        ],
        "Hinglish": [
            f"{bank}-A/C XXXX{end} inactive hai since 15-02-2026. Fresh KYC Document ke saath Branch visit karein.",
            f"{bank}: A/c XXXX{end} ke liye Re-KYC due hai. {bank} mobile app (Service > Re-KYC) se ya 30-Jun-26 tak kisi bhi branch me update karo.",
            f"{bank}: A/c XXXX{end} ke liye periodic KYC pending. Last 6 months me update hua hai to kuch karne ki zarurat nahi. Official app se verify karo. -{bank}",
        ],
    }
    return "SMS", pick(kyc_g[lang], tidx)


def scam_message(scam: str, lang: str, pattern_id: str, idx: int, surface: str, tidx: int = 0) -> tuple[str, str, bool, str, str, str, str]:
    bank = pick(BANKS, idx)
    bank_short = BANK_SHORT.get(bank, bank)
    agency = institution_for("digital_arrest", idx)
    courier = institution_for("fake_courier_parcel", idx)
    amt = amount(idx)
    link = pick(LINKS.get(scam, ["bit[.]ly/kyc482"]), idx)

    if scam == "digital_arrest":
        da_templates = {
            "English": [
                f"Caller claimed to be from {agency}, said Aadhaar was linked to a criminal case, and kept the victim on video call while demanding account verification.",
                f"Person on video call wore a fake {agency} uniform, showed a forged FIR with the victim's name, and warned that disconnecting would mean immediate arrest.",
                f"Caller said {agency} traced narcotics in a parcel sent in the victim's name and ordered the victim to stay on camera until 'remand verification' was complete.",
            ],
            "Hindi": [
                f"कॉलर ने खुद को {agency} बताया, Aadhaar को case से जोड़ा और video call चालू रखकर account verification के लिए दबाव बनाया.",
                f"video call पर {agency} की uniform पहने व्यक्ति ने fake FIR दिखाई और कहा call काटी तो तुरंत arrest होगा.",
                f"{agency} का नाम लेकर कॉलर बोला तुम्हारे नाम का parcel narcotics के साथ पकड़ा, camera on रखो वरना remand होगा.",
                f"{agency} officer होने का दावा करके कॉलर ने कहा money laundering case चल रहा है, settlement के लिए abhi RTGS करो वरना घर पर पुलिस आएगी.",
            ],
            "Marathi": [
                f"कॉलरने स्वतःला {agency} officer सांगितले, Aadhaar case शी जोडले आणि video call चालू ठेवून account verification साठी दबाव टाकला.",
                f"video call वर {agency} ची uniform घातलेल्या व्यक्तीने खोटी FIR दाखवली आणि म्हटले call कट केली तर लगेच arrest होईल.",
                f"{agency} च्या नावाने कॉलर म्हणाला तुमच्या नावाने narcotics parcel पकडले, camera चालू ठेवा नाही तर remand होईल.",
                f"{agency} officer असल्याचा दावा करून कॉलर म्हणाला money laundering case चालू आहे, settlement साठी आत्ता RTGS करा नाही तर पोलिस घरी येतील.",
            ],
            "Hinglish": [
                f"Caller ne khud ko {agency} bataya, Aadhaar case se link bola aur video call chalu rakhne ka pressure dala.",
                f"Video call par {agency} ki fake uniform pehne banda nakli FIR dikha raha tha, bola call cut kiya to seedha arrest.",
                f"{agency} ka officer banke caller bola tumhare naam ka parcel narcotics ke saath pakda gaya, camera on rakho warna remand.",
            ],
        }
        text = pick(da_templates[lang], tidx)
        return surface, text, False, "none", f"{agency}|Aadhaar|WhatsApp", "fake_arrest|isolation|video_call_pressure", "stay_on_video_call"

    if scam == "upi_collect_request":
        upi_templates = {
            "English": [
                f"Rs.{amt} refund pending. Approve UPI collect from {bank_short}-REFUND. Credit today.",
                f"{bank_short} cashback Rs.{amt} ready. Tap APPROVE on UPI app within 5 min or amount lapses.",
                f"Power bill double-debit refund Rs.{amt}. Accept the {bank_short}-REFUND collect request, money will hit account.",
            ],
            "Hindi": [
                f"Rs.{amt} refund pending है. {bank_short}-REFUND का UPI collect approve करें. Credit आज होगा.",
                f"{bank_short} cashback Rs.{amt} ready है. UPI app पर 5 min में APPROVE करो वरना expire.",
                f"बिजली bill double cut हो गया, Rs.{amt} वापस. {bank_short}-REFUND का collect request accept करें, पैसे आ जाएंगे.",
            ],
            "Marathi": [
                f"Rs.{amt} refund pending आहे. {bank_short}-REFUND कडून आलेला UPI collect approve करा. Credit आज होईल.",
                f"{bank_short} cashback Rs.{amt} तयार आहे. UPI app वर 5 min मध्ये APPROVE करा, नाही तर expire होईल.",
                f"वीज bill double cut झाले, Rs.{amt} परत. {bank_short}-REFUND चा collect request accept करा, पैसे लगेच मिळतील.",
            ],
            "Hinglish": [
                f"Rs.{amt} refund pending hai. {bank_short}-REFUND se UPI collect approve karo. Aaj hi credit hoga.",
                f"{bank_short} cashback Rs.{amt} ready hai. UPI app par 5 min me APPROVE karo warna expire ho jayega.",
                f"Bijli bill double cut hua, Rs.{amt} wapas. {bank_short}-REFUND ka collect request accept karo, paise turant aayenge.",
                f"{bank_short}-REFUND: prize amount Rs.{amt} jeeti hai. UPI request approve karo aur PIN dalo, paise wallet me aa jayenge.",
            ],
        }
        text = pick(upi_templates[lang], tidx)
        return surface, text, False, "none", f"{bank}|{bank_short}|UPI", "refund_lure|hidden_upi_pin_risk|unknown_collect_request|bank_impersonation", "approve_collect_request"

    if scam == "fake_courier_parcel":
        if pattern_id == "PAT-FC-008":
            ussd_templates = {
                "English": [
                    f"Caller posed as {courier} delivery staff, said address confirmation failed, and pushed the user to dial a special code before delivery hold.",
                    f"Person on phone claimed to be {courier} hub manager, sent an SMS with a star-hash code, and demanded the user dial it to 'release' the parcel.",
                    f"Caller pretending to be {courier} executive said the courier was undeliverable until the recipient activated a forwarding code dictated over phone.",
                ],
                "Hindi": [
                    f"कॉलर ने खुद को {courier} delivery agent बताया. Address confirm नहीं हो रहा बोलकर SMS वाला special code dial करने की जल्दी कराई.",
                    f"Phone पर {courier} hub manager बनकर बोला, star-hash code का SMS भेजा और parcel छुड़वाने के लिए dial करने पर जोर डाला.",
                    f"{courier} का executive होने का दावा करके कॉलर ने कहा parcel deliver नहीं होगा जब तक forwarding code activate नहीं किया जाए.",
                ],
                "Marathi": [
                    f"कॉलरने {courier} delivery agent असल्याचे सांगितले. address confirm होत नसल्यामुळे SMS मधला special code dial करायला घाई केली.",
                    f"फोनवर {courier} hub manager म्हणून बोलला, star-hash code चा SMS पाठवला आणि parcel सोडवण्यासाठी dial करायला सांगितले.",
                    f"{courier} executive असल्याचा दावा करून कॉलर म्हणाला forwarding code activate केल्याशिवाय parcel deliver होणार नाही.",
                    f"{courier} customer care म्हणून कॉलर बोलला, OTP verify करण्यासाठी फोनवर typed digits बोलायला सांगितले, पुढे call divert झाला.",
                ],
                "Hinglish": [
                    f"Caller ne {courier} delivery agent bola. Address confirm nahi ho raha, SMS ka special code dial karo warna parcel hold.",
                    f"Phone par {courier} hub manager banke bola, star-hash code SMS bheja aur parcel release ke liye dial karne ka pressure dala.",
                    f"{courier} executive bata ke caller bola jab tak forwarding code activate nahi karoge parcel deliver nahi hoga.",
                ],
            }
            text = pick(ussd_templates[lang], tidx)
            return surface, text, False, "none", courier, "courier_impersonation|asks_to_dial_code|urgency", "dial_fake_ussd_code"
        if surface == "SMS":
            sms_templates = {
                "English": [
                    f"{courier}: Parcel held for address issue. Confirm now at {link} Ref PRC{482 + idx}.",
                    f"{courier} ALERT: Delivery cancelled due to incomplete address. Reschedule via {link} (Ref {482 + idx}).",
                    f"{courier}: Customs duty Rs.{amt} pending on your parcel. Pay at {link} to avoid return. PRC{482 + idx}.",
                ],
                "Hindi": [
                    f"{courier}: Parcel address issue से hold है. Confirm करें {link} Ref PRC{482 + idx}.",
                    f"{courier} ALERT: address adhura होने से delivery cancel. Reschedule करें {link} (Ref {482 + idx}).",
                    f"{courier}: Parcel पर customs duty Rs.{amt} pending. Return से बचने के लिए pay करें {link}. PRC{482 + idx}.",
                ],
                "Marathi": [
                    f"{courier}: parcel address issue मुळे hold आहे. Confirm करा {link} Ref PRC{482 + idx}.",
                    f"{courier} ALERT: address अपूर्ण असल्याने delivery cancel. Reschedule करा {link} (Ref {482 + idx}).",
                    f"{courier}: parcel वर customs duty Rs.{amt} pending. Return टाळण्यासाठी pay करा {link}. PRC{482 + idx}.",
                    f"{courier}: PIN code mismatch मुळे parcel वापस गेला. New slot निवडण्यासाठी {link} वर जा. PRC{482 + idx}.",
                ],
                "Hinglish": [
                    f"{courier}: Parcel address issue se hold hai. Confirm karo {link} Ref PRC{482 + idx}.",
                    f"{courier} ALERT: address adhura hone se delivery cancel. Reschedule karo {link} (Ref {482 + idx}).",
                    f"{courier}: Parcel par customs duty Rs.{amt} pending. Return se bachne ke liye pay karo {link}. PRC{482 + idx}.",
                ],
            }
            text = pick(sms_templates[lang], tidx)
            return surface, text, True, "shortened", courier, "courier_impersonation|inert_link|urgency", "open_courier_link"
        illegal_templates = {
            "English": [
                f"Caller claimed a parcel in the user name contained illegal items and transferred the call to a fake cyber officer for urgent verification.",
                f"Person posed as {courier} security desk, said the parcel held banned drugs, and patched the call to a fake DCP for statement recording.",
                f"Voice claimed Aadhaar misuse for shipping illegal goods through {courier}, then passed the call to a fake Mumbai Crime Branch officer.",
            ],
            "Hindi": [
                f"कॉलर ने कहा user के नाम का parcel illegal items के साथ पकड़ा गया और call fake cyber officer को transfer कर दी.",
                f"{courier} security desk बनकर बोला parcel में banned drugs मिले, और call नकली DCP को statement के लिए जोड़ दी.",
                f"आवाज़ बोली Aadhaar misuse करके {courier} से illegal goods भेजे गए, फिर call नकली Mumbai Crime Branch officer को दे दी.",
            ],
            "Marathi": [
                f"कॉलरने user च्या नावाचे parcel illegal items सह पकडले असे सांगितले आणि call fake cyber officer कडे transfer केला.",
                f"{courier} security desk म्हणून बोलला parcel मध्ये banned drugs सापडले, आणि call खोट्या DCP कडे statement साठी जोडला.",
                f"आवाजाने सांगितले Aadhaar misuse करून {courier} मधून illegal goods पाठवले, मग call खोट्या Mumbai Crime Branch officer ला दिला.",
                f"{courier} fraud cell म्हणून कॉलर म्हणाला तुमच्या नावाने parcel मध्ये fake currency आहे, customs officer ला direct जोडतो म्हणून call hold वर ठेवला.",
            ],
            "Hinglish": [
                f"Caller ne bola user ke naam ka parcel illegal items ke saath pakda gaya, phir call fake cyber officer ko transfer kiya.",
                f"{courier} security desk banke bola parcel me banned drugs mile, aur call nakli DCP ko statement ke liye join kar di.",
                f"Awaaz boli Aadhaar misuse karke {courier} se illegal goods bheje gaye, phir call nakli Mumbai Crime Branch officer ko de di.",
            ],
        }
        text = pick(illegal_templates[lang], tidx)
        return surface, text, False, "none", f"{courier}|Cyber Crime Branch", "illegal_parcel_threat|fake_transfer|urgency", "join_fake_inquiry"

    apk = pattern_id == "PAT-KYC-008"
    link_pattern = "apk_drop" if apk else "lookalike_bank"
    action = "APK security update" if apk else "KYC update"
    kyc_templates = {
        "English": [
            f"{bank_short} KYC expired! Ur A/c will block today. {action}: {link} Ref KYC{482 + idx} -{bank_short}",
            f"Dear Customer, {bank_short} A/c suspension at 6 PM today due to pending KYC. {action} via {link}. Ref:{482+idx}",
            f"{bank_short} ALERT: PAN-Aadhaar mismatch detected. Complete {action} in next 2 hrs at {link} or A/c freeze. -{bank_short}",
            f"URGENT-{bank_short}: Reward points worth Rs.{amt} expiring tonight. Redeem after {action} at {link}. KYC{482 + idx}",
        ],
        "Hindi": [
            f"{bank_short} KYC expired! A/c आज block होगा. {action} करें {link} Ref KYC{482 + idx} -{bank_short}",
            f"प्रिय Customer, pending KYC के कारण आज 6 बजे {bank_short} A/c suspend हो जाएगा. {action} करें {link}. Ref:{482+idx}",
            f"{bank_short} ALERT: PAN-Aadhaar mismatch detected. अगले 2 ghante में {action} करें {link} वरना A/c freeze. -{bank_short}",
        ],
        "Marathi": [
            f"{bank_short} KYC expired! A/c आज block होईल. {action} करा {link} Ref KYC{482 + idx} -{bank_short}",
            f"प्रिय Customer, pending KYC मुळे आज 6 वाजता {bank_short} A/c suspend होईल. {action} करा {link}. Ref:{482+idx}",
            f"{bank_short} ALERT: PAN-Aadhaar mismatch आढळले. पुढच्या 2 तासात {action} करा {link} नाही तर A/c freeze. -{bank_short}",
        ],
        "Hinglish": [
            f"{bank_short} KYC expired! A/c aaj block hoga. {action} karo {link} Ref KYC{482 + idx} -{bank_short}",
            f"Dear Customer, pending KYC ki wajah se aaj 6 baje {bank_short} A/c suspend ho jayega. {action} karo {link}. Ref:{482+idx}",
            f"{bank_short} ALERT: PAN-Aadhaar mismatch detected. Agle 2 ghante me {action} karo {link} warna A/c freeze. -{bank_short}",
        ],
    }
    text = pick(kyc_templates[lang], tidx)
    return surface, text, True, link_pattern, f"{bank}|{bank_short}", "urgent|lookalike_bank_link|account_block_threat", "click_kyc_link"


def help_message(scam: str, lang: str, idx: int, surface: str, tidx: int = 0) -> tuple[str, str, str]:
    bank = pick(BANKS, idx)
    bank_short = BANK_SHORT.get(bank, bank)
    agency = institution_for("digital_arrest", idx)
    courier = institution_for("fake_courier_parcel", idx)
    amt = amount(idx)

    if scam == "digital_arrest":
        h_da = {
            "English": [
                f"Uncle, someone saying {agency} put me under digital arrest on video call. They told me not to disconnect. Should I call 1930?",
                f"Bhaiya help — guy in {agency} uniform on Skype showing my Aadhaar, says case filed, asking transfer for verification. Real or scam?",
                f"Sister, woman claiming {agency} officer threatening jail if I don't stay on camera. Hands shaking, what do I do, dial 1930?",
            ],
            "Hindi": [
                f"भैया, कोई {agency} वाला digital arrest बोल रहा है और video call काटने मना कर रहा है. 1930 पर call करूं क्या?",
                f"भैया मदद — Skype पर {agency} uniform में आदमी मेरा Aadhaar दिखा रहा, case file होने की धमकी देकर transfer मांग रहा. Real है क्या?",
                f"दीदी, औरत {agency} officer बता के बोल रही camera off किया तो jail. हाथ कांप रहे, 1930 dial करूं?",
                f"पापा सुनो — {agency} का बंदा बोल रहा money laundering का case है, 2 lakh RTGS नहीं किया तो घर पर पुलिस आएगी. क्या करूं?",
            ],
            "Marathi": [
                f"दादा, {agency} वाला digital arrest म्हणतोय आणि video call कट करू नको म्हणतो. 1930 ला call करू का?",
                f"दादा मदत — Skype वर {agency} uniform मधला माणूस माझे Aadhaar दाखवतोय, case file केल्याची धमकी देऊन transfer मागतोय. खरं आहे का?",
                f"ताई, बाई {agency} officer सांगून म्हणतेय camera off केला तर jail. हात थरथरतायत, 1930 dial करू का?",
            ],
            "Hinglish": [
                f"Bhai, {agency} wala digital arrest bol raha hai aur video call cut mat karo keh raha. 1930 pe call karu kya?",
                f"Bhaiya help — Skype par {agency} uniform me banda mera Aadhaar dikha raha, case file ki dhamki deke transfer maang raha. Real hai kya?",
                f"Didi, aurat {agency} officer bata ke boli camera off kiya to jail. Haath kaap rahe, 1930 dial karu?",
            ],
        }
        text = pick(h_da[lang], tidx)
        return surface, text, f"{agency}|1930"

    if scam == "upi_collect_request":
        h_upi = {
            "English": [
                f"Dad, {bank_short}-REFUND sent a UPI collect request for Rs.{amt}. It says refund credit today. Should receiving money need approval?",
                f"Bhai, GPay popup from {bank_short}-REFUND for Rs.{amt}, says enter PIN to receive cashback. PIN for receiving — that right?",
                f"Mom, PhonePe asking me to APPROVE Rs.{amt} from {bank_short}-REFUND, timer running. Pending refund se related, ya scam?",
            ],
            "Hindi": [
                f"भैया, {bank_short}-REFUND से Rs.{amt} का UPI collect आया है. Refund credit बोल रहा. Receive money में approve करना पड़ता है क्या?",
                f"भाई, GPay popup {bank_short}-REFUND से Rs.{amt} के लिए आया, cashback लेने के लिए PIN डालने को बोल रहा. लेने के लिए PIN सही है?",
                f"माँ, PhonePe Rs.{amt} APPROVE करने को बोल रहा {bank_short}-REFUND से, timer चल रहा. Refund है या scam?",
            ],
            "Marathi": [
                f"आई, {bank_short}-REFUND कडून Rs.{amt} चा UPI collect आला आहे. refund credit म्हणतोय. पैसे receive करायला approve लागतं का?",
                f"दादा, GPay popup {bank_short}-REFUND कडून Rs.{amt} साठी, cashback घ्यायला PIN टाकायला सांगतोय. घ्यायला PIN बरोबर आहे का?",
                f"आई, PhonePe Rs.{amt} APPROVE करायला सांगतोय {bank_short}-REFUND कडून, timer चालू. खरंच refund आहे का scam?",
            ],
            "Hinglish": [
                f"Bhai UPI app me {bank_short}-REFUND se Rs.{amt} collect req aaya. Refund credit bol raha. Receive money me approve lagta kya?",
                f"Bhai, GPay popup {bank_short}-REFUND se Rs.{amt} ke liye, cashback lene ke liye PIN dalo bol raha. Lene ke liye PIN sahi?",
                f"Mom, PhonePe Rs.{amt} APPROVE karne bol raha {bank_short}-REFUND se, timer chal raha. Refund se related ya scam?",
                f"Bhaiya, {bank_short}-REFUND wala bola lottery prize Rs.{amt} jeeti, UPI request approve aur PIN dalu. Genuine hoga ya nahi?",
            ],
        }
        text = pick(h_upi[lang], tidx)
        return surface, text, f"{bank}|{bank_short}|UPI"

    if scam == "fake_courier_parcel":
        h_fc = {
            "English": [
                f"Mom, {courier} caller says my parcel/address has issue and I must confirm now. Should I use official app or call 1930?",
                f"Dad, got {courier} SMS with a link saying customs duty pending Rs.{amt}, parcel will return. Pay or ignore?",
                f"Bhaiya, {courier} agent says my parcel has banned items, transferring me to cyber officer. Drop the call ya nahi?",
            ],
            "Hindi": [
                f"माँ, {courier} वाला कह रहा parcel/address issue है और अभी confirm करना है. Official app देखूं या 1930 call करूं?",
                f"पापा, {courier} का SMS आया link के साथ, customs duty Rs.{amt} pending बोल रहा, return हो जाएगा parcel. Pay करूं या ignore?",
                f"भैया, {courier} agent बोल रहा parcel में banned items हैं, cyber officer को transfer कर रहा. Call काटूं या नहीं?",
            ],
            "Marathi": [
                f"आई, {courier} वाला म्हणतो parcel/address issue आहे आणि लगेच confirm कर म्हणतोय. Official app पाहू का 1930 ला call करू?",
                f"बाबा, {courier} चा SMS आला link सोबत, customs duty Rs.{amt} pending म्हणतोय, parcel return होईल. Pay करू का ignore?",
                f"दादा, {courier} agent म्हणतोय parcel मध्ये banned items आहेत, cyber officer कडे transfer करतोय. Call कट करू की नाही?",
                f"ताई, {courier} hub manager म्हणून फोन आला, parcel सोडवण्यासाठी star-hash code dial करायला सांगतोय. खरंच असे करायचे का?",
            ],
            "Hinglish": [
                f"Mom, {courier} wala bol raha parcel/address issue hai aur abhi confirm karo. Official app check karu ya 1930 call?",
                f"Dad, {courier} ka SMS aaya link ke saath, customs duty Rs.{amt} pending bol raha, parcel return ho jayega. Pay karu ya ignore?",
                f"Bhaiya, {courier} agent bol raha parcel me banned items hain, cyber officer ko transfer kar raha. Call cut karu ya nahi?",
            ],
        }
        text = pick(h_fc[lang], tidx)
        return surface, text, f"{courier}|1930"

    h_kyc = {
        "English": [
            f"Dad, got {bank_short} KYC expiry SMS with a link and account block warning. Should I ignore and visit branch?",
            f"Mom, {bank_short} message says PAN-Aadhaar mismatch, A/c freeze in 2 hrs unless I tap link. Real warning or scam?",
            f"Bhaiya, {bank_short} sent APK file saying security update for KYC. Install karu ya ignore?",
            f"Sister, URGENT-{bank_short} SMS says reward points Rs.{amt} expire tonight, redeem after KYC at link. Press redeem ya skip?",
        ],
        "Hindi": [
            f"पापा, {bank_short} KYC expiry SMS आया है link के साथ, account block बोल रहा. Ignore करके branch जाऊं?",
            f"माँ, {bank_short} का message आया PAN-Aadhaar mismatch बोल रहा, 2 ghante में A/c freeze अगर link नहीं खोला. Real warning है क्या?",
            f"भैया, {bank_short} ने APK file भेजी KYC के लिए security update बोल रहा. Install करूं या ignore?",
        ],
        "Marathi": [
            f"बाबा, {bank_short} KYC expiry SMS आला आहे link सोबत, account block म्हणतोय. Ignore करून branch ला जाऊ का?",
            f"आई, {bank_short} चा message आला PAN-Aadhaar mismatch म्हणतोय, 2 तासात A/c freeze होईल link उघडला नाही तर. खरंच warning आहे का?",
            f"दादा, {bank_short} ने APK file पाठवली KYC साठी security update म्हणून. Install करू का ignore?",
        ],
        "Hinglish": [
            f"Dad, {bank_short} KYC expiry SMS link ke saath aaya, account block bol raha. Ignore karke branch jau?",
            f"Mom, {bank_short} ka message PAN-Aadhaar mismatch bol raha, 2 ghante me A/c freeze agar link nahi khola. Real warning hai kya?",
            f"Bhaiya, {bank_short} ne APK file bheji KYC ke liye security update bol raha. Install karu ya ignore?",
        ],
    }
    text = pick(h_kyc[lang], tidx)
    return surface, text, f"{bank}|{bank_short}"


def main() -> None:
    patterns = {row["pattern_id"]: row for row in read_csv(PATTERNS)}
    anchors = {row["anchor_id"]: row for row in read_csv(ANCHORS)}
    with DATASET.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = [row for row in reader if row["row_id"].startswith("CYB-PILOT-")]

    existing = defaultdict(int)
    for row in rows:
        if row["variant_type"] == "genuine":
            existing[(row["scam_type"], row["language"])] += 1

    specs: list[tuple[str, str]] = []
    for scam in SCAMS:
        for lang in LANGS:
            for _ in range(TARGET_TRIPLETS[scam][lang] - existing[(scam, lang)]):
                specs.append((scam, lang))
    if len(specs) != 36:
        raise RuntimeError(f"Expected 36 new triplets, got {len(specs)}")

    cell_counter = Counter((row["scam_type"], row["language"]) for row in rows if row["variant_type"] == "genuine")
    help_surfaces = ["WhatsApp"] * 24 + ["phone_call_summary"] * 8 + ["SMS"] * 4
    scam_surfaces = {
        "digital_arrest": ["video_call_summary"] * 9,
        "fake_courier_parcel": ["phone_call_summary"] * 5 + ["SMS"] * 4,
        "fake_kyc": ["SMS"] * 7 + ["WhatsApp"] * 2,
        "upi_collect_request": ["app_notification"] * 5 + ["SMS"] * 4,
    }
    scam_surface_idx: Counter[str] = Counter()
    help_idx = 0
    row_num = 13
    new_rows: list[dict[str, str]] = []

    for idx, (scam, lang) in enumerate(specs, start=1):
        cell_counter[(scam, lang)] += 1
        suffix = cell_counter[(scam, lang)]
        phase = "XLANG" if idx > 28 else "SCALE"
        triplet_id = f"TRIP-{phase}-{SCAM_CODE[scam]}-{LANG_CODE[lang]}-{suffix:03d}"
        pool = POOLS[scam]
        pattern_id = pick(pool["patterns"], idx + suffix)
        pattern = patterns[pattern_id]
        anchor_id = pick(pool["anchors"], idx + suffix)
        source_type = "synthetic_from_verified_pattern"
        status = VALIDATION[lang]

        g_surface, g_text = genuine_message(scam, lang, idx + suffix, tidx=suffix - 1)
        anchor = anchors.get(anchor_id, {})
        new_rows.append({
            "row_id": f"CYB-SCALE-{row_num:03d}",
            "triplet_id": triplet_id,
            "variant_type": "genuine",
            "scam_type": scam,
            "language": lang,
            "script": SCRIPT[lang],
            "surface_format": g_surface,
            "message_text": g_text,
            "text_en_gloss": f"Genuine {scam.replace('_', ' ')} notice in {lang}.",
            "genuine_anchor_id": anchor_id,
            "pattern_id": pool["genuine_pattern"],
            "source_type": source_type,
            "source_url": anchor.get("source_url", "user_supplied_private_sms") or "user_supplied_private_sms",
            "source_date": "2026-04-28",
            "pressure_tactic": "none",
            "ask": "safe_or_routine_action",
            "red_flags": "none",
            "mentioned_institutions": anchor.get("institution", institution_for(scam, idx)),
            "contains_link": "false",
            "link_pattern": "none",
            "validation_status": status,
        })
        row_num += 1

        s_queue = scam_surfaces[scam]
        s_surface = s_queue[scam_surface_idx[scam] % len(s_queue)]
        scam_surface_idx[scam] += 1
        s_surface, s_text, has_link, link_pattern, institutions, red_flags, ask = scam_message(
            scam, lang, pattern_id, idx + suffix, s_surface, tidx=suffix - 1
        )
        new_rows.append({
            "row_id": f"CYB-SCALE-{row_num:03d}",
            "triplet_id": triplet_id,
            "variant_type": "scam",
            "scam_type": scam,
            "language": lang,
            "script": SCRIPT[lang],
            "surface_format": s_surface,
            "message_text": s_text,
            "text_en_gloss": f"Scam variant for {pattern['pattern_name']}.",
            "genuine_anchor_id": anchor_id,
            "pattern_id": pattern_id,
            "source_type": source_type,
            "source_url": pattern["source_url"],
            "source_date": pattern["source_date"],
            "pressure_tactic": pattern["pressure_tactic"],
            "ask": ask,
            "red_flags": red_flags,
            "mentioned_institutions": institutions,
            "contains_link": "true" if has_link else "false",
            "link_pattern": link_pattern,
            "validation_status": status,
        })
        row_num += 1

        h_surface = help_surfaces[help_idx % len(help_surfaces)]
        help_idx += 1
        h_surface, h_text, h_inst = help_message(scam, lang, idx + suffix, h_surface, tidx=suffix - 1)
        new_rows.append({
            "row_id": f"CYB-SCALE-{row_num:03d}",
            "triplet_id": triplet_id,
            "variant_type": "help_seeking",
            "scam_type": scam,
            "language": lang,
            "script": SCRIPT[lang],
            "surface_format": h_surface,
            "message_text": h_text,
            "text_en_gloss": f"Help-seeking message about suspected {scam.replace('_', ' ')} fraud.",
            "genuine_anchor_id": anchor_id,
            "pattern_id": pattern_id,
            "source_type": source_type,
            "source_url": pattern["source_url"],
            "source_date": pattern["source_date"],
            "pressure_tactic": "anxiety_after_contact",
            "ask": "ask_trusted_contact",
            "red_flags": "anxious|asks_before_acting",
            "mentioned_institutions": h_inst,
            "contains_link": "false",
            "link_pattern": "none",
            "validation_status": status,
        })
        row_num += 1

    all_rows = rows + new_rows
    if len(all_rows) != 120:
        raise RuntimeError(f"Expected 120 rows, got {len(all_rows)}")

    cell_counts = Counter((row["scam_type"], row["language"], row["variant_type"]) for row in all_rows)
    checks = [
        all(Counter(row["language"] for row in all_rows)[lang] == 30 for lang in LANGS),
        all(Counter(row["scam_type"] for row in all_rows)[scam] == 30 for scam in SCAMS),
        all(Counter(row["variant_type"] for row in all_rows)[variant] == 40 for variant in ["genuine", "scam", "help_seeking"]),
        min(cell_counts.values()) >= 2,
        not any("??" in row["message_text"] for row in all_rows if row["language"] in {"Hindi", "Marathi"}),
    ]
    if not all(checks):
        raise RuntimeError("Generated dataset failed balance or encoding sanity checks")

    with DATASET.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)

    random.seed(4282026)
    spot_ids = random.sample([row["row_id"] for row in all_rows], 15)
    write_audit(all_rows, new_rows, cell_counts, spot_ids)
    write_spot_check(all_rows, spot_ids)
    print(f"wrote {len(all_rows)} rows; new rows {len(new_rows)}")
    print("spot_check_ids=" + ",".join(spot_ids))


def write_audit(all_rows: list[dict[str, str]], new_rows: list[dict[str, str]], cell_counts: Counter, spot_ids: list[str]) -> None:
    lines: list[str] = []
    lines.append("# Scaling Audit\n\n")
    lines.append("Generated: 2026-04-28\n\n")
    lines.append("## Summary\n\n")
    lines.append(f"- Total rows: {len(all_rows)}\n")
    lines.append(f"- Pilot rows preserved: {sum(1 for row in all_rows if row['row_id'].startswith('CYB-PILOT-'))}\n")
    lines.append(f"- New generated rows: {len(new_rows)}\n")
    lines.append("- New triplets: 36 (28 base generation + 8 cross-language variants)\n")
    lines.append("- No Adaption job has been run.\n\n")
    for title, key in [
        ("Language", "language"),
        ("Scam Type", "scam_type"),
        ("Variant Type", "variant_type"),
        ("Surface Format", "surface_format"),
        ("Validation Status", "validation_status"),
    ]:
        lines.append(f"### {title}\n\n")
        lines.append("| value | count |\n|---|---:|\n")
        for value, count in sorted(Counter(row[key] for row in all_rows).items()):
            lines.append(f"| {value} | {count} |\n")
        lines.append("\n")

    lines.append("## 4 x 4 x 3 Cell Counts\n\n")
    lines.append("| scam_type | language | genuine | scam | help_seeking | flag |\n|---|---|---:|---:|---:|---|\n")
    for scam in SCAMS:
        for lang in LANGS:
            g = cell_counts[(scam, lang, "genuine")]
            s = cell_counts[(scam, lang, "scam")]
            h = cell_counts[(scam, lang, "help_seeking")]
            flag = "ok" if min(g, s, h) >= 2 else "needs_more"
            lines.append(f"| {scam} | {lang} | {g} | {s} | {h} | {flag} |\n")

    lines.append("\n## Random Spot-Check Row IDs\n\n")
    lines.append("Use these 15 row IDs for human register review:\n\n")
    for row_id in spot_ids:
        lines.append(f"- `{row_id}`\n")
    lines.append("\n## Notes\n\n")
    lines.append("- English and Hinglish generated rows are marked `machine_generated`.\n")
    lines.append("- Hindi and Marathi generated rows are marked `needs_human_review`.\n")
    lines.append("- Reviewed pilot corrections remain marked `corrected_after_review`.\n")
    lines.append("- Scam links, where present, use inert `[.]` notation.\n")
    (ROOT / "scaling_audit.md").write_text("".join(lines), encoding="utf-8")


def write_spot_check(all_rows: list[dict[str, str]], spot_ids: list[str]) -> None:
    by_id = {row["row_id"]: row for row in all_rows}
    lines = ["# Spot Check Sample\n\n", "Generated: 2026-04-28\n\n"]
    lines.append("These are the 15 random rows selected in `scaling_audit.md`.\n\n")
    lines.append("| row_id | scam_type | language | variant_type | validation_status | message_text |\n")
    lines.append("|---|---|---|---|---|---|\n")
    for row_id in spot_ids:
        row = by_id[row_id]
        text = row["message_text"].replace("|", "\\|")
        lines.append(
            f"| {row_id} | {row['scam_type']} | {row['language']} | {row['variant_type']} | {row['validation_status']} | {text} |\n"
        )
    (ROOT / "spot_check_sample.md").write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
