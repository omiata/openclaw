# bitacora_reglas.md
# Reglas de Oro: Implementacion de la skill bitacora

Estas reglas son de **obligado cumplimiento**. Son restricciones de diseno que prevalecen sobre cualquier decision menor tomada en borradores anteriores. No son sugerencias.

---

## Regla 1. Simplicidad primero en las Fases 1 a 5

El sistema debe empezar siendo lo mas pequeno posible.

Durante las Fases 1 a 5, el archivo de datos de cada proyecto debe contener unicamente los bloques de las entradas. Queda **prohibido** introducir en esas fases:

- cabeceras complejas,
- metadatos globales mantenidos automaticamente,
- indices de categorias,
- indices de tipos,
- secciones auxiliares que compliquen la escritura.

Todo eso, si alguna vez resulta util, se pospone a la Fase 6.

---

## Regla 2. Un archivo por proyecto

La informacion se organiza por proyectos, no por categorias externas.

Cada proyecto tendra su propio archivo maestro:

- `camper.md`
- `balcon.md`
- `recetas.md`
- `poesia.md`

Las categorias son etiquetas internas dentro de cada archivo. No deben convertirse en carpetas ni en archivos separados dentro de la V1.

---

## Regla 3. Formato hibrido obligatorio

Cada entrada debe combinar dos capas:

1. **YAML Frontmatter** entre lineas `---` para los campos estructurados.
2. **Markdown libre** debajo para el contenido legible.

Los campos estructurados deben poder leerse de forma robusta por maquina. El contenido libre debe seguir siendo comodo de inspeccionar y editar por una persona.

En v0.2, el YAML pasa a ser la fuente unica de verdad para los datos estructurados y el bloque Markdown queda reservado a la nota personal del usuario. No se debe volver a introducir redundancia de titulo, resumen o fuente fuera del YAML.

---

## Regla 4. Delimitador de entradas fijo e inviolable

Cada entrada debe estar separada de la siguiente por el delimitador exacto:

```text
---entry---
```

seguido de una linea en blanco.

Reglas criticas:

- El agente debe conocer este delimitador antes de escribir la primera entrada.
- Este delimitador nunca debe aparecer dentro del contenido de una entrada.

---

## Regla 5. IDs unicos y autonomos

Queda **prohibido** usar IDs secuenciales (001, 002, ENTRY-001...).

Los IDs deben poder generarse en memoria sin necesidad de leer el archivo completo.

Formato preferido: Unix timestamp de alta precision.

Ejemplo valido: `entry-1712613864123`

---

## Regla 6. Campos inmutables

Una vez creada una entrada, estos campos **no pueden modificarse**:

- `id`
- `fecha` (fecha de creacion original)

El resto puede corregirse o ampliarse. Si se quiere registrar cuando se modifico una entrada, puede anadirse un campo opcional `fecha_actualizacion`, sin tocar la fecha original.

---

## Regla 7. Insercion segura por append

Las nuevas entradas se anaden siempre al **final del archivo** del proyecto mediante append directo. No se reordena el archivo para mantener cronologia inversa. Si el usuario quiere ver primero lo mas reciente, ese reordenamiento se hace dinamicamente en la lectura, nunca en la escritura.

---

## Regla 8. Atomicidad de escritura para modificaciones

La Regla 7 (append) aplica exclusivamente a la **insercion de entradas nuevas**.

Para cualquier operacion que implique **modificar o reescribir** el contenido existente del archivo (por ejemplo, actualizar una entrada existente), el sistema debe:

1. Leer el contenido completo del archivo original.
2. Generar el contenido modificado en memoria.
3. Escribir ese contenido en un **archivo temporal**.
4. Solo reemplazar el archivo original por el temporal si la escritura ha terminado sin errores.

Si algo falla a mitad del proceso:

- El archivo original no debe tocarse.
- El usuario debe recibir un mensaje claro de error.
- La operacion no debe darse por exitosa.

---

## Regla 9. Codificacion y formato de archivo

Todos los archivos de datos deben usar obligatoriamente:

- **UTF-8 sin BOM**
- **Saltos de linea LF** (Unix), nunca CRLF

---

## Regla 10. Comportamiento ante errores de lectura

Si un archivo contiene una entrada con YAML invalido o bloque corrupto, el sistema debe:

1. Avisar al usuario con detalle.
2. Identificar la entrada problematica por `id` si es posible, o por posicion si no lo es.
3. Continuar procesando el resto de entradas validas.
4. No fallar silenciosamente.
5. No detener toda la operacion por una unica entrada corrupta.

---

## Regla 11. Control de versiones del codigo

- El codigo de la skill debe vivir en un directorio dedicado, separado de los archivos `.md` de datos.
- Antes de iniciar la Fase 0, comprobar si ya existe un repositorio Git en algun directorio ancestro del workspace. Si existe, usarlo. Solo ejecutar `git init` si no hay ningun repo Git en ningun directorio padre.
- El `.gitignore` debe ignorar unicamente los archivos de datos del proyecto, no todos los `.md` del arbol. La regla debe acotarse a la ruta concreta de datos decidida en Fase 0, por ejemplo `data/*.md` o `skills/bitacora/data/*.md`. No usar `*.md` como patron global, ya que ignoraria tambien los archivos de referencia de la skill.
- Un commit por funcion individual que pase su prueba minima. No un unico commit por fase completa.

Ejemplo de mensaje adecuado:
```text
feat: guardado basico de entrada con proyecto y categoria
```

---

## Regla 12. Desarrollo incremental y regresion obligatoria

Cada fase debe dejar un sistema usable por si mismo.

Antes de dar una fase por terminada, es **obligatorio** comprobar que el nuevo codigo no ha roto la capacidad de guardar o leer correctamente las entradas de fases anteriores.

---

## Regla 13. Caso de borde obligatorio desde el inicio

Desde la Fase 0, el sistema debe comportarse correctamente en estos dos casos:

- El archivo del proyecto **todavia no existe** -> crearlo limpio.
- El archivo del proyecto **ya existe y tiene entradas previas** -> no romper nada.

Ambos casos deben formar parte explicita de los tests de cada fase. En modo autonomo se verifican mediante los tests ejecutables del Apendice A.3. En modo asistido se verifican mediante las pruebas manuales descritas en cada fase.

---

## Regla 14. Proyecto siempre preguntado primero

Si el usuario no indica proyecto, el sistema debe preguntar primero por el.

No se permite inferencia silenciosa del proyecto a partir del contenido.

---

## Regla 15. Categoria obligatoria

No se debe guardar una entrada sin categoria.

Si la categoria falta, el sistema debe pedirla o proponer categorias del proyecto antes de guardar.

---

## Regla 16. Campos obligatorios de v0.2

Toda entrada nueva o migrada al formato v0.2 debe incluir, ademas de los campos estructurados previos:

- `calidad_resumen`
- `estado`

Valores validos de `calidad_resumen`:
- `fallback`
- `auto`
- `usuario`

Valores validos de `estado`:
- `nuevo`
- `revisado`
- `descartado`

---

## Regla 17. Metadata externa opcional, con timeout y fallback seguro

La extraccion de metadata externa:

- es opcional,
- nunca bloquea el guardado,
- tiene timeout duro de 3 segundos,
- debe fallar de forma segura,
- no debe introducir dependencia fuerte de red.

Si falla, la entrada se guarda igualmente.

---

## Regla 18. Migracion obligatoria antes de mejoras dependientes

La migracion de las 4 entradas antiguas de `camper.md` al nuevo formato v0.2 debe realizarse antes de cualquier mejora funcional o de UX que dependa del nuevo esquema.

La Fase 8 no puede iniciarse hasta que la Fase 7 haya completado con exito.

Las Fases 9, 10, 13 y 14 requieren tambien que la Fase 7 haya completado con exito.

---

## Regla 19. Resumen honesto

No debe generarse un resumen que finja mas conocimiento del que realmente existe.

Si solo hay URL o contexto insuficiente, se debe usar un fallback minimo honesto y marcar la entrada con `calidad_resumen: fallback`.

---

## Regla 20. Compatibilidad durante la transicion

Durante la fase de migracion, el sistema debe seguir siendo capaz de:

- leer entradas antiguas si aun existieran,
- detectar inconsistencias sin detener todo el procesamiento,
- continuar operando sobre entradas validas aunque una concreta falle.

---

## Regla 21. Salida humana por defecto y modo tecnico explicito

La salida visible al usuario no debe exponer por defecto:

- rutas fisicas,
- fechas ISO crudas,
- banderas CLI,
- IDs en listados resumidos.

Todo eso queda reservado al modo tecnico explicito.

---

## Regla 22. Recordatorio programado con mecanismo nativo

La funcion de recordatorio de entradas pendientes de enriquecer debe configurarse para ejecutarse cada dia a las 20:00.

La generacion del recordatorio debe basarse exclusivamente en entradas con `calidad_resumen: fallback` que sigan sin enriquecer.

Antes de implementar el mecanismo de programacion, se debe verificar como gestiona OpenClaw las tareas programadas de forma nativa y usar ese mecanismo. Si no existe un mecanismo nativo claro, se detiene y se reporta antes de inventar una solucion propia.

---

## Regla 23. No modificar lo canonico sin aprobacion

Mientras se trabaja en v0.2 a nivel documental o experimental, los archivos canonicos no se sustituyen hasta revision y aprobacion.

---

## Regla 24. Definicion estricta de test valido

Un test es valido si y solo si:
1. Es ejecutable de forma autonoma.
2. Lee el estado real del archivo en disco DESPUES de la operacion.
3. Compara valores campo a campo contra los esperados.
4. Falla explicitamente si cualquier campo no coincide.
5. No puede pasar si el archivo no existe o esta vacio.

Un `assert True`, un `assert len(x) >= 0` o cualquier comprobacion que no pueda fallar NO es un test valido. Escribir un test trivial y pasarlo equivale a fallar la fase inmediatamente.

---

## Nota de uso

Estas reglas deben estar presentes cuando se trabaja con Codex o con OpenClaw en cualquier fase de implementacion.

Si una tarea propuesta entra en conflicto con alguna de estas reglas, debe revisarse la tarea, no las reglas.
