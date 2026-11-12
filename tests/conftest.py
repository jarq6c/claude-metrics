"""Shared pytest fixtures."""

import numpy as np
import pytest
from numpy.typing import NDArray


@pytest.fixture
def observed_streamflow() -> NDArray[np.float64]:
    """Return a short, positive, non-constant observed streamflow series."""
    return np.array([1.0, 3.0, 2.0, 5.0, 4.0])


@pytest.fixture
def simulated_streamflow() -> NDArray[np.float64]:
    """Return an imperfect simulation of ``observed_streamflow``."""
    return np.array([2.0, 3.0, 2.0, 4.0, 4.0])
