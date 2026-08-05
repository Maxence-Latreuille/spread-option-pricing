# Spread Option Pricing

Pricing and risk management of options written on the price spread between two
assets — energy, commodities, equities, and processing spreads.

**Status:** early stage. Research and implementation in progress.

## Context

Projet d'Application Recherche (PAr), École Centrale de Lyon — Département SHLS,
équipe SHS-EG.

| | |
|---|---|
| **Authors** | Maxence Latreuille, Elliot Béreau |
| **Supervisor** | Christian de Peretti, Maître de conférences en finance |
| **Academic year** | 2026–2027 |

## Objectives

- [ ] Price the product under Black–Scholes (bivariate geometric Brownian motion)
- [ ] Price the product under stochastic volatility (Heston)
- [ ] Derive and compute the replicating portfolio
- [ ] Compute the Greeks for risk management
- [ ] Study implied volatility / implied correlation across strike and maturity
- [ ] *(optional)* Price the product with a multilayer perceptron and benchmark it
      against the analytical and Monte Carlo methods (pricing error, computation time)

## Problem statement

The payoff of a spread call at maturity is

    max(S1_T - S2_T - K, 0)

Two regimes have to be distinguished, and the distinction drives the whole project.

**K = 0.** A closed-form solution exists — the Margrabe (1978) exchange option
formula, built on the volatility of the ratio S1/S2:

    sigma_hat = sqrt(sigma1^2 + sigma2^2 - 2 * rho * sigma1 * sigma2)

Its value is independent of the risk-free rate: taking asset 2 as numeraire turns
the problem into a standard call on the ratio S1/S2.

**K != 0.** No closed form exists, even under Black–Scholes, because the difference
of two lognormal variables is not lognormal. Three routes are explored here:

- Kirk's (1995) approximation, which treats S2 + K as lognormal
- the Bjerksund–Stensland (2014) refinement
- Monte Carlo simulation, used as the reference benchmark

Under bivariate Heston no analytical solution is available in either regime; Monte
Carlo and Fourier methods (Dempster–Hong, Hurd–Zhou) apply.

## A note on implied volatility

The implied volatility of a spread option is not well defined: the price depends on
three diffusion parameters (sigma1, sigma2, rho) and a single market quote cannot
pin down three unknowns. Two coherent readings are used in this project:

1. **Implied correlation** — fix sigma1 and sigma2 at the implied volatilities
   quoted on each underlying and invert for rho. This is the market convention in
   energy.
2. **Implied spread volatility** — invert Margrabe for sigma_hat, aggregating the
   three parameters into one, which allows a strike x maturity surface comparable
   to a vanilla one.

The price is monotonically decreasing in rho, which makes the inversion stable.

## Repository structure

    src/spread_options/   Core library: models, Greeks, calibration
    notebooks/            Exploratory analysis and figures for the report
    tests/                Unit tests
    data/                 Market data (not versioned)
    docs/                 Report, bibliography, working notes

## Getting started

```bash
git clone https://github.com/Maxence-Latreuille/spread-option-pricing.git
cd spread-option-pricing

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest
```

## Working conventions

- `main` is protected: no direct commits, everything goes through a pull request
  reviewed by the other author
- One branch per feature: `feat/margrabe`, `feat/heston-mc`, `docs/report`
- Commit messages prefixed `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Every pricing model ships with unit tests, including a check against a known
  limiting case

## References

- Margrabe, W. (1978). *The Value of an Option to Exchange One Asset for Another.*
  Journal of Finance, 33(1), 177–186.
- Kirk, E. (1995). *Correlation in the Energy Markets.* In Managing Energy Price Risk.
- Carmona, R. & Durrleman, V. (2003). *Pricing and Hedging Spread Options.*
  SIAM Review, 45(4), 627–685.
- Bjerksund, P. & Stensland, G. (2014). *Closed Form Spread Option Valuation.*
  Quantitative Finance, 14(10), 1785–1794.
- Heston, S. (1993). *A Closed-Form Solution for Options with Stochastic Volatility.*
  Review of Financial Studies, 6(2), 327–343.
- Hull, J. C. *Options, Futures and Other Derivatives*, 11th ed. — ch. 26.6, 27.2,
  27.7, 28.4–28.5.

## License

MIT — see [LICENSE](LICENSE).
