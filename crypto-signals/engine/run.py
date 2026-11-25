#!/usr/bin/env python3
"""
Advanced SMC opportunity engine — BACKTEST + PAPER TRADING only.

  python3 run.py                 # backtest all strategies x R:R profiles + paper-trade status + report.html
  python3 run.py --risk-profile test_500
  python3 run.py --config my_config.json

There is deliberately NO real-order code here. live_trading=true is refused.
"""
import argparse
import datetime as dt
import html
import json
import math
import os
import sys

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest as bt  # noqa: E402
import smc  # noqa: E402


def inr(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{'-' if x < 0 else ''}₹{abs(x):,.0f}"


def px(x):
    return f"{x:,.2f}" if x >= 1 else f"{x:.5f}"


def pf(x):
    return "∞" if x == float("inf") else f"{x:.2f}"


# ================================================================= paper
def paper(data, cfg, risk):
    pc = cfg["paper"]
    start = pd.Timestamp(pc["start"])
    prof = next(p for p in bt.profiles(cfg) if p["name"] == pc["profile"])
    closed, opened, pending = [], [], []
    for sym, df in data.items():
        idx = df.index[df["time"] >= start]
        if not len(idx):
            continue
        ods = [o for o in bt.candidates(df, cfg) if pc["strategy"] == "Combined" or o["setup"] == pc["strategy"]]
        c, o, p = bt.simulate(df, ods, prof, cfg, start_i=idx[0])
        for lst in (c, o, p):
            for t in lst:
                t["symbol"] = sym
        closed, opened, pending = closed + c, opened + o, pending + p
    cap = pc["capital_inr"]
    res = bt.portfolio(closed, cfg, risk, capital=cap)
    m = bt.metrics(*res, cfg, cap)
    equity = res[1]
    for t in opened + pending:
        risk_amt = min(risk["fixed"] or float("inf"), equity * risk["pct"] / 100)
        t["size_inr"] = min(risk_amt / t["risk_frac"], equity)
        t["risk_inr"] = t["size_inr"] * t["risk_frac"]
    return {"profile": prof, "closed": res[0], "open": opened, "pending": pending, "metrics": m,
            "equity": equity, "start": start}


# ================================================================ alerts
def github_issue(title, body):
    tok, repo = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY")
    if not (tok and repo):
        return False
    h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/issues"
    try:
        existing = requests.get(url, headers=h, params={"state": "all", "per_page": 100}, timeout=20).json()
        if any(i.get("title") == title for i in existing if isinstance(i, dict)):
            return False
        requests.post(url, headers=h, json={"title": title, "body": body}, timeout=20).raise_for_status()
        return True
    except requests.RequestException as e:
        print("GitHub issue error:", e, file=sys.stderr)
        return False


def alerts(pp):
    foot = "\n\n_PAPER TRADING ONLY — not financial advice. No real order was placed._"
    for t in pp["open"]:
        title = f"[PAPER] OPEN {t['side']} {t['symbol']} {t['setup']} @ {px(t['entry'])} ({t['entry_time']:%Y-%m-%d %H:%M} UTC)"
        body = (f"Profile: {pp['profile']['name']}\nEntry: {px(t['entry'])}\nStop now: {px(t['stop_now'])}\n"
                f"Target: {px(t['target'])}\nPaper size: {inr(t['size_inr'])} (risk {inr(t['risk_inr'])})" + foot)
        github_issue(title, body)
    for t in pp["pending"]:
        title = f"[PAPER] LIMIT {t['side']} {t['symbol']} {t['setup']} @ {px(t['limit_entry'])} ({t['signal_time']:%Y-%m-%d %H:%M} UTC)"
        body = (f"Profile: {pp['profile']['name']}\nLimit entry: {px(t['limit_entry'])}\nStop: {px(t['sl'])}\n"
                f"Target: {px(t['target'])}\nValid for ~{t['expires_bars']} more candles\n"
                f"Paper size: {inr(t['size_inr'])} (risk {inr(t['risk_inr'])})" + foot)
        github_issue(title, body)


# ================================================================ report
def verdict(row, min_oos=20):
    i, o = row["is"], row["oos"]
    if not i.get("trades") or not o.get("trades"):
        return "no data", "none"
    if i["exp_r"] > 0 and o["exp_r"] > 0 and o["trades"] >= min_oos and o["pf"] > 1.1:
        return "Candidate (keep paper-testing)", "ok"
    if i["exp_r"] > 0 and o["exp_r"] > 0:
        return "Positive but too few OOS trades", "warn"
    if i["exp_r"] > 0 >= o["exp_r"]:
        return "Failed out-of-sample", "bad"
    return "Negative edge", "bad"


def build_report(cfg, risk, rows, regimes, pp, cut, t0, t1, path):
    css = """
:root{--bg:#f6f7f9;--fg:#1b1f24;--card:#fff;--mut:#5c6670;--bd:#dde1e6;--ok:#1e8e3e;--okbg:#e6f4ea;--bad:#c5221f;--badbg:#fce8e6;--warn:#b06000;--warnbg:#fef7e0}
@media (prefers-color-scheme:dark){:root{--bg:#111418;--fg:#e8eaed;--card:#1b1f24;--mut:#9aa0a6;--bd:#2d333b;--okbg:#12321d;--badbg:#3a1614;--warnbg:#3a2c0c;--ok:#81c995;--bad:#f28b82;--warn:#fdd663}}
body{background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif;margin:0;padding:16px}
main{max-width:1200px;margin:auto}section{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:16px;margin:14px 0}
h1{margin:4px 0}h2{margin:0 0 8px;font-size:18px}.mut{color:var(--mut)}.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:5px 8px;border-bottom:1px solid var(--bd);text-align:right;white-space:nowrap}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left}th{font-weight:600;color:var(--mut);font-size:12px}
.ok{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}.box{border-radius:8px;padding:10px 12px;margin:8px 0}
.boxbad{background:var(--badbg)}.boxok{background:var(--okbg)}.boxwarn{background:var(--warnbg)}td.sep,th.sep{border-left:2px solid var(--bd)}
"""
    e = html.escape
    now = dt.datetime.now(dt.timezone.utc)

    # --- risk
    risk_html = (f"<p>Capital <b>{inr(risk['capital'])}</b> · max risk <b>{risk['pct']}%</b> per trade · "
                 f"profile <b>{e(cfg['active_risk_profile'])}</b> → risk per trade <b>{inr(risk['per_trade'])}</b> · "
                 f"max {cfg['max_open_trades']} open trades · spot only (no leverage, no shorting) · "
                 f"kill-switch at {cfg['kill_switch_drawdown_pct']}% drawdown</p>")
    for n in risk["notes"]:
        risk_html += f"<div class='box boxwarn'>⚠️ {e(n)}</div>"
    for cap in (10000, 25000):
        risk_html += (f"<p class='mut'>₹500 test profile on {inr(cap)} = {500 / cap * 100:.1f}% of capital per trade "
                      f"→ needs max_risk_pct ≥ {500 / cap * 100:.1f}. "
                      f"{'Above the 2% most risk guides recommend.' if 500 / cap > 0.02 else ''}</p>")

    # --- verdict summary
    cands = [r for r in rows if verdict(r)[1] == "ok"]
    if cands:
        vt = ("<div class='box boxok'>Some combinations were profitable both in-sample and out-of-sample: "
              + ", ".join(f"{e(r['strategy'])} {e(r['profile'])}" for r in cands)
              + ". That is NOT proof — paper-trade them for months before risking money.</div>")
    else:
        vt = ("<div class='box boxbad'><b>No strategy/profile combination showed a reliable edge.</b> "
              "None was profitable in-sample AND out-of-sample with enough trades after fees. "
              "Do not trade these with real money. Keep them in paper mode, or change the rules and re-test.</div>")

    # --- comparison table
    head = ("<tr><th>Strategy</th><th>Profile</th><th>Trades</th><th>Win %</th><th>Avg win</th><th>Avg loss</th>"
            "<th>Net (fees)</th><th>After 30% tax</th><th>PF</th><th>Max DD</th><th>Loss streak</th>"
            "<th class='sep'>OOS trades</th><th>OOS win %</th><th>OOS net</th><th>OOS PF</th><th>OOS avg R</th><th>Verdict</th></tr>")
    body = ""
    for r in rows:
        f, o = r["full"], r["oos"]
        v, cls = verdict(r)
        if not f.get("trades"):
            continue
        kill = " ⛔" if f["killed"] is not None else ""
        body += (f"<tr><td>{e(r['strategy'])}</td><td>{e(r['profile'])}</td><td>{f['trades']}</td>"
                 f"<td>{f['win_rate']:.0f}%</td><td>{inr(f['avg_win'])}</td><td>{inr(f['avg_loss'])}</td>"
                 f"<td class='{'ok' if f['net'] > 0 else 'bad'}'>{inr(f['net'])}</td><td>{inr(f['net_after_tax'])}</td>"
                 f"<td>{pf(f['pf'])}</td><td>{f['max_dd_pct']:.1f}%{kill}</td><td>{f['max_consec_loss']}</td>"
                 + (f"<td class='sep'>{o['trades']}</td><td>{o['win_rate']:.0f}%</td>"
                    f"<td class='{'ok' if o['net'] > 0 else 'bad'}'>{inr(o['net'])}</td><td>{pf(o['pf'])}</td>"
                    f"<td>{o['exp_r']:+.2f}R</td>" if o.get("trades") else "<td class='sep'>0</td><td></td><td></td><td></td><td></td>")
                 + f"<td class='{cls}'>{e(v)}</td></tr>")

    # --- regime table
    reg = "".join(
        f"<tr><td>{e(x['strategy'])}</td><td>{e(x['regime'])}</td><td>{e(x['best_profile'])}</td>"
        f"<td>{x['is_exp_r']:+.2f}R ({x['is_n']})</td>"
        f"<td class='{'ok' if x['oos_exp_r'] > 0 else 'bad'}'>"
        f"{'—' if math.isnan(x['oos_exp_r']) else format(x['oos_exp_r'], '+.2f') + 'R'} ({x['oos_n']})</td></tr>"
        for x in regimes)

    # --- paper
    m = pp["metrics"]
    ptxt = (f"<p>Started {pp['start']:%d %b %Y} with {inr(cfg['paper']['capital_inr'])} · "
            f"strategy <b>{e(cfg['paper']['strategy'])}</b> · profile <b>{e(pp['profile']['name'])}</b> · "
            f"paper equity now <b>{inr(pp['equity'])}</b> · closed trades {m.get('trades', 0)}</p>")
    rows_open = "".join(
        f"<tr><td>{t['symbol']}</td><td>{e(t['setup'])}</td><td>{t['entry_time']:%d %b %H:%M}</td><td>{px(t['entry'])}</td>"
        f"<td>{px(t['stop_now'])}</td><td>{px(t['target'])}</td><td>{'yes' if t['partial_booked'] else 'no'}</td>"
        f"<td>{inr(t['size_inr'])}</td></tr>" for t in pp["open"])
    rows_pend = "".join(
        f"<tr><td>{t['symbol']}</td><td>{e(t['setup'])}</td><td>{t['signal_time']:%d %b %H:%M}</td><td>{px(t['limit_entry'])}</td>"
        f"<td>{px(t['sl'])}</td><td>{px(t['target'])}</td><td>{t['expires_bars']} candles</td>"
        f"<td>{inr(t['size_inr'])} (risk {inr(t['risk_inr'])})</td></tr>" for t in pp["pending"])
    rows_closed = "".join(
        f"<tr><td>{t['symbol']}</td><td>{e(t['setup'])}</td><td>{t['entry_time']:%d %b}</td><td>{t['exit_time']:%d %b}</td>"
        f"<td>{e(t['reason'])}</td><td class='{'ok' if t['pnl'] > 0 else 'bad'}'>{inr(t['pnl'])}</td></tr>"
        for t in pp["closed"])
    paper_html = ptxt
    paper_html += ("<h3>Open paper positions</h3><div class='scroll'><table><tr><th>Coin</th><th>Setup</th><th>Entered</th>"
                   "<th>Entry</th><th>Stop now</th><th>Target</th><th>Partial booked</th><th>Size</th></tr>"
                   + rows_open + "</table></div>") if rows_open else "<p class='mut'>No open paper positions.</p>"
    paper_html += ("<h3>Waiting limit orders (current opportunities)</h3><div class='scroll'><table><tr><th>Coin</th><th>Setup</th>"
                   "<th>Signal</th><th>Limit entry</th><th>Stop</th><th>Target</th><th>Valid</th><th>Paper size</th></tr>"
                   + rows_pend + "</table></div>") if rows_pend else "<p class='mut'>No pending setups right now — the engine is waiting. That is normal.</p>"
    if rows_closed:
        paper_html += ("<h3>Closed paper trades</h3><div class='scroll'><table><tr><th>Coin</th><th>Setup</th><th>In</th>"
                       "<th>Out</th><th>Exit</th><th>P&L</th></tr>" + rows_closed + "</table></div>")

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMC Backtest Report</title><style>{css}</style></head><body><main>
<h1>SMC Opportunity Engine — Backtest &amp; Paper Report</h1>
<p class="mut">Generated {now:%Y-%m-%d %H:%M} UTC · {e(', '.join(cfg['symbols']))} · entry {cfg['entry_tf']}, trend filter {cfg['htf']} ·
data {t0:%d %b %Y} → {t1:%d %b %Y} · in-sample before {cut:%d %b %Y}, out-of-sample after · fees {cfg['fee_pct']}% + slippage {cfg['slippage_pct']}% per side</p>
<div class="box boxbad">⚠️ Backtest &amp; paper trading only. Real-money trading is disabled. Past results do not predict future results.</div>
<section><h2>Verdict</h2>{vt}</section>
<section><h2>Risk settings</h2>{risk_html}</section>
<section><h2>Strategy × Risk/Reward comparison</h2>
<p class="mut">Each row is simulated as its own ₹ account using the risk settings above. "fixed" = stop + single target.
"managed" = 50% partial at min(2R, target/2), break-even at 1R, ATR trailing stop after the partial, trend-reversal and volatility exits.
⛔ = kill-switch hit (trading stopped after {cfg['kill_switch_drawdown_pct']}% drawdown). OOS = out-of-sample (data the rules were not judged on).</p>
<div class="scroll"><table>{head}{body}</table></div></section>
<section><h2>Which target works in which market?</h2>
<p class="mut">Best profile chosen on in-sample trades (min 10) per market regime, then checked on out-of-sample trades.
If the OOS column is red, the "best" target was luck, not a pattern.</p>
<div class="scroll"><table><tr><th>Strategy</th><th>Regime</th><th>Best in-sample</th><th>In-sample avg R (n)</th><th>Out-of-sample avg R (n)</th></tr>{reg}</table></div></section>
<section><h2>Paper trading (forward test)</h2>{paper_html}</section>
<section><h2>Setups</h2><ul>
<li><b>Breakout</b> — close through the last swing high (BOS/MSS) with volume ≥1.5× average, body ≥0.6 ATR, close in top 30% of the candle, daily trend up. Market entry next candle. Stop ≥1.5 ATR.</li>
<li><b>Sweep+MSS</b> — wick below a swing low that closes back above (liquidity sweep), then a market-structure shift up within 15 candles with displacement. Limit entry at the FVG midpoint (or order block). Stop below the sweep low. Daily trend not bearish.</li>
<li><b>OB/FVG Retest</b> — after a bullish BOS in a daily uptrend, limit buy at the top of the order block that started the move. Stop below the block.</li>
<li><b>Combined</b> — all three, one position per coin at a time.</li></ul></section>
</main></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


def summary_md(rows, pp, risk):
    out = ["## SMC engine — paper/backtest", f"Risk per trade: {inr(risk['per_trade'])}", "",
           "| Strategy | Profile | Trades | Win% | Net | PF | MaxDD | OOS net | Verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        f, o = r["full"], r["oos"]
        if f.get("trades"):
            out.append(f"| {r['strategy']} | {r['profile']} | {f['trades']} | {f['win_rate']:.0f}% | {inr(f['net'])} | "
                       f"{pf(f['pf'])} | {f['max_dd_pct']:.1f}% | {inr(o.get('net'))} | {verdict(r)[0]} |")
    out += ["", f"**Paper equity:** {inr(pp['equity'])} · open {len(pp['open'])} · pending {len(pp['pending'])}"]
    for t in pp["pending"]:
        out.append(f"- LIMIT {t['symbol']} {t['setup']} @ {px(t['limit_entry'])} SL {px(t['sl'])} TP {px(t['target'])}")
    return "\n".join(out) + "\n"


# ================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config.json"))
    ap.add_argument("--risk-profile")
    ap.add_argument("--out", default=os.path.join(HERE, "report.html"))
    args = ap.parse_args()
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if cfg.get("live_trading"):
        sys.exit("live_trading=true refused: this engine only backtests and paper-trades. "
                 "Real-money execution needs your explicit approval and a separate, reviewed module.")
    if args.risk_profile:
        cfg["active_risk_profile"] = args.risk_profile
    risk = bt.risk_settings(cfg)
    for n in risk["notes"]:
        print("RISK WARNING:", n)

    data = {}
    for s in cfg["symbols"]:
        try:
            data[s] = smc.load(s, cfg)
            print(f"loaded {s}: {len(data[s])} candles")
        except Exception as ex:  # keep going if one coin fails
            print(f"{s}: data error {ex}", file=sys.stderr)
    if not data:
        sys.exit("no data")

    rows, all_trades, cut, t0, t1 = bt.run_all(data, cfg, risk)
    regimes = bt.regime_table(all_trades, cut)
    pp = paper(data, cfg, risk)
    build_report(cfg, risk, rows, regimes, pp, cut, t0, t1, args.out)
    md = summary_md(rows, pp, risk)
    print("\n" + md)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.getenv("GITHUB_STEP_SUMMARY"), "a", encoding="utf-8") as f:
            f.write(md)
    alerts(pp)
    print("Report:", args.out)


if __name__ == "__main__":
    main()
