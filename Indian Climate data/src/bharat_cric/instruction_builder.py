"""Convert source extracts into instruction-format BharatCRICRow objects.

Five templates per the Day 1 spec:
  1. Bulletin -> SMS
  2. Bulletin -> WhatsApp
  3. Do's list -> Q&A
  4. Symptom -> first aid
  5. Vulnerable population
Plus a small set of official_bulletin / radio_script / community_post rows so
the seed covers all 5 surface formats by EOD.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import List

from .helpline_registry import find_valid_helplines
from .schema import BharatCRICRow, SMS_MAX_CHARS
from .sources import SourceExtract


logger = logging.getLogger(__name__)


def _pair_id() -> str:
    return str(uuid.uuid4())


def _shorten_for_sms(text: str, helpline: str = "") -> str:
    """Cut text to fit within SMS_MAX_CHARS while preserving any helpline."""
    if helpline and helpline not in text:
        suffix = f" Call {helpline}."
    else:
        suffix = ""
    budget = SMS_MAX_CHARS - len(suffix)
    if len(text) <= budget:
        return (text + suffix).strip()
    # cut at last sentence/clause boundary <= budget
    truncated = text[:budget]
    cut = max(truncated.rfind(". "), truncated.rfind("; "), truncated.rfind(", "))
    if cut > 80:
        truncated = truncated[: cut + 1]
    return (truncated.rstrip() + suffix).strip()[:SMS_MAX_CHARS]


def _whatsapp_rewrite(item: str) -> str:
    """Conversational, friend-forward tone, always includes a helpline."""
    base = item.rstrip(".")
    helpline_in_text = find_valid_helplines(item)
    if helpline_in_text:
        helpline_clause = f"If anything goes wrong, call {helpline_in_text[0]}."
    else:
        helpline_clause = "For medical emergencies dial 108."
    return (
        f"Bhai/behen, ek heatwave safety reminder: {base}. "
        f"Stay safe and check on your parents/grandparents today. "
        f"{helpline_clause} "
        f"Forward to anyone working outdoors."
    )


def _is_dont(item: str) -> bool:
    return item.strip().lower().startswith(("do not", "don't", "never", "avoid"))


def _detect_helpline(item: str) -> str:
    nums = find_valid_helplines(item)
    return nums[0] if nums else ""


def _ensure_helpline_grounding(item: str, default: str) -> str:
    if find_valid_helplines(item):
        return item
    return f"{item.rstrip('.')}. If symptoms worsen, call {default} immediately."


# ----------------------------- templates -----------------------------------


def _bulletin_to_sms_row(item: str, src: SourceExtract,
                          disaster_type: str,
                          intent_label: str) -> BharatCRICRow:
    helpline = _detect_helpline(item)
    completion = _shorten_for_sms(item, helpline=helpline)
    instruction = (
        "Convert this official heatwave advisory into an SMS alert under "
        "160 characters preserving any emergency number and the core action: "
        f"\"{item}\""
    )
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type=disaster_type,  # type: ignore[arg-type]
        language="eng",
        script="Latn",
        surface_format="sms",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label=intent_label,  # type: ignore[arg-type]
        helplines_mentioned=helplines,
        metadata_json={
            "template": "bulletin_to_sms",
            "source_section": src.section,
            **src.metadata,
        },
    )


def _bulletin_to_whatsapp_row(item: str, src: SourceExtract,
                               disaster_type: str,
                               intent_label: str) -> BharatCRICRow:
    completion = _whatsapp_rewrite(item)
    instruction = (
        "Rewrite this advisory as a WhatsApp message a friend would forward — "
        "conversational tone, keep all safety facts and helpline numbers: "
        f"\"{item}\""
    )
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type=disaster_type,  # type: ignore[arg-type]
        language="eng",
        script="Latn",
        surface_format="whatsapp",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label=intent_label,  # type: ignore[arg-type]
        helplines_mentioned=helplines,
        metadata_json={
            "template": "bulletin_to_whatsapp",
            "source_section": src.section,
            **src.metadata,
        },
    )


def _dos_to_qa_row(item: str, src: SourceExtract) -> BharatCRICRow:
    instruction = (
        "What should an outdoor worker do during a heatwave between 12 PM and 4 PM "
        "to stay safe, based on official IMD/NDMA guidance?"
    )
    completion = (
        f"Per IMD/NDMA heatwave guidance: {item} Take frequent rest breaks in shade, "
        f"keep ORS and water within reach, and inform your supervisor if you feel "
        f"dizzy or nauseated. In an emergency call 108 or 112."
    )
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type="worker_safety",
        language="eng",
        script="Latn",
        surface_format="community_post",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="worker_safety_protocol",
        helplines_mentioned=helplines,
        metadata_json={"template": "dos_to_qa", "source_section": src.section,
                        **src.metadata},
    )


def _symptom_to_first_aid_row(item: str, src: SourceExtract) -> BharatCRICRow:
    instruction = (
        "Someone shows signs of heatstroke — fainting, hot dry skin, confusion. "
        "What is the immediate first aid before the ambulance arrives?"
    )
    completion = _ensure_helpline_grounding(item, default="108")
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type="heatstroke_health",
        language="eng",
        script="Latn",
        surface_format="community_post",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="first_aid_instruction",
        helplines_mentioned=helplines,
        metadata_json={"template": "symptom_to_first_aid",
                        "source_section": src.section, **src.metadata},
    )


def _vulnerable_row(item: str, src: SourceExtract) -> BharatCRICRow:
    if "infant" in item.lower() or "child" in item.lower():
        cohort = "infants"
    elif "pregnant" in item.lower():
        cohort = "pregnant women"
    elif "elder" in item.lower() or "kidney" in item.lower() or "diabetes" in item.lower():
        cohort = "elderly with chronic disease"
    else:
        cohort = "vulnerable populations"
    instruction = (
        f"Explain heatwave risks specific to {cohort} and what caregivers should do, "
        f"based on official IMD/NDMA guidance."
    )
    completion = _ensure_helpline_grounding(item, default="104")
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type="vulnerable_population",
        language="eng",
        script="Latn",
        surface_format="community_post",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="vulnerable_population_guidance",
        helplines_mentioned=helplines,
        metadata_json={"template": "vulnerable", "source_section": src.section,
                        **src.metadata},
    )


# Surface-format extras: ensure radio_script and official_bulletin coverage.
def _radio_script_row(item: str, src: SourceExtract) -> BharatCRICRow:
    instruction = (
        "Rewrite this heatwave guidance as a 30-second All-India-Radio public "
        "service announcement, formal narrator tone, mention the helpline at the end."
    )
    completion = (
        "[Narrator, calm tone] Listeners, the India Meteorological Department has "
        f"issued the following advisory. {item} If you or anyone in your family "
        "shows signs of heatstroke, call 108 immediately. This message is brought "
        "to you by All India Radio in coordination with the National Disaster "
        "Management Authority."
    )
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type="heatwave",
        language="eng",
        script="Latn",
        surface_format="radio_script",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="warn_imminent_risk",
        helplines_mentioned=helplines,
        metadata_json={"template": "radio_script", "source_section": src.section,
                        **src.metadata},
    )


def _official_bulletin_row(items: List[str], src: SourceExtract) -> BharatCRICRow:
    instruction = (
        "Draft a one-page official heatwave bulletin in the format used by the "
        "India Meteorological Department, including a header, advisory body and "
        "helpline footer."
    )
    body = " ".join(items[:4])
    completion = (
        "INDIA METEOROLOGICAL DEPARTMENT — DAILY HEATWAVE BULLETIN\n"
        "Issued: today, 1730 IST.\n\n"
        f"Advisory: {body}\n\n"
        "Vulnerable groups (infants, elderly, outdoor workers, pregnant women) "
        "should take additional precautions.\n\n"
        "For medical emergencies dial 108. For disaster control room dial 1077. "
        "For unified emergency response dial 112."
    )
    helplines = find_valid_helplines(completion)
    return BharatCRICRow(
        disaster_type="heatwave",
        language="eng",
        script="Latn",
        surface_format="official_bulletin",
        instruction=instruction,
        completion=completion,
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="warn_imminent_risk",
        helplines_mentioned=helplines,
        metadata_json={"template": "official_bulletin", "source_section": src.section,
                        **src.metadata},
    )


def _scam_alert_row(scam_msg: str, genuine_msg: str, src: SourceExtract) -> List[BharatCRICRow]:
    """Build a paired (genuine, scam) advisory pair for the disaster_scam_heat type."""
    pid = _pair_id()
    genuine = BharatCRICRow(
        pair_id=pid,
        disaster_type="heatwave",
        language="eng",
        script="Latn",
        surface_format="sms",
        instruction=(
            "Draft a genuine government heatwave alert SMS that a citizen would "
            "receive from their district administration."
        ),
        completion=_shorten_for_sms(genuine_msg, helpline="1077"),
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="warn_imminent_risk",
        helplines_mentioned=find_valid_helplines(genuine_msg),
        metadata_json={"template": "scam_pair_genuine",
                        "source_section": src.section, **src.metadata},
    )
    scam = BharatCRICRow(
        pair_id=pid,
        disaster_type="disaster_scam_heat",
        language="eng",
        script="Latn",
        surface_format="community_post",
        instruction=(
            "Identify the red flags in this disaster-scam SMS that imitates a "
            "government heatwave-relief message, and explain why a citizen "
            "should not respond."
        ),
        completion=(
            f"This SMS is a scam. Red flags: it asks for personal/bank details, "
            f"it claims a non-existent 'PM Heat Relief Yojana', and it does not "
            f"come from a verified government short-code. The text reads: "
            f"\"{scam_msg}\" — do not click any link. Verify with 1077 (district "
            f"control room) and report on 1930 (cyber-crime helpline)."
        ),
        source_reference=src.url,
        validation_status="source_authentic",
        intent_label="scam_alert",
        helplines_mentioned=["1077", "1930"],
        metadata_json={
            "template": "scam_pair_scam",
            "source_section": src.section,
            "red_flags": ["asks_bank_details", "fake_scheme_name", "unknown_sender"],
            "pressure_tactic": "urgency_and_money",
            "recommended_action": "verify_with_1077_then_report_1930",
            **src.metadata,
        },
    )
    return [genuine, scam]


# --------------------- top-level dispatcher --------------------------------


def source_extract_to_instruction_rows(extract: SourceExtract) -> List[BharatCRICRow]:
    """Fan a single source extract into one or more instruction rows."""
    rows: List[BharatCRICRow] = []
    section = extract.section

    if section in {"do_list", "live_guidance_items", "beat_the_heat",
                    "ors_recipe", "live_ndma_items", "pib_curated",
                    "sdma_bihar", "sdma_up", "sdma_odisha", "sdma_jharkhand",
                    "pib_search_titles"}:
        for item in extract.items:
            if not _is_dont(item):
                rows.append(_bulletin_to_sms_row(
                    item, extract,
                    disaster_type="heatwave",
                    intent_label="preparedness_advice",
                ))
                rows.append(_bulletin_to_whatsapp_row(
                    item, extract,
                    disaster_type="heatwave",
                    intent_label="preparedness_advice",
                ))
            else:
                rows.append(_bulletin_to_sms_row(
                    item, extract,
                    disaster_type="heatwave",
                    intent_label="myth_correction",
                ))

        # one Q&A worker-safety row per do-list extract
        if extract.items:
            rows.append(_dos_to_qa_row(extract.items[0], extract))

    elif section == "dont_list":
        for item in extract.items:
            rows.append(_bulletin_to_sms_row(
                item, extract,
                disaster_type="heatwave",
                intent_label="myth_correction",
            ))

    elif section == "first_aid":
        for item in extract.items:
            rows.append(_symptom_to_first_aid_row(item, extract))
            rows.append(_bulletin_to_whatsapp_row(
                item, extract,
                disaster_type="heatstroke_health",
                intent_label="first_aid_instruction",
            ))

    elif section == "vulnerable":
        for item in extract.items:
            rows.append(_vulnerable_row(item, extract))

    elif section == "worker_safety":
        for item in extract.items:
            rows.append(_dos_to_qa_row(item, extract))
            rows.append(_bulletin_to_sms_row(
                item, extract,
                disaster_type="worker_safety",
                intent_label="worker_safety_protocol",
            ))

    elif section == "fraud_awareness":
        for item in extract.items:
            rows.append(_bulletin_to_sms_row(
                item, extract,
                disaster_type="heatwave",
                intent_label="scam_alert",
            ))
        # paired scam alerts
        scam_pairs = [
            (
                "URGENT: PM Heat Relief Yojana 2026. Send Aadhar+bank to 9876xxxxx within 24h to claim Rs 5000.",
                "District Administration: heatwave red alert today. Avoid outdoor work 12-3 PM. Helpline 1077.",
            ),
            (
                "Govt Heatwave Compensation: click bit.ly/relief-2026 to receive Rs 8000 in your account.",
                "DM Office advisory: stay indoors 12 PM - 4 PM. Drink ORS. Emergency 108.",
            ),
            (
                "Last day to register for free AC under PM Cool Bharat. Reply with PAN to 5xxxx now.",
                "IMD heatwave bulletin: severe heat expected next 48 hours. Follow do's and don'ts.",
            ),
        ]
        for scam_msg, genuine_msg in scam_pairs:
            rows.extend(_scam_alert_row(scam_msg, genuine_msg, extract))

    # Add radio_script + official_bulletin row anchored on this extract if it
    # has rich content. Keeps surface-format coverage broad without inflating
    # row count.
    if section in {"beat_the_heat", "do_list"}:
        if extract.items:
            rows.append(_radio_script_row(extract.items[0], extract))
            rows.append(_official_bulletin_row(extract.items, extract))

    return rows
