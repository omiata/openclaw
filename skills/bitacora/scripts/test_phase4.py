#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase4"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import (  # noqa: E402
    build_entry_output,
    build_output,
    build_search_output,
    get_entry_by_id,
    list_entries,
    search_entries,
)
from save_entry import append_entry  # noqa: E402


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        project = "phase4-test"

        title_entry, _ = append_entry(
            project=project,
            category="cama",
            content="",
            data_dir=DATA_DIR,
            title="Cama plegable con guías laterales",
            summary="Estructura modular para ahorrar espacio.",
        )
        summary_entry, _ = append_entry(
            project=project,
            category="aislamiento",
            content="Paneles XPS y lana técnica.",
            data_dir=DATA_DIR,
            title="Comparativa de aislamiento",
            summary="Analiza condensacion en pasos de rueda y puentes térmicos.",
        )
        tags_entry, _ = append_entry(
            project=project,
            category="electricidad",
            content="Esquema base de batería auxiliar.",
            data_dir=DATA_DIR,
            title="Instalación 12V básica",
            summary="Punto de partida para fusibles y consumos.",
            tags=["solar", "bateria", "12v"],
        )
        note_entry, _ = append_entry(
            project=project,
            category="distribucion",
            content="Croquis preliminar del mueble lateral.",
            data_dir=DATA_DIR,
            title="Mueble lateral estrecho",
            summary="Hueco útil para cocina portátil.",
            additional_content="Revisar si admite mesa extraíble para comer dentro.",
        )
        extra_entry, _ = append_entry(
            project=project,
            category="ventilacion",
            content="Ventana abatible con mosquitera.",
            data_dir=DATA_DIR,
            title="Ventana lateral",
            summary="Opciones de apertura y sellado.",
        )

        # Test 1: búsqueda por palabra presente en el título
        title_search = search_entries(project, "plegable", DATA_DIR)
        assert len(title_search.matched_hits) == 1, "La búsqueda por título no devolvió una sola coincidencia"
        assert title_search.matched_hits[0].entry.entry_id == title_entry.entry_id
        assert any(match.field_name == "titulo" for match in title_search.matched_hits[0].matches)
        title_output = build_search_output(title_search)
        assert 'búsqueda "plegable": 1 coincidencias' in title_output
        assert "coincidencia en titulo" in title_output

        # Test 2: búsqueda por palabra presente solo en el resumen
        summary_search = search_entries(project, "condensacion", DATA_DIR)
        assert len(summary_search.matched_hits) == 1, "La búsqueda por resumen no devolvió una sola coincidencia"
        assert summary_search.matched_hits[0].entry.entry_id == summary_entry.entry_id
        assert any(match.field_name == "resumen" for match in summary_search.matched_hits[0].matches)

        # Test 3: búsqueda por palabra presente en tags
        tags_search = search_entries(project, "solar", DATA_DIR)
        assert len(tags_search.matched_hits) == 1, "La búsqueda por tags no devolvió una sola coincidencia"
        assert tags_search.matched_hits[0].entry.entry_id == tags_entry.entry_id
        assert any(match.field_name == "tags" for match in tags_search.matched_hits[0].matches)

        # Test 4: búsqueda por contenido adicional
        additional_search = search_entries(project, "extraible", DATA_DIR)
        assert len(additional_search.matched_hits) == 1, "La búsqueda por contenido adicional no devolvió una sola coincidencia"
        assert additional_search.matched_hits[0].entry.entry_id == note_entry.entry_id
        assert any(match.field_name == "contenido_adicional" for match in additional_search.matched_hits[0].matches)

        # Test 5: búsqueda inexistente devuelve cero resultados sin error
        empty_search = search_entries(project, "homologacion-francesa", DATA_DIR)
        assert len(empty_search.matched_hits) == 0, "La búsqueda inexistente no devolvió cero resultados"
        empty_output = build_search_output(empty_search)
        assert "No se encontraron coincidencias." in empty_output

        # Test 6: se puede mostrar la entrada completa por id después de buscar
        entry_lookup = get_entry_by_id(project, title_entry.entry_id, DATA_DIR)
        assert entry_lookup.entry is not None, "No se encontró la entrada por id"
        full_output = build_entry_output(entry_lookup)
        assert f"ID: {title_entry.entry_id}" in full_output
        assert "Título: Cama plegable con guías laterales" in full_output

        # Regresión Fase 1: guardar sigue funcionando
        regression_entry, _ = append_entry(
            project=project,
            category="agua",
            content="Depósito interior de 50 litros.",
            data_dir=DATA_DIR,
        )
        assert regression_entry.entry_id.startswith("entry-")

        # Regresión Fase 2: listado sigue funcionando
        listing = list_entries(project, DATA_DIR)
        assert listing.total_entries == 6, "El listado global dejó de contar correctamente las entradas"
        listing_output = build_output(listing)
        assert "Proyecto phase4-test: 6 entradas válidas." in listing_output

        # Regresión Fase 2: filtrado por categoría sigue funcionando
        category_listing = list_entries(project, DATA_DIR, category="Electricidad")
        assert len(category_listing.matched_entries) == 1, "El filtrado por categoría dejó de funcionar"
        assert category_listing.matched_entries[0].entry_id == tags_entry.entry_id

        # Regresión Fase 3: campos estructurados opcionales siguen accesibles
        solar_lookup = get_entry_by_id(project, tags_entry.entry_id, DATA_DIR)
        assert solar_lookup.entry is not None
        assert solar_lookup.entry.tags == ["solar", "bateria", "12v"]
        assert solar_lookup.entry.contenido_adicional is None

        print("OK: fase 4 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
