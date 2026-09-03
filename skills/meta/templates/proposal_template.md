# [Skill] v[X.Y] — pack documental para revisión

[Descripción de la intención de esta iteración en 2-3 líneas.
Qué problema resuelve esta versión. Por qué ahora.]

---

# PARTE I — Contenido propuesto para [skill]_maestro.md

[Indicar secciones que se conservan intactas. Solo incluir las que cambian o son nuevas.]

## Secciones que se conservan sin cambios
- [lista]

## Secciones que se amplían
### [Nombre de sección]
[Contenido nuevo o modificado]

## Secciones nuevas
### [Nombre de sección nueva]
[Contenido]

---

# PARTE II — Contenido propuesto para [skill]_reglas.md

## Reglas que se conservan sin cambios
- [lista de números de regla]

## Reglas que se modifican
### Regla [N]. [Nombre]
**Cambio:** [descripción del cambio]
[Contenido nuevo]

## Reglas nuevas que se añaden
### Regla [N+1]. [Nombre]
[Contenido]

---

# PARTE III — Contenido propuesto para [skill]_fases.md

## Fases que se conservan sin cambios
- Fases [rango] — ya implementadas, sin modificación

## Fases nuevas

### Fase [N]. [Nombre de la fase]

#### Dependencia bloqueante
[Si existe, cuál es. Si no existe: "No aplica."]

#### Objetivo
[Qué capacidad nueva deja el sistema al terminar esta fase.]

#### Qué toca implementar
1. [ítem concreto]
2. [ítem concreto]

#### Qué NO toca todavía
- [ítem]

#### Criterio de éxito
- [criterio medible]

#### Prueba manual
1. [paso]
2. [paso]

#### Prueba de regresión mínima
- [qué del trabajo anterior debe seguir funcionando]

#### Tests que el agente deberá materializar
- test de [descripción]
- test de [descripción]
- regresión de [descripción]

#### Riesgos
- [riesgo concreto]

#### Decisión de salida
[La condición exacta que permite pasar a la siguiente fase.]

---

## Organización por bloques (para el prompt de ejecución)

- Bloque 1: Fase [N] — [razón para aislar: p.ej. "base estructural crítica"]
- Bloque 2: Fases [N+1], [N+2] — [objetivo común]
- Bloque 3: Fases [N+3], [N+4] — [objetivo común]

---

# PARTE IV — Changelog previsto

## v[X.Y]

### Cambios previstos
- [cambio funcional 1]
- [cambio funcional 2]

---

# Decisiones cerradas que incorpora esta propuesta

1. [Decisión cerrada 1 — ya confirmada por el usuario]
2. [Decisión cerrada 2]

---

# Conflictos detectados entre el estado actual y esta propuesta

| Conflicto | Propuesta de resolución | Estado |
|-----------|------------------------|--------|
| [descripción] | [cómo resolverlo] | Abierto / Cerrado |

---

# Huecos abiertos — pendientes de decisión antes de implementar

- [hueco 1: descripción + por qué no se puede cerrar ahora]
- [hueco 2]

---

# Matriz de Cambios — PASO A (para confirmación humana antes del PASO B)

## [skill]_maestro.md
- Conservar intactas: [secciones]
- Ampliar: [secciones + descripción del cambio]
- Añadir nuevas: [secciones]

## [skill]_reglas.md
- Conservar intactas: [reglas]
- Modificar: [reglas + descripción del cambio]
- Añadir nuevas: [reglas]

## [skill]_fases.md
- Conservar intactas: [fases]
- Fases nuevas: [lista]
- Cambios en Apéndice A: [descripción o "ninguno"]

## Archivos draft que se van a crear
- [skill]_maestro_v[X.Y]_draft.md
- [skill]_reglas_v[X.Y]_draft.md
- [skill]_fases_v[X.Y]_draft.md
- [skill]_changelog_v[X.Y]_draft.md

## Correcciones/parches que se van a aplicar
- [descripción + en qué archivo]
