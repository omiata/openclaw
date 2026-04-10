# bitacora_maestro.md
# Documento maestro: Knowledge Base de Proyectos (skill bitacora)

**Version:** 1.1 - draft documental para v0.2
**Uso:** Este documento define la vision funcional, la filosofia y las decisiones de diseno de la skill bitacora para la ronda v0.2. Es el documento al que se consulta cuando hay dudas sobre comportamiento esperado o criterios de diseno. No es un plan de ejecucion. No debe darse a Codex para que lo implemente de una sola vez.

---

## 1. Proposito general

Se quiere convertir OpenClaw en una **bandeja de entrada inteligente** para proyectos personales del usuario.

El flujo deseado sigue siendo simple en esencia:

1. El usuario envia al bot de Telegram un link, una nota, una idea, un documento o una referencia.
2. El sistema confirma el proyecto destino si falta y asegura una categoria explicita antes de guardar.
3. El sistema guarda esa informacion en la knowledge base del proyecto correspondiente.
4. Mas adelante, el usuario puede pedir que se le muestre lo guardado, completo o filtrado por categoria, tipo de recurso, estado o busqueda.
5. El usuario puede enriquecer posteriormente las entradas pobres y revisar lo pendiente.

El objetivo sigue siendo crear una **knowledge base personal, practica, controlable y facil de mantener**. No un second brain complejo, no una arquitectura semantica avanzada, no una base de datos pesada.

---

## 2. Que problema resuelve

Cuando el usuario encuentra recursos utiles sobre un proyecto, existe el riesgo de que:

- se pierdan en chats o favoritos dispersos,
- no queden asociados claramente al proyecto,
- no se puedan recuperar bien mas tarde,
- no tengan una clasificacion consistente,
- no exista una vista unica y acumulativa de lo ya recopilado,
- o se acumulen entradas pobres cuyo valor real sea dificil de recuperar despues.

La skill bitacora debe resolver exactamente eso: captura rapida, almacenamiento estructurado, recuperacion sencilla, bajo mantenimiento, maximo control por parte del usuario y una forma clara de distinguir entre captura minima y conocimiento ya enriquecido.

---

## 3. Filosofia de diseno

### 3.1 Simplicidad primero

La solucion debe empezar siendo deliberadamente pequena. No se busca una arquitectura teoricamente perfecta desde el principio, sino una solucion que funcione de forma fiable y que se pueda entender facilmente incluso meses despues.

### 3.2 El usuario manda el proyecto y la categoria

La clasificacion principal no debe depender de que el sistema adivine demasiado.

En v0.2 esto queda cerrado asi:

1. Si falta el proyecto, el sistema lo pregunta siempre primero.
2. La categoria sigue siendo explicita y obligatoria.
3. El sistema puede ayudar con sugerencias, pero el proyecto y la categoria confirmados por el usuario tienen prioridad.

### 3.3 Markdown legible y controlable

La base de conocimiento debe vivir en archivos faciles de leer, inspeccionar, editar y respaldar.

### 3.4 No sobrearquitecturar al principio

No es necesario dividir la informacion en multiples carpetas o archivos por categoria. Un archivo por proyecto, con buena estructura interna, sigue siendo suficiente.

### 3.5 Estructura interna mejor que fragmentacion externa

En vez de dispersar la informacion en numerosos archivos, tiene mas sentido priorizar una buena estructura interna dentro del archivo de cada proyecto.

### 3.6 Robustez sobre automatizacion

Cuando haya conflicto entre "hacer magia" y "hacer algo robusto", debe ganar la robustez.

La prioridad de diseno, en este orden:
1. fiabilidad,
2. claridad,
3. consistencia,
4. facilidad de inspeccion manual,
5. comodidad de uso,
6. automatizacion adicional.

### 3.7 Enriquecimiento progresivo

Una entrada puede empezar siendo pobre y enriquecerse despues. Bitacora no debe exigir perfeccion en la captura inicial, pero si debe reflejar con honestidad el nivel real de calidad de cada entrada.

### 3.8 Salida humana por defecto

La salida visible al usuario debe ser limpia, natural y orientada a Telegram. La informacion tecnica solo debe aparecer cuando el usuario la pida de forma explicita.

---

## 4. Scope y nombre de la skill

La skill se llama **bitacora**.

No esta ligada a un unico proyecto. Es una skill **generica de knowledge base por proyecto**, capaz de gestionar proyectos distintos como:

- camper
- balcon
- poesia
- bicicleta
- recetas
- y otros futuros

El campo `proyecto` es un valor dinamico. `camper` es solo un ejemplo.

---

## 5. Workspace real

El workspace real del usuario donde debe instalarse y ejecutarse la skill es:

```text
/mnt/c/omi/openclaw/
```

Cualquier decision de rutas para el codigo de la skill, los archivos de referencia y los archivos de datos debe formularse en relacion con ese workspace, no con ejemplos genericos.

La ubicacion exacta dentro de ese workspace debe ser evaluada y justificada por Codex antes de implementar, atendiendo a criterios de coherencia con la estructura de OpenClaw, separacion entre logica y datos, facilidad de backup e inspeccion manual.

---

## 6. Resultado esperado desde el punto de vista del usuario

### Guardar
- "Guarda este link en camper, categoria aislamiento."
- "Anade esta idea a camper en electricidad."
- "Guarda este video para la camper, tema distribucion."
- "https://youtu.be/xxx"
  - Si falta el proyecto, el sistema debe preguntar primero por el proyecto.

### Consultar
- "Ensename todo lo guardado sobre aislamiento."
- "Lista los videos que tengo guardados para la camper."
- "Busca dentro de camper lo relacionado con cama plegable."
- "Ensename lo nuevo de camper."
- "Que tengo pendiente de enriquecer."

### Revisar y enriquecer
- "Que tengo guardado de electricidad."
- "Cuales son los ultimos recursos anadidos a camper."
- "Marca esta entrada como revisada."
- "Anade una nota personal a esta entrada."

---

## 7. Alcance funcional hasta v0.2

### Incluido hasta v0.2
- Guardar entradas en la knowledge base de un proyecto.
- Preguntar siempre primero por el proyecto cuando falte.
- Exigir categoria explicita antes de guardar.
- Registrar tipo de recurso.
- Mantener un formato de entrada consistente y legible.
- Migrar las 4 entradas antiguas de `camper.md` al nuevo formato antes de las mejoras dependientes.
- Incorporar `calidad_resumen` y `estado` como campos oficiales.
- Permitir consulta por categoria, tipo, estado y listado global por proyecto.
- Permitir busqueda textual simple.
- Mostrar ultimas entradas y pendientes de enriquecer.
- Permitir enriquecer entradas existentes mediante nota personal y ampliacion de tags.
- Aplicar metadata externa ligera con timeout duro y fallback seguro.
- Mantener salida humana por defecto y modo tecnico explicito.
- Definir recordatorio diario a las 20:00 usando el mecanismo nativo de OpenClaw.

### Posiblemente incluido si no complica demasiado
- Canonicalizacion conservadora de URLs para duplicados obvios.
- Upsert opt-in cuando una URL ya existe.
- Paginacion simple en listados largos.
- `fecha_actualizacion` para mantenimiento de entradas.

### No prioritario para v0.2
- Resumenes avanzados de videos de YouTube.
- Extraccion compleja de metadatos.
- Clasificacion automatica sofisticada.
- Embeddings, vector DB o RAG avanzado.
- Varios archivos por categoria.
- Priorizacion inteligente compleja.
- Configuracion avanzada por usuario del recordatorio.

---

## 8. Modelo de persistencia

La informacion se organiza **por proyecto**, usando un archivo por proyecto:

- `camper.md`
- `balcon.md`
- `poesia.md`
- `bicicleta.md`

Queda descartado un unico archivo general para todos los proyectos. Las categorias son etiquetas internas dentro de cada archivo. No se convierten en carpetas ni en archivos separados dentro de la V1 ni de la v0.2.

---

## 9. Modelo de entrada

Cada recurso guardado se convierte en una entrada homogenea con estos campos.

### Campos obligatorios en v0.2
- `id` - identificador unico autonomo, inmutable
- `fecha` - fecha y hora de guardado, inmutable
- `proyecto` - nombre del proyecto destino
- `categoria` - eje principal de organizacion
- `tipo` - tipo de recurso
- `titulo` - breve y claro
- `resumen` - una a tres lineas o fallback minimo honesto
- `calidad_resumen` - `fallback`, `auto` o `usuario`
- `estado` - `nuevo`, `revisado` o `descartado`

### Campos opcionales en v0.2
- `fuente` - URL o descripcion del origen
- `tags` - lista opcional
- `contenido_adicional` - nota libre del usuario cuando siga siendo util internamente
- `fecha_actualizacion` - para futuras ediciones

---

## 10. Formato de cada entrada

Cada entrada usa un **formato hibrido**:

1. **YAML Frontmatter** entre lineas `---` para los campos estructurados.
2. **Markdown libre** debajo para la nota personal del usuario.

En v0.2 el YAML pasa a ser la fuente unica de verdad para los campos estructurados. El bloque Markdown ya no repite titulo, resumen o fuente.

Ejemplo conceptual:

```markdown
---entry---

---
id: entry-1712613864123
fecha: 2026-04-08T21:15:30.123Z
proyecto: camper
categoria: aislamiento
tipo: video
titulo: Aislamiento con XPS en Transit Custom
resumen: Resumen automatico o fallback minimo honesto.
fuente: https://...
tags: [xps, suelo, paredes]
calidad_resumen: fallback
estado: nuevo
---

**Nota personal**
Especialmente interesante la parte de como resuelven los huecos estructurales.
```

El delimitador `---entry---` seguido de linea en blanco separa cada entrada. Es fijo e inviolable. Nunca debe aparecer dentro del contenido de una entrada.

---

## 11. Politica de IDs

- Prohibido usar IDs secuenciales.
- El ID debe poder generarse en memoria sin leer el archivo.
- Formato preferido: Unix timestamp de alta precision.
- Ejemplo valido: `entry-1712613864123`
- Una vez creado, el ID es inmutable.

---

## 12. Categorias

Sistema semi-controlado:
- existe una lista base recomendada,
- el usuario puede introducir una categoria nueva,
- el sistema intenta mantener consistencia,
- y puede sugerir normalizacion ante variantes proximas.

Si el proyecto ya esta claro pero falta la categoria, el sistema debe pedirla o proponer categorias frecuentes del proyecto. Nunca debe guardar silenciosamente sin categoria.

### Lista base inicial (proyecto camper)
- aislamiento
- cama
- distribucion
- almacenamiento
- electricidad
- iluminacion
- ventilacion
- cocina
- agua
- moto
- fijaciones-estructura
- homologacion
- herramientas-materiales
- ideas-generales

### Reglas de normalizacion
1. Preferir minusculas.
2. Preferir singular o formato fijo consistente.
3. Evitar variantes triviales del mismo concepto.
4. Si el usuario escribe una variante proxima, proponer la categoria existente.
5. Si el usuario insiste, guardar la categoria nueva.

---

## 13. Tipos de recurso

Lista inicial:
- `link` - paginas web, articulos, foros, posts
- `video` - YouTube u otras plataformas
- `documento` - PDFs, manuales, archivos descargables
- `nota` - observaciones propias, apuntes tecnicos
- `idea` - propuestas o conceptos no verificados
- `referencia` - recursos que no encajan bien en otro tipo

---

## 14. Operaciones funcionales minimas

### Guardar
1. Confirmar proyecto destino. Si falta, preguntarlo primero.
2. Resolver categoria. Si falta, pedirla o proponer opciones.
3. Resolver tipo.
4. Generar ID autonomo no secuencial.
5. Registrar fecha de alta.
6. Intentar extraer metadata ligera si hay URL, con timeout duro y sin bloquear el guardado.
7. Generar titulo y resumen honestos si hace falta.
8. Asignar `calidad_resumen`.
9. Asignar `estado: nuevo`.
10. Comprobar duplicado basico si hay URL.
11. Crear entrada con formato estable.
12. Anadirla al final del archivo del proyecto mediante escritura segura.
13. Confirmar al usuario que se ha guardado en formato humano.

### Mostrar categoria
- Aceptar categoria exacta o tolerar variaciones obvias.
- Devolver entradas ordenadas por fecha.
- Mostrar primero un resumen de cuantas hay.

### Listar todo
- Indicar numero total de entradas.
- Opcionalmente agrupar por categoria o estado.
- No volcar el archivo completo si es muy largo.

### Buscar
- Buscar en titulo, resumen, tags y contenido adicional o nota personal cuando aplique.
- Devolver coincidencias con contexto corto.
- Permitir luego mostrar la entrada completa.

### Listar por tipo
- Permitir preguntas como "ensename todos los videos" o "que ideas tengo guardadas".

### Consultas operativas de v0.2
- Permitir listar por `estado`.
- Permitir ver ultimas entradas.
- Permitir ver entradas con `calidad_resumen: fallback`.
- Permitir distinguir entre capturas pobres y entradas enriquecidas.

---

## 15. Convenciones de interaccion

### Para guardar
- `guarda esto en camper, categoria aislamiento`
- `guarda esto en camper, categoria cama, tipo video`
- `anade a camper en electricidad`
- `guarda esta idea en camper, categoria distribucion, tags cama-plegable, modular`
- `https://youtu.be/xxx`
  - Respuesta esperada si falta contexto: `En que proyecto guardo esto?`

### Para consultar
- `ensename camper`
- `ensename camper, categoria aislamiento`
- `lista camper, tipo video`
- `busca en camper: cama plegable`
- `lista camper, estado revisado`
- `que tengo pendiente de enriquecer en camper`

---

## 16. Gestion de duplicados

- Si una entrada trae una URL y esa URL exacta ya existe en el archivo, detectarlo.
- Avisar al usuario que ya existe.
- No duplicar automaticamente.
- Ofrecer actualizar tags, resumen o nota si el usuario quiere.
- En v0.2 puede aplicarse una normalizacion conservadora de URL antes de comparar, siempre que no aumente el riesgo de fusionar recursos distintos por error.

---

## 17. Salida al usuario

La salida debe ser practica para leer en Telegram.

- Para listados: formato resumido y humano.
- Para una entrada concreta: formato ampliado.
- Para busqueda: vista de coincidencias con contexto.
- No mostrar por defecto IDs, rutas fisicas ni fechas ISO crudas en vistas normales.
- Reservar la salida tecnica a un modo explicito.

No volcar bloques enormes si el usuario solo pide una vista rapida.

---

## 18. Estrategia de mantenimiento del archivo

- Nunca romper el formato historico de las entradas existentes sin una migracion explicita.
- Evitar reordenaciones innecesarias de todo el archivo.
- Insertar entradas nuevas siempre al final, mediante append seguro.
- La fuente unica de verdad es el listado maestro de entradas.
- Los indices o resumenes son derivados y secundarios.
- La migracion de las 4 entradas antiguas de `camper.md` al nuevo formato debe ocurrir antes de las mejoras que dependan del nuevo esquema.
- Toda migracion o reescritura debe ser atomica y conservadora.

---

## 19. Escalabilidad futura

El archivo unico por proyecto es la decision correcta para la V1 y sigue siendolo en v0.2, pero no es una decision arquitectonica definitiva. Si el volumen crece demasiado, podra activarse una politica de rotacion de archivos sin romper el modelo funcional:

- `camper_2026.md`
- `camper_2027.md`
- `camper_2026_Q1.md`

La experiencia funcional para el usuario debe seguir siendo la misma independientemente del contenedor fisico.

---

## 20. Reglas de generacion del titulo

1. Debe ser breve y claro.
2. Debe describir de que trata el recurso.
3. No debe depender de frases vagas como "video interesante".
4. Si la fuente ya trae un titulo bueno, puede reutilizarse.
5. Si el titulo original es malo o largo, debe resumirse.
6. Si el usuario da un titulo explicito, ese prevalece siempre.
7. En v0.2, si existe metadata externa util, puede usarse con prioridad sobre un titulo pobre inferido del contenido.

---

## 21. Reglas de generacion del resumen

- Entre una y tres lineas cortas cuando exista contexto suficiente.
- Debe capturar: que es, por que es relevante, que aspecto concreto puede interesar al proyecto.
- Debe evitar: copiar texto bruto, repetir solo el titulo, usar frases vacias, inventar detalles.
- Si solo hay URL o contexto insuficiente, debe usarse un fallback minimo honesto.
- La entrada debe marcarse con `calidad_resumen: fallback`, `auto` o `usuario` segun corresponda.

---

## 22. Decisiones cerradas

1. Un unico archivo por proyecto en la V1 y en v0.2.
2. Las entradas mantienen estructura explicita en formato hibrido YAML + Markdown.
3. El YAML pasa a ser la fuente unica de verdad para los campos estructurados en v0.2.
4. La categoria es obligatoria y central.
5. El proyecto nunca se infiere silenciosamente si falta; se pregunta primero.
6. El tipo de recurso es un campo explicito.
7. Los tags son secundarios y opcionales.
8. `calidad_resumen` y `estado` pasan a formar parte del modelo oficial.
9. El listado maestro cronologico es la base real del sistema.
10. La interaccion debe seguir siendo sencilla y explicita.
11. La deduplicacion sigue siendo conservadora.
12. La extraccion de metadata externa es ligera, con timeout duro y fallback seguro.
13. La salida por defecto es humana y limpia.
14. El modo tecnico es explicito.
15. El recordatorio de pendientes de enriquecer sera diario a las 20:00, usando el mecanismo nativo de OpenClaw.
16. Las 4 entradas antiguas de `camper.md` se migran en la Fase 7 antes de las mejoras que dependan del nuevo esquema.
17. La arquitectura debera poder evolucionar a rotacion de archivos si el tamano lo exige.
18. El workspace real es `/mnt/c/omi/openclaw/`.
19. La skill se llama bitacora y es generica para multiples proyectos.

---

## 23. Preguntas que debe resolver Codex antes de implementar

1. Cual es la mejor ubicacion para la skill dentro de `/mnt/c/omi/openclaw/`?
2. Cual es la mejor ubicacion para los archivos de referencia de la skill?
3. Cual es la mejor ubicacion para los archivos de datos por proyecto?
4. Justificar brevemente esa decision antes de implementar.
5. No asumir rutas por defecto si no encajan con el workspace real.
6. Antes de implementar el recordatorio de la Fase 15, verificar como gestiona OpenClaw las tareas programadas de forma nativa y usar ese mecanismo. Si no existe uno claro, detener y reportar.

---

## 24. Como usar este documento

Este documento es de **referencia y consulta**, no de ejecucion.

- Usalo para resolver dudas sobre comportamiento esperado.
- Usalo para verificar que una decision tecnica encaja con la filosofia del sistema.
- No lo des a Codex para que lo implemente entero de una sola vez.
- Durante esta ronda documental, el documento operativo complementario es `bitacora_fases_v0_2_draft.md`.
