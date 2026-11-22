import numpy as np

from spread_options.analytics import bs_call, bs_delta
from spread_options.hedging import hedge_one_path, delta_hedge_pnl
from spread_options.models import simulate_gbm_paths
from spread_options.products import call_payoff

PARAMS = dict(S0=100.0, K=100.0, T=1.0, r=0.03, sigma=0.2)
N_PATHS = 100 # the simple loop is slow, 500 scenarios are enough for these checks (here 100 to make pytest faster)

def hedge_call(mu=0.03, true_sigma=0.2, n_steps=252):
    """Sell a call at the BS price (sigma=0.2) and hedge it daily on paths simulated with true_sigma."""
    S0, K, T, r, sigma = PARAMS.values()
    obs_times = np.linspace(0, T, n_steps + 1) # n_steps + 1 dates for n_steps days
    # the "real world": prices move with mu and true_sigma (drawn once, before hedging)
    paths = simulate_gbm_paths(S0, mu, true_sigma, obs_times, N_PATHS)
    # the bank: prices and hedges with ITS model, sigma = 0.2
    return delta_hedge_pnl(
        paths, T, r,
        price0=bs_call(S0, K, T, r, sigma),
        delta_fn=lambda S, time_left: bs_delta(S, K, time_left, r, sigma), # rule Delta(S, tau)
        payoff_fn=lambda ST: call_payoff(ST, K),
    ) # return 100 P&L

def test_hedge_hand_example():
    # tests the engine alone (no BS): delta fixed at 0.5, no interest (r = 0)
    # day 0: cash = 1.60 - 0.5 * 25 = -10.90 ; day 1: delta unchanged, nothing bought
    # maturity: resale 0.5 * 27 = 13.50, payoff 27 - 25 = 2 -> P&L = -10.90 + 13.50 - 2 = 0.60
    pnl = hedge_one_path(
        np.array([25.0, 26.0, 27.0]), T=1.0, r=0.0, price0=1.60,
        delta_fn=lambda S, time_left: 0.5,
        payoff_fn=lambda ST: call_payoff(ST, 25.0),
    )
    assert abs(pnl - 0.60) < 1e-12 # exact computation: only rounding errors of the computer

def test_daily_hedge_pnl_is_zero_on_average():
    # right model (true sigma = model sigma = 20%): each path has its own P&L
    # (calm path: small gain, agitated path: small loss) but the MEAN is ~ 0
    pnl = hedge_call() # obtained: mean 0.03, std 0.47
    std_err = pnl.std(ddof=1) / np.sqrt(N_PATHS) # precision of the mean: 0.47 / sqrt(500) = 0.02
    assert abs(pnl.mean()) < 3 * std_err # no bias
    # daily (not continuous) hedging leaves a small residual: 0.47 is 5% of the 9.41 price
    assert pnl.std(ddof=1) < 0.1 * bs_call(**PARAMS)

def test_real_drift_does_not_matter():
    # the stock really grows at 15% a year, not r = 3%: the hedge never uses mu,
    # so the price cannot depend on it (obtained: mean 0.00)
    pnl = hedge_call(mu=0.15)
    std_err = pnl.std(ddof=1) / np.sqrt(N_PATHS)
    assert abs(pnl.mean()) < 3 * std_err

def test_underestimated_vol_loses_the_price_gap():
    # the market moves at 30% but the bank priced and hedged at 20%:
    # it sold for 9.41 a call really worth 13.28, so it loses the 3.87 gap on average
    S0, K, T, r, sigma = PARAMS.values()
    # P&L is measured at maturity (obtained: mean -4.02), the price gap is today:
    # bring the P&L back to today with e^{-rT} -> -4.02 * e^{-0.03} = -3.90
    pnl = hedge_call(true_sigma=0.3) * np.exp(-r * T)
    gap = bs_call(S0, K, T, r, sigma) - bs_call(S0, K, T, r, 0.3) # 9.41 - 13.28 = -3.87
    std_err = pnl.std(ddof=1) / np.sqrt(N_PATHS) # ~ 0.08
    assert abs(pnl.mean() - gap) < 3 * std_err # |-3.90 - (-3.87)| = 0.03 < 0.24