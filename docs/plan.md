# Plan — exp/2026-09-30-auditoria (iteración 1)

Referencia: `docs/brief.md`. Este plan no entra en vigor sin la aprobación de P1.

## Contrato de interfaz

Está fijo para que el Tester escriba las pruebas sin leer `src/`.

- **Comando:** `uv run jupyter nbconvert --to notebook --execute classification.ipynb --output /tmp/run.ipynb`
- **Datos crudos:** `data/raw/exoplanets_clean.csv`, más `data/raw/SHA256SUMS`.
- **Métricas:** `data/processed/metrics.json`, con la forma `{modelo: {métrica: {"mean": float, "std": float}}}`. Incluye la línea base, y las métricas son `accuracy`, `precision_terrestrial`, `recall_terrestrial` y `f1_terrestrial`.
- **Particiones:** `data/processed/folds.csv`, con las columnas `row_id`, `group_id`, `fold` y `split` (`train`/`eval`).
- **Variables del modelo:** `data/processed/features.json`, con la lista final.
- **Métricas por procedencia de la masa:** `data/processed/metrics_by_mass_provenance.json`, con la forma `{categoría: {"n": int, "metrics": <mismo esquema que metrics.json>}}`.
- **Linaje:** `data/processed/lineage.csv`, con las columnas `row_id`, `pl_name`, `hostname` y `match_status` (`unique`/`none`/`ambiguous`).
- **Agrupamiento:** `data/processed/grouping_report.json`, con las llaves `n_by_hostname`, `n_by_tuple`, `tuple_collisions` y `hostname_collisions`.
- **Formato determinista:** todos los JSON se escriben con llaves ordenadas (`sort_keys`) y floats con 6 decimales fijos, y todos los CSV van ordenados por `row_id`. Esto es lo que hace posible la comparación byte a byte del criterio 1.

## Tareas

| # | Tarea | Rol | Entrada | Salida | Criterio de listo | Tipo |
|---|---|---|---|---|---|---|
| T0 | Pasar el brief al Crítico (ChatGPT) y decidir P1 | Mai | `docs/brief.md`, `docs/plan.md` | P1 registrado en la bitácora | Entrada en la bitácora con la decisión y los cambios | [TÚ] |
| T1 | Reconstruir el linaje: emparejar las 623 filas con el `exoplanets.csv` del Proyecto 1, recuperar `pl_name`/`hostname` y reconstruir filtro, unidades y etiqueta | Especialista | CSV de este repo y del Proyecto 1 | `data/processed/lineage.csv` y una sección en `docs/decisiones.md` | Emparejamiento uno a uno (criterio 14); conteo por `match_status`; filas sin pareja o ambiguas listadas; cada paso marcado como reconstruido o desconocido | [AGENTE] |
| T2 | Mover el CSV a `data/raw/` con `git mv`, sin cambiar bytes, y registrar el SHA-256 | Implementador | CSV en la raíz | `data/raw/exoplanets_clean.csv`, `data/raw/SHA256SUMS` | El checksum es igual al del blob en b316a47 | [AGENTE] |
| T3 | Consultar `pl_bmassprov` y `hostname` en el NASA Exoplanet Archive vía TAP para los planetas emparejados (consulta pública, solo lectura) | Especialista | `data/processed/lineage.csv` | `data/raw/pscomppars_provenance_<fecha>.csv`; `hostname` en `lineage.csv`; la consulta en `docs/decisiones.md` | Conteo de filas por categoría de procedencia de la masa; conteo de colisiones entre `hostname` y la tupla estelar | [AGENTE] |
| T4 | Decidir el veredicto de fuga de cada variable **por procedencia** (criterio 4) con la evidencia de T1 y T3 | Mai | `docs/decisiones.md`, salidas de T1 y T3 | Veredictos y lista de variables vetadas en `docs/decisiones.md` | Las cinco variables con veredicto (fuga / sin fuga / incierta) y su evidencia de procedencia | [TÚ] |
| T4b | Decidir la pregunta que responde el modelo, la definición exacta de la etiqueta y los nombres de las clases (criterio 12) | Mai | Linaje terminado (T1, T3) | Decisión en `docs/decisiones.md` | Una frase con la pregunta, la definición de la etiqueta y por qué se conservan o se cambian los nombres | [TÚ] |
| T5 | Decidir el esquema de evaluación: k, repeticiones, métrica principal y si queda un conjunto de prueba aparte. La agrupación ya está fijada por el criterio 13 y no se elige un modelo final | Mai | Brief, T4 | Decisión en `docs/decisiones.md` | Cada parámetro fijado con una frase de justificación | [TÚ] |
| T6 | Fase A: escribir pruebas contra el brief y este contrato (criterios 1, 2, 4 a 7, 11, 13 y 14) | Tester | Brief, contrato, `tests/` | `tests/`, `reports/pruebas_v1.md`, tag `pruebas-1` | Las pruebas fallan hoy por la razón esperada; cada una apunta a un criterio | [AGENTE] |
| T7 | Adaptar el notebook a T4 y T5: leer de `data/raw/`, celda de separabilidad por variable, CV agrupada por `hostname`, los tres modelos más la línea base, escribir todas las salidas del contrato; agregar `pytest` como dependencia de desarrollo | Implementador | T2, T4, T5, pruebas | Notebook, `pyproject.toml`, `uv.lock`, `docs/decisiones.md` | `uv run pytest -q` en verde y `uvx ruff check .` limpio, sin tocar `tests/` | [AGENTE] |
| T8 | Interpretar los resultados y redactar el método, los resultados y la discusión del README | Mai | `metrics.json`, notebook ejecutado | README | Cumple los criterios 7, 9 y 12 | [TÚ] |
| T9 | Partes mecánicas del README: setup con `uv`, tabla de métricas generada desde el JSON y sección de autoría con los datos que dé Mai | Implementador | T8 y la lista de autoría de Mai | README | Cumple los criterios 7 y 8 | [AGENTE], con la lista de autoría [TÚ] |
| T10 | Red team M2 (otro modelo, según `AGENTS.md`) | Red team | Brief, diff contra `main`, `tests/`, `reports/pruebas_v1.md` | `reports/ataque_v1.md` | Los cinco ataques M2 corridos y con evidencia reproducible | [AGENTE] |
| T11 | Verificar contra el criterio de éxito | Verificador | Todo menos `docs/decisiones.md` | `reports/veredicto_v1.md` | Cada uno de los 14 criterios con "cumple" o "no cumple" y su evidencia | [AGENTE] |
| T12 | P2 (aceptar la iteración), tag `iter-1`, abrir el PR y P3 (merge en GitHub) | Mai | Veredicto y ataque | Tag `iter-1` y merge | Merge hecho por Mai | [TÚ] |

## Orden

T0 → T1 → T2 → T3 → T4, T4b, T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12.

T6 puede empezar en cuanto P1 esté aprobado, porque solo depende del contrato. La lista de variables vetadas la lee de `features.json`, no de `docs/decisiones.md`.

## Presupuesto

- Total: 12 h de Mai.
- Al cerrar cada tarea [TÚ], Mai anota en `docs/bitacora.md` las horas acumuladas.
- Al llegar a 6 h (50 %), se avisa en la bitácora y se compara con las tareas que faltan.
- Si se superan 18 h, se detiene el trabajo y hay revisión obligatoria con Mai antes de continuar.
