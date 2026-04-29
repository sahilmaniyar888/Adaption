"""Minimal instruction-tuning schema for the ISL-Medical dataset (v1.0).

One row = one healthcare instruction-tuning example. No multimodal pointers,
no provenance bloat — just clean prompt / completion / control tags.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    NEUROLOGY = "Neurology"
    CARDIOLOGY = "Cardiology"
    PULMONOLOGY = "Pulmonology"
    ONCOLOGY = "Oncology"
    ENDOCRINOLOGY = "Endocrinology"
    GASTROENTEROLOGY = "Gastroenterology"
    NEPHROLOGY = "Nephrology"
    ORTHOPEDICS = "Orthopedics"
    DERMATOLOGY = "Dermatology"
    OPHTHALMOLOGY = "Ophthalmology"
    ENT = "ENT"
    PSYCHIATRY = "Psychiatry"
    PEDIATRICS = "Pediatrics"
    MATERNAL = "Maternal Health"
    ANESTHESIOLOGY = "Anesthesiology"
    FIRST_AID = "First Aid"
    PHARMACY = "Pharmacy"
    DIAGNOSTICS = "Diagnostics"
    VACCINATION = "Vaccination"
    PUBLIC_HEALTH = "Public Health"
    HOSPITAL = "Hospital Administration"
    DENTISTRY = "Dentistry"
    REPRODUCTIVE = "Reproductive Health"
    ANATOMY = "Anatomy"
    SYMPTOMS = "Symptoms"


class Intent(str, Enum):
    TREATMENT_ADVICE = "treatment_advice"
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    EMERGENCY = "emergency"
    PREVENTION = "prevention"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Sample(BaseModel):
    id: str = Field(..., pattern=r"^isl-med-[a-z0-9-]+$")
    text_en: str = Field(..., min_length=1, max_length=512)
    text_hi: str = Field(..., min_length=1, max_length=512)
    gloss_sequence: str = Field(..., min_length=1, max_length=512)
    category: Category
    intent: Intent
    urgency: Urgency
    difficulty: Difficulty
    source: str = "synthetic_curated"

    @field_validator("text_en")
    @classmethod
    def en_word_count(cls, v: str) -> str:
        n = len(v.split())
        if not (8 <= n <= 20):
            raise ValueError(f"text_en must be 8-20 words; got {n}: {v!r}")
        return v

    @field_validator("gloss_sequence")
    @classmethod
    def gloss_uppercase_token_range(cls, v: str) -> str:
        allowed = set(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.?!+-/")
        bad = [c for c in v if c not in allowed]
        if bad:
            raise ValueError(f"gloss must be uppercase ISL; bad chars: {set(bad)!r}")
        tokens = [t for t in v.replace(",", " ").replace(".", " ")
                  .replace("?", " ").replace("!", " ").split() if t]
        if not (5 <= len(tokens) <= 12):
            raise ValueError(
                f"gloss_sequence must have 5-12 tokens; got {len(tokens)}: {v!r}"
            )
        return v


# Backwards-compat alias — `lexicon.py` / `contextual.py` still import the old
# enum name. Functionally identical.
MedicalCategory = Category


def json_schema() -> dict:
    return Sample.model_json_schema()
