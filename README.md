# Spread Option Pricing

Pricing and hedging of options written on the price spread between two
assets, with an application to energy markets (Brent, WTI, heating oil).

**Status:** the single-asset foundation (Black–Scholes call, delta hedging,
volatility estimation, real-data backtest on Brent) is done. On the spread side,
the bivariate GBM with its Monte Carlo reference and Margrabe's exact formula
(K = 0) are implemented and tested. Next: Margrabe's deltas and the first hedge of a
spread in simulation (see the [roadmap](#roadmap)).

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
- [x] Simulate two correlated prices (bivariate GBM) and price a spread call by Monte Carlo
- [x] Price the zero-strike spread call exactly (Margrabe)
- [ ] Compare fast pricing methods against Monte Carlo (price error, delta error, computation time)
- [ ] Hedge a spread option in simulation, then on a real spread trade with ρ estimated from data
- [ ] Price under stochastic volatility (Heston) and with jumps
- [ ] Study implied volatility / implied correlation across strike and maturity
- [ ] *(optional)* Price with a multilayer perceptron and benchmark it against the
      analytical and Monte Carlo methods

## Problem statement

The payoff of a spread call at maturity is

    max(S1_T - S2_T - K, 0)

**K = 0.** A closed-form solution exists: the Margrabe (1978) exchange option
formula. Factoring out S2_T turns the payoff into a call on the ratio S1/S2 with
strike 1. The ratio of two GBMs is lognormal, with volatility

    sigma_hat = sqrt(sigma1^2 + sigma2^2 - 2 * rho * sigma1 * sigma2)

so Black–Scholes applies to it. The price does not depend on the risk-free rate,
because the "strike" is paid in barrels of asset 2 rather than in dollars.

**K != 0.** No closed form exists, even under Black–Scholes. The difference of two
lognormal prices is not lognormal: it can be negative, and its volatility depends on
S1 and S2 separately, not only on their difference. Plugging a "spread volatility"
into the Black–Scholes formula gives a wrong price (4.88 $ against 8.95 $ by Monte
Carlo in our base case). Factoring out S2_T no longer helps either: the strike on the
ratio becomes 1 + K / S2_T, which is random. This is why so many approximations
exist, and why the project compares them against a Monte Carlo reference.

## Models and methods

Pricing an option needs two separate choices.

| | **Model** | **Pricing method** |
|---|---|---|
| Question | How do prices move? | Given the model, how do we compute the price? |
| Examples | bivariate GBM, Bachelier, Heston, Merton jumps | Monte Carlo, exact formula (Margrabe), approximations (Kirk, Li–Deng–Zhou, Carmona–Durrleman), Fourier, neural network |
| What it decides | **which** price and which deltas are right | **how fast and how precisely** we get them |
| How it is judged | realism, on real market data | speed and error against a reference, in simulation |

The premium and the hedge ratios (deltas) both come from the pair model + method.
A wrong method gives a slow or inaccurate number; a wrong model gives an accurate
number for the wrong question.

Most fast formulas are derived under one model and only make sense there:

| Method | GBM | Bachelier | Heston | Jumps |
|---|---|---|---|---|
| Monte Carlo | ✔ | ✔ | ✔ | ✔ |
| Margrabe (K = 0) | ✔ exact | | | |
| Kirk, Bjerksund–Stensland, Li–Deng–Zhou, Carmona–Durrleman | ✔ approximate | | | |
| Bachelier formula | | ✔ exact | | |
| Fourier | ✔ | ✔ | ✔ | ✔ |
| Neural network | ✔ | ✔ | ✔ | ✔ (retrained on each model) |

The working plan is to **keep the bivariate GBM**, replace Monte Carlo by a fast
formula so that daily hedging is practical, and change the model only if the
real-data tests show that the GBM is the problem.

## How the comparison is organised

### One hedging strategy, many deltas

The hedging strategy is the same throughout the project: every day, hold Δ1 units of
asset 1 and Δ2 units of asset 2, financed with cash, and rebalance the next day. Only
the values of the deltas change from one model or method to another. The hedging code
takes the delta function as an argument, so comparing methods in a hedge means
changing one line.

### A three-stage funnel

Crossing every model, method and parameter estimator would give dozens of hedging
experiments that nobody could read. Each stage changes one thing and keeps the rest
fixed at the winner of the previous stage.

| Stage | What varies | What is fixed | Data | Judged by | Notebook |
|---|---|---|---|---|---|
| 1. Methods | the pricing method | the model and its parameters | simulation | price and delta error against the model's reference, computation time | 04, and 01 for 2–3 methods |
| 2. Parameters | the estimator of σ1, σ2, ρ (historical, EWMA) | the best method | real | estimate vs value realised over the next year | 02, spread part |
| 3. Models | the model | each with its best method and the best estimator | real | real hedging P&L and hindsight P&L | 03, spread part |

- Stage 1 concludes on the best method **for a given model, in the parameter range of
  our data** (ρ between 0.7 and 0.97, K around the spread level). Each new model gets
  its own small stage 1 with the methods that apply to it (Heston: Monte Carlo vs
  Fourier).
- A method whose deltas match the reference gives the same hedge, so stage 1 mostly
  compares prices and deltas. Full hedging simulations are only run for a few methods,
  to show how delta errors turn into P&L dispersion.
- Using a GBM formula while the market is not a GBM is a model error. It shows up at
  stage 3, not at stage 1.
- All methods are run on the same base case, the same grid of K, ρ and T, and the
  same random seeds, and reported with the same indicators (mean, standard deviation,
  standard deviation / premium, worst 5 %, time).

### What simulation can answer, and what needs real data

| Question | Where it is answered | Why |
|---|---|---|
| Does a method compute its model's price? | simulation only | the right answer is known; on market data the errors mix |
| Does the hedge work when the model is true? (mean P&L ≈ 0, dispersion shrinking as 1/√n) | simulation (notebook 01) | same reason |
| Can σ1, σ2 and ρ be estimated before the trade? | real data (notebook 02) | compare the estimate with the value realised over the next year |
| Is the model realistic? | real data (notebook 03) | hedging P&L on real paths, then recomputed with the realised parameters: if this "hindsight" P&L is close to 0, the model is fine and the error comes from the parameters |
| Do our prices match quoted spread-option prices? | not feasible | no free spread-option quotes. The call study did not use option quotes either: everything is judged through hedging P&L on real price paths |

### The correlation ρ can be estimated, but it moves

ρ is not observed, but it can be estimated from free daily prices, exactly like σ.
Correlation of daily returns:

| | 2013 | 2015 | 2017 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| Brent / WTI | 0.70 | 0.86 | 0.93 | 0.92 | 0.46 | 0.97 | 0.94 | 0.97 | 0.96 |
| Heating oil / WTI | 0.67 | 0.72 | 0.85 | 0.91 | 0.40 | 0.95 | 0.61 | 0.71 | 0.85 |

Using last year's ρ for the next year gives a mean absolute error of 0.12 on
Brent / WTI (0.05 without 2020 and 2021) and 0.18 on heating oil / WTI. An error of
0.04 on ρ moves the spread-call price by about 18 %, so estimating ρ is expected to
be the main difficulty on real data.

## What has been done

### Single-asset foundation

The whole pricing and hedging chain was first built and tested on a single call on
Brent (`BZ=F`):

    estimate sigma  ->  premium (Black–Scholes)  ->  daily delta hedge  ->  P&L

| Notebook | Question | Main results |
|---|---|---|
| [`01_hedging_simulation`](notebooks/01_hedging_simulation.ipynb) | Does delta hedging work when the model is right? (simulated prices) | Mean P&L ≈ 0. With daily rebalancing the P&L standard deviation is 4.8 % of the premium, and it shrinks as 1/√n (log slope −0.48). One day of hedging = time decay (theta) earned minus the squared move paid (gamma); break-even at the "normal" daily move σ/√252. With a wrong volatility, the mean P&L equals the premium error (≈ 0.39 $ per volatility point) and a wrong delta adds dispersion. |
| [`02_volatility_estimation`](notebooks/02_volatility_estimation.ipynb) | Can sigma be forecast on January 1st? (Brent 2013–2024) | Mean absolute error on the next year's volatility: 14.7 pts with last year's historical volatility, 11.7 pts with EWMA (λ = 0.94). Neither foresees shocks such as 2020. |
| [`03_hedging_real_data`](notebooks/03_hedging_real_data.ipynb) | On real data, where does the hedging P&L come from? (12 one-year at-the-money calls on Brent, 2013–2024) | Mean absolute P&L: 3.49 $ with historical volatility, 2.15 $ with EWMA, 0.64 $ if the realized volatility of the year had been known, 0.23 $ if the remaining volatility had been known every day. Most of the error comes from not knowing sigma when the option is sold; the rest from volatility changing during the year (motivation for Heston). |

Modelling note: `BZ=F` is a futures price. The notebooks deliberately treat Brent
like a stock (Black–Scholes, r = 3 %); the final model should use the Black-76
versions of each formula (Black–Scholes overprices the 2023 at-the-money call by
about 12 %).

### Spread: Monte Carlo reference and Margrabe

Two correlated GBMs are built from independent shocks with
`Z2 = rho * Z1 + sqrt(1 - rho^2) * Z'`, which keeps a unit variance and gives a
correlation ρ. Base case: Brent 80 $, WTI 75 $, σ1 = 30 %, σ2 = 35 %, ρ = 0.6,
r = 3 %, one year.

| Check | Result |
|---|---|
| Simulated correlation / volatilities | 0.5998 / 29.99 % / 35.00 % |
| Monte Carlo price, K = 5 $ (100 000 paths) | 8.95 $ ± 0.04 |
| Effect of ρ on the K = 5 $ price (ρ = 0 / 0.6 / 0.9) | 14.01 / 8.95 / 4.61 $: the higher ρ, the calmer the spread, the cheaper the option |
| Margrabe, K = 0 (ρ = 0 / 0.6 / 0.9) | 16.76 / 11.78 / 7.65 $, against Monte Carlo 16.63 / 11.69 / 7.62 $, all within 2 standard errors |
| Effect of r on the K = 0 price | none: the Monte Carlo price is identical with r = 3 % and r = 10 % |
| Margrabe deltas (ρ = 0.6) | buy 0.643 barrel of Brent, sell 0.529 barrel of WTI; this hedge costs exactly the option price (11.78 $), with no borrowing |
| Computation time per price | Monte Carlo 5.8 ms, Margrabe 0.08 ms, Black–Scholes 0.09 ms |

Unit tests cover both ends of the chain: with S2 = 0 the spread call is a plain call
and Monte Carlo gives back Black–Scholes; with K = 0 Monte Carlo gives back
Margrabe. The second test is the one that checks the correlation: it fails if ρ is
dropped from the simulation or if the square root in the mixing formula is forgotten.

Known limits of the GBM reference: each leg stays positive, so a negative price
such as WTI at −37.63 $ on 20 April 2020 cannot occur; Monte Carlo is too slow and
too noisy for daily deltas (about 49 minutes for a 1 000-path hedging simulation);
the price is only exact if the GBM assumptions (constant σ1, σ2, ρ, no jumps) hold.

## Roadmap

Each step comes with its formula worked out on a small numerical example, a library
function, one unit test against a known case, and a notebook analysis.

**Phase A: model = bivariate GBM, reference method**

| # | Step | Status |
|---|---|---|
| A0 | Bivariate GBM + Monte Carlo, the reference for every other method | done |

**Phase B: fast methods under the same GBM model** (stage 1 of the funnel)

| # | Method | Idea | Accuracy / limits | Reference check | Status |
|---|---|---|---|---|---|
| B1 | **Margrabe (1978)** | exchange option, K = 0 | exact with exact deltas, but only for K = 0; first spread hedged in simulation | Monte Carlo ≈ Margrabe | price done; deltas and hedge next |
| B2 | **Kirk (1995)** | treat S2 + K as lognormal, Black-type formula | energy market standard; degrades for large K or ρ close to 1 | K = 0 gives Margrabe | planned |
| B3 | Modified Kirk (Bjerksund–Stensland) | correction of Kirk's formula | more accurate, still closed form | vs Monte Carlo | planned |
| B4 | Li–Deng–Zhou (2008) | second-order closed-form approximation | very accurate, heavier formula | vs Monte Carlo | planned |
| B5 | Carmona–Durrleman (2003) | optimised lower bound | very accurate, needs a numerical optimisation | vs Monte Carlo | planned |
| B6 | Fourier (Hurd–Zhou 2010) | price through a Fourier transform | near-exact and fast; most useful later under Heston | vs Monte Carlo | optional |
| B7 | Neural network (MLP) | learn the price from (S1, S2, K, σ1, σ2, ρ, T) | compare error and computation time with the formulas | vs Monte Carlo / Kirk on a test set | optional |

**Phase C: real data, still with the GBM** (stages 2 and 3; the spread, crack
`42 × HO − WTI` or `Brent − WTI`, is chosen before this phase)

| # | Step | Notebook |
|---|---|---|
| C1 | Estimate σ1, σ2 and ρ (historical, EWMA), estimate vs realised | 02, spread part |
| C2 | Real spread trade hedged with the best method of phase B; real P&L and hindsight P&L | 03, spread part |

**Phase D: other models**, used where phase C shows a model error (Heston is part
of the project brief in any case). Each one gets its own small stage 1, then a
real-data test.

| # | Model | What it fixes | Pricing methods | Reference check |
|---|---|---|---|---|
| D1 | **Bachelier** (normal spread) | negative spreads and prices (WTI in 2020) | closed form vs Monte Carlo | Monte Carlo on a normal spread |
| D2 | Bivariate Heston | volatility that changes during the year | Monte Carlo vs Fourier | vol of vol = 0 gives the GBM |
| D3 | Bivariate Merton jump-diffusion | shocks such as 2020 and 2022 | Monte Carlo (vs Fourier) | jump intensity = 0 gives the GBM |
| D4 | SABR | stochastic volatility, smile model | | optional |

**Phase E: implied volatility and correlation.** The implied volatility of a spread
option is not well defined: the price depends on three parameters (σ1, σ2, ρ) and a
single quote cannot pin down three unknowns. Two readings are possible:

1. **Implied correlation**: fix σ1 and σ2 at the implied volatilities quoted on each
   underlying and invert for ρ (the market convention in energy). The price
   decreases with ρ, so the inversion is stable.
2. **Implied spread volatility**: invert Margrabe for sigma_hat, which allows a
   strike × maturity surface comparable to a vanilla one.

Without free spread-option quotes, this phase can only demonstrate the method.

## Repository structure

    src/spread_options/   Core library
        products.py       payoffs (call, put, spread call)
        models.py         GBM terminal prices and paths, bivariate GBM paths
        monte_carlo.py    Monte Carlo pricing (call, put, spread call), returns (price, standard error)
        analytics.py      closed forms (Black–Scholes price and delta, Margrabe price)
        hedging.py        delta-hedging P&L along one or many paths (single asset)
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
- Every pricing method ships with a unit test against a known case
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
- Hull, J. C. *Options, Futures and Other Derivatives*, 11th ed., ch. 26.6, 27.2,
  27.7, 28.4–28.5.

## License

MIT, see [LICENSE](LICENSE).
