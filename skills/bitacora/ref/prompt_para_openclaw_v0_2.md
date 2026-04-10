# Prompt para OpenClaw: implementar skill bitacora (v0.2 — Trabajo por Bloques)

> Los principios de diseño que dan forma a este prompt están documentados en:
> `skills/meta/PROMPT_ENGINEERING.md` y `skills/meta/AGENTIC_PROMPTING.md`
> Ver `skills/meta/WORKFLOW.md` para el proceso completo.

Usa este prompt una vez por **BLOQUE**. Sustituye únicamente el número de bloque en el `PASO 2` en cada sesión nueva.

---

## Prompt base (copiar y pegar en OpenClaw, cambiando el PASO 2)

```text
Tienes que implementar la versión 0.2 de la skill bitacora.
Estaremos trabajando por BLOQUES lógicos consecutivos.

Los documentos de referencia v0.2 están en:
/mnt/c/omi/openclaw/skills/bitacora/ref/

PASO 1 — Lee estos tres archivos ANTES de hacer absolutamente nada más.
Considéralos tu única fuente de verdad durante toda la sesión:
- bitacora_reglas.md  ← léelo primero. Son restricciones obligatorias.
- bitacora_fases.md
- bitacora_maestro.md

PASO 2 — Implementa únicamente el Bloque 1.
Busca su definición en bitacora_fases.md, bajo la sección
"Agrupación de fases por bloques (Scope y Seguridad)".
- Ejecuta las fases del bloque en orden.
- Respeta estrictamente el SCOPE de archivos definido para el bloque.
- Aplica el criterio de BACKUP indicado.
- Asegúrate de pasar todos los tests listados en la fase. 
En caso de conflicto entre lo más cómodo y las reglas, ganan las reglas.

PASO 3 — Reglas de ejecución:
1. No necesito ver tu razonamiento interno. Loguea tu progreso al terminar cada subpaso con el formato [ESTADO] (fase, subpaso, decisión, siguiente paso...).
2. Si pasan 2 min sin avance real no sigas explorando en silencio: para, resume, propón 2 opciones.
3. Máximo 2 intentos por bloqueo/test fallido. Si tras 2 intentos distintos no se resuelve: para y reporta.

PASO 4 — Cierre del bloque:
Cuando todas las fases del bloque pasen todos sus tests (ver Regla 24):
1. Imprímeme un reporte estructurado final (formato Apéndice A.6 de fases).
2. Añade ese mismo reporte haciendo append al log: bitacora_log.md
3. Añade una entrada al changelog: bitacora_changelog.md
```

---

## Instrucciones de uso

1. Abre una sesión nueva (`/new`)
2. Ajusta el parámetro de *Thinking* en el modelo basándote en la recomendación que hace el bloque en el archivo `_fases.md`.
3. Copia el prompt de arriba.
4. Si vas a hacer el Bloque 1, envíalo tal cual. Si vas a hacer los siguientes, cambia solamente número en `PASO 2 — Implementa únicamente el Bloque [X].` 
