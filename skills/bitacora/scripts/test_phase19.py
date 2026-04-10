#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase19"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import get_entry_by_id, search_entries  # noqa: E402
from save_entry import DuplicateEntryError, append_entry, capture_entry, split_entry_blocks  # noqa: E402


def count_blocks(file_path: Path) -> int:
    return len(split_entry_blocks(file_path.read_text(encoding="utf-8")))


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        url = "https://example.com/instalacion-electrica"
        original_entry, file_path = append_entry(
            project="camper",
            category="electricidad",
            content=url,
            source=url,
            additional_content="Nota base sobre ubicación del inversor.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        assert count_blocks(file_path) == 1
        time.sleep(0.02)

        # Test 1: oferta de upsert cuando aparece un duplicado
        offered = capture_entry(
            project="camper",
            category="electricidad",
            content="Comparar también con el paso de cables hacia el arcón.",
            source=url,
            tags=["cableado", "arcon"],
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="offer",
        )
        assert offered.status == "duplicate"
        assert "fusionar" in offered.prompt.lower()
        assert count_blocks(file_path) == 1, "La oferta de upsert no debe crear una entrada nueva"

        # Test 2: fusión correcta de nota personal sin tocar campos inmutables
        merged = capture_entry(
            project="camper",
            category="electricidad",
            content="Comparar también con el paso de cables hacia el arcón.",
            source=url,
            tags=["cableado", "arcon"],
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="merge",
        )
        assert merged.status == "merged"
        assert merged.entry is not None
        assert "no he creado un duplicado" in merged.prompt.lower()
        assert count_blocks(file_path) == 1
        assert merged.entry.entry_id == original_entry.entry_id
        assert merged.entry.fecha == original_entry.fecha
        assert merged.entry.fecha_actualizacion is not None

        lookup = get_entry_by_id("camper", original_entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        assert lookup.entry.entry_id == original_entry.entry_id
        assert lookup.entry.fecha == original_entry.fecha
        assert lookup.entry.tags == ["cableado", "arcon"]
        assert lookup.entry.contenido_adicional is not None
        assert "Nota base sobre ubicación del inversor." in lookup.entry.contenido_adicional
        assert "Comparar también con el paso de cables hacia el arcón." in lookup.entry.contenido_adicional
        assert "\n\n" in lookup.entry.contenido_adicional

        # Test 3: no se crea entrada duplicada y la lectura sigue siendo correcta
        technical_search = search_entries("camper", "arcón", DATA_DIR)
        assert len(technical_search.matched_hits) == 1
        assert technical_search.matched_hits[0].entry.entry_id == original_entry.entry_id

        # Regresión mínima: si no se acepta la fusión, la deduplicación sigue bloqueando
        blocked = False
        try:
            capture_entry(
                project="camper",
                category="electricidad",
                content="Otra observación que no debería crear otra entrada.",
                source=url,
                data_dir=DATA_DIR,
                metadata_fetcher=no_metadata,
            )
        except DuplicateEntryError:
            blocked = True
        assert blocked, "La deduplicación debe seguir bloqueando si no se acepta la fusión"
        assert count_blocks(file_path) == 1

        print("OK: fase 19 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
