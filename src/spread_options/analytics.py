import numpy as np
from scipy.stats import norm

def bs_call(S0, K, T, r, sigma):
    """Black-Scholes price of a European call option."""
    d1 = (np.log(S0 / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    # S0*N(d1): shares held by the hedger; K*exp(-rT)*N(d2): cash borrowed
    return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def bs_delta(S0, K, T, r, sigma):
    """Black-Scholes delta of a European call: number of shares to hold."""
    d1 = (np.log(S0 / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    return norm.cdf(d1) # delta = N(d1)

def margrabe_call(S1_0, S2_0, T, sigma1, sigma2, rho):
    """Margrabe price of the option to exchange asset 2 for asset 1 (spread call with K = 0)."""
    # volatility of the ratio S1/S2: the two vols add up, minus what moves together
    sigma_hat = np.sqrt(sigma1**2 + sigma2**2 - 2 * rho * sigma1 * sigma2)
    # call on the ratio with strike 1, counted in units of asset 2: Black-Scholes with K = S2_0 and r = 0
    return bs_call(S1_0, S2_0, T, 0.0, sigma_hat)