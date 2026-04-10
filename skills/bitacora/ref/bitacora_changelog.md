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
