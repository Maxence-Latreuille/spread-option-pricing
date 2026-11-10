import numpy as np

# Two ways to simulate the same GBM:
# - terminal prices: S_T in one jump. Enough for European payoffs, much cheaper
# - paths: S_t at every date, step by step. Needed for hedging or path-dependent payoffs.
# Both give the same law for S_T (variances of independent steps add up to sigma^2 * T),
# but not the same numbers: compare them over many scenarios, not path by path.

def terminal_prices_from_shocks(S0, T, r, sigma, Z):
    """Build S_T under the risk-neutral GBM from given standard normal shocks Z."""
    WT = np.sqrt(T) * Z # one shock per scenario covers the whole life: W_T ~ N(0, T)
    return S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * WT) # -sigma^2/2 so that E^Q[S_T] = S0 e^{rT}

def simulate_terminal_prices(S0, T, r, sigma, n_paths=100_000, seed=23):
    """Draw S_T under the risk-neutral Black-Scholes model."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths) # shape (n_paths,): one number per scenario
    return terminal_prices_from_shocks(S0, T, r, sigma, Z)


def gbm_paths_from_shocks(S0, mu, sigma, obs_times, Z):
    """Build GBM paths at the observation dates from given standard normal shocks."""
    obs_times = np.asarray(obs_times, dtype=float)
    dt = np.diff(obs_times, prepend=0) # length of each step; dt = 0 at t = 0, so column 0 is S0
    # one log-return per step and per scenario (dt is broadcast over the rows of Z)
    log_increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    # summing log-returns along time = multiplying returns, so S_t = S0 * exp(cumulative sum)
    return S0 * np.exp(np.cumsum(log_increments, axis=1))

def simulate_gbm_paths(S0, mu, sigma, obs_times, n_paths=100_000, seed=23):
    """Simulate GBM paths with drift mu (mu = r for risk-neutral paths): one row per scenario."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((n_paths, len(obs_times))) # one shock per scenario and per date
    return gbm_paths_from_shocks(S0, mu, sigma, obs_times, Z)