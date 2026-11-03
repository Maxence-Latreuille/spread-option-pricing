import numpy as np

def call_payoff(ST, K):
    """Payoff of a European call option."""
    return np.maximum(ST - K, 0)

def put_payoff(ST, K):
    """Payoff of a European put option."""
    return np.maximum(K - ST, 0)