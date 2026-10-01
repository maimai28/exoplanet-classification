# exoplanet-classification

Proyecto: Clasificación de exoplanetas en terrestres vs gigantes gaseosos (scikit-learn, notebook).
Módulo por defecto: M2 (Datos)
Dueño: Mai. Todas las decisiones P1, P2 y P3 son suyas.

## Sistema de trabajo
Este repositorio sigue el "Sistema de agentes de IA para código". Cada sesión tiene UN rol, declarado en su primer mensaje. Si no se declaró un rol, pregunta cuál es antes de hacer nada.

## Permisos por rol
| Rol | Lee | Escribe |
|---|---|---|
| Arquitecto / Planificador | todo | docs/brief.md, docs/plan.md, docs/bitacora.md |
| Implementador | todo | src/, data/processed/, pyproject.toml, uv.lock, docs/decisiones.md |
| Tester | docs/brief.md, tests/ (fase A: NO src/) | tests/, reports/pruebas_vN.md |
| Verificador | todo menos docs/decisiones.md | reports/veredicto_vN.md |
| Especialista | lo que diga su tarea | lo que diga su tarea + docs/decisiones.md |

## Reglas que no se rompen
1. Nunca hagas commit ni push a main. Todo trabajo va en la rama exp/{AAAA-MM-DD-nombre}. main solo cambia cuando Mai hace el merge del pull request en GitHub (P3).
2. Nunca modifiques, borres ni saltes pruebas para que pasen. Solo el Tester escribe en tests/.
3. Nunca subas secretos. Credenciales en .env (incluido en .gitignore). No leas .env.
4. data/raw/ es inmutable: se escribe una vez y no se toca.
5. Nunca agregues funcionalidad que no pide docs/brief.md.
6. Una regla o un criterio de éxito solo cambia con aprobación de Mai, registrada en docs/bitacora.md.
7. En modo Estudio o en tareas [TÚ]: no resuelvas por Mai. Señala la línea del error, luego el concepto, luego un ejemplo análogo; nunca la solución.
8. Si algo requiere dinero, es irreversible o involucra a terceros: detente y escala a Mai.

## Comandos
Entorno: Debian 13 en la ThinkCentre; Python y dependencias gestionados con uv.
Instalar: uv sync
Pruebas: uv run pytest -q
Linter: uvx ruff check .
Correr: uv run jupyter nbconvert --to notebook --execute classification.ipynb --output /tmp/run.ipynb

## Convenciones
- Código, nombres y comentarios en inglés.
- docs/ y reports/ en español.
- Dependencias en pyproject.toml, fijadas por uv.lock; requirements.txt no es la fuente de verdad.
- Commits pequeños; tag pruebas-N al cerrar la fase A del Tester y tag iter-N al cerrar cada iteración.

## Estado actual
Expediente activo: exp/2026-09-30-auditoria
Iteración: 1
Nivel / modo: N3 / Guiado
