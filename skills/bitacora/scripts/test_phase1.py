#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase1"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

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


def assert_utf8_lf(file_path: Path) -> None:
    raw = file_path.read_bytes()
    raw.decode("utf-8")
    if b"\r" in raw:
        raise AssertionError("El archivo contiene CR o CRLF")


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        project = "phase1-test"
        file_path = DATA_DIR / f"{project}.md"

        # Test 1: crea archivo inexistente y guarda un único bloque
        entry1, path1 = append_entry(project, "aislamiento", "Panel XPS para suelo y paredes", DATA_DIR)
        assert path1 == file_path
        assert file_path.exists(), "No se creó el archivo del proyecto"

        content1 = file_path.read_text(encoding="utf-8")
        blocks1 = split_entries(content1)
        assert len(blocks1) == 1, f"Se esperaba 1 bloque y hay {len(blocks1)}"
        yaml1 = extract_yaml_block(blocks1[0])
        required_fields = {"id", "fecha", "proyecto", "categoria", "tipo", "titulo", "resumen"}
        assert required_fields.issubset(yaml1.keys()), "Faltan campos obligatorios en la entrada 1"
        assert yaml1["id"] == entry1.entry_id
        assert yaml1["proyecto"] == project
        assert yaml1["categoria"] == "aislamiento"

        # Test 2: lee el archivo existente, añade una segunda entrada y mantiene dos bloques
        before_second_write = file_path.read_text(encoding="utf-8")
        entry2, _ = append_entry(project, "electricidad", "https://example.com/esquema-12v", DATA_DIR)
        after_second_write = file_path.read_text(encoding="utf-8")
        assert after_second_write.startswith(before_second_write), "La segunda escritura no fue append al final"

        blocks2 = split_entries(after_second_write)
        assert len(blocks2) == 2, f"Se esperaban 2 bloques y hay {len(blocks2)}"
        yaml2_first = extract_yaml_block(blocks2[0])
        yaml2_second = extract_yaml_block(blocks2[1])
        assert yaml2_first["id"] == entry1.entry_id
        assert yaml2_second["id"] == entry2.entry_id
        assert yaml2_second["categoria"] == "electricidad"
        assert yaml2_second["tipo"] == "link"

        # Test 3: YAML parseable en todos los bloques
        for block in blocks2:
            parsed = extract_yaml_block(block)
            assert required_fields.issubset(parsed.keys()), "Un bloque no tiene todos los campos obligatorios"

        # Test 4: UTF-8 y LF
        assert_utf8_lf(file_path)

        print("OK: fase 1 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
