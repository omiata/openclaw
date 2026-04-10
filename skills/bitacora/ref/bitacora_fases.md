# bitacora_fases.md
# Plan de implementación por fases: skill bitacora

**Uso:** Este documento es el backlog activo de la skill bitacora. Las fases
completadas están resumidas en la tabla de historial. Los criterios de éxito,
pruebas manuales y decisiones de salida originales están archivados en:
`ref/arc/bitacora_fases_v0_2_full.md`

**Para implementar una fase nueva con OpenClaw:**
1. Lee `bitacora_maestro.md` y `bitacora_reglas.md` antes de empezar.
2. Copia únicamente la fase en curso a tu contexto — no este documento entero.
3. Implementa, valida con los tests, haz commit por unidad funcional.
4. Actualiza la tabla de historial y el changelog al cerrar.

**Documentos de referencia canónicos:**
- `bitacora_maestro.md` — visión funcional y decisiones de diseño
- `bitacora_reglas.md` — restricciones técnicas obligatorias
- `bitacora_changelog.md` — historial de cambios
- `bitacora_log.md` — log operativo de sesiones

**Workspace:** `c:\omi\openclaw\`

---

## Historial de fases completadas

| Fase | Nombre                                | Versión | Estado | Test                |
|------|---------------------------------------|---------|--------|---------------------|
| 0    | Preparación y decisiones de ruta      | v0.1    | ✅     | —                   |
| 1    | Guardado mínimo funcional             | v0.1    | ✅     | test_phase1.py      |
| 2    | Lectura y listado básico              | v0.1    | ✅     | test_phase2.py      |
| 3    | Campos estructurados completos        | v0.1    | ✅     | test_phase3.py      |
| 4    | Búsqueda textual sencilla             | v0.1    | ✅     | test_phase4.py      |
| 5    | Duplicados básicos y pulido           | v0.1    | ✅     | test_phase5.py      |
| 6    | Índices y mejoras secundarias         | v0.1    | ✅     | test_phase6.py      |
| 7    | Migración al formato v0.2             | v0.2    | ✅     | test_phase7.py      |
| 8    | Proyecto y categoría obligatorios     | v0.2    | ✅     | test_phase8.py      |
| 9    | Metadata externa ligera               | v0.2    | ✅     | test_phase9.py      |
| 10   | Resúmenes honestos y calidad_resumen  | v0.2    | ✅     | test_phase10.py     |
| 11   | Confirmación limpia y salida humana   | v0.2    | ✅     | test_phase11.py     |
| 12   | Etiquetas visibles y representación   | v0.2    | ✅     | test_phase12.py     |
| 13   | Estados funcionales                   | v0.2    | ✅     | test_phase13.py     |
| 14   | Vistas operativas                     | v0.2    | ✅     | test_phase14.py     |
| 15   | Recordatorio diario programado        | v0.2    | ✅     | test_phase15.py     |
| 16   | Paginación                            | v0.2    | ✅     | test_phase16.py     |
| 17   | Enriquecimiento progresivo            | v0.2    | ✅     | test_phase17.py     |
| 18   | Deduplicación inteligente             | v0.2    | ✅     | test_phase18.py     |
| 19   | Upsert opt-in sobre duplicados        | v0.2    | ✅     | test_phase19.py     |
| 20   | Edición de entradas                   | v0.2    | ✅     | test_phase20.py     |
| 21   | Capa conversacional reforzada         | v0.2    | ✅     | test_phase21.py     |
| 22   | Cierre y SKILL.md                     | v0.2    | ✅     | test_phase22.py     |

> Para ejecutar la suite de regresión completa:
> `python -m pytest scripts/test_phase*.py` desde el directorio de la skill.

---

## Parches y fixes

### Parche v0.2a — Fail fast CLI (2026-04-11)

**Problema:** El script retornaba éxito aunque `--content` o `--title` fueran
ignorados silenciosamente en modo `--update-entry-id`.

**Corrección:** En `scripts/save_entry.py`, función `main()`, al entrar en
`update_mode` se validan los argumentos `args.content`, `args.title`,
`args.resource_type` y `args.source`. Si alguno tiene valor, se lanza un
`ValueError` con mensaje explicativo y el script aborta (exit code 1).

**Regla asociada:** Regla 25 de `bitacora_reglas.md`.

---

## Próximas fases (v0.3+)

*Sin fases planificadas todavía.*
