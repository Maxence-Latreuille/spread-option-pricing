import numpy as np
from scipy.stats import norm
from scipy.special import roots_hermitenorm


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

def exact_spread_call(S1_0, S2_0, K, T, r, sigma1, sigma2, rho, n_points=32):
    """Spread call under bivariate GBM: conditional Black-Scholes averaged over the WTI shock (Gauss-Hermite)."""
    # --- Part 1: Gauss-Hermite points z_i and weights w_i for Z2 ~ N(0, 1)
    z, w = roots_hermitenorm(n_points)
    w = w / np.sqrt(2 * np.pi) # scipy weights sum to sqrt(2 pi): divide so they sum to 1

    # --- Part 2: conditional vol of the Brent, the same in every scenario
    sigma_star = sigma1 * np.sqrt(1 - rho**2)

    price = 0.0
    for zi, wi in zip(z, w):
        # --- Part 3: WTI at maturity fixed by the shock zi -> conditional strike
        S2_T = S2_0 * np.exp((r - 0.5 * sigma2**2) * T + sigma2 * np.sqrt(T) * zi)
        K_star = S2_T + K

        # --- Part 4: Brent spot to give Black-Scholes so that its mean at T is the conditional mean
        S1_star = S1_0 * np.exp(-0.5 * rho**2 * sigma1**2 * T + rho * sigma1 * np.sqrt(T) * zi)

        # --- Part 5: conditional call price
        if K_star > 0:
            c = bs_call(S1_star, K_star, T, r, sigma_star) # ordinary Black-Scholes
        else:
            c = S1_star - K_star * np.exp(-r * T) # K_star <= 0: always exercised, payoff is linear

        # --- Part 6: weighted contribution
        price += wi * c
    return price

def exact_spread_deltas(S1_0, S2_0, K, T, r, sigma1, sigma2, rho, n_points=32):
    """Deltas (Brent, WTI) of the spread call under bivariate GBM: derivative of exact_spread_call, point by point."""
    # --- Part 1: same Gauss-Hermite points and weights as the price
    z, w = roots_hermitenorm(n_points)
    w = w / np.sqrt(2 * np.pi)

    # --- Part 2: what does not depend on the scenario
    sigma_star = sigma1 * np.sqrt(1 - rho**2)
    discount = np.exp(-r * T)

    delta1, delta2 = 0.0, 0.0
    for zi, wi in zip(z, w):
        # --- Part 3: the two scaling factors of the scenario
        a = np.exp(-0.5 * rho**2 * sigma1**2 * T + rho * sigma1 * np.sqrt(T) * zi) # S1_star = S1_0 * a
        b = np.exp((r - 0.5 * sigma2**2) * T + sigma2 * np.sqrt(T) * zi) # S2_T = S2_0 * b
        S1_star = S1_0 * a
        K_star = S2_0 * b + K

        # --- Part 4: N(d1) and N(d2) of the conditional Black-Scholes
        if K_star > 0:
            d1 = (np.log(S1_star / K_star) + (r + sigma_star**2 / 2) * T) / (sigma_star * np.sqrt(T))
            d2 = d1 - sigma_star * np.sqrt(T)
            N1, N2 = norm.cdf(d1), norm.cdf(d2)
        else:
            N1, N2 = 1.0, 1.0 # K_star <= 0: always exercised

        # --- Part 5: chain rule, then weighted average
        delta1 += wi * a * N1 # dBS/dS = w_i * dS1_star/dS1_0 (= a) * N(d1)
        delta2 += wi * (-discount * N2) * b # dBS/dK = -exp(-rT) *N(d2) * dK_star/dS2_0 (= b)
    return delta1, delta2


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


def ldz_integral(C, D, eps):
    """Li-Deng-Zhou: average of N(C + D*y + eps*y^2) over y ~ N(0, 1), to second order in eps."""
    v = 1 + D**2
    z = C / np.sqrt(v)
    J0 = norm.cdf(z) # eps = 0: average of N(straight line), exact
    J1 = (1 + (1 + C**2) * D**2) / v**2.5 * norm.pdf(z) # first derivative in eps
    J2 = ((6 - 6 * C**2) * D**2 + (21 - 2 * C**2 - C**4) * D**4 + 4 * (3 + C**2) * D**6 - 3) / v**5.5 * C * norm.pdf(z) # second
    return J0 + J1 * eps + 0.5 * J2 * eps**2

def ldz_call(S1_0, S2_0, K, T, r, sigma1, sigma2, rho):
    """Li-Deng-Zhou (2008) spread call: exercise boundary replaced by a parabola around the median WTI."""
    if K < 0: # the formula needs K >= 0: parity, then swap the two assets
        return S1_0 - S2_0 - K * np.exp(-r * T) + ldz_call(S2_0, S1_0, -K, T, r, sigma2, sigma1, rho)

    # --- Part 1: log prices at maturity, ln S_iT = mu_i + nu_i * shock
    mu1 = np.log(S1_0) + (r - 0.5 * sigma1**2) * T
    mu2 = np.log(S2_0) + (r - 0.5 * sigma2**2) * T
    nu1, nu2 = sigma1 * np.sqrt(T), sigma2 * np.sqrt(T)
    R = np.exp(mu2) # median WTI at maturity: the parabola is built around it
    s = nu1 * np.sqrt(1 - rho**2) # conditional std of ln S1T once the WTI shock is known

    # --- Part 2: parabola C3 + D3*y + eps*y^2 for A(y) (value, slope, curvature at y = 0)
    C3 = (mu1 - np.log(R + K)) / s
    D3 = (rho * nu1 - nu2 * R / (R + K)) / s
    eps = -0.5 * nu2**2 * R * K / (R + K)**2 / s # zero when K = 0 -> Margrabe

    # --- Part 3: same parabola shifted for the Brent term (y + rho*nu1) and the WTI term (y + nu2)
    C1 = C3 + D3 * rho * nu1 + eps * rho**2 * nu1**2 + np.sqrt(1 - rho**2) * nu1
    D1 = D3 + 2 * rho * nu1 * eps
    C2 = C3 + D3 * nu2 + eps * nu2**2
    D2 = D3 + 2 * nu2 * eps

    # --- Part 4: receive the Brent, give the WTI, pay K, each with its own probability
    I1, I2, I3 = ldz_integral(C1, D1, eps), ldz_integral(C2, D2, eps), ldz_integral(C3, D3, eps)
    return S1_0 * I1 - S2_0 * I2 - K * np.exp(-r * T) * I3