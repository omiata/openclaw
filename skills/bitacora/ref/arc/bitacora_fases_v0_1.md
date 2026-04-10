# bitacora_fases.md
# Plan de implementación por fases: skill bitacora

**Uso:** Este es el documento operativo para trabajar con Codex o con OpenClaw. Cada sesión de implementación debe empezar con una sola fase. No dar este documento entero de una vez.

**Documentos de referencia:**
- `bitacora_maestro.md` — visión funcional y decisiones de diseño
- `bitacora_reglas.md` — restricciones técnicas obligatorias

**Workspace real:** `/mnt/c/omi/openclaw/`

---

## Cómo usar este documento

1. Abre una sesión con Codex o con OpenClaw.
2. Dale las Reglas de Oro (`bitacora_reglas.md`).
3. Dale únicamente la fase en curso, no el documento entero.
4. Implementa y valida.
5. Haz el commit correspondiente.
6. Solo entonces pasa a la siguiente fase.

**Modo autónomo (OpenClaw sin intervención del usuario):** las secciones de "Prueba manual" de cada fase describen la intención de verificación, pero en ejecución autónoma deben sustituirse por los tests ejecutables definidos en el Apéndice A.3. El agente no debe esperar confirmación humana para ejecutar los tests ni para pasar de fase si todos los tests pasan. Sí debe esperar confirmación humana en los casos listados en A.8.

**Modo asistido (con el usuario en el bucle):** las pruebas manuales pueden ejecutarse tal como están descritas, con el usuario verificando el resultado antes de confirmar el avance a la siguiente fase.

---

## Fase 0. Preparación y decisiones de ruta

### Objetivo
Dejar resuelto el punto de entrada, las rutas del sistema y verificar que el entorno funciona antes de escribir una sola línea de lógica.

### Tarea mínima
OpenClaw debe:

1. Examinar la estructura real de `/mnt/c/omi/openclaw/`.
2. Proponer y justificar la mejor ubicación para:
   - el código de la skill bitacora,
   - los archivos de datos por proyecto (los `.md`).
3. No asumir rutas genéricas. Basar la decisión en la estructura real del workspace.
4. Comprobar si ya existe un repositorio Git en algún directorio ancestro del workspace. Si existe, usarlo sin crear uno nuevo. Solo ejecutar `git init` si no hay ningún repo Git en ningún directorio padre.
5. Añadir al `.gitignore` existente (o crear uno nuevo si no existe) una regla acotada a la ruta concreta de datos decidida en este paso, por ejemplo `skills/bitacora/data/*.md`. No usar `*.md` como patrón global, ya que ignoraría también los archivos de referencia de la skill.
6. Crear el archivo de datos para el proyecto camper si no existe.
7. Verificar que puede leerlo si ya existe.

Nota: los archivos de referencia de la skill (`bitacora_maestro.md`, `bitacora_reglas.md`, `bitacora_fases.md`) ya han sido creados por Codex en `/mnt/c/omi/openclaw/skills/bitacora/ref/`. No hace falta crearlos de nuevo.

### Criterio de éxito
- Las rutas están decididas y documentadas.
- El directorio de código tiene git inicializado.
- El archivo `camper.md` puede crearse si no existe y leerse si ya existe.
- No se ha roto nada en el workspace.

### Prueba manual
- Verificar que el archivo `camper.md` existe en la ruta decidida.
- Abrirlo manualmente y comprobar que está vacío o tiene contenido previo intacto.
- El `.gitignore` tiene una regla acotada a la ruta de datos, sin ignorar los archivos de referencia de la skill.

### Prueba de regresión
No aplica en esta fase (es la primera).

### Riesgos
- Rutas incorrectas que rompan otras partes de OpenClaw.
- Olvidar el caso de archivo inexistente.

### Decisión de salida
Las rutas están fijadas y documentadas. El entorno está listo. Se puede pasar a la Fase 1.

---

## Fase 1. Guardado mínimo funcional

### Objetivo
Poder guardar una entrada muy simple con los campos mínimos obligatorios.

### Tarea mínima
Implementar la función de guardado que:

1. Recibe: proyecto, categoría y contenido o recurso del usuario.
2. Genera un ID autónomo no secuencial (Unix timestamp de alta precisión).
3. Registra la fecha de creación.
4. Crea una entrada en formato híbrido (YAML + Markdown) con los campos mínimos:
   - `id`, `fecha`, `proyecto`, `categoria`, `tipo` (inferido o por defecto), `titulo`, `resumen`.
5. Separa la entrada con el delimitador `---entry---` seguido de línea en blanco.
6. Añade la entrada al **final del archivo** del proyecto mediante append seguro.
7. Confirma al usuario qué se ha guardado.

### Lo que todavía no hace falta
- Índices, metadatos globales ni cabeceras.
- Tags sofisticados.
- Deduplicación.
- Búsqueda.

### Criterio de éxito
- El usuario manda algo y la entrada aparece bien guardada en el archivo.
- El formato es estable y legible.
- Se puede repetir con dos o tres entradas seguidas sin problemas.
- El archivo sigue siendo válido UTF-8 LF.

### Prueba manual
1. Guardar una entrada con proyecto=camper, categoría=aislamiento.
2. Abrir el archivo y verificar que la entrada está al final, bien formada.
3. Guardar una segunda entrada con categoría=electricidad.
4. Verificar que ambas entradas están presentes y separadas por `---entry---`.

### Prueba de regresión
- El archivo del proyecto puede crearse si no existe (Fase 0).
- El archivo del proyecto puede leerse si ya existe (Fase 0).

### Riesgos
- Formato YAML malformado que rompa el parseo posterior.
- Delimitador incorrecto o inconsistente.
- Codificación incorrecta si el sistema corre en Windows.

### Decisión de salida
Se pueden guardar entradas de forma fiable y repetible. El archivo resultante es legible manualmente. Se puede pasar a la Fase 2.

---

## Fase 2. Lectura y listado básico

### Objetivo
Poder recuperar lo guardado de forma útil.

### Tarea mínima
Implementar las funciones de lectura que permitan:

1. **Listar todo** lo guardado en un proyecto:
   - Indicar cuántas entradas hay en total.
   - Mostrar cada entrada en formato resumido (título, categoría, tipo, fecha, resumen).
   - No volcar el archivo completo si es muy largo.

2. **Filtrar por categoría**:
   - Aceptar categoría exacta.
   - Tolerar pequeñas variaciones obvias.
   - Mostrar cuántas entradas hay en esa categoría y luego las entradas.

### Criterio de éxito
- Las entradas guardadas se recuperan correctamente.
- El filtrado por categoría funciona.
- Los resultados no dependen del orden accidental del archivo.
- La salida es legible en Telegram.

### Prueba manual
1. Con al menos tres entradas guardadas de categorías distintas, pedir listar todo.
2. Verificar que aparecen todas.
3. Pedir filtrar por una categoría concreta.
4. Verificar que solo aparecen las entradas de esa categoría.
5. Probar con una variante menor de la categoría (ej. "Aislamiento" en mayúscula).

### Prueba de regresión
- Guardar una nueva entrada después de leer (Fase 1) y verificar que sigue funcionando.

### Riesgos
- Parseo frágil que falle ante entradas con texto largo en el Markdown libre.
- Filtrado que no tolere variaciones menores de categoría.

### Decisión de salida
Guardar y listar funcionan de forma fiable. Se puede pasar a la Fase 3.

---

## Fase 3. Campos estructurados completos

### Objetivo
Enriquecer el modelo de entrada sin romper lo anterior.

### Tarea mínima
Añadir soporte completo para todos los campos del modelo:

1. **Campos opcionales a soportar en escritura:**
   - `fuente` (URL o descripción del origen),
   - `tags` (lista opcional),
   - `contenido_adicional` (nota libre del usuario).

2. **Tipo de recurso explícito:**
   - Soportar los tipos: `link`, `video`, `documento`, `nota`, `idea`, `referencia`.
   - Si el usuario no lo especifica, inferir el más probable o usar `nota` por defecto.

3. **Título generado:**
   - Si el usuario no da título explícito, generarlo de forma breve y clara.
   - Si la fuente tiene un título bueno, reutilizarlo.

4. **Resumen generado:**
   - Entre una y tres líneas.
   - Capturar qué es, por qué es relevante y qué aspecto puede interesar al proyecto.

### Criterio de éxito
- Las nuevas entradas salen completas con todos los campos relevantes.
- Las entradas anteriores (más simples) siguen siendo legibles y recuperables.
- El sistema no exige rehacer entradas antiguas.

### Prueba manual
1. Guardar un link con URL, pedir que infiera el tipo y genere título y resumen.
2. Verificar que la entrada tiene `fuente`, `tipo: link`, título y resumen generados.
3. Guardar una idea sin URL con tags explícitos.
4. Verificar que los tags aparecen correctamente en el YAML.
5. Leer las entradas antiguas de Fase 1 y verificar que siguen funcionando.

### Prueba de regresión
- Listado global (Fase 2) sigue funcionando con las nuevas entradas.
- Filtrado por categoría (Fase 2) sigue funcionando.

### Riesgos
- Generación de títulos pobres o demasiado genéricos.
- Tags con formato inconsistente.
- Entradas antiguas con campos faltantes que rompan el parseo.

### Decisión de salida
El modelo de entrada está completo. Las entradas nuevas son ricas y las antiguas siguen siendo válidas. Se puede pasar a la Fase 4.

---

## Fase 4. Búsqueda textual sencilla

### Objetivo
Encontrar entradas sin depender solo de la categoría.

### Tarea mínima
Implementar una función de búsqueda que:

1. Busque texto en: título, resumen, tags y contenido adicional.
2. Devuelva coincidencias con un contexto corto.
3. Indique en qué campo ha encontrado la coincidencia.
4. Permita luego mostrar la entrada completa si el usuario lo pide.

No hace falta ranking sofisticado. Una búsqueda por coincidencia de texto simple es suficiente.

### Criterio de éxito
- Consultas simples devuelven coincidencias razonables.
- Los resultados son entendibles en Telegram.
- No se devuelven falsos positivos obvios.

### Prueba manual
1. Con al menos cinco entradas guardadas, buscar una palabra que aparezca en el título de una de ellas.
2. Buscar una palabra que solo aparezca en el resumen de otra.
3. Buscar una palabra que aparezca en tags.
4. Buscar algo que no existe y verificar que el sistema lo indica claramente.

### Prueba de regresión
- Guardar (Fase 1), listar (Fase 2) y filtrar por categoría (Fase 2) siguen funcionando.

### Riesgos
- Búsqueda demasiado literal que no tolere variaciones menores.
- Resultados demasiado largos que saturen el chat de Telegram.

### Decisión de salida
La búsqueda textual simple funciona de forma útil. Se puede pasar a la Fase 5.

---

## Fase 5. Duplicados básicos y pulido

### Objetivo
Evitar problemas obvios en uso real continuado.

### Tarea mínima

1. **Detección de duplicados por URL exacta:**
   - Si una entrada nueva trae una URL que ya existe en el archivo, detectarlo.
   - Avisar al usuario que ya existe esa URL.
   - No duplicar automáticamente.
   - Ofrecer actualizar tags, resumen o nota de la entrada existente si el usuario quiere.

2. **Mejora de mensajes:**
   - Mensajes de confirmación al guardar más claros.
   - Mensajes de error más informativos.
   - Mensajes de aviso ante ambigüedades de categoría.

### Criterio de éxito
- Una URL repetida no genera entrada duplicada.
- El usuario entiende qué ha pasado.
- El archivo sigue limpio después del intento de duplicado.

### Prueba manual
1. Guardar una entrada con una URL concreta.
2. Intentar guardar la misma URL de nuevo.
3. Verificar que el sistema avisa y no duplica.
4. Aceptar la oferta de actualizar la nota.
5. Verificar que la entrada original ahora tiene la nota actualizada.

### Prueba de regresión
- Guardar, listar, filtrar y buscar (Fases 1 a 4) siguen funcionando correctamente.

### Riesgos
- Comparación de URLs frágil ante pequeñas variaciones (http vs https, trailing slash...).
- Lógica de actualización que rompa la entrada existente.

### Decisión de salida
El sistema es robusto para uso real continuado. No genera duplicados accidentales. Se puede considerar la V1 completada o pasar a la Fase 6 si se quiere añadir comodidades.

---

## Fase 6. Índices y mejoras secundarias (opcional)

### Objetivo
Añadir comodidad de navegación, no funcionalidad crítica.

### Posible alcance
- Índice de categorías con número de entradas y última actualización.
- Índice de tipos de recurso presentes.
- Estadísticas simples: total de entradas, entradas por proyecto, categorías más usadas.
- Normalización mejorada de categorías con sugerencias automáticas.

### Regla crítica de esta fase
Cualquier índice o sección derivada debe recalcularse a partir del listado maestro de entradas, nunca al revés. La fuente única de verdad sigue siendo el listado de entradas.

### Criterio de éxito
- Las mejoras no rompen la fuente principal de verdad.
- Si alguna mejora falla, el sistema sigue pudiendo guardar y consultar entradas sin problemas.

### Prueba de regresión
- Guardar, listar, filtrar, buscar y deduplicar (Fases 1 a 5) siguen funcionando correctamente después de añadir cualquier mejora de esta fase.

### Decisión de salida
Las mejoras añaden valor real sin fragilizar el sistema base.

---

## Apéndice A. Política de ejecución autónoma

Esta sección define cómo debe comportarse OpenClaw cuando implementa y testea la skill de forma autónoma, sin intervención manual del usuario en cada paso.

Su objetivo es doble: maximizar la autonomía del agente y evitar loops de corrección que degraden el sistema en vez de mejorarlo.

---

### A.1 Principio general

OpenClaw debe tratar cada fase como una unidad de trabajo atómica con resultado binario: **la fase pasa o no pasa**. No existe un estado intermedio válido. Si la fase no pasa, el agente no avanza.

---

### A.2 Qué es un test válido

Un test válido para ejecución autónoma debe cumplir estas condiciones:

1. **Es ejecutable por el propio agente** sin intervención humana.
2. **Produce un resultado inequívoco**: pasa o falla. No produce "parece que funciona".
3. **Es reproducible**: ejecutarlo dos veces seguidas debe dar el mismo resultado.
4. **Verifica el estado real del archivo**, no solo que el código haya corrido sin errores.

Cada fase debe incluir al menos un test de este tipo antes de declararse completada. Las "pruebas manuales" descritas en cada fase deben traducirse a tests ejecutables equivalentes.

---

### A.3 Tests mínimos por fase

Cada fase debe implementar estos tests antes de declararse completada:

**Fase 0**
- Crear el archivo del proyecto si no existe y verificar que existe en disco.
- Leer el archivo si ya existe y verificar que el contenido no ha cambiado.
- Verificar que `.gitignore` contiene una regla acotada a la ruta de datos decidida en Fase 0 (por ejemplo `skills/bitacora/data/*.md`), no un patrón global `*.md`.

**Fase 1**
- Guardar una entrada mínima y verificar que el archivo contiene exactamente un bloque delimitado por `---entry---`.
- Guardar una segunda entrada y verificar que el archivo contiene exactamente dos bloques.
- Verificar que el YAML de cada bloque es parseable sin errores.
- Verificar que la codificación del archivo es UTF-8 y los saltos de línea son LF.

**Fase 2**
- Listar todo y verificar que el número de entradas devuelto coincide con el número real de bloques en el archivo.
- Filtrar por una categoría existente y verificar que solo se devuelven entradas de esa categoría.
- Filtrar por una categoría inexistente y verificar que el sistema devuelve cero resultados sin error.

**Fase 3**
- Guardar una entrada con todos los campos opcionales y verificar que cada campo aparece correctamente en el YAML.
- Leer una entrada antigua (sin campos opcionales) y verificar que no produce error de parseo.

**Fase 4**
- Buscar una palabra presente en el título de una entrada y verificar que esa entrada aparece en los resultados.
- Buscar una palabra que no existe en ninguna entrada y verificar que el sistema devuelve cero resultados sin error.

**Fase 5**
- Intentar guardar una URL ya existente y verificar que el archivo no ha ganado una nueva entrada.
- Guardar una URL nueva y verificar que sí se ha añadido correctamente.

---

### A.4 Política de reintentos

Cuando un test falla, el agente debe seguir esta política estrictamente:

1. **Primer fallo**: analizar el error, identificar la causa, aplicar una corrección concreta y volver a ejecutar el test.
2. **Segundo fallo consecutivo sobre el mismo test**: aplicar una segunda corrección distinta a la anterior y volver a ejecutar.
3. **Tercer fallo consecutivo sobre el mismo test**: **parar inmediatamente**. No intentar más correcciones. Reportar el estado según la política de reporte definida en A.6.

**Regla crítica**: cada corrección debe ser diferente a la anterior. Si el agente se encuentra repitiendo la misma corrección, debe parar antes de llegar al tercer intento.

---

### A.5 Política ante regresiones

Si al ejecutar los tests de regresión de una fase se detecta que algo que funcionaba en una fase anterior ha dejado de funcionar:

1. El agente debe **revertir los cambios de la fase actual** antes de hacer nada más.
2. Debe verificar que la regresión ha desaparecido tras el revert.
3. Debe reportar exactamente qué cambio introdujo la regresión.
4. **No debe intentar corregir la regresión y avanzar a la vez**. Primero se estabiliza el sistema, luego se replantea el enfoque.

Si el revert no es posible o no elimina la regresión, el agente debe parar y reportar.

---

### A.6 Política de reporte al terminar una fase

Al terminar cada fase, ya sea con éxito o con fallo, el agente debe:

1. Mostrar el reporte estructurado al usuario con exactamente estos campos:

```
FECHA: [fecha y hora exacta]
FASE: [número y nombre]
ESTADO: COMPLETADA | FALLIDA | BLOQUEADA
TESTS EJECUTADOS: [número]
TESTS PASADOS: [número]
TESTS FALLIDOS: [número]
REGRESIONES DETECTADAS: SÍ | NO
COMMIT REALIZADO: SÍ | NO | NO PROCEDE
DESCRIPCIÓN: [una o dos líneas explicando qué ha pasado]
ACCIÓN REQUERIDA: [solo si el estado no es COMPLETADA — qué necesita el usuario decidir o revisar]
```

2. Guardar ese mismo reporte en:
   `/mnt/c/omi/openclaw/skills/bitacora/ref/bitacora_log.md`
   - Si el archivo no existe, crearlo.
   - Si ya existe, añadir el nuevo reporte al final sin modificar las entradas anteriores.
   - Cada entrada debe empezar con la fecha y hora exacta.

Este reporte debe producirse siempre, incluso si la fase ha completado sin ningún problema. Es la señal que indica que la fase ha terminado y el sistema está en un estado conocido.

---

### A.7 Condiciones de parada automática

El agente debe parar de forma inmediata y reportar, sin intentar continuar, si ocurre cualquiera de estas condiciones:

1. Un test ha fallado tres veces consecutivas con correcciones distintas.
2. Se ha detectado una regresión que no desaparece tras revertir los cambios.
3. Una operación de escritura ha fallado y el archivo de datos podría estar en estado inconsistente.
4. El agente detecta que está a punto de modificar un campo inmutable (`id` o `fecha`) de una entrada existente.
5. El agente no puede determinar con certeza cuál es el estado actual del archivo antes de escribir.
6. Se ha producido el mismo error más de dos veces en la misma sesión, aunque sea en puntos distintos del código.

En todos estos casos, la acción correcta es: **parar, preservar el estado actual sin modificarlo más, y reportar**.

---

### A.8 Lo que el agente nunca debe hacer de forma autónoma

Independientemente del resultado de los tests, estas acciones requieren confirmación explícita del usuario y nunca deben tomarse de forma autónoma:

- Modificar o eliminar entradas existentes en un archivo de datos.
- Cambiar la estructura del formato de entrada de forma incompatible con entradas anteriores.
- Avanzar a una fase siguiente si la fase actual no ha pasado todos sus tests.
- Saltarse una fase aunque parezca trivial.
- Crear archivos de datos nuevos en rutas distintas a las decididas en la Fase 0.
- Modificar el `.gitignore` después de la Fase 0.

---

### A.9 Política de commits en ejecución autónoma

Los commits deben hacerse únicamente cuando:

1. La función implementada pasa todos sus tests.
2. Los tests de regresión de la fase actual también pasan.

No se debe hacer commit de código que no pase sus tests, aunque el código "parezca correcto". El historial de git debe reflejar solo estados verificados y funcionales.

Formato de mensaje obligatorio:
```
feat(bitacora): [descripción breve de lo implementado] — fase [N] tests OK
```

Ejemplo:
```
feat(bitacora): guardado básico con proyecto y categoría — fase 1 tests OK
```
