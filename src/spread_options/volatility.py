import numpy as np

def historical_vol(prices, days_per_year=252):
    """Annualized volatility from daily closing prices: std of daily log-returns times sqrt(252)."""
    prices = np.asarray(prices, dtype=float) # works with a numpy array or a pandas Series
    log_returns = np.diff(np.log(prices)) # r_i = ln(S_i) - ln(S_{i-1}) = ln(S_i / S_{i-1})
    daily_vol = log_returns.std(ddof=1) # ddof=1: divide by n-1, the mean is estimated on the same data
    return daily_vol * np.sqrt(days_per_year) # variances of independent days add up over the year