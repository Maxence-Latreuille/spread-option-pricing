import numpy as np

def historical_vol(prices, days_per_year=252):
    """Annualized volatility from daily closing prices: std of daily log-returns times sqrt(252)."""
    prices = np.asarray(prices, dtype=float) # works with a numpy array or a pandas Series
    log_returns = np.diff(np.log(prices)) # r_i = ln(S_i) - ln(S_{i-1}) = ln(S_i / S_{i-1})
    daily_vol = log_returns.std(ddof=1) # ddof=1: divide by n-1, the mean is estimated on the same data
    return daily_vol * np.sqrt(days_per_year) # variances of independent days add up over the year

def ewma_vol(prices, lam=0.94, days_per_year=252):
    """Annualized EWMA (RiskMetrics) volatility at the last date: recent days weigh more."""
    prices = np.asarray(prices, dtype=float) # works with a numpy array or a pandas Series
    log_returns = np.diff(np.log(prices)) # r_t = ln(S_t / S_{t-1})
    variance = log_returns[0] ** 2 # start: the first squared return
    for r in log_returns[1:]:
        variance = lam * variance + (1 - lam) * r ** 2 # keep 94% of yesterday, add 6% of today
    return np.sqrt(variance * days_per_year) # daily variance -> annual, then the square root

def historical_corr(prices1, prices2):
    """Correlation of the daily log-returns of two assets (same dates, positive prices)."""
    r1 = np.diff(np.log(np.asarray(prices1, dtype=float))) # same log-returns as historical_vol
    r2 = np.diff(np.log(np.asarray(prices2, dtype=float)))
    dev1, dev2 = r1 - r1.mean(), r2 - r2.mean() # each day: above (+) or below (-) its usual move
    cov = (dev1 * dev2).sum() / (len(r1) - 1) # > 0 when both are on the same side
    return cov / (r1.std(ddof=1) * r2.std(ddof=1)) # divide by both stds: between -1 and +1

def ewma_corr(prices1, prices2, lam=0.94):
    """EWMA (RiskMetrics) correlation of two assets at the last date: recent days weigh more."""
    r1 = np.diff(np.log(np.asarray(prices1, dtype=float))) # same log-returns as ewma_vol
    r2 = np.diff(np.log(np.asarray(prices2, dtype=float)))
    cov, var1, var2 = r1[0] * r2[0], r1[0] ** 2, r2[0] ** 2 # start: the first day alone
    for a, b in zip(r1[1:], r2[1:]): # walk both return series together, day by day
        cov = lam * cov + (1 - lam) * a * b # keep 94% of yesterday, add 6% of today's product
        var1 = lam * var1 + (1 - lam) * a ** 2
        var2 = lam * var2 + (1 - lam) * b ** 2
    return cov / np.sqrt(var1 * var2) # no sqrt(252): it would cancel out