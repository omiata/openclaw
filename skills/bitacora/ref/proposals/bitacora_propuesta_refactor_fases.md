# Bitacora — Refactor de bitacora_fases.md (propuesta puntual)

Reducir `bitacora_fases.md` de 1.545 líneas a un documento operativo compacto que
un agente pueda consumir sin coste de contexto innecesario. Todo el historial
detallado se preserva en `ref/arc/`.

---

# PARTE I — Contenido propuesto para bitacora_maestro.md

[NINGÚN CAMBIO]

---

# PARTE II — Contenido propuesto para bitacora_reglas.md

[NINGÚN CAMBIO]

---

# PARTE III — Estructura propuesta para el nuevo bitacora_fases.md

El documento canónico pasa a tener cuatro secciones, nada más:

### §1 Cabecera de uso (conservada, compactada)
Cómo usar el documento, referencia a los archivos canónicos de apoyo y modo
autónomo vs asistido. Sin cambios funcionales, solo texto compacto.

### §2 Historial de fases completadas (tabla de una línea por fase)
Una única tabla Markdown:

| Fase | Nombre | Versión | Estado | Archivo de test |
|------|--------|---------|--------|-----------------|
| 0    | Preparación y decisiones de ruta      | v0.1 | ✅ | — |
| 1    | Guardado mínimo funcional             | v0.1 | ✅ | test_phase1.py |
| 2    | Lectura y listado básico              | v0.1 | ✅ | test_phase2.py |
| 3    | Campos estructurados completos        | v0.1 | ✅ | test_phase3.py (legacy) |
| 4    | Búsqueda textual sencilla             | v0.1 | ✅ | test_phase4.py |
| 5    | Duplicados básicos y pulido           | v0.1 | ✅ | test_phase5.py |
| 6    | Índices y mejoras secundarias         | v0.1 | ✅ | test_phase6.py |
| 7    | Migración al formato v0.2             | v0.2 | ✅ | test_phase7.py |
| 8    | Proyecto y categoría obligatorios     | v0.2 | ✅ | test_phase8.py |
| 9    | Metadata externa ligera               | v0.2 | ✅ | test_phase9.py |
| 10   | Resúmenes honestos y calidad_resumen  | v0.2 | ✅ | test_phase10.py |
| 11   | Confirmación limpia y salida humana   | v0.2 | ✅ | test_phase11.py |
| 12   | Etiquetas visibles y representación   | v0.2 | ✅ | test_phase12.py |
| 13   | Estados funcionales                   | v0.2 | ✅ | test_phase13.py |
| 14   | Vistas operativas                     | v0.2 | ✅ | test_phase14.py |
| 15   | Recordatorio diario programado        | v0.2 | ✅ | test_phase15.py |
| 16   | Paginación                            | v0.2 | ✅ | test_phase16.py |
| 17   | Enriquecimiento progresivo            | v0.2 | ✅ | test_phase17.py |
| 18   | Deduplicación inteligente             | v0.2 | ✅ | test_phase18.py |
| 19   | Upsert opt-in sobre duplicados        | v0.2 | ✅ | test_phase19.py |
| 20   | Edición de entradas                   | v0.2 | ✅ | test_phase20.py |
| 21   | Capa conversacional reforzada         | v0.2 | ✅ | test_phase21.py |
| 22   | Cierre y SKILL.md                     | v0.2 | ✅ | test_phase22.py |

> Historial completo con criterios de éxito, pruebas manuales y decisiones de
> salida: `ref/arc/bitacora_fases_v0_2_full.md`

### §3 Fixes y parches aplicados
Lista compacta de correcciones post-versión. Actualmente:

- **Parche v0.2a** — Fail fast en CLI para evitar descarte silencioso de
  `--content`, `--title`, `--type`, `--source` en modo `update`.
  Archivo: `scripts/save_entry.py`, función `main()`.

### §4 Próximas fases (v0.3+)
Sección vacía, lista para el siguiente ciclo de desarrollo.

---

# PARTE IV — Changelog previsto

- Refactor documental de `bitacora_fases.md`: de 1.545 líneas a ~80 líneas.
- Archivo `ref/arc/bitacora_fases_v0_2_full.md` creado con el contenido histórico
  completo preservado.

---

# Decisiones cerradas que incorpora esta propuesta

1. El historico de fases no necesita estar cargado en el contexto operativo. Los
   tests ejecutables en `scripts/tests/` son la fuente de verdad de regresión.
2. El documento de fases es, a partir de ahora, un backlog activo, no un diario
   de implementación.

---

# Conflictos detectados

- **`bitacora_fases_v0_2a_draft.md`** sigue existiendo en disco como artefacto
  del ciclo anterior. Debe eliminarse al promover este refactor para no confundir.

---

# Huecos abiertos

- Los nombres exactos de los archivos de test (`test_phase*.py`) deben verificarse
  contra los que existen realmente en `scripts/tests/` antes de escribir la tabla.
  Si alguno no existe, la celda se marca con `—`.
