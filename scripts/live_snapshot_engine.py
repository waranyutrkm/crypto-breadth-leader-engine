#!/usr/bin/env python3
"""Binance Live Market Data Snapshot Engine for BTH_C2LR v2.0 Dashboard.

Fetches top USDT pairs from Binance Global API, computes all technical gates,
regimes, momentum scores, and assigns precise Entry/Exit/Hold/Watchlist signals
for every coin in the market.
"""

from __future__ import annotations

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "results_portfolio" / "bth_c2lr_entry_exit_eda"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STABLECOINS = {
    "USDCUSDT", "FDUSDUSDT", "TUSDUSDT", "USDPUSDT", "BUSDUSDT",
    "EURUSDT", "DAIUSDT", "AEURUSDT", "USD1USDT", "RLUSDUSDT",
    "WBTCUSDT", "TBTCUSDT", "CETHUSDT",
}
LEVERAGED_SUFFIXES = ("UPUSDT", "DOWNUSDT", "BULLUSDT", "BEARUSDT")


def fetch_json(url: str, timeout: int = 10) -> dict | list:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_top_usdt_pairs(limit: int = 80) -> list[dict]:
    tickers = fetch_json("https://api.binance.com/api/v3/ticker/24hr")
    filtered = []
    for t in tickers:
        sym = t.get("symbol", "")
        if (
            sym.endswith("USDT")
            and not sym.endswith(LEVERAGED_SUFFIXES)
            and sym not in STABLECOINS
            and float(t.get("quoteVolume", 0)) > 100_000
        ):
            filtered.append(t)
    filtered.sort(key=lambda x: float(x.get("quoteVolume", 0)), reverse=True)
    return filtered[:limit]


def fetch_klines_for_symbol(symbol: str, limit: int = 150) -> pd.Series | None:
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit={limit}"
        data = fetch_json(url, timeout=8)
        if not data or len(data) < 125:
            return None
        closes = [float(k[4]) for k in data]
        return pd.Series(closes)
    except Exception:
        return None


def generate_market_snapshot() -> dict:
    start_time = time.time()
    print("[*] Step 1: Fetching top USDT trading pairs from Binance Global...")
    top_tickers = get_top_usdt_pairs(limit=80)
    ticker_map = {t["symbol"]: t for t in top_tickers}
    symbols = [t["symbol"] for t in top_tickers]
    
    # Ensure BTCUSDT is present
    if "BTCUSDT" not in symbols:
        symbols.insert(0, "BTCUSDT")

    print(f"[*] Step 2: Fetching daily klines for {len(symbols)} candidate symbols in parallel...")
    klines_dict: dict[str, pd.Series] = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_sym = {executor.submit(fetch_klines_for_symbol, s): s for s in symbols}
        for fut in as_completed(future_to_sym):
            s = future_to_sym[fut]
            series = fut.result()
            if series is not None:
                klines_dict[s] = series

    print(f"    [+] Successfully acquired {len(klines_dict)} symbol kline histories.")

    # Step 3: Compute Indicators & Gates
    print("[*] Step 3: Computing technical indicators and multi-scale momentum scores...")
    coin_data = []
    btc_series = klines_dict.get("BTCUSDT")
    if btc_series is None:
        raise RuntimeError("Failed to fetch BTCUSDT klines")

    btc_c = float(btc_series.iloc[-1])
    btc_ema100 = float(btc_series.ewm(span=100, adjust=False).mean().iloc[-1])
    btc_trend_ok = btc_c > btc_ema100
    btc_distance_pct = float((btc_c / btc_ema100 - 1.0) * 100)

    # Market Breadth (% of Altcoins with Close > EMA50)
    alt_symbols = [s for s in klines_dict if s != "BTCUSDT"]
    alt_above_ema50 = 0
    valid_alts = 0

    for s, c_series in klines_dict.items():
        if len(c_series) < 125:
            continue
        c = float(c_series.iloc[-1])
        ema12 = float(c_series.ewm(span=12, adjust=False).mean().iloc[-1])
        ema26 = float(c_series.ewm(span=26, adjust=False).mean().iloc[-1])
        ema50 = float(c_series.ewm(span=50, adjust=False).mean().iloc[-1])
        ema100 = float(c_series.ewm(span=100, adjust=False).mean().iloc[-1])

        # Returns over 30, 60, 120 days
        r30 = float(c / c_series.iloc[-31] - 1.0)
        r60 = float(c / c_series.iloc[-61] - 1.0)
        r120 = float(c / c_series.iloc[-121] - 1.0)
        momentum_score = 0.50 * r30 + 0.30 * r60 + 0.20 * r120

        # Technical Gates
        is_above_ema50 = c > ema50
        trend_ok = (c > ema26) and (ema12 > ema26)
        eligible = trend_ok and (momentum_score > 0) and (r30 > 0) and (r60 > 0)

        if s != "BTCUSDT":
            valid_alts += 1
            if is_above_ema50:
                alt_above_ema50 += 1

        t_info = ticker_map.get(s, {})
        quote_vol = float(t_info.get("quoteVolume", 0))
        price_change_24h = float(t_info.get("priceChangePercent", 0))

        coin_data.append({
            "symbol": s,
            "close": c,
            "ema12": ema12,
            "ema26": ema26,
            "ema50": ema50,
            "ema100": ema100,
            "r30": r30,
            "r60": r60,
            "r120": r120,
            "momentum_score": momentum_score,
            "is_above_ema50": is_above_ema50,
            "trend_ok": trend_ok,
            "eligible": eligible,
            "quote_volume": quote_vol,
            "price_change_24h": price_change_24h,
            "close_to_ema26_pct": float((c / ema26 - 1.0) * 100),
            "ema12_to_ema26_pct": float((ema12 / ema26 - 1.0) * 100),
        })

    breadth_pct = (alt_above_ema50 / valid_alts) if valid_alts > 0 else 0.0

    # Step 4: Evaluate Macro Regime Matrix
    if not btc_trend_ok or breadth_pct < 0.20:
        regime = "CASH_GUARD"
        active_top_k = 0
        crypto_exposure = 0.0
        cash_reserve_pct = 1.0
        regime_desc = "BTC หลุด EMA100 หรือ Altcoin Breadth ต่ำกว่า 20% -> ถือ 100% USDT ป้องกันเงินต้น"
    elif breadth_pct >= 0.55:
        regime = "BROAD_BULL"
        active_top_k = 5
        crypto_exposure = 0.95
        cash_reserve_pct = 0.05
        regime_desc = "ตลาดกระทิงเต็มสูบ กระจายลงทุน Top-5 ผู้นำโมเมนตัมสูง (Crypto 95%, Cash 5%)"
    elif breadth_pct >= 0.35:
        regime = "NORMAL_BULL"
        active_top_k = 3
        crypto_exposure = 0.90
        cash_reserve_pct = 0.10
        regime_desc = "ตลาดกระทิงปกติ คัดถือ Top-3 ผู้นำโมเมนตัมแข็งแกร่ง (Crypto 90%, Cash 10%)"
    else:  # 0.20 <= breadth_pct < 0.35
        regime = "SELECTIVE_BULL"
        active_top_k = 2
        crypto_exposure = 0.70
        cash_reserve_pct = 0.30
        regime_desc = "ตลาดคัดเลือกเฉพาะตัว ถือ Top-2 และสำรองเงินสด 30% (Crypto 70%, Cash 30%)"

    # Step 5: Rank and Assign Signals
    eligible_coins = [c for c in coin_data if c["eligible"]]
    eligible_coins.sort(key=lambda x: x["momentum_score"], reverse=True)

    buffer_pct = 0.50
    exit_rank_limit = int(np.ceil(active_top_k * (1.0 + buffer_pct))) if active_top_k > 0 else 0

    # Map rank to eligible coins
    for i, c in enumerate(eligible_coins):
        c["rank"] = i + 1

    # Assign signals
    for c in coin_data:
        sym = c["symbol"]
        is_eligible = c["eligible"]
        rank = c.get("rank", 999)

        if regime == "CASH_GUARD":
            c["signal"] = "SELL"
            c["signal_badge"] = "🔴 SELL / CASH_GUARD"
            c["action_reason"] = "ตลาดเข้าสู่ CASH_GUARD (ถือ USDT 100% ป้องกันความเสี่ยง)"
            c["target_weight"] = 0.0
        elif is_eligible:
            if rank <= active_top_k:
                c["signal"] = "BUY"
                c["signal_badge"] = "🟢 BUY / ENTER"
                c["action_reason"] = f"ผู้นำอันดับ #{rank} ผ่านเกณฑ์ Trend & Momentum ครบถ้วน (เป้าหมาย Top-{active_top_k})"
                c["target_weight"] = round(crypto_exposure / active_top_k, 4)
            elif rank <= exit_rank_limit:
                c["signal"] = "HOLD"
                c["signal_badge"] = "🔵 HOLD"
                c["action_reason"] = f"อยู่อันดับ #{rank} ภายในขอบเขต Buffer (อันดับ 1–{exit_rank_limit}) ให้ถือต่อไม่ขายหมู"
                c["target_weight"] = round(crypto_exposure / active_top_k, 4)
            elif rank <= exit_rank_limit + 5:
                c["signal"] = "WATCHLIST"
                c["signal_badge"] = "🟡 WATCHLIST"
                c["action_reason"] = f"ผ่านเกณฑ์ทุกข้อ อันดับ #{rank} อยู่ในคิวรอสวิตช์เข้าพอร์ตเมื่อมีตัวหลุด"
                c["target_weight"] = 0.0
            else:
                c["signal"] = "ELIGIBLE"
                c["signal_badge"] = "⚪ ELIGIBLE"
                c["action_reason"] = f"ผ่านเกณฑ์แต่โมเมนตัมอันดับ #{rank} ยังไม่ติดกลุ่มผู้นำ"
                c["target_weight"] = 0.0
        else:
            # Check why not eligible
            reasons = []
            if not c["trend_ok"]:
                if c["close"] <= c["ema26"]:
                    reasons.append("ราคาต่ำกว่า EMA26")
                if c["ema12"] <= c["ema26"]:
                    reasons.append("EMA12 ต่ำกว่า EMA26")
            if c["momentum_score"] <= 0:
                reasons.append("Momentum Score ติดลบ")
            if c["r30"] <= 0:
                reasons.append("ผลตอบแทน 30 วันติดลบ")
            if c["r60"] <= 0:
                reasons.append("ผลตอบแทน 60 วันติดลบ")
            
            c["signal"] = "INACTIVE"
            c["signal_badge"] = "⚪ AVOID"
            c["action_reason"] = f"ไม่ผ่านเกณฑ์: {', '.join(reasons)}"
            c["target_weight"] = 0.0

    # Sort all coins: BUY first, then HOLD, then WATCHLIST, then ELIGIBLE, then INACTIVE
    signal_priority = {"BUY": 0, "HOLD": 1, "WATCHLIST": 2, "ELIGIBLE": 3, "SELL": 4, "INACTIVE": 5}
    coin_data.sort(key=lambda x: (signal_priority.get(x["signal"], 99), -x["momentum_score"]))

    # Load historical EDA summary if exists
    eda_summary_path = OUT_DIR / "entry_exit_eda_summary.json"
    eda_summary = {}
    if eda_summary_path.exists():
        with open(eda_summary_path, "r", encoding="utf-8") as f:
            eda_summary = json.load(f)

    snapshot = {
        "as_of_time": datetime.now(timezone.utc).isoformat(),
        "as_of_bkk": datetime.now().strftime("%Y-%m-%d %H:%M:%S BKK"),
        "macro_regime": {
            "regime": regime,
            "description": regime_desc,
            "btc_price": btc_c,
            "btc_ema100": btc_ema100,
            "btc_trend_ok": btc_trend_ok,
            "btc_distance_pct": round(btc_distance_pct, 2),
            "altcoin_breadth_pct": round(breadth_pct * 100, 1),
            "altcoins_above_ema50": alt_above_ema50,
            "total_altcoins_evaluated": valid_alts,
            "active_top_k": active_top_k,
            "crypto_exposure_pct": round(crypto_exposure * 100, 1),
            "cash_reserve_pct": round(cash_reserve_pct * 100, 1),
            "exit_rank_limit": exit_rank_limit,
        },
        "coins_table": coin_data,
        "historical_eda": eda_summary,
        "execution_rules": {
            "sell_first": True,
            "rebalance_band_pct": 5.0,
            "min_order_usdt": 6.0,
            "turnover_cap_pct": 95.0,
            "fee_rate_pct": 0.075,  # VIP/BNB tier on Binance Global
            "slippage_est_pct": 0.05,
        }
    }

    out_file = OUT_DIR / "binance_live_signals_snapshot.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(f"\n[+] Snapshot saved to {out_file}")
    print(f"    Macro Regime: {regime}")
    print(f"    BTC Price: ${btc_c:,.2f} vs EMA100 ${btc_ema100:,.2f} ({btc_distance_pct:+.2f}%)")
    print(f"    Breadth: {breadth_pct*100:.1f}% ({alt_above_ema50}/{valid_alts} alts > EMA50)")
    print(f"    Active Leaders (BUY): {[c['symbol'] for c in coin_data if c['signal'] == 'BUY']}")
    print(f"    Total Evaluated: {len(coin_data)} coins | Elapsed: {time.time() - start_time:.2f}s")

    return snapshot


if __name__ == "__main__":
    generate_market_snapshot()
