import numpy as np

from spread_options.models import terminal_prices_from_shocks, simulate_terminal_prices

def test_terminal_prices_match_hand_calculation():
    Z = np.array([-0.4, 0.0, 1.0])
    ST = terminal_prices_from_shocks(100, 1.0, 0.03, 0.2, Z)
    expected = np.array([93.24, 101.01, 123.37])
    assert np.allclose(ST, expected, atol=1e-2)

def test_discounted_mean_equals_spot():
    S0, T, r = 100, 1.0, 0.03
    ST = simulate_terminal_prices(S0, T, r, sigma=0.2)
    discounted = np.exp(-r * T) * ST
    std_error = discounted.std(ddof=1) / np.sqrt(len(ST))
    assert abs(discounted.mean() - S0) < 3 * std_error # E^Q[S_T] = S0 e^{rT}

from spread_options.models import gbm_paths_from_shocks

def test_gbm_paths_match_hand_calculation():
    # 2 scenarios, 3 dates (0, 6 months, 1 year): same numbers as the hand example
    Z = np.array([[0.5, 1.0, -0.5], [-1.2, 0.3, 0.8]])
    paths = gbm_paths_from_shocks(100.0, 0.03, 0.2, [0, 0.5, 1], Z)
    expected = np.array([[100, 115.77, 108.41], [100, 104.86, 118.01]])
    assert np.allclose(paths, expected, atol=1e-2)

def test_one_step_path_equals_terminal_price():
    # with a single date T, the path method is exactly the one-jump method
    Z = np.array([-0.4, 0.0, 1.0])
    path_end = gbm_paths_from_shocks(100.0, 0.03, 0.2, [1.0], Z.reshape(-1, 1))[:, -1]
    ST = terminal_prices_from_shocks(100.0, 1.0, 0.03, 0.2, Z)
    assert np.allclose(path_end, ST)