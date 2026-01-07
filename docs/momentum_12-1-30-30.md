# Momentum 12-1 (30/30) — Strategy Notes & Test Variants

## Base strategy name
**Momentum 12-1 (30/30), monthly rebalance**  
(AKA **cross-sectional momentum**: rank assets by prior 12-month return, skipping the most recent month; buy winners, optionally short losers.)

**Signal (per asset, monthly, using month-end prices):**
- **1M return (current holding month):** \( r_{t} = \log(P_t / P_{t-1}) \)
- **12-1 momentum (formation, excluding current month):** \( m_{t} = \log(P_{t-1} / P_{t-13}) \)

**Selection (each month):**
- Rank assets by \(m_t\)
- Winners = top **30%** (\(k = \lfloor 0.30 \cdot N\rfloor\))
- Losers  = bottom **30%** (same \(k\))

**Returns (your current reporting convention):**
- `winner_logret` = equal-weight mean log return of winners in month \(t\)
- `loser_long_logret` = equal-weight mean log return of losers in month \(t\) **held long** (diagnostic)
- `wml_spread_logret` = `winner_logret - loser_long_logret` (spread in log space)
- `wml_cap05_logret` = **2 ×** `wml_spread_logret` (your “0.5 capital” normalization)

> Note: “W−L” is a *spread*, not a return on net capital (net is ~0 in long–short). Your `cap05` convention makes the denominator explicit.

---

## Why dotcom-like decades can break it
Momentum tends to suffer in **sharp reversals**: last year’s leaders mean-revert violently, and the portfolio is concentrated in what just ran up.  
So you don’t remove the bad decade; you add risk controls that are **auditable** and **monthly**.

---

## Risk measurement you must use
Month-end-only drawdown understates risk. Use at least:
- **Path-aware Max Drawdown** (daily equity curve or “monthly low” computed from daily series)
- Worst rolling 12–36 month returns

---

## Fine-tuning levers (ranked by “least BS”)
### 1) Universe / data hygiene (biggest source of fake results)
- Expand beyond a modern hand-picked Nasdaq list.
- Control for survivorship bias (today’s winners survived; delisted names vanish from your sample).
- Test multiple universes (see test matrix below).

### 2) Signal variants
- 12-1 (baseline) vs 12-0 (no skip)
- 6-1 (faster)
- Composite: average z-score of 12-1 and 6-1

### 3) Portfolio construction
- Long-only winners (most investable baseline)
- Long–short only if you model collateral/margin and costs
- Weighting:
  - Equal-weight (baseline)
  - Volatility-scaled monthly (cap concentration)

### 4) Crash coping overlays (monthly, auditable)
- **Market regime filter:** only run momentum when benchmark is above a long MA (e.g., 10-month).
- **Volatility targeting:** scale exposure down when vol spikes.
- Optional tail clamp: **wide stop-loss** (only extreme moves; avoid whipsaw).

### 5) Costs & turnover
Momentum turnover is high. Always report:
- monthly turnover
- cost haircuts (spreads/slippage/fees) and sensitivity

---

## Test variants you should run (parameter sweep)
Keep everything else constant; change **one knob at a time**.

### A) Selection breadth (top/bottom %)
Test:
- 10% / 10%
- 20% / 20%
- 30% / 30% (baseline)
- 40% / 40%

Notes:
- Narrower (10–20%) = more concentrated, higher volatility, potentially higher edge (if real).
- Wider (40%) = smoother, more beta-like.

### B) Lookback / skip
Test:
- 12-1 (baseline)
- 12-0
- 6-1
- 6-0

### C) Rebalance frequency
- Monthly (baseline)
- Quarterly (lower turnover, often more robust after costs)

### D) Universe sets (tickers)
Run each variant over multiple universes:
1) Your **Nasdaq mega-cap** list (diagnostic / fast iteration)
2) Broader US universe you can source (preferred):
   - S&P 500 (constituents history ideal)
   - Russell 1000/3000 if possible
3) Sector-neutral universe (optional):
   - equal names per sector to reduce “tech bubble” concentration

**Implementation tip (simple):**
- Keep tickers in `config/universe.toml`
- Create multiple files:  
  `config/universe_nasdaq_mega.toml`, `config/universe_sp500.toml`, `config/universe_custom_X.toml`

---

## What to report for every run (minimum viable)
Monthly series + summary stats:
- CAGR, Vol, Sharpe (rf=0), MaxDD (path-aware)
- Worst rolling 12/36 month returns
- Turnover + cost sensitivity
- Concentration (top-5 contributions / effective N)
- Decade table (first/last decade can be partial)

---

## “Go / No-go” rules (practical)
- Must survive **all decades** with acceptable MaxDD (after path-aware DD).
- If you add an overlay, it must reduce drawdown **materially** without destroying CAGR, and it must be executable with **monthly checks**.
