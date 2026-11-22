from spread_options.analytics import bs_call, bs_delta

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