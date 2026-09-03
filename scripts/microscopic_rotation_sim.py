#!/usr/bin/env python3
"""Microscopic Point-in-Time Daily Portfolio Rotation Engine for BTH_C2LR v2.0.

Strictly follows:
1. Dynamic Point-in-Time Universe: On each day t, selects top 50 altcoins by 30-day trailing median quote volume.
2. Point-in-Time Market Breadth: Computed strictly from active Top-50 altcoins at day t (% > EMA50).
3. Coupled Macro Regime Matrix: BTC > EMA100 & Breadth Thresholds (55%, 35%, 20%).
4. Multi-Scale Momentum & Quality Gates: Close > EMA26, EMA12 > EMA26, Score > 0, R30 > 0, R60 > 0.
5. Percentage Rank Hysteresis (+50% Buffer): Retain held positions up to rank ceil(K * 1.5).
6. Microscopic Execution Sequence: Sell-First -> Deduct Fees/Slippage -> Reconcile Cash -> Buy-Second.
7. Rebalance Band (5%) & Minimum Order ($6 USDT) enforcement.
8. Complete daily ledger recording portfolio holdings, cash, trades, and market breadth for every single day.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "results_portfolio" / "binance_global_pit"
OUT_DIR = ROOT / "results_portfolio" / "binance_global_pit"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STRATEGY_SRC = ROOT / "bth-conservative-top2-leader" / "src"
if str(STRATEGY_SRC) not in sys.path:
    sys.path.insert(0, str(STRATEGY_SRC))

from bth_c2lr.strategy_core import (
    calculate_target_weights,
    evaluate_market_regime,
    select_leaders_with_hysteresis,
)

INITIAL_NAV = 10_000.0
BTC = "BTCUSDT"
CASH = "USDT"
FEE_RATE = 0.00075  # Binance Global VIP / BNB Fee Tier (0.075%)
SLIPPAGE_RATE = 0.0005
COST_RATE = FEE_RATE + SLIPPAGE_RATE
REBALANCE_BAND = 0.05
MIN_ORDER_USDT = 6.0
MIN_HISTORY_DAYS = 150


def load_pit_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    close = pd.read_csv(DATA_DIR / "binance_global_close.csv", index_col=0, parse_dates=True)
    volume = pd.read_csv(DATA_DIR / "binance_global_quote_volume.csv", index_col=0, parse_dates=True)
    close.index = pd.to_datetime(close.index).tz_localize(None)
    volume.index = pd.to_datetime(volume.index).tz_localize(None)
    common_dates = close.index.intersection(volume.index).sort_values()
    symbols = [s for s in close.columns if s in volume.columns]
    return close.loc[common_dates, symbols], volume.loc[common_dates, symbols]


def precalculate_indicators(close: pd.DataFrame) -> dict[str, pd.DataFrame]:
    panels = {}
    for s in close.columns:
        c = close[s]
        ema12 = c.ewm(span=12, adjust=False).mean()
        ema26 = c.ewm(span=26, adjust=False).mean()
        ema50 = c.ewm(span=50, adjust=False).mean()
        ema100 = c.ewm(span=100, adjust=False).mean()
        r30 = c / c.shift(30) - 1.0
        r60 = c / c.shift(60) - 1.0
        r120 = c / c.shift(120) - 1.0
        score = 0.50 * r30 + 0.30 * r60 + 0.20 * r120
        history = c.notna().cumsum()
        trend_ok = (c > ema26) & (ema12 > ema26)
        eligible = (history >= MIN_HISTORY_DAYS) & trend_ok & (score > 0) & (r30 > 0) & (r60 > 0)
        panels[s] = pd.DataFrame({
            "close": c,
            "ema12": ema12,
            "ema26": ema26,
            "ema50": ema50,
            "ema100": ema100,
            "r30": r30,
            "r60": r60,
            "r120": r120,
            "score": score,
            "history": history,
            "trend_ok": trend_ok.fillna(False),
            "eligible": eligible.fillna(False),
        }, index=close.index)
    return panels


def run_microscopic_rotation():
    print("[*] Phase 1: Loading Binance Global Point-in-Time data panel...")
    close, volume = load_pit_data()
    dates = close.index
    symbols = list(close.columns)
    print(f"    Loaded {len(symbols)} symbols across {len(dates)} dates ({dates[0].date()} to {dates[-1].date()})")

    print("[*] Phase 2: Computing technical indicators and multi-scale momentum...")
    panels = precalculate_indicators(close)
    
    # Precompute trailing 30-day median quote volume for point-in-time ranking
    trailing_vol = volume.rolling(30, min_periods=1).median()

    print("[*] Phase 3: Executing Microscopic Daily Portfolio Rotation...")
    # Portfolio state:
    # holdings: dict[symbol, float] -> number of units held
    holdings: dict[str, float] = {}
    cash = INITIAL_NAV
    prior_selected: list[str] = []

    daily_ledger = []
    trade_ledger = []

    # Warmup period for indicators (first 125 days)
    warmup_days = 125

    for i in range(warmup_days, len(dates)):
        date = dates[i]
        date_str = date.strftime("%Y-%m-%d")
        
        # 1. Point-in-Time Universe Selection at Date t:
        # Rank available coins by their 30-day trailing median volume up to date t
        vol_t = trailing_vol.loc[date].dropna()
        # Exclude BTC from altcoin pool
        alt_vol = vol_t.drop(labels=[BTC], errors="ignore")
        # Top 50 altcoins by liquidity on this exact date
        top_alt_universe = list(alt_vol.nlargest(50).index)

        # 2. Point-in-Time Altcoin Breadth at Date t:
        # % of the top 50 altcoins with Close > EMA50 at date t
        valid_breadth_alts = 0
        alts_above_ema50 = 0
        for s in top_alt_universe:
            p = panels[s]
            if (
                int(p.at[date, "history"]) >= 50
                and pd.notna(p.at[date, "close"])
                and pd.notna(p.at[date, "ema50"])
            ):
                valid_breadth_alts += 1
                if float(p.at[date, "close"]) > float(p.at[date, "ema50"]):
                    alts_above_ema50 += 1

        breadth_pct = (alts_above_ema50 / valid_breadth_alts) if valid_breadth_alts > 0 else 0.0

        # 3. BTC Trend Gate at Date t:
        btc_p = panels[BTC]
        btc_close = float(btc_p.at[date, "close"])
        btc_ema100 = float(btc_p.at[date, "ema100"])
        btc_trend_ok = btc_close > btc_ema100

        # 4. Evaluate Macro Regime Matrix at Date t:
        regime_dec = evaluate_market_regime(btc_trend_ok, breadth_pct)
        active_top_k = regime_dec.active_top_k
        crypto_exposure = regime_dec.crypto_exposure
        cash_reserve_pct = regime_dec.cash_reserve_pct

        # 5. Rank Eligible Candidates at Date t:
        eligible_candidates = []
        score_map = {}
        for s in top_alt_universe:
            p = panels[s]
            if bool(p.at[date, "eligible"]):
                sc = float(p.at[date, "score"])
                if math.isfinite(sc):
                    eligible_candidates.append(s)
                    score_map[s] = sc
        ranked_candidates = sorted(eligible_candidates, key=lambda s: (-score_map[s], s))

        # 6. Hysteresis Selection (+50% buffer):
        buffer_pct = 0.50
        exit_rank_limit = int(np.ceil(active_top_k * (1.0 + buffer_pct))) if active_top_k > 0 else 0

        selected_leaders = select_leaders_with_hysteresis(
            current_selected=prior_selected,
            candidates_ranked=ranked_candidates,
            active_top_k=active_top_k,
            buffer_k=2,
            buffer_pct=buffer_pct,
            eligible_symbols=set(eligible_candidates),
        )

        # 7. Mark to Market NAV before rebalancing:
        current_prices = {s: float(close.at[date, s]) for s in holdings if pd.notna(close.at[date, s])}
        asset_values = {s: holdings[s] * current_prices[s] for s in holdings if s in current_prices}
        nav_pre = cash + sum(asset_values.values())

        # Target weights & values
        target_weights = calculate_target_weights(selected_leaders, crypto_exposure, CASH)
        target_values = {s: nav_pre * target_weights.get(s, 0.0) for s in selected_leaders}
        band_threshold = max(nav_pre * REBALANCE_BAND, MIN_ORDER_USDT)

        daily_trades = []
        fee_paid_today = 0.0
        slippage_paid_today = 0.0

        # 8. EXECUTION STEP 1: SELL-FIRST (Liquidate dropped leaders / trim weights)
        # Check all currently held assets
        for s in list(holdings.keys()):
            current_val = asset_values.get(s, 0.0)
            cur_price = current_prices.get(s, float(close.at[date, s]))
            target_val = target_values.get(s, 0.0)
            delta = target_val - current_val

            # Determine sell need
            sell_amount_usdt = 0.0
            sell_reason = ""
            if s not in target_values:
                # Liquidate fully
                sell_amount_usdt = current_val
                if regime_dec.regime == "CASH_GUARD":
                    sell_reason = "EXIT_CASH_GUARD (ตลาดเข้าสู่โหมดรักษาเงินต้น 100% USDT)"
                elif not bool(panels[s].at[date, "trend_ok"]):
                    sell_reason = "EXIT_TREND_FAIL (หลุดเส้น EMA26 หรือ MACD ตัดลง)"
                elif active_top_k < len(prior_selected):
                    sell_reason = "EXIT_REGIME_PRUNING (ลดจำนวนเหรียญตามสภาวะตลาด)"
                else:
                    sell_reason = "EXIT_HYSTERESIS_DROP (ตกอันดับเกินขอบเขต Buffer 8)"
            elif delta < -band_threshold:
                # Trim rebalance
                sell_amount_usdt = -delta
                sell_reason = "TRIM_REBALANCE (ปรับลดน้ำหนักเกิน Band 5%)"

            if sell_amount_usdt >= MIN_ORDER_USDT and cur_price > 0:
                units_to_sell = min(holdings[s], sell_amount_usdt / cur_price)
                executed_notional = units_to_sell * cur_price
                fee = executed_notional * FEE_RATE
                slip = executed_notional * SLIPPAGE_RATE
                net_proceeds = executed_notional - fee - slip

                holdings[s] -= units_to_sell
                if holdings[s] < 1e-7:
                    del holdings[s]

                cash += net_proceeds
                fee_paid_today += fee
                slippage_paid_today += slip

                trade_entry = {
                    "date": date_str,
                    "symbol": s,
                    "side": "SELL",
                    "units": units_to_sell,
                    "price": cur_price,
                    "notional": executed_notional,
                    "fee": fee,
                    "slippage": slip,
                    "reason": sell_reason,
                }
                daily_trades.append(trade_entry)
                trade_ledger.append(trade_entry)

        # 9. EXECUTION STEP 2: RECONCILE CASH
        reconciled_cash = cash

        # 10. EXECUTION STEP 3: BUY-SECOND (Allocate available cash to Top Leaders)
        for s in selected_leaders:
            target_val = target_values.get(s, 0.0)
            current_val = holdings.get(s, 0.0) * float(close.at[date, s])
            delta = target_val - current_val

            if delta > band_threshold and cash >= MIN_ORDER_USDT:
                cur_price = float(close.at[date, s])
                # Limit order by available cash accounting for costs
                executable_notional = min(delta, cash / (1.0 + COST_RATE))
                if executable_notional >= MIN_ORDER_USDT and cur_price > 0:
                    fee = executable_notional * FEE_RATE
                    slip = executable_notional * SLIPPAGE_RATE
                    total_cash_needed = executable_notional + fee + slip

                    units_bought = executable_notional / cur_price
                    holdings[s] = holdings.get(s, 0.0) + units_bought
                    cash -= total_cash_needed
                    fee_paid_today += fee
                    slippage_paid_today += slip

                    rank_idx = ranked_candidates.index(s) + 1 if s in ranked_candidates else 1
                    trade_entry = {
                        "date": date_str,
                        "symbol": s,
                        "side": "BUY",
                        "units": units_bought,
                        "price": cur_price,
                        "notional": executable_notional,
                        "fee": fee,
                        "slippage": slip,
                        "reason": f"BUY_LEADER (ผู้นำอันดับ #{rank_idx} Momentum Score: {(score_map.get(s,0)*100):.1f}%)",
                    }
                    daily_trades.append(trade_entry)
                    trade_ledger.append(trade_entry)

        # 11. Final Mark to Market NAV Post-Execution
        post_asset_vals = {s: holdings[s] * float(close.at[date, s]) for s in holdings}
        nav_post = cash + sum(post_asset_vals.values())

        # Prepare formatted holdings breakdown
        holdings_list = []
        for s, qty in holdings.items():
            px = float(close.at[date, s])
            val = qty * px
            holdings_list.append({
                "symbol": s,
                "units": qty,
                "price": px,
                "value": round(val, 2),
                "weight_pct": round(val / nav_post * 100, 2) if nav_post > 0 else 0.0,
            })
        holdings_list.sort(key=lambda x: -x["value"])

        # Top 10 ranked candidate summary for this date
        candidates_summary = []
        for rank_num, s in enumerate(ranked_candidates[:10], start=1):
            p = panels[s]
            status = "BUY" if s in selected_leaders else ("HOLD" if s in prior_selected else "WATCHLIST")
            candidates_summary.append({
                "rank": rank_num,
                "symbol": s,
                "score": round(float(p.at[date, "score"]) * 100, 2),
                "close": float(p.at[date, "close"]),
                "r30": round(float(p.at[date, "r30"]) * 100, 2),
                "r60": round(float(p.at[date, "r60"]) * 100, 2),
                "status": status,
            })

        daily_ledger.append({
            "date": date_str,
            "nav": round(nav_post, 2),
            "cash": round(cash, 2),
            "cash_weight_pct": round(cash / nav_post * 100, 2) if nav_post > 0 else 100.0,
            "regime": regime_dec.regime,
            "btc_price": round(btc_close, 2),
            "btc_ema100": round(btc_ema100, 2),
            "btc_trend_ok": btc_trend_ok,
            "breadth_pct": round(breadth_pct * 100, 1),
            "altcoins_above_ema50": alts_above_ema50,
            "valid_breadth_alts": valid_breadth_alts,
            "active_top_k": active_top_k,
            "crypto_exposure_pct": round(crypto_exposure * 100, 1),
            "exit_rank_limit": exit_rank_limit,
            "selected_leaders": selected_leaders,
            "holdings_count": len(holdings),
            "holdings": holdings_list,
            "trades_count": len(daily_trades),
            "trades": daily_trades,
            "candidates_top10": candidates_summary,
            "fees_paid_today": round(fee_paid_today, 4),
            "slippage_paid_today": round(slippage_paid_today, 4),
        })

        prior_selected = selected_leaders

    print(f"[*] Simulation completed across {len(daily_ledger)} rebalance days.")
    print(f"    Total trades executed: {len(trade_ledger)}")
    initial_val = INITIAL_NAV
    final_val = daily_ledger[-1]["nav"]
    total_ret = (final_val / initial_val - 1.0) * 100
    days_span = len(daily_ledger)
    cagr = ((final_val / initial_val) ** (365.25 / days_span) - 1.0) * 100

    # Calculate Max Drawdown
    nav_series = pd.Series([x["nav"] for x in daily_ledger])
    peaks = nav_series.cummax()
    dds = (nav_series - peaks) / peaks
    mdd = float(dds.min()) * 100

    print(f"    Initial NAV: ${initial_val:,.2f} -> Final NAV: ${final_val:,.2f} (+{total_ret:.1f}%)")
    print(f"    CAGR: {cagr:.2f}% | Max Drawdown: {mdd:.2f}%")

    # Save to JSON
    with open(OUT_DIR / "microscopic_rotation_ledger.json", "w", encoding="utf-8") as f:
        json.dump(daily_ledger, f, indent=2)

    pd.DataFrame(trade_ledger).to_csv(OUT_DIR / "all_executed_trades.csv", index=False)
    pd.DataFrame(daily_ledger)[["date", "nav", "cash", "regime", "btc_price", "breadth_pct", "active_top_k", "holdings_count", "trades_count"]].to_csv(OUT_DIR / "daily_nav_summary.csv", index=False)

    print(f"[+] Saved microscopic ledger to {OUT_DIR / 'microscopic_rotation_ledger.json'}")
    return daily_ledger, trade_ledger


if __name__ == "__main__":
    run_microscopic_rotation()
