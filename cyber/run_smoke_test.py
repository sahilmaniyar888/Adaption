"""Smoke test: upload 12 rows to Adaption, run prompt_rephrase, compare in/out.

Reports inline (no .md output). Use:
    uv run python -X utf8 cyber/run_smoke_test.py
"""
from __future__ import annotations

import csv
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATASET = ROOT / "dataset_v0.csv"
SMOKE_CSV = ROOT / "smoke_test_input.csv"

SMOKE_IDS = [
    "CYB-SCALE-046",   # genuine Hindi UPI
    "CYB-PILOT-004",   # genuine Marathi courier
    "CYB-PILOT-007",   # genuine English KYC
    "CYB-SCALE-014",   # scam English digital_arrest
    "CYB-PILOT-002",   # scam Hindi digital_arrest
    "CYB-PILOT-005",   # scam Marathi courier (USSD)
    "CYB-PILOT-008",   # scam English KYC
    "CYB-SCALE-104",   # scam Hindi KYC
    "CYB-PILOT-011",   # scam Hinglish UPI - the deliberately-ambiguous one
    "CYB-PILOT-003",   # help Hindi digital_arrest
    "CYB-PILOT-006",   # help Marathi courier
    "CYB-PILOT-012",   # help Hinglish UPI
]


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)


def select_rows() -> list[dict]:
    rows = list(csv.DictReader(DATASET.open(encoding="utf-8")))
    by_id = {r["row_id"]: r for r in rows}
    return [by_id[i] for i in SMOKE_IDS if i in by_id]


def write_smoke_csv(picked: list[dict]) -> list[str]:
    fields = list(picked[0].keys())
    with SMOKE_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writeheader()
        w.writerows(picked)
    return fields


def main() -> int:
    load_env(ROOT / ".env")
    api_key = os.environ.get("ADAPTION_API_KEY")
    if not api_key:
        print("ERROR: ADAPTION_API_KEY not set in cyber/.env or environment", file=sys.stderr)
        return 1
    print(f"[env] ADAPTION_API_KEY loaded ({len(api_key)} chars, prefix={api_key[:8]}...)")

    picked = select_rows()
    if len(picked) != 12:
        print(f"ERROR: expected 12 rows, got {len(picked)}", file=sys.stderr)
        return 1
    fields = write_smoke_csv(picked)
    print(f"[csv] wrote 12 rows to {SMOKE_CSV} ({len(fields)} cols)")

    from adaption import Adaption, BadRequestError, AdaptionError
    client = Adaption(api_key=api_key)

    print("\n[upload] sending CSV to Adaption…")
    upload_resp = client.datasets.upload_file(path=str(SMOKE_CSV), name="ISL-Cyber smoke test 12 rows")
    print(f"[upload] response: {upload_resp!r}")

    dataset_id = getattr(upload_resp, "id", None) or getattr(upload_resp, "dataset_id", None)
    if not dataset_id and isinstance(upload_resp, dict):
        dataset_id = upload_resp.get("id") or upload_resp.get("dataset_id")
    if not dataset_id:
        print(f"ERROR: could not extract dataset_id from upload response", file=sys.stderr)
        return 1
    print(f"[upload] dataset_id = {dataset_id}")

    print("\n[run] starting prompt_rephrase recipe…")
    try:
        run_resp = client.datasets.run(
            dataset_id,
            column_mapping={"prompt": "message_text"},
            recipe_specification={
                "recipes": {"prompt_rephrase": True, "deduplication": False, "reasoning_traces": False},
                "version": "v1",
            },
        )
        print(f"[run] response: {run_resp!r}")
    except BadRequestError as e:
        print(f"[run] BadRequestError: {e}")
        print("[run] trying alternative column_mapping (prompt only) without recipe version…")
        try:
            run_resp = client.datasets.run(
                dataset_id,
                column_mapping={"prompt": "message_text"},
                recipe_specification={"recipes": {"prompt_rephrase": True}},
            )
            print(f"[run] response: {run_resp!r}")
        except Exception as e2:
            print(f"[run] still failed: {e2}", file=sys.stderr)
            return 1

    print("\n[wait] waiting for completion (timeout 10 min)…")
    status = client.datasets.wait_for_completion(dataset_id, timeout=600.0)
    print(f"[wait] final status: {status!r}")

    print("\n[download] fetching transformed CSV…")
    out_csv = client.datasets.download(dataset_id, file_format="csv")
    out_rows = list(csv.DictReader(io.StringIO(out_csv)))
    print(f"[download] received {len(out_rows)} rows, columns: {list(out_rows[0].keys()) if out_rows else 'none'}")

    in_by_id = {r["row_id"]: r for r in picked} if picked and "row_id" in picked[0] else {}
    out_by_id = {r.get("row_id", ""): r for r in out_rows} if out_rows else {}

    print("\n========================================")
    print("INPUT vs OUTPUT comparison")
    print("========================================")
    for inp in picked:
        rid = inp["row_id"]
        outp = out_by_id.get(rid)
        print(f"\n--- {rid} | {inp['variant_type']} | {inp['language']} | {inp['scam_type']} ---")
        print(f"  IN  : {inp['message_text']}")
        if outp:
            out_text = outp.get("message_text") or outp.get("prompt") or outp.get("rephrased") or "<no text col>"
            print(f"  OUT : {out_text}")
            same = (out_text.strip() == inp['message_text'].strip())
            print(f"  same?: {same}")
            cols_preserved = all(outp.get(c) == inp.get(c) for c in inp if c != "message_text" and c in outp)
            print(f"  metadata cols preserved: {cols_preserved}")
        else:
            print(f"  OUT : <not found in output>")

    print("\n[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
