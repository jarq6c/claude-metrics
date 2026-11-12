"""Tests for hydrodemo.metrics."""

import math
from collections.abc import Callable

import numpy as np
import pytest

from hydrodemo import metrics

OBSERVED = np.array([1.0, 3.0, 2.0, 5.0, 4.0])


# ---------------------------------------------------------------------------
# Input validation (shared by all metrics)
# ---------------------------------------------------------------------------

ALL_METRICS: list[Callable[..., float]] = [
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


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_mismatched_lengths_raise(metric_function: Callable[..., float]) -> None:
    with pytest.raises(ValueError, match="same length"):
        metric_function(simulated=[1.0, 2.0], observed=[1.0, 2.0, 3.0])


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_empty_input_raises(metric_function: Callable[..., float]) -> None:
    with pytest.raises(ValueError, match="empty"):
        metric_function(simulated=[], observed=[])


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_nonfinite_input_raises(metric_function: Callable[..., float]) -> None:
    with pytest.raises(ValueError, match="finite"):
        metric_function(simulated=[1.0, np.nan, 3.0], observed=[1.0, 2.0, 3.0])


@pytest.mark.parametrize("metric_function", ALL_METRICS)
def test_multidimensional_input_raises(metric_function: Callable[..., float]) -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        metric_function(simulated=[[1.0, 2.0]], observed=[[1.0, 2.0]])


# ---------------------------------------------------------------------------
# Nash-Sutcliffe efficiency
# ---------------------------------------------------------------------------


def test_nse_perfect_simulation_is_one() -> None:
    assert metrics.nash_sutcliffe_efficiency(OBSERVED, OBSERVED) == pytest.approx(1.0)


def test_nse_mean_simulation_is_zero() -> None:
    mean_simulation = np.full_like(OBSERVED, OBSERVED.mean())
    assert metrics.nash_sutcliffe_efficiency(mean_simulation, OBSERVED) == pytest.approx(0.0)


def test_nse_known_value() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    # Sum of squared errors = 2, sum of squared deviations from mean (3) = 10.
    assert metrics.nash_sutcliffe_efficiency(simulated, OBSERVED) == pytest.approx(0.8)


def test_nse_constant_observations_raise() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.nash_sutcliffe_efficiency([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])


# ---------------------------------------------------------------------------
# Log Nash-Sutcliffe efficiency
# ---------------------------------------------------------------------------


def test_log_nse_perfect_simulation_is_one() -> None:
    assert metrics.log_nash_sutcliffe_efficiency(OBSERVED, OBSERVED) == pytest.approx(1.0)


def test_log_nse_matches_nse_of_transformed_series() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    offset = 0.5
    expected = metrics.nash_sutcliffe_efficiency(
        np.log(simulated + offset), np.log(OBSERVED + offset)
    )
    result = metrics.log_nash_sutcliffe_efficiency(simulated, OBSERVED, offset=offset)
    assert result == pytest.approx(expected)


def test_log_nse_default_offset_is_one_percent_of_observed_mean() -> None:
    simulated = np.array([0.0, 3.0, 2.0, 4.0, 4.0])
    default_offset = OBSERVED.mean() / 100.0
    expected = metrics.log_nash_sutcliffe_efficiency(simulated, OBSERVED, offset=default_offset)
    assert metrics.log_nash_sutcliffe_efficiency(simulated, OBSERVED) == pytest.approx(expected)


def test_log_nse_handles_zero_flows_with_default_offset() -> None:
    observed = np.array([0.0, 1.0, 2.0, 3.0])
    simulated = np.array([0.0, 1.0, 2.0, 2.5])
    assert math.isfinite(metrics.log_nash_sutcliffe_efficiency(simulated, observed))


def test_log_nse_nonpositive_shifted_values_raise() -> None:
    with pytest.raises(ValueError, match="positive"):
        metrics.log_nash_sutcliffe_efficiency([-1.0, 2.0, 3.0], [1.0, 2.0, 3.0], offset=0.5)


def test_log_nse_negative_offset_raises() -> None:
    with pytest.raises(ValueError, match="offset"):
        metrics.log_nash_sutcliffe_efficiency(OBSERVED, OBSERVED, offset=-1.0)


# ---------------------------------------------------------------------------
# Root mean squared error
# ---------------------------------------------------------------------------


def test_rmse_perfect_simulation_is_zero() -> None:
    assert metrics.root_mean_squared_error(OBSERVED, OBSERVED) == pytest.approx(0.0)


def test_rmse_known_value() -> None:
    simulated = OBSERVED + np.array([1.0, -1.0, 1.0, -1.0, 2.0])
    # Mean squared error = (1 + 1 + 1 + 1 + 4) / 5 = 1.6.
    result = metrics.root_mean_squared_error(simulated, OBSERVED)
    assert result == pytest.approx(math.sqrt(1.6))


# ---------------------------------------------------------------------------
# Percent bias
# ---------------------------------------------------------------------------


def test_percent_bias_perfect_simulation_is_zero() -> None:
    assert metrics.percent_bias(OBSERVED, OBSERVED) == pytest.approx(0.0)


def test_percent_bias_overestimation_is_positive() -> None:
    assert metrics.percent_bias(OBSERVED * 1.1, OBSERVED) == pytest.approx(10.0)


def test_percent_bias_underestimation_is_negative() -> None:
    assert metrics.percent_bias(OBSERVED * 0.8, OBSERVED) == pytest.approx(-20.0)


def test_percent_bias_zero_observed_total_raises() -> None:
    with pytest.raises(ValueError, match="sum"):
        metrics.percent_bias([1.0, 1.0], [1.0, -1.0])


# ---------------------------------------------------------------------------
# Kling-Gupta efficiency components
# ---------------------------------------------------------------------------


def test_pearson_correlation_matches_numpy() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    expected = np.corrcoef(simulated, OBSERVED)[0, 1]
    assert metrics.pearson_correlation(simulated, OBSERVED) == pytest.approx(expected)


def test_pearson_correlation_of_negated_series_is_minus_one() -> None:
    assert metrics.pearson_correlation(-OBSERVED, OBSERVED) == pytest.approx(-1.0)


def test_pearson_correlation_constant_series_raises() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.pearson_correlation([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])


def test_variability_ratio_of_scaled_series() -> None:
    assert metrics.variability_ratio(OBSERVED * 2.0, OBSERVED) == pytest.approx(2.0)


def test_variability_ratio_ignores_offset() -> None:
    assert metrics.variability_ratio(OBSERVED + 10.0, OBSERVED) == pytest.approx(1.0)


def test_variability_ratio_constant_observations_raise() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.variability_ratio([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])


def test_bias_ratio_of_scaled_series() -> None:
    assert metrics.bias_ratio(OBSERVED * 1.5, OBSERVED) == pytest.approx(1.5)


def test_bias_ratio_zero_observed_mean_raises() -> None:
    with pytest.raises(ValueError, match="mean"):
        metrics.bias_ratio([1.0, 2.0], [-1.0, 1.0])


def test_coefficient_of_variation_ratio_is_unaffected_by_scaling() -> None:
    assert metrics.coefficient_of_variation_ratio(OBSERVED * 3.0, OBSERVED) == pytest.approx(1.0)


def test_coefficient_of_variation_ratio_equals_alpha_over_beta() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    expected = metrics.variability_ratio(simulated, OBSERVED) / metrics.bias_ratio(
        simulated, OBSERVED
    )
    result = metrics.coefficient_of_variation_ratio(simulated, OBSERVED)
    assert result == pytest.approx(expected)


def test_coefficient_of_variation_ratio_zero_simulated_mean_raises() -> None:
    with pytest.raises(ValueError, match="mean"):
        metrics.coefficient_of_variation_ratio([-1.0, 1.0], [1.0, 2.0])


# ---------------------------------------------------------------------------
# Kling-Gupta efficiency and decomposition
# ---------------------------------------------------------------------------


def test_kge_perfect_simulation_is_one() -> None:
    assert metrics.kling_gupta_efficiency(OBSERVED, OBSERVED) == pytest.approx(1.0)


def test_kge_2009_from_components() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    correlation = metrics.pearson_correlation(simulated, OBSERVED)
    alpha = metrics.variability_ratio(simulated, OBSERVED)
    beta = metrics.bias_ratio(simulated, OBSERVED)
    expected = 1.0 - math.sqrt((correlation - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    assert metrics.kling_gupta_efficiency(simulated, OBSERVED) == pytest.approx(expected)


def test_kge_2012_from_components() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    correlation = metrics.pearson_correlation(simulated, OBSERVED)
    gamma = metrics.coefficient_of_variation_ratio(simulated, OBSERVED)
    beta = metrics.bias_ratio(simulated, OBSERVED)
    expected = 1.0 - math.sqrt((correlation - 1) ** 2 + (gamma - 1) ** 2 + (beta - 1) ** 2)
    result = metrics.kling_gupta_efficiency(simulated, OBSERVED, variant="2012")
    assert result == pytest.approx(expected)


def test_kge_variants_differ_when_bias_is_present() -> None:
    simulated = OBSERVED * 2.0
    kge_2009 = metrics.kling_gupta_efficiency(simulated, OBSERVED, variant="2009")
    kge_2012 = metrics.kling_gupta_efficiency(simulated, OBSERVED, variant="2012")
    # Scaling doubles alpha and beta, but leaves gamma at 1.
    assert kge_2009 == pytest.approx(1.0 - math.sqrt(2.0))
    assert kge_2012 == pytest.approx(0.0)


def test_kge_unknown_variant_raises() -> None:
    with pytest.raises(ValueError, match="variant"):
        metrics.kling_gupta_efficiency(
            OBSERVED, OBSERVED, variant="2020"  # type: ignore[arg-type]
        )


def test_decomposition_2009_matches_independent_functions() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    decomposition = metrics.kling_gupta_decomposition(simulated, OBSERVED)
    assert decomposition.variant == "2009"
    assert decomposition.correlation == pytest.approx(
        metrics.pearson_correlation(simulated, OBSERVED)
    )
    assert decomposition.variability == pytest.approx(
        metrics.variability_ratio(simulated, OBSERVED)
    )
    assert decomposition.bias == pytest.approx(metrics.bias_ratio(simulated, OBSERVED))
    assert decomposition.efficiency == pytest.approx(
        metrics.kling_gupta_efficiency(simulated, OBSERVED)
    )


def test_decomposition_2012_uses_coefficient_of_variation_ratio() -> None:
    simulated = np.array([2.0, 3.0, 2.0, 4.0, 4.0])
    decomposition = metrics.kling_gupta_decomposition(simulated, OBSERVED, variant="2012")
    assert decomposition.variant == "2012"
    assert decomposition.variability == pytest.approx(
        metrics.coefficient_of_variation_ratio(simulated, OBSERVED)
    )
    assert decomposition.efficiency == pytest.approx(
        metrics.kling_gupta_efficiency(simulated, OBSERVED, variant="2012")
    )


def test_decomposition_is_immutable() -> None:
    decomposition = metrics.kling_gupta_decomposition(OBSERVED, OBSERVED)
    with pytest.raises(AttributeError):
        decomposition.efficiency = 0.0  # type: ignore[misc]


def test_coefficient_of_variation_ratio_constant_observations_raise() -> None:
    with pytest.raises(ValueError, match="constant"):
        metrics.coefficient_of_variation_ratio([1.0, 2.0, 3.0], [2.0, 2.0, 2.0])
