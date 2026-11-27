"""Smoke tests for the installed package."""

import example_package


def test_version_is_a_nonempty_string() -> None:
    assert isinstance(example_package.__version__, str)
    assert example_package.__version__ != ""
