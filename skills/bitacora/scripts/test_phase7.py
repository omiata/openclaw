#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase7"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import list_entries, load_entries, search_entries  # noqa: E402
from save_entry import migrate_project_file, split_entry_blocks  # noqa: E402

OLD_CAMPER_CONTENT = """---entry---

---
id: \"entry-1775744296910\"
fecha: \"2026-04-09T14:18:16.909Z\"
proyecto: \"camper\"
categoria: \"electricidad\"
tipo: \"video\"
titulo: \"I Built a Hidden Electrical System Under My Camper Bed\"
resumen: |-
  I Built a Hidden Electrical System Under My Camper Bed.
  Fuente: www.youtube.com.
  Relevante para camper/electricidad.
fuente: \"https://www.youtube.com/watch?v=e6q55k_MWQw\"
---

**Título**
I Built a Hidden Electrical System Under My Camper Bed

**Resumen**
I Built a Hidden Electrical System Under My Camper Bed.
Fuente: www.youtube.com.
Relevante para camper/electricidad.

**Fuente**
https://www.youtube.com/watch?v=e6q55k_MWQw

**Contenido**
https://www.youtube.com/watch?v=e6q55k_MWQw
---entry---

---
id: \"entry-1775744432909\"
fecha: \"2026-04-09T14:20:32.908Z\"
proyecto: \"camper\"
categoria: \"electricidad\"
tipo: \"video\"
titulo: \"DIY PreWiring my Camper Van Conversion as a Beginner\"
resumen: |-
  DIY PreWiring my Camper Van Conversion as a Beginner.
  Fuente: www.youtube.com.
  Relevante para camper/electricidad.
fuente: \"https://www.youtube.com/watch?v=7j23gGdmXzg\"
---

**Título**
DIY PreWiring my Camper Van Conversion as a Beginner

**Resumen**
DIY PreWiring my Camper Van Conversion as a Beginner.
Fuente: www.youtube.com.
Relevante para camper/electricidad.

**Fuente**
https://www.youtube.com/watch?v=7j23gGdmXzg

**Contenido**
https://www.youtube.com/watch?v=7j23gGdmXzg
---entry---

---
id: \"entry-1775744433057\"
fecha: \"2026-04-09T14:20:33.056Z\"
proyecto: \"camper\"
categoria: \"electricidad\"
tipo: \"video\"
titulo: \"Wiring Up My DIY Camper Van! (Crimping Wires & Powering Devices)\"
resumen: |-
  Wiring Up My DIY Camper Van! (Crimping Wires & Powering Devices).
  Fuente: www.youtube.com.
  Relevante para camper/electricidad.
fuente: \"https://www.youtube.com/watch?v=fgWb_PeHpW4\"
---

**Título**
Wiring Up My DIY Camper Van! (Crimping Wires & Powering Devices)

**Resumen**
Wiring Up My DIY Camper Van! (Crimping Wires & Powering Devices).
Fuente: www.youtube.com.
Relevante para camper/electricidad.

**Fuente**
https://www.youtube.com/watch?v=fgWb_PeHpW4

**Contenido**
https://www.youtube.com/watch?v=fgWb_PeHpW4
---entry---

---
id: \"entry-1775745506286\"
fecha: \"2026-04-09T14:38:26.286Z\"
proyecto: \"camper\"
categoria: \"general\"
tipo: \"video\"
titulo: \"Don't Waste Time and Money | 5 Campervan Build Mistakes\"
resumen: |-
  Don't Waste Time and Money | 5 Campervan Build Mistakes.
  Fuente: youtu.be.
  Relevante para camper/general.
fuente: \"https://youtu.be/Wyqv40KmNOk\"
---

**Título**
Don't Waste Time and Money | 5 Campervan Build Mistakes

**Resumen**
Don't Waste Time and Money | 5 Campervan Build Mistakes.
Fuente: youtu.be.
Relevante para camper/general.

**Fuente**
https://youtu.be/Wyqv40KmNOk

**Contenido**
https://youtu.be/Wyqv40KmNOk
"""

EXPECTED_FIELDS = {
    "entry-1775744296910": {
        "fecha": "2026-04-09T14:18:16.909Z",
        "proyecto": "camper",
        "categoria": "electricidad",
        "tipo": "video",
        "titulo": "I Built a Hidden Electrical System Under My Camper Bed",
        "resumen": "I Built a Hidden Electrical System Under My Camper Bed.\nFuente: www.youtube.com.\nRelevante para camper/electricidad.",
        "fuente": "https://www.youtube.com/watch?v=e6q55k_MWQw",
    },
    "entry-1775744432909": {
        "fecha": "2026-04-09T14:20:32.908Z",
        "proyecto": "camper",
        "categoria": "electricidad",
        "tipo": "video",
        "titulo": "DIY PreWiring my Camper Van Conversion as a Beginner",
        "resumen": "DIY PreWiring my Camper Van Conversion as a Beginner.\nFuente: www.youtube.com.\nRelevante para camper/electricidad.",
        "fuente": "https://www.youtube.com/watch?v=7j23gGdmXzg",
    },
    "entry-1775744433057": {
        "fecha": "2026-04-09T14:20:33.056Z",
        "proyecto": "camper",
        "categoria": "electricidad",
        "tipo": "video",
        "titulo": "Wiring Up My DIY Camper Van! (Crimping Wires & Powering Devices)",
        "resumen": "Wiring Up My DIY Camper Van! (Crimping Wires & Powering Devices).\nFuente: www.youtube.com.\nRelevante para camper/electricidad.",
        "fuente": "https://www.youtube.com/watch?v=fgWb_PeHpW4",
    },
    "entry-1775745506286": {
        "fecha": "2026-04-09T14:38:26.286Z",
        "proyecto": "camper",
        "categoria": "general",
        "tipo": "video",
        "titulo": "Don't Waste Time and Money | 5 Campervan Build Mistakes",
        "resumen": "Don't Waste Time and Money | 5 Campervan Build Mistakes.\nFuente: youtu.be.\nRelevante para camper/general.",
        "fuente": "https://youtu.be/Wyqv40KmNOk",
    },
}


def reset_workdir() -> Path:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    camper_path = DATA_DIR / "camper.md"
    camper_path.write_text(OLD_CAMPER_CONTENT, encoding="utf-8", newline="\n")
    return camper_path


def count_blocks(file_path: Path) -> int:
    return len(split_entry_blocks(file_path.read_text(encoding="utf-8")))


def assert_preserved_entries(entries) -> None:
    assert len(entries) == 4, "La migración no preservó las 4 entradas esperadas"
    by_id = {entry.entry_id: entry for entry in entries}
    assert set(by_id) == set(EXPECTED_FIELDS), "Los ids migrados no coinciden con los esperados"

    for entry_id, expected in EXPECTED_FIELDS.items():
        entry = by_id[entry_id]
        for field_name, expected_value in expected.items():
            actual_value = getattr(entry, field_name)
            assert actual_value == expected_value, f"Campo {field_name} distinto en {entry_id}: {actual_value!r} != {expected_value!r}"
        assert entry.calidad_resumen == "fallback", f"calidad_resumen incorrecta en {entry_id}"
        assert entry.estado == "nuevo", f"estado incorrecto en {entry_id}"
        assert entry.contenido_adicional in (None, ""), f"La nota personal migrada debería estar vacía en {entry_id}"


def main() -> int:
    try:
        # Test 1: migración de 4 entradas antiguas + backup obligatorio
        camper_path = reset_workdir()
        result = migrate_project_file("camper", DATA_DIR, create_backup=True)
        migrated_text = camper_path.read_text(encoding="utf-8")
        assert result.backup_path is not None and result.backup_path.exists(), "No se creó el backup obligatorio camper.md.bak"
        assert result.backup_path.read_text(encoding="utf-8") == OLD_CAMPER_CONTENT, "El backup no preserva el contenido original"
        assert camper_path.exists(), "camper.md desapareció tras la migración"
        assert count_blocks(camper_path) == 4, "El archivo migrado no contiene exactamente 4 bloques"
        assert "\r" not in migrated_text, "El archivo migrado contiene saltos CRLF"
        assert migrated_text.count("**Nota personal**") == 4, "No todas las entradas tienen bloque Nota personal"
        for legacy_marker in ("**Título**", "**Resumen**", "**Fuente**", "**Contenido**"):
            assert legacy_marker not in migrated_text, f"Sigue presente el marcador legacy {legacy_marker}"

        # Test 2: preservación campo a campo + nuevos defaults
        migrated_entries, warnings, _ = load_entries("camper", DATA_DIR)
        assert not warnings, f"La lectura tras migrar produjo avisos: {warnings}"
        assert_preserved_entries(migrated_entries)

        # Test 3: atomicidad si falla la escritura
        camper_path = reset_workdir()
        original_text = camper_path.read_text(encoding="utf-8")
        failure_seen = False
        try:
            migrate_project_file(
                "camper",
                DATA_DIR,
                create_backup=True,
                before_replace=lambda _temp_path: (_ for _ in ()).throw(RuntimeError("fallo inducido antes del replace")),
            )
        except RuntimeError as exc:
            failure_seen = True
            assert "fallo inducido" in str(exc)
        assert failure_seen, "La prueba de atomicidad no llegó a fallar"
        assert camper_path.read_text(encoding="utf-8") == original_text, "La escritura atómica alteró el original pese al fallo"
        assert camper_path.with_name("camper.md.bak").exists(), "El backup debe existir aunque falle el replace"

        # Test 4: lectura posterior tras migración + regresión mínima
        reset_workdir()
        migrate_project_file("camper", DATA_DIR, create_backup=True)
        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 4, "El listado global dejó de contar correctamente tras migrar"
        filtered = list_entries("camper", DATA_DIR, category="Electricidad")
        assert len(filtered.matched_entries) == 3, "El filtrado por categoría dejó de funcionar tras migrar"
        search = search_entries("camper", "money", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de encontrar entradas existentes tras migrar"
        assert search.matched_hits[0].entry.entry_id == "entry-1775745506286"

        print("OK: fase 7 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
