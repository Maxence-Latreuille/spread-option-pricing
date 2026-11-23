# Spread Option Pricing

Pricing and hedging of options written on the price spread between two
assets, with an application to energy markets (Brent, WTI, heating oil).

**Status:** the single-asset foundation (Black–Scholes call, delta hedging,
volatility estimation, real-data backtest on Brent) is done. On the spread side,
the bivariate GBM with its Monte Carlo reference, Margrabe's exact price and deltas
(K = 0) and two-asset delta hedging are implemented and tested. Next: notebook 04
(simulation lab: accuracy, speed, hedging) with Monte Carlo and Margrabe as its first
rows, then Kirk (see the [roadmap](#roadmap-the-master-table)).

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
- [x] Hedge a spread option in simulation (Margrabe deltas, two-asset delta hedge)
- [ ] Hedge a real spread trade with σ1, σ2 and ρ estimated from data
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

## How the project is organised

Every model and every pricing method is looked at through three lenses.

| Lens | Question | Where |
|---|---|---|
| **1. Simulation lab** | Inside a model we control, does the method give the right price and deltas, how fast, and does its hedge work? | notebook 04 (one table per criterion) |
| **2. Real market** | Can the parameters be estimated, and does the model survive real price paths? | notebooks 02 and 03 |
| **3. Desk practice** | Do trading desks use it, for what, and why did they pick it over the others? | literature, one column of the master table below |

A model or method is never studied in a notebook of its own. Each one brings a
library function, a unit test against a known case, and **one row** in the shared
tables. Adding the fifteenth method costs as much as adding the second.

### Lens 1: the simulation lab (notebook 04)

Prices are simulated from the model itself, so the right answer is known. The
notebook has three fixed sections, one per criterion, and each method adds one row
to each.

| Section | Criterion | Measured as | Reference |
|---|---|---|---|
| 1 | **Accuracy** | price error and delta error, over a common grid of K, ρ and T around our data (ρ from 0.7 to 0.97, K around the spread level) | the model's exact formula when one exists, else Monte Carlo with many paths |
| 2 | **Speed** | milliseconds per price, and per pair of deltas | — |
| 3 | **Hedging** | daily delta hedge on 1 000 simulated paths: mean P&L (≈ 0 if the price is right), standard deviation / premium, worst 5 % | the call of notebook 01: 4.8 % of the premium with daily rebalancing |

All rows use the same base case (Brent 80 $, WTI 75 $, σ1 = 30 %, σ2 = 35 %,
ρ = 0.6, r = 3 %, one year), the same grid and the same random seeds. The hedging
strategy itself is fixed for the whole project and was validated once, on the call,
in notebook 01: every day, hold Δ1 units of asset 1 and Δ2 units of asset 2 financed
with cash. Only the delta function changes from one row to the next.

Each model gets its own block of rows with the methods that apply to it (under
Heston: Monte Carlo vs Fourier). Using a GBM formula while the market is not a GBM is
a model error: it is measured with real data (lens 2), not here.

### Lens 2: real market (notebooks 02 and 03)

| Notebook | Question | How |
|---|---|---|
| 02 | Can σ1, σ2 and ρ be forecast before the trade? | estimate (historical, EWMA) vs value realised over the next year |
| 03 | Is the model realistic? | real hedging P&L, then the same hedge recomputed with the realised parameters ("hindsight" P&L): close to 0 means the model is fine and the error comes from the parameters; far from 0 means the model itself is wrong. One row per model. |

Spread-option quotes are not freely available, so prices are never compared with
market quotes: everything is judged through hedging P&L on real price paths, as for
the call.

### Lens 3: desk practice

For each model and method, the report states who uses it and why, with a source.
What is already established:

- **Kirk's formula** is the most popular spread-option formula among market
  participants ([Probability in the Engineering and Informational Sciences, 2023](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/A6FCDA861E587A47FDE425744FE60996/S0269964823000049a.pdf/a-closed-form-approximation-for-pricing-spread-options-on-futures-under-a-mean-reverting-spot-price-model-with-multiscale-stochastic-volatility.pdf)).
  Bjerksund and Stensland showed that it underprices near K = 0 and overprices
  further away, which motivates their correction ([MathWorks documentation](https://uk.mathworks.com/help/fininst/pricing-european-and-american-spread-options.html)).
- **Bachelier**: when WTI futures went negative on 20 April 2020, CME Clearing
  switched its energy options valuation to the Bachelier model, effective 22 April
  2020 ([CME advisory 20-171](https://www.cmegroup.com/notices/clearing/2020/04/Chadv20-171.html)).
- **Black-76**: energy options are written on futures, so desks use the futures
  versions of the formulas (no carry term). Our notebooks treat Brent like a stock;
  the final model switches to Black-76.
- **Monte Carlo** is kept for products with no formula (path-dependent, many assets);
  it is too slow and too noisy for daily deltas on a whole book.
- **Fixing the model by hand**: desks keep simple models but feed them a different
  implied volatility (and implied correlation) per strike and maturity, which is
  objective 4 of the project.
- Still to document: how desks quote and calibrate implied correlation (and its
  skew across strikes), and which models are used for crack spreads.

### Why the GBM + Monte Carlo reference is not enough

It is right inside its own world, but:

| Limit | Kind | Seen where | Answered by |
|---|---|---|---|
| Monte Carlo: 5.8 ms per price, noisy deltas (Δ1 = 0.56 or 0.39 depending on the seeds), 49 min for a 1 000-path hedge | method | spread notebooks so far | fast methods (B) |
| Prices stay positive; WTI closed at −37.63 $ on 20 April 2020 | model | Yahoo data | Bachelier (D1) |
| Constant volatility; it moves by 14.7 points a year on Brent | model | notebooks 02, 03 | Heston (D2) |
| No jumps (2020, 2022) | model | notebook 03 (hindsight P&L +1.80 $ in 2022) | Merton (D3) |
| Constant ρ; Brent / WTI went from 0.92 in 2019 to 0.46 in 2020 | parameter | correlation table below | estimation (C1) |
| Energy spreads tend to revert to a normal level (refining or transport cost); the GBM lets them drift away | model | to be measured on our data | mean-reverting spread model (D5) |
| One volatility for every strike, while markets show a smile | model | objective 4 | implied vol / correlation (E) |

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
| Daily Margrabe hedge, 100 simulated paths | mean P&L +0.03 $, standard deviation 0.52 $ (4.4 % of the premium; 4.8 % for the call) |
| Computation time per price | Monte Carlo 5.8 ms, Margrabe 0.08 ms, Black–Scholes 0.09 ms |

Unit tests cover both ends of the chain: with S2 = 0 the spread call is a plain call
and Monte Carlo gives back Black–Scholes; with K = 0 Monte Carlo gives back
Margrabe. The second test is the one that checks the correlation: it fails if ρ is
dropped from the simulation or if the square root in the mixing formula is forgotten.

## Roadmap: the master table

Each row follows the same recipe: formula worked out on a small numerical example,
library function, one unit test against a known case, then one row in each table of
notebook 04 and a line of desk practice in the report.

**Phases.** A: reference. B: fast methods under the GBM (simulation lab).
C: real data with the best GBM method (choose the spread first: crack
`42 × HO − WTI` or `Brent − WTI`). D: other models, each with its own methods.
E: implied volatility and correlation.

| # | Model | Method | Kind | Simulation lab (notebook 04) | Real data | Desk practice | Status |
|---|---|---|---|---|---|---|---|
| A0 | GBM | Monte Carlo | reference | reference for the others; 5.8 ms per price | — | products with no formula | done |
| B1 | GBM | Margrabe (K = 0) | exact | exact price and deltas; 0.08 ms; daily hedge mean ≈ 0, std ≈ 4–5 % of premium | — | the base of Kirk | done |
| B2 | GBM | **Kirk (1995)** | approximation | | 03 | most popular formula on desks | next |
| B3 | GBM | Bjerksund–Stensland (2014) | approximation | | | correction of Kirk's known bias | planned |
| B4 | GBM | Li–Deng–Zhou (2008) | approximation | | | academic, very accurate | planned |
| B5 | GBM | Carmona–Durrleman (2003) | lower bound | | | academic | planned |
| B6 | GBM | Fourier (Hurd–Zhou 2010) | numerical | | | to document | planned |
| B7 | GBM | Neural network (MLP) | learned | | | to document | planned |
| C1 | GBM | estimators of σ1, σ2, ρ (historical, EWMA) | parameters | — | 02 | to document | planned |
| C2 | GBM | best method of B | real trade | — | 03 | — | planned |
| D1 | **Bachelier** | closed form, vs Monte Carlo | exact | | 03 | CME clearing since April 2020 | planned |
| D2 | Heston (bivariate) | Monte Carlo, vs Fourier | reference / numerical | | 03 | to document | planned |
| D3 | Merton jumps (bivariate) | Monte Carlo | reference | | 03 | to document | planned |
| D4 | SABR | Hagan's formula | approximation | | | smile model, to document for energy | optional |
| D5 | Mean-reverting spread (Ornstein–Uhlenbeck) | closed form, vs Monte Carlo | exact | | 03 | to document | planned |
| E | any | invert Kirk or Margrabe for ρ or the spread volatility | implied | method only (no free quotes) | | implied correlation, smile | planned |

**Phase E in detail.** The implied volatility of a spread option is not well defined:
the price depends on three parameters (σ1, σ2, ρ) and one quote cannot pin down three
unknowns. Two readings: fix σ1 and σ2 at the implied volatilities quoted on each leg
and invert for ρ (implied correlation, the energy-market convention; stable because
the price decreases with ρ), or invert Margrabe for sigma_hat to draw a strike ×
maturity surface.

## Repository structure

    src/spread_options/   Core library
        products.py       payoffs (call, put, spread call)
        models.py         GBM terminal prices and paths, bivariate GBM paths
        monte_carlo.py    Monte Carlo pricing (call, put, spread call), returns (price, standard error)
        analytics.py      closed forms (Black–Scholes price and delta, Margrabe price and deltas)
        hedging.py        delta-hedging P&L along one or many paths (one asset, or two for a spread)
        volatility.py     volatility estimators (historical, EWMA)
        data.py           daily prices from Yahoo Finance
    tests/                Unit tests (pytest), one meaningful test per function
    notebooks/            Analyses and figures for the report (01–03 done, 04 simulation lab next)

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
