import numpy as np

from spread_options.products import call_payoff, put_payoff, spread_call_payoff
from spread_options.models import simulate_terminal_prices, simulate_bivariate_gbm_paths

def mc_price(payoff_fn, S0, T, r, sigma, n_paths=100_000, seed=23):
    """Price any payoff that depends on S_T only, with its standard error."""
    ST = simulate_terminal_prices(S0, T, r, sigma, n_paths, seed)
    discounted = np.exp(-r * T) * payoff_fn(ST) # price = e^{-rT} E^Q[payoff]
    return discounted.mean(), discounted.std(ddof=1) / np.sqrt(n_paths)

def mc_call(S0, K, T, r, sigma, n_paths=100_000, seed=23):
    # mc_price needs a one-argument payoff: the lambda fixes K
    return mc_price(lambda ST: call_payoff(ST, K), S0, T, r, sigma, n_paths, seed)

def mc_put(S0, K, T, r, sigma, n_paths=100_000, seed=23):
    return mc_price(lambda ST: put_payoff(ST, K), S0, T, r, sigma, n_paths, seed)

def mc_spread_call(S1_0, S2_0, K, T, r, sigma1, sigma2, rho, n_paths=100_000, seed=23):
    """Price a European call on S1 - S2 under two correlated GBMs, with its standard error."""
    # obs_times = [T]: a European payoff only needs the prices at maturity
    S1, S2 = simulate_bivariate_gbm_paths(S1_0, S2_0, r, sigma1, sigma2, rho, [T], n_paths, seed) # mu = r: risk-neutral
    discounted = np.exp(-r * T) * spread_call_payoff(S1[:, -1], S2[:, -1], K)
    return discounted.mean(), discounted.std(ddof=1) / np.sqrt(n_paths)