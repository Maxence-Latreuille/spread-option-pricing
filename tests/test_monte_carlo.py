import numpy as np

from spread_options.analytics import bs_call, kirk_call, margrabe_call, margrabe_deltas
from spread_options.monte_carlo import mc_call, mc_spread_call, mc_spread_deltas

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

def test_zero_strike_mc_deltas_match_margrabe():
    # 1. K = 0: the spread call is the exchange option, whose exact deltas Margrabe gives (+0.6430 / -0.5289)
    spread = dict(S1_0=80.0, S2_0=75.0, T=1.0, sigma1=0.3, sigma2=0.35, rho=0.6)
    exact1, exact2 = margrabe_deltas(**spread)
    # 2. Monte Carlo deltas on 100,000 scenarios: obtained +0.6426 / -0.5296, std errors 0.0018 / 0.0015
    delta1, delta2, err1, err2 = mc_spread_deltas(K=0.0, r=0.03, **spread)
    # 3. no bias: each delta within 3 standard errors of the exact one
    #    |0.6426 - 0.6430| = 0.0004 < 3 * 0.0018 = 0.0054 ; |-0.5296 - (-0.5289)| = 0.0007 < 3 * 0.0015 = 0.0045
    assert abs(delta1 - exact1) < 3 * err1
    assert abs(delta2 - exact2) < 3 * err2

def test_kirk_matches_mc_for_nonzero_strike():
    # 1. K = 5: no exact formula, Kirk is an approximation; the reference is Monte Carlo
    spread = dict(S1_0=80.0, S2_0=75.0, K=5.0, T=1.0, r=0.03, sigma1=0.3, sigma2=0.35, rho=0.6)
    # 2. 500,000 scenarios (std error 0.019): with 100,000 (0.042) the test would miss a forgotten discount
    price, std_err = mc_spread_call(n_paths=500_000, **spread)
    # 3. Kirk 9.047 vs MC 9.063, gap 0.016 < 3 * 0.019 = 0.057
    #    catches: w forgotten -> 9.418, K not discounted -> 8.971
    assert abs(kirk_call(**spread) - price) < 3 * std_err