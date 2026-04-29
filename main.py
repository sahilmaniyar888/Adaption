"""CLI entry point — build, validate, extract landmarks, push to HF + Adaption.

Examples
--------
    python main.py build
    python main.py extract-landmarks --video clip.mp4 --out data/landmarks/clip.npy
    python main.py push-hf --repo sahilmaniyar/isl-medical-it
    python main.py push-adaption --hf sahilmaniyar/isl-medical-it
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from isl_dataset.generator import build_dataset, write_dataset_card, write_schema


def _load_dotenv() -> None:
    """Lightweight .env loader (avoids adding python-dotenv).

    Reads `KEY=value` lines from `.env` next to this file and registers them
    in `os.environ` if not already set. Lines starting with `#` are ignored.
    """
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
JSONL = DATA_DIR / "isl_medical.jsonl"
SCHEMA = DATA_DIR / "isl_medical.schema.json"
CARD = DATA_DIR / "README.md"


def cmd_build(_: argparse.Namespace) -> int:
    print(f"[build] writing -> {JSONL}")
    stats = build_dataset(JSONL)
    write_schema(SCHEMA)
    write_dataset_card(CARD, stats)
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"[build] schema  -> {SCHEMA}")
    print(f"[build] card    -> {CARD}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    from isl_dataset.mediapipe_pipeline import extract_and_save

    res = extract_and_save(Path(args.video), Path(args.out))
    print(json.dumps({
        "frames": res.frame_count,
        "fps": res.fps,
        "shape": list(res.landmarks.shape),
        "bbox": res.bbox,
        "out": str(args.out),
    }, indent=2))
    return 0


def cmd_push_hf(args: argparse.Namespace) -> int:
    from isl_dataset.upload import push_to_huggingface

    if not JSONL.exists():
        print("Dataset not built yet — run `python main.py build` first.", file=sys.stderr)
        return 1
    url = push_to_huggingface(
        repo_id=args.repo,
        jsonl_path=JSONL,
        schema_path=SCHEMA,
        dataset_card_path=CARD,
        private=args.private,
    )
    print(f"[hf] pushed -> {url}")
    return 0


def cmd_push_adaption(args: argparse.Namespace) -> int:
    from isl_dataset.upload import push_to_adaption

    result = push_to_adaption(
        hf_repo_id=args.hf,
        local_jsonl=JSONL if args.local else None,
        name=args.name,
    )
    print(f"[adaption] dataset created: {result}")
    return 0


def cli() -> int:
    p = argparse.ArgumentParser(prog="isl-build")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("build", help="Generate the JSONL dataset + schema + card.")
    sp.set_defaults(func=cmd_build)

    sp = sub.add_parser("extract-landmarks", help="Run MediaPipe Holistic on a video.")
    sp.add_argument("--video", required=True)
    sp.add_argument("--out", required=True)
    sp.set_defaults(func=cmd_extract)

    sp = sub.add_parser("push-hf", help="Push to a Hugging Face dataset repo.")
    sp.add_argument("--repo", required=True, help="e.g. sahilmaniyar/isl-medical-it")
    sp.add_argument("--private", action="store_true")
    sp.set_defaults(func=cmd_push_hf)

    sp = sub.add_parser("push-adaption", help="Ingest into the Adaption platform.")
    sp.add_argument("--hf", help="HF repo id to import from (preferred).")
    sp.add_argument("--local", action="store_true", help="Upload local JSONL instead.")
    sp.add_argument("--name", default="ISL-Medical Instruction Tuning")
    sp.set_defaults(func=cmd_push_adaption)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(cli())
