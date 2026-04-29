"""Row- and corpus-level validators for BharatCRIC.

Includes the locked corpus rule: at least 20 percent of rows must contain a
validated helpline grounding in their completion.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .helpline_registry import (
    extract_helpline_candidates,
    find_invalid_helplines,
    find_valid_helplines,
    is_valid_helpline,
)
from .schema import BharatCRICRow, SMS_MAX_CHARS


HELPLINE_GROUNDING_MIN_RATIO = 0.20


# Hard-coded validated central-government scheme names. Heat-relief schemes
# are deliberately absent: there is no centralised PM heat-relief scheme as
# of April 2026, so any row that names one is flagged as hallucinated.
VALIDATED_SCHEMES: List[str] = [
    "PMAY",
    "Pradhan Mantri Awas Yojana",
    "MGNREGA",
    "Mahatma Gandhi National Rural Employment Guarantee",
    "Ayushman Bharat",
    "PM Jan Arogya Yojana",
    "PMJAY",
    "Jan Aushadhi",
    "Pradhan Mantri Bhartiya Janaushadhi Pariyojana",
]

_SCHEME_TRIGGER_RE = re.compile(
    r"\b(PM\s+|Pradhan\s+Mantri\s+|Yojana\b|scheme\b)",
    flags=re.IGNORECASE,
)


@dataclass
class ValidationResult:
    ok: bool
    row_id: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CorpusReport:
    total_rows: int = 0
    by_language: Dict[str, int] = field(default_factory=dict)
    by_disaster_type: Dict[str, int] = field(default_factory=dict)
    by_surface_format: Dict[str, int] = field(default_factory=dict)
    by_validation_status: Dict[str, int] = field(default_factory=dict)
    by_intent_label: Dict[str, int] = field(default_factory=dict)
    by_source_host: Dict[str, int] = field(default_factory=dict)
    rows_with_helpline: int = 0
    helpline_grounding_ratio: float = 0.0
    helpline_grounding_target_met: bool = False
    duplicate_row_ids: List[str] = field(default_factory=list)
    near_duplicate_pairs: List[Tuple[str, str]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    # Day 2 metrics
    helpline_grounding_by_lang: Dict[str, float] = field(default_factory=dict)
    script_consistency_ratio: float = 1.0
    english_gloss_coverage: float = 1.0
    by_instruction_type: Dict[str, int] = field(default_factory=dict)
    by_source_quality: Dict[str, int] = field(default_factory=dict)
    instruction_diversity_ratio: float = 1.0

    def as_dict(self) -> Dict:
        return {
            "total_rows": self.total_rows,
            "by_language": dict(self.by_language),
            "by_disaster_type": dict(self.by_disaster_type),
            "by_surface_format": dict(self.by_surface_format),
            "by_validation_status": dict(self.by_validation_status),
            "by_intent_label": dict(self.by_intent_label),
            "by_source_host": dict(self.by_source_host),
            "rows_with_helpline": self.rows_with_helpline,
            "helpline_grounding_ratio": round(self.helpline_grounding_ratio, 4),
            "helpline_grounding_target_met": self.helpline_grounding_target_met,
            "duplicate_row_ids": list(self.duplicate_row_ids),
            "near_duplicate_pairs": list(self.near_duplicate_pairs),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            # Day 2 metrics
            "helpline_grounding_by_lang": dict(self.helpline_grounding_by_lang),
            "script_consistency_ratio": round(self.script_consistency_ratio, 4),
            "english_gloss_coverage": round(self.english_gloss_coverage, 4),
            "by_instruction_type": dict(self.by_instruction_type),
            "by_source_quality": dict(self.by_source_quality),
            "instruction_diversity_ratio": round(self.instruction_diversity_ratio, 4),
        }


# ---------------------- row-level checks ----------------------------------


def validate_helplines(row: BharatCRICRow) -> Tuple[bool, List[str]]:
    """Reject rows whose completion contains a helpline-shaped number that is
    not in the registry."""
    invalid = find_invalid_helplines(row.completion)
    return (len(invalid) == 0, invalid)


def validate_no_invented_schemes(row: BharatCRICRow) -> Tuple[bool, Optional[str]]:
    """Flag rows that mention 'PM ', 'Pradhan Mantri ', 'Yojana' or 'scheme'
    without naming a scheme from the validated list. The disaster_scam_heat
    type is exempt because scam rows must be allowed to *quote* a fake scheme
    in order to label it as such."""
    if row.disaster_type == "disaster_scam_heat":
        return True, None
    if row.intent_label in {"scam_alert", "myth_correction"}:
        return True, None
    text = row.completion
    if not _SCHEME_TRIGGER_RE.search(text):
        return True, None
    if any(s.lower() in text.lower() for s in VALIDATED_SCHEMES):
        return True, None
    return False, "scheme-shaped phrase without a validated scheme name"


def validate_row(row: BharatCRICRow) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    if row.surface_format == "sms" and len(row.completion) > SMS_MAX_CHARS:
        errors.append(
            f"sms completion length {len(row.completion)} > {SMS_MAX_CHARS}"
        )

    ok_helplines, invalid = validate_helplines(row)
    if not ok_helplines:
        errors.append(
            f"unverified helpline-shaped numbers in completion: {invalid}"
        )

    ok_schemes, scheme_msg = validate_no_invented_schemes(row)
    if not ok_schemes:
        errors.append(f"hallucinated-scheme guard: {scheme_msg}")

    declared = set(row.helplines_mentioned)
    discovered = set(find_valid_helplines(row.completion))
    if declared != discovered:
        warnings.append(
            f"helplines_mentioned mismatch: declared={sorted(declared)} "
            f"discovered={sorted(discovered)}"
        )

    return ValidationResult(
        ok=not errors,
        row_id=row.row_id,
        errors=errors,
        warnings=warnings,
    )


# ---------------------- corpus-level checks -------------------------------


def _shingles(text: str, k: int = 6) -> set:
    tokens = re.findall(r"\w+", text.lower())
    return {" ".join(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _row_signature(row: BharatCRICRow) -> str:
    h = hashlib.sha1()
    h.update(row.completion.encode("utf-8"))
    h.update(b"||")
    h.update(row.instruction.encode("utf-8"))
    return h.hexdigest()


def _source_host(ref: str) -> str:
    if ref.startswith("internal_curated:"):
        return "internal_curated"
    m = re.match(r"https?://([^/]+)", ref)
    return m.group(1) if m else "unknown"


def validate_corpus(rows: Iterable[BharatCRICRow],
                     near_dup_threshold: float = 0.92) -> CorpusReport:
    rows = list(rows)
    report = CorpusReport(total_rows=len(rows))

    lang = Counter()
    dtype = Counter()
    sfmt = Counter()
    vstat = Counter()
    intent = Counter()
    host = Counter()

    seen_sigs: Dict[str, str] = {}
    duplicates: List[str] = []
    rows_with_helpline = 0
    shingles_by_id: List[Tuple[str, set]] = []

    for row in rows:
        result = validate_row(row)
        if not result.ok:
            report.errors.extend(f"row {row.row_id}: {e}" for e in result.errors)
        report.warnings.extend(f"row {row.row_id}: {w}" for w in result.warnings)

        lang[row.language] += 1
        dtype[row.disaster_type] += 1
        sfmt[row.surface_format] += 1
        vstat[row.validation_status] += 1
        intent[row.intent_label] += 1
        host[_source_host(row.source_reference)] += 1

        if find_valid_helplines(row.completion):
            rows_with_helpline += 1

        sig = _row_signature(row)
        if sig in seen_sigs:
            duplicates.append(row.row_id)
        else:
            seen_sigs[sig] = row.row_id

        shingles_by_id.append((row.row_id, _shingles(row.completion)))

    report.by_language = dict(lang)
    report.by_disaster_type = dict(dtype)
    report.by_surface_format = dict(sfmt)
    report.by_validation_status = dict(vstat)
    report.by_intent_label = dict(intent)
    report.by_source_host = dict(host)
    report.rows_with_helpline = rows_with_helpline
    report.helpline_grounding_ratio = (
        rows_with_helpline / len(rows) if rows else 0.0
    )
    report.helpline_grounding_target_met = (
        report.helpline_grounding_ratio >= HELPLINE_GROUNDING_MIN_RATIO
    )
    report.duplicate_row_ids = duplicates
    if duplicates:
        report.errors.append(
            f"{len(duplicates)} exact-duplicate completion+instruction pairs"
        )

    if not report.helpline_grounding_target_met and rows:
        report.errors.append(
            f"helpline grounding ratio {report.helpline_grounding_ratio:.2%} "
            f"< required {HELPLINE_GROUNDING_MIN_RATIO:.0%}"
        )

    # near-dup detection (O(n^2) — fine for Day 1 sizes)
    near_dups: List[Tuple[str, str]] = []
    for i in range(len(shingles_by_id)):
        id_a, sh_a = shingles_by_id[i]
        if not sh_a:
            continue
        for j in range(i + 1, len(shingles_by_id)):
            id_b, sh_b = shingles_by_id[j]
            if not sh_b:
                continue
            if _jaccard(sh_a, sh_b) >= near_dup_threshold:
                near_dups.append((id_a, id_b))
    report.near_duplicate_pairs = near_dups
    if near_dups:
        report.warnings.append(f"{len(near_dups)} near-duplicate pairs (J>={near_dup_threshold})")

    # ---- Day 2 metrics ----

    # Per-language helpline grounding
    lang_helpline: Dict[str, int] = defaultdict(int)
    lang_total: Dict[str, int] = defaultdict(int)
    for row in rows:
        lang_total[row.language] += 1
        if find_valid_helplines(row.completion):
            lang_helpline[row.language] += 1
    report.helpline_grounding_by_lang = {
        k: (lang_helpline[k] / v if v else 0.0) for k, v in lang_total.items()
    }

    # Script consistency
    from .schema import LANGUAGE_TO_SCRIPT
    script_ok = sum(
        1 for r in rows
        if LANGUAGE_TO_SCRIPT.get(r.language) == r.script
    )
    report.script_consistency_ratio = script_ok / len(rows) if rows else 1.0
    if report.script_consistency_ratio < 0.95:
        report.errors.append(
            f"script consistency {report.script_consistency_ratio:.2%} < 95%"
        )

    # English gloss coverage (non-English rows)
    non_eng = [r for r in rows if r.language != "eng"]
    if non_eng:
        gloss_present = sum(1 for r in non_eng
                           if r.english_gloss and r.english_gloss.strip())
        report.english_gloss_coverage = gloss_present / len(non_eng)
        if report.english_gloss_coverage < 0.70:
            report.warnings.append(
                f"english_gloss coverage {report.english_gloss_coverage:.2%} "
                f"< recommended 70%"
            )
    else:
        report.english_gloss_coverage = 1.0

    # Instruction type distribution
    itype = Counter()
    for r in rows:
        if r.instruction_type:
            itype[r.instruction_type] += 1
        else:
            itype["unspecified"] += 1
    report.by_instruction_type = dict(itype)

    # Instruction diversity: % of non-English rows that are non-translation
    if non_eng:
        non_translation = sum(
            1 for r in non_eng
            if r.instruction_type and r.instruction_type != "translation"
        )
        report.instruction_diversity_ratio = non_translation / len(non_eng)
    else:
        report.instruction_diversity_ratio = 1.0

    # Source quality distribution
    squal = Counter()
    for r in rows:
        if r.source_quality:
            squal[r.source_quality] += 1
        else:
            squal["unspecified"] += 1
    report.by_source_quality = dict(squal)

    # Domain keyword validation
    for r in rows:
        if r.language != "eng":
            ok, msg = validate_domain_keywords(r)
            if not ok:
                report.warnings.append(f"row {r.row_id}: {msg}")

    # Santali Devanagari leakage check
    for r in rows:
        if r.language == "sat":
            ok, msg = validate_no_devanagari_leakage(r)
            if not ok:
                report.warnings.append(f"row {r.row_id}: {msg}")

    return report


# ---------------------- Day 2 row-level validators --------------------------


# Domain keywords for filtering non-English extracts
DOMAIN_KEYWORDS_EN = {
    "heat", "heatwave", "temperature", "sun", "shade", "water", "hydration",
    "dehydration", "ors", "heatstroke", "summer", "hot", "cool", "safety",
    "precaution", "ambulance", "hospital", "emergency", "helpline",
}
DOMAIN_KEYWORDS_DEVA = {
    "लू", "गर्मी", "धूप", "पानी", "तापमान", "लू चलना", "गरमी",
    "ठंडा", "छाया", "ओआरएस", "अस्पताल", "सूरज", "बचाव",
    "स्वास्थ्य", "सावधानी", "हीटवेव", "उपचार", "पीना",
}
DOMAIN_KEYWORDS_OLCK = {
    "ᱦᱟᱯᱨᱟᱢ", "ᱫᱟᱜ", "ᱵᱤᱱ", "ᱨᱚᱜ", "ᱥᱮᱸᱫᱨᱟ",
}


def validate_domain_keywords(row: BharatCRICRow) -> Tuple[bool, Optional[str]]:
    """Check that non-English rows contain at least one domain keyword."""
    if row.language == "eng":
        return True, None
    text = (row.completion + " " + row.instruction).lower()
    if row.script == "Deva":
        keywords = DOMAIN_KEYWORDS_DEVA | DOMAIN_KEYWORDS_EN
    elif row.script == "Olck":
        keywords = DOMAIN_KEYWORDS_OLCK | DOMAIN_KEYWORDS_EN
    else:
        keywords = DOMAIN_KEYWORDS_EN
    for kw in keywords:
        if kw.lower() in text:
            return True, None
    return False, "no domain-relevant keyword found in completion+instruction"


def validate_no_devanagari_leakage(row: BharatCRICRow) -> Tuple[bool, Optional[str]]:
    """For Santali (Ol Chiki) rows, ensure Devanagari characters are <10%."""
    if row.language != "sat":
        return True, None
    text = row.completion
    if not text:
        return True, None
    deva_count = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    ratio = deva_count / len(text) if text else 0
    if ratio >= 0.10:
        return False, f"Devanagari leakage {ratio:.1%} >= 10% in Santali row"
    return True, None


def validate_olchiki_coverage(row: BharatCRICRow) -> Tuple[bool, Optional[str]]:
    """For Santali rows, check ≥80% Ol Chiki Unicode (U+1C50-U+1C7F)."""
    if row.language != "sat":
        return True, None
    text = row.completion
    if not text:
        return True, None
    olck_count = sum(1 for ch in text if '\u1C50' <= ch <= '\u1C7F')
    # Only count actual characters, not whitespace/punctuation
    alpha_chars = sum(1 for ch in text if not ch.isspace() and not ch in '.,;:!?()-')
    if alpha_chars == 0:
        return True, None
    ratio = olck_count / alpha_chars
    if ratio < 0.80:
        return False, f"Ol Chiki coverage {ratio:.1%} < 80%"
    return True, None


def validate_script_consistency(row: BharatCRICRow) -> Tuple[bool, Optional[str]]:
    """Verify script field matches language per LANGUAGE_TO_SCRIPT mapping."""
    from .schema import LANGUAGE_TO_SCRIPT
    expected = LANGUAGE_TO_SCRIPT.get(row.language)
    if expected and row.script != expected:
        return False, f"expected script {expected} for {row.language}, got {row.script}"
    return True, None
