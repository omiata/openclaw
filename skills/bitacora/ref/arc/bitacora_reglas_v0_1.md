# bitacora_reglas.md
# Reglas de Oro: Implementación de la skill bitacora

Estas reglas son de **obligado cumplimiento**. Son restricciones de diseño que prevalecen sobre cualquier decisión menor tomada en borradores anteriores. No son sugerencias.

---

## Regla 1. Simplicidad primero en las Fases 1 a 5

El sistema debe empezar siendo lo más pequeño posible.

Durante las Fases 1 a 5, el archivo de datos de cada proyecto debe contener únicamente los bloques de las entradas. Queda **prohibido** introducir en esas fases:

- cabeceras complejas,
- metadatos globales mantenidos automáticamente,
- índices de categorías,
- índices de tipos,
- secciones auxiliares que compliquen la escritura.

Todo eso, si alguna vez resulta útil, se pospone a la Fase 6.

---

## Regla 2. Un archivo por proyecto

La información se organiza por proyectos, no por categorías externas.

Cada proyecto tendrá su propio archivo maestro:

- `camper.md`
- `balcon.md`
- `recetas.md`
- `poesia.md`

Las categorías son etiquetas internas dentro de cada archivo. No deben convertirse en carpetas ni en archivos separados dentro de la V1.

---

## Regla 3. Formato híbrido obligatorio

Cada entrada debe combinar dos capas:

1. **YAML Frontmatter** entre líneas `---` para los campos estructurados.
2. **Markdown libre** debajo para el contenido legible (título, resumen, nota del usuario).

Los campos estructurados deben poder leerse de forma robusta por máquina. El contenido libre debe seguir siendo cómodo de inspeccionar y editar por una persona.

---

## Regla 4. Delimitador de entradas fijo e inviolable

Cada entrada debe estar separada de la siguiente por el delimitador exacto:

```
---entry---
```

seguido de una línea en blanco.

Reglas críticas:

- El agente debe conocer este delimitador antes de escribir la primera entrada.
- Este delimitador nunca debe aparecer dentro del contenido de una entrada.

---

## Regla 5. IDs únicos y autónomos

Queda **prohibido** usar IDs secuenciales (001, 002, ENTRY-001...).

Los IDs deben poder generarse en memoria sin necesidad de leer el archivo completo.

Formato preferido: Unix timestamp de alta precisión.

Ejemplo válido: `entry-1712613864123`

---

## Regla 6. Campos inmutables

Una vez creada una entrada, estos campos **no pueden modificarse**:

- `id`
- `fecha` (fecha de creación original)

El resto puede corregirse o ampliarse. Si se quiere registrar cuándo se modificó una entrada, puede añadirse un campo opcional `fecha_actualizacion`, sin tocar la fecha original.

---

## Regla 7. Inserción segura por append

Las nuevas entradas se añaden siempre al **final del archivo** del proyecto mediante append directo. No se reordena el archivo para mantener cronología inversa. Si el usuario quiere ver primero lo más reciente, ese reordenamiento se hace dinámicamente en la lectura, nunca en la escritura.

---

## Regla 8. Atomicidad de escritura para modificaciones

La Regla 7 (append) aplica exclusivamente a la **inserción de entradas nuevas**.

Para cualquier operación que implique **modificar o reescribir** el contenido existente del archivo (por ejemplo, actualizar una entrada existente), el sistema debe:

1. Leer el contenido completo del archivo original.
2. Generar el contenido modificado en memoria.
3. Escribir ese contenido en un **archivo temporal**.
4. Solo reemplazar el archivo original por el temporal si la escritura ha terminado sin errores.

Si algo falla a mitad del proceso:

- El archivo original no debe tocarse.
- El usuario debe recibir un mensaje claro de error.
- La operación no debe darse por exitosa.

---

## Regla 9. Codificación y formato de archivo

Todos los archivos de datos deben usar obligatoriamente:

- **UTF-8 sin BOM**
- **Saltos de línea LF** (Unix), nunca CRLF

---

## Regla 10. Comportamiento ante errores de lectura

Si un archivo contiene una entrada con YAML inválido o bloque corrupto, el sistema debe:

1. Avisar al usuario con detalle.
2. Identificar la entrada problemática por `id` si es posible, o por posición si no lo es.
3. Continuar procesando el resto de entradas válidas.
4. No fallar silenciosamente.
5. No detener toda la operación por una única entrada corrupta.

---

## Regla 11. Control de versiones del código

- El código de la skill debe vivir en un directorio dedicado, separado de los archivos `.md` de datos.
- Antes de iniciar la Fase 0, comprobar si ya existe un repositorio Git en algún directorio ancestro del workspace. Si existe, usarlo. Solo ejecutar `git init` si no hay ningún repo Git en ningún directorio padre.
- El `.gitignore` debe ignorar únicamente los archivos de datos del proyecto, no todos los `.md` del árbol. La regla debe acotarse a la ruta concreta de datos decidida en Fase 0, por ejemplo `data/*.md` o `skills/bitacora/data/*.md`. No usar `*.md` como patrón global, ya que ignoraría también los archivos de referencia de la skill.
- Un commit por función individual que pase su prueba mínima. No un único commit por fase completa.

Ejemplo de mensaje adecuado:
```
feat: guardado básico de entrada con proyecto y categoría
```

---

## Regla 12. Desarrollo incremental y regresión obligatoria

Cada fase debe dejar un sistema usable por sí mismo.

Antes de dar una fase por terminada, es **obligatorio** comprobar que el nuevo código no ha roto la capacidad de guardar o leer correctamente las entradas de fases anteriores.

---

## Regla 13. Caso de borde obligatorio desde el inicio

Desde la Fase 0, el sistema debe comportarse correctamente en estos dos casos:

- El archivo del proyecto **todavía no existe** → crearlo limpio.
- El archivo del proyecto **ya existe y tiene entradas previas** → no romper nada.

Ambos casos deben formar parte explícita de los tests de cada fase. En modo autónomo se verifican mediante los tests ejecutables del Apéndice A.3. En modo asistido se verifican mediante las pruebas manuales descritas en cada fase.

---

## Nota de uso

Estas reglas deben estar presentes cuando se trabaja con Codex o con OpenClaw en cualquier fase de implementación.

Si una tarea propuesta entra en conflicto con alguna de estas reglas, debe revisarse la tarea, no las reglas.
