# AGENTIC_PROMPTING.md
# Política de ejecución autónoma y lecciones aprendidas

Este documento cubre dos cosas:
- **D. Política de runtime:** cómo se comporta el agente durante la ejecución.
- **E. Meta-lecciones:** lo que no se vuelve a hacer.

Para el flujo completo desde propuesta hasta ejecución, ver `skills/meta/WORKFLOW.md`.

---

## D. Política de ejecución autónoma

Esta sección es el Apéndice A generalizado, basado en `bitacora/ref/bitacora_fases.md`.
Aplica a cualquier agente autónomo que opere en este workspace.

### D.1 Cada unidad de trabajo es atómica — resultado binario

El agente trata cada fase/bloque como algo que **pasa o no pasa**.
No existe un estado intermedio válido. Si no pasa: no avanza.

### D.2 Definición formal de test válido

Un test es válido si cumple TODAS estas condiciones:

1. Es ejecutable por el agente sin intervención humana.
2. Produce resultado inequívoco: pasa o falla. No "parece que funciona".
3. Es reproducible: ejecutarlo dos veces da el mismo resultado.
4. Verifica el estado real del archivo en disco, no solo que el código haya corrido.
5. No puede pasar si el archivo no existe o está vacío.

**Lo que NO es un test válido — el agente debe tratarlo como fallo de fase:**
- `assert True`
- `assert len(x) >= 0`
- Cualquier comprobación que no pueda fallar
- Cualquier comprobación que no lea el archivo real después de la operación

**Límite de la autonomía (Testing NLP vs CLI):**
Los tests autónomos del agente deben enfocarse en la **capa técnica CLI y de datos**. El testeo end-to-end conversacional (asegurar que un intento en lenguaje natural se mapea correctamente al script) es propenso a alucinaciones de la IA. El agente valida los scripts; el humano valida la conversación NLP final.

### D.3 Política de reintentos ante fallos

1. **1er fallo:** analizar el error, corrección concreta, volver a ejecutar.
2. **2o fallo consecutivo en el mismo test:** corrección DISTINTA, volver a ejecutar.
3. **3er fallo consecutivo:** **parar inmediatamente**. Reportar. No más intentos.

Regla crítica: si el agente repite la misma corrección, parar antes del tercer intento.

### D.4 Política ante regresiones

Si algo que funcionaba deja de funcionar:

1. **Revertir los cambios de la unidad actual** antes de hacer nada más.
2. Verificar que la regresión desaparece tras el revert.
3. Reportar qué cambio introdujo la regresión.
4. **No corregir la regresión y avanzar a la vez.** Primero estabilizar, luego replantear.

Si el revert no elimina la regresión: parar y reportar.

### D.5 Formato de reporte obligatorio al terminar cada unidad

El agente reporta siempre — tanto si completa como si falla.
El reporte es la señal de que la unidad terminó y el sistema está en estado conocido.

```
FECHA: [fecha y hora exacta]
FASE: [número y nombre]
ESTADO: COMPLETADA | FALLIDA | BLOQUEADA
TESTS EJECUTADOS: [número]
TESTS PASADOS: [número]
TESTS FALLIDOS: [número]
REGRESIONES DETECTADAS: SÍ | NO
COMMIT REALIZADO: SÍ | NO | NO PROCEDE
DESCRIPCIÓN: [una o dos líneas]
ACCIÓN REQUERIDA: [solo si el estado no es COMPLETADA]
```

Este reporte se guarda también por append en el archivo de log de la skill.
**Mantenimiento del log:** Dado que el log crece indefinidamente (`append`), si supera las ~500 líneas perderá eficacia en el límite de contexto del LLM. Relegar entradas antiguas a un archivo `arc/[skill]_log_archivo.md` periódicamente.

### D.6 Condiciones de parada automática

El agente para y reporta inmediatamente si ocurre cualquiera de estas condiciones:

1. Un test ha fallado tres veces consecutivas con correcciones distintas.
2. Se detectó una regresión que no desaparece tras revertir.
3. Una operación de escritura ha fallado y el archivo podría estar en estado inconsistente.
4. El agente está a punto de modificar un campo declarado como inmutable en las reglas.
5. El agente no puede determinar con certeza el estado del archivo antes de escribir.
6. El mismo error ha ocurrido más de dos veces en la sesión, aunque sea en puntos distintos.

En todos estos casos: **parar, preservar el estado sin modificarlo más, reportar**.

### D.7 Lo que el agente NUNCA hace de forma autónoma

Estas acciones requieren confirmación explícita del usuario:

- Modificar o eliminar entradas existentes en archivos de datos.
- Cambiar el formato de manera incompatible con entradas anteriores.
- Avanzar a la siguiente fase si la actual no ha pasado todos sus tests.
- Saltarse una fase aunque parezca trivial.
- Crear archivos de datos en rutas no establecidas.
- Modificar el `.gitignore` tras la fase de configuración inicial.

### D.8 Política de commits

Los commits se hacen únicamente cuando:
1. La función implementada pasa todos sus tests.
2. Los tests de regresión de esa unidad también pasan.

No se hace commit de código que no pase sus tests, aunque "parezca correcto".

Formato orientativo:
```
feat([skill]): [descripción breve] — bloque [N] tests OK
```
**Frecuencia de commit:** El commit se realiza automáticamente al cerrar un **bloque** completo. Solo en la excepción de no existir bloques en el diseño, se permite el commit por unidad funcional/fase. Nunca se hace push automáticamente.

### D.9 Disciplina de debug

1. Aislar el camino que falla y compararlo con el que funciona antes de hacer cambios.
2. Antes de cambiar configuración, confirmar:
   - nombre exacto de la clave
   - valor permitido exacto
   - archivo exacto que controla el runtime
   - valor efectivo en runtime
3. Reportar los hallazgos antes de aplicar cambios.
4. No especular antes de hacer una prueba directa.
5. Si 5 acciones útiles no revelan una causa concreta: parar y reportar.
6. No repetir la misma acción más de 2 veces sin progreso.

---

## E. Meta-lecciones — lo que no se vuelve a hacer

### E.1 Las reglas críticas de seguridad van en el prompt Y en los documentos de referencia

Lo que está solo en el documento de reglas puede ser ignorado por el agente al
priorizar la instrucción explícita del prompt. Backup, atomicidad y scope deben
estar en ambos sitios.

### E.2 Los bloques del prompt deben estar definidos también en el documento de fases

Si el prompt habla de "Bloque 1" pero el documento de fases no tiene esa agrupación,
el agente no puede cruzar ambas fuentes correctamente.

### E.3 El nivel de Thinking va junto al bloque a copiar, no al final del documento

Si está en una tabla al final, el operador puede no llegar a leerla antes de abrir
la sesión. Debe estar visible en el bloque activo.

### E.4 El paso de cierre del prompt debe incluir log Y changelog explícitamente

El agente no lo infiere. Si no está en el prompt, no lo hace.

### E.5 La definición de test inválido es tan importante como la de test válido

Sin decirle al agente qué NO es un test válido, puede usar `assert True` y declararse
listo. Incluir siempre ejemplos negativos explícitos.

### E.6 Sesión nueva (`/new`) entre bloques — siempre

El contexto acumulado de intentos fallidos contamina los bloques siguientes.

### E.7 Fases ya implementadas deben marcarse visualmente en el documento

Sin marcado claro, el agente puede intentar reimplementarlas.

### E.8 No redistribuir contenido libremente entre maestro, reglas y fases

Cada documento tiene su rol. Mover contenido entre ellos crea inconsistencias y
hace que el agente reciba información duplicada o contradictoria.

### E.9 Auditar el prompt antes de lanzar — los tres vectores

Antes de lanzar un agente sobre datos reales, verificar:
1. **Atomicidad:** ¿El backup y el patrón `.tmp → rename` están en el prompt?
2. **Tests triviales:** ¿Está definido qué NO es un test válido?
3. **Scope:** ¿Hay lista ✅/❌ con archivos concretos?

---

## Checklist de verificación antes de lanzar un agente

- [ ] El prompt incluye instrucción explícita de backup (.bak y .tmp → rename)
- [ ] El prompt define qué NO es un test válido
- [ ] Los tests de la checklist están copiados del documento de fases
- [ ] El scope lista archivos permitidos/prohibidos con ✅/❌
- [ ] La agrupación en bloques existe también en el documento de fases
- [ ] Las fases ya implementadas están marcadas visualmente
- [ ] El nivel de Thinking está junto al bloque activo
- [ ] El paso de cierre incluye log Y changelog
- [ ] Se va a abrir sesión nueva (`/new`) antes de pegar el prompt
- [ ] Se han auditado los tres vectores de fallo

---

## Referencias

- `skills/meta/WORKFLOW.md` — índice maestro del proceso completo
- `skills/meta/PROPOSAL_METHODOLOGY.md` — cómo elaborar una propuesta (tipo A)
- `skills/meta/PLAN_METHODOLOGY.md` — cómo estructurar los documentos canónicos (tipo B)
- `skills/meta/PROMPT_ENGINEERING.md` — cómo preparar el prompt de ejecución (tipo C)
- `skills/bitacora/ref/bitacora_fases.md` — Apéndice A: fuente original de la política de runtime
- `skills/bitacora/ref/prompt_para_openclaw_v0_2.md` — prompt de referencia que aplica todo esto
