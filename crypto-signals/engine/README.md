# SMC Opportunity Engine (backtest + paper trading)

An advanced spot-crypto opportunity engine. **It never places real orders.** There is no
exchange-order code in it, and `live_trading: true` in the config makes it exit with an error.

## Run

```
pip install pandas numpy requests
python crypto-signals/engine/run.py                          # uses config.json
python crypto-signals/engine/run.py --risk-profile test_500  # try the ₹500 profile (capped by max_risk_pct)
```
Open `crypto-signals/engine/report.html`. On GitHub it runs every 4 hours by itself
(Actions → "Crypto Signals"). New paper entries and waiting limit setups open a `[PAPER]` Issue.

## What it detects (`smc.py`, no look-ahead)

| Feature | Rule |
|---|---|
| Swing highs/lows | pivot with 3 candles each side, usable only after confirmation |
| **BOS** | close beyond the last swing in the direction of the current structure |
| **MSS** | close beyond the last swing *against* the current structure (shift) |
| **Liquidity sweep** | wick through an unbroken swing high/low that closes back inside |
| **Order block** | last opposite-colour candle before the structure break |
| **Fair value gap** | 3-candle imbalance `low[i] > high[i-2]` (bullish), ≥ 0.1 ATR |
| Volume | candle volume ÷ previous 20-candle average |
| Volatility | ATR(14), and its percentile vs. the last 500 candles (Low/Norm/High regime) |
| Multi-timeframe | entries on 4h, trend filter from the **closed** daily candle (EMA 50/200) |

## Setups (`backtest.py`)
1. **Breakout**: BOS/MSS close + volume ≥ 1.5× + strong candle + daily uptrend → market entry next candle.
2. **Sweep+MSS**: liquidity sweep → MSS with displacement → limit at FVG midpoint / order block, stop below the sweep.
3. **OB/FVG Retest**: BOS in a daily uptrend → limit at the top of the order block, stop below it.
4. **Combined**: all of them, one position per coin.

Stops are structural with an ATR buffer. Setups whose stop is too wide (over 3–4 ATR) are skipped.

## Exit profiles
`rr_targets` × `exit_modes` = 8 profiles: 1:2, 1:3, 1:5, 1:10, each **fixed** (stop + one target) or **managed**:
- partial profit (50%) at min(2R, target/2)
- stop moved to break-even (+fees) at 1R
- ATR trailing stop (2.5 ATR from the high) after the partial
- trend-reversal exit (bearish structure break or daily trend turns bear)
- volatility exit (bearish candle bigger than 2.5 ATR)
- time exit after 180 candles (30 days)

## Capital protection (`config.json`)
- `capital_inr` (e.g. 10000–25000) and `max_risk_pct` (default 1%, hard limit 5%).
- `risk_profiles.test_500` asks for ₹500 per trade, but it is **always capped** at `max_risk_pct` of capital.
  At ₹10,000 and 1% you get ₹100. To really allow ₹500 you must raise `max_risk_pct` yourself
  (5% on ₹10k, 2% on ₹25k).
- Position size = risk ÷ stop distance, never more than free cash (spot, no leverage).
- `max_open_trades`, `min_order_inr`, and a **kill-switch** that stops new trades after `kill_switch_drawdown_pct` drawdown.
- `allow_short` is `false`: spot only. Bearish structure is used to exit, not to short.

## Testing honesty
- Fees 0.1% and slippage 0.05% per side. If stop and target are in the same candle, the stop is assumed hit first.
- First 70% of history = in-sample; last 30% = **out-of-sample**, reported separately.
- Metrics: win rate, average win/loss (₹), net after fees, estimated net after 30% Indian crypto tax
  (losses can't offset gains), profit factor, max drawdown, longest losing streak, average R.
- "Which target works in which market" picks the best profile per regime in-sample, then shows the OOS result.
- 1% TDS is a tax credit/cash-flow item and is not modelled.

## Paper trading
`paper.start` sets the forward-test start date. Every run replays the rules on candles after that date
(closed candles only), so the paper record is reproducible. Waiting limit orders are listed as
"current opportunities" with a suggested size. They are for observation, not instructions to trade.
