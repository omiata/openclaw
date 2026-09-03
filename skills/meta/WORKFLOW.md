# WORKFLOW.md
# Índice maestro: proceso completo de desarrollo de una skill

Este documento es el punto de entrada. Describe el proceso completo desde que
se quiere mejorar una skill hasta que el agente termina de implementarla.

---

## El proceso en cuatro etapas

```
A. PROPUESTA          B. PLAN DOCUMENTAL       C. EJECUCIÓN            D+E. RUNTIME
──────────────        ──────────────────        ────────────            ────────────
¿Qué queremos         ¿Cómo documentamos        ¿Cómo le damos          ¿Cómo se
cambiar y por qué?    los cambios?              las instrucciones       comporta el
                                                al agente?              agente?

PROPOSAL_             PLAN_                     PROMPT_                 AGENTIC_
METHODOLOGY.md        METHODOLOGY.md            ENGINEERING.md          PROMPTING.md
```

---

## Etapa A — Propuesta

**Documento:** `skills/meta/PROPOSAL_METHODOLOGY.md`

**Cuándo:** antes de tocar cualquier archivo canónico.

**Qué produce:**
- Un archivo en `/proposals/` con el pack de propuesta completo
- Una Matriz de Cambios (PASO A) revisada y confirmada por el humano
- Los archivos `*_draft.md` con los nuevos documentos canónicos (PASO B)

**Regla crítica:** los canónicos no se tocan hasta aprobación explícita.

---

## Etapa B — Plan documental

**Documento:** `skills/meta/PLAN_METHODOLOGY.md`

**Cuándo:** al estructurar o revisar los documentos maestro, reglas y fases
(tanto antes de una iteración como cuando se detecta que un documento canónico
tiene carencias).

**Qué cubre:**
- Qué va en el maestro vs en las reglas vs en las fases
- Estructura obligatoria de cada fase (dependencias, criterios, tests, risks...)
- Cómo agrupar fases en bloques para ejecución
- Naming conventions y gestión de versiones

---

## Etapa C — Preparar el prompt de ejecución

**Documento:** `skills/meta/PROMPT_ENGINEERING.md`

**Cuándo:** cuando los documentos de fases están listos y se va a dar tarea al agente.

**Qué cubre:**
- Estructura obligatoria del prompt (7 pasos)
- Los tres blindajes de seguridad (backup, tests válidos, scope)
- Cómo rellenar el bloque activo para cada sesión
- Thinking mode: cuándo usar Alto vs Medio
- La regla de `/new` entre bloques

**Regla crítica:** nunca dar el documento de fases completo como prompt.
Solo la fase o bloque activo.

---

## Etapa D+E — Ejecución y lecciones aprendidas

**Documento:** `skills/meta/AGENTIC_PROMPTING.md`

**Cuándo:**
- D: durante la ejecución — el agente consulta su política de comportamiento
- E: después de cada iteración — añadir nuevas lecciones aprendidas

**Qué cubre:**
- Política de ejecución (resultado binario, reintentos, regresiones, parada automática)
- Formato de reporte por fase
- Lo que el agente nunca hace de forma autónoma
- Política de commits
- Disciplina de debug
- Meta-lecciones: lo que no se vuelve a hacer

---

## Árbol de archivos de metodología

```
skills/
  meta/                              ← ESTE directorio (metodología del workspace)
    WORKFLOW.md                      ← índice maestro del proceso
    PROPOSAL_METHODOLOGY.md          ← etapa A: elaborar la propuesta
    PLAN_METHODOLOGY.md              ← etapa B: estructurar los documentos
    PROMPT_ENGINEERING.md            ← etapa C: preparar el prompt de ejecución
    AGENTIC_PROMPTING.md             ← etapa D+E: política de runtime y lecciones
    templates/
      proposal_template.md           ← plantilla reutilizable de propuesta
      prompt_template.md             ← plantilla reutilizable de prompt

  [skill]/
    ref/
      proposals/
        [skill]_propuesta_v[X.Y].md    ← pack de propuesta (etapa A)
      [skill]_maestro.md               ← canónico activo
      [skill]_reglas.md                ← canónico activo
      [skill]_fases.md                 ← canónico activo
      [skill]_maestro_v[X.Y]_draft.md  ← draft en revisión (etapa A paso B)
      [skill]_reglas_v[X.Y]_draft.md
      [skill]_fases_v[X.Y]_draft.md
      [skill]_changelog_v[X.Y]_draft.md
      [skill]_log.md                   ← log de ejecución (append, nunca borrar)
      prompt_para_[agent]_v[X.Y].md    ← prompt de ejecución (etapa C)
      arc/
        [skill]_maestro_v[X.Y-1].md   ← versiones anteriores archivadas
        prompt_para_[agent]_v[X.Y-1].md
```

---

## Flujo de decisión rápida

| Situación | Documento a consultar |
|-----------|----------------------|
| Quiero mejorar una skill — ¿por dónde empiezo? | `meta/PROPOSAL_METHODOLOGY.md` |
| ¿Qué va en el maestro vs las reglas? | `meta/PLAN_METHODOLOGY.md` |
| ¿Cómo escribo una fase con todos los campos? | `meta/PLAN_METHODOLOGY.md` |
| Tengo las fases listas — ¿cómo preparo el prompt? | `meta/PROMPT_ENGINEERING.md` |
| ¿Qué nivel de Thinking uso para este bloque? | `meta/PROMPT_ENGINEERING.md` |
| El agente ha fallado 3 veces — ¿qué hace? | `meta/AGENTIC_PROMPTING.md` §D.3 |
| ¿Puedo hacer commit si los tests pasan pero hay warnings? | `meta/AGENTIC_PROMPTING.md` §D.8 |
| Quiero añadir una lección aprendida nueva | `meta/AGENTIC_PROMPTING.md` sección E |

---

## Referencia: el proceso de bitacora v0.2

La primera iteración completa que siguió este flujo fue bitacora v0.2:

| Etapa | Artefacto producido |
|-------|---------------------|
| A — Propuesta | `bitacora/ref/proposals/bitacora_propuesta_v0_2.md` |
| A — Drafts | `bitacora/ref/bitacora_*_v0_2_draft.md` |
| C — Prompt | `bitacora/ref/prompt_para_openclaw_v0_2.md` |
| D — Runtime | extraído de `bitacora/ref/bitacora_fases.md` Apéndice A |
