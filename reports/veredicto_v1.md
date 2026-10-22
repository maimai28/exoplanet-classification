# Veredicto v1 (re-verificación) — T11, Verificador (2026-10-22)

**Expediente:** `exp/2026-09-30-auditoria`, iteración 1. **Versión verificada:** commit `476b930` (HEAD), árbol de trabajo limpio.
**Referencia:** criterio de éxito de `docs/brief.md`, con el texto de los criterios 1, 4, 6 y 12 enmendado el 2026-10-18 (el que está hoy en el brief), y el contrato de `docs/plan.md`. No se leyó `docs/decisiones.md`.
**Entorno:** ThinkCentre, Debian 13, uv 0.12.10, ruff 0.16.9, Python 3.14.

> **Este archivo reemplaza al veredicto de `aa9a472`** (NO CUMPLE en los criterios 3, 4 y 9 sobre `760cc1f`). Esa versión sigue en el historial de git. Desde `760cc1f` solo cambiaron `README.md` (`16df2b4`, T8 iteración 2), `docs/bitacora.md` y este archivo. `git diff --stat 760cc1f HEAD -- classification.ipynb src/ tests/ pyproject.toml uv.lock data/` sale vacío.

## Veredicto global: **NO CUMPLE**

Cumplen 13 de 14 criterios. La iteración 2 de T8 resolvió los criterios 3 y 4 y los hallazgos H1 y H2. Sigue sin cumplir el **9**, por tres afirmaciones del README:

1. `README.md:45` dice que 4 masas caen sobre la relación de Chen & Kipping, pero `mass_provenance.csv` solo tiene 3 filas `on_relation`.
2. `README.md:160` da como hecho la fuente "*PSCompPars* (older release)", que `README.md:29-30` declara no documentada y presenta como hipótesis.
3. `README.md:156-157` atribuye `reports/ataque_v1.md` al Verificador (T11) y marca como "pendiente" un veredicto que ya existe.

Reproducibilidad, datos, código y métricas: cumplen sin cambios respecto a `aa9a472`.

## Paso 1 — Pruebas intactas

```
$ git diff pruebas-1 HEAD -- tests/          → (vacío)
$ git diff pruebas-1 HEAD --stat -- tests/   → (vacío)
```
Se continúa.

## Paso 2 — Ejecuciones

| Comando | Resultado |
|---|---|
| `uv sync --locked` | `Resolved 119 packages`, `Checked 115 packages`, exit 0 |
| Comando del contrato (`README.md:12`), ejecución 1 | exit 0, 33 s |
| Comando del contrato, ejecución 2 | exit 0, 35 s |
| `cmp` de las 11 salidas, ejecución 1 vs 2 | 11/11 idénticas |
| `git status --short data/processed` tras las dos ejecuciones | vacío (iguales a lo que está en el commit) |
| `uv run pytest -q` | `91 passed in 72.71s` |
| `uvx ruff check .` | `All checks passed!` |

SHA-256 (primeros 16 hex), idénticos a los de `aa9a472`: `labels.csv` 550b546c5eff54fa, `features.json` 2bdfbe5f945a55a8, `folds.csv` b75bd9108162abca, `folds_sensitivity.csv` be8543e5c6a427dc, `predictions.csv` f5a023a0aa747a99, `metrics_by_fold.csv` cbaa187fe5163c39, `metrics.json` 84fb4118ea58839f, `metrics_sensitivity.json` 3280c6aa5961f046, `metrics_by_mass_provenance.json` 3f235f46f6cd9d99, `comparisons.json` 5aa5fd9e3ce09b51, `grouping_report.json` d0dfcbd29f24c0e6.

No se repitió el clon limpio: `aa9a472` lo hizo sobre `760cc1f`, y desde entonces no cambió ningún archivo que afecte la ejecución (ver la nota de arriba).

## Paso 3 — Los 14 criterios

| # | Criterio | Veredicto | Evidencia |
|---|---|---|---|
| 1 | Reproducible | **cumple** | `uv sync --locked` + comando de `README.md:10-13`: exit 0; dos ejecuciones con 11/11 salidas idénticas byte a byte; `test_reproducibility.py` y `test_format.py` en verde |
| 2 | Datos crudos inmutables | **cumple** | `sha256sum data/raw/exoplanets_clean.csv` = `git show b316a47:exoplanets_clean.csv \| sha256sum` = `SHA256SUMS` = 15f10a81…6378; `RAW_CSV = Path("data/raw/exoplanets_clean.csv")` en la celda `setup`; `test_raw_data.py` en verde |
| 3 | Linaje documentado | **cumple** (parte del README) | `README.md:29-34`: fuente y filtros de origen declarados "not documented", con lo que se intentó (T1); descarga de referencia del 2026-09-18 y consulta T3 del 2026-10-13; filtros del análisis 623 → 623 (sensibilidad: 236); regla de etiquetado. La parte de `docs/decisiones.md` no se revisó por instrucción (ver 3.1) |
| 4 | Veredicto de fuga por variable | **cumple** | Tabla en `README.md:42-49`: las cinco variables con veredicto en las categorías del brief, razón y evidencia; pruebas de `features.json`, de las filas `measured` y de `metrics_by_mass_provenance.json` en verde (ver 3.2) |
| 5 | Sin fuga entre particiones | **cumple** | `test_folds.py` en verde; `folds.csv` sin cambios respecto a `aa9a472`, que dio 0 grupos partidos |
| 6 | Métricas con incertidumbre | **cumple** | Hiperparámetros de la celda `models` idénticos a los de `main` (`class_weight="balanced"`, `max_iter=1000`, `n_estimators=300`, SVC por defecto, escalado en el `Pipeline`); SGKF 5 × semillas 0–4; ajuste con `clone(model).fit(X[~test], …)` por fold; `comparisons.json` con 6 pares, `df` 24 y ρ 0.250008; pruebas de métricas en verde (ver 3.3) |
| 7 | README = ejecución | **cumple** | `test_readme.py` en verde; recálculo propio de las tablas de métricas (4 filas), de sensibilidad (4 + 4) y de comparaciones (6): 0 discrepancias a 3 decimales |
| 8 | Autoría declarada | **cumple** | `README.md:140-155` asigna el notebook §1–§14, las partes del README, `tests/`, los datos y b316a47/1f2e02f. Tiene defectos en las filas de `reports/`, que se cuentan en el criterio 9 (ver 3.4) |
| 9 | Afirmaciones sostenidas | **no cumple** | `README.md:45` (4 sobre la relación vs 3 `on_relation`), `README.md:160` (hipótesis dicha como hecho), `README.md:156-157` (autoría falsa, sin evidencia) (ver 3.5) |
| 10 | Sin funcionalidad nueva | **cumple** | Notebook y `src/` sin cambios desde `760cc1f`. En `git diff main HEAD -- classification.ipynb src/ pyproject.toml`, las líneas añadidas tienen 0 coincidencias de búsqueda de hiperparámetros o modelos nuevos; `pyproject.toml` solo agrega `scipy` y `pytest`; las variables son un subconjunto de las de `main` |
| 11 | Calidad | **cumple** | `91 passed`; `All checks passed!` |
| 12 | Pregunta y etiqueta | **cumple** | Pregunta en una frase en negritas (`README.md:23`); definición R ≥ 0.1784 R_J (= 2 R⊕), `small`/`large` y razón del cambio de nombre ("The original names describe composition, which the data do not contain", `README.md:33`); `test_labels.py` en verde |
| 13 | Particiones agrupadas por sistema | **cumple** | `test_folds.py` y `test_grouping_report.py` en verde; `grouping_report.json`: `n_groups` 504, `max_group_size` 7, `n_groups_multi_hostname` 4 |
| 14 | Emparejamiento uno a uno | **cumple** | `lineage.csv`: 623 filas; `unique` 521, `none` 83, `ambiguous` 19; `test_lineage.py` en verde |

### 3.1 Criterio 3 (revisión manual)

| Elemento del criterio | `README.md` | Revisión |
|---|---|---|
| Fuente | 29: "Its exact source and the filters that produced it are not documented" | Se declara desconocida, como pide el criterio |
| Lo que se intentó | 30: emparejamiento con la descarga *PSCompPars* del 2026-09-18, regla y resultado (521 `unique`, 102 sin pareja o ambiguas) | 521 y 102 (83 + 19) coinciden con `lineage.csv` |
| Consulta o descarga con fecha | 29: archivo agregado el 2026-09-19 (`b316a47`; `git show -s` da 2026-09-19 01:05 −0500); 30: descarga del 2026-09-18; 31: consulta `pl_bmassprov` del 2026-10-13 sobre 521 filas | `pscomppars_provenance_2026-10-13.csv` tiene 521 filas |
| Filtros con filas antes y después | 29: los filtros de origen son desconocidos; 32: "None: 623 rows in, 623 rows used"; sensibilidad con 236 | `predictions.csv`: 623 filas por (modelo, repetición) en `main` y 236 en `sens_*` |
| Regla de etiquetado | 33 | Recálculo: R ≥ 2/11.208981 R_J reproduce 623/623; máximo `terrestrial` 0.178, mínimo `gas_giant` 0.178428 |

Sobre `docs/decisiones.md`: no se leyó, por instrucción. Solo se ve en los metadatos de git que los commits de T1 (`8c93eb2`, +155 líneas en `docs/decisiones.md`) y de T3 (`19605bb`) lo modificaron. El veredicto "cumple" cubre la parte del README. Que `decisiones.md` cumpla su parte queda a cargo de Mai.

### 3.2 Criterio 4 (revisión manual de la prosa)

| Variable | Veredicto (`README.md`) | Razón | Evidencia | Revisión |
|---|---|---|---|---|
| `mass` | uncertain (45) | 4 derivadas, 236 medidas, 383 no verificables | `mass_provenance.csv` (T3b) | Los conteos 4/236/383 coinciden. La frase "4 masses lie on the … relation" es incorrecta: se cuenta en el criterio 9 |
| `orbital_period` | no leak (46) | Se mide por tiempos de tránsito o de VR; no usa el radio | Coincide con el catálogo a 10⁻³ en 521 filas | Cumple. Observación: la coincidencia a 10⁻³ es la regla de emparejamiento (`README.md:30`), así que se cumple por construcción. Sirve como evidencia de que el valor es el `pl_orbper` del catálogo, no como confirmación independiente |
| `star_mass` | no leak (47) | Parámetro estelar | Columna `st_mass` (T1) | Cumple |
| `star_teff` | no leak (48) | Parámetro estelar | Columna `st_teff` (T1) | Cumple |
| `star_radius` | no leak (tested) (49) | R = (Rp/R*)·R*: el radio del planeta sale de él, no al revés | Ablación: ΔAP 0.007–0.019, p ≥ 0.58 | Reproducido por este rol con los mismos folds: ΔAP +0.0072 / +0.0186 / +0.0094, p 0.5832 / 0.6039 / 0.7137. Coincide con `reports/ataque_v1.md` |

Las definiciones de `README.md:40` corresponden a las del brief. La de "leak" dice "computed from [the label]" y no menciona el radio, pero cada fila de la tabla razona sobre el radio, que es lo que pide el brief.

### 3.3 Criterio 6 (revisión manual del método)

El notebook no cambió desde `760cc1f`; se mantiene la revisión de `aa9a472`. Se volvió a comprobar:

- Celda `models` de HEAD frente a `git show main:classification.ipynb`: `LogisticRegression(class_weight="balanced", random_state=RANDOM_STATE, max_iter=1000)`, `RandomForestClassifier(class_weight="balanced", n_estimators=300, random_state=RANDOM_STATE)` y `SVC(class_weight="balanced", kernel="rbf", random_state=RANDOM_STATE)`, con `StandardScaler` en el `Pipeline` de LR y SVM. Son idénticos. Se agrega `DummyClassifier(strategy="prior")`.
- Celda `groups-and-folds`: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=repeat)` con `REPEATS = range(5)`. Sin CV interior.
- Sensibilidad: `n_small` = 17 < 25, `exploratory` = true, y `comparisons.json` solo tiene la llave `main`.

### 3.4 Criterio 8 (revisión manual)

Las partes que exige el criterio están asignadas (la cobertura del notebook §1–§14 no cambió respecto a `aa9a472`). Hay tres defectos en las filas de autoría:

- `README.md:156`, fila de `reports/ataque_v1.md`: "T10: agent: Gemini (Antigravity CLI) …; **T11: agent: Claude Code, role Verifier**, claude-opus-5-5, 2026-10-21". T11 no escribió ese archivo. Escribió `reports/veredicto_v1.md` (`aa9a472`). Parece que la atribución de T11 quedó en la fila equivocada.
- `README.md:157`: `reports/veredicto_v1.md` dice "pendiente", pero existe desde `aa9a472`.
- `README.md:154`: la fila de T8 cita solo `f2cc43a` (2026-10-21). Falta la iteración 2 (`16df2b4`, 2026-10-22).

`reports/` no está en la lista del criterio 8, así que el criterio cumple. Las dos primeras son afirmaciones factuales falsas, sin evidencia ("—"), y se cuentan en el criterio 9.

### 3.5 Criterio 9 (revisión manual de la prosa)

Ya están corregidas las ocho afirmaciones de `aa9a472` (antes en las líneas 23, 29, 37, 38, 39, 115, 116 y 118). Ahora se dicen como hipótesis ("Our hypothesis…", "(hypothesis)", "how much of that came from `mass` was not tested"), citan su fuente (`reports/ataque_v1.md`, ataques a y b, H5; "README on `main`") o se quitaron.

**No cumplen:**

| `README.md` | Afirmación | Problema |
|---|---|---|
| 45 | "4 masses lie on the Chen & Kipping (2017) mass–radius relation used by the Archive (derived from radius)" | La evidencia que cita la contradice. En `mass_provenance.csv` hay 3 filas `on_relation` (53, 284, 424). La cuarta `derived`, la fila 460, es `not_testable` con `low_precision` (residuo 0.138) y quedó `derived` porque su masa coincide con el Proyecto 1 y `pl_bmassprov` = `M-R relationship`. "4 derived" es correcto; "4 lie on the relation", no. La versión de `760cc1f` decía "4 masses are derived from radius", que era correcto, así que el error entró en la iteración 2 |
| 160 | "**Data:** NASA Exoplanet Archive, *PSCompPars* (older release)" | Da como hecho la fuente, que `README.md:29` declara no documentada y `README.md:30` presenta como hipótesis no probada ("this is not proven"). Es el patrón que pone de ejemplo el criterio. Ya estaba en `760cc1f` y el veredicto de `aa9a472` no lo señaló |
| 156-157 | Autoría de `reports/ataque_v1.md` asignada en parte a T11; `reports/veredicto_v1.md` "pendiente" | Afirmaciones falsas según el historial de git (`760cc1f`, `aa9a472`), con "—" en la columna de evidencia (ver 3.4) |

**No se pueden comprobar con las fuentes de este rol** (no bloquean, pero Mai debería revisarlas):

- `README.md:30`, "6,366 rows", la lista de columnas y la regla de emparejamiento ("10⁻³ … at least 2 of the other 5 columns within 5 %"): solo están en la descarga del Proyecto 1 (fuera del repo) y, presumiblemente, en `docs/decisiones.md`. Citan la descarga con su fecha, que es lo que pide el criterio.
- `README.md:30`, "only 284 have the same radius (within 1 %)": **coincidencia sospechosa.** En `mass_provenance.csv`, `mass_matches_p1` da 237 `true` y **284 `false`**. El 237 del README coincide con las masas que sí coinciden. El 284 es justo el número de masas que *no* coinciden. Puede ser casualidad, pero hay que comprobarlo con la descarga del Proyecto 1.

**Observaciones que no cambian el veredicto** (mismo estándar que en `aa9a472`: cifras correctas sin archivo citado):

- Cifras correctas sin archivo citado: `README.md:33` (86/537, `labels.csv`), 34 (504 y 7, `grouping_report.json`), 85 y 130 (ROC-AUC 0.81/0.68, `metrics_by_mass_provenance.json`) y 131 ("train AP = 1.0", que solo está en `reports/ataque_v1.md`, H3; este rol lo reprodujo: 1.0000 ± 0.0000).
- `README.md:130`, "univariate ROC-AUC 0.78 → 0.58". Recálculo con `max(AUC, 1 − AUC)`: en `unverifiable`, `star_radius` 0.794, `star_teff` 0.770 y `star_mass` 0.805; en `measured`, 0.579, 0.578 y **0.672**. El 0.58 vale para dos de las tres variables, y "0.78" no aparece tal cual en H5 (que da 0.77–0.80). Está dentro de lo que cita, pero es impreciso.
- `README.md:33`, la cita de Fulton et al. (2017), AJ 154, 109, es correcta.

## Paso 4 — Números del README frente a `data/processed/`

Recalculado con un script de solo lectura sobre las salidas de esta ejecución:

| Afirmación (`README.md`) | Valor en los archivos | ¿Respaldada? |
|---|---|---|
| Tablas entre marcadores (`metrics`, `comparisons`, `sensitivity` ×2) | — | sí, 0 discrepancias |
| 623/623 por la regla R ≥ 2 R⊕ (23, 33, 44) | 623/623 | sí |
| AP 0.43–0.52 vs 0.14 (23); 0.52/0.43/0.43 vs 0.138 (81) | 0.5153 / 0.4330 / 0.4264; 0.138039 | sí |
| 521 `unique`, 102 sin pareja o ambiguas (30) | `lineage.csv`: 521; 83 + 19 | sí |
| 237 masas coinciden (30) | `mass_matches_p1` = `true`: 237 | sí |
| 284 radios coinciden (30) | no está en `data/processed/` | no comprobable (ver 3.5) |
| `pl_bmassprov` para 521 filas (31) | `pscomppars_provenance_2026-10-13.csv`: 521 | sí |
| 623 → 623 en `main`, 236 en sensibilidad (32, 53) | `predictions.csv` | sí |
| 0.178000 / 0.178428 R_J; 86 / 537 (33) | `raw`; `labels.csv` | sí |
| 504 grupos, máximo 7 (34) | `grouping_report.json` | sí |
| **4 sobre la relación M-R** (45) | **3 `on_relation`**; 4 `derived` | **no** |
| 4 / 236 / 383 (45) | `mass_provenance.csv` | sí |
| p < 0.001 vs línea base (81, 128) | 0.000133 / 0.000030 / 0.000004 | sí |
| ROC-AUC 0.77–0.80 (81) | 0.7694–0.7970 | sí |
| p = 0.20–0.91 entre modelos (81) | 0.201358 / 0.263822 / 0.905695 | sí |
| LR 68 % / 32 %; RF 35 % / 44 % (83) | 0.6841 / 0.3222; 0.3472 / 0.4353 | sí |
| Accuracy 0.76–0.85 < 0.86 (83) | 0.7575–0.8468; 0.861961 | sí |
| LR ROC-AUC 0.81 / 0.68 (85, 130) | 0.810821 / 0.677464 | sí |
| Sin masa 0.55–0.63; SVM 0.55 → 0.83 (85) | 0.5488–0.6292; 0.5488 → 0.8299 | sí |
| 17 `small` en la sensibilidad (63, 103) | `n_small` 17 | sí |
| ρ = 0.250, df = 24 (62, 88) | 0.250008; 24 | sí |
| 3–4× sobre el azar (128) | 3.09× – 3.73× | sí |
| F1 de `small` 0.38–0.47 (132) | 0.3791–0.4711 | sí |
| F1 = 0.72 original (132) | README de `main`, línea 92: 0.718 | sí |

Un conteo del README contradice `data/processed/`: la línea 45.

## Paso 5 — Hallazgos de `reports/ataque_v1.md`

| Hallazgo | Severidad | ¿Atendido? |
|---|---|---|
| H1: sesgo de detección por tránsito (δ ≈ (Rp/R*)²) | mayor | **Sí.** `README.md:129` explica el mecanismo, lo presenta como hipótesis, dice cómo se podría estimar (`discoverymethod` en las 521 filas emparejadas) y que no se hizo. `README.md:128` deja la tendencia astrofísica y la selección como explicaciones en competencia. Se quitó la afirmación de "known trends" de la versión anterior |
| H2: muestra restringida a planetas con masa, prevalencia artificial | mayor | **Sí.** `README.md:129`: "restricted to planets with a catalogued mass, which shapes which planets are included" (las 623 filas tienen `mass`: 0 NaN). `README.md:29` declara desconocidos los filtros de origen, y el README no repite la cifra 5906 → 623 del red team, que tampoco está probada. Observación: no dice de forma explícita que la prevalencia de 0.138 sea propia de la muestra y no de la población. La frase de `760cc1f` que lo cubría ("the numbers should not be read as properties of the planet population") se quitó en la iteración 2 |
| H3: sobreajuste de RF | menor | Mencionado en `README.md:131` (train AP = 1.0, reproducido) |
| H4: ablación de `star_radius` en el SVM, formalmente anómala | menor | No se menciona. `README.md:49` da los ΔAP correctos, pero no dice que en el SVM el de `star_radius` (+0.0094) queda fuera del rango de las otras tres (−0.0241 a −0.0083) |
| H5: brecha de ROC-AUC 0.81/0.68 | menor | Sí, `README.md:130`, citando H5 |

## Observaciones fuera de los criterios

- Siguen sin cambios las dos observaciones de `aa9a472`: el `df` sobrescrito en la celda `readme-tables` y los 14 avisos con `~/dotfiles/ruff.toml` (el criterio 11 se juzga con el `ruff.toml` del repo).
- `docs/bitacora.md`, última línea: "Horas: X h acumuladas", con un marcador sin llenar.
- Las ejecuciones de este rol reescribieron las 11 salidas con bytes idénticos (`git status` sin cambios en `data/processed/`).

## Qué haría falta para CUMPLE

No es una propuesta de redacción: lo que se escriba es decisión de Mai (T8/T9). Falta:

- **Criterio 9.** Corregir `README.md:45` para que el conteo coincida con `mass_provenance.csv`. Presentar `README.md:160` como hipótesis o alinearlo con `README.md:29-30`. Corregir las filas de autoría de `reports/` (`README.md:156-157`).
- Antes de P2 conviene comprobar el "284 have the same radius" de `README.md:30` contra la descarga del Proyecto 1.
