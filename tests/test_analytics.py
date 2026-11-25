from spread_options.analytics import bs_call, bs_delta, exact_spread_call, exact_spread_deltas, ldz_call, margrabe_call, margrabe_deltas

PARAMS = dict(S0=100.0, K=100.0, T=1.0, r=0.03, sigma=0.2)

def test_bs_call_hand_value():
    assert abs(bs_call(**PARAMS) - 9.4134) < 1e-4

def test_delta_is_slope_of_price():
    # delta = how much the call moves when S0 moves: measure it with S0 +/- 0.01
    h = 0.01
    up = bs_call(**{**PARAMS, "S0": PARAMS["S0"] + h})
    down = bs_call(**{**PARAMS, "S0": PARAMS["S0"] - h})
    assert abs((up - down) / (2 * h) - bs_delta(**PARAMS)) < 1e-6

def test_delta_goes_from_0_to_1():
    # deep out of the money: call barely moves; deep in the money: moves like the stock
    assert bs_delta(**{**PARAMS, "S0": 50.0}) < 0.01
    assert bs_delta(**{**PARAMS, "S0": 200.0}) > 0.99


def test_margrabe_deltas_are_slopes_of_price():
    # 1. same exchange option as the Margrabe price test: price 11.78, deltas +0.6430 / -0.5289
    spread = dict(S1_0=80.0, S2_0=75.0, T=1.0,
     sigma1=0.3, sigma2=0.35, rho=0.6)
    delta1, delta2 = margrabe_deltas(**spread)
    h = 0.01
    # 2. move the Brent only (WTI stays at 75): price slope = delta of asset 1
    up1 = margrabe_call(**{**spread, "S1_0": 80.0 + h})
    down1 = margrabe_call(**{**spread, "S1_0": 80.0 - h})
    assert abs((up1 - down1) / (2 * h) - delta1) < 1e-6
    # 3. move the WTI only (Brent stays at 80): price slope = delta of asset 2, negative
    up2 = margrabe_call(**{**spread, "S2_0": 75.0 + h})
    down2 = margrabe_call(**{**spread, "S2_0": 75.0 - h})
    assert abs((up2 - down2) / (2 * h) - delta2) < 1e-6


def test_exact_spread_deltas_are_slopes_of_exact_price():
    # 1. fil rouge with K = 5: deltas from the formula +0.5600617 / -0.4433854
    spread = dict(S1_0=80.0, S2_0=75.0, K=5.0, T=1.0, r=0.03, sigma1=0.3, sigma2=0.35, rho=0.6)
    delta1, delta2 = exact_spread_deltas(**spread)
    h = 0.01
    # 2. move the Brent only (80.01 and 79.99), WTI stays at 75: price slope 0.5600617
    up1 = exact_spread_call(**{**spread, "S1_0": 80.0 + h})
    down1 = exact_spread_call(**{**spread, "S1_0": 80.0 - h})
    assert abs((up1 - down1) / (2 * h) - delta1) < 1e-6
    # 3. move the WTI only (75.01 and 74.99), Brent stays at 80: price slope -0.4433854
    up2 = exact_spread_call(**{**spread, "S2_0": 75.0 + h})
    down2 = exact_spread_call(**{**spread, "S2_0": 75.0 - h})
    assert abs((up2 - down2) / (2 * h) - delta2) < 1e-6


def test_ldz_matches_exact_spread_call_for_negative_strike():
    # 1. fil rouge with K = -5: Kirk's worst kind of case (+1.6 cents); exact price from the 1-D integral
    spread = dict(S1_0=80.0, S2_0=75.0, K=-5.0, T=1.0, r=0.03, sigma1=0.3, sigma2=0.35, rho=0.6)
    exact = exact_spread_call(**spread, n_points=64)
    # 2. K < 0 goes through the parity branch, which calls the K >= 0 formula with the assets swapped:
    #    one case checks both parts (LDZ error -0.00003 $, far below 0.01 cent)
    assert abs(ldz_call(**spread) - exact) < 1e-4