#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase12"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_output, build_search_output, get_entry_by_id, list_entries, search_entries  # noqa: E402
from save_entry import append_entry, split_entry_blocks  # noqa: E402


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        entry, file_path = append_entry(
            project="mini-camper",
            category="fijaciones-estructura",
            content="https://example.com/guia-anclajes",
            source="https://example.com/guia-anclajes",
            data_dir=DATA_DIR,
            resource_type="video",
            summary="Guía para anclajes limpios en estructura ligera.",
            tags=["anclajes", "estructura-ligera"],
        )
        assert file_path.exists(), "No se creó el archivo del proyecto"
        raw_text = file_path.read_text(encoding="utf-8")
        assert len(split_entry_blocks(raw_text)) == 1, "El archivo no contiene exactamente una entrada"
        assert "categoria: \"fijaciones-estructura\"" in raw_text, "La clave interna de categoría cambió en disco"
        assert "proyecto: \"mini-camper\"" in raw_text, "La clave interna de proyecto cambió en disco"
        assert "tipo: \"video\"" in raw_text, "La clave interna del tipo cambió en disco"

        # Test 1: humanización visible de categorías, proyectos y tipos
        listing = list_entries("mini-camper", DATA_DIR)
        assert listing.total_entries == 1
        human_listing = build_output(listing, technical=False)
        assert "Mini camper: 1 entrada." in human_listing
        assert "Fijaciones estructura" in human_listing
        assert "vídeo" in human_listing
        assert "fijaciones-estructura" not in human_listing
        assert "mini-camper" not in human_listing

        # Test 2: conservación de claves internas y filtrado correcto
        assert listing.matched_entries[0].categoria == "fijaciones-estructura"
        assert listing.matched_entries[0].proyecto == "mini-camper"
        assert listing.matched_entries[0].tipo == "video"

        filtered = list_entries("mini-camper", DATA_DIR, category="Fijaciones estructura")
        assert len(filtered.matched_entries) == 1, "El filtrado por categoría visible dejó de resolver la clave interna"
        assert filtered.matched_entries[0].categoria == "fijaciones-estructura"

        # Test 3: regresión de búsqueda y representación humana
        search = search_entries("mini-camper", "anclajes", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de encontrar la entrada"
        human_search = build_search_output(search, technical=False)
        assert "Fijaciones estructura" in human_search
        assert "vídeo" in human_search

        lookup = get_entry_by_id("mini-camper", entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        assert lookup.entry.categoria == "fijaciones-estructura"
        assert lookup.entry.tipo == "video"

        print("OK: fase 12 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
