# Decisiones

## T1 — Linaje de `exoplanets_clean.csv` (Especialista, 2026-10-02)

### Entradas

| Archivo | Filas | SHA-256 | Estado en git |
|---|---|---|---|
| `exoplanets_clean.csv` (este repo) | 623 | `15f10a81606288d4dec71a8380fff47451cd9f8b5346add5b1c34e79bb966378` | versionado desde b316a47 |
| `~/proyectos/exoplanet-analysis/exoplanets.csv` (Proyecto 1) | 6366 (`pl_name` único) | `e5570cbaae8004213616c02ce9c30634a8b3d2c67c0e2acef90344b47fbe28e8` | **no versionado** (`.gitignore: *.csv`); mtime 2026-09-18 00:33 -0600 |

`exoplanets.csv` del Proyecto 1 es la salida de la consulta TAP del README del Proyecto 1 (commit 8e7f428): `select pl_name,pl_bmassj,pl_rade,pl_orbper,discoverymethod,st_mass,st_rad,st_teff from pscomppars`. Como no está versionado, el linaje depende de este SHA-256: si se vuelve a descargar, el emparejamiento puede cambiar.

### Método de emparejamiento

`row_id` = posición de la fila de datos en `exoplanets_clean.csv`, empezando en 0.

Columnas comparadas (este repo → Proyecto 1): `orbital_period→pl_orbper`, `mass→pl_bmassj`, `radius×11.208981→pl_rade`, `star_mass→st_mass`, `star_radius→st_rad`, `star_teff→st_teff`.

Regla:
1. Hay candidato si el periodo coincide con `rtol = 1e-3` **y** al menos 2 de las otras 5 columnas coinciden con `rtol = 5 %`. Puntaje = columnas que coinciden (de 6).
2. Si una fila tiene un solo candidato, o el mejor le gana al segundo por ≥ 1 punto, se toma el mejor de forma provisional.
3. Uno a uno: si un mismo `pl_name` lo toman dos o más filas, todas esas filas pasan a `ambiguous`.
4. `none` = sin candidatos; `ambiguous` = empate en el mejor puntaje o `pl_name` disputado.

Se toleran diferencias porque los valores no coinciden exactamente (ver "Fuente"). Entre las 521 filas `unique`, solo 284 tienen el radio a menos de 1 % y 237 tienen la masa a menos de 1 % de los valores del Proyecto 1.

El script que generó `data/processed/lineage.csv` (se ejecutó con `uv run --no-project --with pandas python t1_lineage.py exoplanets_clean.csv ~/proyectos/exoplanet-analysis/exoplanets.csv data/processed/lineage.csv`):

```python
"""T1: match the 623 labelled rows to Project 1's exoplanets.csv (pscomppars)."""

import sys
from collections import Counter

import numpy as np
import pandas as pd

R_JUP_IN_R_EARTH = 11.208981
PERIOD_RTOL = 1e-3
OTHER_RTOL = 0.05
MIN_OTHER_AGREE = 2
MARGIN = 1

ours_path, p1_path, out_path = sys.argv[1:4]
ours = pd.read_csv(ours_path)
ours.insert(0, "row_id", range(len(ours)))
p1 = pd.read_csv(p1_path)

cols_ours = [
    "orbital_period", "mass", "radius", "star_mass", "star_radius", "star_teff"
]
cols_p1 = ["pl_orbper", "pl_bmassj", "pl_rade", "st_mass", "st_rad", "st_teff"]
A = ours[cols_ours].to_numpy(dtype=float)
A[:, 2] *= R_JUP_IN_R_EARTH
P = p1[cols_p1].to_numpy(dtype=float)

cands = []
for x in A:
    per = np.isclose(P[:, 0], x[0], rtol=PERIOD_RTOL, atol=0)
    oth = np.isclose(P[:, 1:], x[1:], rtol=OTHER_RTOL, atol=0).sum(axis=1)
    idx = np.where(per & (oth >= MIN_OTHER_AGREE))[0]
    score = 1 + oth[idx]
    order = np.argsort(-score, kind="stable")
    cands.append(list(zip(idx[order], score[order], strict=True)))

pick = {}
for rid, c in enumerate(cands):
    if len(c) == 1 or (len(c) > 1 and c[0][1] - c[1][1] >= MARGIN):
        pick[rid] = c[0][0]
claims = Counter(pick.values())

rows = []
for rid, c in enumerate(cands):
    if rid in pick and claims[pick[rid]] == 1:
        rows.append((rid, p1.pl_name.iloc[pick[rid]], "", "unique"))
    elif not c:
        rows.append((rid, "", "", "none"))
    else:
        rows.append((rid, "", "", "ambiguous"))
out = pd.DataFrame(rows, columns=["row_id", "pl_name", "hostname", "match_status"])
out.sort_values("row_id").to_csv(out_path, index=False, lineterminator="\n")

print(out.match_status.value_counts().to_string())
for rid, c in enumerate(cands):
    if rows[rid][3] == "ambiguous":
        names = "; ".join(f"{p1.pl_name.iloc[j]} ({s}/6)" for j, s in c)
        print(f"AMB {rid}: {names}")
```

`hostname` queda vacío en todas las filas: el CSV del Proyecto 1 no lo trae. Lo llena T3 desde TAP. No se dedujo de `pl_name` para no meter una heurística sin verificar.

### Resultado (criterio 14)

| `match_status` | Filas | gas_giant | terrestrial |
|---|---|---|---|
| `unique` | 521 | 447 | 74 |
| `none` | 83 | 72 | 11 |
| `ambiguous` | 19 | 18 | 1 |
| **Total** | 623 | 537 | 86 |

Comprobado sobre `lineage.csv`: 623 filas, `row_id` único, ningún `pl_name` repetido entre las `unique`. Método de descubrimiento de las 521 `unique` (según el Proyecto 1): Transit 501, Radial Velocity 17, Orbital Brightness Modulation 3.

**Filas `none` (83):** 0 1 2 6 7 34 44 46 48 57 58 65 78 81 82 94 95 103 112 113 114 130 170 176 178 179 181 188 206 211 215 223 225 228 234 235 250 269 271 299 319 320 326 327 339 346 359 361 368 429 442 443 449 450 458 464 484 486 490 498 499 502 503 533 535 543 547 555 559 562 566 573 576 584 586 587 591 601 604 607 613 614 619. Las 4 filas con `mass > 30 M_J` están aquí; en el Proyecto 1 la masa máxima es 30 M_J.

**Filas `ambiguous` (19), con sus candidatos (puntaje/6):**

| row_id | Candidatos |
|---|---|
| 3 | Kepler-208 b (3/6); 51 Peg b (3/6) |
| 73 | TOI-3877 b (3/6); Kepler-119 c (3/6) |
| 102 | WASP-62 b (4/6); Kepler-914 b (3/6) |
| 104 | Kepler-1398 b (4/6); HAT-P-5 b (4/6) |
| 123 | HATS-12 b (3/6); HATS-66 b (3/6) |
| 132 | Kepler-425 b (4/6); HD 108236 b (4/6) |
| 137 | HATS-25 b (6/6) |
| 172 | Kepler-15 b (4/6); HD 49674 b (4/6); TIC 117642575 b (3/6) |
| 227 | TOI-3688 A b (3/6); TOI-3819 b (3/6) |
| 229 | Kepler-416 c (4/6); TOI-5174 b (4/6); Kepler-418 c (4/6) |
| 279 | Kepler-145 c (3/6); Kepler-1452 b (3/6) |
| 333 | Kepler-307 b (4/6); Kepler-1765 b (4/6); K2-393 b (4/6) |
| 347 | HATS-17 b (3/6); TIC 393818343 b (3/6) |
| 378 | TOI-3688 A b (4/6); TOI-3819 b (4/6); TOI-3278 b (3/6); KELT-8 b (3/6); Kepler-44 b (3/6) |
| 425 | Kepler-336 c (4/6); Kepler-68 c (4/6) |
| 447 | KOI-94 e (3/6); Kepler-403 c (3/6) |
| 539 | WASP-20 b (4/6); Kepler-107 c (4/6); Kepler-535 b (3/6) |
| 575 | HATS-25 b (3/6) |
| 577 | WASP-62 b (3/6) |

Las filas 137/575 se disputan HATS-25 b, y 102/577 se disputan WASP-62 b; por eso las cuatro quedan como ambiguas. La regla trata igual todas las columnas, así que algunos empates parecen fáciles de resolver a ojo (por ejemplo, la fila 104 tiene 1.06 M_J y apunta a HAT-P-5 b, no a Kepler-1398 b). No se resolvieron a mano para no meter juicio sin una regla fija.

**Sensibilidad.** Si se cambia un parámetro a la vez, casi todas las `unique` conservan el mismo `pl_name`. Estas filas sí cambian de pareja en al menos una variante, así que son `unique` pero frágiles:

| Variante | Conteos (u/n/a) | Filas que cambian de `pl_name` |
|---|---|---|
| periodo `rtol 1e-4` | 485/137/1 | 50, 183, 265 |
| otras columnas `rtol 10 %` | 549/37/37 | 50, 74, 122, 265, 439, 524, 545, 612 |
| otras columnas `rtol 2 %` | 413/193/17 | 308, 344, 398 |
| margen ≥ 2 | 486/83/54 | ninguna |

### Pasos del linaje

| Paso | Estado | Evidencia / lo que se intentó |
|---|---|---|
| **Fuente** | **Reconstruido parcialmente.** Los valores son del NASA Exoplanet Archive (`pscomppars` o equivalente), pero de una **versión anterior** a la descarga del Proyecto 1 del 2026-09-18 | El 84 % de las filas se empareja con `pscomppars` por periodo + parámetros, pero con deriva en los valores (ver arriba). Ejemplo: la fila 3 tiene el periodo de 51 Peg b (4.2308 d) con radio 21.30 R⊕, mientras que el `pscomppars` del Proyecto 1 da 14.1 R⊕. Ese radio es una imputación distinta, así que viene de otra versión del archivo. Conclusión: las 623 filas **no se derivaron del `exoplanets.csv` ni del `exoplanets_clean.csv` (5906 filas) del Proyecto 1**. Esto es compatible con una copia más vieja, como el dataset de Kaggle `eduardowoj/exoplanets-database` (~3741 planetas) que cita la celda 3 de `exoplanet_eda.ipynb`, pero **no se verificó**: no se descargó Kaggle. |
| **Consulta / descarga y fecha** | **Desconocido** | No hay script ni registro en este repo ni en el Proyecto 1. Se buscaron en `~` otros CSV o ZIP de exoplanetas y archivos que mencionen `planet_type`: solo aparecen este CSV y el notebook. El commit b316a47 (2026-09-19, coautoría "Claude Sonnet 5") agrega el CSV ya filtrado y etiquetado. |
| **Filtro hasta 623 filas** | **Desconocido** | Las 623 filas no tienen nulos ni duplicados. De las `unique`, 520 de 521 están completas en las 6 columnas del Proyecto 1, lo que es compatible con un filtro de casos completos sobre la fuente original, pero no explica el tamaño (623 contra 5906). El 96 % de las `unique` son de tránsito. No se pueden reconstruir los conteos antes/después de cada filtro sin la fuente original. |
| **Unidades** | **Reconstruido** | `mass` en M_J (≡ `pl_bmassj`; mediana del cociente 1.000). `radius` en R_J: `radius × 11.208981` ≈ `pl_rade` (mediana del cociente 11.209). El gigante gaseoso más chico, 0.17842836725554 R_J, es igual a 2/11.208981, lo que indica una conversión R⊕→R_J con ese factor. `orbital_period` en días, `star_mass` en M☉, `star_radius` en R☉ y `star_teff` en K (≡ `pl_orbper`, `st_mass`, `st_rad`, `st_teff`). |
| **Etiqueta `planet_type`** | **Reconstruido como regla consistente; la regla exacta no se confirmó** | La regla `radius × 11.208981 ≥ 2 R⊕ → gas_giant`, y si no `terrestrial`, reproduce las 623 etiquetas. Máx. terrestre = 1.99520 R⊕; mín. gigante = 2.00000 R⊕. Cualquier umbral en (1.9952, 2.0000] R⊕ da lo mismo; 2 R⊕ es el valor natural, pero no hay registro de que fuera la regla usada. |

### Para Mai

- La discrepancia de S1 (Kaggle vs. `pscomppars`) se resuelve en parte: los datos son del archivo de la NASA, pero no de la descarga del Proyecto 1. "Kaggle" es compatible con esto y no se ha verificado.
- El `exoplanets.csv` del Proyecto 1 no está versionado; el linaje se fija con el SHA-256 de arriba.
- Hay 102 filas (`none` + `ambiguous`) sin `pl_name`. T3 solo puede traer `hostname` para las 521 `unique`, así que las demás usarán el respaldo `tuple:` del criterio 13.
