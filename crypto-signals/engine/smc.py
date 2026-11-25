"""
Market data + Smart-Money-Concepts feature extraction.

Everything here is computed WITHOUT look-ahead: a value at bar i only uses
candles 0..i (swing points are confirmed K bars after they print).
"""
import time

import numpy as np
import pandas as pd
import requests

API = "https://data-api.binance.vision/api/v3/klines"
TF_MS = {"15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}


# ------------------------------------------------------------------ data
def fetch(symbol, interval, bars):
    """Last `bars` CLOSED candles from Binance public market data (no account needed)."""
    out, end = [], None
    while len(out) < bars:
        params = {"symbol": symbol, "interval": interval, "limit": 1000}
        if end:
            params["endTime"] = end
        for attempt in range(4):
            try:
                r = requests.get(API, params=params, timeout=20)
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        chunk = r.json()
        if not chunk:
            break
        out = chunk + out
        end = chunk[0][0] - 1
        if len(chunk) < 1000:
            break
    df = pd.DataFrame(out).iloc[:, :7]
    df.columns = ["t", "open", "high", "low", "close", "volume", "ct"]
    df = df.drop_duplicates("t").sort_values("t")
    df = df[df["ct"] < time.time() * 1000]                 # drop the still-forming candle
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df["time"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    return df[["time", "open", "high", "low", "close", "volume"]].tail(bars).reset_index(drop=True)


# ------------------------------------------------------------ indicators
def indicators(df):
    c = df["close"]
    for n in (20, 50, 200):
        df[f"ema{n}"] = c.ewm(span=n, adjust=False).mean()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - c.shift()).abs(),
                    (df["low"] - c.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    df["vol_ratio"] = df["volume"] / df["volume"].rolling(20).mean().shift(1)
    df["body"] = (c - df["open"]).abs()
    df["atr_pct"] = df["atr"] / c
    # volatility regime: where today's ATR% sits vs the last ~3 months of bars
    df["atr_rank"] = df["atr_pct"].rolling(500, min_periods=100).rank(pct=True)
    return df


def htf_trend(dfh, tf):
    """Higher-timeframe trend: +1 bull, -1 bear, 0 range. Usable only after the HTF candle CLOSES."""
    c = dfh["close"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    trend = np.where((c > e200) & (e50 > e200), 1, np.where((c < e200) & (e50 < e200), -1, 0))
    return pd.DataFrame({"avail": dfh["time"] + pd.Timedelta(milliseconds=TF_MS[tf]), "htf": trend})


def attach_htf(df, htf, entry_tf):
    df["close_time"] = df["time"] + pd.Timedelta(milliseconds=TF_MS[entry_tf])
    m = pd.merge_asof(df[["close_time"]], htf.sort_values("avail"), left_on="close_time",
                      right_on="avail", direction="backward")
    df["htf"] = m["htf"].fillna(0).astype(int).values
    return df


# ------------------------------------------------------ market structure
def structure(df, k=3):
    """
    Swing points, BOS / MSS, liquidity sweeps, order blocks and fair value gaps.

    BOS  = close beyond the last swing in the direction of the current structure (continuation).
    MSS  = close beyond the last swing AGAINST the current structure (shift / CHoCH).
    Sweep = wick through a swing high/low that closes back inside (stop-hunt / liquidity grab).
    OB   = last opposite-colour candle before the break (where the move originated).
    FVG  = 3-candle imbalance: low[i] > high[i-2] (bullish) or high[i] < low[i-2] (bearish).
    """
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    atr = df["atr"].values
    n = len(df)
    z = np.zeros(n, bool)
    ev = {x: z.copy() for x in ("bull_bos", "bull_mss", "bear_bos", "bear_mss", "sweep_low", "sweep_high")}
    nan = np.full(n, np.nan)
    ob = {x: nan.copy() for x in ("bull_ob_top", "bull_ob_bot", "bear_ob_top", "bear_ob_bot")}
    swing_hi, swing_lo, struct_arr = nan.copy(), nan.copy(), np.zeros(n, int)

    sh = sl = None          # [price, idx, broken]
    struct = 0
    for i in range(n):
        j = i - k
        if j >= k:
            if h[j] == h[j - k:i + 1].max():
                sh = [h[j], j, False]
            if l[j] == l[j - k:i + 1].min():
                sl = [l[j], j, False]
        if sl and not sl[2] and l[i] < sl[0] < c[i]:
            ev["sweep_low"][i] = True
        if sh and not sh[2] and h[i] > sh[0] > c[i]:
            ev["sweep_high"][i] = True
        if sh and not sh[2] and c[i] > sh[0]:
            ev["bull_mss" if struct == -1 else "bull_bos"][i] = True
            struct, sh[2] = 1, True
            for b in range(i - 1, max(i - 15, 0), -1):          # last bearish candle before the push
                if c[b] < o[b]:
                    ob["bull_ob_top"][i], ob["bull_ob_bot"][i] = h[b], l[b]
                    break
        if sl and not sl[2] and c[i] < sl[0]:
            ev["bear_mss" if struct == 1 else "bear_bos"][i] = True
            struct, sl[2] = -1, True
            for b in range(i - 1, max(i - 15, 0), -1):
                if c[b] > o[b]:
                    ob["bear_ob_top"][i], ob["bear_ob_bot"][i] = h[b], l[b]
                    break
        swing_hi[i] = sh[0] if sh else np.nan
        swing_lo[i] = sl[0] if sl else np.nan
        struct_arr[i] = struct

    for key, v in {**ev, **ob}.items():
        df[key] = v
    df["swing_hi"], df["swing_lo"], df["struct"] = swing_hi, swing_lo, struct_arr
    hs2, ls2 = df["high"].shift(2), df["low"].shift(2)
    df["bull_fvg"] = (df["low"] > hs2) & ((df["low"] - hs2) > 0.1 * df["atr"])
    df["bull_fvg_top"], df["bull_fvg_bot"] = df["low"].where(df["bull_fvg"]), hs2.where(df["bull_fvg"])
    df["bear_fvg"] = (df["high"] < ls2) & ((ls2 - df["high"]) > 0.1 * df["atr"])
    df["bear_fvg_top"], df["bear_fvg_bot"] = ls2.where(df["bear_fvg"]), df["high"].where(df["bear_fvg"])
    df["bull_break"] = df["bull_bos"] | df["bull_mss"]
    df["bear_break"] = df["bear_bos"] | df["bear_mss"]
    return df


def load(symbol, cfg):
    df = indicators(fetch(symbol, cfg["entry_tf"], cfg["bars"]))
    dfh = fetch(symbol, cfg["htf"], cfg["htf_bars"])
    df = attach_htf(df, htf_trend(dfh, cfg["htf"]), cfg["entry_tf"])
    return structure(df, cfg.get("swing_k", 3))
