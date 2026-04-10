#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase16"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_operational_view_output, build_output, list_entries, list_recent_entries  # noqa: E402
from save_entry import capture_entry  # noqa: E402


def pause() -> None:
    time.sleep(0.02)


def save_note(project: str, category: str, content: str) -> str:
    outcome = capture_entry(
        project=project,
        category=category,
        content=content,
        data_dir=DATA_DIR,
        human_output=True,
    )
    assert outcome.status == "saved"
    assert outcome.entry is not None
    return outcome.entry.titulo


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        titles: list[str] = []
        titles.append(save_note("camper", "electricidad", "Entrada uno para cuadro eléctrico."))
        pause()
        titles.append(save_note("camper", "agua", "Entrada dos para depósito auxiliar."))
        pause()
        titles.append(save_note("camper", "cama", "Entrada tres para cama plegable."))
        pause()
        titles.append(save_note("camper", "cocina", "Entrada cuatro para cocina lateral."))
        pause()
        titles.append(save_note("camper", "ventilacion", "Entrada cinco para claraboya."))
        pause()
        titles.append(save_note("camper", "aislamiento", "Entrada seis para paneles XPS."))

        newest_to_oldest = list(reversed(titles))

        # Test 1: offset básico en listados largos con pista conversacional
        listing = list_entries("camper", DATA_DIR)
        page_one = build_output(listing, max_entries=2, technical=False, offset=0)
        assert newest_to_oldest[0] in page_one and newest_to_oldest[1] in page_one
        assert newest_to_oldest[2] not in page_one
        assert "Te enseño las entradas 1 a 2 de 6 entradas." in page_one
        assert "más" in page_one and "siguiente página" in page_one

        page_two = build_output(listing, max_entries=2, technical=False, offset=2)
        assert newest_to_oldest[2] in page_two and newest_to_oldest[3] in page_two
        assert newest_to_oldest[0] not in page_two and newest_to_oldest[1] not in page_two
        assert "Te enseño las entradas 3 a 4 de 6 entradas." in page_two

        # Test 2: límites claros también en vistas operativas
        recent = list_recent_entries("camper", DATA_DIR, limit=6)
        recent_page = build_operational_view_output(recent, max_entries=2, technical=True, offset=4)
        assert newest_to_oldest[4] in recent_page and newest_to_oldest[5] in recent_page
        assert newest_to_oldest[3] not in recent_page
        assert "Mostrando entradas 5 a 6 de 6 entradas." in recent_page
        assert "--offset" not in recent_page.splitlines()[-1], "La última página no debe anunciar más páginas"

        # Test 3: fin de resultados cuando el offset ya se pasó
        beyond_end = build_output(listing, max_entries=2, technical=False, offset=20)
        assert "No he encontrado entradas para mostrar." in beyond_end
        assert "No hay más resultados. Ya has llegado al final." in beyond_end

        # Regresión mínima: listados pequeños siguen funcionando igual, sin contaminar la salida
        single_category = list_entries("camper", DATA_DIR, category="aislamiento")
        single_output = build_output(single_category, max_entries=5, technical=False)
        assert newest_to_oldest[0] in single_output
        assert "siguiente página" not in single_output
        assert "Te enseño las entradas" not in single_output

        print("OK: fase 16 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
