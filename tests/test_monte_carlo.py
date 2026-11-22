import numpy as np

from spread_options.analytics import bs_call
from spread_options.monte_carlo import mc_call

PARAMS = dict(S0=100.0, K=100.0, T=1.0, r=0.03, sigma=0.2)

def test_mc_call_matches_bs():
    price, std_err = mc_call(**PARAMS)
    assert abs(price - bs_call(**PARAMS)) < 3 * std_err

def test_zero_strike_call_is_worth_spot():
    # K = 0: the call always pays S_T, so it is worth the stock itself
    price, std_err = mc_call(**{**PARAMS, "K": 0.0})
    assert abs(price - PARAMS["S0"]) < 3 * std_err