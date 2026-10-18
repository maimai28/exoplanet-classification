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

## T2 — CSV a `data/raw/` (Implementador, 2026-10-13)

- `git mv exoplanets_clean.csv data/raw/exoplanets_clean.csv`. El blob no cambia: `c6671ce61c7c339a91699ead01c17f911a04afe1`, igual al de b316a47.
- `data/raw/SHA256SUMS` usa el formato de `sha256sum` con la ruta relativa a `data/raw/`, así que se comprueba con `cd data/raw && sha256sum -c SHA256SUMS`. Valor: `15f10a81606288d4dec71a8380fff47451cd9f8b5346add5b1c34e79bb966378`, igual a `git show b316a47:exoplanets_clean.csv | sha256sum` y al que registró T1.
- El notebook sigue leyendo `exoplanets_clean.csv` desde la raíz, así que **no corre entre T2 y T7**. No se tocó: cambiar la ruta de lectura es parte de T7.

## T3 — Procedencia de la masa y `hostname` desde `pscomppars` (Especialista, 2026-10-13)

### Consulta

- Servicio: NASA Exoplanet Archive, TAP síncrono (`https://exoplanetarchive.ipac.caltech.edu/TAP/sync`), `POST`, `format=csv`. Pública, de solo lectura, sin credenciales (autorizada en P1).
- Fecha: 2026-10-13 21:32 -0600 (2026-10-14T03:32:28Z).
- ADQL: `select pl_name,hostname,pl_bmassprov from pscomppars where pl_name in (<los 521 pl_name con match_status = unique en lineage.csv de 94fb11b, entre comillas simples, en orden de row_id>) order by pl_name`. SHA-256 del texto exacto de la consulta (con `\n` final): `a79fd72171c36c1c0dd7ae13b021aa2ec422d33008dd58597c7573db9cf9b7dc`.
- Filas devueltas: **521** (una por planeta pedido; ningún nombre faltó ni se repitió).
- Respuesta guardada sin cambios en `data/raw/pscomppars_provenance_2026-10-13.csv`, SHA-256 `4d280c02823322a876d4321aec570643413d57bfc6c622c9b5b5ea9f714baacd`. Escrito una vez (regla 4); no se agregó a `SHA256SUMS`, que es de T2.

Para reproducir:

```bash
names=$(awk -F, 'NR>1 && $4=="unique"{printf "%s'\''%s'\''", (n++?",":""), $2}' data/processed/lineage.csv)
printf '%s\n' "select pl_name,hostname,pl_bmassprov from pscomppars where pl_name in ($names) order by pl_name" > query.adql
curl -sS --fail -X POST https://exoplanetarchive.ipac.caltech.edu/TAP/sync \
  --data-urlencode "query@query.adql" --data-urlencode "format=csv" -o resp.csv
```

Una nueva descarga puede dar otros valores: `pscomppars` cambia con el tiempo (ver "Deriva" abajo).

### `lineage.csv`

Solo cambió la columna `hostname`: se llenó, por `pl_name`, en las 521 filas `unique`; queda vacía en las 102 `none` + `ambiguous`, que van al respaldo `tuple:` del criterio 13 (decisión de Mai, bitácora 2026-10-02). `row_id`, `pl_name` y `match_status` son idénticos byte a byte a los de 94fb11b. No se dedujo `hostname` de `pl_name` ni de la tupla para las filas sin pareja.

### Criterio de listo 1: filas por categoría de procedencia de la masa

| `pl_bmassprov` | gas_giant | terrestrial | Total |
|---|---|---|---|
| `Mass` | 418 | 66 | 484 |
| `M-R relationship` | 22 | 8 | 30 |
| `Msini` | 7 | 0 | 7 |
| Sin procedencia (`none` + `ambiguous`, sin `pl_name`) | 90 | 12 | 102 |
| **Total** | 537 | 86 | 623 |

Ninguna fila `unique` tiene `pl_bmassprov` vacío.

**Deriva.** `pl_bmassprov` describe el valor de `pscomppars` **de hoy**, no necesariamente el valor de `mass` de nuestro CSV, que viene de una versión anterior (T1). Contra la `pl_bmassj` del Proyecto 1 (descarga del 2026-09-18), la `mass` de nuestro CSV coincide a 1 % en:

| `pl_bmassprov` | coincide | no coincide |
|---|---|---|
| `Mass` | 234 | 250 |
| `M-R relationship` | 1 | 29 |
| `Msini` | 2 | 5 |

Es decir, en 284 de las 521 filas la masa del CSV no es la masa a la que se refiere la etiqueta de procedencia.

### Criterio de listo 2: colisiones entre `hostname` y la tupla estelar

Tupla = (`star_mass`, `star_radius`, `star_teff`) tal como está en el CSV.

| Medida | Valor |
|---|---|
| Filas agrupables por `hostname` (`n_by_hostname`) | 521 (422 `hostname` distintos) |
| Filas al respaldo por tupla (`n_by_tuple`) | 102 |
| `hostname` con más de una tupla (`hostname_collisions`) | 1 |
| Tuplas con más de un `hostname` (`tuple_collisions`) | 4 |
| Tuplas del respaldo que también aparecen en filas con `hostname` | 11 tuplas, 13 filas de respaldo |

- `hostname` con más de una tupla: **Kepler-20** — filas 293–297 (0.912, 0.944, 5466) y fila 338, Kepler-20 g (0.98, 0.97, 5314).
- Tuplas con más de un `hostname`:
  - (0.65, 0.59, 4500): 309 Kepler-1388 b / 310 Kepler-26 c
  - (0.71, 0.65, 4450): 265 K2-121 b / 266–267 Kepler-114 c, d
  - (0.83, 0.73, 5145): 406 Kepler-1254 d / 407 Kepler-57 c
  - (0.93, 0.98, 5942): 287 Kepler-529 d / 288 Kepler-177 c

  En los cuatro casos las filas son contiguas en el CSV, lo que es compatible con que pertenezcan al mismo sistema y una de las parejas de T1 sea incorrecta (la fila 265 es frágil). No se corrigió: es una observación, no una decisión.
- Las 13 filas de respaldo que comparten tupla con filas que sí tienen `hostname` recibirían un `group_id` `tuple:` distinto del `hostname` de su posible sistema.

### Filas frágiles

Las filas `unique` que cambian de `pl_name` en alguna variante de la sensibilidad de T1 conservan su pareja y su `hostname` (decisión de Mai) y se marcan aquí como frágiles. Son **12 filas distintas**: la tabla de T1 lista 14 apariciones, pero 50 y 265 aparecen en dos variantes.

| row_id | `pl_name` | `hostname` | `pl_bmassprov` | `planet_type` |
|---|---|---|---|---|
| 50 | Kepler-677 b | Kepler-677 | M-R relationship | gas_giant |
| 74 | Kepler-1772 b | Kepler-1772 | M-R relationship | gas_giant |
| 122 | Kepler-501 c | Kepler-501 | M-R relationship | gas_giant |
| 183 | K2-215 b | K2-215 | M-R relationship | gas_giant |
| 265 | K2-121 b | K2-121 | Mass | terrestrial |
| 308 | Kepler-25 c | Kepler-25 | Mass | gas_giant |
| 344 | Kepler-350 c | Kepler-350 | Mass | gas_giant |
| 398 | Kepler-51 c | Kepler-51 | Mass | gas_giant |
| 439 | Kepler-85 b | Kepler-85 | Mass | terrestrial |
| 524 | HD 212301 b | HD 212301 | Msini | gas_giant |
| 545 | Kepler-1061 b | Kepler-1061 | M-R relationship | gas_giant |
| 612 | WASP-188 b | WASP-188 | Mass | gas_giant |

El contrato de `lineage.csv` no tiene una columna para esto, así que la marca vive solo en este documento.

### Uso

`hostname` y `pl_bmassprov` son metadatos de auditoría y agrupamiento; no son variables del modelo (brief, "NO incluye").

## T3b — Masa del CSV frente a la relación masa-radio del Archive (Especialista, 2026-10-13)

Ajustes de Mai al prompt (2026-10-13), antes de empezar: manda el contrato de `docs/plan.md` (columnas, `mr_rel_residual`, y "no establecida" solo en este documento); las filas `Msini` entran a la prueba como cualquier otra; los controles son los del plan, y el positivo se estratifica por `mass_matches_p1`; las 17 filas RV van como subconjunto informativo; el `exoplanets.csv` del Proyecto 1 es entrada de solo lectura. No hubo consultas TAP, descargas de tablas ni dependencias nuevas.

### Entradas (solo lectura, SHA-256 verificado por el script)

| Archivo | SHA-256 |
|---|---|
| `data/raw/exoplanets_clean.csv` | `15f10a81606288d4dec71a8380fff47451cd9f8b5346add5b1c34e79bb966378` |
| `data/raw/pscomppars_provenance_2026-10-13.csv` | `4d280c02823322a876d4321aec570643413d57bfc6c622c9b5b5ea9f714baacd` |
| `~/proyectos/exoplanet-analysis/exoplanets.csv` (Proyecto 1) | `e5570cbaae8004213616c02ce9c30634a8b3d2c67c0e2acef90344b47fbe28e8` (coincide con T1) |
| `data/processed/lineage.csv` | el de bc9592e |

### Fuentes consultadas (todas con acceso el 2026-10-13)

| Fuente | URL / DOI | Qué se tomó |
|---|---|---|
| NASA Exoplanet Archive, *How the Archive Calculates Values in the Planetary Systems Composite Parameters Table* ("Last updated: 10 June 2026") | https://exoplanetarchive.ipac.caltech.edu/docs/pscp_calc.html (SHA-256 del HTML leído: `b53385e75bb1196c03f233b84a7b3fd8e79d7f67cb05129f7e509ad9d8586c97`) | Forma, coeficientes y regímenes de la relación (secciones "Planet Radius" y "Planet Mass") |
| La misma página en Wayback Machine | https://web.archive.org/web/20210923025628/https://exoplanetarchive.ipac.caltech.edu/docs/pscp_calc.html ("Last updated: 14 April 2021"); también las capturas 20230304190815, 20240523163444 ("2 May 2024") y 20260315143404 | Comprobar si la relación cambió: la sección "Planet Mass" es idéntica en las cinco versiones |
| NASA Exoplanet Archive, *Planetary Systems and PSCompPars Table Definitions* ("Last updated: 4 June 2026") | https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html | Definición de `pl_bmassprov`: "Options are: Mass, M\*sin(i)/sin(i), and M\*sini". **No menciona `M-R relationship`**, aunque T3 sí lo recibió de TAP; la documentación de la columna está desactualizada respecto a sus valores |
| Chen, J. & Kipping, D. (2017), *Probabilistic Forecasting of the Masses and Radii of Other Worlds*, ApJ 834, 17 | DOI 10.3847/1538-4357/834/1/17; arXiv:1603.08614 (solo se leyó el resumen) | Es la relación que cita el Archive. Los coeficientes se tomaron del Archive, que dice tomarlos de "their Table 2 (or derived thereof)"; la tabla del artículo no se leyó directamente |
| Mamajek et al. (2015), *IAU 2015 Resolution B3* | arXiv:1510.07674, DOI 10.48550/arXiv.1510.07674 (p. 3, tabla de constantes) | (GM)_J^N / (GM)_E^N = 1.2668653e17 / 3.986004e14 = 317.8284; R_eJ^N / R_eE^N = 7.1492e7 / 6.3781e6 = 11.208981, que es el mismo factor que T1 reconstruyó para el radio |

### Relación: **establecida**

El Archive invierte la relación de Chen & Kipping (2017) por tramos, con 𝓜 = log10(Mp/M⊕) y 𝓡 = log10(Rp/R⊕):

𝓜 = (𝓡 − 𝓒) / 𝓢, con

| Régimen (Rp en R⊕) | 𝓒 | 𝓢 |
|---|---|---|
| Rp < 1.23 | 0.00346 | 0.2790 |
| 1.23 ≤ Rp < 11.1 | −0.0925 | 0.589 |
| 11.1 ≤ Rp < 14.3 | — | — (el Archive "abstain[s] from calculating a planet mass": régimen degenerado por la pendiente negativa del tramo joviano) |
| Rp ≥ 14.3 | −2.85 | 0.881 |

- **Versión del catálogo a la que aplica:** la documentación es idéntica desde la captura del 2021-09-23 (página fechada el 14 de abril de 2021) hasta la versión del 10 de junio de 2026. La versión del catálogo de la que salió el CSV es desconocida (T1). Si es anterior a abril de 2021, la relación de ese momento no está documentada aquí.
- **Frontera de 14.3:** el texto dice "≈ 11.1 ≤ Rp ≤ 14.3", y la tabla asigna Rp ≥ 14.3 al tramo estelar. Se usó la tabla. Ninguna fila tiene Rp exactamente igual a 14.3.
- **Tramo Rp ≥ 14.3:** predice masas estelares (≈ 110 M_J para 14.6 R⊕), así que un gigante de ~1 M_J con ese radio nunca puede caer sobre la relación. Es lo que dice la documentación; se trata como un régimen comprobable.
- **Coherencia interna:** el tramo terrestre en Mp = 2.04 M⊕ da 𝓡 = 0.0898 y el neptuniano da 0.0899, así que es continuo dentro del redondeo de los coeficientes.
- **Validación de la implementación** con los valores de `pscomppars` del Proyecto 1 (2026-09-18), no con el CSV: las 30 filas con `pl_bmassprov` = `M-R relationship` dan `pl_bmassj`/predicción − 1 en [−0.0037, +0.0035]. Esa diferencia se explica por el redondeo de `pl_bmassj` a 3 cifras significativas (p. ej., 0.0101 ± 0.00005 es ±0.5 %). En todo el `exoplanets.csv` del Proyecto 1, 1886 de 6366 filas caen a menos de 1e-3. Es un dato informativo; no se usa para clasificar.
- **Unidades:** Rp = `radius` × 11.208981; la masa predicha pasa a M_J dividiendo entre 317.8284.

### Tolerancia ("exacto") por precisión numérica del CSV

Se fija por fila, según cuántos decimales trae cada valor escrito en el CSV:

- δm = ½·10^(−decimales de `mass`); δr = ½·10^(−decimales de `radius`).
- La fila es `on_relation` si el intervalo [m − δm, m + δm] cruza el intervalo [f(Rp_lo)·(1 − ε), f(Rp_hi)·(1 + ε)], donde Rp_lo y Rp_hi = (r ∓ δr)·11.208981 y f es la relación (creciente dentro de cada régimen comprobable).
- Si un extremo del intervalo de radio entra en la zona degenerada, se recorta al borde del lado comprobable.
- ε = 1e-3 es un margen por convenciones de unidades (M_J/M⊕ y R_J/R⊕). La diferencia entre 317.83 y 317.8284 es de 5e-6, así que ε es holgado.

Justificación: si la masa se calculó con la relación y luego se redondeó al escribirse, el único desacuerdo posible es el del redondeo de los dos valores impresos. Esta regla no tiene parámetros ajustables más allá de ε.

Tolerancia relativa equivalente en masa, ≈ δm/m + (δr/r)/𝓢 + ε, sobre las 466 filas comprobables: mínimo 0.001, p25 0.0036, mediana 0.0088, p75 0.028, p90 0.064, máximo 0.93. Es amplia en las masas con una sola cifra significativa (p. ej., `0.01` → ±50 %).

Nota de proceso: antes de fijar la regla se miró una exploración de residuos crudos con umbrales globales (ninguna fila a menos de 1e-3; 2 a menos de 1e-2), incluida la de las 30 filas `M-R relationship`. La regla no se ajustó después de eso: sale solo de los decimales impresos.

### `not_testable`

Solo por régimen, según el plan: 11.1 ≤ Rp < 14.3 R⊕ (valor puntual), **157 filas**. Ninguna fila carece de radio. Las `Msini` entran a la prueba (decisión de Mai).

Hay 13 filas cuyo intervalo de redondeo del radio cruza 11.1 o 14.3: 2, 20, 64, 98, 127, 170, 174, 179, 282, 522, 543, 571 y 616. Se clasifican por su valor puntual. Las filas 179 y 282 (11.209 R⊕) quedan `not_testable`; las demás son comprobables y todas quedan `off_relation`.

### Distribución de `mr_rel_residual` (466 filas comprobables)

Cuantiles 0 / 5 / 25 / 50 / 75 / 95 / 100 %: −0.998 / −0.996 / −0.985 / −0.106 / 1.86 / 52.8 / 1059.3.

| \|`mr_rel_residual`\| | ≤ 1e-3 | (1e-3, 1e-2] | (1e-2, 0.05] | (0.05, 0.1] | (0.1, 0.5] | (0.5, 1] | (1, 10] | > 10 |
|---|---|---|---|---|---|---|---|---|
| Filas | 0 | 2 | 7 | 9 | 79 | 226 | 91 | 52 |

Los residuos cercanos a −1 vienen sobre todo del tramo Rp ≥ 14.3 (predicción estelar contra masa planetaria).

### Controles

**Positivo: las 30 filas `M-R relationship`.** 8 son `not_testable`; de las 22 comprobables, 3 quedan `on_relation` (14 %).

| `mass_matches_p1` | Filas | Comprobables | `on_relation` | Tasa |
|---|---|---|---|---|
| `true` | 1 (fila 460, K2-133 c) | 1 | 1 | 1/1 |
| `false` | 29 | 21 | 2 (filas 284 y 384) | 2/21 |

- **Hallazgo:** el control positivo falla en las filas que no coinciden con el Proyecto 1. En el catálogo de hoy esas 30 masas sí caen sobre la relación (validación de arriba), pero en el CSV la masa es otra. Por ejemplo, K2-95 b: CSV 1.67 M_J y catálogo 0.0345 M_J; Kepler-1254 d: 18.86 M_J y 0.00714 M_J. Es compatible con que, en la versión que originó el CSV, esas masas no vinieran de la relación, o vinieran de otro radio. Esto refuerza la decisión de T3 de que `pl_bmassprov` solo vale donde la masa coincide.
- El único positivo que coincide (fila 460) pasa con una masa impresa como `0.01`, que tiene una tolerancia de ±50 %; su residuo es +0.138. Su paso es poco informativo.

**Negativo: las 234 filas `Mass` que coinciden con el Proyecto 1.** 70 son `not_testable`; de las 164 comprobables, las **164 quedan `off_relation` (100 %)**, con un \|residuo\| mínimo de 0.0136. Por régimen: terrestre 3/3, neptuniano 84/84, estelar 77/77 (estos últimos son triviales por lo dicho del tramo Rp ≥ 14.3). La parte informativa del control son las 87 filas con Rp < 11.1.

**Subconjunto informativo, fuera de los controles: las 17 filas `unique` con `discoverymethod` = Radial Velocity (Proyecto 1).** Ninguna queda `on_relation`.
- `off_relation`: 9 (filas 4, 55, 56, 165, 169, 174, 180, 338 y 524).
- `not_testable`: 8 (filas 166, 167, 168, 171, 173, 175, 177 y 622).
- `mass_provenance`: `measured` 4 (filas 55, 56, 167 y 177) y `unverifiable` 13.

### Resultado (623 filas)

| `mr_status` | Filas |
|---|---|
| `on_relation` | 10 |
| `off_relation` | 456 |
| `not_testable` | 157 |

| `mass_provenance` | gas_giant | terrestrial | Total |
|---|---|---|---|
| `derived` | 4 | 6 | **10** |
| `measured` | 219 | 17 | **236** |
| `unverifiable` | 314 | 63 | **377** |
| **Total** | 537 | 86 | **623** |

- `derived` = las 10 `on_relation`. La única fila que coincide y tiene `M-R relationship` (460) también está `on_relation`.
- `measured` = las 234 `Mass` y las 2 `Msini` que coinciden con el Proyecto 1 (ninguna `on_relation`). Incluye 72 filas `not_testable`.
- `unverifiable` = 276 filas con `pl_name` cuya masa no coincide y 101 sin `pl_name`, todas sin `on_relation` (de las 284 que no coinciden, 8 quedan `on_relation` y van a `derived`; de las 102 sin `pl_name`, 1).

Cruce por procedencia:

| `pl_bmassprov` / `mass_matches_p1` | `on_relation` | `off_relation` | `not_testable` |
|---|---|---|---|
| sin `pl_name` | 1 | 77 | 24 |
| `M-R relationship` / false | 2 | 19 | 8 |
| `M-R relationship` / true | 1 | 0 | 0 |
| `Mass` / false | 6 | 193 | 51 |
| `Mass` / true | 0 | 164 | 70 |
| `Msini` / false | 0 | 3 | 2 |
| `Msini` / true | 0 | 0 | 2 |

### Diagnóstico de tolerancia: filas `Mass` que quedan `on_relation`

- `mass_matches_p1` = `true`: **0**.
- `mass_matches_p1` = `false`: **6**, con estos `row_id`:

| row_id | `pl_name` | `mass` | `radius` | residuo | Tolerancia por masa / por radio |
|---|---|---|---|---|---|
| 53 | GJ 1132 b | 0.0051 | 0.103 | −0.0035 | 0.010 / 0.017 |
| 190 | K2-18 b | 0.025 | 0.2 | +0.406 | 0.020 / 0.424 |
| 202 | K2-32 c | 0.04 | 0.31 | +0.069 | 0.125 / 0.027 |
| 247 | Kepler-102 f | 0.002 | 0.079 | +0.011 | 0.250 / 0.023 |
| 424 | Kepler-68 b | 0.0188 | 0.206 | +0.0052 | 0.003 / 0.004 |
| 481 | TRAPPIST-1 e | 0.002 | 0.0819 | −0.111 | 0.250 / 0.002 |

Las otras 4 filas `on_relation` son la 339 (sin `pl_name`; `0.1` M_J, ±50 %) y las `M-R relationship` 284, 384 y 460.

En 7 de las 10 filas `on_relation` (190, 202, 247, 339, 384, 460 y 481), la tolerancia que se deriva de la precisión supera el 10 %. Solo 53, 424 y, en menor grado, 284 (±8 %) caen sobre la relación con precisión fina.

### Para Mai (sin decidir fuga; eso es T4)

1. `derived` = 10 descansa sobre todo en masas impresas con 1–2 cifras significativas. Con la regla de combinación aprobada ("`on_relation` manda"), filas como K2-18 b o TRAPPIST-1 e, cuyas masas en la literatura vienen de RV o TTV, quedan `derived` por la tolerancia de redondeo. La tolerancia no se cambió después de ver esto. Si quieres una regla distinta (p. ej., `not_testable` cuando la tolerancia supere un umbral), es un cambio de criterio que pasa por la regla 6.
2. En el régimen terrestre, la relación de Chen & Kipping es un ajuste a planetas reales, así que una masa medida puede caer sobre ella por coincidencia. GJ 1132 b (−0.35 %) y Kepler-68 b (+0.5 %) son los casos finos.
3. El control positivo solo es fuerte en el catálogo actual (30/30 en el Proyecto 1). Sobre los valores del CSV pasa en 3 de 22; lo interpreto como deriva de versión, no como falla de la implementación.

### Reproducir

```bash
uv run python src/t3b_mass_provenance.py [ruta al exoplanets.csv del Proyecto 1]
```

Sin argumento usa `~/proyectos/exoplanet-analysis/exoplanets.csv`. El script verifica los tres SHA-256 y escribe `data/processed/mass_provenance.csv` con las columnas del contrato (623 filas, ordenadas por `row_id`).

### T3b — intento 2 (Especialista, 2026-10-15)

Re-ejecución con el criterio 4 modificado en d2a938e (regla 6, decisión de Mai del 2026-10-13). No hubo consultas TAP, descargas, dependencias nuevas ni escrituras en `data/raw/` o `tests/`. Las entradas, la relación, la tolerancia por fila, ε, los controles y la regla de combinación son los del intento 1 (43a9b14).

**Cambio de criterio.**
- Una fila que con la tolerancia de T3b daría `on_relation` y cuya tolerancia relativa por fila, δm/m + (δr/r)/𝓢 + ε, supera **0.10 (±10 % en masa)** queda `mr_status` = `not_testable` con `not_testable_reason` = `low_precision`. 𝓢 es la pendiente del régimen del radio puntual. En esas filas se conservan `mr_predicted_mass` y `mr_rel_residual` como diagnóstico.
- Las filas `off_relation` no cambian, sea cual sea su tolerancia.
- Las 157 filas de 11.1 ≤ Rp < 14.3 R⊕ llevan ahora `not_testable_reason` = `gap_11.1_14.3`, y en ellas `mr_predicted_mass` y `mr_rel_residual` siguen vacíos. Si una fila cumpliera las dos condiciones, manda `gap_11.1_14.3`; ninguna las cumple porque las del tramo no tienen predicción.
- Columna nueva en `mass_provenance.csv`: `not_testable_reason`, entre `mr_status` y `mass_provenance`.
- **El umbral de 0.10 se fijó después de ver los resultados del intento 1** (sección "Diagnóstico de tolerancia" de arriba). No es un umbral elegido a ciegas.

**Justificación.** Una tolerancia amplia debilita una coincidencia, no una discrepancia. Si una masa impresa con una sola cifra significativa (p. ej., `0.01`, ±50 %) cae dentro de la banda, eso no distingue una masa derivada de una medida. En cambio, si la masa queda fuera incluso de esa banda tan amplia, la discrepancia es aún más clara. Por eso el umbral solo se aplica a las filas que darían `on_relation`.

**Filas que cambiaron (7; todas eran `on_relation` en el intento 1):**

| row_id | `pl_name` | `mass` | `radius` | `pl_bmassprov` / `mass_matches_p1` | Tolerancia | `mr_rel_residual` | `mass_provenance` |
|---|---|---|---|---|---|---|---|
| 190 | K2-18 b | 0.025 | 0.2 | `Mass` / false | 0.445 | +0.406 | `derived` → `unverifiable` |
| 202 | K2-32 c | 0.04 | 0.31 | `Mass` / false | 0.153 | +0.069 | `derived` → `unverifiable` |
| 247 | Kepler-102 f | 0.002 | 0.079 | `Mass` / false | 0.274 | +0.011 | `derived` → `unverifiable` |
| 339 | (sin `pl_name`) | 0.1 | 0.483 | — | 0.503 | +0.258 | `derived` → `unverifiable` |
| 384 | Kepler-446 d | 0.01 | 0.12 | `M-R relationship` / false | 0.572 | +0.338 | `derived` → `unverifiable` |
| 460 | K2-133 c | 0.01 | 0.132 | `M-R relationship` / true | 0.507 | +0.138 | `derived` → `derived` (por la segunda rama de la regla: coincide y `M-R relationship`) |
| 481 | TRAPPIST-1 e | 0.002 | 0.0819 | `Mass` / false | 0.253 | −0.111 | `derived` → `unverifiable` |

Las otras 616 filas son idénticas al intento 1 en todas las columnas que ya existían.

**Filas que siguen `on_relation` (3):**

| row_id | `pl_name` | `pl_bmassprov` / `mass_matches_p1` | Tolerancia | `mr_rel_residual` |
|---|---|---|---|---|
| 53 | GJ 1132 b | `Mass` / false | 0.028 | −0.0035 |
| 284 | Kepler-167 d | `M-R relationship` / false | 0.086 | +0.040 |
| 424 | Kepler-68 b | `Mass` / false | 0.0078 | +0.0052 |

**Posibles falsos `derived`, para T4:** GJ 1132 b (fila 53) y Kepler-68 b (fila 424). Ambas tienen `pl_bmassprov` = `Mass` en el catálogo de hoy, aunque su masa no coincide con la del Proyecto 1, y caen sobre la relación con precisión fina en el régimen terrestre. Ahí la relación de Chen & Kipping es un ajuste a planetas reales, así que una masa medida puede caer sobre ella por coincidencia. Siguen `derived` por la regla de combinación ("`on_relation` manda"); no se cambia nada aquí.

**Controles (criterio de listo 4), después del cambio:**
- Positivo, las 30 `M-R relationship`: `mass_matches_p1` = true → 0 comprobables (la fila 460 pasa a `low_precision`); false → 1 `on_relation` (284), 19 `off_relation`, 1 `low_precision` (384) y 8 `gap`. El control positivo sobre los valores del CSV queda en 1 de 20 filas comprobables sin `low_precision`.
- Negativo, las 234 `Mass` que coinciden: sin cambios, 164/164 `off_relation` y 70 `gap`.
- Diagnóstico, filas `Mass` que quedan `on_relation`: `mass_matches_p1` = true → **0**; false → **2** (filas 53 y 424).
- Subconjunto RV (17 filas): sin cambios.

**Resultado (623 filas), antes → después:**

| `mr_status` | Intento 1 | Intento 2 |
|---|---|---|
| `on_relation` | 10 | **3** |
| `off_relation` | 456 | **456** |
| `not_testable` | 157 | **164** (157 `gap_11.1_14.3` + 7 `low_precision`) |
| Total | 623 | 623 |

| `mass_provenance` | Intento 1 | Intento 2 | gas_giant | terrestrial |
|---|---|---|---|---|
| `derived` | 10 | **4** (53, 284, 424, 460) | 1 | 3 |
| `measured` | 236 | **236** | 219 | 17 |
| `unverifiable` | 377 | **383** | 317 | 66 |
| Total | 623 | **623** | 537 | 86 |

Cruce por procedencia:

| `pl_bmassprov` / `mass_matches_p1` | `on_relation` | `off_relation` | `not_testable` / `gap_11.1_14.3` | `not_testable` / `low_precision` |
|---|---|---|---|---|
| sin `pl_name` | 0 | 77 | 24 | 1 |
| `M-R relationship` / false | 1 | 19 | 8 | 1 |
| `M-R relationship` / true | 0 | 0 | 0 | 1 |
| `Mass` / false | 2 | 193 | 51 | 4 |
| `Mass` / true | 0 | 164 | 70 | 0 |
| `Msini` / false | 0 | 3 | 2 | 0 |
| `Msini` / true | 0 | 0 | 2 | 0 |

Los conteos coinciden fila por fila con el efecto esperado por el Arquitecto.

**Determinismo.** Dos ejecuciones seguidas de `uv run python src/t3b_mass_provenance.py` dan un `mass_provenance.csv` idéntico byte a byte (`cmp` sin diferencias), con SHA-256 `5fa605237b26bcac446d78e9c869bb936e194ad53e8341d0f490969881229992`.

## T4 — Veredicto de fuga por variable [TÚ]

Fecha: 2026-10-18. Insumos: criterio 4 del brief, mass_provenance.csv (T3b intento 2, commit 1617f94), hipótesis de etiqueta de T1 (radius ≥ 2 R⊕ reproduce 623/623).

### Criterio
Una variable es fuga si la etiqueta se puede calcular a partir de ella, o si ella se calcula a partir del radio planetario. Que una variable esté correlacionada físicamente con el radio no la hace fuga.

### Tabla

| Columna | Relación con la etiqueta | Veredicto | Justificación |
|---|---|---|---|
| planet_type | Es la etiqueta | objetivo | — |
| radius | La etiqueta es un umbral sobre esta columna | excluir | Fuga por definición (T1: 623/623). |
| mass | Mixta según la procedencia | sensibilidad | Ver la sección Masa. |
| orbital_period | Ninguna | incluir | Se mide del tránsito o de la velocidad radial, sin usar R. |
| star_mass | Ninguna | incluir | Propiedad estelar. |
| star_teff | Ninguna | incluir | Propiedad estelar. |
| star_radius | Indirecta: R = (Rp/R*)·R* | incluir | Por sí sola no fija R; Rp/R* no está en el CSV. Riesgo anotado para el red team. |

### Masa
- **derived (4): fuga directa.** Su masa se calculó a partir de R con Chen & Kipping (2017).
- **unverifiable (383, 61 %): no se puede descartar fuga.** Vienen de una versión anterior del catálogo y su procedencia no se puede reconstruir.
- **measured (236): sin fuga detectada.** GJ 1132 b y Kepler-68 b se anotan como posibles falsos derived.
- **Veredicto: sensibilidad.**
  - Modelo principal: sin masa, sobre las 623 filas.
  - Corrida de sensibilidad: con masa, solo sobre las 236 measured, comparada contra el modelo principal evaluado en esas mismas 236 filas.
- Si la masa mejora mucho la métrica, se reporta como dependencia de una variable físicamente ligada al radio por la relación M-R real.

### Consecuencia para el modelo
- El modelo principal usa 4 variables: orbital_period, star_mass, star_radius y star_teff.
- La pregunta pasa a ser si la clase de tamaño del planeta se puede predecir desde su órbita y su estrella. Se formula en T4b.

### Contrato para T5 a T7
- La lista de variables queda fija en `data/processed/features.json`:
  - `"main": ["orbital_period", "star_mass", "star_radius", "star_teff"]`
  - `"sensitivity_mass": main + ["mass"]`, restringida a mass_provenance == "measured"
  - `"excluded": {"radius": "etiqueta por umbral (T1)"}`
  - `"target": "planet_type"`
- T6 prueba que `radius` nunca entra al pipeline y que la corrida de sensibilidad usa solo filas measured.
- Cambiar esta lista requiere la regla 6.

### Abierto para el red team (T10)
- star_radius: ¿la métrica cae de forma anómala al quitarla? Eso indicaría que lleva información del radio planetario más allá de la física esperable.
