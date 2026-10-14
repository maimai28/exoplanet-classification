# Plan — exp/2026-09-30-auditoria (iteración 1)

Referencia: `docs/brief.md`. Este plan no entra en vigor sin la aprobación de P1.

## Contrato de interfaz

Está fijo para que el Tester escriba las pruebas sin leer `src/`.

- **Comando:** `uv run jupyter nbconvert --to notebook --execute classification.ipynb --output /tmp/run.ipynb`
- **Datos crudos:** `data/raw/exoplanets_clean.csv`, más `data/raw/SHA256SUMS`.
- **Métricas:** `data/processed/metrics.json`, con la forma `{modelo: {métrica: {"mean": float, "std": float}}}`. Incluye la línea base, y las métricas son `accuracy`, `precision_terrestrial`, `recall_terrestrial` y `f1_terrestrial`.
- **Particiones:** `data/processed/folds.csv`, con las columnas `row_id`, `group_id`, `fold` y `split` (`train`/`eval`). `group_id` tiene la forma `g:<row_id mínimo de la componente>` (criterio 13).
- **Variables del modelo:** `data/processed/features.json`, con la lista final.
- **Procedencia de la masa por fila:** `data/processed/mass_provenance.csv` (lo escribe T3b), con 623 filas ordenadas por `row_id` y estas columnas:
  - `row_id`.
  - `pl_bmassprov`: la de T3, o vacío si la fila no tiene `pl_name`.
  - `mass_matches_p1`: `true` o `false` según la `mass` coincida a ±1 % con `pl_bmassj` del Proyecto 1; vacío si la fila no tiene pareja.
  - `mr_predicted_mass`: en M_J, con 6 decimales; vacío si es `not_testable`.
  - `mr_rel_residual`: `(mass − mr_predicted_mass) / mr_predicted_mass`, con 6 decimales; vacío si es `not_testable`.
  - `mr_status`: `on_relation`, `off_relation` o `not_testable`.
  - `mass_provenance`: `measured`, `derived` o `unverifiable`, con la regla del criterio 4.
- **Métricas por procedencia de la masa:** `data/processed/metrics_by_mass_provenance.json`, con la forma `{categoría: {"n": int, "metrics": <mismo esquema que metrics.json>}}`. Las categorías son exactamente `measured`, `derived` y `unverifiable`, y `n` es igual al conteo en `mass_provenance.csv`.
- **Linaje:** `data/processed/lineage.csv`, con las columnas `row_id`, `pl_name`, `hostname` y `match_status` (`unique`/`none`/`ambiguous`).
- **Agrupamiento:** `data/processed/grouping_report.json`. Todas sus llaves son enteros:
  - `n_rows` (623); `n_rows_with_hostname` y `n_rows_without_hostname`, que suman `n_rows`.
  - `n_groups`, igual al número de `group_id` distintos en `folds.csv`.
  - `n_groups_multi_hostname`: componentes con más de un `hostname`.
  - `n_fallback_rows_joined`: filas sin `hostname` que caen en una componente que sí tiene `hostname`.
  - `max_group_size`.
  - `tuple_collisions`: tuplas con más de un `hostname`.
  - `hostname_collisions`: `hostname` con más de una tupla.
- **Formato determinista:** todos los JSON se escriben con llaves ordenadas (`sort_keys`) y floats con 6 decimales fijos, y todos los CSV van ordenados por `row_id`. Esto es lo que hace posible la comparación byte a byte del criterio 1.

## Tareas

| # | Tarea | Rol | Entrada | Salida | Criterio de listo | Tipo |
|---|---|---|---|---|---|---|
| T0 | Pasar el brief al Crítico (ChatGPT) y decidir P1 | Mai | `docs/brief.md`, `docs/plan.md` | P1 registrado en la bitácora | Entrada en la bitácora con la decisión y los cambios | [TÚ] |
| T1 | Reconstruir el linaje: emparejar las 623 filas con el `exoplanets.csv` del Proyecto 1, recuperar `pl_name`/`hostname` y reconstruir filtro, unidades y etiqueta | Especialista | CSV de este repo y del Proyecto 1 | `data/processed/lineage.csv` y una sección en `docs/decisiones.md` | Emparejamiento uno a uno (criterio 14); conteo por `match_status`; filas sin pareja o ambiguas listadas; cada paso marcado como reconstruido o desconocido | [AGENTE] |
| T2 | Mover el CSV a `data/raw/` con `git mv`, sin cambiar bytes, y registrar el SHA-256 | Implementador | CSV en la raíz | `data/raw/exoplanets_clean.csv`, `data/raw/SHA256SUMS` | El checksum es igual al del blob en b316a47 | [AGENTE] |
| T3 | Consultar `pl_bmassprov` y `hostname` en el NASA Exoplanet Archive vía TAP para los planetas emparejados (consulta pública, solo lectura) | Especialista | `data/processed/lineage.csv` | `data/raw/pscomppars_provenance_<fecha>.csv`; `hostname` en `lineage.csv`; la consulta en `docs/decisiones.md` | Conteo de filas por categoría de procedencia de la masa; conteo de colisiones entre `hostname` y la tupla estelar | [AGENTE] |
| T3b | Probar, en las 623 filas, si la `mass` del CSV cae exactamente sobre la relación masa-radio del catálogo, aplicada al radio del CSV (`radius × 11.208981` R⊕); eso sería evidencia directa de una masa derivada. Clasificar cada fila con la regla del criterio 4. Permitido, solo como lectura: la documentación web del NASA Exoplanet Archive y la literatura que esa documentación cite. Prohibido: consultas TAP, descargar tablas e instalar dependencias. La relación M-R se implementa a partir de los coeficientes publicados | Especialista | `data/raw/exoplanets_clean.csv`, `data/processed/lineage.csv`, `data/raw/pscomppars_provenance_2026-10-13.csv`, `exoplanets.csv` del Proyecto 1 (SHA-256 e5570cba…), documentación del NASA Exoplanet Archive | `data/processed/mass_provenance.csv` y una sección en `docs/decisiones.md` | (0) Cada fuente consultada se registra en `docs/decisiones.md` con su URL o DOI y la fecha de acceso. (1) La relación queda escrita: forma, coeficientes publicados y regímenes, con su fuente y la versión del catálogo a la que aplica. Si no se puede establecer, se declara "no establecida" con lo que se intentó, y todas las filas quedan `not_testable`. (2) La tolerancia de "exacto" se justifica con la precisión numérica del CSV y se publica la distribución de `mr_rel_residual`. (3) Las filas de regímenes donde la masa no se puede obtener del radio con un solo valor (p. ej., la meseta joviana) quedan `not_testable`. (4) Controles: tasa de `on_relation` entre las filas `M-R relationship` (positivos) y entre las `Mass` que coinciden con el Proyecto 1 (negativos). Además, como diagnóstico de la tolerancia, cuántas filas con `pl_bmassprov` = `Mass` quedan `on_relation`, separadas por `mass_matches_p1`, con su lista de `row_id`. (5) Las 623 filas clasificadas, con conteos por `mr_status` y por `mass_provenance` | [AGENTE] |
| T4 | Decidir el veredicto de fuga de cada variable **por procedencia** (criterio 4) con la evidencia de T1, T3 y T3b | Mai | `docs/decisiones.md`, salidas de T1, T3 y T3b (`mass_provenance.csv`) | Veredictos y lista de variables vetadas en `docs/decisiones.md` | Las cinco variables con veredicto (fuga / sin fuga / incierta) y su evidencia de procedencia; el de `mass` cita los conteos por `mass_provenance` | [TÚ] |
| T4b | Decidir la pregunta que responde el modelo, la definición exacta de la etiqueta y los nombres de las clases (criterio 12) | Mai | Linaje terminado (T1, T3) | Decisión en `docs/decisiones.md` | Una frase con la pregunta, la definición de la etiqueta y por qué se conservan o se cambian los nombres | [TÚ] |
| T5 | Decidir el esquema de evaluación: k, repeticiones, métrica principal y si queda un conjunto de prueba aparte. La agrupación ya está fijada por el criterio 13 y no se elige un modelo final | Mai | Brief, T4 | Decisión en `docs/decisiones.md` | Cada parámetro fijado con una frase de justificación | [TÚ] |
| T6 | Fase A: escribir pruebas contra el brief y este contrato (criterios 1, 2, 4 a 7, 11, 13 y 14), incluidas la de componentes conexas del criterio 13 y la de `metrics_by_mass_provenance.json` frente a `mass_provenance.csv` | Tester | Brief, contrato, `tests/` | `tests/`, `reports/pruebas_v1.md`, tag `pruebas-1` | Las pruebas fallan hoy por la razón esperada; cada una apunta a un criterio | [AGENTE] |
| T7 | Adaptar el notebook a T4 y T5: leer de `data/raw/`, celda de separabilidad por variable, CV agrupada por componente conexa (criterio 13), los tres modelos más la línea base, métricas por `mass_provenance` leyendo `mass_provenance.csv`, escribir todas las salidas del contrato que le tocan; agregar `pytest` como dependencia de desarrollo | Implementador | T2, T3b, T4, T5, pruebas | Notebook, `pyproject.toml`, `uv.lock`, `docs/decisiones.md` | `uv run pytest -q` en verde y `uvx ruff check .` limpio, sin tocar `tests/` | [AGENTE] |
| T8 | Interpretar los resultados y redactar el método, los resultados y la discusión del README | Mai | `metrics.json`, notebook ejecutado | README | Cumple los criterios 7, 9 y 12 | [TÚ] |
| T9 | Partes mecánicas del README: setup con `uv`, tabla de métricas generada desde el JSON y sección de autoría con los datos que dé Mai | Implementador | T8 y la lista de autoría de Mai | README | Cumple los criterios 7 y 8 | [AGENTE], con la lista de autoría [TÚ] |
| T10 | Red team M2 (otro modelo, según `AGENTS.md`) | Red team | Brief, diff contra `main`, `tests/`, `reports/pruebas_v1.md` | `reports/ataque_v1.md` | Los cinco ataques M2 corridos y con evidencia reproducible | [AGENTE] |
| T11 | Verificar contra el criterio de éxito | Verificador | Todo menos `docs/decisiones.md` | `reports/veredicto_v1.md` | Cada uno de los 14 criterios con "cumple" o "no cumple" y su evidencia | [AGENTE] |
| T12 | P2 (aceptar la iteración), tag `iter-1`, abrir el PR y P3 (merge en GitHub) | Mai | Veredicto y ataque | Tag `iter-1` y merge | Merge hecho por Mai | [TÚ] |

## Orden

T0 → T1 → T2 → T3 → T3b → T4, T4b, T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12.

T3b va antes de T4 porque el veredicto de `mass` depende de su clasificación. T6 puede empezar en cuanto Mai apruebe este cambio de contrato (2026-10-13), porque solo depende del contrato. La lista de variables vetadas la lee de `features.json`, no de `docs/decisiones.md`.

## Presupuesto

- Total: 12 h de Mai.
- Al cerrar cada tarea [TÚ], Mai anota en `docs/bitacora.md` las horas acumuladas.
- Al llegar a 6 h (50 %), se avisa en la bitácora y se compara con las tareas que faltan.
- Si se superan 18 h, se detiene el trabajo y hay revisión obligatoria con Mai antes de continuar.
