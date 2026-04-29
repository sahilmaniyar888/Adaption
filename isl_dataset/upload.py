"""Publish the dataset to Hugging Face Hub, then ingest it into Adaption."""

from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import HfApi, create_repo, upload_file


def push_to_huggingface(
    *,
    repo_id: str,
    jsonl_path: Path,
    schema_path: Path,
    dataset_card_path: Path,
    private: bool = False,
    token: str | None = None,
) -> str:
    """Push dataset assets to a HF dataset repo and return the repo URL."""
    token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise RuntimeError(
            "Hugging Face token missing. Run `huggingface-cli login` or set HF_TOKEN."
        )

    api = HfApi(token=token)
    create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True, token=token)

    targets = [
        (jsonl_path, "data/isl_medical.jsonl"),
        (schema_path, "schema/isl_medical.schema.json"),
        (dataset_card_path, "README.md"),
    ]
    for local, remote in targets:
        if not local.exists():
            raise FileNotFoundError(f"Missing artifact: {local}")
        upload_file(
            path_or_fileobj=str(local),
            path_in_repo=remote,
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
            commit_message=f"upload {remote}",
        )
        api.upload_file  # silences linters that expect HfApi usage

    return f"https://huggingface.co/datasets/{repo_id}"


def push_to_adaption(
    *,
    hf_repo_id: str | None = None,
    local_jsonl: Path | None = None,
    name: str = "ISL-Medical Instruction Tuning",
    files: list[str] | None = None,
    api_key: str | None = None,
):
    """Ingest the dataset into the Adaption platform.

    Two paths:
      1. `hf_repo_id` set — async pull from HF using `create_from_huggingface`.
         Pass `files=[...]` listing the in-repo paths to import.
      2. `local_jsonl` set — direct presigned `upload_file` flow.
    """
    try:
        from adaption import Adaption
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Adaption SDK not installed. Run `pip install adaption`."
        ) from exc

    api_key = api_key or os.environ.get("ADAPTION_API_KEY")
    if not api_key:
        raise RuntimeError("ADAPTION_API_KEY missing. Get one at Adaption → Settings → API keys.")

    client = Adaption(api_key=api_key)

    if hf_repo_id:
        url = f"https://huggingface.co/datasets/{hf_repo_id}"
        return client.datasets.create_from_huggingface(
            url=url,
            files=files or ["data/isl_medical.jsonl"],
        )

    if local_jsonl:
        if not local_jsonl.exists():
            raise FileNotFoundError(local_jsonl)
        return client.datasets.upload_file(path=str(local_jsonl), name=name)

    raise ValueError("Provide either hf_repo_id or local_jsonl.")
