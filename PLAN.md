# Project plan: hydrodemo

A demonstration hydrological modeling package, built to practice using Claude
Code as a development assistant.

## Goals

- A PyPI-compatible Python package with documentation.
- Synthetic rainfall forcing and synthetic observed streamflow.
- A unit hydrograph model with gamma distributed ordinates.
- GLUE-based calibration.
- Standard evaluation metrics.
- Pytest test suite, docstrings, full type hints, fully spelled out names, Python 3.13.

## Modules

| Module | Contents |
|---|---|
| `parameters.py` | Frozen dataclasses for model parameters and sampling bounds, with validation. |
| `forcing.py` | Synthetic rainfall: random storm occurrence, exponential or gamma storm depths, optional seasonal cycle. |
| `model.py` | Gamma unit hydrograph ordinates (normalized to sum to 1); streamflow by convolving effective rainfall with the unit hydrograph, plus baseflow. |
| `observations.py` | Synthetic observed streamflow from known "true" parameters with multiplicative AR(1) noise, clipped at zero. |
| `metrics.py` | NSE, KGE, RMSE, percent bias, log NSE, with input validation. |
| `calibration.py` | GLUE: uniform or Latin hypercube sampling, likelihood metric, behavioral threshold, normalized weights, weighted prediction bounds, `GlueResult` dataclass. |

## Testing strategy

- Known-answer tests (for example, a perfect simulation gives NSE = 1).
- Property tests (unit hydrograph sums to 1; mass balance of runoff).
- Reproducibility with fixed random seeds.
- Parameter recovery: GLUE behavioral set contains the true parameters.
- Error handling: invalid inputs raise `ValueError`.
- Coverage of at least 90%, enforced by pytest-cov.

## Phases

| Phase | Work | Claude Code practice | Status |
|---|---|---|---|
| 0 | Scaffolding: `pyproject.toml`, `CLAUDE.md`, ruff, mypy, pytest, docs skeleton, CI | Writing project rules in `CLAUDE.md` | [x] |
| 1 | `metrics.py` and tests | Test-driven development | [ ] |
| 2 | `parameters.py`, `forcing.py` | Plan mode: review the design before code | [ ] |
| 3 | `model.py` | Asking for evidence (passing mass balance test) | [ ] |
| 4 | `observations.py` | Small, focused commits and PRs per phase | [ ] |
| 5 | `calibration.py` | `/code-review` and `/simplify` on a larger change | [ ] |
| 6 | Docs pages, end-to-end example, docs build in CI | Generating docs from docstrings; running examples | [ ] |
| 7 | `uv build`, `twine check`, optional TestPyPI upload | Confirming before outward-facing actions | [ ] |

## Habits to practice

- Keep project rules in `CLAUDE.md` rather than repeating them in prompts.
- Give Claude a way to verify its work: tests, linters, type checker.
- Start a fresh session or `/clear` between phases to keep context small.
- Review diffs before each commit; open one PR per phase.
