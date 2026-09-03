#!/usr/bin/env python3
"""Comprehensive Quantitative Grid Search & Research on Crypto Regime & Breadth Engines.

Synthesizes:
1. https://github.com/waranyutrkm/quant-regime-v3.2 (Volume-Weighted Breadth, Vol Targeting, Exposure Models)
2. https://github.com/waranyutrkm/crypto-breadth-engine (Top-N Universe, Top-K Momentum Grid, Timeframes)
3. https://github.com/waranyutrkm/global-macro-breadth-engine (Inverse Volatility Basket Weighting, Liquidity Lookback)

Runs a multi-parameter grid search on real Binance Global daily panel:
- Universe Size N: [20, 30, 50]
- Lookback LB: [14, 30, 60]
- Breadth Threshold TH: [0.35, 0.50, 0.65]
- Holdings K: [1, 3, 5]
- Weighting Scheme: ['Equal_Weight', 'Inverse_Vol', 'Hysteresis_Rank']
- Volatility Targeting: [False, True]
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "results_portfolio" / "binance_global_pit"
OUT_DIR = ROOT / "results_portfolio" / "grid_research"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BTC = "BTCUSDT"
COST_PER_FLIP = 0.0015  # 0.15% fee + slippage per regime turnover


def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    close = pd.read_csv(DATA_DIR / "binance_global_close.csv", index_col=0, parse_dates=True)
    vol = pd.read_csv(DATA_DIR / "binance_global_quote_volume.csv", index_col=0, parse_dates=True)
    close.index = pd.to_datetime(close.index).tz_localize(None)
    vol.index = pd.to_datetime(vol.index).tz_localize(None)
    common_dates = close.index.intersection(vol.index).sort_values()
    symbols = [s for s in close.columns if s in vol.columns]
    return close.loc[common_dates, symbols], vol.loc[common_dates, symbols]


def simulate_grid_combination(
    close: pd.DataFrame,
    vol: pd.DataFrame,
    N: int,
    LB: int,
    TH: float,
    K: int,
    weight_mode: str,
    vol_target: bool,
    target_vol_ann: float = 0.50,
) -> dict:
    dates = close.index
    symbols = [s for s in close.columns if s != BTC]
    
    # 1. Precalculate Momentum and Daily Returns
    mom = (close / close.shift(LB) - 1.0)
    daily_ret = close.pct_change()
    rolling_vol = daily_ret.rolling(30).std()
    
    # BTC rolling volatility for vol targeting
    btc_vol = (daily_ret[BTC].rolling(20).std() * math.sqrt(365)).fillna(0.60)

    # 30-day trailing median volume for liquidity ranking
    trailing_vol = vol.rolling(30, min_periods=1).median()

    equity = [10000.0]
    trades_count = 0
    on_days = 0
    prior_regime_on = False
    prior_selected: list[str] = []

    # Run simulation
    start_idx = max(LB + 10, 60)
    for i in range(start_idx, len(dates)):
        date = dates[i]
        
        # 1. Universe Selection: Top N by liquidity
        vol_row = trailing_vol.loc[date, symbols].dropna()
        if len(vol_row) < N:
            top_universe = list(vol_row.index)
        else:
            top_universe = list(vol_row.nlargest(N).index)

        # 2. Market Breadth: Fraction of Universe with Momentum > 0
        mom_row = mom.loc[date, top_universe].dropna()
        if len(mom_row) == 0:
            breadth = 0.0
        else:
            breadth = (mom_row > 0).mean()

        # 3. Macro Regime Filter (quant-regime & crypto-breadth style)
        # Check BTC trend overlay
        btc_c = close.at[date, BTC]
        btc_ema100 = close[BTC].iloc[:i+1].ewm(span=100, adjust=False).mean().iloc[-1]
        btc_bull = btc_c > btc_ema100

        regime_on = (breadth >= TH) and btc_bull

        # 4. Top K Leader Selection
        current_eq = equity[-1]
        
        if regime_on:
            on_days += 1
            # Candidates with positive momentum
            pos_mom = mom_row[mom_row > 0].sort_values(ascending=False)
            
            if len(pos_mom) == 0:
                selected_k = []
            else:
                if weight_mode == "Hysteresis_Rank":
                    # Retain previously held coins if still positive momentum and within K * 1.5
                    limit_rank = int(math.ceil(K * 1.5))
                    ranked_all = list(pos_mom.index)
                    selected_k = []
                    for s in prior_selected:
                        if s in ranked_all and ranked_all.index(s) < limit_rank:
                            selected_k.append(s)
                            if len(selected_k) >= K:
                                break
                    for s in ranked_all:
                        if len(selected_k) >= K:
                            break
                        if s not in selected_k:
                            selected_k.append(s)
                else:
                    selected_k = list(pos_mom.head(K).index)

            # Determine weights
            if len(selected_k) == 0:
                port_ret = 0.0
            elif weight_mode == "Inverse_Vol":
                # Inverse volatility weighting (from global-macro-breadth-engine)
                vols = rolling_vol.loc[date, selected_k].replace(0, np.nan).fillna(0.05)
                inv_v = 1.0 / vols
                weights = inv_v / inv_v.sum()
                next_rets = daily_ret.loc[dates[min(i + 1, len(dates) - 1)], selected_k]
                port_ret = (weights * next_rets).sum()
            else:
                # Equal weight (from crypto-breadth-engine)
                next_rets = daily_ret.loc[dates[min(i + 1, len(dates) - 1)], selected_k]
                port_ret = next_rets.mean()

            # Volatility Targeting (from quant-regime-v3.2)
            if vol_target:
                b_v = btc_vol.at[date]
                vol_mult = min(1.2, target_vol_ann / b_v) if b_v > 0 else 1.0
                port_ret *= vol_mult

            # Regime turnover cost
            if not prior_regime_on or set(selected_k) != set(prior_selected):
                current_eq *= (1.0 - COST_PER_FLIP)
                trades_count += 1

            new_eq = current_eq * (1.0 + port_ret)
            equity.append(new_eq)
            prior_selected = selected_k
            prior_regime_on = True
        else:
            # Regime is OFF: 100% Cash Guard
            if prior_regime_on:
                current_eq *= (1.0 - COST_PER_FLIP)
                trades_count += 1
            equity.append(current_eq)
            prior_selected = []
            prior_regime_on = False

    eq_series = pd.Series(equity)
    total_ret = (eq_series.iloc[-1] / eq_series.iloc[0] - 1.0) * 100.0
    days = len(equity)
    cagr = ((eq_series.iloc[-1] / eq_series.iloc[0]) ** (365.25 / max(1, days)) - 1.0) * 100.0

    peaks = eq_series.cummax()
    dds = (eq_series - peaks) / peaks
    mdd = float(dds.min()) * 100.0

    # Sharpe ratio
    daily_returns = eq_series.pct_change().dropna()
    sharpe = float(daily_returns.mean() / daily_returns.std() * math.sqrt(365)) if daily_returns.std() > 0 else 0.0
    calmar = abs(cagr / mdd) if mdd != 0 else 0.0
    exposure_pct = (on_days / days) * 100.0

    return {
        "N": N,
        "LB": LB,
        "TH": TH,
        "K": K,
        "weight_mode": weight_mode,
        "vol_target": vol_target,
        "total_return_pct": round(total_ret, 2),
        "cagr_pct": round(cagr, 2),
        "max_drawdown_pct": round(mdd, 2),
        "sharpe_ratio": round(sharpe, 2),
        "calmar_ratio": round(calmar, 2),
        "exposure_pct": round(exposure_pct, 1),
        "total_trades": trades_count,
        "final_nav": round(float(eq_series.iloc[-1]), 2),
    }


def run_full_grid_research():
    print("[*] Phase 1: Loading Binance Global dataset...")
    close, vol = load_dataset()
    print(f"    Loaded {len(close.columns)} symbols over {len(close)} days.")

    # Grid parameter search space
    grid_params = {
        "N": [20, 30, 50],
        "LB": [14, 30, 60],
        "TH": [0.40, 0.50, 0.65],
        "K": [1, 3, 5],
        "weight_mode": ["Equal_Weight", "Inverse_Vol", "Hysteresis_Rank"],
        "vol_target": [False, True],
    }

    param_combinations = list(itertools.product(
        grid_params["N"],
        grid_params["LB"],
        grid_params["TH"],
        grid_params["K"],
        grid_params["weight_mode"],
        grid_params["vol_target"],
    ))
    print(f"[*] Phase 2: Running Grid Search across {len(param_combinations)} scenarios...")

    results = []
    for i, (N, LB, TH, K, wm, vt) in enumerate(param_combinations):
        res = simulate_grid_combination(close, vol, N, LB, TH, K, wm, vt)
        results.append(res)
        if (i + 1) % 50 == 0 or (i + 1) == len(param_combinations):
            print(f"    Completed {i + 1}/{len(param_combinations)} combinations...")

    df_res = pd.DataFrame(results)

    # Sort by Sharpe and Calmar
    df_res_sorted = df_res.sort_values(by=["sharpe_ratio", "calmar_ratio"], ascending=False)
    
    # Save results to CSV & JSON
    df_res_sorted.to_csv(OUT_DIR / "grid_search_all_combinations.csv", index=False)
    with open(OUT_DIR / "grid_search_summary.json", "w", encoding="utf-8") as f:
        json.dump(df_res_sorted.to_dict(orient="records"), f, indent=2)

    print("\n[+] Top 10 Optimal Parameter Configurations (Ranked by Sharpe Ratio):")
    top10 = df_res_sorted.head(10)[["N", "LB", "TH", "K", "weight_mode", "vol_target", "cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio", "exposure_pct"]]
    print(top10.to_string(index=False))

    # Calculate parameter sensitivity aggregates
    sensitivity = {
        "by_weight_mode": df_res.groupby("weight_mode")[["cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio"]].mean().to_dict(),
        "by_holdings_k": df_res.groupby("K")[["cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio"]].mean().to_dict(),
        "by_breadth_threshold": df_res.groupby("TH")[["cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio"]].mean().to_dict(),
        "by_lookback": df_res.groupby("LB")[["cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio"]].mean().to_dict(),
        "by_universe_size": df_res.groupby("N")[["cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio"]].mean().to_dict(),
        "by_vol_target": df_res.groupby("vol_target")[["cagr_pct", "max_drawdown_pct", "sharpe_ratio", "calmar_ratio"]].mean().to_dict(),
    }

    with open(OUT_DIR / "parameter_sensitivity.json", "w", encoding="utf-8") as f:
        json.dump(sensitivity, f, indent=2)

    print(f"\n[+] Parameter Sensitivity & Grid Summary saved to {OUT_DIR}")
    return df_res_sorted, sensitivity


if __name__ == "__main__":
    run_full_grid_research()
