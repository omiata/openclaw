# PROMPT_ENGINEERING.md
# Cómo preparar el prompt de ejecución para un agente autónomo

Este documento describe cómo construir el prompt que se le da a un agente autónomo para que implemente código basándose en el plan documental (maestro + reglas + fases).

**Prerequisito:** tener los documentos de fases bien estructurados (`PLAN_METHODOLOGY.md`).
**Evolución:** en versiones anteriores (v0.2 draft inicial) se recomendaba copiar todo el scope y las checklists dentro del prompt (Prompt Largo). Ahora, usamos el **Prompt Corto**, que delega esas responsabilidades a los archivos de referencia para evitar redundancia y mantener una "única fuente de la verdad".

---

## 1. Dónde viven "Los 3 Blindajes"

Antes de lanzar un prompt, el sistema debe estar protegido contra 3 fallos típicos del agente:

1. **Blindaje 1 (Atomicidad y Backup):** Vive en `[skill]_reglas.md` (y referenciado en el bloque de fases). Evita sobreescrituras corruptas.
2. **Blindaje 2 (Test Válido definido explícitamente):** Vive en `[skill]_reglas.md`. Prohíbe tests triviales como `assert True`.
3. **Blindaje 3 (Scope ✅/❌ explicitado):** Vive en `[skill]_fases.md`, en la sección que agrupa las fases por bloques.

**Si estos tres blindajes no están en los archivos de referencia, el agente fracasará.** El prompt asume que ya existen.

---

## 2. Estructura del Prompt de Ejecución (Prompt Corto)

El prompt es un bloque estático de texto donde solo cambia el número de Bloque en el PASO 2.

### PASO 1 — Lectura de documentos
Obliga al agente a cargar todo el contexto en el orden adecuado (las reglas restrictivas siempre primero).

```text
PASO 1 — Lee estos archivos ANTES de hacer absolutamente nada más.
Considéralos tu única fuente de verdad durante toda la sesión:
- [skill]_reglas.md  ← léelo primero. Son restricciones obligatorias.
- [skill]_fases.md
- [skill]_maestro.md
```

### PASO 2 — La unidad de trabajo (El bloque activo)
Solo cambia el número de bloque en cada sesión.

```text
PASO 2 — Implementa únicamente el Bloque [N].
Busca su definición en [skill]_fases.md, bajo la sección de Agrupación por bloques.
- Ejecuta las fases del bloque en orden.
- Respeta estrictamente el SCOPE de archivos definido para el bloque.
- Aplica el criterio de BACKUP indicado.
- Asegúrate de pasar todos los tests listados en la fase. 
En caso de conflicto entre lo más cómodo y las reglas, ganan las reglas.
```

### PASO 3 — Reglas de runtime
Evita que el agente se quede en bucles silenciosos o agote tokens intentando arreglar lo inarreglable.

```text
PASO 3 — Reglas de ejecución:
1. Log de progreso al terminar cada subpaso con el formato [ESTADO] (fase, subpaso, decisión, siguiente paso...).
2. Si pasan 2 min sin avance real no sigas explorando en silencio: para, resume, propón 2 opciones.
3. Máximo 2 intentos por bloqueo/test fallido. Si tras 2 intentos distintos no se resuelve: para y reporta.
```

### PASO 4 — Cierre
Asegura la trazabilidad obligando a actualizar los changelogs y logs.

```text
PASO 4 — Cierre del bloque:
Cuando todas las fases del bloque pasen todos sus tests (asegúrate de cumplir la regla de tests válidos):
1. Imprímeme un reporte estructurado final (formato Apéndice A.6 de fases).
2. Añade ese mismo reporte haciendo append al log: [skill]_log.md
3. Añade una entrada al changelog: [skill]_changelog.md
```

---

## 3. Preparación de la sesión de ejecución

### Cuándo usar Thinking Alto vs Medio

**Thinking Alto** se usa cuando la sesión implica:
- Reescritura, migración o parcheo de archivos de datos existentes (`.md`, `JSON`, etc).
- Interacciones con APIs complejas o integraciones nativas difíciles.
- Heurísticas que requieran evaluación (como resumir texto o parsear estructuras anidadas sueltas).

**Thinking Medio** se usa cuando la sesión implica:
- UI/Presentación y formateo.
- Scripting sencillo de filtros, parsing simple o lectura de datos sin escritura.

### La Sesión Limpia (`/new`)

**Siempre iniciar una sesión nueva (`/new`) de OpenClaw antes de cada bloque.**

El contexto acumulado de intentos fallidos, bugs intermedios y código viejo de un bloque "contamina" el razonamiento del agente para el bloque siguiente. Una sesión limpia garantiza que el agente parte fresca de los documentos de referencia canónicos.

---

## 4. Lista de comprobación antes de empezar la ejecución

- [ ] Las reglas incluyen la definición de Test Válido.
- [ ] Las reglas incluyen las normas de backup atómico.
- [ ] El documento de fases tiene definidos los SCOPES de cada bloque.
- [ ] El documento de fases detalla la lista exacta de tests a cumplir por fase.
- [ ] Vas a abrir una sesión `/new` antes de pegar el prompt.
- [ ] Has configurado el Thinking (Alto/Medio) correcto.

---

## Referencias

- `skills/bitacora/ref/prompt_para_openclaw_v0_2.md` — archivo de plantilla de prompt completo
- `skills/meta/AGENTIC_PROMPTING.md` — política profunda de comportamiento en runtime.
