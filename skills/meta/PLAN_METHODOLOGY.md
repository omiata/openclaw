# PLAN_METHODOLOGY.md
# Cómo estructurar los documentos de referencia de una skill (maestro, reglas, fases)

Este documento describe cómo estructurar correctamente los tres documentos canónicos
que forman el núcleo documental de cualquier skill de este workspace.

Estos documentos son la fuente de verdad para el agente que implementa. Su calidad
determina directamente la calidad de la implementación.

**Prerequisito:** haber pasado por el proceso de propuesta (`PROPOSAL_METHODOLOGY.md`).

---

## Los tres documentos y su rol

| Documento | Pregunta que responde | Quién lo lee primero |
|-----------|----------------------|----------------------|
| `*_maestro.md` | ¿Qué es el sistema y qué problema resuelve? | El agente al inicio de cada sesión |
| `*_reglas.md` | ¿Qué está prohibido? ¿Qué es obligatorio? | El agente al inicio — restricciones que prevalecen |
| `*_fases.md` | ¿Cómo se implementa, en qué orden, con qué criterios? | El agente por fases, nunca el documento entero |
| `SKILL.md` | ¿Qué hace la skill y cómo se invoca desde LLM? | El enrutador central de OpenClaw |

**Regla de jerarquía:** cuando hay conflicto entre lo que parece conveniente y
una regla, gana la regla. Las reglas prevalecen sobre cualquier instrucción ad-hoc.

---

## El documento maestro

### Qué va en el maestro

- Propósito general y problema que resuelve
- Filosofía de diseño (principios, no reglas técnicas)
- Scope: qué está dentro, qué no
- Modelo de datos: campos, tipos, estructura conceptual
- Operaciones funcionales desde el punto de vista del usuario
- Convenciones de interacción
- Decisiones de diseño ya cerradas (numeradas)
- Escalabilidad futura prevista
- Cómo usar el documento (instrucciones de uso para el agente)

### Qué NO va en el maestro

- Implementación técnica (eso va en el código)
- Restricciones específicas (eso va en reglas)
- Plan de ejecución por fases (eso va en fases)
- Detalles de tests (eso va en fases)

### Tono y enfoque

El maestro habla de **qué hace el sistema y por qué**, no de cómo implementarlo.
Es el documento que un nuevo miembro del equipo leería para entender el sistema
antes de tocar una sola línea de código.

### Cómo evoluciona entre versiones

Al crear una nueva versión:
- Conservar intactas las secciones que no cambian
- Ampliar secciones existentes si hay nuevas decisiones de diseño
- Añadir secciones nuevas solo si no encajan en las existentes
- No redistribuir libremente el contenido existente

---

## El documento de reglas

### Qué va en las reglas

- Restricciones técnicas de obligado cumplimiento
- Formatos y estructuras inviolables (delimitadores, IDs, codificación)
- Campos inmutables
- Comportamiento ante errores (qué hace el sistema cuando algo falla)
- Política de escritura (append vs reescritura, atomicidad)
- Política de versionado y commits
- Restricciones de scope (qué puede y no puede hacer el agente)
- Restricciones operativas de la versión actual

### Qué NO va en las reglas

- Filosofía o motivación (eso va en el maestro)
- Plan de implementación (eso va en fases)
- Detalles de UX o interacción (eso va en el maestro)

### Tono y enfoque

Las reglas son **restricciones, no sugerencias**. Cada regla debe poder leerse como
"esto NUNCA se hace" o "esto SIEMPRE se hace". Si una regla dice "conviene hacer X",
no es una regla, es una recomendación y pertenece al maestro.

### Principio de mínimo cambio entre versiones

Conservar todas las reglas existentes salvo conflicto directo con decisiones ya
cerradas de la nueva versión. Solo añadir o ajustar reglas mínimas necesarias.
No reescribir reglas que siguen siendo válidas.

### Regla de uso en el prompt

El documento de reglas debe estar presente en CADA sesión de implementación.
Es el primer documento que el agente lee. Si una tarea propuesta entra en conflicto
con una regla, se revisa la tarea, no la regla.

---

## El documento de fases

### Qué va en las fases

El documento de fases es el **plan de ejecución operativo**. Cada fase representa
una unidad de trabajo atómica con resultado binario (pasa o no pasa).

**Estructura obligatoria de cada fase:**

```markdown
## Fase N. Nombre de la fase

### Dependencia bloqueante
[Si existe, cuál es. Si no existe, indicarlo explícitamente.]

### Objetivo
[Qué capacidad nueva deja el sistema al terminar esta fase. Una o dos líneas.]

### Qué toca implementar
[Lista concreta de lo que se va a hacer. Sin ambigüedad.]

### Qué NO toca todavía
[Lista explícita de lo que queda fuera de esta fase.]

### Criterio de éxito
[Cómo saber que la fase ha terminado bien. Sin "parece que funciona".]

### Prueba manual
[Pasos concretos que un humano puede hacer para verificar.]

### Prueba de regresión mínima
[Qué del trabajo anterior debe seguir funcionando.]

### Tests que el agente deberá materializar
[Lista de tests ejecutables. Son obligatorios, no sugerencias.]

### Riesgos
[Qué puede salir mal en esta fase concreta.]

### Decisión de salida
[La condición exacta que permite pasar a la siguiente fase.]
```

### Las fases deben tener dependencias explícitas

Las dependencias entre fases se declaran de dos formas:
1. **Mapa global** al inicio del bloque de fases — visión completa de la cadena
2. **Dependencia individual** en cada fase — explícita en texto, no implícita

Ejemplo de mapa global:
```
- Fase 7 → sin dependencia bloqueante previa
- Fase 8 → requiere Fase 7
- Fase 9 → requiere Fase 7
- Fase 14 → requiere Fases 7, 10 y 13
```

### Fases ya implementadas en versiones anteriores

Si el documento de fases incluye fases de versiones anteriores (para contexto de
regresión), deben marcarse visualmente como implementadas:

```markdown
> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla.
> Se mantiene solo como contexto y para verificar regresiones.
```

### Cómo se agrupa en bloques para ejecución

Las fases del documento se agrupan en **bloques lógicos** para facilitar la ejecución
autónoma. Esta agrupación se añade como sección en el documento de fases:

```markdown
## Organización por bloques

- Bloque 1: Fase N (base estructural crítica — siempre aislada)
- Bloque 2: Fases N+1, N+2, N+3 (captura y enriquecimiento)
- Bloque 3: Fases N+4, N+5 (salida y UX)
...
```

Criterios de agrupación:
- El primer bloque siempre es la fase más crítica, aislada
- Agrupar fases que comparten contexto técnico y tienen dependencias internas
- No hay bloques de más de 4-5 fases — el agente pierde foco

### La política de ejecución autónoma — Apéndice A

El documento de fases incluye un Apéndice A con la política completa de ejecución
autónoma. Esta política define:

- Principio de resultado binario (pasa/no pasa)
- Definición de test válido
- Tests mínimos por fase
- Política de reintentos (máximo 3, cada uno diferente)
- Política ante regresiones (revertir antes de corregir)
- Formato de reporte obligatorio
- Condiciones de parada automática
- Lo que el agente nunca hace de forma autónoma
- Política de commits

**Este apéndice NO se da al agente por completo en cada sesión.** Se referencia
desde el prompt, que extrae y hace explícitas las políticas más críticas.

Ver `skills/meta/AGENTIC_PROMPTING.md` para el contenido completo de estas políticas.

---

## Relación entre los tres documentos

```
maestro
  └── Define QUÉ y POR QUÉ
  └── Las reglas operativizan algunas decisiones del maestro

reglas
  └── Define RESTRICCIONES que prevalecen sobre todo
  └── Si hay conflicto reglas vs conveniencia → ganan las reglas

fases
  └── Define CÓMO y EN QUÉ ORDEN se implementa
  └── Cada fase respeta las reglas
  └── Cada fase avanza hacia el objetivo del maestro

SKILL.md
  └── Define la INTERFAZ PÚBLICA (API)
  └── Traduce el propósito (maestro) a comandos invocables (scripts)
```

**Las cuatro capas son necesarias.** Un sistema sin maestro no tiene visión. Un sistema
sin reglas no tiene restricciones. Un sistema sin fases no tiene plan. Un sistema sin `SKILL.md` está desconectado del usuario.

---

## El documento de interfaz (SKILL.md)

Este documento no guía la implementación interna de los Python/datos, sino que actúa como **contrato entre el router NLP de OpenClaw y la skill aislada**.

### Qué va en SKILL.md
- Nombre y descripción de 1 línea.
- Ejemplos claros de invocación en lenguaje natural (NL).
- Mapeo exacto entre comandos CLI disponibles (ej. `read_entries.py`) y qué casos de uso en NL resuelven.
- Estado actual funcional (qué fases están ya en producción).

### Qué NO va en SKILL.md
- Detalles del modelo de datos interno.
- Prompts.
- Reglas de desarrollo.

**Regla de actualización:** El `SKILL.md` **solo** se actualiza al final de una iteración o bloque, una vez que la nueva funcionalidad está completamente validada. Nunca se documenta funcionalidad "en proceso" en `SKILL.md`.

---

## Naming conventions

| Tipo de archivo | Nombre |
|----------------|--------|
| Canónico activo | `[skill]_maestro.md` |
| Draft en revisión | `[skill]_maestro_v[X.Y]_draft.md` |
| Archivado | `arc/[skill]_maestro_v[X_Y-1].md` |

---

## Qué NO hacer con estos documentos

- No dar el documento de fases completo al agente — solo la fase en curso.
- No mezclar instrucciones de implementación en el maestro.
- No poner filosofía o motivación en las reglas.
- No crear una fase sin los campos de dependencia, criterio de éxito y tests.
- No dejar dependencias implícitas — todas deben estar declaradas.
- No sustituir canónicos sin aprobación humana.

---

## Referencias

- `skills/bitacora/ref/bitacora_maestro.md` — ejemplo de maestro maduro
- `skills/bitacora/ref/bitacora_reglas.md` — ejemplo de reglas maduras
- `skills/bitacora/ref/bitacora_fases.md` — ejemplo de fases con Apéndice A completo
- `skills/bitacora/ref/bitacora_maestro.md` — ejemplo de maestro
- `skills/bitacora/ref/bitacora_fases.md` — ejemplo de fases v0.2 con bloques
- `skills/meta/PROPOSAL_METHODOLOGY.md` — cómo llegar a tener estos documentos
- `skills/meta/PROMPT_ENGINEERING.md` — cómo usar estos documentos para preparar el prompt de ejecución
- `skills/meta/AGENTIC_PROMPTING.md` — política de ejecución autónoma (Apéndice A generalizado)
