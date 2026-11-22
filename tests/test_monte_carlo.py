import numpy as np

from spread_options.analytics import bs_call, margrabe_call
from spread_options.monte_carlo import mc_call, mc_spread_call

PARAMS = dict(S0=100.0, K=100.0, T=1.0, r=0.03, sigma=0.2)

def test_mc_call_matches_bs():
    price, std_err = mc_call(**PARAMS)
    assert abs(price - bs_call(**PARAMS)) < 3 * std_err

def test_zero_strike_call_is_worth_spot():
    # K = 0: the call always pays S_T, so it is worth the stock itself
    price, std_err = mc_call(**{**PARAMS, "K": 0.0})
    assert abs(price - PARAMS["S0"]) < 3 * std_err

def test_spread_call_without_second_asset_is_bs():
    # 1. S2_0 = 0: the second price stays at 0 on every path (0 * exp(...) = 0),
    #    so the payoff max(S1_T - 0 - K, 0) is a plain call on S1
    # 2. sigma2 and rho then have no effect: any values work (here 0.3 and 0.5)
    # 3. the other inputs are those of PARAMS: S1_0 = 100, K = 100, T = 1, r = 3 %, sigma1 = 20 %
    price, std_err = mc_spread_call(S1_0=100.0, S2_0=0.0, K=100.0, T=1.0, r=0.03,
                                    sigma1=0.2, sigma2=0.3, rho=0.5)
    # 4. compare with Black-Scholes: 9.34 vs 9.41, gap 0.07 < 3 * 0.044 = 0.13
    assert abs(price - bs_call(**PARAMS)) < 3 * std_err

######

def test_zero_strike_spread_call_matches_margrabe():
    # 1. K = 0: the spread call is the exchange option, priced exactly by Margrabe (11.78)
    # 2. here rho matters: a wrong correlation in the simulation would move the MC price
    #    (rho = 0 -> 16.76, rho = 0.9 -> 7.65), so this test checks the Z2 mixing
    spread = dict(S1_0=80.0, S2_0=75.0, T=1.0, sigma1=0.3, sigma2=0.35, rho=0.6)
    # 3. Monte Carlo needs K and r; Margrabe needs neither (r cancels out)
    price, std_err = mc_spread_call(K=0.0, r=0.03, **spread)
    # 4. 11.69 vs 11.78, gap 0.09 < 3 * 0.047 = 0.14
    assert abs(price - margrabe_call(**spread)) < 3 * std_err