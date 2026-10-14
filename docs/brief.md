# Brief — exp/2026-09-30-auditoria

**Objetivo:** auditar y endurecer `classification.ipynb` para que sus métricas se regeneren con un comando, tengan un veredicto de fuga documentado por variable, se evalúen de forma honesta fuera de muestra y queden documentadas en el README, con la autoría declarada, sin agregar funcionalidad.

**Módulo:** M2   **Nivel:** N3 (cálculo: 1+0+1+1+2 = 5 → N2; subido a N3 por decisión de Mai el 2026-09-30, registrada en `docs/bitacora.md`)   **Modo:** Guiado

| Pregunta del triaje | Valor | Razón |
|---|---|---|
| Costo del error | 1 | Afecta la credibilidad ante revisores; no hay dinero ni seguridad de por medio |
| Reversibilidad | 0 | Repo local bajo git; nada se publica sin P3 |
| Tamaño | 1 | Un notebook, el README, pruebas y la reorganización de datos |
| Novedad | 1 | Validación agrupada y procedencia de la masa, nuevas en este proyecto |
| Verificabilidad | 2 | "Sin fuga" no se demuestra solo con pruebas; depende del linaje y el juicio |

## Alcance

**Incluye:**
1. Linaje de `exoplanets_clean.csv`: fuente, consulta o descarga, filtrado hasta 623 filas, conversión de unidades y regla que generó `planet_type`.
2. Auditoría de fuga de las cinco variables que quedan (`mass`, `orbital_period`, `star_mass`, `star_radius`, `star_teff`), incluida la procedencia de la masa (medida vs. derivada del radio).
3. Evaluación fuera de muestra: particiones agrupadas por sistema, varianza entre particiones, línea base trivial; se reportan todos los modelos existentes sin elegir un modelo final.
4. Reproducibilidad con un solo comando, en un entorno instalado desde `uv.lock`.
5. Un README que diga solo lo que la evidencia sostiene, con una sección de autoría (Mai vs. agente).
6. Pruebas automáticas de los criterios comprobables.

**NO incluye:** modelos nuevos; búsqueda de hiperparámetros para subir métricas; variables nuevas o *feature engineering*; cambiar de clasificador; apps, APIs o despliegue; ampliar el conjunto de datos para entrenar. Si se piden metadatos externos, son solo para auditar y agrupar, nunca para usarlos como variables.

## Criterio de éxito

1. **Reproducible.** Partiendo de un clon limpio, `uv sync --locked` seguido del comando documentado en el README ejecuta el notebook de principio a fin sin errores y escribe las salidas en las rutas y esquemas fijados en `docs/plan.md`. Dos ejecuciones seguidas producen `metrics.json`, `metrics_by_mass_provenance.json`, `folds.csv` y `features.json` idénticos byte a byte (llaves ordenadas, 6 decimales fijos). El criterio no aplica al notebook ejecutado. *Comprobación:* una prueba de pytest.
2. **Datos crudos inmutables.** El CSV original vive en `data/raw/`, con los bytes sin cambios respecto al commit b316a47 y su SHA-256 registrado. El notebook lee desde ahí. *Comprobación:* una prueba de pytest que compara el checksum.
3. **Linaje documentado.** `docs/decisiones.md` y el README registran la fuente, la consulta o descarga con fecha, cada filtro con su número de filas antes y después, y la regla de etiquetado. Si algún paso no se puede reconstruir, se declara "desconocido" junto con lo que se intentó. *Comprobación:* revisión del Verificador.
4. **Veredicto de fuga por variable, decidido por procedencia.** El README da un veredicto para cada una de las cinco variables, con su razón y la evidencia de procedencia:
   - **Fuga:** el valor se derivó del radio o de la etiqueta; por ejemplo, una masa cuya `pl_bmassprov` indica relación masa-radio.
   - **Sin fuga:** se midió de forma independiente.
   - **Incierta:** la procedencia no está establecida.

   **Procedencia de la masa por fila.** Cada fila recibe una categoría `mass_provenance` en `mass_provenance.csv` (T3b), combinando tres evidencias: si la `mass` del CSV coincide a ±1 % con `pl_bmassj` de la descarga del Proyecto 1 (2026-09-18, SHA-256 e5570cba…), la `pl_bmassprov` de T3 y el resultado `mr_status` de T3b. La etiqueta `pl_bmassprov` solo vale en las filas que coinciden; en las demás la procedencia es "no verificable" (decisión de Mai, 2026-10-13).
   - **`derived`:** T3b da `on_relation`, sea cual sea `pl_bmassprov`; o la masa coincide con el Proyecto 1 y `pl_bmassprov` = `M-R relationship`.
   - **`measured`:** la masa coincide con el Proyecto 1, `pl_bmassprov` ∈ {`Mass`, `Msini`} y T3b no da `on_relation`.
   - **`unverifiable`:** todas las demás. Son las filas cuya masa no coincide con el Proyecto 1 y las filas sin `pl_name`, siempre que T3b no dé `on_relation`.

   Regla de combinación: la evidencia directa de T3b (`on_relation`) manda sobre la etiqueta. `off_relation` o `not_testable` no bastan para que una fila sea `measured`, porque no caer sobre la relación no prueba que la masa se haya medido. Si T3b no logra establecer la relación, todas sus filas quedan `not_testable` y la clasificación depende solo de la coincidencia y de `pl_bmassprov`. El veredicto de la variable `mass` lo decide Mai en T4 a partir de los conteos por categoría.

   El notebook imprime la separabilidad con una sola variable como evidencia; ese número no decide el veredicto. Las masas medidas y las derivadas se reportan por separado: conteo por categoría y métricas por subconjunto en `metrics_by_mass_provenance.json`, con exactamente las llaves `measured`, `derived` y `unverifiable`. *Comprobación:* revisión del README; una prueba de que `radius` y cualquier variable vetada no estén en `features.json`; una prueba de que `metrics_by_mass_provenance.json` tenga exactamente esas tres llaves y de que cada `n` sea igual al conteo de esa categoría en `mass_provenance.csv`.
5. **Sin fuga entre particiones.** Ningún sistema planetario aparece a la vez en entrenamiento y evaluación de una misma partición. *Comprobación:* una prueba sobre el archivo de asignación de particiones.
6. **Métricas con incertidumbre, para todos los modelos.** Se evalúan los tres modelos que ya existen en el notebook ("Logistic Regression", "Random Forest", "SVM (RBF)") y la línea base trivial. De cada uno se reportan accuracy, y precisión, *recall* y F1 de `terrestrial`, como media ± desviación sobre validación cruzada estratificada y agrupada. No se elige un modelo final. *Comprobación:* una prueba de que `metrics.json` tiene exactamente esos cuatro modelos y las cuatro métricas, más revisión del método.
7. **El README coincide con la ejecución.** Cada número de la tabla de resultados del README coincide a 3 decimales con el archivo de métricas. *Comprobación:* una prueba de pytest.
8. **Autoría declarada.** El README tiene una sección que asigna a "Mai" o a "agente (modelo, fecha)" cada parte: el notebook por secciones, el README, las pruebas, los datos y los commits b316a47 y 1f2e02f. *Comprobación:* revisión.
9. **Afirmaciones sostenidas.** Cada afirmación factual del README cita su evidencia: un archivo, un commit o una consulta con fecha. Lo que no tenga evidencia se presenta como hipótesis; por ejemplo, "la etiqueta se generó con un umbral de radio" queda como hecho o como hipótesis según el linaje. *Comprobación:* revisión del Verificador y del red team.
10. **Sin funcionalidad nueva.** El diff contra `main` no agrega modelos, variables ni búsqueda de hiperparámetros. *Comprobación:* revisión del diff.
11. **Calidad.** `uv run pytest -q` pasa y `uvx ruff check .` no reporta nada. *Comprobación:* los dos comandos.
12. **Pregunta y etiqueta declaradas [TÚ].** El README declara en una frase la pregunta que responde el modelo, la definición exacta de la etiqueta y por qué se conservan o se cambian los nombres de las clases. Lo decide Mai cuando el linaje esté terminado. *Comprobación:* revisión.
13. **Particiones agrupadas por sistema.** `group_id` es la componente conexa del grafo cuyos nodos son las 623 filas. Dos filas quedan unidas si comparten un `hostname` no vacío (de `lineage.csv`, obtenido en T3) o si comparten la tupla exacta (`star_mass`, `star_radius`, `star_teff`) tal como aparece en `data/raw/exoplanets_clean.csv`. El `group_id` se escribe como `g:<row_id mínimo de la componente>`. Ningún sistema puede quedar partido entre particiones. `grouping_report.json` reporta el tamaño y la composición de las componentes y las colisiones entre `hostname` y tupla (llaves en `docs/plan.md`). *Comprobación:* una prueba de pytest que reconstruye las componentes desde `lineage.csv` y `data/raw/exoplanets_clean.csv`. Exige que la partición inducida por `group_id` en `folds.csv` sea igual a esas componentes, ni más gruesa ni más fina, y que los `group_id` tengan el formato fijado. Una segunda prueba revisa que el reporte tenga las llaves del contrato y sea consistente con `folds.csv`.
14. **Emparejamiento uno a uno.** El emparejamiento de las 623 filas con el `exoplanets.csv` del Proyecto 1 es uno a uno. Cada `row_id` aparece una sola vez en `lineage.csv`, con `match_status` ∈ {`unique`, `none`, `ambiguous`}; ningún `pl_name` se repite entre las filas `unique`; las filas sin pareja o ambiguas se listan y se cuentan. *Comprobación:* una prueba de pytest.

## Restricciones

- **Herramientas:** `uv`, scikit-learn y notebook como artefacto principal, Python 3.14 (`.python-version`). Las dependencias necesarias para ejecutar el notebook (`jupyter`, `nbconvert`) deben estar fijadas en `uv.lock`; hoy ya lo están. Cualquier dependencia nueva requiere justificación; la única que se espera es `pytest`, como dependencia de desarrollo.
- **Hardware:** la ThinkCentre tiene 8 GB de RAM, así que la ejecución completa debe caber ahí.
- **Nivel técnico:** licenciatura en Ingeniería Física.
- **Rol de las decisiones:** las de dominio (definición de la clase, veredicto de fuga, esquema de evaluación, interpretación) son de Mai.

## Supuestos iniciales

- **S1.** El CSV de 623 filas proviene del Proyecto 1 (`~/proyectos/exoplanet-analysis`), pero el paso que lo filtró y lo etiquetó no está versionado. El `exoplanets_clean.csv` del Proyecto 1 tiene 5906 filas, no tiene etiqueta y da el radio en R⊕. La fuente declarada se contradice: Mai dice Kaggle, y el README del Proyecto 1 (commit 8e7f428) dice NASA TAP `pscomppars`.
- **S2.** Las filas se pueden emparejar con el `exoplanets.csv` del Proyecto 1 (que tiene `pl_name`) comparando sus valores numéricos.
- **S3.** `pscomppars` expone `pl_bmassprov` (confirmado en T3) e imputa masas con una relación masa-radio. T3b documenta qué relación es y de qué fuente sale, o declara que no se pudo establecer.
- **S4.** Un sistema puede aparecer con `hostname` o solo con su tupla estelar. Por eso el grupo es la unión de ambos criterios (criterio 13). Un cálculo de solo lectura del Arquitecto (2026-10-13) da 504 componentes; la mayor tiene 7 filas y 4 de ellas juntan más de un `hostname`. T7 da las cifras oficiales en `grouping_report.json`.
- **S5.** El gigante gaseoso de menor radio mide 0.17842836725554 R_Jup, que equivale a 2.000 R⊕. La etiqueta parece seguir la regla `radio ≥ 2 R⊕ → gas_giant`. Decidir si se conservan los nombres "terrestrial" y "gas_giant" le toca a Mai.
- **S6.** Con `uv.lock` fijado y semillas fijas, la ejecución es determinista en la misma máquina.
- **S7.** Reportar una línea base trivial (DummyClassifier) es parte de "evaluación honesta" y no cuenta como funcionalidad nueva. Si el Crítico lo objeta, se quita.

## Presupuesto de tiempo de Mai

12 h, sin fecha límite. Aviso al 50 % (6 h). Si se superan 18 h, revisión obligatoria antes de continuar. La audiencia son revisores de portafolio (veranos de investigación, posgrado o trabajo).
