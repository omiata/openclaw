# bitacora_maestro.md
# Documento maestro: Knowledge Base de Proyectos (skill bitacora)

**Versión:** 1.0 — documento de referencia consolidado
**Uso:** Este documento define la visión funcional, la filosofía y las decisiones de diseño de la skill bitacora. Es el documento al que se consulta cuando hay dudas sobre comportamiento esperado o criterios de diseño. No es un plan de ejecución. No debe darse a Codex para que lo implemente de una sola vez.

---

## 1. Propósito general

Se quiere convertir OpenClaw en una **bandeja de entrada inteligente** para proyectos personales del usuario.

El flujo deseado es simple en esencia:

1. El usuario envía al bot de Telegram un link, una nota, una idea, un documento o una referencia.
2. El usuario indica a qué proyecto y categoría pertenece, o lo deja suficientemente claro en el mensaje.
3. El sistema guarda esa información en la knowledge base del proyecto correspondiente.
4. Más adelante, el usuario puede pedir que se le muestre lo guardado, completo o filtrado por categoría, tipo de recurso o búsqueda.

El objetivo es crear una **knowledge base personal, práctica, controlable y fácil de mantener**. No un second brain complejo, no una arquitectura semántica avanzada, no una base de datos pesada.

---

## 2. Qué problema resuelve

Cuando el usuario encuentra recursos útiles sobre un proyecto, existe el riesgo de que:

- se pierdan en chats o favoritos dispersos,
- no queden asociados claramente al proyecto,
- no se puedan recuperar bien más tarde,
- no tengan una clasificación consistente,
- no exista una vista única y acumulativa de lo ya recopilado.

La skill bitacora debe resolver exactamente eso: captura rápida, almacenamiento estructurado, recuperación sencilla, bajo mantenimiento y máximo control por parte del usuario.

---

## 3. Filosofía de diseño

### 3.1 Simplicidad primero

La solución debe empezar siendo deliberadamente pequeña. No se busca una arquitectura teóricamente perfecta desde el principio, sino una solución que funcione de forma fiable y que se pueda entender fácilmente incluso meses después.

### 3.2 El usuario manda la categoría

La clasificación principal no debe depender de que el sistema adivine demasiado. El usuario indica explícitamente la categoría. El sistema puede ayudar con sugerencias, pero la categoría explícita del usuario tiene prioridad.

### 3.3 Markdown legible y controlable

La base de conocimiento debe vivir en archivos fáciles de leer, inspeccionar, editar y respaldar.

### 3.4 No sobrearquitecturar al principio

En la fase inicial no es necesario dividir la información en múltiples carpetas o archivos por categoría. Un archivo por proyecto, con buena estructura interna, es suficiente.

### 3.5 Estructura interna mejor que fragmentación externa

En vez de dispersar la información en numerosos archivos, tiene más sentido priorizar una buena estructura interna dentro del archivo de cada proyecto.

### 3.6 Robustez sobre automatización

Cuando haya conflicto entre "hacer magia" y "hacer algo robusto", debe ganar la robustez.

La prioridad de diseño, en este orden:
1. fiabilidad,
2. claridad,
3. consistencia,
4. facilidad de inspección manual,
5. comodidad de uso,
6. automatización adicional.

---

## 4. Scope y nombre de la skill

La skill se llama **bitacora**.

No está ligada a un único proyecto. Es una skill **genérica de knowledge base por proyecto**, capaz de gestionar proyectos distintos como:

- camper
- balcon
- poesia
- bicicleta
- y otros futuros

El campo `proyecto` es un valor dinámico. `camper` es solo un ejemplo.

---

## 5. Workspace real

El workspace real del usuario donde debe instalarse y ejecutarse la skill es:

```
/mnt/c/omi/openclaw/
```

Cualquier decisión de rutas para el código de la skill, los archivos de referencia y los archivos de datos debe formularse en relación con ese workspace, no con ejemplos genéricos.

La ubicación exacta dentro de ese workspace debe ser evaluada y justificada por Codex antes de implementar, atendiendo a criterios de coherencia con la estructura de OpenClaw, separación entre lógica y datos, facilidad de backup e inspección manual.

---

## 6. Resultado esperado desde el punto de vista del usuario

### Guardar
- "Guarda este link en camper, categoría aislamiento."
- "Añade esta idea a camper en electricidad."
- "Guarda este vídeo para la camper, tema distribución."

### Consultar
- "Enséñame todo lo guardado sobre aislamiento."
- "Lista los vídeos que tengo guardados para la camper."
- "Busca dentro de camper lo relacionado con cama plegable."

### Revisar
- "¿Qué tengo guardado de electricidad?"
- "¿Cuáles son los últimos recursos añadidos a camper?"

---

## 7. Alcance inicial de la función

### Incluido en la primera versión
- Guardar entradas en la knowledge base de un proyecto.
- Asignar proyecto y categoría principal.
- Registrar tipo de recurso.
- Permitir consulta por categoría.
- Permitir listado global por proyecto.
- Permitir búsqueda textual simple.
- Mantener formato consistente y legible.

### Posiblemente incluido si no complica demasiado
- Tags adicionales.
- Resumen corto automático.
- Fecha de alta automática.
- Detección básica de duplicados por URL exacta.

### No prioritario para la primera versión
- Resúmenes avanzados de vídeos de YouTube.
- Extracción compleja de metadatos.
- Clasificación automática sofisticada.
- Embeddings, vector DB o RAG avanzado.
- Varios archivos por categoría.
- Sistema de revisión espaciada o recordatorios.
- Priorización inteligente.

---

## 8. Modelo de persistencia

La información se organiza **por proyecto**, usando un archivo por proyecto:

- `camper.md`
- `balcon.md`
- `poesia.md`
- `bicicleta.md`

Queda descartado un único archivo general para todos los proyectos. Las categorías son etiquetas internas dentro de cada archivo. No se convierten en carpetas ni en archivos separados dentro de la V1.

---

## 9. Modelo de entrada

Cada recurso guardado se convierte en una entrada homogénea con estos campos:

### Campos obligatorios en V1
- `id` — identificador único autónomo, inmutable
- `fecha` — fecha y hora de guardado, inmutable
- `proyecto` — nombre del proyecto destino
- `categoria` — eje principal de organización
- `tipo` — tipo de recurso
- `titulo` — breve y claro
- `resumen` — una a tres líneas

### Campos opcionales en V1
- `fuente` — URL o descripción del origen
- `tags` — lista opcional
- `contenido_adicional` — nota libre del usuario
- `estado` — para uso futuro

---

## 10. Formato de cada entrada

Cada entrada usa un **formato híbrido**:

1. **YAML Frontmatter** entre líneas `---` para los campos estructurados.
2. **Markdown libre** debajo para el contenido legible (título, resumen, nota).

Ejemplo conceptual:

```markdown
---entry---

---
id: entry-1712613864123
fecha: 2026-04-08T21:15:30.123Z
proyecto: camper
categoria: aislamiento
tipo: video
fuente: https://...
tags: [xps, suelo, paredes]
estado: activo
---

**Título**
Aislamiento con XPS en Transit Custom

**Resumen**
Comparación práctica de espesores, puntos de condensación y montaje en furgoneta.

**Nota adicional**
Especialmente interesante la parte de cómo resuelven los huecos estructurales.
```

El delimitador `---entry---` seguido de línea en blanco separa cada entrada. Es fijo e inviolable. Nunca debe aparecer dentro del contenido de una entrada.

---

## 11. Política de IDs

- Prohibido usar IDs secuenciales.
- El ID debe poder generarse en memoria sin leer el archivo.
- Formato preferido: Unix timestamp de alta precisión.
- Ejemplo válido: `entry-1712613864123`
- Una vez creado, el ID es inmutable.

---

## 12. Categorías

Sistema semi-controlado:
- existe una lista base recomendada,
- el usuario puede introducir una categoría nueva,
- el sistema intenta mantener consistencia,
- y puede sugerir normalización ante variantes próximas.

### Lista base inicial (proyecto camper)
- aislamiento
- cama
- distribución
- almacenamiento
- electricidad
- iluminación
- ventilación
- cocina
- agua
- moto
- fijaciones-estructura
- homologación
- herramientas-materiales
- ideas-generales

### Reglas de normalización
1. Preferir minúsculas.
2. Preferir singular o formato fijo consistente.
3. Evitar variantes triviales del mismo concepto.
4. Si el usuario escribe una variante próxima, proponer la categoría existente.
5. Si el usuario insiste, guardar la categoría nueva.

---

## 13. Tipos de recurso

Lista inicial:
- `link` — páginas web, artículos, foros, posts
- `video` — YouTube u otras plataformas
- `documento` — PDFs, manuales, archivos descargables
- `nota` — observaciones propias, apuntes técnicos
- `idea` — propuestas o conceptos no verificados
- `referencia` — recursos que no encajan bien en otro tipo

---

## 14. Operaciones funcionales mínimas

### Guardar
1. Confirmar proyecto destino.
2. Resolver categoría.
3. Resolver tipo.
4. Generar ID autónomo no secuencial.
5. Generar título y resumen si hace falta.
6. Comprobar duplicado básico si hay URL.
7. Crear entrada con formato estable.
8. Añadirla al final del archivo del proyecto mediante escritura segura.
9. Confirmar al usuario qué se ha guardado.

### Mostrar categoría
- Aceptar categoría exacta o tolerar variaciones obvias.
- Devolver entradas ordenadas por fecha.
- Mostrar primero un resumen de cuántas hay.

### Listar todo
- Indicar número total de entradas.
- Opcionalmente agrupar por categoría.
- No volcar el archivo completo si es muy largo.

### Buscar
- Buscar en título, resumen, tags y contenido adicional.
- Devolver coincidencias con contexto corto.
- Permitir luego mostrar la entrada completa.

### Listar por tipo
- Permitir preguntas como "enséñame todos los vídeos" o "qué ideas tengo guardadas".

---

## 15. Convenciones de interacción

### Para guardar
- `guarda esto en camper, categoría aislamiento`
- `guarda esto en camper, categoría cama, tipo vídeo`
- `añade a camper en electricidad`
- `guarda esta idea en camper, categoría distribución, tags cama-plegable, modular`

### Para consultar
- `enséñame camper`
- `enséñame camper, categoría aislamiento`
- `lista camper, tipo video`
- `busca en camper: cama plegable`

---

## 16. Gestión de duplicados

- Si una entrada trae una URL y esa URL exacta ya existe en el archivo, detectarlo.
- Avisar al usuario que ya existe.
- No duplicar automáticamente.
- Ofrecer actualizar tags, resumen o nota si el usuario quiere.

---

## 17. Salida al usuario

La salida debe ser práctica para leer en Telegram.

- Para listados: formato resumido (título, categoría, tipo, fecha, resumen, fuente si existe).
- Para una entrada concreta: formato ampliado.
- Para búsqueda: vista de coincidencias con contexto.

No volcar bloques enormes si el usuario solo pide una vista rápida.

---

## 18. Estrategia de mantenimiento del archivo

- Nunca romper el formato histórico de las entradas existentes.
- Evitar reordenaciones innecesarias de todo el archivo.
- Insertar entradas nuevas siempre al final, mediante append seguro.
- La fuente única de verdad es el listado maestro de entradas.
- Los índices o resúmenes son derivados y secundarios.

---

## 19. Escalabilidad futura

El archivo único por proyecto es la decisión correcta para la V1, pero no es una decisión arquitectónica definitiva. Si el volumen crece demasiado, podrá activarse una política de rotación de archivos sin romper el modelo funcional:

- `camper_2026.md`
- `camper_2027.md`
- `camper_2026_Q1.md`

La experiencia funcional para el usuario debe seguir siendo la misma independientemente del contenedor físico.

---

## 20. Reglas de generación del título

1. Debe ser breve y claro.
2. Debe describir de qué trata el recurso.
3. No debe depender de frases vagas como "vídeo interesante".
4. Si la fuente ya trae un título bueno, puede reutilizarse.
5. Si el título original es malo o largo, debe resumirse.
6. Si el usuario da un título explícito, ese prevalece siempre.

---

## 21. Reglas de generación del resumen

- Entre una y tres líneas cortas.
- Debe capturar: qué es, por qué es relevante, qué aspecto concreto puede interesar al proyecto.
- Debe evitar: copiar texto bruto, repetir solo el título, usar frases vacías, inventar detalles.

---

## 22. Decisiones cerradas

1. Un único archivo por proyecto en la V1.
2. Las entradas tendrán estructura explícita en formato híbrido YAML + Markdown.
3. La categoría es obligatoria y central.
4. El tipo de recurso es un campo explícito.
5. Los tags son secundarios y opcionales.
6. El listado maestro cronológico es la base real del sistema.
7. La interacción será sencilla y explícita.
8. La deduplicación será básica.
9. Los IDs no serán secuenciales.
10. La arquitectura deberá poder evolucionar a rotación de archivos si el tamaño lo exige.
11. El workspace real es `/mnt/c/omi/openclaw/`.
12. La skill se llama bitacora y es genérica para múltiples proyectos.

---

## 23. Preguntas que debe resolver Codex antes de implementar

1. ¿Cuál es la mejor ubicación para la skill dentro de `/mnt/c/omi/openclaw/`?
2. ¿Cuál es la mejor ubicación para los archivos de referencia de la skill?
3. ¿Cuál es la mejor ubicación para los archivos de datos por proyecto?
4. Justificar brevemente esa decisión antes de implementar.
5. No asumir rutas por defecto si no encajan con el workspace real.

---

## 24. Cómo usar este documento

Este documento es de **referencia y consulta**, no de ejecución.

- Úsalo para resolver dudas sobre comportamiento esperado.
- Úsalo para verificar que una decisión técnica encaja con la filosofía del sistema.
- No lo des a Codex para que lo implemente entero de una sola vez.
- El documento operativo para Codex es `bitacora_fases.md`.
