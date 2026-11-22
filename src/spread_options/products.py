import numpy as np

def call_payoff(ST, K):
    """Payoff of a European call option."""
    return np.maximum(ST - K, 0)

def put_payoff(ST, K):
    """Payoff of a European put option."""
    return np.maximum(K - ST, 0)

def spread_call_payoff(S1T, S2T, K):
    """Payoff of a European call on the spread S1 - S2."""
    return np.maximum(S1T - S2T - K, 0) # spread can be negative: the holder then gets 0