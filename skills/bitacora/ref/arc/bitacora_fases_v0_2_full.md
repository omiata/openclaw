# bitacora_fases.md
# Plan de implementacion por fases: skill bitacora

**Uso:** Este es el documento operativo para trabajar con Codex o con OpenClaw durante la preparacion e implementacion de v0.2. Cada sesion de implementacion debe empezar con una sola fase. No dar este documento entero de una vez.

**Documentos de referencia para esta ronda documental:**
- `bitacora_maestro_v0_2_draft.md` - vision funcional y decisiones de diseno
- `bitacora_reglas_v0_2_draft.md` - restricciones tecnicas obligatorias

**Workspace real:** `/mnt/c/omi/openclaw/`

---

## Como usar este documento

1. Abre una sesion con Codex o con OpenClaw.
2. Dale las Reglas de Oro (`bitacora_reglas_v0_2_draft.md`).
3. Dale unicamente la fase en curso, no el documento entero.
4. Implementa y valida.
5. Haz el commit correspondiente.
6. Solo entonces pasa a la siguiente fase.

**Modo autonomo (OpenClaw sin intervencion del usuario):** las secciones de "Prueba manual" de cada fase describen la intencion de verificacion, pero en ejecucion autonoma deben sustituirse por los tests ejecutables definidos en el Apendice A.3 o por los tests equivalentes definidos dentro de cada fase v0.2. El agente no debe esperar confirmacion humana para ejecutar los tests ni para pasar de fase si todos los tests pasan. Si debe esperar confirmacion humana en los casos listados en A.8.

**Modo asistido (con el usuario en el bucle):** las pruebas manuales pueden ejecutarse tal como estan descritas, con el usuario verificando el resultado antes de confirmar el avance a la siguiente fase.

---

## Fase 0. Preparación y decisiones de ruta

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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

> [!IMPORTANT]
> **ESTA FASE YA ESTÁ IMPLEMENTADA.** No debes volver a implementarla ni reescribirla. Se mantiene en este documento exclusivamente como contexto y para verificar que no se rompe nada al avanzar (tests de regresión).


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
## Organización del Desarrollo v0.2: Bloques y Fases

Para facilitar la implementación autónoma de la v0.2, las fases se han agrupado en bloques lógicos. El agente recibe instrucciones y ejecuta por bloque.

### Agrupación de fases por bloques (Scope y Seguridad)

**Bloque 1: Fase 7 (Migración al formato v0.2)**
- **SCOPE:** ✅ Archivos .py en `skills/bitacora/`. ✅ Archivo de datos `camper.md` (SOLO migración). ❌ `SKILL.md`, archivos en `ref/`, otros datos `.md`.
- **BACKUP:** OBLIGATORIO. Crear `camper.md.bak` antes de operar.
- **THINKING RECOMENDADO:** ALTO

**Bloque 2: Fases 8, 9 y 10 (Captura y enriquecimiento inicial)**
- **SCOPE:** ✅ Archivos .py en `skills/bitacora/`. ❌ Archivos .md directamente, `SKILL.md`, `ref/`.
- **BACKUP:** Solo si la lógica de upsert implica reescritura. (Regla Atomicidad).
- **THINKING RECOMENDADO:** ALTO

**Bloque 3: Fases 11 y 12 (Salida y representación humana)**
- **SCOPE:** ✅ Archivos .py en `skills/bitacora/` (lógica/presentación). ❌ Archivos .md directamente, `SKILL.md`, `ref/`.
- **BACKUP:** No requerido explícitamente ya que no escribe datos.
- **THINKING RECOMENDADO:** MEDIO

**Bloque 4: Fases 13, 14, 15 y 17 (Flujo operativo y recordatorio)**
- **SCOPE:** ✅ Archivos .py en `skills/bitacora/`. ✅ Configuración del scheduler OpenClaw (si existe, ver Fase 15). ❌ Archivos .md directamente, `SKILL.md`, `ref/`.
- **BACKUP:** Aplicar atomicidad si se cambian estados.
- **THINKING RECOMENDADO:** ALTO

**Bloque 5: Fases 16, 18, 19 y 20 (Escalado funcional)**
- **SCOPE:** ✅ Archivos .py en `skills/bitacora/`. ❌ Archivos .md directamente, `SKILL.md`, `ref/`.
- **BACKUP:** OBLIGATORIO (Atomicidad) ya que implica edición pesada (upsert, edit).
- **THINKING RECOMENDADO:** ALTO

**Bloque 6: Fases 21 y 22 (Modo técnico y cierre)**
- **SCOPE:** ✅ Archivos .py en `skills/bitacora/`. ✅ `SKILL.md` (solo estado real implementado). ❌ Archivos de datos o `ref/` sin aprobación.
- **BACKUP:** No reescribe entradas.
- **THINKING RECOMENDADO:** MEDIO

### Mapa explicito de dependencias entre fases nuevas

- Fase 7 -> sin dependencia bloqueante previa dentro de v0.2
- Fase 8 -> requiere Fase 7
- Fase 9 -> requiere Fase 7
- Fase 10 -> requiere Fase 7
- Fase 11 -> requiere Fase 10
- Fase 12 -> requiere Fase 11
- Fase 13 -> requiere Fase 7
- Fase 14 -> requiere Fase 10 y Fase 13, con Fase 7 ya completada como precondicion estructural
- Fase 15 -> requiere Fase 14 y verificacion previa del mecanismo nativo de tareas programadas de OpenClaw
- Fase 16 -> requiere Fase 11
- Fase 17 -> requiere Fase 10
- Fase 18 -> requiere Fase 9 y se apoya en la deduplicacion basica estable de la Fase 5
- Fase 19 -> requiere Fase 18
- Fase 20 -> requiere Fase 17
- Fase 21 -> requiere las fases funcionales previas ya estabilizadas, en especial Fases 8, 11, 13, 17, 19 y 20
- Fase 22 -> requiere el cierre satisfactorio de las Fases 7 a 21

### Bugfix Parche v0.2a
Integrar validación destructiva (fail fast) para prevenir comandos CLI erróneos que mezclan semántica de creación con semántica de actualización en `scripts/save_entry.py`.

---

## Fase 7. Migracion al formato v0.2

### Dependencia bloqueante

No aplica. Es la primera fase especifica de v0.2.

### Objetivo

Migrar la estructura de entradas al nuevo formato v0.2 sin perdida de datos y dejando el sistema preparado para las mejoras posteriores.

### Que toca implementar

1. Definir el nuevo render de entrada con:
   - YAML completo como fuente de verdad
   - bloque Markdown reservado a `Nota personal`
2. Anadir los campos nuevos:
   - `calidad_resumen`
   - `estado`
3. Implementar la migracion de las 4 entradas antiguas de `camper.md`.
4. Reescribir las entradas al nuevo formato de forma atomica.
5. Mantener compatibilidad de lectura durante la transicion.

### Que no toca todavia

- extraccion de metadata externa
- UX mejorada en Telegram
- estados como flujo de trabajo visible
- paginacion
- recordatorios

### Criterio de exito

- Las 4 entradas antiguas se migran sin perdida de datos.
- El archivo resultante queda en el formato nuevo.
- Las entradas siguen siendo parseables.
- El sistema sigue pudiendo leer el proyecto tras la migracion.

### Prueba manual

1. Ejecutar la migracion sobre `camper.md`.
2. Abrir el archivo resultante.
3. Verificar que cada entrada tiene:
   - delimitador correcto
   - YAML completo
   - `calidad_resumen`
   - `estado`
   - bloque `Nota personal`
4. Comprobar que no se ha perdido ninguna entrada.
5. Comprobar que el YAML de cada entrada sigue siendo legible.

### Prueba de regresion minima

- lectura global del proyecto sigue funcionando
- filtrado por categoria sigue funcionando
- busqueda sobre entradas existentes sigue funcionando

### Tests que OpenClaw debera materializar

- test de migracion de 4 entradas antiguas
- test de preservacion de numero de entradas
- test de preservacion de `id`, `fecha`, `proyecto`, `categoria`, `tipo`, `titulo`, `resumen`, `fuente`
- test de creacion de campos nuevos por defecto
- test de atomicidad si falla la escritura
- test de lectura posterior tras la migracion

### Riesgos

- perdida de informacion al eliminar redundancia antigua
- error al reinterpretar el Markdown previo
- reescritura parcial del archivo

### Decision de salida

La base ya esta en formato v0.2 y se puede pasar a las mejoras que dependen del nuevo esquema.

---

## Fase 8. Proyecto y categoria como flujo obligatorio de captura

### Dependencia bloqueante

Esta fase no puede iniciarse hasta que la Fase 7 (Migracion al formato v0.2) haya completado con exito y todas las entradas existentes esten en el nuevo formato. Si la Fase 7 no ha pasado todos sus tests, esta fase no debe empezar.

### Objetivo

Asegurar que el guardado siempre tiene proyecto y categoria de forma explicita y predecible.

### Que toca implementar

1. Si falta proyecto, preguntar primero por el proyecto.
2. Si falta categoria, preguntar por la categoria o proponer las mas usadas del proyecto.
3. No guardar una entrada sin proyecto.
4. No guardar una entrada sin categoria.
5. Ajustar `SKILL.md` y el flujo conversacional basico para reflejarlo.

### Que no toca todavia

- metadata externa
- resumenes mejorados
- estados funcionales visibles
- recordatorios

### Criterio de exito

- El sistema nunca guarda sin proyecto.
- El sistema nunca guarda sin categoria.
- El flujo conversacional es claro y predecible.

### Prueba manual

1. Intentar guardar una URL sin proyecto.
2. Verificar que el sistema pregunta primero por proyecto.
3. Responder con el proyecto, pero sin categoria.
4. Verificar que el sistema pide categoria o propone opciones.
5. Confirmar una categoria y guardar.
6. Verificar que la entrada solo se crea al final del flujo completo.

### Prueba de regresion minima

- guardado normal con proyecto y categoria ya dados sigue funcionando
- lectura, busqueda y deduplicacion basica siguen funcionando

### Tests que OpenClaw debera materializar

- test de faltante de proyecto con pregunta obligatoria
- test de faltante de categoria con pregunta o propuesta
- test de no guardado parcial sin proyecto
- test de no guardado parcial sin categoria
- regresion de guardado normal y lectura

### Riesgos

- flujos conversacionales ambiguos
- guardar parcialmente antes de tener los datos minimos

### Decision de salida

El flujo de captura queda cerrado: proyecto primero, categoria obligatoria y guardado solo al final.

---

## Fase 9. Metadata externa ligera

### Dependencia bloqueante

Esta fase requiere que la Fase 7 (Migracion al formato v0.2) haya completado con exito. Debe ejecutarse manteniendo el orden del plan tras la Fase 8, pero su bloqueo estructural es la Fase 7.

### Objetivo

Enriquecer la captura de URLs sin convertir el guardado en una operacion fragil o dependiente de la red.

### Que toca implementar

1. Intentar extraer metadata externa ligera cuando entre una URL.
2. Priorizar fuentes seguras y simples:
   - oEmbed para YouTube o Vimeo
   - `og:title`
   - `og:description`
   - `meta description`
   - `<title>`
3. Imponer timeout duro de 3 segundos.
4. Si falla la red o la metadata, guardar igualmente con fallback seguro.
5. No bloquear el guardado ni dejar la entrada en estado inconsistente.

### Que no toca todavia

- scraping complejo
- parseo profundo de paginas
- dependencias externas pesadas

### Criterio de exito

- Las URLs se enriquecen cuando hay metadata util.
- Si no la hay, el guardado sigue funcionando.
- El tiempo de espera no degrada la experiencia mas alla del timeout definido.

### Prueba manual

1. Guardar una URL de YouTube o Vimeo.
2. Verificar que se aprovecha oEmbed si esta disponible.
3. Guardar una URL web normal con `og:title` o `meta description`.
4. Simular un fallo de red o una URL sin metadata util.
5. Verificar que la entrada se guarda igualmente con fallback seguro.

### Prueba de regresion minima

- guardado de entradas sin URL sigue funcionando
- guardado de entradas con texto puro sigue funcionando
- lectura y busqueda siguen funcionando

### Tests que OpenClaw debera materializar

- test de extraccion exitosa en YouTube/Vimeo
- test de extraccion exitosa en web normal
- test de timeout
- test de fallo de red con fallback seguro
- test de no bloqueo del guardado
- regresion de entradas sin URL

### Riesgos

- dependencia excesiva de la red
- lentitud del guardado
- metadatos pobres o enganhosos

### Decision de salida

La captura de URLs es mas rica sin sacrificar robustez.

---

## Fase 10. Resumenes honestos y `calidad_resumen`

### Dependencia bloqueante

Esta fase requiere que la Fase 7 (Migracion al formato v0.2) haya completado con exito. Debe ejecutarse despues de la Fase 9 para aprovechar la metadata ya disponible.

### Objetivo

Distinguir entradas ricas de entradas pobres y mejorar la honestidad del resumen mostrado y almacenado.

### Que toca implementar

1. Ajustar la logica de resumen segun prioridad:
   - resumen del usuario
   - metadata externa util
   - texto libre util
   - fallback minimo
2. Asignar correctamente `calidad_resumen`:
   - `usuario`
   - `auto`
   - `fallback`
3. Eliminar frases vacias y plantillas poco utiles.
4. Hacer visible cuando una entrada quedo pobre.

### Que no toca todavia

- recordatorios periodicos
- vistas de mantenimiento complejas

### Criterio de exito

- El resumen ya no repite informacion vacia sin valor.
- Las entradas pobres se marcan claramente como tales.
- El usuario puede distinguir una entrada enriquecida de una apenas capturada.

### Prueba manual

1. Guardar una entrada con resumen explicito del usuario.
2. Verificar `calidad_resumen: usuario`.
3. Guardar una URL con metadata suficiente.
4. Verificar `calidad_resumen: auto`.
5. Guardar una URL sin contexto suficiente.
6. Verificar `calidad_resumen: fallback`.

### Prueba de regresion minima

- titulo y resumen siguen siendo parseables
- guardado, lectura, busqueda y listado siguen funcionando

### Tests que OpenClaw debera materializar

- test de prioridad correcta de fuentes de resumen
- test de etiquetado correcto de `calidad_resumen`
- test de entrada pobre con fallback minimo
- regresion de render y parseo de entradas

### Riesgos

- sobrecomplicar la heuristica
- generar resumenes aparentemente ricos pero poco fiables

### Decision de salida

El sistema distingue de forma honesta entre conocimiento fuerte y captura debil.

---

## Fase 11. Confirmacion limpia y salida humana basica

### Dependencia bloqueante

Esta fase requiere que la Fase 10 haya completado con exito, para humanizar una salida que ya conoce `calidad_resumen` y el nuevo formato.

### Objetivo

Mejorar la presentacion al usuario en Telegram sin tocar aun toda la navegacion avanzada.

### Que toca implementar

1. Limpiar la confirmacion de guardado:
   - sin rutas
   - sin ID por defecto
2. Humanizar fechas en la salida visible.
3. Ocultar IDs en listados resumidos.
4. Sustituir mensajes CLI por lenguaje natural.
5. Reservar modo tecnico a una vista explicita.

### Que no toca todavia

- paginacion
- vistas de mantenimiento
- verbose completo si no es estrictamente necesario

### Criterio de exito

- La salida normal deja de parecer un CLI.
- La informacion importante se entiende mas rapido.
- El modo tecnico no contamina la experiencia por defecto.

### Prueba manual

1. Guardar una entrada nueva.
2. Verificar que la confirmacion es corta y limpia.
3. Listar un proyecto.
4. Verificar que la fecha es humana.
5. Verificar que no aparece el ID en el listado resumido.
6. Ejecutar una busqueda y comprobar que no aparece lenguaje tipo `--entry-id`.

### Prueba de regresion minima

- busqueda sigue encontrando entradas
- vista completa tecnica sigue disponible si existe
- guardado y lectura siguen funcionando

### Tests que OpenClaw debera materializar

- test de formato de confirmacion de guardado
- test de humanizacion de fecha
- test de ausencia de ID en listado resumido
- test de lenguaje natural en mensajes de busqueda
- regresion de lectura y busqueda

### Riesgos

- perder demasiado detalle util
- inconsistencias entre salida humana y salida tecnica

### Decision de salida

La experiencia visible ya esta claramente orientada a usuario humano.

---

## Fase 12. Etiquetas visibles y representacion humana

### Dependencia bloqueante

Esta fase requiere que la Fase 11 haya completado con exito.

### Objetivo

Separar claves internas normalizadas de etiquetas visibles agradables para el usuario.

### Que toca implementar

1. Mantener claves internas actuales.
2. Anadir funcion de humanizacion de etiquetas visibles.
3. Aplicarla a:
   - categorias
   - tipos si procede
   - proyectos en salida visible si mejora la lectura

### Que no toca todavia

- alias complejos
- diccionarios enormes de nombres

### Criterio de exito

- La salida muestra etiquetas humanas sin romper el modelo interno.

### Prueba manual

1. Guardar o listar entradas con categorias normalizadas.
2. Verificar que se muestran como etiquetas humanas en la salida.
3. Verificar que la busqueda y el parseo siguen usando la forma interna correctamente.

### Prueba de regresion minima

- filtrado por categoria sigue funcionando
- busqueda sigue funcionando
- lectura de archivos no cambia

### Tests que OpenClaw debera materializar

- test de humanizacion visible de categorias
- test de conservacion de claves internas
- regresion de filtrado y busqueda

### Riesgos

- desacoplar mal valor interno y visible
- generar presentaciones inconsistentes

### Decision de salida

La informacion se ve humana sin comprometer la consistencia interna.

---

## Fase 13. Estados funcionales y consultas por estado

### Dependencia bloqueante

Esta fase requiere que la Fase 7 (Migracion al formato v0.2) haya completado con exito.

### Objetivo

Activar `estado` como parte real del flujo de trabajo.

### Que toca implementar

1. Estado por defecto `nuevo` en entradas nuevas.
2. Soportar actualizacion de estado a:
   - `revisado`
   - `descartado`
3. Permitir listados filtrados por estado.
4. Permitir acciones conversacionales como "marca como revisado".

### Que no toca todavia

- recordatorio automatico diario
- vistas complejas de mantenimiento

### Criterio de exito

- El usuario puede consultar y cambiar el estado de las entradas.
- El sistema puede diferenciar lo nuevo de lo ya procesado.

### Prueba manual

1. Guardar una entrada nueva y verificar `estado: nuevo`.
2. Marcarla como revisada.
3. Listar solo lo revisado.
4. Verificar que aparece ahi y no en lo nuevo.

### Prueba de regresion minima

- guardado sigue asignando el estado correcto
- busqueda y listado general siguen funcionando

### Tests que OpenClaw debera materializar

- test de estado por defecto
- test de actualizacion de estado
- test de filtro por estado
- regresion de lectura, busqueda y listado global

### Riesgos

- confusion entre estado y calidad del resumen
- inconsistencias al actualizar YAML

### Decision de salida

Bitacora deja de ser solo almacenamiento y pasa a ser una bandeja accionable.

---

## Fase 14. Vista de ultimas entradas y pendientes de enriquecer

### Dependencia bloqueante

Esta fase requiere que la Fase 7 haya completado con exito como precondicion estructural y, ademas, que las Fases 10 y 13 hayan completado con exito para que `calidad_resumen` y `estado` ya sean operativos.

### Objetivo

Empezar a explotar el valor operativo de `estado` y `calidad_resumen`.

### Que toca implementar

1. Vista de ultimas entradas por proyecto.
2. Vista de entradas con `calidad_resumen: fallback`.
3. Vista de pendientes de enriquecer.
4. Mensajes orientados a reenganchar al usuario con entradas pobres.

### Que no toca todavia

- recordatorio programado automatico
- vistas complejas por antiguedad o tendencia

### Criterio de exito

- El usuario puede ver rapidamente que ha guardado hace poco.
- El usuario puede identificar entradas pobres pendientes de enriquecer.

### Prueba manual

1. Guardar varias entradas de distinta calidad.
2. Pedir ultimas entradas.
3. Pedir pendientes de enriquecer.
4. Verificar que la seleccion coincide con `calidad_resumen` y orden temporal.

### Prueba de regresion minima

- estados siguen funcionando
- busqueda y listados generales siguen funcionando

### Tests que OpenClaw debera materializar

- test de vista ultimas entradas
- test de vista pendientes de enriquecer
- test de filtrado por `calidad_resumen`
- regresion de estado y listado

### Riesgos

- mezclar mal estado funcional con pobreza de resumen
- salidas demasiado largas

### Decision de salida

La base empieza a ayudar a priorizar que revisar o enriquecer.

---

## Fase 15. Recordatorio diario de pendientes de enriquecer

### Dependencia bloqueante

Esta fase requiere que la Fase 14 haya completado con exito. Antes de implementar el mecanismo de programacion, es obligatorio verificar como gestiona OpenClaw las tareas programadas de forma nativa y usar ese mecanismo. Si no existe un mecanismo nativo claro, la fase debe detenerse y reportarse como bloqueada.

### Objetivo

Anadir la funcion de recordatorio periodico para entradas con resumen pobre.

### Que toca implementar

1. Verificar primero el mecanismo nativo de tareas programadas de OpenClaw.
2. Generar un recordatorio diario a las 20:00 usando ese mecanismo nativo.
3. Basarlo en entradas con `calidad_resumen: fallback` que sigan sin enriquecer.
4. Presentarlo de forma breve y util.

### Que no toca todavia

- notificaciones complejas
- frecuencia configurable por usuario
- scheduler propio ad hoc

### Criterio de exito

- El recordatorio se genera una vez al dia a la hora definida.
- Solo incluye entradas realmente pendientes de enriquecer.
- La programacion usa el mecanismo nativo de OpenClaw.

### Prueba manual

1. Tener varias entradas con `fallback`.
2. Forzar o simular la ejecucion del recordatorio.
3. Verificar que solo aparecen las entradas pendientes.
4. Verificar que la programacion esta configurada a las 20:00 mediante el mecanismo nativo elegido.

### Prueba de regresion minima

- guardado y estados siguen funcionando
- vistas de pendientes siguen funcionando

### Tests que OpenClaw debera materializar

- test de seleccion correcta de entradas fallback
- test de formato del recordatorio
- test de periodicidad configurada a las 20:00
- test de uso del mecanismo nativo validado
- regresion de estados y vistas de pendientes

### Riesgos

- recordar entradas ya enriquecidas
- generar ruido excesivo
- implementar un scheduler propio cuando OpenClaw ya tiene uno nativo
- crear dependencias externas innecesarias para algo que ya resuelve la plataforma

### Decision de salida

La base ya no solo almacena: tambien reengancha al usuario con lo pendiente, usando la programacion nativa de OpenClaw.

---

## Fase 16. Paginacion y navegacion larga

### Dependencia bloqueante

Esta fase requiere que la Fase 11 haya completado con exito, de forma que la paginacion se aplique sobre una salida humana ya estabilizada.

### Objetivo

Permitir navegar proyectos o categorias con muchas entradas sin saturar Telegram.

### Que toca implementar

1. Anadir offset o mecanismo equivalente.
2. Mostrar tramos claros de resultados.
3. Permitir "mas", "siguiente pagina" o similares en la capa conversacional.

### Que no toca todavia

- botones
- cursores complejos

### Criterio de exito

- El usuario puede navegar resultados largos sin perder contexto.

### Prueba manual

1. Tener suficientes entradas para varias paginas.
2. Pedir primera pagina.
3. Pedir la siguiente.
4. Verificar que no hay solapamientos ni saltos incorrectos.

### Prueba de regresion minima

- listados pequenos siguen funcionando igual
- busqueda y filtrado siguen funcionando

### Tests que OpenClaw debera materializar

- test de offset basico
- test de limites
- test de fin de resultados
- regresion de listados normales

### Riesgos

- perder contexto de navegacion
- errores de paginacion acumulativa

### Decision de salida

Bitacora sigue siendo usable cuando la base crece.

---

## Fase 17. Nota personal y ampliacion de tags en entradas existentes

### Dependencia bloqueante

Esta fase requiere que la Fase 10 haya completado con exito, para que el enriquecimiento pueda reflejar correctamente los cambios en `calidad_resumen`.

### Objetivo

Hacer explicito el modelo de enriquecimiento progresivo.

### Que toca implementar

1. Anadir nota personal a una entrada existente.
2. Ampliar tags en cualquier momento.
3. Si una entrada pobre se enriquece con nota del usuario, actualizar `calidad_resumen` a `usuario` si procede.

### Que no toca todavia

- edicion completa de todos los campos
- upsert sobre duplicados

### Criterio de exito

- El usuario puede enriquecer entradas ya guardadas.
- La entrada conserva `id` y `fecha`.
- El sistema refleja el enriquecimiento correctamente.

### Prueba manual

1. Tomar una entrada `fallback`.
2. Anadir una nota personal.
3. Anadir uno o mas tags.
4. Verificar el YAML y la nota personal resultante.

### Prueba de regresion minima

- busqueda sigue encontrando la entrada
- vistas por estado y pendientes siguen funcionando

### Tests que OpenClaw debera materializar

- test de anadir nota personal
- test de ampliar tags
- test de cambio correcto de `calidad_resumen`
- regresion de busqueda y vistas de pendientes

### Riesgos

- sobrescribir nota previa
- mezclar mal nota personal y resumen

### Decision de salida

El modelo de enriquecimiento ya funciona de forma explicita.

---

## Fase 18. Duplicados inteligentes y canonicalizacion

### Dependencia bloqueante

Esta fase requiere que la Fase 9 haya completado con exito y se apoya en la deduplicacion exacta ya estable de la Fase 5.

### Objetivo

Reducir duplicados obvios con URLs equivalentes.

### Que toca implementar

1. Canonicalizacion basica de URLs.
2. Comparacion de duplicados sobre la URL canonicalizada.
3. Mantener comportamiento conservador si la canonicalizacion no es segura.

### Que no toca todavia

- upsert automatico
- reglas demasiado agresivas de equivalencia

### Criterio de exito

- URLs obvias equivalentes ya no se guardan como duplicados separados.

### Prueba manual

1. Guardar un recurso de YouTube en formato corto.
2. Intentar guardar el mismo recurso en formato largo.
3. Verificar que se detecta como duplicado.

### Prueba de regresion minima

- deduplicacion exacta previa sigue funcionando
- guardado normal de URL distintas sigue funcionando

### Tests que OpenClaw debera materializar

- test de canonicalizacion YouTube corto/largo
- test de trailing slash
- test de parametros irrelevantes
- regresion de deduplicacion exacta previa

### Riesgos

- sobrecanonicalizar y confundir recursos distintos

### Decision de salida

La deduplicacion es mas util sin dejar de ser conservadora.

---

## Fase 19. Upsert opt-in en duplicados

### Dependencia bloqueante

Esta fase requiere que la Fase 18 haya completado con exito.

### Objetivo

Permitir que una nueva observacion sobre una URL ya existente se anada a la misma entrada sin duplicarla.

### Que toca implementar

1. Ofrecer fusion opcional cuando una URL ya existe.
2. Anadir la nueva observacion a la nota personal existente con separacion clara.
3. Mantener intactos los campos inmutables.

### Que no toca todavia

- fusion automatica silenciosa
- reescritura agresiva de estructura

### Criterio de exito

- El usuario puede anadir una nueva observacion a una entrada ya existente sin crear duplicado.

### Prueba manual

1. Guardar una URL.
2. Intentar guardarla de nuevo con nueva observacion.
3. Aceptar la fusion.
4. Verificar que no se crea una nueva entrada y que la nota personal se amplia.

### Prueba de regresion minima

- deduplicacion sigue bloqueando si no se acepta la fusion
- busqueda y lectura de la entrada siguen funcionando

### Tests que OpenClaw debera materializar

- test de oferta de upsert
- test de fusion correcta de nota
- test de no creacion de entrada duplicada
- regresion de deduplicacion y lectura

### Riesgos

- fusionar contenido donde no toca
- sobrescribir nota previa en vez de ampliarla

### Decision de salida

El sistema puede absorber observaciones repetidas sobre el mismo recurso sin duplicar conocimiento.

---

## Fase 20. Edicion completa de entradas y `fecha_actualizacion`

### Dependencia bloqueante

Esta fase requiere que la Fase 17 haya completado con exito, para apoyarse en una via de reescritura y enriquecimiento ya estabilizada.

### Objetivo

Permitir mantenimiento real de entradas ya existentes.

### Que toca implementar

1. Permitir actualizar:
   - `categoria`
   - `tipo`
   - `titulo`
   - `fuente`
2. Anadir `fecha_actualizacion` cuando proceda.
3. Mantener `id` y `fecha` inmutables.
4. Soportar, si es razonable, mover una entrada a otro proyecto.

### Que no toca todavia

- rediseno completo de modelo
- edicion libre del YAML completo por conversacion

### Criterio de exito

- Las entradas se pueden corregir sin recrearlas.
- La inmutabilidad de `id` y `fecha` se conserva.

### Prueba manual

1. Tomar una entrada existente.
2. Cambiar categoria.
3. Cambiar titulo.
4. Cambiar tipo si procede.
5. Verificar `fecha_actualizacion` y la conservacion de `id` y `fecha`.

### Prueba de regresion minima

- busqueda sigue funcionando
- deduplicacion sigue funcionando
- lectura del archivo sigue siendo correcta

### Tests que OpenClaw debera materializar

- test de actualizacion de categoria
- test de actualizacion de titulo
- test de actualizacion de tipo y fuente
- test de conservacion de campos inmutables
- test de `fecha_actualizacion`
- regresion de busqueda, lectura y deduplicacion

### Riesgos

- corrupcion de YAML al actualizar multiples campos
- perdida accidental de campos opcionales

### Decision de salida

Bitacora ya se puede mantener y corregir de forma natural.

---

## Fase 21. Capa conversacional fuerte y modo tecnico

### Dependencia bloqueante

Esta fase requiere que las capacidades funcionales previas ya esten estabilizadas, en especial las Fases 8, 11, 13, 17, 19 y 20.

### Objetivo

Formalizar en la skill el comportamiento conversacional esperado y el modo tecnico explicito.

### Que toca implementar

1. Actualizar `SKILL.md` con reglas conversacionales claras.
2. Definir comportamiento ante:
   - falta de proyecto
   - falta de categoria
   - duplicados
   - entrada pobre
   - enriquecimiento posterior
3. Activar un modo tecnico explicito.

### Que no toca todavia

- agente complejo con memoria conversacional profunda

### Criterio de exito

- La skill se comporta de forma predecible y alineada con la filosofia v0.2.

### Prueba manual

1. Probar varias capturas ambiguas.
2. Verificar que la skill pregunta o propone de forma coherente.
3. Probar modo tecnico y salida humana.

### Prueba de regresion minima

- flujos normales de guardado y lectura siguen funcionando

### Tests que OpenClaw debera materializar

- test de faltante de proyecto
- test de faltante de categoria
- test de duplicado con respuesta conversacional correcta
- test de modo tecnico
- regresion de guardado y lectura

### Riesgos

- `SKILL.md` demasiado largo o ambiguo
- contradicciones entre skill y scripts

### Decision de salida

La capa conversacional queda alineada con la arquitectura y el producto esperado.

---

## Fase 22. Limpieza final y mantenimiento del historico

### Dependencia bloqueante

Esta fase requiere el cierre satisfactorio de las Fases 7 a 21.

### Objetivo

Cerrar la v0.2 con limpieza documental y de datos no estructurales.

### Que toca implementar

1. Evitar repeticiones innecesarias como URL en `fuente` y nota si son identicas y no aportan valor.
2. Limpiar el log de desarrollo si procede.
3. Revisar ejemplos y documentacion final.

### Que no toca todavia

- cambios incompatibles de formato
- redisenos profundos

### Criterio de exito

- La base se ve limpia y consistente.
- No hay artefactos de desarrollo innecesarios.

### Prueba manual

1. Revisar varios archivos de proyecto.
2. Revisar el log.
3. Verificar que no se ha roto nada por los ajustes de limpieza.

### Prueba de regresion minima

- lectura, guardado, busqueda, estados, edicion y deduplicacion siguen funcionando

### Tests que OpenClaw debera materializar

- test de no perdida de informacion por limpieza
- regresion global de todas las fases anteriores relevantes

### Riesgos

- limpiar demasiado y perder trazabilidad util

### Decision de salida

La version 0.2 queda cerrada en estado consistente y limpio.

---

## Apendice A. Politica de ejecucion autonoma

Esta seccion define como debe comportarse OpenClaw cuando implementa y testea la skill de forma autonoma, sin intervencion manual del usuario en cada paso.

Su objetivo es doble: maximizar la autonomia del agente y evitar loops de correccion que degraden el sistema en vez de mejorarlo.

---

### A.1 Principio general

OpenClaw debe tratar cada fase como una unidad de trabajo atomica con resultado binario: **la fase pasa o no pasa**. No existe un estado intermedio valido. Si la fase no pasa, el agente no avanza.

---

### A.2 Que es un test valido

Un test valido para ejecucion autonoma debe cumplir estas condiciones:

1. **Es ejecutable por el propio agente** sin intervencion humana.
2. **Produce un resultado inequivoco**: pasa o falla. No produce "parece que funciona".
3. **Es reproducible**: ejecutarlo dos veces seguidas debe dar el mismo resultado.
4. **Verifica el estado real del archivo**, no solo que el codigo haya corrido sin errores.

Cada fase debe incluir al menos un test de este tipo antes de declararse completada. Las "pruebas manuales" descritas en cada fase deben traducirse a tests ejecutables equivalentes.

---

### A.3 Tests minimos por fase

Cada fase debe implementar estos tests antes de declararse completada:

**Fase 0**
- Crear el archivo del proyecto si no existe y verificar que existe en disco.
- Leer el archivo si ya existe y verificar que el contenido no ha cambiado.
- Verificar que `.gitignore` contiene una regla acotada a la ruta de datos decidida en Fase 0 (por ejemplo `skills/bitacora/data/*.md`), no un patron global `*.md`.

**Fase 1**
- Guardar una entrada minima y verificar que el archivo contiene exactamente un bloque delimitado por `---entry---`.
- Guardar una segunda entrada y verificar que el archivo contiene exactamente dos bloques.
- Verificar que el YAML de cada bloque es parseable sin errores.
- Verificar que la codificacion del archivo es UTF-8 y los saltos de linea son LF.

**Fase 2**
- Listar todo y verificar que el numero de entradas devuelto coincide con el numero real de bloques en el archivo.
- Filtrar por una categoria existente y verificar que solo se devuelven entradas de esa categoria.
- Filtrar por una categoria inexistente y verificar que el sistema devuelve cero resultados sin error.

**Fase 3**
- Guardar una entrada con todos los campos opcionales y verificar que cada campo aparece correctamente en el YAML.
- Leer una entrada antigua (sin campos opcionales) y verificar que no produce error de parseo.

**Fase 4**
- Buscar una palabra presente en el titulo de una entrada y verificar que esa entrada aparece en los resultados.
- Buscar una palabra que no existe en ninguna entrada y verificar que el sistema devuelve cero resultados sin error.

**Fase 5**
- Intentar guardar una URL ya existente y verificar que el archivo no ha ganado una nueva entrada.
- Guardar una URL nueva y verificar que si se ha anadido correctamente.

**Fases 7 a 22**
- Los tests minimos obligatorios son los definidos en cada fase v0.2 del presente documento.
- Ninguna fase nueva puede darse por completada sin materializar y ejecutar esos tests y su regresion minima.

---

### A.4 Politica de reintentos

Cuando un test falla, el agente debe seguir esta politica estrictamente:

1. **Primer fallo**: analizar el error, identificar la causa, aplicar una correccion concreta y volver a ejecutar el test.
2. **Segundo fallo consecutivo sobre el mismo test**: aplicar una segunda correccion distinta a la anterior y volver a ejecutar.
3. **Tercer fallo consecutivo sobre el mismo test**: **parar inmediatamente**. No intentar mas correcciones. Reportar el estado segun la politica de reporte definida en A.6.

**Regla critica**: cada correccion debe ser diferente a la anterior. Si el agente se encuentra repitiendo la misma correccion, debe parar antes de llegar al tercer intento.

---

### A.5 Politica ante regresiones

Si al ejecutar los tests de regresion de una fase se detecta que algo que funcionaba en una fase anterior ha dejado de funcionar:

1. El agente debe **revertir los cambios de la fase actual** antes de hacer nada mas.
2. Debe verificar que la regresion ha desaparecido tras el revert.
3. Debe reportar exactamente que cambio introdujo la regresion.
4. **No debe intentar corregir la regresion y avanzar a la vez**. Primero se estabiliza el sistema, luego se replantea el enfoque.

Si el revert no es posible o no elimina la regresion, el agente debe parar y reportar.

---

### A.6 Politica de reporte al terminar una fase

Al terminar cada fase, ya sea con exito o con fallo, el agente debe:

1. Mostrar el reporte estructurado al usuario con exactamente estos campos:

```text
FECHA: [fecha y hora exacta]
FASE: [numero y nombre]
ESTADO: COMPLETADA | FALLIDA | BLOQUEADA
TESTS EJECUTADOS: [numero]
TESTS PASADOS: [numero]
TESTS FALLIDOS: [numero]
REGRESIONES DETECTADAS: SI | NO
COMMIT REALIZADO: SI | NO | NO PROCEDE
DESCRIPCION: [una o dos lineas explicando que ha pasado]
ACCION REQUERIDA: [solo si el estado no es COMPLETADA - que necesita el usuario decidir o revisar]
```

2. Guardar ese mismo reporte en:
   `/mnt/c/omi/openclaw/skills/bitacora/ref/bitacora_log.md`
   - Si el archivo no existe, crearlo.
   - Si ya existe, anadir el nuevo reporte al final sin modificar las entradas anteriores.
   - Cada entrada debe empezar con la fecha y hora exacta.

Este reporte debe producirse siempre, incluso si la fase ha completado sin ningun problema. Es la senal que indica que la fase ha terminado y el sistema esta en un estado conocido.

---

### A.7 Condiciones de parada automatica

El agente debe parar de forma inmediata y reportar, sin intentar continuar, si ocurre cualquiera de estas condiciones:

1. Un test ha fallado tres veces consecutivas con correcciones distintas.
2. Se ha detectado una regresion que no desaparece tras revertir los cambios.
3. Una operacion de escritura ha fallado y el archivo de datos podria estar en estado inconsistente.
4. El agente detecta que esta a punto de modificar un campo inmutable (`id` o `fecha`) de una entrada existente.
5. El agente no puede determinar con certeza cual es el estado actual del archivo antes de escribir.
6. Se ha producido el mismo error mas de dos veces en la misma sesion, aunque sea en puntos distintos del codigo.
7. En la Fase 15 no se identifica un mecanismo nativo claro de OpenClaw para tareas programadas.

En todos estos casos, la accion correcta es: **parar, preservar el estado actual sin modificarlo mas, y reportar**.

---

### A.8 Lo que el agente nunca debe hacer de forma autonoma

Independientemente del resultado de los tests, estas acciones requieren confirmacion explicita del usuario y nunca deben tomarse de forma autonoma:

- Modificar o eliminar entradas existentes en un archivo de datos.
- Cambiar la estructura del formato de entrada de forma incompatible con entradas anteriores.
- Avanzar a una fase siguiente si la fase actual no ha pasado todos sus tests.
- Saltarse una fase aunque parezca trivial.
- Crear archivos de datos nuevos en rutas distintas a las decididas en la Fase 0.
- Modificar el `.gitignore` despues de la Fase 0.
- Inventar un mecanismo propio de tareas programadas si la plataforma ya no ofrece uno nativo claro.

---

### A.9 Politica de commits en ejecucion autonoma

Los commits deben hacerse unicamente cuando:

1. La funcion implementada pasa todos sus tests.
2. Los tests de regresion de la fase actual tambien pasan.

No se debe hacer commit de codigo que no pase sus tests, aunque el codigo "parezca correcto". El historial de git debe reflejar solo estados verificados y funcionales.

Formato de mensaje obligatorio:
```text
feat(bitacora): [descripcion breve de lo implementado] - fase [N] tests OK
```

Ejemplo:
```text
feat(bitacora): guardado basico con proyecto y categoria - fase 1 tests OK
```
