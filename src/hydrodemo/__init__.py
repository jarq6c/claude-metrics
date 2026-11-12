"""Unit hydrograph modeling and GLUE calibration with synthetic data.

``hydrodemo`` is a teaching package. It generates synthetic rainfall and
streamflow, simulates streamflow with a gamma distributed unit hydrograph,
calibrates the model with the Generalized Likelihood Uncertainty Estimation
(GLUE) method, and evaluates results with standard hydrological metrics.
"""

from importlib.metadata import version

__version__: str = version("hydrodemo")

__all__ = ["__version__"]
