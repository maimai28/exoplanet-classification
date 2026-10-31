# Pruebas v1 — T6, Tester fase A (2026-10-18)

Rama `exp/2026-09-30-auditoria`, tag `pruebas-1`. Referencias: `docs/brief.md`, contrato de `docs/plan.md` y "Enmiendas por regla 6 (2026-10-18)" de `docs/decisiones.md`. No se leyó `src/` ni el notebook (solo se inspecciona en las pruebas estáticas).

## Resultado hoy

`uv run --with pytest pytest -q` da **76 fallan y 15 pasan** (91 pruebas).

| Causa del fallo | Pruebas | ¿Razón esperada? |
|---|---|---|
| Falta una salida de T7 en `data/processed/` (`labels.csv`, `features.json`, `folds*.csv`, `predictions.csv`, `metrics_by_fold.csv`, `metrics*.json`, `comparisons.json`, `grouping_report.json`) | 67 | Sí: T7 no ha corrido |
| El notebook falla al ejecutarse: `FileNotFoundError: 'exoplanets_clean.csv'` (lo busca en la raíz, no en `data/raw/`) | 3 (criterio 1) | Sí: el notebook es el de `main` |
| Estático: el notebook lee el CSV desde la raíz | 1 (criterio 2) | Sí |
| Estático: hay literales de columnas en las celdas 6 y 7, y no se lee `features.json` | 1 (T6 k) | Sí |
| El README no tiene los marcadores `metrics:start/end` ni el comando `uv sync --locked` | 2 (criterios 1 y 7) | Sí: T9 |
| `pyproject.toml` no declara `scipy` ni `pytest` (grupo dev) | 1 | Sí: lo agrega T7 |
| `uvx ruff check .` reporta 7 errores, todos en `classification.ipynb` (6 E501 y 1 E741) | 1 (criterio 11) | Sí: el notebook es el de `main`; `tests/` está limpio |

**Las 15 que pasan** verifican lo que ya existe: `data/raw/` contra SHA256SUMS y el blob de b316a47 (T2, 4 pruebas), `lineage.csv` (T1/T3, 4), `mass_provenance.csv` con la regla de combinación del criterio 4 (T3b, 6) y `uv lock --check` (1). Ninguna pasa trivialmente: comparan contra datos fijos.

**Verificación de las propias pruebas** (en una copia de trabajo, en el scratchpad, sin tocar `data/`):
- Con salidas sintéticas generadas siguiendo el contrato, las 79 pruebas de datos pasan. Las que dependen del notebook o del README se excluyeron de esta corrida.
- Siete mutaciones, cada una detectada: `radius` en `main`, una etiqueta invertida, un grupo de 7 filas partido entre folds, AP + 1e-5 en `metrics_by_fold.csv`, un `p_value` alterado, una fila `measured` que falta en `sens_with_mass` y `17` escrito como `17.0` en el JSON.
- Las componentes reconstruidas dan 504 grupos, con un máximo de 7 filas y 4 con más de un `hostname`, igual que S4 del brief.

## Decisiones de Mai para escribir las pruebas (2026-10-18)

El contrato no fijaba estos tres puntos; se preguntaron antes de escribir:
1. **(k)** Los literales `orbital_period`, `star_mass`, `star_radius`, `star_teff`, `mass` y `radius` aparecen como string exacto solo en la celda que escribe `features.json` (con `json.dump(s)`), y una celda posterior lo vuelve a leer con `json.load(s)`.
2. **Orden de los CSV:** las llaves de texto (`run`, `model`) van en orden lexicográfico ascendente, como `sort_values`.
3. **Tabla del README:** los encabezados son las 7 llaves de métrica y la primera columna lleva las 4 llaves de modelo, tal cual (se aceptan backticks).

## Mapa criterio → pruebas

| Criterio / contrato | Pruebas (`tests/`) | Por qué falla hoy |
|---|---|---|
| 1 Reproducible | `test_reproducibility.py`: `test_notebook_runs_and_writes_every_contract_output`, `test_two_runs_are_byte_identical`, `test_repository_outputs_are_what_the_command_produces`, `test_lockfile_is_consistent_with_pyproject`; `test_readme.py::test_readme_documents_the_run_command`; `test_format.py` (formato determinista: 6 JSON y 7 CSV) | El notebook falla al leer el CSV; faltan las salidas y el README |
| 2 Datos crudos inmutables | `test_raw_data.py`: `test_sha256sums_records_raw_csv`, `test_every_file_in_sha256sums_matches`, `test_raw_csv_bytes_equal_commit_b316a47`, `test_raw_csv_has_623_rows`, `test_notebook_reads_raw_csv_from_data_raw` | Solo la estática: el notebook lee desde la raíz |
| 4 Fuga (`features.json`, T6 a y k) | `test_features.py`: `test_features_json_matches_contract`, `test_radius_excluded_from_model_inputs`, `test_mass_only_in_sensitivity`, `test_target_is_size_class`, `test_notebook_takes_x_only_from_features_json` | No existe `features.json`; hay literales en las celdas 6 y 7 |
| 4 Procedencia (`mass_provenance.csv`) | `test_mass_provenance.py` (6 pruebas: columnas, dominios, `not_testable_reason`, vacíos por `gap_11.1_14.3`, vacíos según el linaje, regla de combinación) | Pasan (T3b) |
| 4 Sensibilidad = filas `measured` (T6 d) | `test_folds.py::test_sensitivity_rows_are_exactly_measured`, `test_predictions.py::test_sensitivity_runs_use_exactly_measured_rows`, `test_metrics.py::test_metrics_sensitivity_keys_and_counts` | Faltan `folds_sensitivity.csv`, `predictions.csv` y `metrics_sensitivity.json` |
| 4 `metrics_by_mass_provenance.json` (T6 i) | `test_metrics.py`: `test_metrics_by_mass_provenance_keys_and_n`, `test_metrics_by_mass_provenance_recomputed_from_predictions` | Falta el archivo |
| 5 Sin fuga entre particiones | `test_folds.py::test_no_group_split_across_folds[folds.csv / folds_sensitivity.csv]` | Faltan los folds |
| 6 Métricas y modelos (T6 e, f) | `test_metrics.py`: `test_metrics_by_fold_columns`, `test_metrics_by_fold_grid_and_order`, `test_metrics_by_fold_recomputed_from_predictions`, `test_baseline_sanity`, `test_metrics_json_schema`, `test_metrics_json_recomputed_from_metrics_by_fold`, `test_metrics_sensitivity_recomputed_from_metrics_by_fold` | Faltan los archivos |
| 6 Sensibilidad exploratoria (T6 h) | `test_metrics.py::test_exploratory_flag_follows_n_small`, `test_comparisons.py::test_top_level_keys_follow_exploratory` | Faltan los archivos |
| 6 Comparaciones (T6 g) | `test_comparisons.py`: `test_main_has_the_six_pairs_in_contract_order`, `test_pair_fields`, `test_sensitivity_compares_with_vs_without_mass_per_model`, `test_main_pairs_recomputed_from_metrics_by_fold` | Falta `comparisons.json` |
| Contrato `predictions.csv` | `test_predictions.py` (10 pruebas: columnas, conteo y llave única, orden, cobertura `main`, filas `measured`, fold igual al de los archivos de folds, dominio de `pred`, umbral por defecto, score en [0, 1], score constante de la línea base) | Falta el archivo |
| 7 README = métricas | `test_readme.py`: `test_results_table_layout`, `test_results_table_matches_metrics_json` | Faltan los marcadores y `metrics.json` |
| 11 Calidad | `test_quality.py::test_ruff_check_is_clean`; la otra mitad es la propia suite | 7 errores de ruff en el notebook |
| 12 Etiqueta (T6 b) | `test_labels.py`: `test_labels_columns`, `test_labels_rows_ordered_by_row_id`, `test_planet_type_copied_verbatim_from_raw`, `test_size_class_mapping_on_all_rows` | Falta `labels.csv` |
| 13 Grupos (T6 c y j) | `test_folds.py` (por archivo: columnas, una línea por (`row_id`, `repeat`), formato de `group_id`, componentes exactas, una `small` por fold, reproducción de `StratifiedGroupKFold`); `test_grouping_report.py` (4 pruebas: llaves enteras, sumas, `n_groups` frente a `folds.csv`, las 9 llaves recalculadas) | Faltan los archivos |
| 14 Uno a uno | `test_lineage.py` (4 pruebas) | Pasan (T1) |
| Restricción de dependencias | `test_reproducibility.py::test_declared_dependencies` | Faltan `scipy` y `pytest` (dev) |

## Criterios no verificables automáticamente

| Criterio | Por qué |
|---|---|
| 3 Linaje documentado | Es texto en `docs/decisiones.md` y el README; "reconstruido" o "desconocido" es juicio. Lo revisa el Verificador. |
| 4 Veredicto por variable en el README | Las razones y la evidencia son prosa. Se prueba lo mecánico (`features.json`, filas `measured`, conteos). |
| 6 Hiperparámetros iguales a 1f2e02f; preprocesamiento ajustado solo con el train de cada fold | No se observan en las salidas sin leer el código. Es revisión del método (Verificador y red team). |
| 8 Autoría | Asignación de partes a personas; revisión. |
| 9 Afirmaciones sostenidas | Juicio sobre la prosa; revisión del Verificador y del red team. |
| 10 Sin funcionalidad nueva | Revisión del diff contra `main`. |
| 12 Pregunta y etiqueta en el README | Es prosa; solo el mapeo de `labels.csv` es automatizable. |
| 1 Clon limpio con `uv sync --locked` | La prueba usa `uv lock --check` y ejecuta en una copia del árbol, no en un clon nuevo con red. |

## Notas para T7 (sin resolver por el Implementador)

- **Cada archivo se calcula desde el anterior ya escrito** (contrato): las métricas por fold salen de los `score` de `predictions.csv` redondeados a 6 decimales; `metrics.json`, `metrics_sensitivity.json` y `comparisons.json` salen de los valores de `metrics_by_fold.csv`. Si se calculan desde valores en memoria sin redondear, t, p y AP pueden diferir en más de 1e-6 y las pruebas fallan. La tolerancia es de una unidad en el sexto decimal.
- **"6 decimales fijos" se lee literal:** en el JSON, `0.123400` y no `0.1234`; los enteros (`n`, `n_small`, las llaves de `grouping_report.json`) van sin punto decimal.
- `uv run pytest -q` no corre hoy porque `pytest` no está en el entorno; T7 lo agrega como dependencia de desarrollo. Mientras tanto se usó `uv run --with pytest pytest -q`.
- Las pruebas del criterio 1 ejecutan el notebook dos veces en una copia temporal, con un límite de 30 min por corrida (T7).

## Limitaciones conocidas

- (k) es estática y solo mira el notebook: si X se arma en un módulo importado desde `src/`, la prueba no lo ve.
- La rama `sensitivity` de `comparisons.json` solo se revisa por estructura: el contrato no fija el nombre de sus llaves. Con `n_small` = 17 < 25 es `exploratory` = true y esa rama no debe existir, lo cual sí se prueba.
- Las pruebas del criterio 1 corren `jupyter nbconvert` con el intérprete de pytest (el mismo entorno de uv), no con `uv run` anidado.
- `test_raw_csv_bytes_equal_commit_b316a47` necesita el historial de git, y `test_quality.py` necesita `uvx`.
