# Spread Option Pricing & Hedging

Research project on the pricing, Greeks and dynamic hedging of spread options, applied to Brent–WTI and other energy spreads.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Research status](https://img.shields.io/badge/Status-Research%20in%20Progress-orange)

**École Centrale de Lyon · Research Application Project (PAr) · 2026–2027**  
**Authors:** [Maxence Latreuille](https://maxencelatreuille.com) and Elliot Béreau  
**Academic supervisor:** Christian de Peretti

---

## Overview

A spread option pays on the difference between two prices. Commodity markets trade them because the gap between two prices carries its own risk: transport costs, refining margins, supply and demand imbalances, disruptions.

A spread option depends on two price processes, their volatilities and their correlation. Even when both prices follow geometric Brownian motions (GBMs), their difference is not lognormal, so the Black–Scholes formula no longer applies and valuation and hedging get harder.

**Research question:** *How should pricing accuracy, computational efficiency, and hedging risk be balanced when selecting a model and valuation method for energy spread options?*

The project builds a modular Python framework to:

1. price European spread options with exact formulas, approximations and numerical methods;
2. compute their Greeks and delta-hedge them with two underlyings;
3. benchmark the methods in simulation on pricing error, Greeks error, runtime and hedging P&L;
4. measure model risk on historical commodity prices, with parameters estimated out of sample;
5. compare the findings with what trading desks do (futures conventions, calibration, computing constraints).

## The product

The payoff of a European spread call at maturity is

$$
\boxed{\mathrm{Payoff}_T=\max(S_{1,T}-S_{2,T}-K,\,0)}
$$

where $S_{1,T}$ and $S_{2,T}$ are the terminal prices and $K$ is the strike on their spread.

- $K=0$ (exchange option): Margrabe's formula gives the exact price and deltas under correlated GBMs. The payoff can be written $S_{2,T}\max(S_{1,T}/S_{2,T}-1,0)$, a call on the price ratio, which is lognormal.
- $K\neq0$ (general spread call): the difference of two correlated lognormal prices is not lognormal and no exact formula exists. Prices come from Monte Carlo, from approximations such as Kirk's, or from other numerical methods.

The main case study is Brent against WTI crude oil, possibly extended to the heating oil–WTI spread and other commodity pairs.

## Research design

The project separates three choices:

| Layer | Question | Examples |
|---|---|---|
| Market model | How do prices evolve? | Bivariate GBM, Bachelier, Heston, jump diffusion |
| Pricing method | How is the option value computed *within the model*? | Monte Carlo, Margrabe, Kirk, Fourier methods |
| Hedging strategy | Which positions offset the option's market exposure? | Two-asset dynamic delta hedging |

A method can compute a wrong model's price very accurately, and a sensible model can be computed with a slow or inaccurate method, so models and methods are judged separately.

### 1. Controlled simulation: validating methods

Prices are simulated from a chosen model with known parameters, so the right answer is known. The methods that apply to that model are compared on the same test grid.

| Criterion | Measurements |
|---|---|
| Pricing accuracy | Absolute/relative error against an exact solution, when available, or high-precision Monte Carlo |
| Greeks accuracy | Errors in $\Delta_1$, $\Delta_2$, and selected higher-order sensitivities |
| Computational cost | Runtime per price and per pair of deltas |
| Hedging performance | Mean terminal P&L, P&L standard deviation, and downside risk |
| Numerical robustness | Convergence, sampling uncertainty, and sensitivity to numerical settings |

### 2. Historical data: parameter and model risk

Historical commodity prices are used to study:

- how well volatility and correlation can be estimated and forecast;
- how much a hedge loses when its parameters are wrong;
- what happens in stress periods, when volatility and correlation regimes change;
- where the constant-volatility, constant-correlation and continuous-path assumptions break.

A backtest on historical prices with a premium computed by the model is a model experiment, not the P&L of a traded option. Checking prices against market quotes would need historical option data.

### 3. Desk practice: how models are chosen

The project reviews the constraints behind a desk's choice: speed of prices and Greeks, calibration, scenario risk, futures specifications, collateral and margining, transaction costs, and model governance. Each claim about industry practice cites a publication or exchange documentation.

## Mathematical baseline

### Bivariate geometric Brownian motion

The initial model uses two correlated price processes:

$$
\frac{dS_{1,t}}{S_{1,t}}=\mu_1dt+\sigma_1dW_{1,t},\qquad
\frac{dS_{2,t}}{S_{2,t}}=\mu_2dt+\sigma_2dW_{2,t}
$$

with instantaneous Brownian correlation $\rho$. Correlated standard-normal shocks are generated by

$$
Z_2=\rho Z_1+\sqrt{1-\rho^2}\,Z',\qquad Z_1,Z'\sim\mathcal N(0,1)\text{ independently}.
$$

### Monte Carlo valuation

Under the model's risk-neutral pricing measure, the European spread-call price is

$$
C_0=e^{-rT}\,\mathbb E^{\mathbb Q}\!\left[\max(S_{1,T}-S_{2,T}-K,0)\right].
$$

Monte Carlo estimates this expectation from simulated correlated terminal prices. The estimate carries sampling error and converges to the model price, which need not match a market quote.

### Margrabe exchange option ($K=0$)

For two non-dividend-paying traded assets under correlated GBM assumptions,

$$
\hat\sigma=\sqrt{\sigma_1^2+\sigma_2^2-2\rho\sigma_1\sigma_2},
$$

$$
C_0=S_{1,0}N(d_1)-S_{2,0}N(d_2),
\quad d_1=\frac{\ln(S_{1,0}/S_{2,0})+\tfrac12\hat\sigma^2T}{\hat\sigma\sqrt T},
\quad d_2=d_1-\hat\sigma\sqrt T.
$$

Its analytical deltas are

$$
\boxed{\Delta_1=N(d_1),\qquad\Delta_2=-N(d_2).}
$$

The seller of an exchange option therefore holds asset 1 and is short asset 2 in the idealized replication portfolio.

### Dynamic hedging

The hedge rebalances both positions along each simulated path and compares the final portfolio with the option payoff. The residual P&L measures the cost of rebalancing at discrete dates and, in later experiments, of pricing or parameter errors.

> Futures caveat: the first notebooks use simplified spot-style formulas, while Yahoo Finance series such as `BZ=F` are futures. A consistent futures framework (futures dynamics, contract maturities, rolls, daily margin flows) is a modelling priority. The Margrabe hedge here holds the assets themselves, which a desk hedging with futures would not do.

## Implementation status

| Component | Status |
|---|---|
| European call/put and spread payoffs | Done |
| Black–Scholes call price and delta | Done |
| Single-asset GBM simulation and delta hedging | Done |
| Historical and EWMA volatility estimators | Done |
| Bivariate GBM and correlated-path simulation | Done |
| Monte Carlo spread-call pricing | Done |
| Margrabe price and analytical deltas ($K=0$) | Done |
| Two-asset simulated delta hedging | Done |
| Unified multi-method benchmark | In progress |
| Monte Carlo deltas for nonzero-strike spreads | Planned |
| Kirk and other fast approximations | Planned |
| Historical two-asset spread hedge | Planned |
| Stochastic volatility, jumps, and further models | Planned |
| Market-implied volatility/correlation calibration | Planned |

### First numerical results

Base case: $S_{1,0}=\$80$, $S_{2,0}=\$75$, $\sigma_1=30\%$, $\sigma_2=35\%$, $\rho=0.6$, and $T=1$ year.

| Experiment | Result |
|---|---|
| Monte Carlo spread call, $K=\$5$ | \$8.95, standard error \$0.04 (100,000 paths) |
| Margrabe exchange option, $K=0$ | \$11.78 |
| Margrabe delta hedge at inception | $\Delta_1\approx+0.643$, $\Delta_2\approx-0.529$ |
| Margrabe daily hedge, 100 simulated paths | mean terminal P&L +\$0.03, standard deviation \$0.52 |

These are simulation results under stated assumptions, not market quotes. Runtimes depend on the machine and the code, and hedging statistics from a small sample are rough.

## Notebooks

| Notebook | Main question | Scope |
|---|---|---|
| [01 Hedging simulation](notebooks/01_hedging_simulation.ipynb) | Does delta hedging behave as expected when model assumptions hold? | Simulated single-asset call; hedging frequency, replication error, parameter sensitivity |
| [02 Volatility estimation](notebooks/02_volatility_estimation.ipynb) | How accurately can volatility be estimated from past data? | Historical and EWMA estimators |
| [03 Hedging on real data](notebooks/03_hedging_real_data.ipynb) | How does hedging behave on historical Brent prices? | Historical single-asset experiments and hindsight diagnostics |
| 04 Methods comparison *(planned)* | Which pricing methods best trade off accuracy, runtime, and risk? | Shared benchmark for spread pricing, Greeks, and hedging |

The single-asset notebooks set up the method before moving to spreads. Simulation under a known model and backtests on historical prices answer different questions, so both are kept.

## Roadmap

Every model and method is compared on the same metrics, in shared tables; none gets a separate study of its own.

### Phase A: benchmark infrastructure

- [x] Build correlated two-asset GBM paths and Monte Carlo spread pricing.
- [x] Implement Margrabe pricing and deltas for $K=0$.
- [x] Implement a reusable two-asset hedging engine.
- [ ] Publish the unified comparison notebook.
- [ ] Implement and validate Monte Carlo delta estimators for $K\neq0$.

### Phase B: pricing methods under correlated GBM

- [ ] Kirk (1995): fast approximation for $K\neq0$.
- [ ] Bjerksund–Stensland (2014): alternative spread-option approximation.
- [ ] Li–Deng–Zhou (2008): refined approximation of prices and Greeks.
- [ ] Carmona–Durrleman (2003): pricing bounds and analytical approximations.
- [ ] Fourier pricing: transform-based numerical methods.
- [ ] Neural-network surrogate (MLP): accuracy against training and evaluation cost.

### Phase C: parameter estimation and spread hedging on real data

- [ ] Estimate and forecast $\sigma_1$, $\sigma_2$, and $\rho$ from aligned historical prices.
- [ ] Select and document a consistent spread contract convention (e.g., Brent–WTI).
- [ ] Backtest two-asset hedges using only information available at each decision date.
- [ ] Explore costs, financing assumptions, and out-of-sample robustness.

### Phase D: other market models

- [ ] Bachelier (normal dynamics): additive price changes and negative prices.
- [ ] Bivariate Heston: stochastic volatility.
- [ ] Jump diffusion: price jumps.
- [ ] SABR: volatility smile, where it fits.
- [ ] Mean-reverting spread: test whether commodity spreads revert to a normal level.

### Phase E: market-implied parameters

- [ ] Investigate implied correlation and implied spread/ratio volatility.
- [ ] Study strike and maturity dependence using market quotes, if available.
- [ ] Keep calibration to market prices apart from the simulation experiments.

An analytical formula is only valid in the model it was derived for, so each model is compared against its own reference method, with its assumptions stated.

## Repository layout

```text
spread-option-pricing/
├── src/spread_options/
│   ├── analytics.py       # Black–Scholes and Margrabe formulas / Greeks
│   ├── models.py          # GBM simulations, including correlated paths
│   ├── monte_carlo.py     # Numerical option pricing and standard errors
│   ├── hedging.py         # Single- and two-asset delta-hedging P&L
│   ├── products.py        # Option payoffs
│   ├── volatility.py      # Historical and EWMA estimators
│   └── data.py            # Market-data utilities
├── notebooks/
│   ├── 01_hedging_simulation.ipynb
│   ├── 02_volatility_estimation.ipynb
│   └── 03_hedging_real_data.ipynb
├── tests/                 # Pytest tests
├── spread_data.csv        # Research data
├── pyproject.toml
├── requirements.txt
├── Sujet_PAr.pdf           # Academic project description
└── README.md
```

Pricing and hedging code lives in `src/`; the notebooks import it and only hold experiments and figures.

## Getting started

```bash
# Clone the repository
git clone https://github.com/Maxence-Latreuille/spread-option-pricing.git
cd spread-option-pricing

# Create a virtual environment
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Install dependencies and the local package:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Run the test suite:

```bash
python -m pytest -q
```

Then open the notebooks in Jupyter.

## References

Foundations:

- Bachelier, L. (1900). *Théorie de la spéculation*.
- Black, F. (1976). *The Pricing of Commodity Contracts*.
- Margrabe, W. (1978). *The Value of an Option to Exchange One Asset for Another*.
- Merton, R. C. (1976). *Option Pricing When Underlying Stock Returns Are Discontinuous*.
- Heston, S. L. (1993). *A Closed-Form Solution for Options with Stochastic Volatility*.

Spread-option methods:

- Kirk, E. (1995). *Correlation in the Energy Markets*.
- Carmona, R., & Durrleman, V. (2003). *Pricing and Hedging Spread Options*.
- Li, M., Deng, S.-J., & Zhou, J. (2008). *Closed-Form Approximations for Spread Option Prices and Greeks*.
- Hurd, T. R., & Zhou, Z. (2010). *A Fourier Transform Method for Spread Option Pricing*.
- Bjerksund, P., & Stensland, G. (2014). *Closed Form Spread Option Valuation*.

Market practice and documentation:

- [CME Clearing advisory 20-171 (2020)](https://www.cmegroup.com/notices/clearing/2020/04/Chadv20-171.html): energy options valuation changes after WTI futures went negative.
- [MathWorks: Pricing European and American Spread Options](https://uk.mathworks.com/help/fininst/pricing-european-and-american-spread-options.html).
- Hull, J. C. *Options, Futures, and Other Derivatives*.

For the academic assignment, see [Sujet_PAr.pdf](Sujet_PAr.pdf).

## Academic context and license

Projet d'Application Recherche (PAr), École Centrale de Lyon, academic year 2026–2027, supervised by Christian de Peretti.

**Authors:** [Maxence Latreuille](https://maxencelatreuille.com) · Elliot Béreau

Released under the [MIT License](LICENSE). This is a research and teaching project, not a trading system or an investment recommendation.
