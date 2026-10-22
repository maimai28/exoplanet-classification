# Bitácora

## 2026-09-30 — Arquitecto/Planificador — exp/2026-09-30-auditoria
- Triaje: 1+0+1+1+2 = 5 → N2. Mai decide N3 (aprobado en sesión). CLAUDE.md ya decía N3.
- Audiencia: cambia de "entrevista" a "revisores de portafolio (veranos de investigación, posgrado, trabajo)". Sin fecha; presupuesto >12 h.
- Fuente del CSV: Mai indica Kaggle vía Proyecto 1; README del Proyecto 1 (commit 8e7f428) indica NASA TAP pscomppars. El exoplanets_clean.csv de este repo (623 filas, con etiqueta) no coincide con el del Proyecto 1 (5906 filas, sin etiqueta). Discrepancia abierta → T1.
- Escritos: docs/brief.md, docs/plan.md. Pendiente: Crítico del brief y P1.

## 2026-10-02 — P1 aprobado con cambios por Mai
Aprobados los 4 puntos: CSV a data/raw/ con SHA-256, consulta T3 al NASA Exoplanet Archive, contrato de salidas, brief. Cambios aprobados por Mai (regla 6):
1. Objetivo: "libres de fuga" → "con un veredicto de fuga documentado por variable".
2. Criterio 4: veredicto por procedencia (fuga = derivado del radio o de la etiqueta; sin fuga = medido de forma independiente; incierta = procedencia no establecida). La separabilidad es solo evidencia. Masas medidas y derivadas se reportan por separado.
3. Criterio 6: se evalúan Logistic Regression, Random Forest, SVM (RBF) y la línea base; sin modelo final.
4. Criterio 13 (nuevo): particiones agrupadas por hostname (T3); tupla estelar solo de respaldo, con conteo de colisiones; pytest.
5. Criterio 14 (nuevo): emparejamiento uno a uno con el CSV de 5906 filas; filas sin pareja o ambiguas reportadas; pytest.
6. Restricción: jupyter/nbconvert fijados en uv.lock; pytest como dependencia de desarrollo.
7. Criterio 1: byte a byte solo en las salidas JSON/CSV (llaves ordenadas, 6 decimales), no en el notebook.
8. Criterio 9: cada afirmación factual del README cita evidencia (archivo, commit o consulta con fecha).
9. Criterio 12 (nuevo, [TÚ]): pregunta del modelo, definición de la etiqueta y nombres de clase; tarea T4b, después del linaje.
10. Presupuesto: 12 h; aviso al 50 % (6 h); revisión obligatoria si se superan 18 h.
- Pendiente: confirmación de P1 con el diff.

## 2026-10-02 — P1 aprobado en definitiva por Mai
- Mai aprueba brief y plan con el diff presentado, incluidos los tres puntos que propuso el Arquitecto: 6 decimales fijos; esquemas de metrics_by_mass_provenance.json y grouping_report.json; tarea T4b (criterio 12) antes de T5.
- Siguiente: T1 (Especialista, linaje).
- 2026-10-02 — T0 cerrada. Horas de Mai acumuladas: 6h
- 2026-10-02 — Decisiones de Mai sobre T1:
  - Fuente exacta: desconocida; consistente con versión anterior de NASA pscomppars (posiblemente vía Kaggle). No se busca el archivo de Kaggle.
  - Regla radio >= 2 R⊕: reproduce las 623 etiquetas; se decide en T4b y se reporta como hipótesis sostenida.
  - Filas sin pl_name (102) y ambiguas: se agrupan por tupla estelar (criterio 13); se reporta el conteo.
  - Empates: se acepta la regla sin desempate manual; las 14 filas sensibles a la tolerancia se marcan como frágiles.
- 2026-10-02 — Aviso de presupuesto al 50 % (6 h de 12). Faltan T4, T4b, T5, T8 (estimado 5-6 h). Se mantiene el presupuesto; revisión si se superan 9 h al cerrar T5.
- 2026-10-13 — Decisiones de Mai sobre T3:
  - pl_bmassprov solo vale en filas cuya masa coincide (±1 %) con pl_bmassj de la descarga del Proyecto 1 (2026-09-18, SHA-256 e5570cba…); en las demás la procedencia es "no verificable". No se autoriza una consulta nueva.
  - Se agrega T3b [AGENTE]: probar si las masas del CSV caen exactamente sobre la relación masa-radio del catálogo (evidencia directa de masa derivada), para todas las filas. Pendiente de definirla en el plan.
  - Criterio 13 cambia (regla 6): group_id = componente conexa de filas que comparten hostname O tupla estelar; ningún sistema puede quedar partido entre particiones. Pendiente de pasarlo al brief y al plan.
  - Filas frágiles: 12 (no 14); documentadas en decisiones.md, sin cambiar el contrato de lineage.csv.
  - Se acepta y registra la petición vacía extra a TAP/sync reportada por el agente; no se repite.

## 2026-10-13 — Arquitecto/Planificador — decisiones de T3 pasadas al brief y al plan
- Criterio 13: `group_id` = componente conexa (`hostname` O tupla exacta), formato `g:<row_id mínimo>`; la prueba exige igualdad con las componentes. `grouping_report.json` cambia de llaves (se quitan `n_by_hostname` y `n_by_tuple`).
- Criterio 4: la masa de cada fila se clasifica como `measured`, `derived` o `unverifiable`. "No verificable" se aplica donde la masa no coincide a ±1 % con el Proyecto 1. `on_relation` de T3b manda; `off_relation` no basta para `measured`. El veredicto de `mass` sigue siendo de Mai (T4).
- Nueva salida en el contrato: `data/processed/mass_provenance.csv`. Nueva tarea T3b (Especialista, [AGENTE]), sin consulta TAP nueva.
- Orden: T3 → T3b → T4, T4b, T5.
- Pendiente: aprobación de Mai del diff (regla 6). T6 no empieza hasta entonces.

## 2026-10-13 — Mai aprueba el diff de T3 con ajustes (regla 6)
- (a) Se aprueba la regla de combinación. T3b además reporta cuántas filas con `pl_bmassprov` = `Mass` quedan `on_relation`, como diagnóstico de la tolerancia.
- (b) Se aprueban el formato `g:<row_id mínimo>` y las llaves nuevas de `grouping_report.json`.
- (c) T3b puede leer, solo como lectura, la documentación web del NASA Exoplanet Archive y la literatura que cite. Quedan prohibidas las consultas TAP, la descarga de tablas y la instalación de dependencias. La relación M-R se implementa con los coeficientes publicados, y cada fuente se registra en `docs/decisiones.md` con su URL o DOI y la fecha de acceso.
- Brief y plan actualizados. T6 ya puede empezar. Siguiente: T3b (Especialista).

## 2026-10-13 — Arquitecto/Planificador — cambio del criterio 4 tras T3b (regla 6)
- Mai cambia el criterio 4 tras ver el resultado de T3b (commit 43a9b14): si la tolerancia relativa por fila supera 0.10 (±10 % en masa) y la fila daría `on_relation`, `mr_status` = `not_testable` con motivo `low_precision`. Las `off_relation` se quedan así sin importar la tolerancia: una tolerancia amplia solo debilita una coincidencia, no una discrepancia (corrección de Mai al primer diff). El tramo 11.1 ≤ Rp < 14.3 R⊕ queda con motivo `gap_11.1_14.3`, que manda si aplican los dos (aprobado por Mai).
- Contrato: `mr_predicted_mass` y `mr_rel_residual` quedan vacíos solo con `gap_11.1_14.3`; con `low_precision` se conservan como diagnóstico.
- El umbral se fijó después de ver los resultados de T3b; se registra así en el brief y en `docs/decisiones.md`.
- La regla de combinación `derived`/`measured`/`unverifiable` no cambia.
- Contrato: nueva columna `not_testable_reason` en `mass_provenance.csv`.
- T3b se re-ejecuta con el criterio nuevo. El Especialista registra en `docs/decisiones.md` el cambio, el umbral, la justificación de aplicarlo solo a coincidencias, que se fijó a posteriori, y GJ 1132 b (fila 53) y Kepler-68 b (fila 424) como posibles falsos `derived`. T4 espera a la re-ejecución.
- Pendiente: aprobación de Mai del diff.

## 2026-10-13 — Mai aprueba el diff del cambio al criterio 4 (regla 6)
- Brief y plan actualizados. Siguiente: re-ejecución de T3b (Especialista), que incluye la sección en `docs/decisiones.md`. T4 espera a esa re-ejecución.
- 2026-10-18 · T4 [TÚ] · fuga: radius excluido, mass → sensibilidad (236 measured); modelo principal con 4 variables. Horas: 8 h acumuladas.
- 2026-10-18 · T4b [TÚ] · pregunta fijada; clases renombradas small/large (umbral 2 R⊕), positiva = small. Horas: 8 h acumuladas.
- 2026-10-18 · T5 [TÚ] · CV anidada 5×5 por grupos, AP de small como métrica principal, Nadeau-Bengio para comparar. Horas: 9 h acumuladas.

## 2026-10-18 — Arquitecto/Planificador — regla 6: T4, T4b y T5 al brief y al plan
- Contradicciones encontradas antes de editar y resueltas por Mai:
  1. La CV interior de T5 chocaba con el criterio 10 y con "NO incluye" (búsqueda de hiperparámetros). Se quita: CV exterior 5×5 sin anidar, con los hiperparámetros exactos del notebook de `main`, `class_weight="balanced"` incluido. El criterio 10 no cambia y no hay rejillas.
  2. El criterio 6 (P/R/F1 de `terrestrial`) chocaba con T4b/T5. Quedan siete métricas: `average_precision_small` (principal), `balanced_accuracy`, `roc_auc`, `precision_small`, `recall_small`, `f1_small` y `accuracy` (contexto). P/R/F1 usan el umbral de `predict()` (`decision_function` > 0 en el SVM).
  3. T4 fijaba `target` = `planet_type`, y T4b, `size_class` con positiva `small`. Queda `target` = `size_class`.
  4. El Implementador no escribe en `reports/`. Las métricas van en `data/processed/`; `reports/` queda para T6, T10 y T11.
- Enmiendas registradas en `docs/decisiones.md` ("Enmiendas por regla 6 (2026-10-18)"), con autorización de Mai para agregar solo esa sección.
- Brief: los criterios 1 (lista byte a byte), 4 (veredictos de T4, prueba de `radius` sobre `main`/`sensitivity_mass`/`excluded`, prueba de filas `measured`), 6 (reescrito) y 12 (decidido en T4b; prueba del mapeo de `labels.csv`); S5 y S7.
- Plan: contrato nuevo (`labels.csv`, `features.json` de cuatro llaves, modelos, `folds.csv` con `repeat`, `folds_sensitivity.csv`, `predictions.csv`, `metrics_by_fold.csv`, `metrics.json` de 4 × 7, `metrics_sensitivity.json`, `comparisons.json`, método de `metrics_by_mass_provenance.json`, marcadores del README, `reports/`, formato determinista). T6 a T11 ajustadas; T10 incluye el ataque sobre `star_radius`.
- Pendiente: aprobación de Mai del diff. T6 no empieza hasta entonces.

## 2026-10-18 — Mai aprueba el diff de T4, T4b y T5 (regla 6)
- Se aprueban los 14 puntos de decisión. Ajuste al punto 14: T7 declara `scipy` explícitamente en `pyproject.toml`; el brief (Restricciones) lo admite junto a `pytest`.
- Se corrige la RAM de la ThinkCentre en el brief (Restricciones): 23 GB útiles, no 8 GB.
- Siguiente: T6 (Tester, fase A).
- 2026-10-22 · T8 iteración 2 (por veredicto_v1: criterios 3, 4, 9; H1/H2). Horas: X h acumuladas.
