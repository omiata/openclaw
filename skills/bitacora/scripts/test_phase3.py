#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase3"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_output, list_entries, load_entries  # noqa: E402
from save_entry import ENTRY_DELIMITER, append_entry  # noqa: E402


def split_entries(content: str) -> list[str]:
    return [part.strip() for part in content.split(ENTRY_DELIMITER) if part.strip()]


def extract_yaml_block(block: str) -> dict:
    lines = block.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError("El bloque no empieza con frontmatter YAML")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise AssertionError("No se encontró cierre del frontmatter YAML")

    yaml_text = "\n".join(lines[1:end_index])
    parsed = yaml.safe_load(yaml_text)
    if not isinstance(parsed, dict):
        raise AssertionError("El YAML no se parseó como mapa")
    return parsed


def write_legacy_entry(file_path: Path) -> None:
    legacy_content = """---entry---

---
id: \"entry-1111111111111\"
fecha: \"2026-04-08T21:15:30.123Z\"
proyecto: \"phase3-test\"
categoria: \"aislamiento\"
tipo: \"nota\"
titulo: \"Panel XPS para suelo y paredes\"
resumen: \"Entrada mínima heredada de la fase 1\"
---

**Título**
Panel XPS para suelo y paredes

**Resumen**
Entrada mínima heredada de la fase 1

**Contenido**
Panel XPS para suelo y paredes
"""
    file_path.write_text(legacy_content, encoding="utf-8", newline="\n")


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        project = "phase3-test"
        file_path = DATA_DIR / f"{project}.md"
        write_legacy_entry(file_path)

        # Test 1: leer una entrada antigua sin campos opcionales no produce error
        legacy_entries, legacy_warnings, legacy_path = load_entries(project, DATA_DIR)
        assert legacy_path == file_path
        assert len(legacy_warnings) == 0, f"La entrada heredada produjo avisos: {legacy_warnings}"
        assert len(legacy_entries) == 1, "La entrada heredada no se leyó correctamente"
        assert legacy_entries[0].entry_id == "entry-1111111111111"
        assert legacy_entries[0].fuente is None
        assert legacy_entries[0].tags == []
        assert legacy_entries[0].contenido_adicional is None

        # Test 2: guardar una entrada con todos los campos opcionales y verificar YAML
        new_entry, _ = append_entry(
            project=project,
            category="Iluminación",
            content="https://example.com/guia-luces-led-camper",
            data_dir=DATA_DIR,
            source="https://example.com/guia-luces-led-camper",
            tags=["led", "12v", "interior"],
            additional_content="Comparar tiras LED y focos empotrables para el techo.",
        )
        assert new_entry.tipo == "link", "La URL no se infirió como tipo link"
        assert new_entry.titulo, "No se generó título"
        assert new_entry.resumen, "No se generó resumen"

        blocks = split_entries(file_path.read_text(encoding="utf-8"))
        assert len(blocks) == 2, f"Se esperaban 2 bloques y hay {len(blocks)}"
        rich_yaml = extract_yaml_block(blocks[1])
        assert rich_yaml["id"] == new_entry.entry_id
        assert rich_yaml["categoria"] == "iluminacion"
        assert rich_yaml["tipo"] == "link"
        assert rich_yaml["fuente"] == "https://example.com/guia-luces-led-camper"
        assert rich_yaml["tags"] == ["led", "12v", "interior"]
        assert rich_yaml["contenido_adicional"] == "Comparar tiras LED y focos empotrables para el techo."
        assert isinstance(rich_yaml["titulo"], str) and rich_yaml["titulo"].strip()
        assert isinstance(rich_yaml["resumen"], str) and rich_yaml["resumen"].strip()

        # Regresión Fase 2: listado global sigue funcionando con entradas mixtas
        listing_all = list_entries(project, DATA_DIR)
        assert listing_all.total_entries == 2, "El listado global no devolvió las 2 entradas válidas"
        output_all = build_output(listing_all)
        assert "Proyecto phase3-test: 2 entradas válidas." in output_all

        # Regresión Fase 2: filtrado por categoría tolera variación obvia y solo devuelve la nueva
        listing_category = list_entries(project, DATA_DIR, category="Iluminación")
        assert listing_category.normalized_category == "iluminacion"
        assert len(listing_category.matched_entries) == 1, "El filtrado por categoría no devolvió una sola entrada"
        assert listing_category.matched_entries[0].entry_id == new_entry.entry_id

        print("OK: fase 3 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
