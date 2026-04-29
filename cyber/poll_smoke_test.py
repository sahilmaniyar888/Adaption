"""Poll the in-flight Adaption smoke-test dataset; download + compare when done."""
from __future__ import annotations

import csv
import io
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
DATASET = ROOT / "dataset_v0.csv"
DATASET_ID = "a9594d9e-371b-434a-a839-37aeb3379e89"
SMOKE_IDS = [
    "CYB-SCALE-046", "CYB-PILOT-004", "CYB-PILOT-007",
    "CYB-SCALE-014", "CYB-PILOT-002", "CYB-PILOT-005",
    "CYB-PILOT-008", "CYB-SCALE-104", "CYB-PILOT-011",
    "CYB-PILOT-003", "CYB-PILOT-006", "CYB-PILOT-012",
]


def load_env(path: Path) -> None:
    if not path.exists(): return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if v: os.environ.setdefault(k.strip(), v)


def main() -> int:
    load_env(ROOT / ".env")
    api_key = os.environ.get("ADAPTION_API_KEY")
    if not api_key:
        print("ERROR: no ADAPTION_API_KEY"); return 1

    from adaption import Adaption
    client = Adaption(api_key=api_key)

    print(f"[poll] dataset {DATASET_ID}")
    deadline = time.time() + 1500.0  # 25 min
    interval = 15.0
    last_status = None
    while time.time() < deadline:
        s = client.datasets.get_status(DATASET_ID)
        status = getattr(s, "status", None) or (s.get("status") if isinstance(s, dict) else "?")
        if status != last_status:
            print(f"[poll] t+{int(time.time() - (deadline - 1500.0))}s status={status}", flush=True)
            last_status = status
        if status in ("completed", "succeeded", "failed", "error", "cancelled"):
            break
        time.sleep(interval)
    else:
        print("[poll] still not terminal after 25 min; aborting"); return 1

    print(f"\n[final] status={status}")
    if status not in ("completed", "succeeded"):
        try:
            print(f"[final] full status object: {s!r}")
        except Exception: pass
        return 1

    print("\n[download] fetching CSV…")
    out_csv = client.datasets.download(DATASET_ID, file_format="csv")
    out_rows = list(csv.DictReader(io.StringIO(out_csv)))
    print(f"[download] {len(out_rows)} rows; cols={list(out_rows[0].keys()) if out_rows else 'none'}")

    in_rows = list(csv.DictReader(DATASET.open(encoding="utf-8")))
    in_by_id = {r["row_id"]: r for r in in_rows}

    out_by_id: dict[str, dict] = {}
    for r in out_rows:
        rid = r.get("row_id") or ""
        if rid:
            out_by_id[rid] = r

    print("\n========== INPUT vs OUTPUT ==========")
    rephrased = unchanged = missing = 0
    metadata_drift = 0
    devanagari_break = 0
    bracket_break = 0

    for rid in SMOKE_IDS:
        inp = in_by_id.get(rid)
        outp = out_by_id.get(rid)
        if not inp:
            print(f"[skip] {rid}: not in source dataset"); continue
        print(f"\n--- {rid} | {inp['variant_type']} | {inp['language']} | {inp['scam_type']} ---")
        print(f"  IN : {inp['message_text']}")
        if not outp:
            print("  OUT: <missing in output>"); missing += 1; continue
        out_text = outp.get("message_text") or outp.get("rephrased") or outp.get("prompt") or ""
        print(f"  OUT: {out_text}")
        if out_text.strip() == inp["message_text"].strip():
            unchanged += 1; print("  -> UNCHANGED")
        else:
            rephrased += 1; print("  -> REPHRASED")

        # Metadata column drift
        for c in inp:
            if c == "message_text": continue
            if c in outp and outp[c] != inp[c]:
                metadata_drift += 1
                print(f"  -> META DRIFT col={c}: '{inp[c]}' -> '{outp[c]}'")

        # Devanagari preservation
        if inp["script"] == "Devanagari":
            in_dev = sum(1 for ch in inp["message_text"] if "ऀ" <= ch <= "ॿ")
            out_dev = sum(1 for ch in out_text if "ऀ" <= ch <= "ॿ")
            if in_dev > 0 and out_dev == 0:
                devanagari_break += 1
                print(f"  -> DEVANAGARI LOST (in:{in_dev} out:{out_dev})")

        # Bracket [.] preservation in scam rows with link
        if inp.get("contains_link") == "true" and "[.]" in inp["message_text"]:
            if "[.]" not in out_text:
                bracket_break += 1
                print(f"  -> BRACKET [.] DROPPED")

    print("\n========== SUMMARY ==========")
    print(f"  rephrased     : {rephrased}/{len(SMOKE_IDS)}")
    print(f"  unchanged     : {unchanged}/{len(SMOKE_IDS)}")
    print(f"  missing       : {missing}/{len(SMOKE_IDS)}")
    print(f"  metadata drift: {metadata_drift} col-violations")
    print(f"  devanagari    : {devanagari_break} rows lost script")
    print(f"  bracket [.]   : {bracket_break} rows dropped notation")

    # Write output CSV for inspection
    if out_rows:
        out_path = ROOT / "smoke_test_output.csv"
        with out_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()), quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writeheader(); w.writerows(out_rows)
        print(f"\n[saved] full output -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
