"""Source-fetching modules. Each exposes a `fetch() -> list[SourceExtract]`."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class SourceExtract:
    """One coherent chunk of authoritative text with provenance."""
    raw_text: str
    url: str
    fetched_at: datetime
    language_hint: str
    doc_type: str  # "bulletin", "guideline", "press_release", "advisory"
    section: str = ""  # e.g. "do_list", "dont_list", "vulnerable", "first_aid"
    items: List[str] = field(default_factory=list)  # parsed bullet items if any
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["fetched_at"] = self.fetched_at.isoformat()
        return d


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
