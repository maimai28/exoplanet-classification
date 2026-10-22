# Veredicto v3 (re-verificación final) — T11, Verificador (2026-10-22)

**Expediente:** `exp/2026-09-30-auditoria`, iteración 3. **Versión verificada:** commit `9e5bb00` (HEAD), árbol de trabajo limpio.
**Referencia:** criterio de éxito de `docs/brief.md`, con el texto de los criterios 1, 4, 6 y 12 enmendado el 2026-10-18 (el que está hoy en el brief), y el contrato de `docs/plan.md`. No se leyó `docs/decisiones.md`.
**Entorno:** ThinkCentre, Debian 13, uv 0.12.10, ruff 0.16.9, Python 3.14.

> **Numeración.** No existe `reports/veredicto_v2.md`: las dos versiones anteriores están en el historial de `reports/veredicto_v1.md`. En este archivo, **v1** = `aa9a472` (sobre `760cc1f`) y **v2** = `435cd88` (sobre `476b930`). Desde v2 solo cambió `README.md` (`9e5bb00`, T8 iteración 3: 5 líneas). `git diff --stat 760cc1f HEAD -- classification.ipynb src/ tests/ pyproject.toml uv.lock data/ ruff.toml .python-version` sale vacío.

## Veredicto global: **CUMPLE**

Cumplen los 14 criterios. La iteración 3 de T8 corrigió las tres afirmaciones que hacían fallar el criterio 9 en v2 (`README.md:45`, `:156-157` y `:160`) y quitó la cifra no comprobable "284 have the same radius". Los puntos que v1 y v2 marcaron como bloqueantes están todos atendidos (paso 4). Quedan observaciones menores que no bloquean (paso 5).

**Alcance del "cumple" del criterio 3:** cubre la parte del README. La parte de `docs/decisiones.md` no se revisó por instrucción; que cumpla queda a cargo de Mai.

## Paso 1 — Pruebas intactas

```
$ git diff pruebas-1 HEAD -- tests/          → (vacío)
$ git diff --stat pruebas-1 HEAD -- tests/   → (vacío)
```
Se continúa.

## Paso 2 — Ejecuciones

| Comando | Resultado |
|---|---|
| `uv sync --locked` | `Resolved 119 packages`, `Checked 115 packages`, exit 0 |
| Comando del contrato (`README.md:12`), ejecución 1 | exit 0, 35 s |
| Comando del contrato, ejecución 2 | exit 0, 34 s |
| `cmp` de las 11 salidas, ejecución 1 vs 2 | **11/11 idénticas** |
| `git status --short` tras las dos ejecuciones | vacío (las salidas son iguales a las del commit) |
| Clon limpio en el scratchpad (`git clone` → rama → `uv sync --locked` → comando del contrato) | exit 0, 42 s; 11/11 idénticas a la ejecución 1; `git status` vacío en el clon |
| `uv run pytest -q` | `91 passed in 75.40s` |
| `uvx ruff check .` | `All checks passed!` |

SHA-256 (primeros 16 hex), iguales a los de v1 y v2: `labels.csv` 550b546c5eff54fa, `features.json` 2bdfbe5f945a55a8, `folds.csv` b75bd9108162abca, `folds_sensitivity.csv` be8543e5c6a427dc, `predictions.csv` f5a023a0aa747a99, `metrics_by_fold.csv` cbaa187fe5163c39, `metrics.json` 84fb4118ea58839f, `metrics_sensitivity.json` 3280c6aa5961f046, `metrics_by_mass_provenance.json` 3f235f46f6cd9d99, `comparisons.json` 5aa5fd9e3ce09b51, `grouping_report.json` d0dfcbd29f24c0e6.

## Paso 3 — Los 14 criterios

| # | Criterio | Veredicto | Evidencia |
|---|---|---|---|
| 1 | Reproducible | **cumple** | Clon limpio + `uv sync --locked` + comando de `README.md:10-13`: exit 0; dos ejecuciones con 11/11 salidas idénticas byte a byte; `test_reproducibility.py` y `test_format.py` en verde |
| 2 | Datos crudos inmutables | **cumple** | `sha256sum data/raw/exoplanets_clean.csv` = `git show b316a47:exoplanets_clean.csv \| sha256sum` = `data/raw/SHA256SUMS` = `15f10a81…bb966378`; `RAW_CSV = Path("data/raw/exoplanets_clean.csv")` (`classification.ipynb:72`); `test_raw_data.py` en verde |
| 3 | Linaje documentado | **cumple** (parte del README) | `README.md:29-34`: fuente y filtros de origen declarados "not documented", con lo que se intentó (emparejamiento T1 con la descarga del 2026-09-18), consulta T3 del 2026-10-13, filtros del análisis 623 → 623 (sensibilidad 236), regla de etiquetado (ver 3.1) |
| 4 | Veredicto de fuga por variable | **cumple** | Tabla `README.md:42-49`: las cinco variables (más `radius`) con veredicto en las categorías del brief, razón y evidencia; `README.md:45` corregido y comprobado fila por fila (ver 3.2); `test_features.py`, `test_mass_provenance.py` y pruebas de `metrics_by_mass_provenance.json` en verde |
| 5 | Sin fuga entre particiones | **cumple** | `test_folds.py` en verde; recálculo propio: 0 pares (`repeat`, `group_id`) con más de un `fold` en `folds.csv` (3115 filas) y `folds_sensitivity.csv` (1180) |
| 6 | Métricas con incertidumbre | **cumple** | Hiperparámetros iguales a `main` (`classification.ipynb:1036-1043` vs `git show main:classification.ipynb`, líneas 672-684: `class_weight="balanced"`, `max_iter=1000`, `n_estimators=300`, `SVC(kernel="rbf")`); `DummyClassifier(strategy="prior")`; `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=repeat)`; `comparisons.json`: 6 pares, `df` 24, ρ 0.250008; sensibilidad `n_small` 17, `exploratory` true, sin test; pruebas de métricas en verde |
| 7 | README = ejecución | **cumple** | `test_readme.py` en verde; recálculo propio a 3 decimales: tabla principal 4 filas, sensibilidad 4 + 4, comparaciones 6 → **0 discrepancias** |
| 8 | Autoría declarada | **cumple** | `README.md:140-157` asigna el notebook §1–§14, las partes del README, `tests/`, los datos y b316a47/1f2e02f. Las filas de `reports/` ya son correctas (ver 3.4) |
| 9 | Afirmaciones sostenidas | **cumple** | Las tres afirmaciones que fallaban en v2 están corregidas y respaldadas; las ocho de v1 siguen corregidas; las cifras de la prosa coinciden con `data/processed/` (ver 3.5 y paso 3.6) |
| 10 | Sin funcionalidad nueva | **cumple** | Notebook y `src/` sin cambios desde `760cc1f`. En las líneas añadidas de `git diff main HEAD -- classification.ipynb src/ pyproject.toml`, 0 coincidencias de `GridSearch\|RandomizedSearch\|HalvingGrid\|cross_val_score\|BayesSearch\|optuna\|param_grid\|XGB\|LGBM\|GradientBoosting\|KNeighbors\|MLPClassifier`; `pyproject.toml` solo agrega `scipy>=1.18.1` y `pytest>=9.1.1`; las variables de `features.json` son un subconjunto de las de `main` |
| 11 | Calidad | **cumple** | `91 passed`; `All checks passed!` |
| 12 | Pregunta y etiqueta | **cumple** | Pregunta en una frase en negritas (`README.md:23`); definición R ≥ 0.1784 R_J (= 2 R⊕), `small` (86)/`large` (537) y razón del cambio de nombre ("The original names describe composition, which the data do not contain", `README.md:33`); `test_labels.py` en verde; recálculo: R ≥ 2/11.208981 R_J reproduce 623/623 |
| 13 | Particiones agrupadas por sistema | **cumple** | `test_folds.py` y `test_grouping_report.py` en verde; `grouping_report.json`: `n_groups` 504, `max_group_size` 7, `n_groups_multi_hostname` 4 |
| 14 | Emparejamiento uno a uno | **cumple** | `lineage.csv`: 623 filas; `unique` 521, `none` 83, `ambiguous` 19; `test_lineage.py` en verde |

### 3.1 Criterio 3 (revisión manual)

| Elemento del criterio | `README.md` | Revisión |
|---|---|---|
| Fuente | 29: "Its exact source and the filters that produced it are not documented"; 160: "origin undocumented; values partially match … *PSCompPars*" | Declarada desconocida, y ahora de forma coherente en las dos líneas |
| Lo que se intentó | 30: emparejamiento con la descarga *PSCompPars* del 2026-09-18, regla y resultado | 521 `unique` y 102 (83 + 19) coinciden con `lineage.csv`; 237 masas coinciden (`mass_matches_p1` = `true`: 237) |
| Consulta o descarga con fecha | 29: `b316a47` (2026-09-19); 30: descarga del 2026-09-18; 31: consulta `pl_bmassprov` del 2026-10-13 | `pscomppars_provenance_2026-10-13.csv`: 521 filas |
| Filtros con filas antes y después | 29: filtros de origen desconocidos; 32: 623 → 623; sensibilidad 236 | `predictions.csv`: 623 filas por (modelo, repetición) en `main`, 236 en `sens_with_mass` y `sens_without_mass` |
| Regla de etiquetado | 33 | Máximo `terrestrial` 0.178, mínimo `gas_giant` 0.17842836725554; regla 623/623 |

### 3.2 Criterio 4 (revisión manual de la prosa)

Cambió solo la fila de `mass` (`README.md:45`): "4 masses are classed as derived from radius: 3 lie on the Chen & Kipping (2017) mass–radius relation used by the Archive, and 1 is flagged by the Archive as computed from that relation and matches the reference catalog, 236 are measured, 383 cannot be checked against the current catalog."

| Parte de la afirmación | Evidencia | ¿Respaldada? |
|---|---|---|
| 4 `derived` / 236 `measured` / 383 `unverifiable` | `mass_provenance.csv` → `mass_provenance`; `metrics_by_mass_provenance.json` → `n` 4 / 236 / 383 | sí |
| 3 sobre la relación | `mr_status` = `on_relation`: filas 53 (GJ 1132 b), 284 (Kepler-167 d), 424 (Kepler-68 b) | sí |
| Relación de Chen & Kipping (2017) usada por el Archive | `src/t3b_mass_provenance.py:7-9` (documentación del Archive `pscp_calc.html`, que invierte Chen & Kipping 2017, ApJ 834, 17) | sí |
| 1 marcada por el Archive y que coincide con el catálogo de referencia | Fila 460 (K2-133 c): `pl_bmassprov` = `M-R relationship` en `pscomppars_provenance_2026-10-13.csv`, `mass_matches_p1` = `true`, `mr_status` = `not_testable` (`low_precision`, residuo 0.138) → `derived` por la regla del brief | sí |

Las otras filas (`orbital_period`, `star_mass`, `star_teff`, `star_radius`) no cambiaron desde v2, que las dio por buenas; la ablación de `star_radius` (`README.md:49`) la reprodujo v2.

### 3.3 Criterio 6 (revisión del método)

El notebook no cambió desde `760cc1f`. Se comprobó de nuevo: modelos y esquema iguales a los descritos en la tabla; `classes_` y score como en v1 (sin cambios en el código).

### 3.4 Criterio 8 (revisión manual)

| `README.md` | Fila | Revisión |
|---|---|---|
| 156 | `reports/ataque_v1.md` (T10): "agent: Gemini (Antigravity CLI), role Red team, 2026-10-21" | Ya no atribuye nada a T11. Fecha coherente con `760cc1f` (2026-10-21 23:23). El nombre de la herramienta no consta en el archivo ni en el commit (observación de v1, se mantiene; no bloquea) |
| 157 | `reports/veredicto_v1.md` (T11): "agent: Claude Code, role Verifier, claude-opus-5-5, 2026-10-21 and 2026-10-22" | Correcto: `aa9a472` (2026-10-21 23:43) y `435cd88` (2026-10-22 00:48), ambos con trailer `Co-Authored-By: Claude Opus 5.5` |
| 159 | "ChatGPT for brief critique" | Respaldado por `docs/plan.md:79` (T0, Crítico = ChatGPT) |

### 3.5 Criterio 9 (revisión manual de la prosa)

Afirmaciones que fallaban en v2, en HEAD:

| v2 | HEAD | Revisión |
|---|---|---|
| `README.md:45`: "4 masses lie on the … relation" | "4 … derived: 3 lie on the relation, and 1 is flagged by the Archive …" | **Corregida.** Cada parte respaldada (ver 3.2) |
| `README.md:160`: "**Data:** NASA Exoplanet Archive, *PSCompPars* (older release)" | "**Data:** origin undocumented; values partially match the NASA Exoplanet Archive *PSCompPars* table (see Data and lineage)" | **Corregida.** Coherente con `README.md:29-30`; "partially match" corresponde a 521/623 `unique` y 237/521 masas coincidentes |
| `README.md:156-157`: autoría de `reports/` falsa | Ver 3.4 | **Corregida** |
| `README.md:30`: "only 284 have the same radius" (no comprobable, coincidencia sospechosa con los 284 `mass_matches_p1` = `false`) | Quitada; queda "only 237 have the same mass (within 1 %) as that catalog" | **Resuelta** por eliminación; 237 respaldado |

Las ocho afirmaciones de v1 (antes en las líneas 23, 29, 37, 38, 39, 115, 116 y 118) siguen corregidas: `grep -n -i -E 'known trends|radial-velocity follow|older release|turned out' README.md` solo encuentra "Our hypothesis is that the file was built from an older release of the table; this is not proven" (`README.md:30`), que está bien formulada como hipótesis.

Se aplica el mismo estándar que v1 y v2: una cifra o afirmación correcta, presente en un archivo del repo pero sin cita explícita en la línea, es observación y no bloquea (ver paso 5).

### 3.6 Números de la prosa frente a `data/processed/`

Recalculado con scripts de solo lectura sobre las salidas de esta ejecución:

| Afirmación (`README.md`) | Valor en los archivos | ¿Respaldada? |
|---|---|---|
| Tablas entre marcadores (`metrics`, `comparisons`, `sensitivity` ×2) | — | sí, 0 discrepancias |
| 623/623 por la regla R ≥ 2 R⊕ (23, 33, 44) | 623/623 | sí |
| AP 0.43–0.52 vs 0.14 (23); 0.52 ± 0.15 / 0.43 ± 0.11 / 0.43 ± 0.09 vs 0.138 (81) | 0.515262 ± 0.154399 / 0.433021 ± 0.106555 / 0.426369 ± 0.089854; 0.138039 | sí |
| 521 `unique`, 102 sin pareja o ambiguas; 237 masas (30) | `lineage.csv`: 521; 83 + 19; `mass_matches_p1` `true`: 237 | sí |
| `pl_bmassprov` para 521 filas (31) | `pscomppars_provenance_2026-10-13.csv`: 521 | sí |
| 623 en `main`, 236 en sensibilidad (32, 53) | `predictions.csv` | sí |
| 0.178000 / 0.178428 R_J; 86 / 537 (33) | `data/raw/`; `labels.csv` | sí |
| 504 grupos, máximo 7 (34) | `grouping_report.json` | sí |
| 4 `derived` (3 `on_relation` + 1) / 236 / 383 (45) | `mass_provenance.csv` | sí |
| p < 0.001 vs línea base (81, 128) | 0.000133 / 0.000030 / 0.000004 | sí |
| ROC-AUC 0.77–0.80 (81) | 0.769397–0.796999 | sí |
| p = 0.20–0.91 entre modelos (81) | 0.201358 / 0.263822 / 0.905695 | sí |
| LR 68 % / 32 %; RF 35 % / 44 % (83) | 0.684052 / 0.322233; 0.347190 / 0.435340 | sí |
| Accuracy 0.76–0.85 < 0.86 (83) | 0.757460–0.846828; 0.861961 | sí |
| LR ROC-AUC 0.81 / 0.68 (85, 130) | 0.810821 / 0.677464 | sí |
| Sin masa 0.55–0.63; SVM 0.55 → 0.83 (85) | 0.548805–0.629227; 0.548805 → 0.829909 | sí |
| 17 `small` en la sensibilidad (63, 103) | `n_small` 17 | sí |
| ρ = 0.250, df = 24 (62, 88) | 0.250008; 24 | sí |
| 3–4× sobre el azar (128) | 3.09× – 3.73× | sí |
| F1 de `small` 0.38–0.47 (132) | 0.379088–0.471137 | sí |

Ningún número, p-valor ni conteo del README contradice `data/processed/`.

## Paso 4 — Puntos de los veredictos anteriores

### v1 (`aa9a472`)

| Punto | Estado en HEAD |
|---|---|
| Criterio 3 (linaje en el README) | **Atendido** (desde `16df2b4`; ver 3.1) |
| Criterio 4 (veredicto por variable) | **Atendido** (desde `16df2b4`; fila de `mass` corregida en `9e5bb00`, ver 3.2) |
| Criterio 9: ocho afirmaciones (23, 29, 37, 38, 39, 115, 116, 118) | **Atendido** (ver 3.5) |
| H1 (sesgo de detección por tránsito) | **Atendido**: `README.md:128-129`, como hipótesis, con mecanismo y forma de estimarlo |
| H2 (muestra restringida a planetas con masa) | **Atendido**: `README.md:129`; filtros de origen declarados desconocidos en `README.md:29` |
| H4 (ablación de `star_radius` en el SVM) | No se menciona. Menor, no bloquea |
| H5 (brecha 0.81/0.68) | **Atendido**: `README.md:130` |
| Obs.: "pendiente" en la fila de `reports/ataque_v1.md` | **Atendido** (`README.md:156`) |
| Obs.: "Gemini (Antigravity CLI)" sin registro | Sigue sin registro en el repo. No bloquea |
| Obs.: celdas en español en un README en inglés | Sigue: "agente", "rol", "con asistencia de", "texto editado y aprobado por Mai" (`README.md:143-155`). No bloquea |
| Obs.: `df` sobrescrito en la celda `readme-tables` | Sigue (`classification.ipynb:1512`). No afecta salidas |
| Obs.: 14 avisos con `~/dotfiles/ruff.toml` | Siguen (12 B905, 2 SIM300). El criterio 11 se juzga con el `ruff.toml` del repo |

### v2 (`435cd88`)

| Punto | Estado en HEAD |
|---|---|
| Criterio 9: `README.md:45` (4 sobre la relación vs 3 `on_relation`) | **Atendido** (ver 3.2) |
| Criterio 9: `README.md:160` (fuente dada como hecho) | **Atendido** (ver 3.5) |
| Criterio 9: `README.md:156-157` (autoría de `reports/`) | **Atendido** (ver 3.4) |
| "284 have the same radius" por comprobar | **Resuelto**: la cifra se quitó del README |
| Fila de T8 (`README.md:154`) sin la iteración 2 | **No atendido**, y ahora faltan las iteraciones 2 (`16df2b4`) y 3 (`9e5bb00`), ambas del 2026-10-22. La fila sigue citando solo `f2cc43a` (2026-10-21). No bloquea: la parte está asignada a Mai, como pide el criterio 8 |
| H2: no dice que la prevalencia 0.138 es propia de la muestra | Sigue sin decirse de forma explícita (`grep -i population README.md` sin resultados). No bloquea |
| "univariate ROC-AUC 0.78 → 0.58" impreciso (`README.md:130`) | Sin cambios. Dentro de lo que cita H5. No bloquea |
| Cifras correctas sin archivo citado (33, 34, 85, 130, 131) | Sin cambios. No bloquea (mismo estándar) |
| `docs/bitacora.md`: "Horas: X h acumuladas" | Sigue sin llenar |

## Paso 5 — Observaciones que no cambian el veredicto

- **Autoría de reports sin evidencia en la columna.** `README.md:156-157` dicen "—" en la columna de evidencia, aunque los commits existen (`760cc1f`; `aa9a472`, `435cd88`). El README tampoco lista este `reports/veredicto_v3.md`; tras este commit, la tabla de autoría quedará incompleta respecto a `reports/`, que no está en la lista del criterio 8.
- **Filas `on_relation` con `pl_bmassprov` = `Mass`.** Dos de las tres masas "on the relation" (`README.md:45`) son GJ 1132 b (fila 53) y Kepler-68 b (fila 424), que la bitácora (2026-10-13) registra como posibles falsos `derived`. La afirmación es correcta para T3b y no afecta el resultado (`mass` queda fuera del modelo principal y la sensibilidad usa solo `measured`), pero el README no menciona la salvedad.
- **Bitácora.** `docs/bitacora.md` no registra la iteración 3 de T8 (`9e5bb00`), y la última línea sigue con "X h".
- **No comprobables con las fuentes de este rol:** "6,366 rows", la lista de columnas y la regla de emparejamiento de `README.md:30` (descarga del Proyecto 1, fuera del repo, y `docs/decisiones.md`), y "@maimai28" (`README.md:159`). Citan la descarga con su fecha, que es lo que pide el criterio 9.
- Las ejecuciones de este rol reescribieron las 11 salidas con bytes idénticos (`git status` vacío).

## Qué queda para Mai antes de P3

Nada bloquea el criterio de éxito. Opcional, a decisión de Mai (no es propuesta de redacción): completar la fila de T8 con las iteraciones 2 y 3, citar los commits en las filas de `reports/` y añadir este veredicto, y cerrar la bitácora (iteración 3 y horas). La parte de `docs/decisiones.md` del criterio 3 queda a revisión de Mai.
