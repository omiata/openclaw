#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase18"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from save_entry import append_entry, capture_entry, split_entry_blocks  # noqa: E402


def count_blocks(file_path: Path) -> int:
    return len(split_entry_blocks(file_path.read_text(encoding="utf-8")))


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Test 1: canonicalización YouTube corto/largo
        youtube_short = "https://youtu.be/Wyqv40KmNOk"
        youtube_long = "https://www.youtube.com/watch?v=Wyqv40KmNOk&feature=share"
        first_youtube, youtube_path = append_entry(
            project="camper-youtube",
            category="electricidad",
            content=youtube_short,
            source=youtube_short,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        duplicate_youtube = capture_entry(
            project="camper-youtube",
            category="electricidad",
            content=youtube_long,
            source=youtube_long,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="offer",
        )
        assert duplicate_youtube.status == "duplicate"
        assert duplicate_youtube.duplicate_match is not None
        assert duplicate_youtube.duplicate_match.entry.entry_id == first_youtube.entry_id
        assert "No he creado un duplicado" in duplicate_youtube.prompt
        assert count_blocks(youtube_path) == 1

        # Test 2: trailing slash conservador
        slash_base = "https://example.com/guia-aislamiento/"
        slash_variant = "https://example.com/guia-aislamiento"
        slash_entry, slash_path = append_entry(
            project="camper-slash",
            category="aislamiento",
            content=slash_base,
            source=slash_base,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        duplicate_slash = capture_entry(
            project="camper-slash",
            category="aislamiento",
            content=slash_variant,
            source=slash_variant,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="offer",
        )
        assert duplicate_slash.status == "duplicate"
        assert duplicate_slash.duplicate_match is not None
        assert duplicate_slash.duplicate_match.entry.entry_id == slash_entry.entry_id
        assert count_blocks(slash_path) == 1

        # Test 3: parámetros irrelevantes
        params_base = "https://example.com/ventana-techo"
        params_variant = "https://example.com/ventana-techo?utm_source=telegram&fbclid=abc123"
        params_entry, params_path = append_entry(
            project="camper-params",
            category="ventilacion",
            content=params_base,
            source=params_base,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        duplicate_params = capture_entry(
            project="camper-params",
            category="ventilacion",
            content=params_variant,
            source=params_variant,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="offer",
        )
        assert duplicate_params.status == "duplicate"
        assert duplicate_params.duplicate_match is not None
        assert duplicate_params.duplicate_match.entry.entry_id == params_entry.entry_id
        assert count_blocks(params_path) == 1

        # Regresión mínima: las URLs distintas con query significativa siguen entrando y la deduplicación exacta previa no se rompe
        page_one = append_entry(
            project="camper-distinct",
            category="ideas-generales",
            content="https://example.com/buscador?page=1",
            source="https://example.com/buscador?page=1",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        page_two = append_entry(
            project="camper-distinct",
            category="ideas-generales",
            content="https://example.com/buscador?page=2",
            source="https://example.com/buscador?page=2",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        distinct_path = page_one[1]
        assert count_blocks(distinct_path) == 2
        assert page_one[0].entry_id != page_two[0].entry_id

        print("OK: fase 18 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
