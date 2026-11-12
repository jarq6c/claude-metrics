"""Tests for hydrodemo.metrics.

Known-value tests list their own inputs and expected results with
``pytest.mark.parametrize``, so each case is self-contained. Property tests
use the ``observed_streamflow`` and ``simulated_streamflow`` fixtures from
``conftest.py`` and check relationships that hold for any valid series.
"""

import math

import numpy as np
import pytest
from numpy.typing import NDArray

from hydrodemo import metrics
from hydrodemo.metrics import MetricFunction

type FloatArray = NDArray[np.float64]

ALL_METRICS: list[MetricFunction] = [
    metrics.nash_sutcliffe_efficiency,
    metrics.log_nash_sutcliffe_efficiency,
    metrics.root_mean_squared_error,
    metrics.percent_bias,
    metrics.pearson_correlation,
    metrics.variability_ratio,
    metrics.bias_ratio,
    metrics.coefficient_of_variation_ratio,
    metrics.kling_gupta_efficiency,
]


# ---------------------------------------------------------------------------
# Input validation (shared by all metrics)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_mismatched_lengths_raise(metric_function: MetricFunction) -> None:
    with pytest.raises(ValueError, match="same length"):
        metric_function(simulated=[1.0, 2.0], observed=[1.0, 2.0, 3.0])


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_empty_input_raises(metric_function: MetricFunction) -> None:
    with pytest.raises(ValueError, match="empty"):
        metric_function(simulated=[], observed=[])


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_nonfinite_input_raises(metric_function: MetricFunction) -> None:
    with pytest.raises(ValueError, match="finite"):
        metric_function(simulated=[1.0, np.nan, 3.0], observed=[1.0, 2.0, 3.0])


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_multidimensional_input_raises(metric_function: MetricFunction) -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        metric_function(simulated=[[1.0, 2.0]], observed=[[1.0, 2.0]])


# ---------------------------------------------------------------------------
# Nash-Sutcliffe efficiency
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("simulated", "observed", "expected"),
    [
        pytest.param([1.0, 3.0, 2.0], [1.0, 3.0, 2.0], 1.0, id="perfect"),
        pytest.param([2.0, 2.0, 2.0], [1.0, 2.0, 3.0], 0.0, id="observed-mean"),
        # Sum of squared errors = 2; squared deviations from the mean of 3 sum to 10.
        pytest.param([2.0, 3.0, 2.0, 4.0, 4.0], [1.0, 3.0, 2.0, 5.0, 4.0], 0.8, id="imperfect"),
        # Sum of squared errors = 8; squared deviations from the mean of 2 sum to 2.
        pytest.param([3.0, 2.0, 1.0], [1.0, 2.0, 3.0], -3.0, id="reversed"),
    ],
)
def test_nse_known_values(simulated: list[float], observed: list[float], expected: float) -> None:
    assert metrics.nash_sutcliffe_efficiency(simulated, observed) == pytest.approx(expected)


def test_nse_constant_observations_raise() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.nash_sutcliffe_efficiency([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])


# ---------------------------------------------------------------------------
# Log Nash-Sutcliffe efficiency
# ---------------------------------------------------------------------------


def test_log_nse_perfect_simulation_is_one(observed_streamflow: FloatArray) -> None:
    result = metrics.log_nash_sutcliffe_efficiency(observed_streamflow, observed_streamflow)
    assert result == pytest.approx(1.0)


def test_log_nse_matches_nse_of_transformed_series(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    offset = 0.5
    expected = metrics.nash_sutcliffe_efficiency(
        np.log(simulated_streamflow + offset), np.log(observed_streamflow + offset)
    )
    result = metrics.log_nash_sutcliffe_efficiency(
        simulated_streamflow, observed_streamflow, offset=offset
    )
    assert result == pytest.approx(expected)


def test_log_nse_default_offset_is_one_percent_of_observed_mean(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    default_offset = observed_streamflow.mean() / 100.0
    expected = metrics.log_nash_sutcliffe_efficiency(
        simulated_streamflow, observed_streamflow, offset=default_offset
    )
    result = metrics.log_nash_sutcliffe_efficiency(simulated_streamflow, observed_streamflow)
    assert result == pytest.approx(expected)


def test_log_nse_handles_zero_flows_with_default_offset() -> None:
    observed = [0.0, 1.0, 2.0, 3.0]
    simulated = [0.0, 1.0, 2.0, 2.5]
    assert math.isfinite(metrics.log_nash_sutcliffe_efficiency(simulated, observed))


def test_log_nse_nonpositive_shifted_values_raise() -> None:
    with pytest.raises(ValueError, match="positive"):
        metrics.log_nash_sutcliffe_efficiency([-1.0, 2.0, 3.0], [1.0, 2.0, 3.0], offset=0.5)


def test_log_nse_negative_offset_raises(observed_streamflow: FloatArray) -> None:
    with pytest.raises(ValueError, match="offset"):
        metrics.log_nash_sutcliffe_efficiency(
            observed_streamflow, observed_streamflow, offset=-1.0
        )


# ---------------------------------------------------------------------------
# Root mean squared error
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("simulated", "observed", "expected"),
    [
        pytest.param([1.0, 3.0, 2.0], [1.0, 3.0, 2.0], 0.0, id="perfect"),
        pytest.param([3.0, 3.0], [1.0, 1.0], 2.0, id="constant-offset"),
        # Squared errors are 1, 1, 1, 1, 4, so the mean squared error is 1.6.
        pytest.param(
            [2.0, 2.0, 3.0, 4.0, 6.0],
            [1.0, 3.0, 2.0, 5.0, 4.0],
            math.sqrt(1.6),
            id="mixed-errors",
        ),
    ],
)
def test_rmse_known_values(simulated: list[float], observed: list[float], expected: float) -> None:
    assert metrics.root_mean_squared_error(simulated, observed) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Percent bias
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("simulated", "observed", "expected"),
    [
        pytest.param([1.0, 3.0, 2.0], [1.0, 3.0, 2.0], 0.0, id="perfect"),
        pytest.param([1.1, 2.2, 3.3], [1.0, 2.0, 3.0], 10.0, id="overestimate"),
        pytest.param([0.8, 1.6, 2.4], [1.0, 2.0, 3.0], -20.0, id="underestimate"),
        # An ephemeral stream: zero flow at some timesteps is fine.
        pytest.param([0.0, 0.0, 3.0, 2.0], [0.0, 1.0, 2.0, 1.0], 25.0, id="ephemeral"),
    ],
)
def test_percent_bias_known_values(
    simulated: list[float], observed: list[float], expected: float
) -> None:
    assert metrics.percent_bias(simulated, observed) == pytest.approx(expected)


def test_percent_bias_all_zero_observations_raise() -> None:
    # With no observed flow at any timestep, there is no volume to compare against.
    with pytest.raises(ValueError, match="sum"):
        metrics.percent_bias([0.5, 0.0, 0.0], [0.0, 0.0, 0.0])


# ---------------------------------------------------------------------------
# Kling-Gupta efficiency components
# ---------------------------------------------------------------------------


def test_pearson_correlation_matches_numpy(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    expected = np.corrcoef(simulated_streamflow, observed_streamflow)[0, 1]
    result = metrics.pearson_correlation(simulated_streamflow, observed_streamflow)
    assert result == pytest.approx(expected)


def test_pearson_correlation_of_negated_series_is_minus_one(
    observed_streamflow: FloatArray,
) -> None:
    result = metrics.pearson_correlation(-observed_streamflow, observed_streamflow)
    assert result == pytest.approx(-1.0)


def test_pearson_correlation_constant_series_raises() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.pearson_correlation([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])


@pytest.mark.parametrize("scale_factor", [0.5, 1.0, 2.0])
def test_variability_ratio_of_scaled_series(
    observed_streamflow: FloatArray, scale_factor: float
) -> None:
    result = metrics.variability_ratio(observed_streamflow * scale_factor, observed_streamflow)
    assert result == pytest.approx(scale_factor)


def test_variability_ratio_ignores_offset(observed_streamflow: FloatArray) -> None:
    result = metrics.variability_ratio(observed_streamflow + 10.0, observed_streamflow)
    assert result == pytest.approx(1.0)


def test_variability_ratio_constant_observations_raise() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.variability_ratio([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])


@pytest.mark.parametrize("scale_factor", [0.5, 1.0, 1.5])
def test_bias_ratio_of_scaled_series(observed_streamflow: FloatArray, scale_factor: float) -> None:
    result = metrics.bias_ratio(observed_streamflow * scale_factor, observed_streamflow)
    assert result == pytest.approx(scale_factor)


def test_bias_ratio_all_zero_observations_raise() -> None:
    with pytest.raises(ValueError, match="mean"):
        metrics.bias_ratio([1.0, 2.0], [0.0, 0.0])


@pytest.mark.parametrize("scale_factor", [0.5, 1.0, 3.0])
def test_coefficient_of_variation_ratio_is_unaffected_by_scaling(
    observed_streamflow: FloatArray, scale_factor: float
) -> None:
    result = metrics.coefficient_of_variation_ratio(
        observed_streamflow * scale_factor, observed_streamflow
    )
    assert result == pytest.approx(1.0)


def test_coefficient_of_variation_ratio_equals_alpha_over_beta(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    alpha = metrics.variability_ratio(simulated_streamflow, observed_streamflow)
    beta = metrics.bias_ratio(simulated_streamflow, observed_streamflow)
    result = metrics.coefficient_of_variation_ratio(simulated_streamflow, observed_streamflow)
    assert result == pytest.approx(alpha / beta)


def test_coefficient_of_variation_ratio_all_zero_simulation_raises() -> None:
    with pytest.raises(ValueError, match="mean"):
        metrics.coefficient_of_variation_ratio([0.0, 0.0], [1.0, 2.0])


def test_coefficient_of_variation_ratio_constant_observations_raise() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.coefficient_of_variation_ratio([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])


# ---------------------------------------------------------------------------
# Kling-Gupta efficiency and decomposition
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("variant", ["2009", "2012"])
def test_kge_perfect_simulation_is_one(
    observed_streamflow: FloatArray, variant: metrics.KlingGuptaVariant
) -> None:
    result = metrics.kling_gupta_efficiency(
        observed_streamflow, observed_streamflow, variant=variant
    )
    assert result == pytest.approx(1.0)


def test_kge_2009_from_components(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    correlation = metrics.pearson_correlation(simulated_streamflow, observed_streamflow)
    alpha = metrics.variability_ratio(simulated_streamflow, observed_streamflow)
    beta = metrics.bias_ratio(simulated_streamflow, observed_streamflow)
    expected = 1.0 - math.sqrt((correlation - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    result = metrics.kling_gupta_efficiency(simulated_streamflow, observed_streamflow)
    assert result == pytest.approx(expected)


def test_kge_2012_from_components(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    correlation = metrics.pearson_correlation(simulated_streamflow, observed_streamflow)
    gamma = metrics.coefficient_of_variation_ratio(simulated_streamflow, observed_streamflow)
    beta = metrics.bias_ratio(simulated_streamflow, observed_streamflow)
    expected = 1.0 - math.sqrt((correlation - 1) ** 2 + (gamma - 1) ** 2 + (beta - 1) ** 2)
    result = metrics.kling_gupta_efficiency(
        simulated_streamflow, observed_streamflow, variant="2012"
    )
    assert result == pytest.approx(expected)


def test_kge_variants_differ_when_bias_is_present(observed_streamflow: FloatArray) -> None:
    simulated = observed_streamflow * 2.0
    kge_2009 = metrics.kling_gupta_efficiency(simulated, observed_streamflow, variant="2009")
    kge_2012 = metrics.kling_gupta_efficiency(simulated, observed_streamflow, variant="2012")
    # Doubling a series doubles alpha and beta but leaves gamma at 1.
    assert kge_2009 == pytest.approx(1.0 - math.sqrt(2.0))
    assert kge_2012 == pytest.approx(0.0)


def test_kge_unknown_variant_raises(observed_streamflow: FloatArray) -> None:
    with pytest.raises(ValueError, match="variant"):
        metrics.kling_gupta_efficiency(
            observed_streamflow, observed_streamflow, variant="2020"  # type: ignore[arg-type]
        )


def test_decomposition_2009_matches_independent_functions(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    decomposition = metrics.kling_gupta_decomposition(simulated_streamflow, observed_streamflow)
    assert decomposition.variant == "2009"
    assert decomposition.correlation == pytest.approx(
        metrics.pearson_correlation(simulated_streamflow, observed_streamflow)
    )
    assert decomposition.variability == pytest.approx(
        metrics.variability_ratio(simulated_streamflow, observed_streamflow)
    )
    assert decomposition.bias == pytest.approx(
        metrics.bias_ratio(simulated_streamflow, observed_streamflow)
    )
    assert decomposition.efficiency == pytest.approx(
        metrics.kling_gupta_efficiency(simulated_streamflow, observed_streamflow)
    )


def test_decomposition_2012_uses_coefficient_of_variation_ratio(
    simulated_streamflow: FloatArray, observed_streamflow: FloatArray
) -> None:
    decomposition = metrics.kling_gupta_decomposition(
        simulated_streamflow, observed_streamflow, variant="2012"
    )
    assert decomposition.variant == "2012"
    assert decomposition.variability == pytest.approx(
        metrics.coefficient_of_variation_ratio(simulated_streamflow, observed_streamflow)
    )
    assert decomposition.efficiency == pytest.approx(
        metrics.kling_gupta_efficiency(simulated_streamflow, observed_streamflow, variant="2012")
    )


def test_decomposition_is_immutable(observed_streamflow: FloatArray) -> None:
    decomposition = metrics.kling_gupta_decomposition(observed_streamflow, observed_streamflow)
    with pytest.raises(AttributeError):
        decomposition.efficiency = 0.0  # type: ignore[misc]
