"""Polite HTTP fetching with backoff and raw-bytes capture."""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests


logger = logging.getLogger(__name__)


DEFAULT_USER_AGENT = (
    "BharatCRIC/0.1 (research dataset; contact: sahilmaniyar1602@gmail.com)"
)
DEFAULT_DELAY_SECONDS = 2.0


def _ua() -> str:
    return os.getenv("BHARAT_CRIC_USER_AGENT", DEFAULT_USER_AGENT)


def fetch(url: str,
          *,
          raw_dir: Optional[Path] = None,
          raw_filename: Optional[str] = None,
          delay: float = DEFAULT_DELAY_SECONDS,
          retries: int = 3,
          timeout: float = 20.0) -> Optional[bytes]:
    """GET a URL politely with exponential backoff. Returns bytes or None.

    Saves the raw response to `raw_dir/raw_filename` when both are provided.
    Failure is non-fatal — we log and return None so the caller can fall back.
    """
    headers = {"User-Agent": _ua()}
    backoff = delay
    for attempt in range(1, retries + 1):
        try:
            time.sleep(delay if attempt == 1 else backoff)
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                if raw_dir and raw_filename:
                    raw_dir.mkdir(parents=True, exist_ok=True)
                    (raw_dir / raw_filename).write_bytes(resp.content)
                return resp.content
            logger.warning("fetch %s -> HTTP %s (attempt %d)",
                           url, resp.status_code, attempt)
        except requests.RequestException as exc:
            logger.warning("fetch %s failed: %s (attempt %d)", url, exc, attempt)
        backoff *= 2
    logger.error("fetch %s gave up after %d attempts", url, retries)
    return None
