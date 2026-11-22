import numpy as np

from spread_options.models import simulate_gbm_paths
from spread_options.volatility import historical_vol, ewma_vol

def test_recovers_the_simulated_vol():
    # 500 one-year GBM paths simulated at 20%: each estimate is a bit off,
    # but their mean must be 20% (obtained: mean 0.1995, std 0.0090)
    obs_times = np.linspace(0, 1, 253) # 252 days
    paths = simulate_gbm_paths(100.0, 0.03, 0.2, obs_times, n_paths=500)
    estimates = np.array([historical_vol(path) for path in paths])
    std_err = estimates.std(ddof=1) / np.sqrt(len(estimates)) # precision of the mean
    assert abs(estimates.mean() - 0.2) < 3 * std_err


def test_ewma_constant_daily_moves():
    # 1. 100 daily log-returns of exactly +1%, -1%, +1%, ...: every r^2 = 0.0001
    returns = np.array([0.01, -0.01] * 50)
    # 2. rebuild the prices: S_0 = 100, S_t = 100 * exp(r_1 + ... + r_t) -> 100, 101.005, 100, ...
    prices = 100 * np.exp(np.concatenate([[0], np.cumsum(returns)]))
    # 3. the variance starts at 0.0001 and each step mixes 0.0001 with 0.0001: it never moves,
    #    so the vol is 1% a day = 0.01 * sqrt(252) = 15.87% a year, whatever lambda
    assert abs(ewma_vol(prices) - 0.01 * np.sqrt(252)) < 1e-12