import numpy as np

from spread_options.models import simulate_gbm_paths
from spread_options.volatility import historical_vol

def test_recovers_the_simulated_vol():
    # 500 one-year GBM paths simulated at 20%: each estimate is a bit off,
    # but their mean must be 20% (obtained: mean 0.1995, std 0.0090)
    obs_times = np.linspace(0, 1, 253) # 252 days
    paths = simulate_gbm_paths(100.0, 0.03, 0.2, obs_times, n_paths=500)
    estimates = np.array([historical_vol(path) for path in paths])
    std_err = estimates.std(ddof=1) / np.sqrt(len(estimates)) # precision of the mean
    assert abs(estimates.mean() - 0.2) < 3 * std_err