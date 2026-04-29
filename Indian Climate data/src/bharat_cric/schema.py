"""Pydantic v2 row schema for BharatCRIC.

The model encodes every cross-field invariant we want enforced at write time so
downstream loaders can trust the JSONL.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


DisasterType = Literal[
    "heatwave",
    "heatstroke_health",
    "worker_safety",
    "vulnerable_population",
    "disaster_scam_heat",
    "cyclone",
    "general_preparedness",
]

LanguageCode = Literal["bho", "mai", "sat", "hin", "eng"]
ScriptCode = Literal["Deva", "Olck", "Latn"]

SurfaceFormat = Literal[
    "sms",
    "whatsapp",
    "official_bulletin",
    "radio_script",
    "community_post",
]

ValidationStatus = Literal[
    "source_authentic",
    "source_extracted_unverified_native_review_pending",
    "llm_adapted_eyescan_reviewed",
    "llm_adapted_unreviewed",
    "native_validated",
]

IntentLabel = Literal[
    "warn_imminent_risk",
    "first_aid_instruction",
    "preparedness_advice",
    "vulnerable_population_guidance",
    "worker_safety_protocol",
    "helpline_referral",
    "myth_correction",
    "scam_alert",
    "scam_attempt",
    "general_information",
]

LANGUAGE_TO_SCRIPT: Dict[str, str] = {
    "bho": "Deva",
    "mai": "Deva",
    "sat": "Olck",
    "hin": "Deva",
    "eng": "Latn",
}

SMS_MAX_CHARS = 160


def _new_row_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BharatCRICRow(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    row_id: str = Field(default_factory=_new_row_id)
    pair_id: Optional[str] = None
    disaster_type: DisasterType
    language: LanguageCode
    script: ScriptCode
    surface_format: SurfaceFormat
    instruction: str = Field(min_length=1)
    completion: str = Field(min_length=1)
    english_gloss: Optional[str] = None
    source_reference: str = Field(min_length=1)
    validation_status: ValidationStatus
    intent_label: IntentLabel
    length_constraint_satisfied: bool = True
    helplines_mentioned: List[str] = Field(default_factory=list)
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=_now)
    adaption_recipes_applied: List[str] = Field(default_factory=list)

    @field_validator("instruction")
    @classmethod
    def _instruction_word_cap(cls, v: str) -> str:
        if len(v.split()) > 500:
            raise ValueError("instruction must be <= 500 words")
        return v

    @field_validator("source_reference")
    @classmethod
    def _source_reference_shape(cls, v: str) -> str:
        if v.startswith("internal_curated:"):
            if len(v) <= len("internal_curated:"):
                raise ValueError("internal_curated reference must include a description")
            return v
        if not re.match(r"^https?://", v):
            raise ValueError(
                "source_reference must be a URL or 'internal_curated:{description}'"
            )
        return v

    @model_validator(mode="after")
    def _cross_field(self) -> "BharatCRICRow":
        # script must match language
        expected_script = LANGUAGE_TO_SCRIPT[self.language]
        if self.script != expected_script:
            raise ValueError(
                f"script {self.script!r} does not match language {self.language!r} "
                f"(expected {expected_script!r})"
            )

        # english_gloss required iff language != eng
        if self.language == "eng" and self.english_gloss is not None:
            raise ValueError("english_gloss must be None when language == 'eng'")
        if self.language != "eng" and (
            self.english_gloss is None or not self.english_gloss.strip()
        ):
            raise ValueError("english_gloss is required when language != 'eng'")

        # SMS length cap
        if self.surface_format == "sms":
            if len(self.completion) > SMS_MAX_CHARS:
                raise ValueError(
                    f"sms completion exceeds {SMS_MAX_CHARS} chars "
                    f"(got {len(self.completion)})"
                )

        # scam pair_id required
        if self.disaster_type == "disaster_scam_heat" and not self.pair_id:
            raise ValueError(
                "pair_id is required when disaster_type == 'disaster_scam_heat'"
            )

        # length_constraint_satisfied recompute
        if self.surface_format == "sms":
            object.__setattr__(
                self,
                "length_constraint_satisfied",
                len(self.completion) <= SMS_MAX_CHARS,
            )
        else:
            object.__setattr__(self, "length_constraint_satisfied", True)
        return self
