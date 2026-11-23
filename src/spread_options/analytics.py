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

def margrabe_deltas(S1_0, S2_0, T, sigma1, sigma2, rho):
    """Margrabe deltas: units of asset 1 and of asset 2 to hold (negative = sell short)."""
    # same ratio volatility and d1, d2 as in margrabe_call (Black-Scholes with K = S2_0, r = 0)
    sigma_hat = np.sqrt(sigma1**2 + sigma2**2 - 2 * rho * sigma1 * sigma2)
    d1 = (np.log(S1_0 / S2_0) + sigma_hat**2 / 2 * T) / (sigma_hat * np.sqrt(T))
    d2 = d1 - sigma_hat * np.sqrt(T)
    # the extra terms from d1 and d2 cancel since S1*n(d1) = S2*n(d2), so only N(d1) and -N(d2) remain
    return norm.cdf(d1), -norm.cdf(d2) # delta1, delta2

def kirk_call(S1_0, S2_0, K, T, r, sigma1, sigma2, rho):
    """Kirk approximation of a spread call: Margrabe with asset 2 replaced by 'asset 2 + K'."""
    B0 = S2_0 + K * np.exp(-r * T) # today's value of 'asset 2 + K': K is paid at maturity
    w = S2_0 / B0 # share of asset 2 in the sum: only this part moves, K stays fixed
    # treat 'asset 2 + K' as lognormal with vol sigma2 * w, then exchange it for asset 1 (Margrabe)
    return margrabe_call(S1_0, B0, T, sigma1, sigma2 * w, rho)

def kirk_deltas(S1_0, S2_0, K, T, r, sigma1, sigma2, rho, h=0.01):
    """Kirk deltas by central bumps: units of asset 1 and of asset 2 to hold (negative = sell short)."""
    price = lambda s1, s2: kirk_call(s1, s2, K, T, r, sigma1, sigma2, rho) # Kirk price, only the two spots change
    # slope of the price when one spot moves by +/- h, the other one fixed
    # bumping S2 also moves w and sigma_K, so delta2 includes that effect (unlike -N(d2))
    delta1 = (price(S1_0 + h, S2_0) - price(S1_0 - h, S2_0)) / (2 * h)
    delta2 = (price(S1_0, S2_0 + h) - price(S1_0, S2_0 - h)) / (2 * h)
    return delta1, delta2


def bjerksund_stensland_call(S1_0, S2_0, K, T, r, sigma1, sigma2, rho):
    """Bjerksund-Stensland (2014) spread call: Kirk's exercise rule, but asset 2 and K each get their own probability."""
    B0 = S2_0 + K * np.exp(-r * T) # same 'asset 2 + K' as in Kirk
    b = S2_0 / B0 # share of B0 that moves (Kirk's w)
    sigma = np.sqrt(sigma1**2 - 2 * rho * sigma1 * sigma2 * b + sigma2**2 * b**2) # same vol as in Kirk
    L = np.log(S1_0 / B0)
    den = sigma * np.sqrt(T)
    # same start L and same denominator; only the drift term changes (seen from asset 1, asset 2, or cash)
    d1 = (L + (sigma1**2 / 2 - b * rho * sigma1 * sigma2 + b**2 * sigma2**2 / 2) * T) / den
    d2 = (L + (-sigma1**2 / 2 + rho * sigma1 * sigma2 + b**2 * sigma2**2 / 2 - b * sigma2**2) * T) / den
    d3 = (L + (-sigma1**2 / 2 + b**2 * sigma2**2 / 2) * T) / den
    # receive asset 1, give back asset 2, pay K: each weighted by its own probability
    return S1_0 * norm.cdf(d1) - S2_0 * norm.cdf(d2) - K * np.exp(-r * T) * norm.cdf(d3)