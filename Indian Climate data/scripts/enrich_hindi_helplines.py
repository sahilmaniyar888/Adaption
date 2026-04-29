"""Enrich Hindi rows with missing helplines.

Targets rows with actionable intents or high risk that lack helplines.
Appends: "आपातकाल में 108 या 112 पर संपर्क करें।"
"""
import json
import logging
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enrich_hindi")

ACTIONABLE_INTENTS = {
    "warn_imminent_risk",
    "first_aid_instruction",
    "worker_safety_protocol",
    "preparedness_advice",
    "vulnerable_population_guidance"
}

def main():
    seed_file = SEED_DIR / "seed_v2_multilingual.jsonl"
    if not seed_file.exists():
        logger.error(f"Not found: {seed_file}")
        sys.exit(1)

    rows = []
    enriched_count = 0

    with seed_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            data = json.loads(line)
            row = BharatCRICRow(**data)

            is_actionable = row.intent_label in ACTIONABLE_INTENTS
            # Risk heuristics
            high_risk_kw = ["108", "112", "heatstroke", "collapse", "emergency", "बेहोश", "लू", "मौत"]
            is_high_risk = any(kw in row.completion for kw in high_risk_kw)

            if row.language == "hin" and not row.helplines_mentioned and (is_actionable or is_high_risk):
                if row.intent_label == "scam_alert" or row.disaster_type == "disaster_scam_heat":
                    suffix = " धोखाधड़ी की सूचना 1930 पर दें।"
                    helplines = ["1930"]
                elif enriched_count % 2 == 0:
                    suffix = " आपातकाल में 108 पर संपर्क करें।"
                    helplines = ["108"]
                else:
                    suffix = " आपातकाल में 112 पर संपर्क करें।"
                    helplines = ["112"]

                if row.surface_format == "sms" and len(row.completion) + len(suffix) > 160:
                    # try shorter
                    suffix = f" कॉल {helplines[0]}."
                    
                if row.surface_format == "sms" and len(row.completion) + len(suffix) > 160:
                    pass # skip if it's too long
                else:
                    object.__setattr__(row, "completion", row.completion.strip() + suffix)
                    row.helplines_mentioned.extend(helplines)
                    row.validation_status = "source_authentic_enriched"
                    if not row.metadata_json:
                        row.metadata_json = {}
                    row.metadata_json["enrichment"] = {
                        "type": "helpline_append",
                        "added_text": suffix.strip()
                    }
                    enriched_count += 1
            
            rows.append(row)

    logger.info(f"Enriched {enriched_count} Hindi rows with helplines.")

    with seed_file.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(row.model_dump_json() + "\n")

if __name__ == "__main__":
    main()
