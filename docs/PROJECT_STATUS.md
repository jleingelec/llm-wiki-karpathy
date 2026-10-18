# Estado y plan de evolución de Wiki Karpathy

> Foto del repositorio a 2026-09-15. Este documento separa lo que existe hoy de
> las recomendaciones; no presenta como implementada ninguna integración externa.

## Resumen ejecutivo

El proyecto tiene un **MVP documental bien definido**: explica el patrón LLM Wiki,
separa fuentes inmutables de conocimiento derivado y proporciona un contrato de
operación para el agente. Todavía no es una wiki alimentada con conocimiento real:
`raw/` está vacío y el índice confirma que no se ha ingerido ninguna fuente.

Esta actualización incorpora la capa mínima de colaboración: instrucciones nativas
para Codex, entorno reproducible de Codespaces, plantillas de issues y pull requests,
y una comprobación automática de integridad. La prioridad siguiente no es añadir más
herramientas, sino ejecutar y evaluar varias ingestas reales.

## Qué se ha realizado

| Área | Estado | Evidencia |
|---|---|---|
| Idea y explicación | Hecho | `llm-wiki.md`, `article.md` y guía de uso en `README.md` |
| Contrato del agente | Hecho | Esquema, tipos de página y flujos en `CLAUDE.md` |
| Núcleo de la wiki | Hecho | Índice, overview, glosario y log en `wiki/` |
| Compatibilidad Obsidian | Base | Vault y carpetas de plugins/snippets preparadas |
| Fuentes e ingestas | Pendiente | `raw/` solo contiene `.gitkeep`; el índice no registra fuentes |
| Automatización de calidad | Hecho en este cambio | `scripts/check_wiki.py` y GitHub Actions |
| Colaboración GitHub | Hecho en este cambio | Formularios de issue y plantilla de pull request |
| Codespaces | Hecho en este cambio | Dev container ligero para Markdown y YAML |
| GitHub Project y protección de rama | Pendiente externo | Requiere configurar el repositorio en GitHub |

## Arquitectura objetivo, sin redundancias

Cada herramienta debe tener una responsabilidad única:

| Herramienta | Responsabilidad | No usar para |
|---|---|---|
| **Git** | Historial auditable del contenido | Gestión de prioridades |
| **GitHub Issues** | Unidad de trabajo: una fuente, defecto o mejora | Notas efímeras o documentación final |
| **GitHub Projects** | Priorización, estado y métricas de los issues | Duplicar páginas de la wiki |
| **Pull requests** | Revisión de cambios y controles automáticos | Mantener un backlog paralelo |
| **Codex** | Ingestar, relacionar, consultar, revisar y proponer cambios | Ser la fuente de verdad sin archivos/versionado |
| **Codespaces** | Entorno opcional y reproducible, útil desde cualquier equipo | Sustituir GitHub Actions |
| **GitHub Actions** | Validación determinista en cada cambio | Generar conocimiento de forma autónoma |
| **Obsidian** | Lectura, navegación y grafo local | Seguimiento de tareas del equipo |

**Decisión recomendada:** GitHub es el plano de colaboración; la carpeta `wiki/` es
la fuente de verdad del conocimiento. Obsidian es una interfaz, Codespaces es un
entorno y Codex es un colaborador. Ninguno debe duplicar el contenido de la wiki.

## Flujo de trabajo recomendado

1. Crear un issue con el formulario **Ingestar una fuente** y explicar propósito,
   alcance, sensibilidad y criterio de aceptación.
2. Añadir la fuente a `raw/` solo si puede versionarse. Para material privado o
   pesado, registrar una referencia autorizada y definir primero una política de
   datos; no subir secretos ni datos personales.
3. Crear una rama corta (`ingest/<fuente>` o `docs/<tema>`), trabajar con Codex
   siguiendo `AGENTS.md` y revisar la síntesis humana antes de aceptarla.
4. Ejecutar `python scripts/check_wiki.py` y abrir un pull request que enlace el
   issue (`Closes #...`).
5. Exigir revisión humana para afirmaciones nuevas. Hacer squash merge para conservar
   una unidad lógica por ingestión o mejora.
6. GitHub Actions vuelve a validar el resultado; GitHub Project refleja el estado
   automáticamente a partir del issue y el PR.

## Configuración propuesta para GitHub

### Repositorio

- Definir `main` como rama por defecto y exigir pull request, un aprobador y el check
  **Wiki quality**. Bloquear force-push y eliminación de la rama.
- Activar eliminación automática de ramas y squash merge. Mantener desactivado el
  merge directo a `main`.
- Añadir topics como `knowledge-base`, `llm-wiki`, `obsidian`, `codex` y `markdown`.
- Activar secret scanning y Dependabot alerts. No añadir Dependabot version updates
  mientras no haya dependencias versionadas que mantener.

### Issues y etiquetas

Usar pocas etiquetas, ortogonales y con prefijos:

- Tipo: `type:ingest`, `type:quality`, `type:feature`, `type:docs`.
- Prioridad: `priority:p0` a `priority:p3`.
- Estado especial: `blocked`, `needs-review`, `sensitive-source`.
- Dominio: crearlo solo cuando haya al menos tres issues del mismo ámbito.

Una ingestión es un issue; las páginas que produce no son issues independientes salvo
que requieran investigación posterior.

### GitHub Project

Crear **un solo Project (v2)** llamado `Wiki Karpathy`, enlazado al repositorio, con:

- Campos: `Status` (Inbox, Ready, In progress, Review, Done), `Priority`, `Type`,
  `Domain`, `Source date` y `Target date`.
- Vistas: **Board** por Status, **Backlog** agrupado por Priority, **Ingestions**
  filtrada por `type:ingest`, y **Roadmap** por Target date.
- Automatizaciones: issue nuevo → Inbox; asignado → In progress; PR abierto → Review;
  issue cerrado → Done.

No crear Projects separados para Codex, Codespaces u Obsidian: son capacidades del
mismo flujo, no líneas de producto.

## Backlog priorizado

### P0 — validar el producto

- Seleccionar 3–5 fuentes pequeñas, públicas y representativas.
- Ejecutar una ingestión completa por fuente y medir correcciones humanas, enlaces
  rotos, duplicados y tiempo ahorrado.
- Definir política de privacidad, licencias, retención y tamaño máximo antes de subir
  fuentes reales.
- Corregir la promesa del editor si fuera necesario: verificar en la práctica qué
  clientes leen automáticamente `CLAUDE.md` y usar `AGENTS.md` como contrato Codex.

### P1 — calidad del conocimiento

- Añadir pruebas con páginas de ejemplo válidas e inválidas para el checker.
- Definir cómo citar pasajes de fuentes (archivo, sección/página y fecha de acceso).
- Añadir detección de páginas huérfanas y ejecutar el lint editorial tras cada diez
  ingestas, tal como propone la guía.
- Normalizar el frontmatter de los cuatro archivos núcleo o documentar formalmente su
  excepción.

### P2 — escala, solo cuando exista uso real

- Introducir búsqueda o índice generado si el volumen hace lento leer `index.md`.
- Evaluar Git LFS para binarios grandes; no activarlo preventivamente.
- Evaluar publicación (por ejemplo, sitio estático) solo si hay una audiencia externa.
- Añadir evaluación automática de respuestas únicamente después de reunir casos de
  consulta reales y resultados esperados.

## Métricas útiles

Revisar mensualmente, no por cada commit:

- Fuentes ingeridas y porcentaje con metadatos/procedencia completos.
- Páginas huérfanas, enlaces sin destino y términos inconsistentes.
- Correcciones humanas por ingestión y tiempo desde issue hasta merge.
- Consultas respondidas reutilizando la wiki y respuestas guardadas como análisis.

Evitar métricas de vanidad como número bruto de páginas o commits: incentivan volumen,
no conocimiento confiable.

## Criterio para la siguiente versión

La versión `0.2` debería declararse solo después de completar al menos tres ingestas,
cerrar los fallos encontrados por esas pruebas y documentar la política de fuentes.
Hasta entonces, el proyecto debe describirse como un MVP operativo sin corpus.
