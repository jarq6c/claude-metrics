"""Evaluation metrics for comparing simulated and observed streamflow.

Every metric takes ``simulated`` and ``observed`` series of equal length and
returns a single float. Inputs must be one-dimensional, non-empty, and
finite. Metrics that would divide by zero for a given input raise
``ValueError`` instead of returning ``nan`` or ``inf``.

The Kling-Gupta efficiency is available both as a single aggregate score
(:func:`kling_gupta_efficiency`) and as its separate components
(:func:`pearson_correlation`, :func:`variability_ratio`,
:func:`coefficient_of_variation_ratio`, and :func:`bias_ratio`).
:func:`kling_gupta_decomposition` returns the components and the aggregate
together.

All standard deviations are population standard deviations (divisor ``n``),
following Gupta et al. (2009).
"""

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

type KlingGuptaVariant = Literal["2009", "2012"]
"""Version of the Kling-Gupta efficiency: Gupta et al. (2009) or Kling et al. (2012)."""

_KLING_GUPTA_VARIANTS: tuple[str, ...] = ("2009", "2012")


@dataclass(frozen=True)
class KlingGuptaDecomposition:
    """Kling-Gupta efficiency and the components it is computed from.

    Attributes
    ----------
    variant : {"2009", "2012"}
        Version of the efficiency. ``"2009"`` uses the variability ratio
        (alpha) of Gupta et al. (2009). ``"2012"`` uses the coefficient of
        variation ratio (gamma) of Kling et al. (2012).
    correlation : float
        Pearson correlation coefficient between simulated and observed
        series (r). Dimensionless, best value 1.
    variability : float
        Variability component. The ratio of standard deviations (alpha) for
        the 2009 variant, or the ratio of coefficients of variation (gamma)
        for the 2012 variant. Dimensionless, best value 1.
    bias : float
        Ratio of simulated mean to observed mean (beta). Dimensionless, best
        value 1.
    efficiency : float
        Aggregate Kling-Gupta efficiency. Dimensionless, best value 1.
    """

    variant: KlingGuptaVariant
    correlation: float
    variability: float
    bias: float
    efficiency: float


def _validate_series(
    simulated: ArrayLike, observed: ArrayLike
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Convert inputs to float arrays and check that they can be compared.

    Parameters
    ----------
    simulated : array_like
        Simulated values.
    observed : array_like
        Observed values.

    Returns
    -------
    tuple of numpy.ndarray
        The simulated and observed values as one-dimensional float64 arrays.

    Raises
    ------
    ValueError
        If either input is not one-dimensional, the inputs differ in length,
        the inputs are empty, or any value is not finite.
    """
    simulated_array = np.asarray(simulated, dtype=np.float64)
    observed_array = np.asarray(observed, dtype=np.float64)
    if simulated_array.ndim != 1 or observed_array.ndim != 1:
        raise ValueError("simulated and observed must be one-dimensional.")
    if simulated_array.shape != observed_array.shape:
        raise ValueError(
            "simulated and observed must have the same length, got "
            f"{simulated_array.size} and {observed_array.size}."
        )
    if simulated_array.size == 0:
        raise ValueError("simulated and observed must not be empty.")
    if not (np.all(np.isfinite(simulated_array)) and np.all(np.isfinite(observed_array))):
        raise ValueError("simulated and observed must contain only finite values.")
    return simulated_array, observed_array


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
        Nash-Sutcliffe efficiency. Dimensionless, ranging from negative
        infinity to 1. A value of 1 is a perfect fit, and 0 means the
        simulation is no better than the mean of the observations.

    Raises
    ------
    ValueError
        If the inputs fail validation or the observations are constant.

    Notes
    -----
    ``NSE = 1 - sum((simulated - observed)**2) / sum((observed - mean(observed))**2)``

    Because errors are squared, NSE is most sensitive to errors at high
    flows.

    References
    ----------
    .. [1] Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting
       through conceptual models part I: A discussion of principles.
       *Journal of Hydrology, 10*(3), 282-290.
       https://doi.org/10.1016/0022-1694(70)90255-6
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    sum_of_squared_errors = float(np.sum((simulated_array - observed_array) ** 2))
    sum_of_squared_deviations = float(np.sum((observed_array - observed_array.mean()) ** 2))
    if sum_of_squared_deviations == 0.0:
        raise ValueError("NSE is undefined when the observations are constant.")
    return 1.0 - sum_of_squared_errors / sum_of_squared_deviations


def log_nash_sutcliffe_efficiency(
    simulated: ArrayLike, observed: ArrayLike, offset: float | None = None
) -> float:
    """Compute the Nash-Sutcliffe efficiency of log-transformed flows.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.
    offset : float or None, optional
        Value added to both series before taking the natural logarithm, in
        the same unit as the flows. It prevents taking the logarithm of zero.
        Must be zero or greater. If None (the default), the offset is 1% of
        the mean observed flow, as recommended by Pushpalatha et al. (2012).

    Returns
    -------
    float
        Log Nash-Sutcliffe efficiency. Dimensionless, ranging from negative
        infinity to 1, with 1 a perfect fit.

    Raises
    ------
    ValueError
        If the inputs fail validation, ``offset`` is negative, any shifted
        value is not positive, or the shifted observations are constant.

    Notes
    -----
    ``logNSE = NSE(log(simulated + offset), log(observed + offset))``

    The logarithm compresses high flows, so this metric emphasizes the fit
    at low flows.

    References
    ----------
    .. [1] Krause, P., Boyle, D. P., & Bäse, F. (2005). Comparison of
       different efficiency criteria for hydrological model assessment.
       *Advances in Geosciences, 5*, 89-97.
       https://doi.org/10.5194/adgeo-5-89-2005
    .. [2] Pushpalatha, R., Perrin, C., Le Moine, N., & Andréassian, V.
       (2012). A review of efficiency criteria suitable for evaluating
       low-flow simulations. *Journal of Hydrology, 420-421*, 171-182.
       https://doi.org/10.1016/j.jhydrol.2011.11.055
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    if offset is None:
        offset = float(observed_array.mean()) / 100.0
    elif offset < 0.0:
        raise ValueError(f"offset must be zero or greater, got {offset}.")
    shifted_simulated = simulated_array + offset
    shifted_observed = observed_array + offset
    if np.any(shifted_simulated <= 0.0) or np.any(shifted_observed <= 0.0):
        raise ValueError(
            "All values plus the offset must be positive to take the logarithm. "
            "Use a larger offset or check for negative flows."
        )
    return nash_sutcliffe_efficiency(np.log(shifted_simulated), np.log(shifted_observed))


def root_mean_squared_error(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the root mean squared error (RMSE).

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Root mean squared error, in the same unit as the flows. Ranges from
        0 to infinity, with 0 a perfect fit.

    Raises
    ------
    ValueError
        If the inputs fail validation.

    Notes
    -----
    ``RMSE = sqrt(mean((simulated - observed)**2))``

    References
    ----------
    .. [1] Legates, D. R., & McCabe, G. J., Jr. (1999). Evaluating the use
       of "goodness-of-fit" measures in hydrologic and hydroclimatic model
       validation. *Water Resources Research, 35*(1), 233-241.
       https://doi.org/10.1029/1998WR900018
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    return math.sqrt(float(np.mean((simulated_array - observed_array) ** 2)))


def percent_bias(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the percent bias (PBIAS) of simulated total volume.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Percent bias, in percent. Positive values mean the simulation
        overestimates total volume, and negative values mean it
        underestimates. The best value is 0.

    Raises
    ------
    ValueError
        If the inputs fail validation or the observations sum to zero.

    Notes
    -----
    ``PBIAS = 100 * sum(simulated - observed) / sum(observed)``

    Sign conventions differ in the literature. Gupta et al. (1999) define
    percent bias as ``observed - simulated``, so their positive values mean
    underestimation. This function uses ``simulated - observed`` so that the
    sign matches the direction of the error.

    References
    ----------
    .. [1] Gupta, H. V., Sorooshian, S., & Yapo, P. O. (1999). Status of
       automatic calibration for hydrologic models: Comparison with
       multilevel expert calibration. *Journal of Hydrologic Engineering,
       4*(2), 135-143. https://doi.org/10.1061/(ASCE)1084-0699(1999)4:2(135)
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    observed_total = float(np.sum(observed_array))
    if observed_total == 0.0:
        raise ValueError("Percent bias is undefined when the observations sum to zero.")
    return 100.0 * float(np.sum(simulated_array - observed_array)) / observed_total


def pearson_correlation(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the Pearson correlation coefficient (r).

    This is the correlation component of the Kling-Gupta efficiency.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Pearson correlation coefficient. Dimensionless, ranging from -1 to
        1, with 1 the best value. It measures how well the timing and shape
        of the simulated series match the observations.

    Raises
    ------
    ValueError
        If the inputs fail validation or either series is constant.

    References
    ----------
    .. [1] Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).
       Decomposition of the mean squared error and NSE performance criteria:
       Implications for improving hydrological modelling. *Journal of
       Hydrology, 377*(1-2), 80-91.
       https://doi.org/10.1016/j.jhydrol.2009.08.003
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    simulated_deviations = simulated_array - simulated_array.mean()
    observed_deviations = observed_array - observed_array.mean()
    denominator = math.sqrt(
        float(np.sum(simulated_deviations**2)) * float(np.sum(observed_deviations**2))
    )
    if denominator == 0.0:
        raise ValueError("Correlation is undefined when either series is constant.")
    return float(np.sum(simulated_deviations * observed_deviations)) / denominator


def variability_ratio(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the ratio of simulated to observed standard deviation (alpha).

    This is the variability component of the 2009 Kling-Gupta efficiency.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Variability ratio. Dimensionless, ranging from 0 to infinity, with 1
        the best value. Values above 1 mean the simulation varies more than
        the observations.

    Raises
    ------
    ValueError
        If the inputs fail validation or the observations are constant.

    Notes
    -----
    ``alpha = std(simulated) / std(observed)``

    References
    ----------
    .. [1] Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).
       Decomposition of the mean squared error and NSE performance criteria:
       Implications for improving hydrological modelling. *Journal of
       Hydrology, 377*(1-2), 80-91.
       https://doi.org/10.1016/j.jhydrol.2009.08.003
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    observed_standard_deviation = float(np.std(observed_array))
    if observed_standard_deviation == 0.0:
        raise ValueError("Variability ratio is undefined when the observations are constant.")
    return float(np.std(simulated_array)) / observed_standard_deviation


def bias_ratio(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the ratio of simulated to observed mean (beta).

    This is the bias component of the Kling-Gupta efficiency.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Bias ratio. Dimensionless, with 1 the best value. Values above 1
        mean the simulation overestimates the mean flow.

    Raises
    ------
    ValueError
        If the inputs fail validation or the observed mean is zero.

    Notes
    -----
    ``beta = mean(simulated) / mean(observed)``

    References
    ----------
    .. [1] Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).
       Decomposition of the mean squared error and NSE performance criteria:
       Implications for improving hydrological modelling. *Journal of
       Hydrology, 377*(1-2), 80-91.
       https://doi.org/10.1016/j.jhydrol.2009.08.003
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    observed_mean = float(observed_array.mean())
    if observed_mean == 0.0:
        raise ValueError("Bias ratio is undefined when the observed mean is zero.")
    return float(simulated_array.mean()) / observed_mean


def coefficient_of_variation_ratio(simulated: ArrayLike, observed: ArrayLike) -> float:
    """Compute the ratio of simulated to observed coefficient of variation (gamma).

    This is the variability component of the 2012 Kling-Gupta efficiency.
    Unlike the variability ratio (alpha), it is not affected by bias, so the
    variability and bias components are not cross-correlated.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.

    Returns
    -------
    float
        Coefficient of variation ratio. Dimensionless, with 1 the best value.

    Raises
    ------
    ValueError
        If the inputs fail validation, either mean is zero, or the
        observations are constant.

    Notes
    -----
    ``gamma = (std(simulated) / mean(simulated)) / (std(observed) / mean(observed))``

    This equals ``alpha / beta``.

    References
    ----------
    .. [1] Kling, H., Fuchs, M., & Paulin, M. (2012). Runoff conditions in
       the upper Danube basin under an ensemble of climate change scenarios.
       *Journal of Hydrology, 424-425*, 264-277.
       https://doi.org/10.1016/j.jhydrol.2012.01.011
    """
    simulated_array, observed_array = _validate_series(simulated, observed)
    simulated_mean = float(simulated_array.mean())
    observed_mean = float(observed_array.mean())
    if simulated_mean == 0.0 or observed_mean == 0.0:
        raise ValueError("Coefficient of variation ratio is undefined when either mean is zero.")
    observed_coefficient_of_variation = float(np.std(observed_array)) / observed_mean
    if observed_coefficient_of_variation == 0.0:
        raise ValueError(
            "Coefficient of variation ratio is undefined when the observations are constant."
        )
    simulated_coefficient_of_variation = float(np.std(simulated_array)) / simulated_mean
    return simulated_coefficient_of_variation / observed_coefficient_of_variation


def kling_gupta_decomposition(
    simulated: ArrayLike, observed: ArrayLike, variant: KlingGuptaVariant = "2009"
) -> KlingGuptaDecomposition:
    """Compute the Kling-Gupta efficiency together with its components.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.
    variant : {"2009", "2012"}, optional
        Version of the efficiency. ``"2009"`` (the default) uses the
        variability ratio (alpha) of Gupta et al. (2009). ``"2012"`` uses the
        coefficient of variation ratio (gamma) of Kling et al. (2012).

    Returns
    -------
    KlingGuptaDecomposition
        The correlation, variability, and bias components and the aggregate
        efficiency.

    Raises
    ------
    ValueError
        If the inputs fail validation, ``variant`` is not recognized, or any
        component is undefined for the inputs.

    See Also
    --------
    pearson_correlation, variability_ratio, coefficient_of_variation_ratio,
    bias_ratio, kling_gupta_efficiency

    Notes
    -----
    ``KGE = 1 - sqrt((r - 1)**2 + (variability - 1)**2 + (beta - 1)**2)``

    The efficiency is the Euclidean distance from the ideal point where all
    three components equal 1, subtracted from 1.

    References
    ----------
    .. [1] Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).
       Decomposition of the mean squared error and NSE performance criteria:
       Implications for improving hydrological modelling. *Journal of
       Hydrology, 377*(1-2), 80-91.
       https://doi.org/10.1016/j.jhydrol.2009.08.003
    .. [2] Kling, H., Fuchs, M., & Paulin, M. (2012). Runoff conditions in
       the upper Danube basin under an ensemble of climate change scenarios.
       *Journal of Hydrology, 424-425*, 264-277.
       https://doi.org/10.1016/j.jhydrol.2012.01.011
    """
    if variant not in _KLING_GUPTA_VARIANTS:
        raise ValueError(f"variant must be one of {_KLING_GUPTA_VARIANTS}, got {variant!r}.")
    correlation = pearson_correlation(simulated, observed)
    if variant == "2009":
        variability = variability_ratio(simulated, observed)
    else:
        variability = coefficient_of_variation_ratio(simulated, observed)
    bias = bias_ratio(simulated, observed)
    efficiency = 1.0 - math.sqrt(
        (correlation - 1.0) ** 2 + (variability - 1.0) ** 2 + (bias - 1.0) ** 2
    )
    return KlingGuptaDecomposition(
        variant=variant,
        correlation=correlation,
        variability=variability,
        bias=bias,
        efficiency=efficiency,
    )


def kling_gupta_efficiency(
    simulated: ArrayLike, observed: ArrayLike, variant: KlingGuptaVariant = "2009"
) -> float:
    """Compute the Kling-Gupta efficiency (KGE).

    Use :func:`kling_gupta_decomposition` to get the components alongside
    the aggregate value.

    Parameters
    ----------
    simulated : array_like
        Simulated streamflow, in any flow unit.
    observed : array_like
        Observed streamflow, in the same unit as ``simulated``.
    variant : {"2009", "2012"}, optional
        Version of the efficiency. ``"2009"`` (the default) uses the
        variability ratio (alpha) of Gupta et al. (2009). ``"2012"`` uses the
        coefficient of variation ratio (gamma) of Kling et al. (2012).

    Returns
    -------
    float
        Kling-Gupta efficiency. Dimensionless, ranging from negative infinity
        to 1, with 1 a perfect fit.

    Raises
    ------
    ValueError
        If the inputs fail validation, ``variant`` is not recognized, or any
        component is undefined for the inputs.

    See Also
    --------
    kling_gupta_decomposition

    Notes
    -----
    ``KGE = 1 - sqrt((r - 1)**2 + (variability - 1)**2 + (beta - 1)**2)``

    References
    ----------
    .. [1] Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).
       Decomposition of the mean squared error and NSE performance criteria:
       Implications for improving hydrological modelling. *Journal of
       Hydrology, 377*(1-2), 80-91.
       https://doi.org/10.1016/j.jhydrol.2009.08.003
    .. [2] Kling, H., Fuchs, M., & Paulin, M. (2012). Runoff conditions in
       the upper Danube basin under an ensemble of climate change scenarios.
       *Journal of Hydrology, 424-425*, 264-277.
       https://doi.org/10.1016/j.jhydrol.2012.01.011
    """
    return kling_gupta_decomposition(simulated, observed, variant=variant).efficiency
