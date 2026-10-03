# Brief — exp/2026-09-30-auditoria

**Objetivo:** auditar y endurecer `classification.ipynb` para que sus métricas se regeneren con un comando, estén libres de fuga, se evalúen de forma honesta fuera de muestra y queden documentadas en el README, con la autoría declarada, sin agregar funcionalidad.

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
3. Evaluación fuera de muestra: particiones agrupadas por sistema, varianza entre particiones, línea base trivial y selección de modelo que no use los datos con los que se reporta.
4. Reproducibilidad con un solo comando, en un entorno instalado desde `uv.lock`.
5. Un README que diga solo lo que la evidencia sostiene, con una sección de autoría (Mai vs. agente).
6. Pruebas automáticas de los criterios comprobables.

**NO incluye:** modelos nuevos; búsqueda de hiperparámetros para subir métricas; variables nuevas o *feature engineering*; cambiar de clasificador; apps, APIs o despliegue; ampliar el conjunto de datos para entrenar. Si se piden metadatos externos, son solo para auditar y agrupar, nunca para usarlos como variables.

## Criterio de éxito

1. **Reproducible.** Partiendo de un clon limpio, `uv sync --locked` seguido del comando documentado en el README ejecuta el notebook de principio a fin sin errores y escribe el archivo de métricas en la ruta y el esquema fijados en `docs/plan.md`. Dos ejecuciones seguidas producen archivos idénticos byte a byte. *Comprobación:* una prueba de pytest.
2. **Datos crudos inmutables.** El CSV original vive en `data/raw/`, con los bytes sin cambios respecto al commit b316a47 y su SHA-256 registrado. El notebook lee desde ahí. *Comprobación:* una prueba de pytest que compara el checksum.
3. **Linaje documentado.** `docs/decisiones.md` y el README registran la fuente, la consulta o descarga con fecha, cada filtro con su número de filas antes y después, y la regla de etiquetado. Si algún paso no se puede reconstruir, se declara "desconocido" junto con lo que se intentó. *Comprobación:* revisión del Verificador.
4. **Veredicto de fuga por variable.** Para cada una de las cinco variables, el notebook imprime evidencia de separabilidad con esa sola variable y el README da un veredicto (fuga / sin fuga / incierta) con su razón. Si una parte de las masas resulta derivada del radio, se reportan métricas con y sin esas filas, o sin `mass`. *Comprobación:* revisión de la celda y del README; una prueba de que `radius` y cualquier variable vetada no estén en las variables del modelo.
5. **Sin fuga entre particiones.** Ningún sistema planetario aparece a la vez en entrenamiento y evaluación de una misma partición. *Comprobación:* una prueba sobre el archivo de asignación de particiones.
6. **Métricas con incertidumbre.** Para cada modelo y para la línea base trivial, se reportan accuracy, y precisión, *recall* y F1 de `terrestrial`, como media ± desviación sobre validación cruzada estratificada y agrupada. La elección del modelo final no usa los datos con los que se reportan sus métricas. *Comprobación:* una prueba del esquema del archivo de métricas y revisión del método.
7. **El README coincide con la ejecución.** Cada número de la tabla de resultados del README coincide a 3 decimales con el archivo de métricas. *Comprobación:* una prueba de pytest.
8. **Autoría declarada.** El README tiene una sección que asigna a "Mai" o a "agente (modelo, fecha)" cada parte: el notebook por secciones, el README, las pruebas, los datos y los commits b316a47 y 1f2e02f. *Comprobación:* revisión.
9. **Afirmaciones sostenidas.** El README no afirma como hecho nada que la evidencia del criterio 3 no sostenga; por ejemplo, "la etiqueta se generó con un umbral de radio" queda como hecho o como hipótesis según el linaje. *Comprobación:* revisión del Verificador y del red team.
10. **Sin funcionalidad nueva.** El diff contra `main` no agrega modelos, variables ni búsqueda de hiperparámetros. *Comprobación:* revisión del diff.
11. **Calidad.** `uv run pytest -q` pasa y `uvx ruff check .` no reporta nada. *Comprobación:* los dos comandos.

## Restricciones

- **Herramientas:** `uv`, scikit-learn y notebook como artefacto principal, Python 3.14 (`.python-version`). Dependencias nuevas solo con justificación; se espera solo `pytest` como dependencia de desarrollo.
- **Hardware:** la ThinkCentre tiene 8 GB de RAM, así que la ejecución completa debe caber ahí.
- **Nivel técnico:** licenciatura en Ingeniería Física.
- **Rol de las decisiones:** las de dominio (definición de la clase, veredicto de fuga, esquema de evaluación, interpretación) son de Mai.

## Supuestos iniciales

- **S1.** El CSV de 623 filas proviene del Proyecto 1 (`~/proyectos/exoplanet-analysis`), pero el paso que lo filtró y lo etiquetó no está versionado. El `exoplanets_clean.csv` del Proyecto 1 tiene 5906 filas, no tiene etiqueta y da el radio en R⊕. La fuente declarada se contradice: Mai dice Kaggle, y el README del Proyecto 1 (commit 8e7f428) dice NASA TAP `pscomppars`.
- **S2.** Las filas se pueden emparejar con el `exoplanets.csv` del Proyecto 1 (que tiene `pl_name`) comparando sus valores numéricos.
- **S3.** `pscomppars` expone `pl_bmassprov` e imputa masas con una relación masa-radio. Hay que verificarlo contra la documentación actual del archivo.
- **S4.** Mientras no haya nombres de sistema, la tupla (`star_mass`, `star_radius`, `star_teff`) sirve como identificador de sistema. 193 de las 623 filas comparten tupla con otra fila, en 75 grupos.
- **S5.** El gigante gaseoso de menor radio mide 0.17842836725554 R_Jup, que equivale a 2.000 R⊕. La etiqueta parece seguir la regla `radio ≥ 2 R⊕ → gas_giant`. Decidir si se conservan los nombres "terrestrial" y "gas_giant" le toca a Mai.
- **S6.** Con `uv.lock` fijado y semillas fijas, la ejecución es determinista en la misma máquina.
- **S7.** Reportar una línea base trivial (DummyClassifier) es parte de "evaluación honesta" y no cuenta como funcionalidad nueva. Si el Crítico lo objeta, se quita.

## Presupuesto de tiempo de Mai

Más de 12 h, sin fecha límite. La audiencia son revisores de portafolio (veranos de investigación, posgrado o trabajo).
