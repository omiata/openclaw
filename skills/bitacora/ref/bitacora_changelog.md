# bitacora_changelog.md

## v0.2 - draft documental

**Estado:** pendiente de implementacion.
**Alcance de este archivo:** historico preliminar de decisiones y cambios previstos para la ronda documental v0.2. No sustituye aun a ningun archivo canonico.

### Cambios principales previstos
- nuevo formato de entrada con YAML como fuente de verdad y nota personal en Markdown
- nuevos campos `calidad_resumen` y `estado`
- migracion obligatoria de las 4 entradas antiguas de `camper.md` en la Fase 7
- proyecto siempre preguntado primero; no se infiere silenciosamente
- categoria obligatoria antes de guardar
- metadata externa ligera con timeout duro y fallback seguro
- resumenes honestos con clasificacion explicita de calidad
- salida humana por defecto y modo tecnico explicito
- estados funcionales y consultas por estado
- vistas de ultimas entradas y pendientes de enriquecer
- recordatorio diario a las 20:00 usando el mecanismo nativo de OpenClaw
- paginacion para navegacion larga
- enriquecimiento progresivo mediante nota personal y tags
- deduplicacion inteligente con canonicalizacion conservadora
- upsert opt-in sobre duplicados
- edicion de entradas con `fecha_actualizacion`
- refuerzo de la capa conversacional

### Decisiones cerradas incorporadas en esta ronda
- el sistema siempre pregunta primero por el proyecto
- las 4 entradas antiguas de `camper.md` se migran antes de cualquier mejora dependiente del nuevo esquema
- la salida visible al usuario es humana por defecto
- el modo tecnico solo aparece de forma explicita
- el recordatorio de pendientes de enriquecer se programa cada dia a las 20:00 y debe usar el mecanismo nativo de OpenClaw

### Cambios documentales preparados
- `bitacora_maestro_v0_2_draft.md`
- `bitacora_reglas_v0_2_draft.md`
- `bitacora_fases_v0_2_draft.md`
- `bitacora_changelog_v0_2_draft.md`

### Nota de estado
Esta version sigue en fase de revision documental. Los archivos canonicos actuales permanecen intactos hasta aprobacion expresa.

### 2026-04-10 15:54:32 CEST+0200 - Fase 7 completada
- implementada la migracion atómica de `camper.md` al formato v0.2
- creado backup obligatorio `skills/bitacora/data/camper.md.bak` antes de reescribir
- nuevo render de entrada con YAML como fuente de verdad y bloque Markdown `**Nota personal**`
- añadidos defaults `calidad_resumen: fallback` y `estado: nuevo` en las 4 entradas migradas
- mantenida compatibilidad de lectura para formato legacy y v0.2 en la transición
- materializados tests autónomos de migración, preservación de campos, atomicidad y regresión mínima de lectura, filtrado y búsqueda

### 2026-04-10 17:27:19 CEST+0200 - Bloque 2 completado (Fases 8, 9 y 10)
- añadido `capture_entry` para cerrar el flujo: si falta proyecto pregunta primero y si falta categoría no guarda, sino que propone opciones del proyecto
- añadidas sugerencias de categorías más usadas y categorías base conocidas por proyecto sin inferencia silenciosa del destino
- integrada extracción ligera de metadata externa con prioridad a oEmbed (YouTube/Vimeo), `og:title`, `og:description`, `meta description` y `<title>`
- fijado timeout duro de 3 segundos para metadata externa, con fallo seguro y guardado no bloqueante
- rehecha la lógica de títulos y resúmenes para priorizar resumen del usuario, luego metadata útil, luego texto libre útil y finalmente fallback honesto
- etiquetado consistente de `calidad_resumen` en `usuario`, `auto` y `fallback`, manteniendo `estado: nuevo` por defecto
- materializados y ejecutados `test_phase8.py`, `test_phase9.py` y `test_phase10.py`, además de regresión satisfactoria sobre `test_phase5.py`, `test_phase6.py` y `test_phase7.py`

### 2026-04-10 18:39:08 CEST+0200 - Bloque 3 completado (Fases 11 y 12)
- añadida salida humana por defecto en `save_entry.py` y `read_entries.py`, con `--technical` como vista técnica explícita
- limpiadas las confirmaciones visibles para ocultar rutas físicas, IDs y mensajes con tono de CLI
- humanizadas las fechas visibles en listados, búsquedas, vistas completas y resúmenes derivados
- ocultados los IDs en listados y búsquedas visibles, manteniendo la vista técnica detallada cuando se solicita
- añadida humanización visible de proyectos, categorías y tipos sin modificar las claves internas almacenadas en YAML
- materializados y ejecutados `test_phase11.py` y `test_phase12.py`, más regresión satisfactoria sobre `test_phase5.py`, `test_phase6.py`, `test_phase8.py` y `test_phase10.py`

### 2026-04-10 19:25:18 CEST+0200 - Bloque 4 completado (Fases 13, 14, 15 y 17)
- añadido soporte de estados funcionales en `save_entry.py` y `read_entries.py`, con actualización atómica de estado y listados filtrados por `nuevo`, `revisado` y `descartado`
- añadidas vistas operativas de últimas entradas, entradas por `calidad_resumen` y pendientes de enriquecer, con salida humana orientada a reenganchar al usuario
- materializada la configuración nativa del recordatorio diario de OpenClaw mediante `build_daily_enrichment_reminder_job()` y la previsualización del mensaje con `build_enrichment_reminder()`
- ampliado el enriquecimiento de entradas existentes para acumular nota personal, fusionar tags sin duplicados y subir `calidad_resumen` a `usuario` cuando una entrada `fallback` se enriquece
- añadidos y ejecutados `test_phase13.py`, `test_phase14.py`, `test_phase15.py` y `test_phase17.py`, más regresión satisfactoria sobre `test_phase1.py`, `test_phase2.py` y `test_phase4.py` a `test_phase12.py`

### 2026-04-10 19:50:19 CEST+0200 - Bloque 5 completado (Fases 16, 18, 19 y 20)
- añadida paginación simple con `offset` en listados, búsquedas y vistas operativas, mostrando tramos claros y pista conversacional para pedir "más" o "siguiente página"
- incorporada canonicalización conservadora de URLs para deduplicación inteligente, cubriendo YouTube corto/largo, `trailing slash` y parámetros irrelevantes sin sobreagrupar URLs con query significativa
- implementado upsert opt-in sobre duplicados, con oferta explícita de fusión y ampliación segura de la nota personal sin crear una entrada nueva
- añadida edición completa de entradas para `categoria`, `tipo`, `titulo` y `fuente`, con `fecha_actualizacion`, preservación de `id` y `fecha`, y soporte de movimiento entre proyectos mediante reescritura atómica
- reforzada la compatibilidad del formato almacenando `contenido_adicional` también en YAML y corrigiendo los códigos de salida CLI en flujos con proyecto o categoría ausentes
- añadidos y ejecutados `test_phase16.py`, `test_phase18.py`, `test_phase19.py` y `test_phase20.py`, más regresión completa satisfactoria sobre `test_phase1.py` a `test_phase20.py`
