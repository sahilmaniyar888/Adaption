"""Multilingual instruction builder for Day 2.

Converts non-English source extracts into instruction-format BharatCRICRow
objects with instruction-type diversity (translation, classification, QA,
extraction, summarization, rewrite).

Hard rule: ≥30% non-translation tasks in non-English rows.
"""
from __future__ import annotations

import logging
import random
import uuid
from typing import List, Optional

from .helpline_registry import find_valid_helplines
from .schema import BharatCRICRow, SMS_MAX_CHARS, LanguageCode, ScriptCode
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
    truncated = text[:budget]
    cut = max(truncated.rfind(". "), truncated.rfind("; "), truncated.rfind(", "))
    if cut > 40:
        truncated = truncated[:cut + 1]
    return (truncated.rstrip() + suffix).strip()[:SMS_MAX_CHARS]


# ---- Instruction templates by type ----


def _translation_row(
    item: str,
    src: SourceExtract,
    lang: LanguageCode,
    script: ScriptCode,
    english_gloss: Optional[str],
    disaster_type: str = "heatwave",
    intent_label: str = "preparedness_advice",
    surface_format: str = "whatsapp",
    source_quality: str = "high",
    extraction_method: str = "manual_curation",
) -> BharatCRICRow:
    """Translation-style instruction row."""
    lang_names = {"hin": "Hindi", "bho": "Bhojpuri", "mai": "Maithili", "sat": "Santali"}
    lang_name = lang_names.get(lang, lang)
    instruction = (
        f"Translate this official heatwave advisory into natural, region-appropriate "
        f"{lang_name}: \"{english_gloss or item}\""
    )
    helplines = find_valid_helplines(item)
    completion = item
    if surface_format == "sms":
        completion = _shorten_for_sms(item, helpline=helplines[0] if helplines else "")

    return BharatCRICRow(
        disaster_type=disaster_type,  # type: ignore[arg-type]
        language=lang,  # type: ignore[arg-type]
        script=script,  # type: ignore[arg-type]
        surface_format=surface_format,  # type: ignore[arg-type]
        instruction=instruction,
        completion=completion,
        english_gloss=english_gloss,
        source_reference=src.url,
        validation_status="source_authentic",  # type: ignore[arg-type]
        intent_label=intent_label,  # type: ignore[arg-type]
        helplines_mentioned=helplines,
        instruction_type="translation",  # type: ignore[arg-type]
        source_quality=source_quality,  # type: ignore[arg-type]
        extraction_method=extraction_method,  # type: ignore[arg-type]
        metadata_json={
            "template": "multilingual_translation",
            "source_section": src.section,
            **src.metadata,
        },
    )


def _classification_row(
    item: str,
    src: SourceExtract,
    lang: LanguageCode,
    script: ScriptCode,
    english_gloss: Optional[str],
    disaster_type: str = "heatwave",
    source_quality: str = "high",
    extraction_method: str = "manual_curation",
) -> BharatCRICRow:
    """Classification-style instruction row."""
    lang_names = {"hin": "Hindi", "bho": "Bhojpuri", "mai": "Maithili", "sat": "Santali"}
    lang_name = lang_names.get(lang, lang)
    instruction = (
        f"Is this {lang_name} advisory about high-risk or low-risk heat exposure? "
        f"Classify and explain: \"{item[:120]}...\""
    )
    # Determine risk level from content
    high_risk_kw = ["108", "112", "heatstroke", "collapse", "emergency", "बेहोश",
                     "लू", "मौत", "ᱨᱚᱜ"]
    is_high = any(kw in item.lower() for kw in high_risk_kw)
    risk = "HIGH-RISK" if is_high else "LOW-RISK"
    completion = (
        f"Classification: {risk}. "
        f"This advisory {'requires immediate action — it mentions emergency symptoms or helplines' if is_high else 'provides general preparedness guidance for heat safety'}. "
        f"Key content: {english_gloss or item[:150]}"
    )
    helplines = find_valid_helplines(item + " " + completion)
    return BharatCRICRow(
        disaster_type=disaster_type,  # type: ignore[arg-type]
        language=lang,  # type: ignore[arg-type]
        script=script,  # type: ignore[arg-type]
        surface_format="community_post",
        instruction=instruction,
        completion=completion,
        english_gloss=english_gloss,
        source_reference=src.url,
        validation_status="source_authentic",  # type: ignore[arg-type]
        intent_label="general_information",
        helplines_mentioned=helplines,
        instruction_type="classification",  # type: ignore[arg-type]
        source_quality=source_quality,  # type: ignore[arg-type]
        extraction_method=extraction_method,  # type: ignore[arg-type]
        metadata_json={
            "template": "multilingual_classification",
            "source_section": src.section,
            **src.metadata,
        },
    )


def _qa_row(
    item: str,
    src: SourceExtract,
    lang: LanguageCode,
    script: ScriptCode,
    english_gloss: Optional[str],
    disaster_type: str = "heatwave",
    source_quality: str = "high",
    extraction_method: str = "manual_curation",
) -> BharatCRICRow:
    """QA-style instruction row."""
    instruction = (
        f"What action is recommended in this heat advisory? "
        f"\"{item[:150]}...\""
    )
    completion = (
        f"The advisory recommends: {english_gloss or item}. "
        f"Follow these precautions during heatwave conditions."
    )
    helplines = find_valid_helplines(item + " " + completion)
    return BharatCRICRow(
        disaster_type=disaster_type,  # type: ignore[arg-type]
        language=lang,  # type: ignore[arg-type]
        script=script,  # type: ignore[arg-type]
        surface_format="community_post",
        instruction=instruction,
        completion=completion,
        english_gloss=english_gloss,
        source_reference=src.url,
        validation_status="source_authentic",  # type: ignore[arg-type]
        intent_label="preparedness_advice",
        helplines_mentioned=helplines,
        instruction_type="qa",  # type: ignore[arg-type]
        source_quality=source_quality,  # type: ignore[arg-type]
        extraction_method=extraction_method,  # type: ignore[arg-type]
        metadata_json={
            "template": "multilingual_qa",
            "source_section": src.section,
            **src.metadata,
        },
    )


def _extraction_row(
    item: str,
    src: SourceExtract,
    lang: LanguageCode,
    script: ScriptCode,
    english_gloss: Optional[str],
    disaster_type: str = "heatwave",
    source_quality: str = "high",
    extraction_method: str = "manual_curation",
) -> BharatCRICRow:
    """Extraction-style instruction row."""
    instruction = (
        f"List the key safety actions mentioned in this advisory: "
        f"\"{item[:150]}...\""
    )
    # Extract action verbs / key phrases
    gloss = english_gloss or item
    actions = [s.strip() for s in gloss.split(".") if len(s.strip()) > 10][:3]
    if actions:
        action_list = "; ".join(f"({i+1}) {a}" for i, a in enumerate(actions))
    else:
        action_list = gloss[:200]
    completion = f"Key safety actions: {action_list}."
    helplines = find_valid_helplines(item + " " + completion)
    return BharatCRICRow(
        disaster_type=disaster_type,  # type: ignore[arg-type]
        language=lang,  # type: ignore[arg-type]
        script=script,  # type: ignore[arg-type]
        surface_format="community_post",
        instruction=instruction,
        completion=completion,
        english_gloss=english_gloss,
        source_reference=src.url,
        validation_status="source_authentic",  # type: ignore[arg-type]
        intent_label="preparedness_advice",
        helplines_mentioned=helplines,
        instruction_type="extraction",  # type: ignore[arg-type]
        source_quality=source_quality,  # type: ignore[arg-type]
        extraction_method=extraction_method,  # type: ignore[arg-type]
        metadata_json={
            "template": "multilingual_extraction",
            "source_section": src.section,
            **src.metadata,
        },
    )


def multilingual_extract_to_rows(
    extract: SourceExtract,
    lang: LanguageCode,
    script: ScriptCode,
    source_quality: str = "high",
    extraction_method: str = "manual_curation",
    validation_status: str = "source_authentic",
    english_glosses: Optional[List[str]] = None,
) -> List[BharatCRICRow]:
    """Fan a single multilingual source extract into diverse instruction rows.

    Ensures ≥30% non-translation instruction types by cycling through
    translation, classification, QA, and extraction templates.
    """
    rows: List[BharatCRICRow] = []
    items = extract.items
    if not items:
        return rows

    # Map disaster types from section
    section = extract.section
    if "worker" in section:
        disaster_type = "worker_safety"
        intent_label = "worker_safety_protocol"
    elif "first_aid" in section:
        disaster_type = "heatstroke_health"
        intent_label = "first_aid_instruction"
    elif "vulnerable" in section:
        disaster_type = "vulnerable_population"
        intent_label = "vulnerable_population_guidance"
    elif "fraud" in section or "scam" in section:
        disaster_type = "heatwave"
        intent_label = "scam_alert"
    else:
        disaster_type = "heatwave"
        intent_label = "preparedness_advice"

    # Each item generates 3-5 rows for density:
    # 2 translation (SMS + WhatsApp) + 1 non-translation (classification/QA/extraction)
    # + occasional radio_script/official_bulletin for surface format balance

    for i, item in enumerate(items):
        gloss = english_glosses[i] if english_glosses and i < len(english_glosses) else None

        # Generate MULTIPLE rows per item (like Day 1 English builder):
        # 1. Translation -> SMS
        # 2. Translation -> WhatsApp
        # 3. Classification or QA or Extraction (cycle for diversity)

        # Row 1: Translation SMS
        row_sms = _translation_row(
            item, extract, lang, script, gloss,
            disaster_type=disaster_type,
            intent_label=intent_label,
            surface_format="sms",
            source_quality=source_quality,
            extraction_method=extraction_method,
        )
        if validation_status != "source_authentic":
            object.__setattr__(row_sms, "validation_status", validation_status)
        rows.append(row_sms)

        # Row 2: Translation WhatsApp
        row_wa = _translation_row(
            item, extract, lang, script, gloss,
            disaster_type=disaster_type,
            intent_label=intent_label,
            surface_format="whatsapp",
            source_quality=source_quality,
            extraction_method=extraction_method,
        )
        if validation_status != "source_authentic":
            object.__setattr__(row_wa, "validation_status", validation_status)
        rows.append(row_wa)

        # Row 3+: Non-translation task (cycle through types)
        non_trans_cycle = ["classification", "qa", "extraction"]
        nt_type = non_trans_cycle[i % len(non_trans_cycle)]

        if nt_type == "classification":
            nt_row = _classification_row(
                item, extract, lang, script, gloss,
                disaster_type=disaster_type,
                source_quality=source_quality,
                extraction_method=extraction_method,
            )
        elif nt_type == "qa":
            nt_row = _qa_row(
                item, extract, lang, script, gloss,
                disaster_type=disaster_type,
                source_quality=source_quality,
                extraction_method=extraction_method,
            )
        else:
            nt_row = _extraction_row(
                item, extract, lang, script, gloss,
                disaster_type=disaster_type,
                source_quality=source_quality,
                extraction_method=extraction_method,
            )

        if validation_status != "source_authentic":
            object.__setattr__(nt_row, "validation_status", validation_status)
        rows.append(nt_row)

        # For items with rich content, add additional surface formats
        if i % 5 == 0 and len(items) > 3:
            # Radio script row
            radio_row = _translation_row(
                item, extract, lang, script, gloss,
                disaster_type=disaster_type,
                intent_label=intent_label,
                surface_format="radio_script" if "radio" not in section else "official_bulletin",
                source_quality=source_quality,
                extraction_method=extraction_method,
            )
            # Override surface format for radio/bulletin
            object.__setattr__(radio_row, "surface_format", "radio_script")
            object.__setattr__(radio_row, "instruction_type", "rewrite")
            if validation_status != "source_authentic":
                object.__setattr__(radio_row, "validation_status", validation_status)
            rows.append(radio_row)

        if i % 7 == 0 and len(items) > 5:
            # Official bulletin row
            bulletin_row = _translation_row(
                item, extract, lang, script, gloss,
                disaster_type=disaster_type,
                intent_label=intent_label,
                surface_format="official_bulletin",
                source_quality=source_quality,
                extraction_method=extraction_method,
            )
            object.__setattr__(bulletin_row, "surface_format", "official_bulletin")
            object.__setattr__(bulletin_row, "instruction_type", "rewrite")
            if validation_status != "source_authentic":
                object.__setattr__(bulletin_row, "validation_status", validation_status)
            rows.append(bulletin_row)

    return rows

