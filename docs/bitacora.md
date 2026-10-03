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
