"""Module entrypoints exposed via pyproject.toml [project.scripts]."""
from __future__ import annotations


def build_seed() -> None:
    from scripts.build_seed import main  # type: ignore[import-not-found]
    main()
