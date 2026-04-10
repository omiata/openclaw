---
name: bitacora
description: Gestionar una knowledge base personal por proyecto en archivos Markdown, con captura, lectura, búsqueda, estados, enriquecimiento progresivo, deduplicación conservadora y recordatorios de entradas pobres. Usar cuando el usuario quiera guardar o consultar links, vídeos, notas, ideas o referencias para proyectos como camper, balcón, recetas, poesía o similares, especialmente si falta proyecto o categoría, hay duplicados, hace falta enriquecer una entrada existente o el usuario pide modo técnico explícito.
---

# Bitácora

Usar esta skill para guardar y mantener recursos por proyecto en `skills/bitacora/data/`, con un archivo `.md` por proyecto.

## Reglas conversacionales

- Preguntar siempre primero por el proyecto si falta.
- No guardar nada si falta la categoría.
- Proponer categorías frecuentes del proyecto cuando ayude, pero no inferir silenciosamente el destino.
- Si una URL ya existe, no crear un duplicado. Ofrecer fusión explícita de la nueva observación en la nota personal.
- Si la entrada queda pobre, dejar un resumen honesto y marcarla como pendiente de enriquecer.
- Permitir enriquecer después una entrada existente con nota personal, tags, estado o edición completa, sin cambiar `id` ni `fecha`.

## Salida

- Usar salida humana por defecto.
- Reservar el modo técnico para cuando el usuario lo pida explícitamente o para depuración.
- En salida humana, ocultar IDs, rutas físicas, fechas ISO y tono de CLI.
- En modo técnico, mostrar detalles internos útiles como IDs, fechas ISO, rutas y campos exactos.

## Formato de datos

- Mantener un archivo por proyecto.
- Mantener YAML como fuente de verdad para los campos estructurados.
- Reservar el bloque Markdown a la **Nota personal**.
- Añadir entradas nuevas por append.
- Hacer las reescrituras de entradas existentes de forma atómica.
- Evitar notas redundantes, por ejemplo una URL repetida idéntica a `fuente`.

## Scripts disponibles

- `scripts/save_entry.py` para guardar, actualizar, migrar, fusionar duplicados, cambiar estado y editar entradas.
- `scripts/read_entries.py` para listar, filtrar, buscar, ver recientes, ver pendientes de enriquecer, generar recordatorios y consultar modo técnico.

## Tests disponibles

- `scripts/test_phase1.py` a `scripts/test_phase22.py`

## Ejemplos de uso

```bash
python3 skills/bitacora/scripts/save_entry.py \
  --project camper \
  --category aislamiento \
  --content "https://example.com/guia-xps" \
  --source "https://example.com/guia-xps"

python3 skills/bitacora/scripts/save_entry.py \
  --project camper \
  --update-entry-id entry-1712613864123 \
  --additional-content "Comparar con lana de roca en pasos de rueda"

python3 skills/bitacora/scripts/read_entries.py --project camper
python3 skills/bitacora/scripts/read_entries.py --project camper --pending-enrichment
python3 skills/bitacora/scripts/read_entries.py --project camper --technical --entry-id entry-1712613864123
```
