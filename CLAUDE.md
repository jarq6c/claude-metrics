# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`hydrodemo` is a teaching Python package for rainfall-runoff modeling: synthetic
rainfall, synthetic observed streamflow, a gamma unit hydrograph model, GLUE
calibration, and evaluation metrics. The phased roadmap is in `PLAN.md`.

## Commands

Use `uv` for everything. Do not use `pip` directly.

```bash
uv sync --all-groups          # install package and dev/docs dependencies
uv run pytest                 # tests with coverage (fails under 90%)
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy                   # strict type check of src and tests
uv run mkdocs build --strict  # build docs
uv build                      # build sdist and wheel
```

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

- Before committing, run `ruff format`, `ruff check`, `mypy`, and `pytest`. All must pass.
- Write or update tests in the same change as the code they cover.
- Keep commits small and focused on one phase or feature.
- Update `PLAN.md` checkboxes when a phase is finished.
