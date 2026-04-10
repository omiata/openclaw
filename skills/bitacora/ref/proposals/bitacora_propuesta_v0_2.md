# bitacora v0.2 — pack documental para revisión y posterior materialización en `ref/`

Este documento reúne, en un solo lugar, el contenido base de la versión 0.2 para que luego pueda separarse en los archivos definitivos:

- `bitacora_maestro.md`
- `bitacora_reglas.md`
- `bitacora_fases.md`
- `bitacora_changelog.md`

La intención de este pack es evitar pérdida de contexto o decisiones a medio cerrar. Primero se revisa aquí de forma integral. Después, Codex puede materializarlo en los archivos correspondientes.

---

# PARTE I — CONTENIDO PROPUESTO PARA `bitacora_maestro.md`

# bitacora_maestro.md
## Documento maestro — versión 0.2

**Rol:** documento de referencia funcional y arquitectónica.
**Uso:** define la visión, el comportamiento esperado, el modelo de datos, las decisiones de diseño y las reglas conceptuales del sistema.
**No es** un plan de ejecución ni debe usarse para implementar todo de una vez.

---

## 1. Propósito general

Bitácora es una skill de knowledge base personal orientada a proyectos. Su función es convertir OpenClaw en una bandeja de entrada estructurada para recursos, ideas, notas, enlaces, documentos y referencias de proyectos del usuario.

El flujo esperado es:

1. El usuario envía al sistema un recurso o una idea.
2. El sistema confirma o solicita el proyecto y la categoría.
3. El sistema guarda la entrada en la base del proyecto correspondiente.
4. Más adelante, el usuario puede listar, buscar, revisar, enriquecer y mantener lo guardado.

Bitácora no pretende ser un second brain complejo ni una base semántica avanzada. La prioridad es una base de conocimiento práctica, controlable, robusta y fácil de mantener.

---

## 2. Qué problema resuelve

Sin bitácora, el usuario corre el riesgo de:

- perder enlaces e ideas en chats dispersos,
- no saber en qué proyecto encaja cada recurso,
- no recordar por qué guardó algo,
- no poder recuperar fácilmente lo ya encontrado,
- acumular recursos pobres que luego no aportan valor real.

Bitácora resuelve esto convirtiendo la captura informal en una base estructurada y revisable.

---

## 3. Filosofía de diseño

### 3.1 Simplicidad primero

La solución debe seguir siendo pequeña, comprensible y robusta. La complejidad solo se introduce cuando aporta valor claro.

### 3.2 El usuario manda el proyecto y la categoría

El sistema no debe asumir demasiado. Si falta el proyecto, lo pregunta siempre primero. Si falta la categoría, la pide o propone opciones. La categoría explícita del usuario prevalece.

### 3.3 Estructura legible y controlable

La base vive en Markdown con YAML. Debe ser legible por humano y parseable por máquina.

### 3.4 Enriquecimiento progresivo

Las entradas pueden empezar pobres y enriquecerse después. Bitácora no exige perfección al capturar, pero sí debe distinguir claramente entre una entrada rica y una entrada pobre.

### 3.5 Honestidad sobre la calidad del conocimiento

Si el sistema no tiene suficiente información para generar un buen resumen, debe ser honesto. No debe inventar valor ni disfrazar una entrada débil como si fuera una nota ya enriquecida.

### 3.6 Salida humana por defecto

La salida visible al usuario debe ser limpia, natural y orientada a Telegram. La información técnica solo debe aparecer en modo explícitamente técnico.

---

## 4. Scope y nombre de la skill

La skill se llama **bitacora**.

Es genérica y soporta múltiples proyectos, por ejemplo:

- camper
- balcon
- poesia
- bicicleta
- recetas
- otros futuros

El proyecto es un valor dinámico, no un conjunto cerrado.

---

## 5. Organización por proyecto

La persistencia se organiza con **un archivo por proyecto**.

Ejemplos:

- `camper.md`
- `balcon.md`
- `poesia.md`
- `bicicleta.md`

Las categorías viven dentro del archivo del proyecto. No se convierten en carpetas ni en archivos separados.

---

## 6. Nuevo modelo de entrada v0.2

### 6.1 Principio general

A partir de v0.2, cada entrada tendrá:

- un delimitador fijo,
- un bloque YAML que contiene todos los datos estructurados,
- un bloque Markdown mínimo reservado a la nota personal del usuario.

### 6.2 Estructura objetivo

```markdown
---entry---

---
id: "entry-xxx"
fecha: "2026-04-09T14:18:16.909Z"
proyecto: "camper"
categoria: "electricidad"
tipo: "video"
titulo: "DIY PreWiring my Camper Van"
resumen: "Resumen automático o fallback"
fuente: "https://youtube.com/watch?v=xxx"
tags: []
calidad_resumen: "fallback"
estado: "nuevo"
---

**Nota personal**
(vacío hasta que el usuario enriquezca la entrada)
```

### 6.3 Fuente única de verdad

El YAML es la fuente única de verdad para todos los campos estructurados.

El bloque Markdown inferior ya no repite título, resumen o fuente. Solo contiene la nota personal del usuario.

### 6.4 Campos obligatorios

- `id`
- `fecha`
- `proyecto`
- `categoria`
- `tipo`
- `titulo`
- `resumen`
- `calidad_resumen`
- `estado`

### 6.5 Campos opcionales

- `fuente`
- `tags`
- `fecha_actualizacion`
- otros campos futuros compatibles con el esquema

---

## 7. Campos nuevos de v0.2

### 7.1 `calidad_resumen`

Indica la calidad y origen práctico del resumen.

Valores válidos:

- `fallback` — resumen mínimo porque solo había URL, título o información pobre
- `auto` — resumen generado automáticamente con contexto suficiente
- `usuario` — resumen o información enriquecida explícitamente por el usuario

### 7.2 `estado`

Representa el estado funcional de la entrada dentro del flujo de trabajo.

Valores iniciales:

- `nuevo`
- `revisado`
- `descartado`

`nuevo` es el estado por defecto al guardar.

### 7.3 `fecha_actualizacion`

Campo opcional para futuras ediciones. No sustituye nunca a `fecha`.

---

## 8. Política de proyecto y categoría

### 8.1 Proyecto

**Decisión cerrada:** si falta el proyecto, el sistema siempre pregunta primero por él. No intenta inferirlo a partir del contenido.

Ejemplo:

```text
Usuario: https://youtu.be/xxx
Sistema: ¿En qué proyecto guardo esto?
```

### 8.2 Categoría

Si el proyecto está claro pero falta la categoría, el sistema propone las categorías más frecuentes del proyecto y pide confirmación o una categoría nueva.

El sistema no guarda una entrada sin categoría.

---

## 9. Política de títulos y resúmenes

### 9.1 Título

Prioridad:

1. título explícito del usuario
2. título extraído de metadata externa
3. primera línea útil del contenido
4. fallback conservador

### 9.2 Resumen

Prioridad:

1. resumen explícito del usuario
2. descripción útil extraída de metadata externa
3. texto libre del usuario
4. fallback mínimo

### 9.3 Honestidad

Si solo hay URL y no hay contexto suficiente, el resumen debe seguir siendo mínimo y la entrada debe marcarse como `calidad_resumen: fallback`.

---

## 10. Extracción ligera de metadata externa

Cuando entra una URL, el sistema puede intentar enriquecer el guardado con metadata externa.

Fuentes permitidas:

- oEmbed para YouTube o Vimeo
- `og:title`
- `og:description`
- `meta description`
- `<title>`

Condiciones:

- timeout duro de 3 segundos
- si falla, el guardado sigue adelante
- nunca bloquear el guardado por un fallo de red o metadata

---

## 11. Canonicalización de URLs

Antes de comparar duplicados o guardar una URL, debe poder normalizarse de forma básica:

- `youtu.be/ID` a `youtube.com/watch?v=ID`
- eliminación de parámetros irrelevantes
- normalización de trailing slash
- reglas básicas de host y protocolo

Esto busca evitar duplicados obvios sin introducir una lógica compleja o peligrosa.

---

## 12. Flujo de captura esperado en v0.2

### 12.1 Captura rica

Si el usuario da proyecto, categoría y contexto, el sistema guarda directamente.

### 12.2 Captura pobre

Si el usuario da solo una URL o una idea muy corta:

1. se pregunta proyecto si falta,
2. se pregunta o propone categoría si falta,
3. se intenta extraer metadata,
4. se guarda igualmente aunque el resumen quede pobre,
5. se avisa que la entrada quedó con contexto limitado,
6. se ofrece enriquecerla.

---

## 13. Salida humana por defecto

La salida normal debe:

- ocultar IDs en listados normales,
- ocultar rutas físicas,
- mostrar fechas humanizadas,
- usar etiquetas visibles humanizadas,
- hablar en lenguaje natural,
- reservar modo técnico para cuando el usuario lo pida.

Ejemplos de mejoras esperadas:

- confirmación corta de guardado
- listados resumidos
- resultados de búsqueda naturales
- vista técnica solo bajo demanda

---

## 14. Bandeja de trabajo y enriquecimiento

Bitácora no es solo almacenamiento. Debe ayudar a trabajar con lo guardado.

Funciones esperadas en v0.2:

- listar lo nuevo,
- listar lo revisado,
- ver últimas entradas,
- ver entradas con resumen pobre,
- añadir nota personal a entradas existentes,
- ampliar tags,
- marcar entradas como revisadas,
- recordar diariamente qué entradas siguen pobres.

**Decisión cerrada:** el recordatorio de pendientes de enriquecer será cada día a las 20:00, usando el mecanismo nativo de OpenClaw para tareas programadas. Si no existe un mecanismo nativo claro, se documenta el hueco y se decide antes de implementar.

---

## 15. Migración de entradas existentes

**Decisión cerrada:** las 4 entradas antiguas de `camper.md` se migran al nuevo formato antes de implementar las mejoras.

La migración debe ser:

- no destructiva,
- atómica,
- conservadora,
- sin pérdida de datos,
- compatible con la lectura posterior.

El Markdown redundante antiguo puede omitirse o transformarse a nota personal si contiene valor real no duplicado en el YAML.

---

## 16. Decisiones cerradas de v0.2

1. El sistema siempre pregunta primero por el proyecto.
2. La categoría nunca se infiere silenciosamente si falta.
3. Se migra `camper.md` al nuevo formato antes de las mejoras.
4. `calidad_resumen` y `estado` pasan a formar parte del modelo oficial.
5. La salida por defecto es humana y limpia.
6. El modo técnico es explícito.
7. La extracción de metadata externa es ligera y con timeout duro.
8. El recordatorio de entradas pendientes de enriquecer será diario a las 20:00, usando el mecanismo nativo de OpenClaw.

---

## 17. Cómo usar este documento

Este documento se usa para:

- resolver dudas de comportamiento esperado,
- validar decisiones de diseño,
- verificar que una implementación encaja con la filosofía del sistema.

No debe usarse como prompt directo para implementar todo a la vez.

---

# PARTE II — CONTENIDO PROPUESTO PARA `bitacora_reglas.md`

# bitacora_reglas.md
## Reglas de Oro — versión 0.2

Estas reglas son de obligado cumplimiento. Son restricciones técnicas y operativas que prevalecen sobre decisiones menores o atajos de implementación.

---

## Regla 1. Simplicidad primero

Las nuevas capacidades de v0.2 no deben introducir complejidad innecesaria. Cada mejora debe respetar la robustez y no convertir bitácora en un sistema opaco o difícil de mantener.

---

## Regla 2. Un archivo por proyecto

Se mantiene el principio de un archivo por proyecto. Las categorías siguen siendo internas a cada archivo.

---

## Regla 3. YAML como fuente de verdad

Todos los datos estructurados viven en el YAML de cada entrada. El bloque Markdown queda reservado a la nota personal del usuario.

No se debe volver a introducir redundancia entre YAML y cuerpo Markdown.

---

## Regla 4. Delimitador fijo e inviolable

El delimitador de entrada sigue siendo exactamente:

```text
---entry---
```

Nunca debe aparecer dentro del contenido libre.

---

## Regla 5. IDs únicos e inmutables

- No usar IDs secuenciales.
- El ID debe poder generarse sin leer el archivo completo.
- `id` y `fecha` nunca se modifican después de crear la entrada.

---

## Regla 6. Nuevos campos obligatorios de v0.2

Toda entrada nueva o migrada debe incluir:

- `calidad_resumen`
- `estado`

Valores válidos:

`calidad_resumen`:
- `fallback`
- `auto`
- `usuario`

`estado`:
- `nuevo`
- `revisado`
- `descartado`

---

## Regla 7. Proyecto siempre explícito

Si el usuario no indica proyecto, el sistema debe preguntar primero por él.

No se permite inferencia silenciosa del proyecto.

---

## Regla 8. Categoría obligatoria

No se debe guardar una entrada sin categoría.

Si la categoría falta, el sistema debe pedirla o proponer categorías del proyecto.

---

## Regla 9. Metadata externa opcional y segura

La extracción de metadata externa:

- es opcional,
- nunca bloquea el guardado,
- tiene timeout duro de 3 segundos,
- debe fallar de forma silenciosa para la lógica interna y segura para el usuario,
- no debe introducir dependencia fuerte de red.

Si falla, la entrada se guarda igualmente.

---

## Regla 10. Resumen honesto

No debe generarse un resumen que finja más conocimiento del que realmente existe.

Si solo hay URL o contexto insuficiente, se debe marcar `calidad_resumen: fallback`.

---

## Regla 11. Canonicalización conservadora de URLs

La canonicalización debe limitarse a reglas simples y seguras. No debe intentar resolver casos complejos que puedan fusionar recursos distintos por error.

---

## Regla 12. Inserción segura por append

Las entradas nuevas siguen añadiéndose al final del archivo.

No se reordena físicamente el archivo para mantener cronología inversa.

---

## Regla 13. Atomicidad para migración y reescritura

Toda operación que reescriba el archivo completo, incluyendo:

- migración al formato v0.2,
- actualización de campos existentes,
- limpieza o normalización,
- cambios estructurales,

se hará mediante escritura a archivo temporal y reemplazo atómico.

Si algo falla, el archivo original no debe tocarse.

---

## Regla 14. Migración obligatoria antes de mejoras funcionales

La migración de las 4 entradas antiguas de `camper.md` al nuevo formato v0.2 debe realizarse antes de las mejoras de UX y flujo que dependan del nuevo esquema.

Las Fases 8 a 22 no pueden iniciarse si la Fase 7 no ha completado con éxito.

---

## Regla 15. Compatibilidad hacia atrás durante la transición

Durante la fase de migración, el sistema debe seguir siendo capaz de:

- leer entradas antiguas si aún existieran,
- detectar inconsistencias sin detener todo el procesamiento,
- continuar operando sobre entradas válidas aunque una concreta falle.

---

## Regla 16. Nota personal como único Markdown relevante

El bloque Markdown de una entrada debe contener solo la nota personal del usuario o quedar vacío.

No volver a repetir título, resumen o fuente fuera del YAML.

---

## Regla 17. Salida humana por defecto

La salida visible al usuario no debe exponer por defecto:

- rutas físicas,
- fechas ISO crudas,
- banderas CLI,
- IDs en listados resumidos.

Todo eso queda reservado al modo técnico explícito.

---

## Regla 18. Modo técnico explícito

La información interna solo se muestra si el usuario pide un modo técnico o una vista completa.

---

## Regla 19. Recordatorio programado con mecanismo nativo

La función de recordatorio de entradas pendientes de enriquecer debe configurarse para ejecutarse cada día a las 20:00.

La generación del recordatorio debe basarse exclusivamente en entradas con `calidad_resumen: fallback` que sigan sin enriquecer.

Antes de implementar el mecanismo de programación, se debe verificar cómo gestiona OpenClaw las tareas programadas de forma nativa y usar ese mecanismo. Si no existe un mecanismo nativo claro, se detiene y se reporta antes de inventar una solución propia.

---

## Regla 20. Desarrollo incremental y regresión obligatoria

Cada fase debe dejar un sistema usable por sí mismo.

Toda fase nueva debe:

- pasar sus tests propios,
- volver a ejecutar la regresión mínima de las fases anteriores relevantes,
- no avanzar si algo falla.

---

## Regla 21. Política de commits

Se mantiene la política de un commit por unidad funcional validada.

No se hace commit de cambios que no hayan pasado tests.

---

## Regla 22. No modificar lo canónico sin aprobación

Mientras se trabaja en v0.2 a nivel documental o experimental, los archivos canónicos no se sustituyen hasta revisión y aprobación.

---

## Regla 23. Nota de uso

Si una tarea concreta entra en conflicto con estas reglas, se revisa la tarea. No las reglas.

---

# PARTE III — CONTENIDO PROPUESTO PARA `bitacora_fases.md`

# bitacora_fases.md
## Plan de implementación por fases — versión 0.2

**Uso:** este es el documento operativo para implementar v0.2 de forma incremental y robusta.
**Regla crítica:** cada sesión debe trabajar una sola fase. No dar el documento entero al agente ejecutor cuando vaya a implementar código.

**Documentos de referencia:**
- `bitacora_maestro.md`
- `bitacora_reglas.md`

---

## Cómo usar este documento

1. Abrir una sesión nueva para la fase correspondiente.
2. Dar siempre `bitacora_reglas.md`.
3. Dar solo la fase en curso y no todo el documento.
4. Implementar.
5. Materializar los tests que esta fase exige.
6. Ejecutar los tests de la fase.
7. Ejecutar la regresión mínima indicada.
8. Solo si todo pasa, cerrar la fase.

---

## Fase 7. Migración al formato v0.2

### Objetivo

Migrar la estructura de entradas al nuevo formato v0.2 sin pérdida de datos y dejando el sistema preparado para las mejoras posteriores.

### Qué toca implementar

1. Definir el nuevo render de entrada con:
   - YAML completo como fuente de verdad
   - bloque Markdown reservado a `Nota personal`
2. Añadir los campos nuevos:
   - `calidad_resumen`
   - `estado`
3. Implementar la migración de las 4 entradas antiguas de `camper.md`.
4. Reescribir las entradas al nuevo formato de forma atómica.
5. Mantener compatibilidad de lectura durante la transición.

### Qué no toca todavía

- extracción de metadata externa
- UX mejorada en Telegram
- estados como flujo de trabajo visible
- paginación
- recordatorios

### Criterio de éxito

- Las 4 entradas antiguas se migran sin pérdida de datos.
- El archivo resultante queda en el formato nuevo.
- Las entradas siguen siendo parseables.
- El sistema sigue pudiendo leer el proyecto tras la migración.

### Prueba manual

1. Ejecutar la migración sobre `camper.md`.
2. Abrir el archivo resultante.
3. Verificar que cada entrada tiene:
   - delimitador correcto
   - YAML completo
   - `calidad_resumen`
   - `estado`
   - bloque `Nota personal`
4. Comprobar que no se ha perdido ninguna entrada.
5. Comprobar que el YAML de cada entrada sigue siendo legible.

### Prueba de regresión mínima

- lectura global del proyecto sigue funcionando
- filtrado por categoría sigue funcionando
- búsqueda sobre entradas existentes sigue funcionando

### Tests que OpenClaw deberá materializar

- test de migración de 4 entradas antiguas
- test de preservación de número de entradas
- test de preservación de `id`, `fecha`, `proyecto`, `categoria`, `tipo`, `titulo`, `resumen`, `fuente`
- test de creación de campos nuevos por defecto
- test de atomicidad si falla la escritura
- test de lectura posterior tras la migración

### Riesgos

- pérdida de información al eliminar redundancia antigua
- error al reinterpretar el Markdown previo
- reescritura parcial del archivo

### Decisión de salida

La base ya está en formato v0.2 y se puede pasar a las mejoras que dependen del nuevo esquema.

---

## Fase 8. Proyecto y categoría como flujo obligatorio de captura

### Dependencia bloqueante

Esta fase no puede iniciarse hasta que la Fase 7 (Migración al formato v0.2) haya completado con éxito y todas las entradas existentes estén en el nuevo formato. Si la Fase 7 no ha pasado todos sus tests, esta fase no debe empezar.

### Objetivo

Asegurar que el guardado siempre tiene proyecto y categoría de forma explícita y predecible.

### Qué toca implementar

1. Si falta proyecto, preguntar primero por el proyecto.
2. Si falta categoría, preguntar por la categoría o proponer las más usadas del proyecto.
3. No guardar una entrada sin proyecto.
4. No guardar una entrada sin categoría.
5. Ajustar `SKILL.md` y el flujo conversacional básico para reflejarlo.

### Qué no toca todavía

- metadata externa
- resúmenes mejorados
- estados funcionales visibles
- recordatorios

### Criterio de éxito

- El sistema nunca guarda sin proyecto.
- El sistema nunca guarda sin categoría.
- El flujo conversacional es claro y predecible.

### Prueba manual

1. Intentar guardar una URL sin proyecto.
2. Verificar que el sistema pregunta primero por proyecto.
3. Dar proyecto pero no categoría.
4. Verificar que el sistema pide o propone categoría.
5. Confirmar categoría.
6. Verificar que el guardado se completa solo después de tener ambos datos.

### Prueba de regresión mínima

- guardado normal cuando proyecto y categoría ya están presentes
- lectura, listado y búsqueda siguen funcionando

### Tests que OpenClaw deberá materializar

- test de intento de guardado sin proyecto
- test de intento de guardado sin categoría
- test de propuesta de categorías frecuentes
- test de no persistencia prematura antes de confirmar datos
- regresión de guardado normal con entrada completa

### Riesgos

- diálogos demasiado largos
- estados intermedios mal resueltos
- confusión entre propuesta y confirmación

### Decisión de salida

El sistema captura siempre con proyecto y categoría explícitos.

---

## Fase 9. Metadata externa ligera

### Dependencia

Esta fase requiere que la Fase 7 (Migración al formato v0.2) haya completado con éxito.

### Objetivo

Mejorar título y resumen de entradas con URL mediante extracción ligera y segura de metadata.

### Qué toca implementar

1. Crear módulo separado de extracción de metadata.
2. Añadir soporte para:
   - oEmbed en YouTube/Vimeo
   - `og:title`
   - `og:description`
   - `meta description`
   - `<title>`
3. Imponer timeout duro de 3 segundos.
4. Integrar la metadata en la generación de título y resumen.
5. Si falla, seguir guardando igual.

### Qué no toca todavía

- resúmenes enriquecidos con IA pesada
- scraping complejo
- navegador headless

### Criterio de éxito

- Una URL con metadata accesible mejora el título y/o resumen.
- Una URL lenta o inaccesible no bloquea el guardado.
- El sistema sigue siendo robusto sin red.

### Prueba manual

1. Guardar una URL de YouTube conocida.
2. Verificar que el título extraído es mejor que el fallback puro.
3. Guardar una URL web con metadata simple.
4. Verificar mejora del título y del resumen.
5. Simular o usar una URL que no responda dentro del timeout.
6. Verificar que la entrada se guarda igualmente.

### Prueba de regresión mínima

- guardado de entradas sin URL sigue funcionando
- guardado de entradas con texto puro sigue funcionando
- lectura y búsqueda siguen funcionando

### Tests que OpenClaw deberá materializar

- test de extracción exitosa en YouTube/Vimeo
- test de extracción exitosa en web normal
- test de timeout
- test de fallo de red con fallback seguro
- test de no bloqueo del guardado
- regresión de entradas sin URL

### Riesgos

- dependencia excesiva de la red
- lentitud del guardado
- metadatos pobres o engañosos

### Decisión de salida

La captura de URLs es más rica sin sacrificar robustez.

---

## Fase 10. Resúmenes honestos y `calidad_resumen`

### Dependencia

Esta fase requiere que la Fase 7 (Migración al formato v0.2) haya completado con éxito.

### Objetivo

Distinguir entradas ricas de entradas pobres y mejorar la honestidad del resumen mostrado y almacenado.

### Qué toca implementar

1. Ajustar la lógica de resumen según prioridad:
   - resumen del usuario
   - metadata externa útil
   - texto libre útil
   - fallback mínimo
2. Asignar correctamente `calidad_resumen`:
   - `usuario`
   - `auto`
   - `fallback`
3. Eliminar frases vacías y plantillas poco útiles.
4. Hacer visible cuándo una entrada quedó pobre.

### Qué no toca todavía

- recordatorios periódicos
- vistas de mantenimiento complejas

### Criterio de éxito

- El resumen ya no repite información vacía sin valor.
- Las entradas pobres se marcan claramente como tales.
- El usuario puede distinguir una entrada enriquecida de una apenas capturada.

### Prueba manual

1. Guardar una entrada con resumen explícito del usuario.
2. Verificar `calidad_resumen: usuario`.
3. Guardar una URL con metadata suficiente.
4. Verificar `calidad_resumen: auto`.
5. Guardar una URL sin contexto suficiente.
6. Verificar `calidad_resumen: fallback`.

### Prueba de regresión mínima

- título y resumen siguen siendo parseables
- guardado, lectura, búsqueda y listado siguen funcionando

### Tests que OpenClaw deberá materializar

- test de prioridad correcta de fuentes de resumen
- test de etiquetado correcto de `calidad_resumen`
- test de entrada pobre con fallback mínimo
- regresión de render y parseo de entradas

### Riesgos

- sobrecomplicar la heurística
- generar resúmenes aparentemente ricos pero poco fiables

### Decisión de salida

El sistema distingue de forma honesta entre conocimiento fuerte y captura débil.

---

## Fase 11. Confirmación limpia y salida humana básica

### Objetivo

Mejorar la presentación al usuario en Telegram sin tocar aún toda la navegación avanzada.

### Qué toca implementar

1. Limpiar la confirmación de guardado:
   - sin rutas
   - sin ID por defecto
2. Humanizar fechas en la salida visible.
3. Ocultar IDs en listados resumidos.
4. Sustituir mensajes CLI por lenguaje natural.
5. Reservar modo técnico a una vista explícita.

### Qué no toca todavía

- paginación
- vistas de mantenimiento
- verbose completo si no es estrictamente necesario

### Criterio de éxito

- La salida normal deja de parecer un CLI.
- La información importante se entiende más rápido.
- El modo técnico no contamina la experiencia por defecto.

### Prueba manual

1. Guardar una entrada nueva.
2. Verificar que la confirmación es corta y limpia.
3. Listar un proyecto.
4. Verificar que la fecha es humana.
5. Verificar que no aparece el ID en el listado resumido.
6. Ejecutar una búsqueda y comprobar que no aparece lenguaje tipo `--entry-id`.

### Prueba de regresión mínima

- búsqueda sigue encontrando entradas
- vista completa técnica sigue disponible si existe
- guardado y lectura siguen funcionando

### Tests que OpenClaw deberá materializar

- test de formato de confirmación de guardado
- test de humanización de fecha
- test de ausencia de ID en listado resumido
- test de lenguaje natural en mensajes de búsqueda
- regresión de lectura y búsqueda

### Riesgos

- perder demasiado detalle útil
- inconsistencias entre salida humana y salida técnica

### Decisión de salida

La experiencia visible ya está claramente orientada a usuario humano.

---

## Fase 12. Etiquetas visibles y representación humana

### Objetivo

Separar claves internas normalizadas de etiquetas visibles agradables para el usuario.

### Qué toca implementar

1. Mantener claves internas actuales.
2. Añadir función de humanización de etiquetas visibles.
3. Aplicarla a:
   - categorías
   - tipos si procede
   - proyectos en salida visible si mejora la lectura

### Qué no toca todavía

- alias complejos
- diccionarios enormes de nombres

### Criterio de éxito

- La salida muestra etiquetas humanas sin romper el modelo interno.

### Prueba manual

1. Guardar o listar entradas con categorías normalizadas.
2. Verificar que se muestran como etiquetas humanas en la salida.
3. Verificar que la búsqueda y el parseo siguen usando la forma interna correctamente.

### Prueba de regresión mínima

- filtrado por categoría sigue funcionando
- búsqueda sigue funcionando
- lectura de archivos no cambia

### Tests que OpenClaw deberá materializar

- test de humanización visible de categorías
- test de conservación de claves internas
- regresión de filtrado y búsqueda

### Riesgos

- desacoplar mal valor interno y visible
- generar presentaciones inconsistentes

### Decisión de salida

La información se ve humana sin comprometer la consistencia interna.

---

## Fase 13. Estados funcionales y consultas por estado

### Dependencia

Esta fase requiere que la Fase 7 (Migración al formato v0.2) haya completado con éxito.

### Objetivo

Activar `estado` como parte real del flujo de trabajo.

### Qué toca implementar

1. Estado por defecto `nuevo` en entradas nuevas.
2. Soportar actualización de estado a:
   - `revisado`
   - `descartado`
3. Permitir listados filtrados por estado.
4. Permitir acciones conversacionales como "marca como revisado".

### Qué no toca todavía

- recordatorio automático diario
- vistas complejas de mantenimiento

### Criterio de éxito

- El usuario puede consultar y cambiar el estado de las entradas.
- El sistema puede diferenciar lo nuevo de lo ya procesado.

### Prueba manual

1. Guardar una entrada nueva y verificar `estado: nuevo`.
2. Marcarla como revisada.
3. Listar solo lo revisado.
4. Verificar que aparece ahí y no en lo nuevo.

### Prueba de regresión mínima

- guardado sigue asignando el estado correcto
- búsqueda y listado general siguen funcionando

### Tests que OpenClaw deberá materializar

- test de estado por defecto
- test de actualización de estado
- test de filtro por estado
- regresión de lectura, búsqueda y listado global

### Riesgos

- confusión entre estado y calidad del resumen
- inconsistencias al actualizar YAML

### Decisión de salida

Bitácora deja de ser solo almacenamiento y pasa a ser una bandeja accionable.

---

## Fase 14. Vista de últimas entradas y pendientes de enriquecer

### Dependencia

Esta fase requiere que la Fase 7 (Migración al formato v0.2) haya completado con éxito.

### Objetivo

Empezar a explotar el valor operativo de `estado` y `calidad_resumen`.

### Qué toca implementar

1. Vista de últimas entradas por proyecto.
2. Vista de entradas con `calidad_resumen: fallback`.
3. Vista de pendientes de enriquecer.
4. Mensajes orientados a reenganchar al usuario con entradas pobres.

### Qué no toca todavía

- recordatorio programado automático
- vistas complejas por antigüedad o tendencia

### Criterio de éxito

- El usuario puede ver rápidamente qué ha guardado hace poco.
- El usuario puede identificar entradas pobres pendientes de enriquecer.

### Prueba manual

1. Guardar varias entradas de distinta calidad.
2. Pedir últimas entradas.
3. Pedir pendientes de enriquecer.
4. Verificar que la selección coincide con `calidad_resumen` y orden temporal.

### Prueba de regresión mínima

- estados siguen funcionando
- búsqueda y listados generales siguen funcionando

### Tests que OpenClaw deberá materializar

- test de vista últimas entradas
- test de vista pendientes de enriquecer
- test de filtrado por `calidad_resumen`
- regresión de estado y listado

### Riesgos

- mezclar mal estado funcional con pobreza de resumen
- salidas demasiado largas

### Decisión de salida

La base empieza a ayudar a priorizar qué revisar o enriquecer.

---

## Fase 15. Recordatorio diario de pendientes de enriquecer

### Objetivo

Añadir la función de recordatorio periódico para entradas con resumen pobre.

### Qué toca implementar

1. Generar un recordatorio diario a las 20:00.
2. Basarlo en entradas con `calidad_resumen: fallback` que sigan sin enriquecer.
3. Presentarlo de forma breve y útil.
4. Antes de implementar el mecanismo de programación, verificar cómo gestiona OpenClaw las tareas programadas de forma nativa y usar ese mecanismo. Si no existe un mecanismo nativo claro, detener y reportar antes de inventar una solución propia.

### Qué no toca todavía

- notificaciones complejas
- frecuencia configurable por usuario

### Criterio de éxito

- El recordatorio se genera una vez al día a la hora definida.
- Solo incluye entradas realmente pendientes de enriquecer.

### Prueba manual

1. Tener varias entradas con `fallback`.
2. Forzar o simular la ejecución del recordatorio.
3. Verificar que solo aparecen las entradas pendientes.

### Prueba de regresión mínima

- guardado y estados siguen funcionando
- vistas de pendientes siguen funcionando

### Tests que OpenClaw deberá materializar

- test de selección correcta de entradas fallback
- test de formato del recordatorio
- test de periodicidad configurada a las 20:00
- regresión de estados y vistas de pendientes

### Riesgos

- recordar entradas ya enriquecidas
- generar ruido excesivo
- implementar un scheduler propio cuando OpenClaw ya tiene uno nativo
- crear dependencias externas innecesarias para algo que ya resuelve la plataforma

### Decisión de salida

La base ya no solo almacena: también reengancha al usuario con lo pendiente.

---

## Fase 16. Paginación y navegación larga

### Objetivo

Permitir navegar proyectos o categorías con muchas entradas sin saturar Telegram.

### Qué toca implementar

1. Añadir offset o mecanismo equivalente.
2. Mostrar tramos claros de resultados.
3. Permitir "más", "siguiente página" o similares en la capa conversacional.

### Qué no toca todavía

- botones
- cursores complejos

### Criterio de éxito

- El usuario puede navegar resultados largos sin perder contexto.

### Prueba manual

1. Tener suficientes entradas para varias páginas.
2. Pedir primera página.
3. Pedir la siguiente.
4. Verificar que no hay solapamientos ni saltos incorrectos.

### Prueba de regresión mínima

- listados pequeños siguen funcionando igual
- búsqueda y filtrado siguen funcionando

### Tests que OpenClaw deberá materializar

- test de offset básico
- test de límites
- test de fin de resultados
- regresión de listados normales

### Riesgos

- perder contexto de navegación
- errores de paginación acumulativa

### Decisión de salida

Bitácora sigue siendo usable cuando la base crece.

---

## Fase 17. Nota personal y ampliación de tags en entradas existentes

### Objetivo

Hacer explícito el modelo de enriquecimiento progresivo.

### Qué toca implementar

1. Añadir nota personal a una entrada existente.
2. Ampliar tags en cualquier momento.
3. Si una entrada pobre se enriquece con nota del usuario, actualizar `calidad_resumen` a `usuario` si procede.

### Qué no toca todavía

- edición completa de todos los campos
- upsert sobre duplicados

### Criterio de éxito

- El usuario puede enriquecer entradas ya guardadas.
- La entrada conserva `id` y `fecha`.
- El sistema refleja el enriquecimiento correctamente.

### Prueba manual

1. Tomar una entrada `fallback`.
2. Añadir una nota personal.
3. Añadir uno o más tags.
4. Verificar el YAML y la nota personal resultante.

### Prueba de regresión mínima

- búsqueda sigue encontrando la entrada
- vistas por estado y pendientes siguen funcionando

### Tests que OpenClaw deberá materializar

- test de añadir nota personal
- test de ampliar tags
- test de cambio correcto de `calidad_resumen`
- regresión de búsqueda y vistas de pendientes

### Riesgos

- sobrescribir nota previa
- mezclar mal nota personal y resumen

### Decisión de salida

El modelo de enriquecimiento ya funciona de forma explícita.

---

## Fase 18. Duplicados inteligentes y canonicalización

### Objetivo

Reducir duplicados obvios con URLs equivalentes.

### Qué toca implementar

1. Canonicalización básica de URLs.
2. Comparación de duplicados sobre la URL canonicalizada.
3. Mantener comportamiento conservador si la canonicalización no es segura.

### Qué no toca todavía

- upsert automático
- reglas demasiado agresivas de equivalencia

### Criterio de éxito

- URLs obvias equivalentes ya no se guardan como duplicados separados.

### Prueba manual

1. Guardar un recurso de YouTube en formato corto.
2. Intentar guardar el mismo recurso en formato largo.
3. Verificar que se detecta como duplicado.

### Prueba de regresión mínima

- deduplicación exacta previa sigue funcionando
- guardado normal de URL distintas sigue funcionando

### Tests que OpenClaw deberá materializar

- test de canonicalización YouTube corto/largo
- test de trailing slash
- test de parámetros irrelevantes
- regresión de deduplicación exacta previa

### Riesgos

- sobrecanonicalizar y confundir recursos distintos

### Decisión de salida

La deduplicación es más útil sin dejar de ser conservadora.

---

## Fase 19. Upsert opt-in en duplicados

### Objetivo

Permitir que una nueva observación sobre una URL ya existente se añada a la misma entrada sin duplicarla.

### Qué toca implementar

1. Ofrecer fusión opcional cuando una URL ya existe.
2. Añadir la nueva observación a la nota personal existente con separación clara.
3. Mantener intactos los campos inmutables.

### Qué no toca todavía

- fusión automática silenciosa
- reescritura agresiva de estructura

### Criterio de éxito

- El usuario puede añadir una nueva observación a una entrada ya existente sin crear duplicado.

### Prueba manual

1. Guardar una URL.
2. Intentar guardarla de nuevo con nueva observación.
3. Aceptar la fusión.
4. Verificar que no se crea una nueva entrada y que la nota personal se amplía.

### Prueba de regresión mínima

- deduplicación sigue bloqueando si no se acepta la fusión
- búsqueda y lectura de la entrada siguen funcionando

### Tests que OpenClaw deberá materializar

- test de offer de upsert
- test de fusión correcta de nota
- test de no creación de entrada duplicada
- regresión de deduplicación y lectura

### Riesgos

- fusionar contenido donde no toca
- sobrescribir nota previa en vez de ampliarla

### Decisión de salida

El sistema puede absorber observaciones repetidas sobre el mismo recurso sin duplicar conocimiento.

---

## Fase 20. Edición completa de entradas y `fecha_actualizacion`

### Objetivo

Permitir mantenimiento real de entradas ya existentes.

### Qué toca implementar

1. Permitir actualizar:
   - `categoria`
   - `tipo`
   - `titulo`
   - `fuente`
2. Añadir `fecha_actualizacion` cuando proceda.
3. Mantener `id` y `fecha` inmutables.
4. Soportar, si es razonable, mover una entrada a otro proyecto.

### Qué no toca todavía

- rediseño completo de modelo
- edición libre del YAML completo por conversación

### Criterio de éxito

- Las entradas se pueden corregir sin recrearlas.
- La inmutabilidad de `id` y `fecha` se conserva.

### Prueba manual

1. Tomar una entrada existente.
2. Cambiar categoría.
3. Cambiar título.
4. Cambiar tipo si procede.
5. Verificar `fecha_actualizacion` y la conservación de `id` y `fecha`.

### Prueba de regresión mínima

- búsqueda sigue funcionando
- deduplicación sigue funcionando
- lectura del archivo sigue siendo correcta

### Tests que OpenClaw deberá materializar

- test de actualización de categoría
- test de actualización de título
- test de actualización de tipo y fuente
- test de conservación de campos inmutables
- test de `fecha_actualizacion`
- regresión de búsqueda, lectura y deduplicación

### Riesgos

- corrupción de YAML al actualizar múltiples campos
- pérdida accidental de campos opcionales

### Decisión de salida

Bitácora ya se puede mantener y corregir de forma natural.

---

## Fase 21. Capa conversacional fuerte y modo técnico

### Objetivo

Formalizar en la skill el comportamiento conversacional esperado y el modo técnico explícito.

### Qué toca implementar

1. Actualizar `SKILL.md` con reglas conversacionales claras.
2. Definir comportamiento ante:
   - falta de proyecto
   - falta de categoría
   - duplicados
   - entrada pobre
   - enriquecimiento posterior
3. Activar un modo técnico explícito.

### Qué no toca todavía

- agente complejo con memoria conversacional profunda

### Criterio de éxito

- La skill se comporta de forma predecible y alineada con la filosofía v0.2.

### Prueba manual

1. Probar varias capturas ambiguas.
2. Verificar que la skill pregunta o propone de forma coherente.
3. Probar modo técnico y salida humana.

### Prueba de regresión mínima

- flujos normales de guardado y lectura siguen funcionando

### Tests que OpenClaw deberá materializar

- test de faltante de proyecto
- test de faltante de categoría
- test de duplicado con respuesta conversacional correcta
- test de modo técnico
- regresión de guardado y lectura

### Riesgos

- `SKILL.md` demasiado largo o ambiguo
- contradicciones entre skill y scripts

### Decisión de salida

La capa conversacional queda alineada con la arquitectura y el producto esperado.

---

## Fase 22. Limpieza final y mantenimiento del histórico

### Objetivo

Cerrar la v0.2 con limpieza documental y de datos no estructurales.

### Qué toca implementar

1. Evitar repeticiones innecesarias como URL en `fuente` y nota si son idénticas y no aportan valor.
2. Limpiar el log de desarrollo si procede.
3. Revisar ejemplos y documentación final.

### Qué no toca todavía

- cambios incompatibles de formato
- rediseños profundos

### Criterio de éxito

- La base se ve limpia y consistente.
- No hay artefactos de desarrollo innecesarios.

### Prueba manual

1. Revisar varios archivos de proyecto.
2. Revisar el log.
3. Verificar que no se ha roto nada por los ajustes de limpieza.

### Prueba de regresión mínima

- lectura, guardado, búsqueda, estados, edición y deduplicación siguen funcionando

### Tests que OpenClaw deberá materializar

- test de no pérdida de información por limpieza
- regresión global de todas las fases anteriores relevantes

### Riesgos

- limpiar demasiado y perder trazabilidad útil

### Decisión de salida

La versión 0.2 queda cerrada en estado consistente y limpio.

---

## Nota final

Este plan debe servir como base para que OpenClaw materialice luego los tests ejecutables por fase, tal como ya se hizo en la v1. La especificación completa de fases y validación queda definida aquí para evitar olvidos o improvisación posterior.

---

# PARTE IV — CONTENIDO PROPUESTO PARA `bitacora_changelog.md`

# bitacora_changelog.md

## v0.2

Pendiente de implementación.

### Cambios previstos
- nuevo formato de entrada con YAML como fuente de verdad y nota personal en Markdown
- nuevos campos `calidad_resumen` y `estado`
- migración de entradas antiguas de `camper.md`
- proyecto siempre preguntado primero, nunca inferido silenciosamente
- metadata externa ligera con timeout duro y fallback seguro
- resúmenes honestos
- salida humana para Telegram
- estados funcionales
- pendientes de enriquecer y recordatorio diario a las 20:00 usando mecanismo nativo de OpenClaw
- paginación
- edición real de entradas
- duplicados inteligentes y upsert opcional
- refuerzo de la capa conversacional
