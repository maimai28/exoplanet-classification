# Veredicto v1 — T11, Verificador (2026-10-21)

**Expediente:** `exp/2026-09-30-auditoria`, iteración 1. **Versión verificada:** commit `760cc1f` (HEAD).
**Referencia:** criterio de éxito de `docs/brief.md`, con el texto de los criterios 1, 4, 6 y 12 enmendado el 2026-10-18 (el que está hoy en el brief), y el contrato de `docs/plan.md`. No se leyó `docs/decisiones.md`.
**Entorno:** ThinkCentre, Debian 13, uv 0.12.10, ruff 0.16.9, Python 3.14.

> **Cambio sin commit en el árbol de trabajo.** Al empezar, `git status` mostraba `M README.md`: un párrafo nuevo en *Discussion* ("Observational selection (red-team findings H1, H2)"), que no escribió este rol. Este veredicto evalúa el README de HEAD. Ese párrafo se comenta aparte en el paso 5.

## Veredicto global: **NO CUMPLE**

Cumplen 11 de 14 criterios. No cumplen el **3** (linaje en el README), el **4** (veredicto por variable en el README) y el **9** (afirmaciones sin evidencia o hipótesis dichas como hechos). Los tres fallos son de prosa del README. El código, los datos, la reproducibilidad y las métricas cumplen. En HEAD, los dos hallazgos mayores del red team (H1, H2) no están atendidos.

## Paso 1 — Pruebas intactas

```
$ git rev-parse --short pruebas-1^{commit}   → dd284e2
$ git diff pruebas-1 HEAD -- tests/ | wc -c  → 0
$ git diff pruebas-1 -- tests/ | wc -c       → 0   (árbol de trabajo incluido)
```
Vacío. Se continúa.

## Paso 2 — Ejecuciones

| Comando | Resultado |
|---|---|
| `uv sync --locked` | `Resolved 119 packages`, `Checked 115 packages`, sin error |
| Comando del contrato, ejecución 1 | exit 0, 34 s |
| Comando del contrato, ejecución 2 | exit 0, 34 s |
| `cmp` de las 11 salidas, ejecución 1 vs 2 | 11/11 idénticas |
| `cmp` de las 11 salidas, ejecución 1 vs commit | 11/11 idénticas (`git status` sin cambios en `data/processed/`) |
| Clon limpio (`git clone` → `uv sync --locked` → comando del contrato), en el scratchpad | exit 0, 39 s; 11/11 idénticas a la ejecución 1 |
| `uv run pytest -q` | `91 passed in 72.78s` |
| `uvx ruff check .` | `All checks passed!` |

SHA-256 (primeros 16 hex) de las salidas: `labels.csv` 550b546c5eff54fa, `features.json` 2bdfbe5f945a55a8, `folds.csv` b75bd9108162abca, `folds_sensitivity.csv` be8543e5c6a427dc, `predictions.csv` f5a023a0aa747a99, `metrics_by_fold.csv` cbaa187fe5163c39, `metrics.json` 84fb4118ea58839f, `metrics_sensitivity.json` 3280c6aa5961f046, `metrics_by_mass_provenance.json` 3f235f46f6cd9d99, `comparisons.json` 5aa5fd9e3ce09b51, `grouping_report.json` d0dfcbd29f24c0e6.

## Paso 3 — Los 14 criterios

| # | Criterio | Veredicto | Evidencia (resumen; el detalle va abajo) |
|---|---|---|---|
| 1 | Reproducible | **cumple** | Clon limpio + `uv sync --locked` + comando del README (`README.md:10-13`): exit 0; dos ejecuciones con las 11 salidas idénticas byte a byte; `test_reproducibility.py` y `test_format.py` en verde |
| 2 | Datos crudos inmutables | **cumple** | `sha256sum data/raw/exoplanets_clean.csv` = `git show b316a47:exoplanets_clean.csv \| sha256sum` = `SHA256SUMS` = 15f10a81…6378; el notebook lee `data/raw/exoplanets_clean.csv` (celda `setup`, `RAW_CSV`); `test_raw_data.py` en verde |
| 3 | Linaje documentado | **no cumple** | El README no registra la consulta o descarga con fecha ni ningún filtro con sus filas antes y después (ver 3.1). La parte de `docs/decisiones.md` no se revisó por instrucción |
| 4 | Veredicto de fuga por variable | **no cumple** | Lo automatizable cumple (`test_features.py`, `test_mass_provenance.py`, filas `measured`, `metrics_by_mass_provenance.json`). La prosa no: `README.md:37-40` no da veredicto, razón ni evidencia de procedencia para `orbital_period`, `star_mass` y `star_teff` (ver 3.2) |
| 5 | Sin fuga entre particiones | **cumple** | `test_no_group_split_across_folds` en verde; recálculo propio: 0 grupos con más de un `fold` por `repeat` en `folds.csv` (3115 líneas) y `folds_sensitivity.csv` (1180) |
| 6 | Métricas con incertidumbre | **cumple** | Hiperparámetros idénticos a 1f2e02f; SGKF 5 × semillas 0–4, sin CV interior; preprocesamiento dentro del `Pipeline`, ajustado por fold; pruebas de métricas y comparaciones en verde (ver 3.3) |
| 7 | README = ejecución | **cumple** | `test_readme.py` en verde; recálculo propio: 0 discrepancias en la tabla principal, las dos de sensibilidad y la de comparaciones |
| 8 | Autoría declarada | **cumple** | `README.md:120-146` cubre §1–§14 del notebook, el README por partes, `tests/`, los datos y b316a47/1f2e02f; modelos y fechas coinciden con los commits (ver 3.4) |
| 9 | Afirmaciones sostenidas | **no cumple** | Hipótesis dichas como hechos y afirmaciones sin evidencia en `README.md:23, 29, 37, 38, 39, 115, 116, 118` (ver 3.5) |
| 10 | Sin funcionalidad nueva | **cumple** | `git diff main HEAD -- classification.ipynb src/`: los mismos tres modelos + `DummyClassifier(strategy="prior")` (admitido por el criterio 6 y S7); las variables son un subconjunto de las originales; 0 coincidencias de búsqueda de hiperparámetros o modelos nuevos (ver 3.6) |
| 11 | Calidad | **cumple** | `91 passed`; `All checks passed!` |
| 12 | Pregunta y etiqueta | **cumple** | Pregunta en una frase, `README.md:23`; definición y razón del cambio de nombre, `README.md:30`; `test_labels.py` en verde (ver 3.7) |
| 13 | Particiones agrupadas por sistema | **cumple** | `test_folds.py` y `test_grouping_report.py` en verde; `grouping_report.json`: `n_groups` 504, `max_group_size` 7, `n_groups_multi_hostname` 4 (igual que S4) |
| 14 | Emparejamiento uno a uno | **cumple** | `lineage.csv`: 623 filas, 623 `row_id` distintos; `unique` 521, `none` 83, `ambiguous` 19; 0 `pl_name` repetidos entre las `unique`; `test_lineage.py` en verde |

### 3.1 Criterio 3 (revisión manual)

El criterio pide que **el README y** `docs/decisiones.md` registren la fuente, la consulta o descarga con fecha, cada filtro con sus filas antes y después, y la regla de etiquetado.

- Fuente: `README.md:29`, "Exact origin unknown: the values match an older release of the NASA Exoplanet Archive *PSCompPars* table". Declara lo desconocido. Lo que se intentó solo aparece como "row-level matching in `data/processed/lineage.csv`".
- Consulta o descarga con fecha: no está en el texto del README. La consulta TAP de T3 solo se ve en el nombre de archivo `pscomppars_provenance_2026-10-13.csv`, dentro de la tabla de autoría (`README.md:132`). La descarga del Proyecto 1 (2026-09-18, SHA-256 e5570cba…) no aparece.
- Filtros con filas antes y después: no hay ninguno. El README no dice cómo se pasó del catálogo (5906 filas en el Proyecto 1, según S1) a 623, ni que ese paso sea "desconocido".
- Regla de etiquetado: sí, `README.md:30` (R ≥ 2 R⊕, 623/623).
- `docs/decisiones.md`: no revisado, por instrucción de esta tarea. Aunque esa parte estuviera completa, la del README falta.

### 3.2 Criterio 4 (revisión manual de la prosa)

El criterio pide que el README dé "un veredicto para cada una de las cinco variables, con su razón y la evidencia de procedencia", con las categorías fuga / sin fuga / incierta.

| Variable | `README.md` | ¿Veredicto? | ¿Razón? | ¿Evidencia de procedencia? |
|---|---|---|---|---|
| `mass` | 38 | Implícito ("excluded from the main model"), sin categoría | Sí ("may have been computed from radius") | Sí: conteos 4 / 236 / 383, iguales a `mass_provenance.csv` |
| `orbital_period` | 39 | No (solo aparece en la lista "Main model features") | No | No |
| `star_mass` | 39 | No | No | No |
| `star_radius` | 39 | No, sin categoría | Parcial (entra en R = (Rp/R*)·R*) | No; "its effect is tested by ablation", pero el README no da el resultado ni cita dónde está |
| `star_teff` | 39 | No | No | No |

`radius` (`README.md:37`) no es una de las cinco. Lo demás del criterio sí está: la separabilidad con una variable se imprime (celda `separability`) y las métricas por procedencia van en `metrics_by_mass_provenance.json`, con las llaves `measured`/`derived`/`unverifiable` y `n` = 236/4/383.

### 3.3 Criterio 6 (revisión manual del método)

- **Hiperparámetros.** `git show main:classification.ipynb`, celda 14, frente a HEAD, celda `models`: `Pipeline(StandardScaler, LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000))`, `RandomForestClassifier(class_weight="balanced", n_estimators=300, random_state=42)` y `Pipeline(StandardScaler, SVC(class_weight="balanced", kernel="rbf", random_state=42))`, idénticos en los dos. Se agrega `DummyClassifier(strategy="prior")`.
- **Esquema.** Celda `groups-and-folds`: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=repeat)` con `REPEATS = range(5)`. Sin CV interior y sin conjunto de prueba aparte.
- **Ajuste por fold.** Celda `predictions`: `clone(model).fit(X[~test], y_run[~test])`. El escalado vive dentro del `Pipeline`, así que se ajusta solo con el entrenamiento del fold.
- **Score.** `predict_proba[:, 1]` con `classes_ == ["large", "small"]` (afirmado con `assert`); `decision_function` en el SVM.
- **Comparación.** Celda `comparisons`: t = d̄ / √((1/J + ρ)·s²), `df` = 24, p de dos colas; ρ = 0.250008. Hay 6 pares en `main`.
- **Sensibilidad.** `n_small` = 17 < 25 → `exploratory` = true y `comparisons.json` solo tiene la llave `main`.

### 3.4 Criterio 8 (revisión manual)

- **Notebook por secciones.** El notebook tiene §1–§14. La tabla de autoría (`README.md:135-137`) asigna §1, §3, §7, §12 y §13 (código original adaptado), §2, §4–§6, §8–§11 y §14 (T7), y la celda `readme-tables` de §10 (T9). No falta ninguna sección.
- **Commits.** b316a47 y 1f2e02f: "Mai, con asistencia de Claude Sonnet 5", 2026-09-19. Coincide con su trailer `Co-Authored-By: Claude Sonnet 5`.
- **Tareas de agente.** Las de T1, T2, T3, T3b, T6, T7 y T9 dicen claude-opus-5-5. Coincide con el trailer `Claude Opus 5.5` de 8c93eb2, 94fb11b, 19605bb, 43a9b14, 1617f94, dd284e2, 93fc459, 922540b y 834757e, y las fechas coinciden con las de esos commits.
- **T8.** Atribuida a Mai, a partir de un borrador de Claude. f2cc43a no tiene trailer, lo cual es coherente.
- **Observaciones que no cambian el veredicto:**
  - `README.md:142` dice "pendiente" para `reports/ataque_v1.md`, pero ya está en 760cc1f.
  - `README.md:145` dice "Gemini (Antigravity CLI) as red team". Ni `reports/ataque_v1.md` ni 760cc1f lo registran, así que no se pudo comprobar.
  - Hay celdas en español dentro de un README en inglés ("agente", "con asistencia de", "pendiente").

### 3.5 Criterio 9 (revisión manual de la prosa)

Los números del README están respaldados (paso 4). No cumplen las afirmaciones siguientes:

| `README.md` | Afirmación | Problema |
|---|---|---|
| 23 | "The original label turned out to be a threshold on planet radius" | Hipótesis dicha como hecho. El paso que generó la etiqueta no está versionado (S1), y S5/T4b manda reportarla "como hipótesis sostenida (623/623)". Es el ejemplo literal del criterio. La línea 30 sí lo dice bien ("reproduced exactly … by the rule") |
| 37 | "the label is a threshold on it" | El mismo problema que en la línea 23 |
| 29 | "the values match an older release of … *PSCompPars*" | Inferencia dicha como hecho: solo 521/623 filas tienen pareja `unique` en `lineage.csv`, y 383 masas no coinciden con el Proyecto 1. Lo de "older release" es la hipótesis que explica esa discrepancia |
| 38 | "383 cannot be verified because they come from an older catalog version" | Causa sin evidencia citada. Lo que está establecido es que no coinciden a ±1 % con el Proyecto 1 |
| 39 | "its effect is tested by ablation" | El README no da el resultado ni cita la fuente (la ablación solo está en `reports/ataque_v1.md`, ataque (a)) |
| 115 | "consistent with known trends (short-period giant planets in transit surveys, small planets being more common around cool, low-mass stars)" | Afirmación de literatura sin cita. Además, es justo lo que H1 atribuye a un sesgo de detección (ver paso 5) |
| 116 | "Measured masses come mostly from radial-velocity follow-up …; the unverifiable rows come from an older catalog release with different detection biases" | Sin evidencia: los datos no registran el método de descubrimiento (lo reconoce el propio párrafo sin commit del árbol de trabajo) |
| 118 | "Its best result, F1 = 0.72 …, depended on `mass`" | La cifra es correcta (1f2e02f, celda 16: F1 = 0.718; 17 `terrestrial` en la prueba), pero no cita el commit. Además, "depended on mass" no está probado: entre los dos resultados cambiaron a la vez la masa, el esquema de partición y el agrupamiento |

Hay más cifras correctas que tampoco citan su archivo, aunque están en él: `README.md:30` (86/537, `labels.csv`), 31 (504 grupos y un máximo de 7, `grouping_report.json`), 38 (4/236/383, `mass_provenance.csv`) y 72 (ROC-AUC 0.81/0.68, `metrics_by_mass_provenance.json`).

### 3.6 Criterio 10 (revisión del diff)

`git diff --stat main HEAD` incluye 49 archivos. En lo que corre, el diff contiene:

- **Notebook.** La lista `FEATURES` de `main` (`mass`, `orbital_period`, `star_mass`, `star_radius`, `star_teff`) pasa a `features.json`: `main` tiene 4 de esas 5 y `sensitivity_mass` tiene las 5. No hay variables nuevas.
- **`src/t3b_mass_provenance.py`.** Clasifica la procedencia de la masa (alcance 2) y no entrena modelos.
- **Búsqueda de patrones.** `grep -cE 'GridSearch|RandomizedSearch|HalvingGrid|cross_val|BayesSearch|optuna|param_grid|XGB|LGBM|GradientBoosting|KNeighbors|MLPClassifier'` sobre las líneas añadidas (sin imágenes) da 0.
- **`pyproject.toml`.** Solo agrega `scipy` y `pytest` (dev), lo que admite el brief en Restricciones.

### 3.7 Criterio 12 (revisión manual)

- **Pregunta.** En una frase, en negritas, en `README.md:23`: "can a planet's size class (below or above 2 R⊕) be predicted from its orbital period and host-star properties alone?"
- **Etiqueta.** `README.md:30`: `small` (R < 2 R⊕, 86) y `large` (537), renombradas desde `planet_type`.
- **Razón del cambio de nombre.** También en `README.md:30`: "physically misleading … separates *size*, not composition".
- **Mapeo.** `test_size_class_mapping_on_all_rows` está en verde. Recálculo propio: la regla R ≥ 2/11.208981 R_J reproduce 623/623.
- **Observación.** La pregunta, la definición y la razón quedan en dos párrafos, no en una sola frase. Se lee "en una frase" como referido a la pregunta, y por eso se da por cumplido.

## Paso 4 — Números del README frente a `data/processed/`

Recalculado con un script de solo lectura sobre las salidas de esta ejecución:

- Tablas entre marcadores: `metrics`, `comparisons` y las dos de `sensitivity`. **0 discrepancias.**
- Cifras en la prosa:

| Afirmación (`README.md`) | Valor en los archivos | ¿Respaldada? |
|---|---|---|
| AP 0.43–0.52 vs 0.14 (23); prevalencia 0.138 (48) | AP 0.4264 / 0.4330 / 0.5153; 86/623 = 0.138042 | sí |
| 86 `small`, 537 `large` (30) | `labels.csv` | sí |
| 504 grupos, máximo 7 (31) | `grouping_report.json` | sí |
| 4 / 236 / 383 (38, 118) | `mass_provenance.csv` | sí |
| p < 0.001 frente a la línea base (68) | 0.000133, 0.000030, 0.000004 | sí |
| ROC-AUC 0.77–0.80 (68) | 0.7694–0.7970 | sí |
| p = 0.20–0.91 entre modelos (68) | 0.201358, 0.263822, 0.905695 | sí |
| LR: recall 68 %, precisión 32 %; RF: recall 35 %, precisión 44 % (70) | 0.6841 / 0.3222; 0.3472 / 0.4353 | sí |
| Accuracy 0.76–0.85 < 0.86 (70) | 0.7575–0.8468; línea base 0.862 | sí |
| LR ROC-AUC 0.81 `unverifiable`, 0.68 `measured` (72) | 0.810821; 0.677464 | sí |
| Sin masa, ROC-AUC 0.55–0.63; SVM 0.55 → 0.83 (72) | 0.5488–0.6292; 0.5488 → 0.8299 | sí |
| 17 `small` en la sensibilidad (50, 72) | `metrics_sensitivity.json`: `n_small` 17 | sí |
| AP 3–4× sobre el azar (115) | 3.09× – 3.73× | sí |
| F1 de `small` 0.38–0.47 (118) | 0.3791–0.4711 | sí |
| ρ = 0.250, df = 24 (75) | 0.250008; 24 | sí |
| F1 original = 0.72, unos 17 `small` en la prueba (118) | 1f2e02f, celda 16: 0.718; soporte 17 | sí (pero sin cita, ver 3.5) |

No hay ningún número, p-valor ni conteo del README que contradiga las salidas.

## Paso 5 — Hallazgos de `reports/ataque_v1.md`

| Hallazgo | Severidad | ¿Atendido en el README de HEAD? |
|---|---|---|
| H1: sesgo de detección por tránsito (δ ≈ (Rp/R*)²) que confunde los parámetros estelares con el tamaño | mayor | **No.** No hay mención en `README.md:111-118`. La línea 115 presenta "small planets being more common around cool, low-mass stars" como tendencia conocida, que es justo lo que H1 atribuye a selección. No hay justificación registrada |
| H2: muestra restringida a planetas con masa, prevalencia de `small` artificial (13.8 %) | mayor | **No.** "Limitations" (117) menciona el origen y la versión del catálogo, pero no el sesgo de selección por masa. No hay justificación registrada |
| H3: sobreajuste de RF (AP de entrenamiento 1.0) | menor | No aplica: los hiperparámetros están congelados por el criterio 6 |
| H4: ablación de `star_radius` en el SVM, formalmente anómala (ΔAP +0.009, p = 0.71) | menor | No. El README dice que el efecto "is tested by ablation" (39) y no da el resultado |
| H5: explicación incompleta de la brecha de ROC-AUC 0.81/0.68 | menor | No |

**Párrafo sin commit del árbol de trabajo** (no forma parte de la versión verificada). Atiende H1 y, en parte, H2: explica la profundidad de tránsito, el sesgo hacia estrellas pequeñas y la restricción a planetas con masa catalogada, con cautela ("to the extent that…", "cannot be measured here"). Si se hace commit, quedan dos cosas por resolver:

1. Contradice `README.md:116`. El párrafo dice "the data do not record the discovery method", y la línea 116 afirma que las masas medidas vienen "mostly from radial-velocity follow-up".
2. No resuelve la parte de H2 que toca el criterio 3, porque el filtrado hasta 623 filas sigue sin documentarse en el README.

Nota menor: el mensaje de 760cc1f dice "2 menores", pero el reporte tiene 3 (H3, H4, H5).

## Observaciones fuera de los criterios

- **`df` sobrescrito.** En la celda `readme-tables` del notebook, `(df,) = {test["df"] for test in tests}` reemplaza el DataFrame `df` por el entero 24. Ninguna celda posterior usa `df` y las salidas no cambian, pero una celda nueva que lo use después de §10 fallaría sin aviso claro.
- **Configuración de ruff.** `ruff.toml` del repo (desde a031544, 2026-09-30) selecciona solo E, F e I. Con `~/dotfiles/ruff.toml` (agrega UP, B, SIM y NPY) aparecen 14 avisos (12 B905, 2 SIM300). El criterio 11 se juzga con la configuración del repo, así que no afecta el veredicto.
- **Efecto de la verificación en `data/processed/`.** Las ejecuciones de este rol reescribieron las 11 salidas con bytes idénticos (`git status` sin cambios en `data/processed/`).

## Qué haría falta para CUMPLE

Esto no es una propuesta de redacción: lo que se escriba es decisión de Mai (T8). Falta:

- **Criterio 3.** Que el README registre la consulta o descarga con fecha y cada filtro con sus filas antes y después, o "desconocido" con lo que se intentó.
- **Criterio 4.** Que el README dé, para cada una de las cinco variables, un veredicto en las categorías del brief, su razón y su evidencia de procedencia.
- **Criterio 9.** Que las afirmaciones de 3.5 citen evidencia o se presenten como hipótesis, y que H1 y H2 queden atendidos o justificados.
