# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`hydrodemo` is a teaching Python package for rainfall-runoff modeling: synthetic
rainfall, synthetic observed streamflow, a gamma unit hydrograph model, GLUE
calibration, and evaluation metrics. The phased roadmap is in `PLAN.md`.

## Commands

Use `pixi` for environments and tasks. Do not use `pip`, `uv`, or `ruff`
(the project avoids Astral tools). Tasks are defined in `pyproject.toml`
under `[tool.pixi.tasks]`.

```bash
pixi install            # create the environment from pixi.lock
pixi run format         # isort + black
pixi run format-check   # verify formatting without changing files
pixi run lint           # flake8 with bugbear, docstrings, and naming plugins
pixi run typecheck      # mypy --strict on src and tests
pixi run test           # pytest with coverage (fails under 90%)
pixi run check          # format-check, lint, typecheck, and test together
pixi run docs           # mkdocs build --strict
pixi run build          # python -m build, then twine check
```

To add a dependency, add it to the right `[tool.pixi...dependencies]` table
(conda-forge). Runtime dependencies also go in `[project].dependencies`.

## Code conventions

- Python 3.13 or newer. Use modern syntax: `list[float]`, `X | None`, `type` aliases.
- Spell out variable names fully: `rainfall_depth`, not `rd` or `p`. Loop indices
  such as `timestep_index` are preferred over `i`.
- Every public function, class, and module has a NumPy-style docstring with
  `Parameters`, `Returns`, and `Raises` sections where relevant. Include units
  (for example, millimeters per timestep).
- Full type hints everywhere. Code must pass `mypy --strict`. Use
  `numpy.typing.NDArray[np.float64]` for arrays.
- Validate inputs at public boundaries and raise `ValueError` with a clear message.
- Randomness takes a `random_seed: int | None` argument and uses
  `numpy.random.default_rng`. Never use global random state.
- Prefer pure functions and frozen dataclasses. No hidden module-level state.
- Dependencies are limited to NumPy and SciPy unless the plan says otherwise.

## Layout

- `src/hydrodemo/`: package source, one module per capability.
- `tests/`: one `test_<module>.py` per source module; shared fixtures in `conftest.py`.
- `docs/`: MkDocs pages. API pages are generated from docstrings with mkdocstrings.

## Workflow

- Before committing, run `pixi run format` and then `pixi run check`. All must pass.
- Write or update tests in the same change as the code they cover.
- Keep commits small and focused on one phase or feature.
- Update `PLAN.md` checkboxes when a phase is finished.
