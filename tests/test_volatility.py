import numpy as np

from spread_options.models import simulate_bivariate_gbm_paths, simulate_gbm_paths
from spread_options.volatility import ewma_corr, ewma_vol, historical_corr, historical_vol

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

def test_recovers_the_simulated_correlation():
    # 1. 500 one-year pairs of GBM paths simulated with rho = 0.6 (vols 30% and 35%)
    obs_times = np.linspace(0, 1, 253) # 252 days
    paths1, paths2 = simulate_bivariate_gbm_paths(100.0, 100.0, 0.03, 0.3, 0.35, 0.6, obs_times, n_paths=500)
    # 2. one estimate per year of data: each is a bit off (std 0.040), their mean must be 0.6
    estimates = np.array([historical_corr(p1, p2) for p1, p2 in zip(paths1, paths2)])
    std_err = estimates.std(ddof=1) / np.sqrt(len(estimates)) # precision of the mean: 0.0018
    # 3. obtained 0.6005: gap 0.0005 < 3 * 0.0018 = 0.0054
    #    catches: correlation of price levels instead of returns -> 0.564, one vol annualized -> 0.038
    assert abs(estimates.mean() - 0.6) < 3 * std_err


def test_ewma_recovers_the_simulated_correlation():
    # 1. same 500 one-year pairs as above, simulated with rho = 0.6
    obs_times = np.linspace(0, 1, 253)
    paths1, paths2 = simulate_bivariate_gbm_paths(100.0, 100.0, 0.03, 0.3, 0.35, 0.6, obs_times, n_paths=500)
    # 2. EWMA at the last date of each year: noisier than the historical one (std 0.115 vs 0.040),
    #    since it mostly looks at the last weeks, but its mean must still be 0.6
    estimates = np.array([ewma_corr(p1, p2) for p1, p2 in zip(paths1, paths2)])
    std_err = estimates.std(ddof=1) / np.sqrt(len(estimates)) # 0.0051
    # 3. obtained 0.5988: gap 0.0012 < 3 * 0.0051 = 0.0154
    #    catches: 0.94 and 0.06 swapped -> 0.439, divided by var2 only -> 0.514
    assert abs(estimates.mean() - 0.6) < 3 * std_err