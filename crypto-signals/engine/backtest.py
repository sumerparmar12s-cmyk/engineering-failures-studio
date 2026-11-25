"""
Setups -> orders -> fills -> exit management -> INR portfolio -> metrics.

Conservative assumptions everywhere:
  * signals use CLOSED candles only; market orders fill at the NEXT candle's open
  * if stop and target are both inside one candle, the STOP is assumed to hit first
  * limit orders cannot also hit their target on the candle they fill
  * fees + slippage are charged on both sides
"""
import numpy as np
import pandas as pd

SETUPS = ("Breakout", "Sweep+MSS", "OB/FVG Retest")


# ================================================================ setups
def candidates(df, cfg):
    """Return a list of order dicts for every setup (long, and short if allowed)."""
    sides = (1, -1) if cfg.get("allow_short") else (1,)
    out = []
    for side in sides:
        a = _view(df, side)
        out += _breakout(a, side) + _sweep_mss(a, side) + _ob_retest(a, side)
    out.sort(key=lambda x: x["i"])
    return out


def _view(df, side):
    """Normalise to a 'long' view. For shorts prices are negated and bull/bear swapped."""
    s = side
    g = lambda col: df[col].values
    if s == 1:
        v = dict(o=g("open"), h=g("high"), l=g("low"), c=g("close"),
                 brk_with=g("bull_break"), bos=g("bull_bos"), mss=g("bull_mss"), brk_against=g("bear_break"),
                 sweep=g("sweep_low"), ob_top=g("bull_ob_top"), ob_bot=g("bull_ob_bot"),
                 fvg=g("bull_fvg"), fvg_top=g("bull_fvg_top"), fvg_bot=g("bull_fvg_bot"))
    else:
        v = dict(o=-g("open"), h=-g("low"), l=-g("high"), c=-g("close"),
                 brk_with=g("bear_break"), bos=g("bear_bos"), mss=g("bear_mss"), brk_against=g("bull_break"),
                 sweep=g("sweep_high"), ob_top=-g("bear_ob_bot"), ob_bot=-g("bear_ob_top"),
                 fvg=g("bear_fvg"), fvg_top=-g("bear_fvg_bot"), fvg_bot=-g("bear_fvg_top"))
    v.update(atr=g("atr"), vol=g("vol_ratio"), body=g("body"), htf=g("htf") * s,
             atr_rank=g("atr_rank"), n=len(df))
    return v


def _order(i, side, setup, kind, entry, sl, expiry, a):
    return {"i": i, "side": side, "setup": setup, "kind": kind, "entry": entry, "sl": sl,
            "expiry": expiry, "htf": int(a["htf"][i] * side), "atr_rank": a["atr_rank"][i]}


def _breakout(a, side, warm=250):
    """BOS/MSS close through structure + volume spike + strong candle + HTF trend agrees."""
    out = []
    for i in range(warm, a["n"] - 1):
        if not a["brk_with"][i] or a["htf"][i] != 1:
            continue
        rng = a["h"][i] - a["l"][i]
        if a["vol"][i] < 1.5 or a["body"][i] < 0.6 * a["atr"][i] or rng <= 0:
            continue
        if (a["c"][i] - a["l"][i]) / rng < 0.7:                     # must close near the high
            continue
        atr = a["atr"][i]
        sl = a["c"][i] - max(1.5 * atr, a["c"][i] - a["l"][i] + 0.2 * atr)
        if a["c"][i] - sl > 3.5 * atr:
            continue
        out.append(_order(i, side, "Breakout", "market", None, sl, 1, a))
    return out


def _sweep_mss(a, side, warm=250, look=15):
    """Liquidity sweep of a swing low, then a market-structure shift up with displacement.
    Enter on a retrace into the FVG (midpoint) or order block; stop below the sweep."""
    out = []
    for i in range(warm, a["n"] - 1):
        if not a["mss"][i] or a["htf"][i] < 0:
            continue
        sweeps = np.where(a["sweep"][i - look:i + 1])[0]
        if not len(sweeps):
            continue
        s0 = i - look + sweeps[0]
        atr = a["atr"][i]
        displaced = a["body"][max(s0, i - 3):i + 1].max() >= 1.0 * atr or a["vol"][i] >= 1.3
        if not displaced:
            continue
        fvg_idx = [b for b in range(s0, i + 1) if a["fvg"][b]]
        if fvg_idx:
            b = fvg_idx[-1]
            entry = (a["fvg_top"][b] + a["fvg_bot"][b]) / 2
        elif not np.isnan(a["ob_top"][i]):
            entry = a["ob_top"][i]
        else:
            continue
        entry = min(entry, a["c"][i])
        sl = a["l"][s0:i + 1].min() - 0.3 * atr
        if not (0.5 * atr <= entry - sl <= 4 * atr):
            continue
        out.append(_order(i, side, "Sweep+MSS", "limit", entry, sl, 10, a))
    return out


def _ob_retest(a, side, warm=250):
    """Continuation: after a BOS in an HTF uptrend, buy the first retest of the order block."""
    out = []
    for i in range(warm, a["n"] - 1):
        if not a["bos"][i] or a["htf"][i] != 1 or np.isnan(a["ob_top"][i]):
            continue
        atr = a["atr"][i]
        entry, sl = a["ob_top"][i], a["ob_bot"][i] - 0.3 * atr
        if entry >= a["c"][i] or not (0.5 * atr <= entry - sl <= 3 * atr):
            continue
        out.append(_order(i, side, "OB/FVG Retest", "limit", entry, sl, 30, a))
    return out


# ======================================================= trade simulation
def simulate(df, orders, profile, cfg, start_i=0):
    """One position at a time. Returns (closed_trades, open_trades, pending_orders)."""
    views = {1: _view(df, 1), -1: _view(df, -1)}
    cost = (cfg["fee_pct"] + cfg["slippage_pct"]) / 100
    closed, still_open, pending = [], [], []
    busy_until = -1
    n = len(df)
    for od in orders:
        if od["i"] < start_i or od["i"] < busy_until:
            continue
        a = views[od["side"]]
        s = od["side"]
        fill = _fill(a, od, n)
        if fill is None:
            if od["kind"] == "limit" and od["i"] + od["expiry"] >= n - 1:
                pending.append(_export(od, df, s, profile))       # still waiting for a fill
            continue
        b, entry = fill
        sl = od["sl"]
        res = _manage(a, b, entry, sl, od["kind"] == "limit", profile, cfg, cost)
        R = entry - sl
        t = {"symbol": None, "setup": od["setup"], "side": "LONG" if s == 1 else "SHORT",
             "signal_time": df["time"].iloc[od["i"]], "entry_time": df["time"].iloc[b],
             "entry": abs(entry), "sl": abs(sl), "risk_frac": R / abs(entry),
             "regime": _regime(od), **res}
        t["exit_time"] = df["time"].iloc[res["exit_i"]] if res["exit_i"] is not None else None
        if res["open"]:
            t["target"] = abs(entry + profile["rr"] * R)
            t["stop_now"] = abs(res["stop_now"])
            still_open.append(t)
            busy_until = n
        else:
            t["r_net"] = t["ret_net"] / t["risk_frac"]
            closed.append(t)
            busy_until = res["exit_i"] + 1
    return closed, still_open, pending


def _fill(a, od, n):
    i = od["i"]
    if od["kind"] == "market":
        return (i + 1, a["o"][i + 1]) if i + 1 < n else None
    entry, sl = od["entry"], od["sl"]                     # already in the normalised (long) view
    for b in range(i + 1, min(n, i + 1 + od["expiry"])):
        if a["l"][b] <= sl and a["o"][b] > entry:        # wicked straight through entry AND stop
            return b, entry
        if a["o"][b] <= entry:
            return (b, a["o"][b]) if a["o"][b] > sl else None   # gapped below stop: skip
        if a["l"][b] <= entry:
            return b, entry
    return None


def _regime(od):
    trend = {1: "Bull", 0: "Range", -1: "Bear"}[od["htf"]]
    r = od["atr_rank"]
    vol = "HighVol" if r > 0.66 else "LowVol" if r < 0.33 else "NormVol"
    return f"{trend} / {vol}"


def _manage(a, b0, entry, sl, is_limit, p, cfg, cost):
    """Exit management in the normalised long view."""
    m = cfg["managed_exit"]
    R = entry - sl
    target = entry + p["rr"] * R
    managed = p["mode"] == "managed"
    partial_r = max(1.0, min(2.0, p["rr"] / 2))
    stop, rem, legs, peak = sl, 1.0, [], entry
    partial_done = be_done = False
    reason = None
    last = min(a["n"] - 1, b0 + m["max_hold_bars"])
    b = b0
    for b in range(b0, last + 1):
        o, h, l, c = a["o"][b], a["h"][b], a["l"][b], a["c"][b]
        if l <= stop:
            legs.append((rem, min(o, stop) if b > b0 else stop))
            reason = "Stop" if stop == sl else ("Break-even" if not partial_done else "Trailing stop")
            break
        can_tp = not (is_limit and b == b0)
        if managed and can_tp and not partial_done and partial_r < p["rr"] and h >= entry + partial_r * R:
            pf = m["partial_fraction"]
            legs.append((pf, entry + partial_r * R))
            rem -= pf
            partial_done = True
        if can_tp and h >= target:
            legs.append((rem, max(o, target) if b > b0 else target))
            reason = "Target"
            break
        if managed:
            if a["brk_against"][b] or a["htf"][b] == -1:
                legs.append((rem, c))
                reason = "Trend reversal"
                break
            if o - c > 0 and h - l > m["volatility_exit_atr"] * a["atr"][b]:
                legs.append((rem, c))
                reason = "Volatility exit"
                break
            peak = max(peak, h)
            if not be_done and peak >= entry + m["breakeven_at_r"] * R:
                stop = max(stop, entry + 2 * cost * abs(entry))
                be_done = True
            if partial_done:
                stop = max(stop, peak - m["trail_atr"] * a["atr"][b])
    else:
        if last == a["n"] - 1:                                     # data ended: trade still open
            return {"open": True, "exit_i": None, "stop_now": stop, "remaining": rem,
                    "partial_booked": partial_done, "ret_net": None, "reason": "Open"}
        legs.append((rem, a["c"][last]))
        reason, b = "Time exit", last
    gross = sum(f * (px - entry) / abs(entry) for f, px in legs)
    return {"open": False, "exit_i": b, "ret_net": gross - 2 * cost, "reason": reason,
            "bars": b - b0, "partial_booked": partial_done}


def _export(od, df, s, profile):
    R = od["entry"] - od["sl"]
    return {"setup": od["setup"], "side": "LONG" if s == 1 else "SHORT",
            "signal_time": df["time"].iloc[od["i"]], "limit_entry": abs(od["entry"]), "sl": abs(od["sl"]),
            "target": abs(od["entry"] + profile["rr"] * R), "risk_frac": R / abs(od["entry"]),
            "expires_bars": od["i"] + od["expiry"] - (len(df) - 1)}


# ===================================================== position sizing
def risk_settings(cfg, profile_name=None):
    """Resolve the INR risk per trade. Never exceeds max_risk_pct of capital."""
    cap = cfg["capital_inr"]
    pct = cfg["max_risk_pct"]
    if not 0 < pct <= 5:
        raise ValueError("max_risk_pct must be between 0 and 5 (%).")
    rp = cfg["risk_profiles"][profile_name or cfg["active_risk_profile"]]
    cap_limit = cap * pct / 100
    fixed = rp.get("risk_per_trade_inr")
    notes = []
    if fixed is not None:
        if fixed > cap_limit:
            notes.append(f"Requested ₹{fixed:,.0f} risk/trade exceeds your {pct}% limit "
                         f"(₹{cap_limit:,.0f} on ₹{cap:,.0f}). Capped to ₹{cap_limit:,.0f}. "
                         f"To allow ₹{fixed:,.0f} you would need max_risk_pct ≥ {fixed / cap * 100:.1f}.")
        if fixed > cap:
            raise ValueError("risk_per_trade_inr can never exceed capital.")
    return {"capital": cap, "pct": pct, "fixed": fixed, "per_trade": min(fixed or cap_limit, cap_limit),
            "notes": notes}


def portfolio(trades, cfg, risk, capital=None):
    """Spot portfolio in INR: risk-based size, capped by free cash, max open trades, kill-switch."""
    cap = capital or risk["capital"]
    cash, open_pos, results = cap, {}, []
    peak, max_dd, max_dd_pct, killed = cap, 0.0, 0.0, None
    events = []
    for k, t in enumerate(trades):
        events.append((t["entry_time"], 1, k))
        ex = t["exit_time"] if t["exit_time"] > t["entry_time"] else t["entry_time"] + pd.Timedelta(1, "ns")
        events.append((ex, 0, k))                                  # exits sort before entries
    events.sort(key=lambda e: (e[0], e[1]))
    for ts, kind, k in events:
        t = trades[k]
        if kind == 1:
            equity = cash + sum(open_pos.values())
            if killed or len(open_pos) >= cfg["max_open_trades"]:
                continue
            risk_amt = min(risk["fixed"] or np.inf, equity * risk["pct"] / 100)
            notional = min(risk_amt / t["risk_frac"], cash)
            if notional < cfg["min_order_inr"]:
                continue
            cash -= notional
            open_pos[k] = notional
        elif k in open_pos:
            notional = open_pos.pop(k)
            pnl = notional * t["ret_net"]
            cash += notional + pnl
            results.append({**t, "notional": notional, "pnl": pnl})
            equity = cash + sum(open_pos.values())
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
            max_dd_pct = max(max_dd_pct, (peak - equity) / peak * 100)
            if not killed and (peak - equity) / peak * 100 >= cfg["kill_switch_drawdown_pct"]:
                killed = ts
    return results, cash + sum(open_pos.values()), max_dd, max_dd_pct, killed


def metrics(results, final, max_dd, max_dd_pct, killed, cfg, capital):
    if not results:
        return {"trades": 0}
    pnl = np.array([r["pnl"] for r in results])
    rr = np.array([r["r_net"] for r in results])
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    streak = best = 0
    for x in pnl:
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)
    tax = wins.sum() * cfg["tax_rate_pct"] / 100                  # India: losses can't offset gains
    return {"trades": len(pnl), "win_rate": len(wins) / len(pnl) * 100,
            "avg_win": wins.mean() if len(wins) else 0.0, "avg_loss": losses.mean() if len(losses) else 0.0,
            "net": final - capital, "net_after_tax": final - capital - tax,
            "pf": wins.sum() / -losses.sum() if losses.sum() < 0 else np.inf,
            "max_dd": max_dd, "max_dd_pct": max_dd_pct, "max_consec_loss": best,
            "exp_r": rr.mean(), "killed": killed}


def profiles(cfg):
    return [{"name": f"1:{rr} {mode}", "rr": rr, "mode": mode}
            for mode in cfg["exit_modes"] for rr in cfg["rr_targets"]]


def run_all(data, cfg, risk):
    """Backtest every strategy x profile. Returns per-combo metrics for Full / In-sample / Out-of-sample."""
    orders = {sym: candidates(df, cfg) for sym, df in data.items()}
    t0 = min(df["time"].iloc[250] for df in data.values())
    t1 = max(df["time"].iloc[-1] for df in data.values())
    cut = t0 + (t1 - t0) * cfg["in_sample_fraction"]
    strategies = list(SETUPS) + ["Combined"]
    rows, all_trades = [], {}
    for strat in strategies:
        for p in profiles(cfg):
            trades = []
            for sym, df in data.items():
                ods = [o for o in orders[sym] if strat == "Combined" or o["setup"] == strat]
                closed, _, _ = simulate(df, ods, p, cfg)
                for t in closed:
                    t["symbol"] = sym
                trades += closed
            all_trades[(strat, p["name"])] = trades
            row = {"strategy": strat, "profile": p["name"], "rr": p["rr"], "mode": p["mode"]}
            for label, subset in (("full", trades),
                                  ("is", [t for t in trades if t["entry_time"] < cut]),
                                  ("oos", [t for t in trades if t["entry_time"] >= cut])):
                res = portfolio(subset, cfg, risk)
                row[label] = metrics(*res, cfg, risk["capital"])
            rows.append(row)
    return rows, all_trades, cut, t0, t1


def regime_table(all_trades, cut, min_trades=10):
    """For each strategy & market regime: pick the best R:R profile IN-SAMPLE, then show how it did OUT-OF-SAMPLE."""
    out = []
    by = {}
    for (strat, prof), trades in all_trades.items():
        for t in trades:
            by.setdefault((strat, t["regime"]), {}).setdefault(prof, []).append(t)
    for (strat, regime), profs in sorted(by.items()):
        best = None
        for prof, ts in profs.items():
            ins = [t["r_net"] for t in ts if t["entry_time"] < cut]
            if len(ins) >= min_trades and (best is None or np.mean(ins) > best[1]):
                best = (prof, np.mean(ins), len(ins))
        if not best:
            continue
        oos = [t["r_net"] for t in profs[best[0]] if t["entry_time"] >= cut]
        out.append({"strategy": strat, "regime": regime, "best_profile": best[0], "is_exp_r": best[1],
                    "is_n": best[2], "oos_exp_r": np.mean(oos) if oos else np.nan, "oos_n": len(oos)})
    return out
