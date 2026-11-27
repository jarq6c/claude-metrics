"""Example package for the Claude Code Python project template.

The package exists to show how a requirement in ``SPEC.md`` becomes tested
code written to the conventions in ``STYLE.md``.
"""

from importlib.metadata import version

__version__: str = version("example_package")

__all__ = ["__version__"]
