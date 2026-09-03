# PROPOSAL_METHODOLOGY.md
# Cómo elaborar una propuesta de iteración para una skill

Este documento describe el proceso para preparar una propuesta sólida antes de
iniciar una nueva iteración de desarrollo en una skill de este workspace.

Una propuesta bien hecha es el paso anterior a tocar cualquier documento canónico.
Sin ella, las decisiones se toman ad-hoc durante la implementación y se pierde
coherencia entre iteraciones.

**Referencia empírica:** este proceso consolidó la propuesta de bitacora v0.2
(`skills/bitacora/ref/proposals/bitacora_propuesta_v0_2.md`).

---

## El flujo completo de una propuesta

```
1. Leer los canónicos actuales
       ↓
2. Identificar decisiones ya cerradas
       ↓
3. Redactar el pack de propuesta (en un archivo en /proposals/)
       ↓
4. Generar la Matriz de Cambios (PASO A) — SIN TOCAR NADA AÚN
       ↓
5. Revisión humana y confirmación de la matriz
       ↓
6. Crear los archivos draft (PASO B)
       ↓
7. Documentar conflictos abiertos y huecos
       ↓
8. Aprobación final → los drafts sustituyen los canónicos
```

---

## Paso 1. Leer los canónicos en orden

Antes de proponer cualquier cambio, el agente (o el humano) debe leer en este orden:

1. `bitacora_maestro.md` — visión funcional y decisiones de diseño
2. `bitacora_reglas.md` — restricciones técnicas obligatorias
3. `bitacora_fases.md` — plan de implementación por fases
4. `bitacora_changelog.md` — historial de iteraciones anteriores (si existe)

Si existe un documento de propuesta previo (`/proposals/`), leerlo también.

**Por qué este orden:** el maestro define qué es el sistema. Las reglas definen qué
no se puede hacer. Las fases definen cómo se ha implementado hasta ahora. Sin ese
contexto, cualquier propuesta puede contradecir decisiones ya cerradas.

---

## Paso 2. Identificar decisiones ya cerradas

Antes de proponer nada, separar claramente:

- **Decisiones cerradas:** ya están en los canónicos y no se discuten. Solo se
  extienden o amplían si hay conflicto directo con algo nuevo.
- **Decisiones abiertas o en conversación:** puntos que el humano ha mencionado
  pero que no están todavía formalizados en los canónicos.
- **Decisiones nuevas que propone esta iteración:** lo que se quiere añadir.

Mezclar estas tres categorías es la fuente principal de confusión en las propuestas.

---

## Paso 3. El pack de propuesta — un solo archivo de revisión

La propuesta se redacta como un único archivo en `/proposals/` con este nombre:
```
[skill]_propuesta_v[X.Y].md
```

**Por qué un solo archivo:** evita pérdida de contexto y permite revisar de forma
integral antes de separar el contenido en los archivos canónicos definitivos.
El pack es el equivalente a un borrador que se revisa en conjunto antes de imprimir.

### Estructura del pack de propuesta

```
# [Skill] v[X.Y] — pack documental para revisión

[Descripción de la intención de esta iteración en 2-3 líneas]

---

# PARTE I — Contenido propuesto para [skill]_maestro.md

[Solo las secciones que cambian o son nuevas. Indicar cuáles se conservan intactas.]

---

# PARTE II — Contenido propuesto para [skill]_reglas.md

[Solo las reglas que cambian o son nuevas. Indicar cuáles se conservan intactas.]

---

# PARTE III — Contenido propuesto para [skill]_fases.md

[Fases nuevas completas. Las fases que se conservan: solo referenciadas, no copiadas.]

---

# PARTE IV — Changelog previsto

[Lista de cambios funcionales esperados para esta iteración.]

---

# Decisiones cerradas que incorpora esta propuesta

[Lista numerada de las decisiones ya tomadas que esta propuesta formaliza.]

---

# Conflictos detectados entre el estado actual y esta propuesta

[Lista de puntos en los que la propuesta choca con algo existente. Cada conflicto
debe tener una propuesta de resolución o quedar marcado como abierto.]

---

# Huecos abiertos

[Lo que esta propuesta no cierra y deberá decidirse antes o durante la implementación.]
```

---

## Paso 4. La Matriz de Cambios — PASO A

Antes de crear ningún draft, el agente genera la Matriz de Cambios y la presenta
al humano para revisión. **No toca ningún archivo hasta que el humano confirme.**

La matriz tiene este formato:

```markdown
## Archivo: [skill]_maestro.md
- Secciones que se conservan intactas: [lista]
- Secciones que se amplían: [lista + descripción del cambio]
- Secciones nuevas a añadir: [lista]

## Archivo: [skill]_reglas.md
- Reglas que se conservan intactas: [lista]
- Reglas que se modifican: [regla + descripción del cambio]
- Reglas nuevas a añadir: [lista]

## Archivo: [skill]_fases.md
- Fases que se conservan intactas: [rango]
- Fases nuevas que se añaden: [lista con nombres]
- Cambios en apéndices o política de ejecución autónoma: [descripción]

## Archivos draft que se van a crear
- [lista]

## Posibles conflictos detectados
- [lista]

## Correcciones o parches que se van a aplicar y dónde
- [lista]
```

**La Matriz de Cambios es necesaria porque:**
- Obliga a pensar antes de editar
- Da al humano visibilidad completa de lo que va a pasar
- Permite detectar errores antes de que el agente toque los documentos
- Es el contrato entre el humano y el agente para esa sesión

---

## Paso 5. Revisión humana y confirmación

El humano lee la matriz y puede:

- **Confirmar** → pasar al PASO B
- **Corregir** → devolver al agente con instrucciones de ajuste
- **Aportar aclaraciones** → complementar la propuesta con decisiones que el agente
  no ha podido deducir por sí solo

Solo se pasa al PASO B después de confirmación explícita.

---

## Paso 6. Crear los archivos draft — PASO B

El agente crea los drafts siguiendo la matriz confirmada. Los drafts se nombran:
```
[skill]_maestro_v[X.Y]_draft.md
[skill]_reglas_v[X.Y]_draft.md
[skill]_fases_v[X.Y]_draft.md
[skill]_changelog_v[X.Y]_draft.md
```

Reglas durante la creación de drafts:

- **Los archivos canónicos no se tocan.** Los drafts coexisten con ellos.
- Trabajar de forma **conservadora**: no redistribuir contenido libremente entre
  maestro, reglas y fases si no es necesario.
- Las fases ya implementadas en versiones anteriores se incluyen en el draft de fases
  pero marcadas visualmente como implementadas (ver `AGENTIC_PROMPTING.md` §3.3).
- Si hay un parche o correcciones sobre la propuesta, integrarlas directamente en los
  drafts. No dejarlas como archivo separado si ya han sido confirmadas.

---

## Paso 7. Documentar conflictos abiertos y huecos

Al final del PASO B, el agente entrega un reporte estructurado con:

```
## Archivos creados
[lista]

## Decisiones de diseño importantes tomadas durante la creación
[lista]

## Cambios principales por documento
- En maestro: [resumen]
- En reglas: [resumen]
- En fases: [resumen]

## Correcciones o parches aplicados
[lista]

## Huecos o conflictos que siguen abiertos
[lista — son los puntos que no se han podido cerrar y necesitan decisión humana]
```

---

## Paso 8. Aprobación y sustitución de canónicos

Los drafts **no sustituyen** los canónicos hasta revisión y aprobación explícita del
humano. Esta es una regla dura.

Cuando el humano aprueba, los canónicos se sustituyen por los drafts y los canónicos
anteriores se archivan en `/arc/` con sufijo de versión.

**Pasos de limpieza al promover un draft:**
1. Renombrar el archivo eliminando el sufijo `_v[X.Y]_draft`.
2. Abrir los archivos y actualizar cualquier mención a `_draft` en la cabecera (H1).
3. Asegurarse de que las referencias cruzadas dentro del archivo apunten a los nombres limpios (ej. apuntar a `_reglas.md` y no a `_reglas_draft.md`).

---

## Qué NO hacer en una propuesta

- No proponer cambios sin haber leído los canónicos actuales completos.
- No crear drafts antes de que el humano confirme la Matriz de Cambios.
- No redistribuir libremente el contenido entre maestro, reglas y fases.
- No integrar un parche o corrección sin indicar explícitamente dónde se aplica y por qué.
- No marcar como "decisión cerrada" algo que el humano no ha confirmado explícitamente.
- No dejar conflictos sin documentar — aunque no tengan resolución, deben aparecer en el reporte.
- No sustituir canónicos sin aprobación, aunque los drafts parezcan correctos.

---

## Localización de archivos de propuesta

```
skills/
  [skill]/
    ref/
      proposals/
        [skill]_propuesta_v[X.Y].md   ← pack de propuesta
      [skill]_maestro_v[X.Y]_draft.md ← drafts generados en PASO B
      [skill]_reglas_v[X.Y]_draft.md
      [skill]_fases_v[X.Y]_draft.md
      [skill]_changelog_v[X.Y]_draft.md
      arc/
        [skill]_maestro_v[X_Y-1].md  ← canónico anterior archivado
```

---

## Referencias

- `skills/bitacora/ref/proposals/bitacora_propuesta_v0_2.md` — ejemplo completo de pack de propuesta
- `skills/bitacora/ref/arc/bitacora_maestro_v0_1.md` — ejemplo de maestro anterior preservado
- `skills/bitacora/ref/bitacora_fases.md` — ejemplo del canónico activo actual
- `skills/meta/PLAN_METHODOLOGY.md` — cómo estructurar el plan documental (siguiente paso)
- `skills/meta/AGENTIC_PROMPTING.md` — principios de ejecución autónoma
