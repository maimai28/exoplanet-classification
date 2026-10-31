# Plan — exp/2026-09-30-auditoria (iteración 1)

Referencia: `docs/brief.md`. Este plan no entra en vigor sin la aprobación de P1.

## Contrato de interfaz

Está fijo para que el Tester escriba las pruebas sin leer `src/`.

- **Comando:** `uv run jupyter nbconvert --to notebook --execute classification.ipynb --output /tmp/run.ipynb`
- **Datos crudos:** `data/raw/exoplanets_clean.csv`, más `data/raw/SHA256SUMS`.
- **Etiqueta (T4b):** `data/processed/labels.csv`, con las columnas `row_id`, `planet_type` (tal como está en `data/raw/`) y `size_class` (`small` si `planet_type` = `terrestrial`; `large` si `planet_type` = `gas_giant`). 623 filas ordenadas por `row_id`. Clase positiva: `small`.
- **Variables del modelo (T4):** `data/processed/features.json`, con exactamente cuatro llaves:
  - `excluded`: `{"radius": "etiqueta por umbral (T1)"}`.
  - `main`: `["orbital_period", "star_mass", "star_radius", "star_teff"]`, en ese orden.
  - `sensitivity_mass`: `["orbital_period", "star_mass", "star_radius", "star_teff", "mass"]`, en ese orden. La restricción a filas `measured` no va aquí: la declara `metrics_sensitivity.json` y la materializa `folds_sensitivity.csv`.
  - `target`: `"size_class"`.

  El notebook toma las columnas de X solo de este archivo. Cambiar esta lista requiere la regla 6.
- **Modelos (T5, enmendado):** "Logistic Regression", "Random Forest" y "SVM (RBF)", con exactamente los hiperparámetros del notebook en `main` (1f2e02f): `class_weight="balanced"` en los tres, `random_state=42`, `max_iter=1000` en LR, `n_estimators=300` en RF, y `C`/`gamma` por defecto en el SVC; el escalado va dentro del `Pipeline` en LR y SVM. Más "Baseline (prior)" = `DummyClassifier(strategy="prior")`. Sin CV interior ni búsqueda de hiperparámetros. Estos cuatro nombres son las llaves de modelo en todos los archivos de métricas.
  - **Score** para AP y ROC-AUC: `predict_proba[:, small]` en LR, RF y la línea base; `decision_function` en el SVM (positivo = `small`).
  - **Predicción** para accuracy, balanced accuracy y P/R/F1: `predict()` por defecto (probabilidad 0.5; en el SVM, `decision_function` > 0). P/R/F1 indefinidos (sin predicciones `small`) valen 0 (`zero_division=0`).
- **Particiones, corrida principal:** `data/processed/folds.csv`, con las columnas `row_id`, `group_id`, `repeat` y `fold`. Una línea por (`row_id`, `repeat`): 623 × 5 = 3115 líneas, ordenadas por `row_id` y `repeat`.
  - `repeat` ∈ {0, …, 4} es la semilla. `fold` ∈ {0, …, 4} es el fold exterior en que la fila se evalúa en esa repetición; en esa repetición entrena con los otros cuatro folds.
  - Se generan con `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=repeat)`, con `y` = `size_class` y `groups` = `group_id`, sobre las filas ordenadas por `row_id`.
  - `group_id` tiene la forma `g:<row_id mínimo de la componente>` (criterio 13).
- **Particiones, corrida de sensibilidad:** `data/processed/folds_sensitivity.csv`, con las mismas columnas y la misma regla, aplicada solo a las filas con `mass_provenance` = `measured`: 236 × 5 = 1180 líneas. Es un particionado propio, porque restringir los folds principales a esas filas podría dejar folds sin ninguna `small`. Las dos ramas de la sensibilidad usan estos mismos folds.
- **Predicciones fuera de fold:** `data/processed/predictions.csv`, con las columnas `run`, `model`, `repeat`, `row_id`, `fold`, `score` y `pred` (`small`/`large`). Ordenado por `run`, `model`, `repeat` y `row_id`.
  - `run` ∈ {`main`, `sens_without_mass`, `sens_with_mass`}. `main` usa `features.main` en las 623 filas y `folds.csv`. `sens_without_mass` usa `features.main` y `sens_with_mass` usa `features.sensitivity_mass`; las dos, solo en las filas `measured` y con `folds_sensitivity.csv`.
  - Cada (`run`, `model`, `repeat`, `row_id`) aparece una vez.
- **Métricas por fold:** `data/processed/metrics_by_fold.csv`, con las columnas `run`, `model`, `repeat`, `fold`, `n_train`, `n_eval`, `n_eval_small` y las siete métricas (`accuracy`, `average_precision_small`, `balanced_accuracy`, `f1_small`, `precision_small`, `recall_small` y `roc_auc`). Ordenado por `run`, `model`, `repeat` y `fold`. Se calculan desde `predictions.csv`.
- **Métricas, corrida principal:** `data/processed/metrics.json`, con la forma `{modelo: {métrica: {"mean": float, "std": float}}}`: los cuatro modelos y las siete métricas (`accuracy`, `average_precision_small`, `balanced_accuracy`, `f1_small`, `precision_small`, `recall_small` y `roc_auc`). `mean` y `std` (ddof = 1) salen de las 25 filas `run` = `main` de `metrics_by_fold.csv`. Métrica principal: `average_precision_small`.
- **Métricas, corrida de sensibilidad:** `data/processed/metrics_sensitivity.json`, con exactamente las llaves:
  - `row_filter`: `"mass_provenance == measured"`.
  - `n` (int): igual al conteo de `measured` en `mass_provenance.csv`.
  - `n_small` (int).
  - `exploratory` (bool): `n_small` < 25 (T5).
  - `without_mass` y `with_mass`: el esquema de `metrics.json`, desde las filas `sens_without_mass` y `sens_with_mass` de `metrics_by_fold.csv`.
- **Comparaciones:** `data/processed/comparisons.json`, con la forma `{corrida: {"A vs B": {...}}}`.
  - La llave `main` siempre está. La llave `sensitivity` solo está si `exploratory` es `false`; en ese caso compara `with_mass vs without_mass` por modelo.
  - En `main` hay seis pares, con `A` antes que `B` en este orden: "Logistic Regression", "Random Forest", "SVM (RBF)", "Baseline (prior)". Son los tres modelos contra la línea base y los tres pares entre modelos.
  - Cada par tiene `metric` (`"average_precision_small"`), `mean_diff` (A − B), `t`, `df`, `p_value` y `test_train_ratio`.
  - Test de Nadeau y Bengio (2003): d_j = AP_A − AP_B en cada una de las J = 25 evaluaciones; t = d̄ / √((1/J + ρ)·s²), con s² la varianza muestral de d_j y ρ = `test_train_ratio` = media de `n_eval/n_train` sobre los 25 folds; `df` = J − 1 = 24; p de dos colas con la t de Student.
- **Procedencia de la masa por fila:** `data/processed/mass_provenance.csv` (lo escribe T3b), con 623 filas ordenadas por `row_id` y estas columnas:
  - `row_id`.
  - `pl_bmassprov`: la de T3, o vacío si la fila no tiene `pl_name`.
  - `mass_matches_p1`: `true` o `false` según la `mass` coincida a ±1 % con `pl_bmassj` del Proyecto 1; vacío si la fila no tiene pareja.
  - `mr_predicted_mass`: en M_J, con 6 decimales; vacío solo si `not_testable_reason` = `gap_11.1_14.3` (con `low_precision` se conserva como diagnóstico).
  - `mr_rel_residual`: `(mass − mr_predicted_mass) / mr_predicted_mass`, con 6 decimales; vacío solo si `not_testable_reason` = `gap_11.1_14.3` (con `low_precision` se conserva como diagnóstico).
  - `mr_status`: `on_relation`, `off_relation` o `not_testable`.
  - `not_testable_reason`: `gap_11.1_14.3` o `low_precision` si `mr_status` = `not_testable` (criterio 4; si aplican los dos, `gap_11.1_14.3`); vacío en las demás filas.
  - `mass_provenance`: `measured`, `derived` o `unverifiable`, con la regla del criterio 4.
- **Métricas por procedencia de la masa:** `data/processed/metrics_by_mass_provenance.json`, con la forma `{categoría: {"n": int, "metrics": <mismo esquema que metrics.json>}}`. Las categorías son exactamente `measured`, `derived` y `unverifiable`, y `n` es igual al conteo en `mass_provenance.csv`.
  - Se calcula con las predicciones `run` = `main`. En cada repetición, cada fila tiene exactamente una predicción fuera de fold; se toman las filas de la categoría, se calculan las siete métricas y se da media y `std` (ddof = 1) sobre las 5 repeticiones.
  - Si la categoría no tiene las dos clases, AP y ROC-AUC valen `null`.
- **Linaje:** `data/processed/lineage.csv`, con las columnas `row_id`, `pl_name`, `hostname` y `match_status` (`unique`/`none`/`ambiguous`).
- **Agrupamiento:** `data/processed/grouping_report.json`. Todas sus llaves son enteros:
  - `n_rows` (623); `n_rows_with_hostname` y `n_rows_without_hostname`, que suman `n_rows`.
  - `n_groups`, igual al número de `group_id` distintos en `folds.csv`.
  - `n_groups_multi_hostname`: componentes con más de un `hostname`.
  - `n_fallback_rows_joined`: filas sin `hostname` que caen en una componente que sí tiene `hostname`.
  - `max_group_size`.
  - `tuple_collisions`: tuplas con más de un `hostname`.
  - `hostname_collisions`: `hostname` con más de una tupla.
- **README:** la tabla de resultados va entre las líneas `<!-- metrics:start -->` y `<!-- metrics:end -->`. Es una fila por modelo y una columna por métrica, con "media ± std" a 3 decimales. La prueba del criterio 7 la lee de ahí.
- **`reports/`** (solo Markdown, en español; T7 no escribe aquí):
  - `pruebas_v1.md` (T6): tabla criterio → prueba(s) → por qué falla hoy.
  - `ataque_v1.md` (T10): formato de `AGENTS.md`.
  - `veredicto_v1.md` (T11): los 14 criterios con "cumple" o "no cumple" y su evidencia.
- **Formato determinista:**
  - JSON: llaves ordenadas (`sort_keys`), `indent=2`, UTF-8 y salto de línea final. Los floats van con 6 decimales fijos y las métricas indefinidas como `null`. Las listas conservan el orden fijado en este contrato.
  - CSV: cada archivo va ordenado por la llave declarada arriba (`row_id` si no se dice otra), con floats a 6 decimales.

  Esto es lo que hace posible la comparación byte a byte del criterio 1.

## Tareas

| # | Tarea | Rol | Entrada | Salida | Criterio de listo | Tipo |
|---|---|---|---|---|---|---|
| T0 | Pasar el brief al Crítico (ChatGPT) y decidir P1 | Mai | `docs/brief.md`, `docs/plan.md` | P1 registrado en la bitácora | Entrada en la bitácora con la decisión y los cambios | [TÚ] |
| T1 | Reconstruir el linaje: emparejar las 623 filas con el `exoplanets.csv` del Proyecto 1, recuperar `pl_name`/`hostname` y reconstruir filtro, unidades y etiqueta | Especialista | CSV de este repo y del Proyecto 1 | `data/processed/lineage.csv` y una sección en `docs/decisiones.md` | Emparejamiento uno a uno (criterio 14); conteo por `match_status`; filas sin pareja o ambiguas listadas; cada paso marcado como reconstruido o desconocido | [AGENTE] |
| T2 | Mover el CSV a `data/raw/` con `git mv`, sin cambiar bytes, y registrar el SHA-256 | Implementador | CSV en la raíz | `data/raw/exoplanets_clean.csv`, `data/raw/SHA256SUMS` | El checksum es igual al del blob en b316a47 | [AGENTE] |
| T3 | Consultar `pl_bmassprov` y `hostname` en el NASA Exoplanet Archive vía TAP para los planetas emparejados (consulta pública, solo lectura) | Especialista | `data/processed/lineage.csv` | `data/raw/pscomppars_provenance_<fecha>.csv`; `hostname` en `lineage.csv`; la consulta en `docs/decisiones.md` | Conteo de filas por categoría de procedencia de la masa; conteo de colisiones entre `hostname` y la tupla estelar | [AGENTE] |
| T3b | Probar, en las 623 filas, si la `mass` del CSV cae exactamente sobre la relación masa-radio del catálogo, aplicada al radio del CSV (`radius × 11.208981` R⊕); eso sería evidencia directa de una masa derivada. Clasificar cada fila con la regla del criterio 4. Permitido, solo como lectura: la documentación web del NASA Exoplanet Archive y la literatura que esa documentación cite. Prohibido: consultas TAP, descargar tablas e instalar dependencias. La relación M-R se implementa a partir de los coeficientes publicados. **Re-ejecución (2026-10-13)** con el criterio 4 modificado: `not_testable` por precisión (tolerancia por fila > 0.10, solo en filas que darían `on_relation`) y la columna `not_testable_reason` | Especialista | `data/raw/exoplanets_clean.csv`, `data/processed/lineage.csv`, `data/raw/pscomppars_provenance_2026-10-13.csv`, `exoplanets.csv` del Proyecto 1 (SHA-256 e5570cba…), documentación del NASA Exoplanet Archive | `data/processed/mass_provenance.csv` y una sección en `docs/decisiones.md` | (0) Cada fuente consultada se registra en `docs/decisiones.md` con su URL o DOI y la fecha de acceso. (1) La relación queda escrita: forma, coeficientes publicados y regímenes, con su fuente y la versión del catálogo a la que aplica. Si no se puede establecer, se declara "no establecida" con lo que se intentó, y todas las filas quedan `not_testable`. (2) La tolerancia de "exacto" se justifica con la precisión numérica del CSV y se publica la distribución de `mr_rel_residual`. (3) Las filas de regímenes donde la masa no se puede obtener del radio con un solo valor (p. ej., la meseta joviana) quedan `not_testable` con motivo `gap_11.1_14.3`, y las filas que con la tolerancia de T3b darían `on_relation` pero cuya tolerancia por fila es > 0.10 quedan `not_testable` con motivo `low_precision`. Las `off_relation` no cambian, sea cual sea su tolerancia. (4) Controles: tasa de `on_relation` entre las filas `M-R relationship` (positivos) y entre las `Mass` que coinciden con el Proyecto 1 (negativos). Además, como diagnóstico de la tolerancia, cuántas filas con `pl_bmassprov` = `Mass` quedan `on_relation`, separadas por `mass_matches_p1`, con su lista de `row_id`. (5) Las 623 filas clasificadas, con conteos por `mr_status`, por `not_testable_reason` y por `mass_provenance`. (6) Re-ejecución: una sección nueva en `docs/decisiones.md` que registre el cambio de criterio, el umbral de 0.10, que solo se aplica a filas que darían `on_relation` y por qué (una tolerancia amplia solo debilita una coincidencia, no una discrepancia), que se fijó después de ver los resultados de T3b (commit 43a9b14), y GJ 1132 b (fila 53) y Kepler-68 b (fila 424) como posibles falsos `derived`; incluye los conteos antes y después del cambio | [AGENTE] |
| T4 | Decidir el veredicto de fuga de cada variable **por procedencia** (criterio 4) con la evidencia de T1, T3 y T3b | Mai | `docs/decisiones.md`, salidas de T1, T3 y T3b (`mass_provenance.csv`) | Veredictos y lista de variables vetadas en `docs/decisiones.md` | Las cinco variables con veredicto (fuga / sin fuga / incierta) y su evidencia de procedencia; el de `mass` cita los conteos por `mass_provenance` | [TÚ] |
| T4b | Decidir la pregunta que responde el modelo, la definición exacta de la etiqueta y los nombres de las clases (criterio 12) | Mai | Linaje terminado (T1, T3) | Decisión en `docs/decisiones.md` | Una frase con la pregunta, la definición de la etiqueta y por qué se conservan o se cambian los nombres | [TÚ] |
| T5 | Decidir el esquema de evaluación: k, repeticiones, métrica principal y si queda un conjunto de prueba aparte. La agrupación ya está fijada por el criterio 13 y no se elige un modelo final | Mai | Brief, T4 | Decisión en `docs/decisiones.md` | Cada parámetro fijado con una frase de justificación | [TÚ] |
| T6 | Fase A: escribir pruebas contra el brief y este contrato (criterios 1, 2, 4 a 7, 11 a 14). Mínimo: (a) `features.json` con exactamente sus cuatro llaves y listas, `radius` fuera de `main` y de `sensitivity_mass` y dentro de `excluded`, `target` = `size_class`; (b) mapeo de `labels.csv` frente a `data/raw/`; (c) `folds.csv` y `folds_sensitivity.csv`: forma, un solo `fold` por (`repeat`, `group_id`) y al menos una `small` en cada (`repeat`, `fold`); (d) las filas de las corridas `sens_*` son exactamente las `measured`; (e) `metrics_by_fold.csv` recalculado desde `predictions.csv`, y `metrics.json` y `metrics_sensitivity.json` desde `metrics_by_fold.csv`, a 6 decimales; (f) sanidad de la línea base: AP = prevalencia de `small` en el fold de evaluación, ROC-AUC = 0.5 y balanced accuracy = 0.5; (g) `comparisons.json`: los seis pares, `df` = 24, y t y p recalculados; (h) `exploratory` coherente con `n_small`; (i) `metrics_by_mass_provenance.json` frente a `mass_provenance.csv`; (j) componentes conexas del criterio 13; (k) comprobación estática de que el notebook arma X solo desde `features.json` | Tester | Brief, contrato, `tests/` | `tests/`, `reports/pruebas_v1.md`, tag `pruebas-1` | Las pruebas fallan hoy por la razón esperada; cada una apunta a un criterio | [AGENTE] |
| T7 | Adaptar el notebook a T4, T4b y T5 (con sus enmiendas): leer de `data/raw/`; escribir `labels.csv`, `features.json`, `grouping_report.json`, `folds.csv` y `folds_sensitivity.csv`; celda de separabilidad por variable; quitar el `train_test_split` 80/20; los tres modelos tal como están en `main`, más la línea base; corridas `main`, `sens_without_mass` y `sens_with_mass`; escribir `predictions.csv`, `metrics_by_fold.csv`, `metrics.json`, `metrics_sensitivity.json`, `metrics_by_mass_provenance.json` y `comparisons.json`; las figuras existentes se rehacen con las predicciones fuera de fold de `main`, repetición 0, sin figuras nuevas; agregar `pytest` como dependencia de desarrollo y declarar `scipy` explícitamente en `pyproject.toml` (ya está en `uv.lock` como dependencia de scikit-learn; lo usa el p-valor de Nadeau y Bengio) | Implementador | T2, T3b, T4, T4b, T5, pruebas | Notebook, `pyproject.toml`, `uv.lock`, `docs/decisiones.md` | `uv run pytest -q` en verde y `uvx ruff check .` limpio, sin tocar `tests/`; dos ejecuciones seguidas dan salidas idénticas (`cmp`); tiempo de pared en la ThinkCentre anotado en `docs/decisiones.md`, y si pasa de 30 min se detiene y se escala a Mai | [AGENTE] |
| T8 | Interpretar los resultados y redactar el método, los resultados y la discusión del README: la AP de `small` frente a la prevalencia (0.138) y la línea base, con los p-valores de Nadeau y Bengio tal cual; la sensibilidad con masa (exploratoria si `exploratory` = true); las métricas por procedencia (`derived` tiene n = 4); la pregunta y la etiqueta de T4b ("por debajo o por encima del valle de radios", sin hablar de composición) | Mai | `metrics.json`, `metrics_sensitivity.json`, `metrics_by_mass_provenance.json`, `comparisons.json`, notebook ejecutado | README | Cumple los criterios 7, 9 y 12 | [TÚ] |
| T9 | Partes mecánicas del README: setup con `uv`, tabla de métricas generada desde `metrics.json` entre los marcadores del contrato, tablas de `comparisons.json` y `metrics_sensitivity.json`, y sección de autoría con los datos que dé Mai | Implementador | T8 y la lista de autoría de Mai | README | Cumple los criterios 7 y 8 | [AGENTE], con la lista de autoría [TÚ] |
| T10 | Red team M2 (otro modelo, según `AGENTS.md`). Además de los cinco ataques M2: (a) `star_radius`, que quedó abierto en T4: ablación de `star_radius` en la corrida `main` con los mismos folds, con ΔAP de `small` y test de Nadeau y Bengio por modelo, comparada con la ablación de cada una de las otras tres variables. "Cae de forma anómala" significa una ΔAP fuera del rango de esas tres ablaciones. (b) Permutar `radius` en una copia del CSV, reejecutar y comprobar que `predictions.csv` no cambia. (c) Repetir la corrida `main` sin las 12 filas frágiles de T3 y sin las 4 `derived`. Todo en una copia de trabajo, sin escribir en `data/` | Red team | Brief, diff contra `main`, `tests/`, `reports/pruebas_v1.md`, salidas de T7 | `reports/ataque_v1.md` | Los cinco ataques M2 y los ataques (a) a (c) corridos, con evidencia reproducible | [AGENTE] |
| T11 | Verificar contra el criterio de éxito, con el texto de los criterios 1, 4, 6 y 12 enmendado el 2026-10-18 | Verificador | Todo menos `docs/decisiones.md`, incluidas todas las salidas de T7 del contrato | `reports/veredicto_v1.md` | Cada uno de los 14 criterios con "cumple" o "no cumple" y su evidencia | [AGENTE] |
| T12 | P2 (aceptar la iteración), tag `iter-1`, abrir el PR y P3 (merge en GitHub) | Mai | Veredicto y ataque | Tag `iter-1` y merge | Merge hecho por Mai | [TÚ] |

## Orden

T0 → T1 → T2 → T3 → T3b → T4, T4b, T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12.

T3b va antes de T4 porque el veredicto de `mass` depende de su clasificación; T4 espera a la re-ejecución de T3b con el criterio 4 modificado. Las pruebas de T6 sobre `mass_provenance.csv` deben incluir la columna `not_testable_reason`. T6 puede empezar en cuanto Mai apruebe este cambio de contrato (2026-10-13), porque solo depende del contrato. La lista de variables vetadas la lee de `features.json`, no de `docs/decisiones.md`.

T4, T4b y T5 se cerraron el 2026-10-18. El mismo día, por regla 6, se enmendaron: `target` = `size_class` (T4); sin CV interior y con los hiperparámetros del notebook (T5); P/R/F1 de `small` como secundarias (criterio 6). Están registradas en `docs/decisiones.md` y en `docs/bitacora.md`. T6 empieza cuando Mai apruebe este cambio de contrato.

## Presupuesto

- Total: 12 h de Mai.
- Al cerrar cada tarea [TÚ], Mai anota en `docs/bitacora.md` las horas acumuladas.
- Al llegar a 6 h (50 %), se avisa en la bitácora y se compara con las tareas que faltan.
- Si se superan 18 h, se detiene el trabajo y hay revisión obligatoria con Mai antes de continuar.
