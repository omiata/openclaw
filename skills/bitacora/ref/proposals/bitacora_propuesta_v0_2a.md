# Bitacora v0.2a — Parche: Prevención de Error Silencioso en Actualizaciones

Esta iteración (patch) tiene la intención exclusiva de corregir un fallo silencioso en el procesamiento CLI durante el modo de actualización de entradas (`--update-entry-id`). Evita que variables de creación (`--content`, `--title`, `--type` y `--source`) sean descartadas sin generar un error.

---

# PARTE I — Contenido propuesto para bitacora_maestro.md

[NINGÚN CAMBIO]

El diseño funcional fundacional se mantiene idéntico. La única diferencia es que el bot recibirá errores tempranos cuando intente enviar comandos ambivalentes.

---

# PARTE II — Contenido propuesto para bitacora_reglas.md

**Reglas nuevas a añadir bajo la sección de validación y CLI:**

- **Prevención de fallos silenciosos en CLI:** El script principal NUNCA debe procesar con "éxito" una petición que contenga argumentos que no van a ser usados para la operación seleccionada. Si la CLI detecta `--content`, `--title`, `--type` o `--source` durante un `update_mode` y está usando la vía por defecto de enriquecimiento sin edición explícita profunda, debe elevar un error duro (fail fast) inmediatamente y no reescribir la entrada ni devolver éxitos falsos.

---

# PARTE III — Contenido propuesto para bitacora_fases.md

**Cambios menores previstos:**
La fase funcional (v0.2) en la que se encontraba la estabilización del CLI se dará por complementada y parcheada. Si es necesario formalizar, se añadirá un inciso de *Bugfix Parche*:
- **Fase Parche v0.2a:** Integrar validación destructiva (fail fast) para prevenir comandos CLI erróneos que mezclan semántica de creación con semántica de actualización en `scripts/save_entry.py`.

---

# PARTE IV — Changelog previsto

**v0.2a (Parche)**
- Fix crítico: `save_entry.py` ahora genera un error explícito (código 1) si se ejecuta una actualización (`--update-entry-id` / `--update-source-url`) usando banderas exclusivas de creación (`--content`, `--title`, `--type`, `--source`). Esto evita que el sistema retorne respuestas de éxito falsas y obliga al LLM o al usuario a utilizar los parámetros explícitos de mutación o enriquecimiento adecuados.

---

# Decisiones cerradas que incorpora esta propuesta

1. La vía priorizada (Opción 1 del análisis) es forzar la consistencia y rigurosidad de comandos CLI por encima de generar mecanismos opacos de redirección (UX tolerante pero silencioso).
2. Se confía en que el prompt de Bitacora sabe usar los parámetros de `--set-*` o complementarios (`--summary`) si el script le indica la restricción.

---

# Conflictos detectados entre el estado actual y esta propuesta

- **Flujos del Bot LLM:** Es posible que en el pasado, el bot se haya habituado a usar `--content` al actualizar porque no fallaba. A partir de ahora, su comando abortará. Se asume que OpenClaw reaccionará positivamente al mensaje del error explicito CLI, comprendiendo la corrección, por tanto no requiere un rediseño mayor de `SKILL.md`. Si reincide erróneamente más de dos veces, habría un problema.

---

# Huecos abiertos

- Solucionar este problema impide la pérdida silente, pero expone que el `parse_args` central es compartido para todas las operaciones (create, update, edit). En un futuro (v0.3), migrar el setup de argumentos a `subparsers` resolverá esto nativamente desde la librería `argparse`. No se soluciona aquí por requerir restructuraciones mayores.
