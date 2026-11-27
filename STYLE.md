# STYLE.md

How code, tests, configuration, and documentation are written in this project.
Read this file in full before changing any of them. `CLAUDE.md` covers the
workflow; `SPEC.md` covers requirements.

## Python version and syntax

- Target Python 3.13 or newer.
- Use modern syntax: built-in generics (`list[float]`), `X | None` instead of
  `Optional[X]`, and the `type` statement for aliases.

## Naming

- Spell out names in full: `rainfall_depth`, not `rd`, `p`, or `depth_mm`.
- This includes loop variables and indices: `timestep_index`, not `i`.
- Common abbreviations that are clearer than the long form are allowed when
  they are standard in the field, such as `id`, `url`, or `rng` (the NumPy
  convention for a random number generator).
- Modules and functions use `snake_case`, classes use `PascalCase`, and
  constants use `UPPER_SNAKE_CASE`.

## Docstrings

Every public module, class, and function has a NumPy-style docstring.

- Include `Parameters`, `Returns`, and `Raises` sections where they apply.
- State units for every physical quantity, for example "millimeters per hour".
- Add a `Notes` section for formulas or behavior a caller could not guess.
- Add a `References` section with APA 7 citations, including DOIs, whenever a
  method comes from the literature.

```python
def nash_sutcliffe_efficiency(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the Nash-Sutcliffe efficiency (NSE).

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Dimensionless efficiency, from negative infinity to 1.

    Raises
    ------
    ValueError
        If the observations are constant.

    References
    ----------
    .. [1] Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting
       through conceptual models part I — A discussion of principles.
       *Journal of Hydrology, 10*(3), 282-290.
       https://doi.org/10.1016/0022-1694(70)90255-6
    """
```

## Type hints

- Annotate every function, method, and module-level variable, including tests.
- Code must pass `mypy --strict`.
- Use `numpy.typing.NDArray[np.float64]` for arrays and `ArrayLike` for inputs
  that accept any array-like value.
- When several functions share a call signature, name it with a `Protocol` or
  a `type` alias instead of repeating `Callable[..., float]`.
- Avoid `Any` and `# type: ignore`. When one is unavoidable, add the specific
  error code and a comment explaining why.

## Errors and validation

- Validate inputs at public boundaries and raise `ValueError` with a message
  that names the argument and the problem.
- Raise instead of returning `nan` or `inf` when a result is undefined, unless
  `SPEC.md` says otherwise.
- Do not validate again inside private helpers that only receive checked data.

## Randomness

- Any function that uses randomness takes an optional generator,
  `rng: numpy.random.Generator | None = None`, and draws every random value from it.
- When `rng` is `None`, create one with `numpy.random.default_rng()`.
- Callers control reproducibility by creating the generator themselves, for
  example `numpy.random.default_rng(42)`, and passing it in. Passing one
  generator through a sequence of calls keeps their random streams independent.
- Never use global random state such as `numpy.random.seed` or the `random` module.

```python
def generate_rainfall(
    number_of_timesteps: int, rng: np.random.Generator | None = None
) -> NDArray[np.float64]:
    """..."""
    if rng is None:
        rng = np.random.default_rng()
    return rng.exponential(scale=2.0, size=number_of_timesteps)
```

## Design

- Prefer pure functions that return new values over functions that modify their inputs.
- Use frozen dataclasses (`@dataclass(frozen=True)`) for structured data.
- No hidden module-level state. Module-level constants are fine.
- Keep public interfaces small. Prefix private helpers with an underscore.

## Project layout

```text
pyproject.toml          # package metadata, pixi workspace, and tool settings
pixi.lock               # committed lock file
src/<package>/
    __init__.py
    py.typed            # marks the package as typed
    <module>.py         # one module per capability
tests/
    conftest.py         # shared fixtures
    test_<module>.py    # one test module per source module
docs/                   # documentation pages
mkdocs.yml              # documentation configuration
```

## Tooling

Tools are named here without pinned versions. Each project's `pixi.lock`
records the exact versions in use.

| Purpose | Tool |
|---|---|
| Environments and tasks | pixi, with packages from conda-forge |
| Build backend | hatchling |
| Formatting | black, line length 99 |
| Import sorting | isort, with `profile = "black"` and line length 99 |
| Linting | flake8, with flake8-bugbear, flake8-docstrings, and pep8-naming |
| Type checking | mypy, strict mode |
| Testing | pytest, with pytest-cov |
| Documentation | Zensical, with mkdocstrings |
| Packaging checks | python-build and twine |

Do not use Astral tools (uv, ruff) or install packages with `pip` directly.
Add dependencies through pixi, and also list runtime dependencies in
`[project].dependencies` so the published package declares them.

## Checks

Each project defines these pixi tasks in `pyproject.toml`:

| Task | Runs |
|---|---|
| `pixi run format` | isort, then black, on `src` and `tests` |
| `pixi run lint` | flake8 |
| `pixi run typecheck` | mypy on `src` and `tests` |
| `pixi run test` | pytest with coverage |
| `pixi run check` | format check, lint, type check, and tests together |
| `pixi run docs` | Zensical build in strict mode |
| `pixi run build` | python-build, then `twine check` |

Before each commit, run `pixi run format` and then `pixi run check`. All must pass.
Formatters run on `src` and `tests` only, never on the whole repository, so
they cannot touch the pixi environment in `.pixi/`.

## Tests

- Use pytest. Put shared data in fixtures in `tests/conftest.py`.
- A test that checks a specific number carries its own inputs and expected
  value through `pytest.mark.parametrize`, with a comment showing the
  arithmetic. It must not depend on shared fixture data that could change.
- Use fixtures for property tests, which check relationships that hold for any
  valid input, such as scaling or symmetry.
- Test error paths: every `ValueError` a public function can raise has a test,
  using `pytest.raises(..., match=...)`.
- Keep coverage at 90% or higher. pytest-cov enforces this floor.
- In tests of random behavior, pass a generator created from a fixed seed,
  such as `numpy.random.default_rng(12345)`.

## Documentation

- Build documentation with Zensical from `mkdocs.yml`.
- Generate API pages from docstrings with mkdocstrings. Do not copy docstring
  content into hand-written pages.
- Update documentation in the same PR as the code it describes.

## Git

- Commit message rules are in `CLAUDE.md`.
- Commit `pixi.lock`. Never commit `.pixi/`, build output, caches, or `HANDOFF.md`.
