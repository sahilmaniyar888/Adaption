# Day 2 Failure Modes & Source Gaps

This document tracks known issues, failure modes, and gaps in the current Day 2 multilingual seed dataset to guide Day 3 Adaption and expansion.

## 1. Missing Helplines
- **Pattern:** Non-English text extracted from generic safety websites often lacks immediate, actionable emergency numbers. 
- **Impact:** Before correction, Hindi helpline grounding was at 17%.
- **Action Taken:** Executed `enrich_hindi_helplines.py` to append "आपातकाल में 108 या 112 पर संपर्क करें" to actionable or high-risk Hindi rows. This manual intervention is necessary for the seed so the expansion model (Adaption) has proper grounding examples.

## 2. Weak Translations & Translation Dominance
- **Pattern:** 91% of non-English rows generated initially were just translations (163 out of 180). This disguises a translation corpus as an instruction dataset.
- **Impact:** Low instruction diversity. If not fixed, Adaption will just generate translation tasks.
- **Action Taken:** Updated the generation cycle to distribute tasks among `translation`, `classification`, `qa`, and `extraction`. For Day 3, we must strictly cap translation expansion to ≤50% of the newly adapted rows.

## 3. Surface Format Imbalance
- **Pattern:** `sms` and `whatsapp` formats dominated due to early design decisions. `community_post` also had healthy numbers, but `radio_script` and `official_bulletin` were severely underrepresented (< 1%).
- **Impact:** Lacks diversity for certain downstream evaluations.
- **Action Taken:** Implemented `balance_formats.py` to inject at least 30 `radio_script` and 30 `official_bulletin` formats by converting selected `sms` / `whatsapp` rows.

## 4. Domain Misses / Source Gaps
- **Pattern:** Authentic Wikipedia articles in Bhojpuri (bh.wikipedia.org) and Maithili (mai.wikipedia.org) on climate/heatwaves are extremely scarce. 
- **Impact:** Forced reliance on NDMA paraphrased translations for these languages.
- **Action Taken:** Tagged Wikipedia rows with `quality_flag="medium"`. Assigned `quality_flag="high_confidence"` only to manually curated, verified sources like NDMA, IMD, PIB, or State SDMAs. Day 3 Adaption should prioritize expanding rows with `high_confidence` flags.

## 5. Santali Ol Chiki Restrictions
- **Pattern:** Ol Chiki source data is highly limited and validation is difficult.
- **Impact:** Risk of hallucinating Devanagari text or low-quality grammar if expanded blindly by LLMs.
- **Action Taken:** Applied a hard `santali_policy: "seed_only_no_expansion"` inside the row metadata. Santali rows will bypass the Adaption pipeline entirely to protect corpus integrity.
