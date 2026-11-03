import numpy as np

def terminal_prices_from_shocks(S0, T, r, sigma, Z):
    """Build S_T under the risk-neutral GBM from given standard normal shocks Z."""
    WT = np.sqrt(T) * Z # W_T ~ N(0, T)
    return S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * WT) # -sigma^2/2 so that E^Q[S_T] = S0 e^{rT}

def simulate_terminal_prices(S0, T, r, sigma, n_paths=100_000, seed=23):
    """Draw S_T under the risk-neutral Black-Scholes model."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    return terminal_prices_from_shocks(S0, T, r, sigma, Z)