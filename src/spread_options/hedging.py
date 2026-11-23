import numpy as np

# Delta hedging: the bank sells an option, then every day holds delta shares so that
# the shares gain roughly what the option costs it. At maturity it sells the shares
# and pays the client. If the model is right, the final P&L is close to 0.
#
# Signs handle every case:
# - cash < 0: money borrowed (e.g. call hedge), cash > 0: money invested (e.g. put hedge)
# - shares < 0: shares sold short (put hedge, delta < 0)
# Assumptions (Black-Scholes): same rate r to borrow and lend, free short selling,
# no transaction costs, no dividends.

def hedge_one_path(path, T, r, price0, delta_fn, payoff_fn):
    """Final P&L of selling an option at price0 and delta-hedging it every day on one scenario of prices."""
    n_steps = len(path) - 1 # n dates = n - 1 rebalancing steps
    dt = T / n_steps # time between two rebalancing dates (equally spaced)
    cash = price0 # day 0: we receive the option price from the client
    shares = 0.0 # we start with no shares

    for i in range(n_steps):
        S = path[i] # today's price
        time_left = T - i * dt # time to maturity, needed by the model's delta
        new_shares = delta_fn(S, time_left) # 1. how many shares the model wants (any model)
        # 2. buy (or sell) only the difference, paid with cash:
        #    buying lowers cash (can go negative = borrowing), selling raises it
        cash = cash - (new_shares - shares) * S
        shares = new_shares
        # 3. interest until tomorrow: cash > 0 earns r, cash < 0 costs r
        cash = cash * np.exp(r * dt)

    ST = path[-1] # price at maturity
    # sell the shares (or buy them back if short), then pay the client
    # P&L > 0: option sold too expensive for this path, P&L < 0: sold too cheap
    return cash + shares * ST - payoff_fn(ST)

def delta_hedge_pnl(paths, T, r, price0, delta_fn, payoff_fn):
    """Final hedging P&L for every path (one row of paths = one scenario)."""
    pnls = []
    for path in paths: # each row is one scenario (simulated or real data)
        pnls.append(hedge_one_path(path, T, r, price0, delta_fn, payoff_fn))
    return np.array(pnls)


def hedge_spread_one_path(path1, path2, T, r, price0, deltas_fn, payoff_fn):
    """Final P&L of selling a spread option at price0 and delta-hedging both assets every day on one scenario."""
    n_steps = len(path1) - 1 # both paths share the same dates
    dt = T / n_steps
    cash = price0 # day 0: we receive the option price from the client
    shares1, shares2 = 0.0, 0.0 # units of asset 1 and asset 2 held (negative = sold short)

    for i in range(n_steps):
        S1, S2 = path1[i], path2[i] # today's two prices
        time_left = T - i * dt
        new1, new2 = deltas_fn(S1, S2, time_left) # 1. the two positions the model wants
        # 2. trade only the differences, paid with cash: buying lowers cash, selling raises it
        #    (for asset 2 held short, selling more raises cash, buying back lowers it)
        cash = cash - (new1 - shares1) * S1 - (new2 - shares2) * S2
        shares1, shares2 = new1, new2
        # 3. interest until tomorrow
        cash = cash * np.exp(r * dt)

    S1T, S2T = path1[-1], path2[-1] # prices at maturity
    # sell asset 1, buy back asset 2 (shares2 < 0, so shares2 * S2T < 0), then pay the client
    return cash + shares1 * S1T + shares2 * S2T - payoff_fn(S1T, S2T)


def delta_hedge_spread_pnl(paths1, paths2, T, r, price0, deltas_fn, payoff_fn):
    """Final spread hedging P&L for every scenario (row k of paths1 and row k of paths2 = one scenario)."""
    pnls = []
    for path1, path2 in zip(paths1, paths2): # walk through the two arrays row by row, together
        pnls.append(hedge_spread_one_path(path1, path2, T, r, price0, deltas_fn, payoff_fn))
    return np.array(pnls)