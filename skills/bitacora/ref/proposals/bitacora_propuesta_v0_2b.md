# Bitacora v0.2b — Parche: Flujo Seguro de Documentos Adjuntos

Esta iteración tiene como objetivo solucionar la gestión de archivos adjuntos (como PDFs) cuando el usuario pide recuperarlos. En lugar de reenviar rutas originales o usar `../` de forma insegura, el sistema resolverá, copiará y servirá el archivo desde un directorio canónico de salida (`tmp/outbound/`).

---

# PARTE I — Contenido propuesto para bitacora_maestro.md

**Modificación menor funcional:**
- **Recuperación de Archivos Adjuntos:** Cuando el usuario solicita un documento guardado (ej. PDF), la skill extraerá el nombre del archivo de la nota o fuente. En lugar de emitir la ruta original (que podría estar bloqueada, contener `../` o ser temporal), el sistema copiará internamente el documento a `tmp/outbound/` con un nombre único y seguro, y emitirá la etiqueta `MEDIA:` correspondiente hacia esa ruta estática.

---

# PARTE II — Contenido propuesto para bitacora_reglas.md

**Reglas nuevas a añadir bajo la sección de formato y seguridad:**

- **Flujo de salida aislado para documentos:** Cualquier documento que se vaya a enviar al usuario a través de canales como Telegram debe copiarse previamente a la carpeta `tmp/outbound/`. Queda estrictamente prohibido emitir comandos `MEDIA:` apuntando a rutas relativas con `../` que intenten escapar del workspace o exponer rutas absolutas internas del sistema.
- **Fail-fast en adjuntos ausentes:** Si se solicita servir un documento y el archivo no existe en la ruta esperada de datos (ej. `skills/bitacora/data/adjuntos/`), el sistema no debe fingir un envío exitoso. Debe fallar de forma ruidosa devolviendo un error explícito (ej. "Error: El archivo adjunto X no existe en disco").

---

# PARTE III — Contenido propuesto para bitacora_fases.md

**Cambios menores previstos:**
- **Fase Parche v0.2b:** Implementar el modo de lectura segura de adjuntos en `scripts/read_entries.py`. Se habilitará un flag especial (ej. `--serve-document`) que resuelva el archivo en la carpeta canónica de datos, lo copie a `tmp/outbound/` con un nombre seguro y emita la etiqueta `MEDIA:./tmp/outbound/<nombre_unico>`. Añadir test unitario riguroso (`test_phase23.py` o anexo).

---

# PARTE IV — Changelog previsto

**v0.2b (Parche)**
- Fix crítico: `read_entries.py` ahora procesa documentos de forma segura evitando *path traversal*.
- Fix crítico: En lugar de emitir el contenido como texto simulado o ignorar el adjunto, se emite `MEDIA:./tmp/outbound/...` para forzar a Telegram a usar `sendDocument`.
- Mejora: Creación de la carpeta recomendada `skills/bitacora/data/adjuntos/` para mantener contenida la base de conocimiento de la skill.

---

# Decisiones cerradas que incorpora esta propuesta

1. Guardar todos los adjuntos (inputs) dentro de `skills/bitacora/data/adjuntos/` para asegurar que todo respaldo de la skill se lleve sus archivos.
2. Usar `tmp/outbound/` garantizando un punto de salida limpio y desacoplado para OpenClaw (output).

---

# Conflictos detectados entre el estado actual y esta propuesta

- **Inbound vs Outbound:** Históricamente, el usuario o el LLM han podido introducir rutas directas desde la carpeta global de descargas. A partir de ahora se estandariza el uso de la carpeta `adjuntos` de la propia skill.
