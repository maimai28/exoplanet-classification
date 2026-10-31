# Reporte de ataque v1 — Red team (M2 Datos)

**Expediente:** `exp/2026-09-30-auditoria`  
**Referencia:** `docs/brief.md`, `tests/`, `reports/pruebas_v1.md`, salidas de T7 en `data/processed/`, diff contra `main`.  
**Entorno de ejecución:** Worktree aislado `/tmp/redteam` sobre commit HEAD (580aace).

---

## Ataques obligatorios

Ataques obligatorios: 1 → sin hallazgos críticos; preprocesamiento aislado por fold, particiones sin fuga inter-sistema y permutación de `radius` produce predicciones idénticas byte a byte; 2 → hallazgo mayor (H1); la relación entre parámetros estelares y tamaño planetario está severamente confundida por el sesgo observacional de detección de tránsitos de Kepler; 3 → hallazgo mayor (H2); selección de casos completos con masa genera fuerte sesgo de supervivencia y prevalencia artificial (13.8 % de `small`); 4 → hallazgo menor (H3); sobreajuste severo en Random Forest (Train AP = 1.0000 vs Test AP = 0.4330), aunque sin violar el brief; 5 → sin hallazgos que invaliden; la conclusión principal sobrevive de forma robusta a la exclusión de filas frágiles/derivadas (LR AP = 0.500, RF AP = 0.407, SVM AP = 0.401 vs baseline 0.133, p < 0.0003) y a la exclusión de periodos extremos.

---

## Ataques extra

- **Ataque (a) — Ablación de `star_radius`:**  
  Se comparó la corrida `main` contra la ablación de cada una de las 4 variables con los mismos folds (`folds.csv`) y semillas (25 evaluaciones).  
  - Logistic Regression: ΔAP = +0.0072 (t = +0.556, p = 0.5832). Rango otras tres: [+0.0065, +0.0266]. Dentro del rango (no anómala).  
  - Random Forest: ΔAP = +0.0186 (t = +0.526, p = 0.6039). Rango otras tres: [-0.0440, +0.0675]. Dentro del rango (no anómala).  
  - SVM (RBF): ΔAP = +0.0094 (t = +0.371, p = 0.7137). Rango otras tres: [-0.0241, -0.0083]. Fuera del rango (H4, anómala por definición de rango, aunque el efecto es < 0.01 y p = 0.714 no es significativo).  
  *Conclusión:* La exclusión de `star_radius` no degrada de forma estadísticamente significativa el desempeño de ningún modelo (p > 0.58).

- **Ataque (b) — Permutación de `radius`:**  
  Se permutó aleatoriamente la columna `radius` en una copia de `data/raw/exoplanets_clean.csv` y se reejecutó `classification.ipynb` de principio a fin.  
  *Resultado:* `data/processed/predictions.csv` resultante es 100 % idéntico byte a byte con respecto al original. Sin fuga de `radius`.

- **Ataque (c) — Sensibilidad sin 12 filas frágiles ni 4 derived:**  
  Se reejecutó la corrida `main` excluyendo las 12 filas frágiles de T3 (50, 74, 122, 183, 265, 308, 344, 398, 439, 524, 545, 612) y las 4 `derived` (53, 284, 424, 460), quedando 607 filas (81 `small`, 526 `large`).  
  - Folds filtrados: Logistic Regression AP = 0.4996 ± 0.1580; Random Forest AP = 0.4074 ± 0.1008; SVM (RBF) AP = 0.4007 ± 0.0769; Baseline (prior) AP = 0.1334 ± 0.0057.  
  - Nadeau-Bengio vs Baseline: LR diff = +0.3661 (p = 0.000253); RF diff = +0.2740 (p = 0.000048); SVM diff = +0.2673 (p = 0.000001).  
  - Comparaciones entre modelos: LR vs RF p = 0.2096; LR vs SVM p = 0.1815; RF vs SVM p = 0.8971.  
  - Folds re-estratificados desde cero: LR AP = 0.4870; RF AP = 0.3844; SVM AP = 0.4138.  
  *Conclusión:* Las conclusiones del estudio se mantienen intactas: todos los modelos superan ampliamente a la línea base y las diferencias entre ellos no son significativas.

- **Ataque extra — Brecha ROC-AUC de LR (0.68 en `measured` vs 0.81 en `unverifiable`):**  
  Se atacó la explicación del README ("efecto de muestra, no fuga"). Se analizaron las distribuciones univariadas estratificadas por clase entre ambas submuestras (H5).  
  *Resultado:* En `unverifiable` (n = 383, 66 `small`), los planetas pequeños están fuertemente concentrados en enanas frías y de bajo radio (`star_radius` mediana 0.66 vs 1.11 en `large`; `star_teff` mediana 4809 K vs 5793 K; `star_mass` mediana 0.71 vs 1.05; ROC-AUC univariada respecto a clase: 0.77–0.80). En `measured` (n = 236, 17 `small`), los planetas pequeños fueron seguidos por RV alrededor de estrellas similares al Sol (`star_radius` mediana 1.03 vs 1.10 en `large`; `star_teff` mediana 5680 K vs 5738 K; `star_mass` mediana 0.95 vs 1.07; ROC-AUC univariada respecto a clase: 0.58). La caída de ROC-AUC de 0.81 a 0.68 se explica porque la separabilidad en el espacio de parámetros estelares colapsa en la submuestra medida debido a la ausencia de enanas M/K en ese subconjunto.

---

## Hallazgos

### H1 — mayor — Variable confusora: sesgo de detección instrumental confunde parámetros estelares con tamaño de planeta
- **Descripción:** La aparente predictibilidad de la clase de tamaño a partir de los parámetros del huésped está fuertemente mediada por la probabilidad de detección de tránsitos de Kepler (la profundidad $\delta \approx (R_p / R_*)^2$ hace que los planetas pequeños solo sean detectables fotométricamente en estrellas pequeñas y frías). El modelo aprende este sesgo instrumental más que una relación astrofísica intrínseca.
- **Evidencia:**  
  - Entrada: Distribuciones de `star_radius` y `star_teff` condicionales a `size_class` en `data/raw/exoplanets_clean.csv`.
  - Comando: `uv run python -c "import pandas as pd; df = pd.read_csv('data/raw/exoplanets_clean.csv'); lab = pd.read_csv('data/processed/labels.csv'); df['sc'] = lab['size_class']; print(df.groupby('sc')[['star_radius', 'star_teff', 'star_mass']].median())"`
  - Salida:
    ```
           star_radius  star_teff  star_mass
    sc                                      
    large        1.104     5779.0       1.06
    small        0.730     4941.0       0.77
    ```
- **Criterio afectado:** Criterio 9 (afirmaciones sostenidas en README sobre consistencia con tendencias astrofísicas).
- **Etapa probable de origen:** Formulación inicial del problema / selección de variables (T0/T4).

### H2 — mayor — Sesgo de origen: filtrado por casos completos en masa genera distorsión poblacional severa
- **Descripción:** Requerir masa y radio completos redujo el catálogo de 5906 a 623 filas, sobrerrepresentando planetas masivos y gigantes gaseosos (86.2 % `large` vs 13.8 % `small`), lo cual distorsiona la prevalencia real de la galaxia donde los planetas pequeños son dominantes.
- **Evidencia:**  
  - Entrada: `data/raw/exoplanets_clean.csv` frente a las 5906 filas del catálogo general del Proyecto 1.
  - Comando: `uv run python -c "import pandas as pd; lab = pd.read_csv('data/processed/labels.csv'); print(lab['size_class'].value_counts(normalize=True))"`
  - Salida:
    ```
    size_class
    large    0.861958
    small    0.138042
    ```
- **Criterio afectado:** Criterio 3 (linaje) y Criterio 9 (afirmaciones sostenidas).
- **Etapa probable de origen:** Proyecto original / T1.

### H3 — menor — Sobreajuste severo en Random Forest por falta de regularización de profundidad
- **Descripción:** Random Forest alcanza un AP perfecto en el conjunto de entrenamiento (1.0000 ± 0.0000) debido a la ausencia de restricción de profundidad (`max_depth=None`, `min_samples_split=2`), mientras que su AP fuera de muestra es 0.4330 ± 0.1066. Esto evidencia sobreajuste completo al train, aunque la evaluación fuera de pliegue reportada en el README es honesta.
- **Evidencia:**  
  - Entrada: Corrida `main` en `classification.ipynb` evaluando AP en train vs test por fold.
  - Comando: `uv run python -c "..."` (evaluación pareada train vs test sobre 25 folds).
  - Salida:
    ```
    Logistic Regression : Train AP = 0.5214 ± 0.0443 | Test AP = 0.5153 ± 0.1544
    Random Forest       : Train AP = 1.0000 ± 0.0000 | Test AP = 0.4330 ± 0.1066
    SVM (RBF)           : Train AP = 0.4266 ± 0.0205 | Test AP = 0.4264 ± 0.0899
    ```
- **Criterio afectado:** Criterio 6 (modelos con hiperparámetros congelados de `main` 1f2e02f).
- **Etapa probable de origen:** Código heredado de `main` (commit 1f2e02f).

### H4 — menor — Anomalía formal en la ablación de `star_radius` para SVM (RBF)
- **Descripción:** En SVM (RBF), remover `star_radius` reduce el AP en 0.0094 (ΔAP = +0.0094), mientras que remover cualquiera de las otras tres variables aumenta el AP (rango [-0.0241, -0.0083]). Por definición estricta del brief ("ΔAP fuera del rango de esas tres"), la variación es formalmente anómala, si bien la magnitud es insignificante (< 0.01) y no tiene significancia estadística (t = +0.371, p = 0.7137).
- **Evidencia:**  
  - Entrada: Evaluación de ablaciones 1-a-1 sobre los 25 folds de `main`.
  - Comando: `uv run python attack_2a.py`
  - Salida:
    ```
    Model: SVM (RBF) (Full AP: 0.4264 ± 0.0899)
      Without orbital_period : AP=0.4346 ± 0.0824 | ΔAP = -0.0083 | t = -0.329, p = 0.7453
      Without star_mass      : AP=0.4465 ± 0.0985 | ΔAP = -0.0202 | t = -0.581, p = 0.5666
      Without star_radius    : AP=0.4170 ± 0.0984 | ΔAP = +0.0094 | t = +0.371, p = 0.7137
      Without star_teff      : AP=0.4505 ± 0.1035 | ΔAP = -0.0241 | t = -0.669, p = 0.5100
      Range of other 3 ΔAP: [-0.0241, -0.0083]
      star_radius ΔAP: +0.0094 -> Anomalous? True
    ```
- **Criterio afectado:** Criterio 4 (veredicto de variables y efecto de `star_radius`).
- **Etapa probable de origen:** Selección de características en T4.

### H5 — menor — La explicación del README para la brecha de ROC-AUC en LR es incompleta respecto a la pérdida de separabilidad univariada
- **Descripción:** El README atribuye la diferencia de ROC-AUC (0.81 en `unverifiable` vs 0.68 en `measured`) a que RV favorece estrellas brillantes y gigantes gaseosos. Si bien no hay fuga, la explicación omite el mecanismo estadístico directo: en `unverifiable`, los planetas pequeños son casi en su totalidad enanas M/K (separabilidad univariada de parámetros estelares con ROC-AUC 0.77–0.80), mientras que en `measured`, los planetas pequeños orbitan estrellas de tipo solar (separabilidad univariada colapsa a ROC-AUC 0.58).
- **Evidencia:**  
  - Entrada: Predicciones fuera de fold por categoría de procedencia frente a distribuciones estelares.
  - Comando: `uv run python attack_extra.py`
  - Salida:
    ```
    Unverifiable small (N=66) star_teff median = 4809 K | large (N=317) median = 5793 K (ROC-AUC: 0.7697)
    Measured small (N=17) star_teff median = 5680 K     | large (N=219) median = 5738 K (ROC-AUC: 0.5775)
    LR ROC-AUC: unverifiable = 0.8108 ± 0.0033 | measured = 0.6775 ± 0.0076
    ```
- **Criterio afectado:** Criterio 9 (afirmaciones sostenidas / discusión del README).
- **Etapa probable de origen:** Redacción de la discusión en T8.

---

## Lo que no pude atacar y por qué

1. **Procedencia exacta de las 623 filas originales:** Imposible de auditar de forma determinista porque no existe registro de la consulta o script de descarga original en el repositorio ni en el Proyecto 1 (reconocido como supuesto S1 en `docs/brief.md`).
2. **Impacto de hiperparámetros alternativos:** El brief (sección "NO incluye" y criterio 6) prohíbe explícitamente modificar o ajustar hiperparámetros de los modelos, por lo que no se evaluó si regularizar Random Forest elimina el sobreajuste de H3 sin alterar el desempeño fuera de muestra.
