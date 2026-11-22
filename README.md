# Spread Option Pricing

Pricing and risk management of options written on the price spread between two
assets, with an application to energy markets (Brent, WTI, heating oil).

**Status:** the single-asset foundation (Black–Scholes call, delta hedging,
volatility estimation, real-data backtest on Brent) is done. The spread-option
models are being implemented one by one, from the simplest to the most complex
(see the [roadmap](#roadmap-spread-option-models)).

## Context

Projet d'Application Recherche (PAr), École Centrale de Lyon, Département SHLS,
équipe SHS-EG.

| | |
|---|---|
| **Authors** | [Maxence Latreuille](https://maxencelatreuille.com), Elliot Béreau |
| **Supervisor** | Christian de Peretti, Maître de conférences en finance |
| **Academic year** | 2026–2027 |

## Objectives

- [x] Delta-hedge a Black–Scholes call, in simulation and on real Brent data (foundation)
- [x] Estimate volatility from market data (historical, EWMA) and measure what the error costs
- [ ] Price a spread option with many models and **compare them** (price error, computation time, hedging quality)
- [ ] Price under stochastic volatility (Heston) and with jumps
- [ ] Derive and compute the replicating portfolio and the Greeks of a spread option
- [ ] Study implied volatility / implied correlation across strike and maturity
- [ ] *(optional)* Price with a multilayer perceptron and benchmark it against the
      analytical and Monte Carlo methods (pricing error, computation time)

## Problem statement

The payoff of a spread call at maturity is

    max(S1_T - S2_T - K, 0)

Two regimes have to be distinguished, and the distinction drives the whole project.

**K = 0.** A closed-form solution exists: the Margrabe (1978) exchange option
formula, built on the volatility of the ratio S1/S2:

    sigma_hat = sqrt(sigma1^2 + sigma2^2 - 2 * rho * sigma1 * sigma2)

Its value is independent of the risk-free rate: taking asset 2 as numeraire turns
the problem into a standard call on the ratio S1/S2.

**K != 0.** No closed form exists, even under Black–Scholes, because the difference
of two lognormal variables is not lognormal. This is why so many approximations
exist, and why the project compares them against a Monte Carlo reference.

## What has been done: the single-asset foundation

Before moving to two assets, the whole pricing and hedging chain was built and
tested on a single call on Brent (`BZ=F`):

    estimate sigma  ->  premium (Black–Scholes)  ->  daily delta hedge  ->  P&L

Each idea is checked twice: first in simulation, where the model is true by
construction and the answer is known, then on real market data.

| Notebook | Question | Main results |
|---|---|---|
| [`01_hedging_simulation`](notebooks/01_hedging_simulation.ipynb) | Does delta hedging work when the model is right? (simulated prices) | Mean P&L ≈ 0. With daily rebalancing the P&L standard deviation is 4.8 % of the premium, and it shrinks as 1/√n (log slope −0.48). One day of hedging = time decay (theta) earned minus the squared move paid (gamma); break-even at the "normal" daily move σ/√252. With a wrong volatility, the mean P&L equals the premium error (≈ 0.39 $ per volatility point) and a wrong delta adds dispersion. |
| [`02_volatility_estimation`](notebooks/02_volatility_estimation.ipynb) | Can sigma be forecast on January 1st? (Brent 2013–2024) | Mean absolute error on the next year's volatility: 14.7 pts with last year's historical volatility, 11.7 pts with EWMA (λ = 0.94). Neither foresees shocks such as 2020. |
| [`03_hedging_real_data`](notebooks/03_hedging_real_data.ipynb) | On real data, where does the hedging P&L come from? (12 one-year at-the-money calls on Brent, 2013–2024) | Mean absolute P&L: 3.49 $ with historical volatility, 2.15 $ with EWMA, 0.64 $ if the realized volatility of the year had been known, 0.23 $ if the remaining volatility had been known every day. Most of the error comes from not knowing sigma when the option is sold; the rest from volatility changing during the year (motivation for Heston). |

Modelling note: `BZ=F` is a futures price. The notebooks deliberately treat Brent
like a stock (Black–Scholes, r = 3 %); the final model should use the Black-76
versions of each formula (Black–Scholes overprices the 2023 at-the-money call by
about 12 %).

## Roadmap: spread option models

The goal is to implement **many pricing models for the spread call and compare
them**, from the simplest / least accurate to the most complex, as far as time
allows. Each model comes with its formula worked out on a small numerical example,
a library function, one unit test against a known limiting case, and a comparison
against the Monte Carlo reference.

| # | Model | Idea | Accuracy / limits | Reference check | Status |
|---|---|---|---|---|---|
| 0 | **Bivariate GBM + Monte Carlo** | simulate two correlated prices (ρ) and average the discounted payoff | exact under GBM but slow and noisy; **reference** for all other models | simulated correlation ≈ ρ; σ2 = 0 → Black–Scholes | next |
| 1 | **Bachelier** | the spread itself follows an arithmetic Brownian motion | simplest; handles negative spreads; ignores the lognormal legs | vs Monte Carlo | planned |
| 2 | **Margrabe (1978)** | exchange option, K = 0 | exact, but only for K = 0 | Monte Carlo ≈ Margrabe | planned |
| 3 | **Kirk (1995)** | treat S2 + K as lognormal, Black-type formula | energy market standard; degrades for large K or ρ close to 1 | K = 0 → Margrabe | planned |
| 4 | **Modified Kirk (Bjerksund–Stensland)** | correction of Kirk's formula | more accurate, still closed form | vs Monte Carlo | planned |
| 5 | **Li–Deng–Zhou (2008)** | second-order closed-form approximation | very accurate under GBM, heavier formula | vs Monte Carlo | planned |
| 6 | **Carmona–Durrleman (2003)** | optimised lower bound | very accurate, needs a numerical optimisation | vs Monte Carlo | planned |
| 7 | **Fourier / FFT (Hurd–Zhou 2010)** | price through a Fourier transform | near-exact and fast under GBM, harder mathematics | vs Monte Carlo | optional |
| 8 | **Bivariate Heston (Monte Carlo)** | stochastic volatility on each leg | captures volatility that changes during the year | vol of vol = 0 → GBM | planned |
| 9 | **Bivariate Merton jump-diffusion** | adds jumps to both prices | captures shocks such as 2020 and 2022; harder to calibrate | jump intensity = 0 → GBM | planned |
| 10 | **SABR** | stochastic volatility, market-standard smile model | if time allows | — | optional |
| 11 | **Neural network (MLP)** | learn the price from (S1, S2, K, σ1, σ2, ρ, T) | compare error and computation time with the formulas | vs Monte Carlo / Kirk on a test set | optional |

Comparison criteria: pricing error against Monte Carlo (across K, ρ, σ1, σ2, T),
computation time, quality of the deltas (hedging P&L in simulation), then real
spread trades with σ1, σ2 and ρ estimated from data. Each of the three notebooks
will get a spread part: hedging in simulation (two deltas), estimation of ρ, and a
real-data backtest. The spread itself (US crack spread `42 × HO − WTI` or
`Brent − WTI`) is still to be chosen.

## A note on implied volatility

The implied volatility of a spread option is not well defined: the price depends on
three diffusion parameters (sigma1, sigma2, rho) and a single market quote cannot
pin down three unknowns. Two coherent readings are used in this project:

1. **Implied correlation**: fix sigma1 and sigma2 at the implied volatilities
   quoted on each underlying and invert for rho. This is the market convention in
   energy.
2. **Implied spread volatility**: invert Margrabe for sigma_hat, aggregating the
   three parameters into one, which allows a strike x maturity surface comparable
   to a vanilla one.

The price is monotonically decreasing in rho, which makes the inversion stable.

## Repository structure

    src/spread_options/   Core library
        products.py       payoffs (call, put; spread call next)
        models.py         GBM terminal prices and paths
        monte_carlo.py    Monte Carlo pricing, returns (price, standard error)
        analytics.py      closed forms (Black–Scholes price and delta)
        hedging.py        delta-hedging P&L along one or many paths
        volatility.py     volatility estimators (historical, EWMA)
        data.py           daily prices from Yahoo Finance
    tests/                Unit tests (pytest), one meaningful test per function
    notebooks/            Analyses and figures for the report (01, 02, 03)

## Getting started

```bash
git clone https://github.com/Maxence-Latreuille/spread-option-pricing.git
cd spread-option-pricing

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .               # makes `import spread_options` work everywhere

pytest
```

## Working conventions

- Two-person project: commits are pushed directly to `main`
- Always fetch and pull before starting work and before pushing
- Commit messages prefixed `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Every pricing model ships with unit tests, including a check against a known
  limiting case
- Library code stays in `src/`; notebooks only import functions

## References

- Bachelier, L. (1900). *Théorie de la spéculation.* Annales scientifiques de
  l'École Normale Supérieure.
- Black, F. (1976). *The Pricing of Commodity Contracts.* Journal of Financial
  Economics.
- Margrabe, W. (1978). *The Value of an Option to Exchange One Asset for Another.*
  Journal of Finance, 33(1), 177–186.
- Merton, R. C. (1976). *Option Pricing When Underlying Stock Returns Are
  Discontinuous.* Journal of Financial Economics.
- Heston, S. (1993). *A Closed-Form Solution for Options with Stochastic Volatility.*
  Review of Financial Studies, 6(2), 327–343.
- Kirk, E. (1995). *Correlation in the Energy Markets.* In Managing Energy Price Risk.
- Hagan, P., Kumar, D., Lesniewski, A. & Woodward, D. (2002). *Managing Smile Risk.*
  Wilmott Magazine.
- Dempster, M. & Hong, S. (2002). *Spread Option Valuation and the Fast Fourier
  Transform.*
- Carmona, R. & Durrleman, V. (2003). *Pricing and Hedging Spread Options.*
  SIAM Review, 45(4), 627–685.
- Li, M., Deng, S.-J. & Zhou, J. (2008). *Closed-Form Approximations for Spread
  Option Prices and Greeks.* Journal of Derivatives.
- Hurd, T. & Zhou, Z. (2010). *A Fourier Transform Method for Spread Option
  Pricing.* SIAM Journal on Financial Mathematics.
- Bjerksund, P. & Stensland, G. (2014). *Closed Form Spread Option Valuation.*
  Quantitative Finance, 14(10), 1785–1794.
- J.P. Morgan / Reuters (1996). *RiskMetrics Technical Document* (EWMA volatility).
- Hull, J. C. *Options, Futures and Other Derivatives*, 11th ed. — ch. 26.6, 27.2,
  27.7, 28.4–28.5.

## License

MIT — see [LICENSE](LICENSE).
