#!/usr/bin/env python3
"""
Crypto Signal System (educational).

What it does
  1. Downloads real candle data (public Binance market-data API, no account needed).
  2. Computes trend (EMA 20/50/200), RSI, ATR, volume spikes,
     support/resistance (swing pivots) and candlestick patterns.
  3. Produces BUY / SELL / NO-TRADE signals with entry, stop-loss and targets.
  4. Backtests the exact same rules on past data (with fees) so you can see
     the REAL historical win-rate - not a promised one.
  5. Optional: sends Telegram alerts and keeps running in a loop.

Usage
  python3 signals.py                    # analyse + backtest, writes report.html
  python3 signals.py --loop 15          # re-check every 15 minutes, alert on new signals
  python3 signals.py --symbols BTCUSDT ETHUSDT --interval 1h

This is NOT financial advice. No strategy is guaranteed.
"""
import argparse
import datetime as dt
import html
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import requests

API = "https://data-api.binance.vision/api/v3/klines"
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
FEE = 0.001          # 0.1% per side (typical spot taker fee)
PIVOT_K = 5          # bars on each side for a swing high/low
VOL_SPIKE = 1.5      # volume must be 1.5x its 20-bar average
SL_ATR = 1.5         # stop-loss distance in ATRs (minimum)
TARGETS_R = (1.5, 3.0)
HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------- data
def fetch(symbol, interval, bars):
    """Download the last `bars` CLOSED candles."""
    out, end = [], None
    while len(out) < bars:
        params = {"symbol": symbol, "interval": interval, "limit": 1000}
        if end:
            params["endTime"] = end
        r = requests.get(API, params=params, timeout=20)
        r.raise_for_status()
        chunk = r.json()
        if not chunk:
            break
        out = chunk + out
        end = chunk[0][0] - 1
        if len(chunk) < 1000:
            break
    df = pd.DataFrame(out, columns=["t", "open", "high", "low", "close", "volume",
                                    "ct", "qv", "n", "tb", "tq", "x"])
    df = df.drop_duplicates("t").sort_values("t")
    df = df[df["ct"] < time.time() * 1000]          # drop the still-forming candle
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df["time"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    return df[["time", "open", "high", "low", "close", "volume"]].tail(bars).reset_index(drop=True)


# ----------------------------------------------------------- indicators
def add_indicators(df):
    c = df["close"]
    for n in (20, 50, 200):
        df[f"ema{n}"] = c.ewm(span=n, adjust=False).mean()
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi"] = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - c.shift()).abs(),
                    (df["low"] - c.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    df["vol_avg"] = df["volume"].rolling(20).mean().shift(1)
    df["vol_ratio"] = df["volume"] / df["vol_avg"]

    # swing pivots - a pivot at bar i is only KNOWN at bar i+K (no look-ahead)
    h, l, k = df["high"], df["low"], PIVOT_K
    win = 2 * k + 1
    df["pivot_high"] = h.where(h == h.rolling(win, center=True).max())
    df["pivot_low"] = l.where(l == l.rolling(win, center=True).min())
    # value of the most recent CONFIRMED pivot, as seen at each bar
    df["last_res"] = df["pivot_high"].shift(k).ffill()
    df["last_sup"] = df["pivot_low"].shift(k).ffill()

    add_patterns(df)
    return df


def add_patterns(df):
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    body = (c - o).abs()
    rng = (h - l).replace(0, np.nan)
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    po, pc = o.shift(), c.shift()
    df["bull_engulf"] = (c > o) & (pc < po) & (c >= po) & (o <= pc)
    df["bear_engulf"] = (c < o) & (pc > po) & (c <= po) & (o >= pc)
    df["hammer"] = (lower >= 2 * body) & (upper <= body) & (body / rng > 0.1)
    df["shooting_star"] = (upper >= 2 * body) & (lower <= body) & (body / rng > 0.1)
    df["doji"] = body / rng < 0.1
    # morning / evening star (3 candles)
    big1 = body.shift(2) > df["atr"].shift(2) * 0.6
    small2 = body.shift(1) < df["atr"].shift(1) * 0.3
    mid1 = (o.shift(2) + c.shift(2)) / 2
    df["morning_star"] = big1 & (c.shift(2) < o.shift(2)) & small2 & (c > o) & (c > mid1)
    df["evening_star"] = big1 & (c.shift(2) > o.shift(2)) & small2 & (c < o) & (c < mid1)


BULL_PATTERNS = {"bull_engulf": "Bullish Engulfing", "hammer": "Hammer", "morning_star": "Morning Star"}
BEAR_PATTERNS = {"bear_engulf": "Bearish Engulfing", "shooting_star": "Shooting Star", "evening_star": "Evening Star"}


# ---------------------------------------------------------------- rules
def signal_at(df, i):
    """Evaluate the rules on CLOSED bar i. Returns dict or None."""
    r = df.iloc[i]
    prev = df.iloc[i - 1]
    if np.isnan(r["ema200"]) or np.isnan(r["vol_ratio"]) or np.isnan(r["last_res"]):
        return None
    up_trend = r["close"] > r["ema200"] and r["ema50"] > r["ema200"]
    dn_trend = r["close"] < r["ema200"] and r["ema50"] < r["ema200"]
    vol_ok = r["vol_ratio"] >= VOL_SPIKE
    bull_pat = [n for k, n in BULL_PATTERNS.items() if r[k]]
    bear_pat = [n for k, n in BEAR_PATTERNS.items() if r[k]]
    atr = r["atr"]
    sig = None

    # 1) Breakout: close above last swing-high resistance with a volume spike
    if up_trend and vol_ok and prev["close"] <= r["last_res"] < r["close"] and r["rsi"] < 75:
        sig = ("BUY", "Breakout", r["last_res"])
    # 2) Breakdown: close below last swing-low support with a volume spike
    elif dn_trend and vol_ok and prev["close"] >= r["last_sup"] > r["close"] and r["rsi"] > 25:
        sig = ("SELL", "Breakdown", r["last_sup"])
    # 3) Pullback buy: uptrend, price dips to EMA50 / support, bullish candle
    elif up_trend and bull_pat and 35 <= r["rsi"] <= 60 and (
            abs(r["low"] - r["ema50"]) <= 0.5 * atr or abs(r["low"] - r["last_sup"]) <= 0.5 * atr):
        sig = ("BUY", "Pullback + " + "/".join(bull_pat), r["low"])
    # 4) Pullback sell: downtrend, price rallies to EMA50 / resistance, bearish candle
    elif dn_trend and bear_pat and 40 <= r["rsi"] <= 65 and (
            abs(r["high"] - r["ema50"]) <= 0.5 * atr or abs(r["high"] - r["last_res"]) <= 0.5 * atr):
        sig = ("SELL", "Pullback + " + "/".join(bear_pat), r["high"])
    if not sig:
        return None

    side, setup, level = sig
    entry = r["close"]
    if side == "BUY":
        sl = min(r["low"], level) - 0.2 * atr
        sl = min(sl, entry - SL_ATR * atr)
        risk = entry - sl
        tps = [entry + m * risk for m in TARGETS_R]
    else:
        sl = max(r["high"], level) + 0.2 * atr
        sl = max(sl, entry + SL_ATR * atr)
        risk = sl - entry
        tps = [entry - m * risk for m in TARGETS_R]

    score = 40                                         # trend aligned (required)
    score += 20 if vol_ok else 0
    score += 20 if (bull_pat if side == "BUY" else bear_pat) else 0
    score += 10 if (r["ema20"] > r["ema50"]) == (side == "BUY") else 0
    score += 10 if (45 <= r["rsi"] <= 65 if side == "BUY" else 35 <= r["rsi"] <= 55) else 0
    return {"side": side, "setup": setup, "entry": entry, "sl": sl, "t1": tps[0], "t2": tps[1],
            "risk_pct": risk / entry * 100, "score": score, "time": r["time"]}


# ------------------------------------------------------------- backtest
def backtest(df, target_r=TARGETS_R[0]):
    """Enter on next bar's open, exit at SL or target. If both hit in one bar -> assume SL."""
    trades, i, n = [], 210, len(df)
    while i < n - 1:
        s = signal_at(df, i)
        if not s:
            i += 1
            continue
        entry = df["open"].iloc[i + 1]
        long = s["side"] == "BUY"
        risk = abs(s["entry"] - s["sl"])
        sl = entry - risk if long else entry + risk
        tp = entry + target_r * risk if long else entry - target_r * risk
        result, j = None, i + 1
        while j < n:
            hi, lo = df["high"].iloc[j], df["low"].iloc[j]
            hit_sl = lo <= sl if long else hi >= sl
            hit_tp = hi >= tp if long else lo <= tp
            if hit_sl:
                result = -1.0
                break
            if hit_tp:
                result = target_r
                break
            j += 1
        if result is None:                              # still open at end of data
            break
        fee_r = (2 * FEE * entry) / risk                # fees expressed in R
        trades.append({"setup": s["setup"].split(" +")[0], "side": s["side"], "r": result - fee_r})
        i = j + 1
    return trades


def summarize(trades):
    if not trades:
        return {"trades": 0}
    r = np.array([t["r"] for t in trades])
    eq = np.cumsum(r)
    dd = (np.maximum.accumulate(np.concatenate([[0], eq]))[1:] - eq).max()
    return {"trades": len(r), "win_rate": (r > 0).mean() * 100, "avg_r": r.mean(),
            "total_r": r.sum(), "max_dd_r": dd}


# --------------------------------------------------------------- levels
def key_levels(df, n=3, lookback=300):
    """Nearest swing-based support & resistance (clustered) around current price."""
    d = df.tail(lookback)
    price, atr = d["close"].iloc[-1], d["atr"].iloc[-1]
    lv = pd.concat([d["pivot_high"].dropna(), d["pivot_low"].dropna()]).sort_values().values
    clusters = []
    for x in lv:
        if clusters and abs(x - clusters[-1][-1]) <= 0.5 * atr:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    levels = [(float(np.mean(c)), len(c)) for c in clusters]
    res = sorted([l for l in levels if l[0] > price], key=lambda l: l[0])[:n]
    sup = sorted([l for l in levels if l[0] < price], key=lambda l: -l[0])[:n]
    return sup, res


def analyse(symbol, interval, bars):
    df = add_indicators(fetch(symbol, interval, bars))
    r = df.iloc[-1]
    sup, res = key_levels(df)
    trend = ("UP (तेज़ी)" if r["close"] > r["ema200"] and r["ema50"] > r["ema200"]
             else "DOWN (मंदी)" if r["close"] < r["ema200"] and r["ema50"] < r["ema200"]
             else "SIDEWAYS (साइडवेज़)")
    pats = [n for k, n in {**BULL_PATTERNS, **BEAR_PATTERNS, "doji": "Doji"}.items() if r[k]]
    sig = signal_at(df, len(df) - 1)
    trades = backtest(df)
    by_setup = {}
    for t in trades:
        by_setup.setdefault(t["setup"], []).append(t)
    return {"symbol": symbol, "price": r["close"], "time": r["time"], "trend": trend,
            "rsi": r["rsi"], "vol_ratio": r["vol_ratio"], "atr": r["atr"], "patterns": pats,
            "support": sup, "resistance": res, "signal": sig,
            "bt": summarize(trades), "bt_setup": {k: summarize(v) for k, v in by_setup.items()},
            "bt_from": df["time"].iloc[210], "df": df}


# --------------------------------------------------------------- output
def fmt(x):
    return f"{x:,.2f}" if x >= 1 else f"{x:.5f}"


def plan_text(a):
    """Plain-language plan when there is no live signal."""
    lines = []
    atr = a["atr"]
    up, down = a["trend"].startswith("UP"), a["trend"].startswith("DOWN")
    if a["resistance"]:
        R = a["resistance"][0][0]
        if up:
            lines.append(f"ब्रेकआउट: कैंडल {fmt(R)} के ऊपर बंद हो + वॉल्यूम 1.5x से ज़्यादा → BUY सिग्नल बनेगा "
                         f"(SL लगभग {fmt(R - SL_ATR * atr)})")
        else:
            lines.append(f"{fmt(R)} के ऊपर बंद होना ट्रेंड बदलने का पहला संकेत होगा, पर ट्रेंड UP होने तक "
                         f"सिस्टम BUY नहीं देगा")
    if a["support"]:
        S = a["support"][0][0]
        if down:
            lines.append(f"ब्रेकडाउन: कैंडल {fmt(S)} के नीचे बंद हो + वॉल्यूम 1.5x से ज़्यादा → SELL सिग्नल बनेगा "
                         f"(SL लगभग {fmt(S + SL_ATR * atr)})")
        else:
            lines.append(f"{fmt(S)} के नीचे बंद हो तो खरीदे हुए कॉइन से बाहर निकलने पर विचार करें")
    return lines


def print_report(results, interval):
    print(f"\n=== Crypto Signals ({interval}) — {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC ===")
    for a in results:
        s = a["signal"]
        print(f"\n{a['symbol']}  price {fmt(a['price'])}  trend {a['trend']}  "
              f"RSI {a['rsi']:.0f}  vol {a['vol_ratio']:.1f}x")
        print("  Support:    " + ", ".join(fmt(l) for l, _ in a["support"]))
        print("  Resistance: " + ", ".join(fmt(l) for l, _ in a["resistance"]))
        if a["patterns"]:
            print("  Last candle pattern: " + ", ".join(a["patterns"]))
        if s:
            print(f"  >>> {s['side']} ({s['setup']}) score {s['score']}/100  entry {fmt(s['entry'])}  "
                  f"SL {fmt(s['sl'])}  T1 {fmt(s['t1'])}  T2 {fmt(s['t2'])}  risk {s['risk_pct']:.1f}%")
        else:
            print("  No signal — wait. " + " | ".join(plan_text(a)))
        b = a["bt"]
        if b["trades"]:
            print(f"  Backtest: {b['trades']} trades, win {b['win_rate']:.0f}%, avg {b['avg_r']:+.2f}R, "
                  f"total {b['total_r']:+.1f}R, max drawdown {b['max_dd_r']:.1f}R")


def write_html(results, interval, path):
    def row_levels(lv):
        return ", ".join(f"{fmt(l)}<small>×{n}</small>" for l, n in lv) or "—"

    cards = []
    for a in results:
        s = a["signal"]
        if s:
            cls = "buy" if s["side"] == "BUY" else "sell"
            sig = (f"<div class='sig {cls}'><b>{s['side']}</b> · {html.escape(s['setup'])} · score {s['score']}/100"
                   f"<table><tr><td>Entry</td><td>{fmt(s['entry'])}</td></tr>"
                   f"<tr><td>Stop-loss</td><td>{fmt(s['sl'])} ({s['risk_pct']:.1f}%)</td></tr>"
                   f"<tr><td>Target 1 (1.5R)</td><td>{fmt(s['t1'])}</td></tr>"
                   f"<tr><td>Target 2 (3R)</td><td>{fmt(s['t2'])}</td></tr></table></div>")
        else:
            sig = "<div class='sig none'><b>अभी कोई सिग्नल नहीं — इंतज़ार करें</b><ul>" + "".join(
                f"<li>{html.escape(t)}</li>" for t in plan_text(a)) + "</ul></div>"
        b = a["bt"]
        bt = "कोई पुराना ट्रेड नहीं" if not b["trades"] else (
            f"{b['trades']} ट्रेड · जीत {b['win_rate']:.0f}% · औसत {b['avg_r']:+.2f}R · "
            f"कुल {b['total_r']:+.1f}R · सबसे बड़ी गिरावट {b['max_dd_r']:.1f}R")
        setups = "".join(f"<li>{html.escape(k)}: {v['trades']} ट्रेड, जीत {v['win_rate']:.0f}%, "
                         f"कुल {v['total_r']:+.1f}R</li>" for k, v in a["bt_setup"].items())
        cards.append(f"""<section class='card'>
<h2>{a['symbol']} <span>{fmt(a['price'])}</span></h2>
<p class='meta'>Trend: <b>{a['trend']}</b> · RSI {a['rsi']:.0f} · Volume {a['vol_ratio']:.1f}× avg ·
Pattern: {html.escape(', '.join(a['patterns']) or '—')}</p>
<p><b>Resistance (ऊपर):</b> {row_levels(a['resistance'])}<br><b>Support (नीचे):</b> {row_levels(a['support'])}</p>
{sig}
<p class='bt'><b>पुराने डेटा पर नतीजा</b> ({a['bt_from']:%d %b %Y} से): {bt}<ul>{setups}</ul></p>
</section>""")
    doc = f"""<!doctype html><html lang='hi'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'><title>Crypto Signals</title>
<style>
:root{{--bg:#f6f7f9;--fg:#1b1f24;--card:#fff;--mut:#5c6670;--bd:#dde1e6;--buy:#e6f4ea;--buyb:#1e8e3e;--sell:#fce8e6;--sellb:#c5221f;--none:#f1f3f4}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111418;--fg:#e8eaed;--card:#1b1f24;--mut:#9aa0a6;--bd:#2d333b;--buy:#12321d;--sell:#3a1614;--none:#22272e}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0;padding:16px}}
main{{max-width:900px;margin:auto}} .card{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:16px;margin:12px 0}}
h2{{margin:0 0 4px}} h2 span{{color:var(--mut);font-weight:400}} .meta,.bt,small{{color:var(--mut)}}
.sig{{border-radius:8px;padding:10px 12px;border-left:4px solid}} .buy{{background:var(--buy);border-color:var(--buyb)}}
.sell{{background:var(--sell);border-color:var(--sellb)}} .none{{background:var(--none);border-color:var(--mut)}}
table td{{padding:2px 12px 2px 0}} .warn{{background:var(--sell);padding:10px 12px;border-radius:8px}}
</style></head><body><main>
<h1>Crypto Signals ({interval})</h1>
<p class='meta'>Updated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC · data: Binance public API · fee 0.1%/side included in backtest</p>
<p class='warn'>⚠️ यह शिक्षा के लिए है, निवेश सलाह नहीं। कोई भी सिग्नल पक्का नहीं होता। हर ट्रेड में अपनी पूंजी का 1% से ज़्यादा रिस्क न लें, और स्टॉप-लॉस हमेशा लगाएँ।</p>
{''.join(cards)}
</main></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


# ---------------------------------------------------------------- alerts
def telegram(text):
    tok, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        return
    try:
        requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                      data={"chat_id": chat, "text": text}, timeout=15)
    except requests.RequestException as e:
        print("Telegram error:", e, file=sys.stderr)


def github_issue(title, body):
    """When running inside GitHub Actions: open an Issue (GitHub emails/notifies the repo owner)."""
    tok, repo = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY")
    if not (tok and repo):
        return
    h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/issues"
    try:
        existing = requests.get(url, headers=h, params={"labels": "signal", "state": "all", "per_page": 100},
                                timeout=20).json()
        if any(i.get("title") == title for i in existing if isinstance(i, dict)):
            return
        requests.post(url, headers=h, json={"title": title, "body": body, "labels": ["signal"]}, timeout=20)
    except requests.RequestException as e:
        print("GitHub issue error:", e, file=sys.stderr)


def step_summary(results):
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if not path:
        return
    rows = ["| Coin | Price | Trend | RSI | Signal | Entry | SL | T1 | T2 |", "|---|---|---|---|---|---|---|---|---|"]
    for a in results:
        s = a["signal"]
        sig = f"**{s['side']}** {s['setup']}" if s else "wait"
        nums = [fmt(s[k]) for k in ("entry", "sl", "t1", "t2")] if s else ["", "", "", ""]
        rows.append(f"| {a['symbol']} | {fmt(a['price'])} | {a['trend']} | {a['rsi']:.0f} | {sig} | " + " | ".join(nums) + " |")
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n\n_Not financial advice. Risk max 1% per trade._\n")


def alert_new(results, state_path):
    step_summary(results)
    try:
        with open(state_path) as f:
            seen = json.load(f)
    except (OSError, ValueError):
        seen = {}
    for a in results:
        s = a["signal"]
        if not s:
            continue
        key = f"{a['symbol']}|{s['time']}"
        if key in seen:
            continue
        seen[key] = True
        b = a["bt"]
        msg = (f"{s['side']} {a['symbol']} — {s['setup']} (score {s['score']}/100)\n"
               f"Entry {fmt(s['entry'])}\nSL {fmt(s['sl'])} ({s['risk_pct']:.1f}%)\n"
               f"T1 {fmt(s['t1'])}  T2 {fmt(s['t2'])}\n"
               f"Backtest win-rate: {b.get('win_rate', 0):.0f}% over {b['trades']} trades\n"
               f"Not financial advice. Risk max 1% per trade.")
        print("\nALERT:\n" + msg)
        telegram(msg)
        github_issue(f"{s['side']} {a['symbol']} @ {fmt(s['entry'])} — {s['time']:%Y-%m-%d %H:%M} UTC", msg)
    with open(state_path, "w") as f:
        json.dump(seen, f)


# ------------------------------------------------------------------ main
def run_once(args):
    results = []
    for sym in args.symbols:
        try:
            results.append(analyse(sym, args.interval, args.bars))
        except Exception as e:                           # keep going if one symbol fails
            print(f"{sym}: error {e}", file=sys.stderr)
    print_report(results, args.interval)
    write_html(results, args.interval, os.path.join(HERE, "report.html"))
    alert_new(results, os.path.join(HERE, ".alert_state.json"))
    print(f"\nReport: {os.path.join(HERE, 'report.html')}")
    return results


def main():
    p = argparse.ArgumentParser(description="Crypto signal + backtest system (educational)")
    p.add_argument("--symbols", nargs="+", default=DEFAULT_SYMBOLS)
    p.add_argument("--interval", default="4h", help="1h, 4h, 1d ...")
    p.add_argument("--bars", type=int, default=3000, help="history to download (also used for backtest)")
    p.add_argument("--loop", type=int, default=0, help="re-run every N minutes")
    args = p.parse_args()
    run_once(args)
    while args.loop:
        time.sleep(args.loop * 60)
        run_once(args)


if __name__ == "__main__":
    main()
