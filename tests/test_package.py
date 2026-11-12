"""Smoke tests for package metadata."""

import hydrodemo


def test_version_is_a_nonempty_string() -> None:
    assert isinstance(hydrodemo.__version__, str)
    assert hydrodemo.__version__ != ""
