"""Adversarial Scam Pair Generator.

Takes genuine advisory rows and generates corresponding heat_scam variants.
"""
import copy
import random
import uuid

from bharat_cric.schema import BharatCRICRow

SCAM_CATEGORIES = [
    "fake_relief_scheme",
    "fake_hospital",
    "fake_subsidy",
    "fake_water_tanker",
    "fake_ngo",
    "fake_employer_allowance"
]

SCAM_PATTERNS = {
    "eng": {
        "fake_relief_scheme": " Govt PM Garmi Rahat Yojana is giving Rs 5000. Click http://pm-yojana-update.in to claim now.",
        "fake_hospital": " 108 Ambulance service. Pay Rs 500 advance via UPI to dispatch ambulance immediately.",
        "fake_subsidy": " Your electricity will be disconnected at 9:30 PM. Click to pay bill update and get AC subsidy: http://power-update.apk",
    },
    "hin": {
        "fake_relief_scheme": " सरकार पीएम गर्मी राहत योजना के तहत ₹5000 दे रही है। अभी क्लेम करने के लिए http://pm-yojana-update.in पर क्लिक करें।",
        "fake_hospital": " 108 एम्बुलेंस सेवा। एम्बुलेंस तुरंत भेजने के लिए UPI के माध्यम से ₹500 एडवांस भुगतान करें।",
        "fake_subsidy": " आपका बिजली कनेक्शन रात 9:30 बजे कट जाएगा। बिल अपडेट करने और एसी सब्सिडी पाने के लिए क्लिक करें: http://power-update.apk",
    },
    "bho": {
        "fake_relief_scheme": " सरकार पीएम गर्मी राहत योजना के तहत ₹5000 दे रहल बा। अभी क्लेम करे खातिर http://pm-yojana-update.in पर क्लिक करीं।",
        "fake_hospital": " 108 एम्बुलेंस सेवा। एम्बुलेंस तुरंत भेजे खातिर UPI के माध्यम से ₹500 एडवांस दीं।",
        "fake_subsidy": " राउर बिजली कनेक्शन रात 9:30 बजे कट जाई। बिल अपडेट करे आ एसी सब्सिडी पावे खातिर क्लिक करीं: http://power-update.apk",
    }
}

def generate_scam_variant(genuine_row: BharatCRICRow) -> BharatCRICRow:
    """Creates a scam variant from a genuine row."""
    if genuine_row.language not in SCAM_PATTERNS:
        # Fallback to English patterns for testing
        lang = "eng"
    else:
        lang = genuine_row.language
        
    cat = random.choice(["fake_relief_scheme", "fake_hospital", "fake_subsidy"])
    pattern = SCAM_PATTERNS[lang][cat]
    
    scam_row = copy.deepcopy(genuine_row)
    scam_row.row_id = str(uuid.uuid4())
    scam_row.disaster_type = "disaster_scam_heat"
    scam_row.intent_label = "scam_alert"
    scam_row.variant_type = "heat_scam"
    scam_row.scam_category = cat
    scam_row.pressure_tactic = ["urgency", "fear"] if cat != "fake_relief_scheme" else ["urgency", "authority_impersonation"]
    scam_row.correct_user_action = "Report to 1930 and do not click links or pay."
    
    # Generate completion
    # We mix the original context with a scam injection to keep lengths similar
    scam_row.completion = genuine_row.completion.split(".")[0] + pattern
    
    if scam_row.surface_format == "sms" and len(scam_row.completion) > 160:
        # Truncate genuine part to make room
        allowable_len = 160 - len(pattern) - 3
        short_base = genuine_row.completion[:max(10, allowable_len)] + "..."
        scam_row.completion = short_base + pattern
        
    if not scam_row.metadata_json:
        scam_row.metadata_json = {}
    
    scam_row.metadata_json["red_flags"] = ["Suspicious URL", "Urgent request for money or details"]
    scam_row.metadata_json["intentional_scam_feature"] = True
    scam_row.validation_status = "source_authentic"
    scam_row.generation_method = "llm_adapted"
    scam_row.instruction = f"Identify if this message is a scam: {genuine_row.instruction}"
    
    return scam_row
