#!/usr/bin/env python3
"""Build the Simplified, Action-First Binance Quantitative Leader Rotation Hub.

Designed around the user's primary mental model:
1. วันนี้ต้องทำอะไร? (What to do TODAY: Buy, Sell, Hold, and exact USDT amount).
2. ก่อนหน้านี้ทำอะไรมาบ้าง? (Past Action History & Timeline: plain-language trade logs).
3. สลับแผนแล้วเหรียญและสัดส่วนต้องเปลี่ยนทันที (BTH_C2LR vs Fast-Alpha vs Core-Satellite).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMBINED_DATA_PATH = ROOT / "data" / "combined_dashboard_data.json"
OUT_HTML = ROOT / "index.html"
PARENT_HTML = ROOT.parent / "binance_c2lr_signals_dashboard.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="th" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Binance Leader Rotation Hub — วันนี้ต้องทำอะไร & ประวัติย้อนหลัง</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    :root {
      --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }
    body {
      font-family: var(--font-sans);
      background-color: #0b0e14;
      color: #e2e8f0;
    }
    .font-mono {
      font-family: var(--font-mono);
    }
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #0e131d;
    }
    ::-webkit-scrollbar-thumb {
      background: #232f45;
      border-radius: 3px;
    }
    .card-dark {
      background: #121824;
      border: 1px solid #1e283b;
    }
  </style>
</head>
<body class="min-h-screen p-3 md:p-6 max-w-5xl mx-auto space-y-6">

  <!-- Header -->
  <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1e283b] pb-4">
    <div class="flex items-center gap-3">
      <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 text-white font-black text-lg shadow-lg shadow-blue-500/20">
        ⚡
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-xl font-extrabold text-white">Binance Leader Rotation Hub</h1>
          <span class="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-bold text-emerald-400 border border-emerald-500/30">Live Spot</span>
        </div>
        <p class="text-xs text-slate-400">ระบบบอกจุดซื้อ-ถือ-ขายประจำวัน (คำนวณจากข้อมูลจริงของ Binance Global)</p>
      </div>
    </div>

    <!-- Quick Strategy Switcher (3 Strategies) -->
    <div class="flex flex-wrap items-center gap-2">
      <div class="flex rounded-lg bg-[#0e131d] border border-[#232f45] p-1 text-xs font-semibold">
        <button id="btn-strat-bth" onclick="setStrategy('BTH_C2LR')" class="px-3 py-1.5 rounded bg-blue-600 text-white font-bold transition">
          🏆 แผนหลัก (BTH_C2LR)
        </button>
        <button id="btn-strat-fast" onclick="setStrategy('FAST_ALPHA')" class="px-3 py-1.5 rounded text-slate-400 hover:text-white transition">
          🚀 คลื่นเร็ว (Fast-Alpha)
        </button>
        <button id="btn-strat-core" onclick="setStrategy('CORE_SATELLITE')" class="px-3 py-1.5 rounded text-slate-400 hover:text-white transition">
          🛡️ ผสมสถาบัน (Core-Sat)
        </button>
      </div>
      <a href="https://github.com/waranyutrkm/crypto-breadth-leader-engine" target="_blank" class="rounded-lg bg-[#151c2a] hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 transition flex items-center gap-1.5" title="อ่านคู่มือและสูตรคำนวณฉบับเต็มบน GitHub">
        📘 คู่มือบน GitHub
      </a>
    </div>
  </header>

  <!-- ================================================================= -->
  <!-- SECTION 1: 🎯 วันนี้ต้องทำอะไร? (WHAT TO DO TODAY) -->
  <!-- ================================================================= -->
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-extrabold text-white flex items-center gap-2">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600/20 text-blue-400 font-bold">1</span>
        <span>วันนี้ต้องทำอะไร? (Today's Direct Action Plan)</span>
      </h2>
      <span class="text-xs font-mono text-slate-400" id="today-date-text">--</span>
    </div>

    <!-- Main Market Status Hero Card -->
    <div class="card-dark rounded-2xl p-5 relative overflow-hidden border border-blue-500/30">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e283b] pb-4 mb-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">กำลังใช้งานกลยุทธ์:</span>
            <span class="text-xs font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/15 border border-blue-500/30" id="hero-strategy-badge">--</span>
          </div>
          <div class="text-2xl font-black flex items-center gap-2.5" id="hero-regime-title">
            <span class="h-3 w-3 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-white" id="hero-regime-name">--</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-bold" id="hero-regime-badge">--</span>
          </div>
          <p class="text-xs text-slate-300 mt-1" id="hero-regime-desc">--</p>
        </div>

        <div class="grid grid-cols-2 gap-3 font-mono text-xs">
          <div class="p-2.5 rounded-xl bg-[#0e131d] border border-[#1e283b]">
            <span class="text-slate-400 text-[10px] block">Bitcoin (Trend Gate)</span>
            <strong class="text-white" id="hero-btc-price">--</strong>
            <span class="text-[10px] text-emerald-400 block" id="hero-btc-status">✓ PASSED (> EMA100)</span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#0e131d] border border-[#1e283b]">
            <span class="text-slate-400 text-[10px] block">ตลาดขึ้นพร้อมกัน (Breadth)</span>
            <strong class="text-emerald-400 text-sm" id="hero-breadth-pct">--%</strong>
            <span class="text-[10px] text-slate-400 block" id="hero-breadth-count">-- alts > EMA50</span>
          </div>
        </div>
      </div>

      <!-- 3 Direct Action Columns: SELL, BUY, HOLD -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Action 1: SELL -->
        <div class="rounded-xl border border-rose-500/30 bg-rose-950/10 p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                🔴 1. ต้องขาย (Sell Orders)
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold" id="cnt-sell-badge">0 ตัว</span>
            </div>
            <p class="text-[11px] text-slate-400 mb-3">เหรียญที่หลุดเกณฑ์แนวโน้ม หรือตกอันดับ ต้องขายออกเพื่อดึงเงินสดกลับ</p>
            <div id="sell-coins-list" class="space-y-1.5 font-mono text-xs">
              <!-- Injected by JS -->
            </div>
          </div>
          <div class="text-[10px] text-slate-500 mt-3 pt-2 border-t border-rose-900/30">
            * ส่งคำสั่งขายให้ Match ก่อน เพื่อให้มีเงินสดพร้อมซื้อ
          </div>
        </div>

        <!-- Action 2: BUY -->
        <div class="rounded-xl border border-emerald-500/30 bg-emerald-950/10 p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                🟢 2. ต้องซื้อ (Buy Orders)
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold" id="cnt-buy-badge">0 ผู้นำ</span>
            </div>
            <p class="text-[11px] text-slate-400 mb-3" id="buy-column-desc">เหรียญผู้นำที่แข็งแกร่งที่สุดตามเกณฑ์ของแผนนี้</p>
            <div id="buy-coins-list" class="space-y-1.5 font-mono text-xs">
              <!-- Injected by JS -->
            </div>
          </div>
          <div class="text-[10px] text-slate-500 mt-3 pt-2 border-t border-emerald-900/30" id="buy-column-footer">
            * คำนวณสัดส่วนตามอัลกอริทึมของกลยุทธ์
          </div>
        </div>

        <!-- Action 3: HOLD -->
        <div class="rounded-xl border border-blue-500/30 bg-blue-950/10 p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
                🔵 3. ถือต่อ (Hold / Run)
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold" id="hold-buffer-badge">Buffer</span>
            </div>
            <p class="text-[11px] text-slate-400 mb-3">เหรียญที่ถืออยู่เดิมและยังอยู่ในเกราะ Buffer ปล่อยให้กำไรวิ่งต่อ</p>
            <div id="hold-coins-list" class="space-y-1.5 font-mono text-xs">
              <!-- Injected by JS -->
            </div>
          </div>
          <div class="text-[10px] text-slate-500 mt-3 pt-2 border-t border-blue-900/30">
            * ไม่หลุดอันดับบัฟเฟอร์ ไม่ต้องรีบขายหมู ช่วยประหยัดค่าคอม
          </div>
        </div>
      </div>

      <!-- Quick Money Calculator -->
      <div class="rounded-xl bg-[#0e131d] border border-[#1e283b] p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="text-xs font-bold text-slate-300 whitespace-nowrap">💵 คำนวณเงินทุนของคุณ:</div>
          <div class="relative w-44">
            <input type="number" id="quick-nav-input" value="10000" step="500" oninput="updateQuickCalc()" class="w-full rounded-lg bg-[#151c2a] border border-[#232f45] px-3 py-1.5 text-xs font-bold font-mono text-white focus:outline-none focus:border-blue-500">
            <span class="absolute right-2.5 top-1.5 text-[10px] font-bold text-slate-400">USDT</span>
          </div>
        </div>

        <div class="flex items-center gap-4 text-xs font-mono">
          <div>
            <span class="text-slate-400 text-[10px] block">ยอดซื้อรวม (Crypto):</span>
            <strong class="text-emerald-400 font-bold text-sm" id="calc-total-crypto">$0.00 USDT</strong>
          </div>
          <div class="border-l border-slate-700 pl-4">
            <span class="text-slate-400 text-[10px] block">สำรองเงินสด (Cash):</span>
            <strong class="text-amber-400 font-bold text-sm" id="calc-cash-reserve">$0.00 USDT</strong>
          </div>
          <div class="border-l border-slate-700 pl-4">
            <span class="text-slate-400 text-[10px] block">ค่าคอม Binance (0.075%):</span>
            <strong class="text-slate-300 font-bold text-sm" id="calc-fee-est">~$0.00 USDT</strong>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- SECTION 2: 🕒 ก่อนหน้านี้ทำอะไรมาบ้าง? (PAST ACTION TIMELINE) -->
  <!-- ================================================================= -->
  <section class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h2 class="text-lg font-extrabold text-white flex items-center gap-2">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-600/20 text-purple-400 font-bold">2</span>
        <span>ก่อนหน้านี้ทำอะไรมาบ้าง? (Past Action History)</span>
      </h2>

      <!-- Search Filter -->
      <div class="relative w-full sm:w-64">
        <input type="text" id="timeline-search-input" oninput="renderPastTimeline()" placeholder="ค้นหาชื่อเหรียญ (เช่น PEPE, SOL, BTC)..." class="w-full rounded-lg bg-[#0e131d] border border-[#232f45] px-3 py-1.5 pl-8 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono">
        <svg class="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
      </div>
    </div>

    <!-- Timeline List Container -->
    <div class="card-dark rounded-2xl p-5 space-y-3 max-h-[500px] overflow-y-auto" id="past-timeline-container">
      <!-- Injected by JS -->
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- SECTION 3: 🔍 ตรวจสอบข้อมูลเชิงลึก (COLLAPSIBLE ADVANCED DATA) -->
  <!-- ================================================================= -->
  <section class="pt-2">
    <details class="group card-dark rounded-2xl p-4 border border-[#1e283b] transition">
      <summary class="flex items-center justify-between cursor-pointer font-bold text-xs text-slate-400 hover:text-white uppercase tracking-wider select-none">
        <span class="flex items-center gap-2">
          <svg class="h-4 w-4 text-blue-400 group-open:rotate-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          🔍 ดูตารางสแกนและค่าทางเทคนิคทั้งหมด 72 เหรียญในตลาด (คลิกเพื่อขยาย)
        </span>
        <span class="text-[11px] text-blue-400 font-mono">Full Scanner Matrix</span>
      </summary>

      <div class="mt-4 pt-4 border-t border-[#1e283b] overflow-x-auto">
        <table class="w-full text-left text-xs font-mono border-collapse">
          <thead class="bg-[#0e131d] text-slate-400 border-b border-[#232f45]">
            <tr>
              <th class="py-2.5 px-3"># Rank</th>
              <th class="py-2.5 px-3">Symbol</th>
              <th class="py-2.5 px-3 text-center">Signal</th>
              <th class="py-2.5 px-3 text-right">Price ($)</th>
              <th class="py-2.5 px-3 text-right">24h %</th>
              <th class="py-2.5 px-3 text-right">14d %</th>
              <th class="py-2.5 px-3 text-right">30d %</th>
              <th class="py-2.5 px-3 text-right">Score</th>
              <th class="py-2.5 px-3 text-center">Trend Gate</th>
              <th class="py-2.5 px-3">เหตุผล</th>
            </tr>
          </thead>
          <tbody id="raw-coins-tbody" class="divide-y divide-[#182030] text-slate-200">
            <!-- Injected by JS -->
          </tbody>
        </table>
      </div>
    </details>
  </section>

  <!-- Footer -->
  <footer class="text-center text-xs text-slate-500 pt-6 border-t border-[#1e283b]">
    Binance Quantitative Crypto Breadth Engine • Auto-updated daily at 07:15 BKK via GitHub Actions • MIT License
  </footer>

  <!-- DATA & SCRIPTS -->
  <script>
    const MASTER_DATA = __COMBINED_DATA__;
    let currentStrategy = 'BTH_C2LR'; // 'BTH_C2LR' | 'FAST_ALPHA' | 'CORE_SATELLITE'
    let currentStrategyPicks = null;

    document.addEventListener('DOMContentLoaded', () => {
      initApp();
    });

    function initApp() {
      setStrategy('BTH_C2LR');
      renderPastTimeline();
      renderRawCoinsTable();
    }

    function setStrategy(strat) {
      currentStrategy = strat;
      const btnBth = document.getElementById('btn-strat-bth');
      const btnFast = document.getElementById('btn-strat-fast');
      const btnCore = document.getElementById('btn-strat-core');

      // Update button highlights
      btnBth.className = (strat === 'BTH_C2LR') ? 'px-3 py-1.5 rounded bg-blue-600 text-white font-bold transition' : 'px-3 py-1.5 rounded text-slate-400 hover:text-white transition';
      btnFast.className = (strat === 'FAST_ALPHA') ? 'px-3 py-1.5 rounded bg-blue-600 text-white font-bold transition' : 'px-3 py-1.5 rounded text-slate-400 hover:text-white transition';
      btnCore.className = (strat === 'CORE_SATELLITE') ? 'px-3 py-1.5 rounded bg-blue-600 text-white font-bold transition' : 'px-3 py-1.5 rounded text-slate-400 hover:text-white transition';

      // Dynamically calculate picks for this strategy!
      currentStrategyPicks = computeStrategyPicks(strat);
      renderTodayAction();
      updateQuickCalc();
    }

    // =================================================================
    // DYNAMIC STRATEGY ENGINE
    // =================================================================
    function computeStrategyPicks(strat) {
      const coins = [...MASTER_DATA.live_snapshot.coins_table];
      const mr = MASTER_DATA.live_snapshot.macro_regime;

      if (strat === 'BTH_C2LR') {
        // 🏆 Strategy 1: BTH_C2LR (Top 5 Multi-Scale Momentum: 30/60/120 days)
        const eligible = coins.filter(c => c.trend_ok && (c.r30 > 0) && (c.r60 > 0));
        eligible.sort((a, b) => b.momentum_score - a.momentum_score);

        const leaders = eligible.slice(0, 5).map((c, idx) => ({
          symbol: c.symbol,
          close: c.close,
          price_change_24h: c.price_change_24h,
          rank_display: '#' + (idx + 1),
          weight_pct: 19.0,
          metric_label: 'Momentum Score',
          metric_val: '+' + (c.momentum_score * 100).toFixed(0) + '%',
          reason: 'ผู้นำโมเมนตัม 3 มิติเวลาอันดับ #' + (idx + 1)
        }));

        return {
          title: '🏆 แผนหลัก BTH_C2LR (Top 5 Multi-Scale)',
          badgeText: '🏆 แผนหลัก (BTH_C2LR v2.0)',
          desc: 'กระจายลงทุนใน Top 5 ผู้นำที่แข็งแกร่งที่สุดใน 3 มิติเวลา (30/60/120 วัน) ถือเท่ากันตัวละ 19% สำรองเงินสด 5%',
          cryptoPct: 95.0,
          cashPct: 5.0,
          bufferBadge: 'Buffer Rank 1–8',
          buyDesc: 'เข้าซื้อ Top 5 ผู้นำ สัดส่วนตัวละ 19% เท่ากัน',
          buyFooter: '* กระจายเท่ากัน 5 ตัว รวม 95% ถือเงินสด 5% USDT',
          leaders: leaders,
          sellCoins: coins.filter(c => c.signal === 'SELL'),
          holdCoins: (MASTER_DATA.historical_ledger && MASTER_DATA.historical_ledger.length > 0)
            ? MASTER_DATA.historical_ledger[MASTER_DATA.historical_ledger.length - 1].holdings
            : []
        };

      } else if (strat === 'FAST_ALPHA') {
        // 🚀 Strategy 2: Fast-Alpha (Top 4 by 14-day return & Inverse Volatility Weighting)
        const eligible = coins.filter(c => (c.close > c.ema26) && ((c.r14 || 0) > 0));
        eligible.sort((a, b) => (b.r14 || 0) - (a.r14 || 0));

        const top4 = eligible.slice(0, 4);
        // Inverse Volatility calculation
        const invVols = top4.map(c => 1.0 / (c.vol30 || 0.8));
        const sumInv = invVols.reduce((a, b) => a + b, 0);

        const leaders = top4.map((c, idx) => {
          const w = sumInv > 0 ? (invVols[idx] / sumInv) * 90.0 : 22.5;
          return {
            symbol: c.symbol,
            close: c.close,
            price_change_24h: c.price_change_24h,
            rank_display: 'Alpha #' + (idx + 1),
            weight_pct: parseFloat(w.toFixed(1)),
            metric_label: '14d Return',
            metric_val: '+' + ((c.r14 || 0) * 100).toFixed(1) + '%',
            reason: 'ผู้นำคลื่นเร็ว 14 วัน (ความผันผวน ' + ((c.vol30 || 0.8) * 100).toFixed(0) + '%)'
          };
        });

        return {
          title: '🚀 คลื่นเร็ว Fast-Alpha (Top 4 14d + Inverse Vol)',
          badgeText: '🚀 แผนคลื่นเร็ว (Fast-Alpha Grid #1)',
          desc: 'คัด Top 4 เหรียญที่ผลตอบแทน 14 วันพุ่งแรงที่สุด และถ่วงน้ำหนักตามความนิ่ง (Inverse Vol) เพื่อ Sharpe สูงสุด 2.03',
          cryptoPct: 90.0,
          cashPct: 10.0,
          bufferBadge: 'Buffer Rank 1–6',
          buyDesc: 'เข้าซื้อ Top 4 ผู้นำคลื่น 14 วัน ถ่วงน้ำหนักตามความนิ่ง',
          buyFooter: '* ตัวนิ่งกว่าได้น้ำหนักเยอะกว่า รวม 90% ถือเงินสด 10% USDT',
          leaders: leaders,
          sellCoins: coins.filter(c => c.close <= c.ema26),
          holdCoins: leaders
        };

      } else {
        // 🛡️ Strategy 3: Core-Satellite (30% Core: BTC/ETH/BNB + 70% Satellite: Top 3 BTH)
        const eligible = coins.filter(c => c.trend_ok && (c.r30 > 0) && (c.r60 > 0));
        eligible.sort((a, b) => b.momentum_score - a.momentum_score);
        const top3Sat = eligible.slice(0, 3);

        const btcCoin = coins.find(c => c.symbol === 'BTCUSDT') || { symbol: 'BTCUSDT', close: mr.btc_price, price_change_24h: 0 };
        const ethCoin = coins.find(c => c.symbol === 'ETHUSDT') || { symbol: 'ETHUSDT', close: 0, price_change_24h: 0 };
        const bnbCoin = coins.find(c => c.symbol === 'BNBUSDT') || { symbol: 'BNBUSDT', close: 0, price_change_24h: 0 };

        const leaders = [
          {
            symbol: 'BTCUSDT',
            close: btcCoin.close,
            price_change_24h: btcCoin.price_change_24h,
            rank_display: 'Core',
            weight_pct: 10.0,
            metric_label: 'Core Anchor',
            metric_val: '10.0%',
            reason: 'สมอเรือหลัก Bitcoin'
          },
          {
            symbol: 'ETHUSDT',
            close: ethCoin.close,
            price_change_24h: ethCoin.price_change_24h,
            rank_display: 'Core',
            weight_pct: 10.0,
            metric_label: 'Core Anchor',
            metric_val: '10.0%',
            reason: 'สมอเรือหลัก Ethereum'
          },
          {
            symbol: 'BNBUSDT',
            close: bnbCoin.close,
            price_change_24h: bnbCoin.price_change_24h,
            rank_display: 'Core',
            weight_pct: 10.0,
            metric_label: 'Core Anchor',
            metric_val: '10.0%',
            reason: 'สมอเรือหลัก BNB'
          },
          ...top3Sat.map((c, idx) => ({
            symbol: c.symbol,
            close: c.close,
            price_change_24h: c.price_change_24h,
            rank_display: 'Sat #' + (idx + 1),
            weight_pct: 23.3,
            metric_label: 'Momentum',
            metric_val: '+' + (c.momentum_score * 100).toFixed(0) + '%',
            reason: 'Satellite ผู้นำอันดับ #' + (idx + 1)
          }))
        ];

        return {
          title: '🛡️ พอร์ตสถาบัน Core-Satellite (All-Weather)',
          badgeText: '🛡️ ผสมสถาบัน (30% Core + 70% Sat)',
          desc: 'แบ่ง 30% ถือสมอเรือ (BTC/ETH/BNB ตัวละ 10%) + 70% หมุน 3 เหรียญผู้นำ ช่วยลดความผันผวนเหลือเพียง -30%',
          cryptoPct: 99.9,
          cashPct: 0.1,
          bufferBadge: 'Buffer Sat 1–5',
          buyDesc: 'ถือ Core 30% + ซื้อ Satellite Top 3 ตัวละ 23.3%',
          buyFooter: '* 30% Core ไม่ต้องสลับ, 70% หมุนตามผู้นำ',
          leaders: leaders,
          sellCoins: coins.filter(c => c.signal === 'SELL' && !['BTCUSDT', 'ETHUSDT', 'BNBUSDT'].includes(c.symbol)),
          holdCoins: leaders
        };
      }
    }

    function renderTodayAction() {
      const live = MASTER_DATA.live_snapshot;
      const mr = live.macro_regime;
      const todayDate = live.as_of_bkk || new Date().toISOString().slice(0, 10);
      document.getElementById('today-date-text').textContent = 'ข้อมูล ณ วันที่: ' + todayDate;

      const sp = currentStrategyPicks;
      document.getElementById('hero-strategy-badge').textContent = sp.badgeText;
      document.getElementById('hero-regime-desc').textContent = sp.desc;

      // Hero Market Status
      document.getElementById('hero-regime-name').textContent = mr.regime;
      const badge = document.getElementById('hero-regime-badge');
      if (mr.regime === 'BROAD_BULL') {
        badge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        badge.textContent = `🟢 ไฟเขียวเต็มสูบ (ลงทุน ${sp.cryptoPct}%)`;
      } else if (mr.regime === 'NORMAL_BULL') {
        badge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30';
        badge.textContent = `🟡 กระทิงปกติ (ลงทุน ${sp.cryptoPct}%)`;
      } else if (mr.regime === 'SELECTIVE_BULL') {
        badge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30';
        badge.textContent = `🟠 ตลาดเลือกตัว (ลงทุน 70%)`;
      } else {
        badge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30';
        badge.textContent = '🚨 ถือเงินสด 100% USDT';
      }

      document.getElementById('hero-btc-price').textContent = '$' + Number(mr.btc_price).toLocaleString('en-US', { minimumFractionDigits: 2 });
      document.getElementById('hero-breadth-pct').textContent = mr.altcoin_breadth_pct + '%';
      document.getElementById('hero-breadth-count').textContent = mr.altcoins_above_ema50 + ' / ' + mr.total_altcoins_evaluated + ' Alts';

      // 1. SELL List
      const sellContainer = document.getElementById('sell-coins-list');
      sellContainer.innerHTML = '';
      const sellCoins = sp.sellCoins || [];
      document.getElementById('cnt-sell-badge').textContent = sellCoins.length + ' ตัว';

      if (sellCoins.length === 0) {
        sellContainer.innerHTML = `
          <div class="p-3 rounded-lg bg-rose-950/20 border border-rose-900/30 text-slate-300 text-xs flex items-center gap-2">
            <span class="text-emerald-400 font-bold">✓</span> วันนี้ไม่มีคำสั่งขาย (ไม่มีเหรียญหลุดเกณฑ์)
          </div>
        `;
      } else {
        sellCoins.slice(0, 5).forEach(c => {
          sellContainer.innerHTML += `
            <div class="p-2.5 rounded-lg bg-rose-900/20 border border-rose-800/30 flex items-center justify-between">
              <div>
                <strong class="text-rose-300 font-bold">${c.symbol}</strong>
                <span class="text-[10px] text-slate-400 block">${c.action_reason || 'หลุดเส้นแนวโน้ม'}</span>
              </div>
              <span class="px-2 py-0.5 rounded bg-rose-500 text-white font-bold text-[10px]">SELL</span>
            </div>
          `;
        });
      }

      // 2. BUY List (Dynamic Leaders per Strategy)
      const buyContainer = document.getElementById('buy-coins-list');
      buyContainer.innerHTML = '';
      const buyCoins = sp.leaders || [];
      document.getElementById('cnt-buy-badge').textContent = buyCoins.length + ' ผู้นำ';
      document.getElementById('buy-column-desc').textContent = sp.buyDesc;
      document.getElementById('buy-column-footer').textContent = sp.buyFooter;

      if (buyCoins.length === 0) {
        buyContainer.innerHTML = `
          <div class="p-3 rounded-lg bg-slate-900/40 border border-slate-800 text-slate-400 text-xs">
            ตลาดอยู่ในสถานะถือเงินสด (ไม่มีคำสั่งซื้อใหม่)
          </div>
        `;
      } else {
        buyCoins.forEach((c) => {
          buyContainer.innerHTML += `
            <div class="p-2.5 rounded-lg bg-emerald-900/20 border border-emerald-800/30 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="flex h-6 px-1.5 items-center justify-center rounded bg-emerald-600 text-white text-[10px] font-bold">${c.rank_display}</span>
                <div>
                  <strong class="text-white font-bold">${c.symbol}</strong>
                  <span class="text-[10px] text-slate-400 block">$${formatPrice(c.close)} (${c.price_change_24h >= 0 ? '+' : ''}${c.price_change_24h.toFixed(1)}%)</span>
                </div>
              </div>
              <div class="text-right">
                <span class="text-emerald-400 font-bold block text-xs">สัดส่วน ${c.weight_pct}%</span>
                <span class="text-[10px] text-slate-400">${c.metric_val}</span>
              </div>
            </div>
          `;
        });
      }

      // 3. HOLD List
      const holdContainer = document.getElementById('hold-coins-list');
      holdContainer.innerHTML = '';
      document.getElementById('hold-buffer-badge').textContent = sp.bufferBadge;
      const holdList = sp.holdCoins || [];

      if (holdList.length === 0) {
        holdContainer.innerHTML = `
          <div class="p-3 rounded-lg bg-blue-950/20 border border-blue-900/30 text-slate-300 text-xs">
            ปัจจุบันถือเงินสด 100% USDT รอเข้าซื้อผู้นำรอบใหม่
          </div>
        `;
      } else {
        holdList.slice(0, 5).forEach(h => {
          holdContainer.innerHTML += `
            <div class="p-2.5 rounded-lg bg-blue-900/20 border border-blue-800/30 flex items-center justify-between">
              <div>
                <strong class="text-white font-bold">${h.symbol}</strong>
                <span class="text-[10px] text-slate-400 block">${h.units ? h.units.toFixed(2) + ' units' : 'อยู่ในเกราะหน่วงอันดับ'} ($${formatPrice(h.price || h.close)})</span>
              </div>
              <span class="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold text-[10px] border border-blue-500/30">HOLD ต่อ</span>
            </div>
          `;
        });
      }
    }

    function updateQuickCalc() {
      const nav = parseFloat(document.getElementById('quick-nav-input').value) || 10000;
      const sp = currentStrategyPicks || computeStrategyPicks(currentStrategy);

      const cryptoVal = nav * (sp.cryptoPct / 100.0);
      const cashVal = nav * (sp.cashPct / 100.0);
      const feeEst = cryptoVal * 0.00075;

      document.getElementById('calc-total-crypto').textContent = '$' + Number(cryptoVal.toFixed(2)).toLocaleString() + ' USDT';
      document.getElementById('calc-cash-reserve').textContent = '$' + Number(cashVal.toFixed(2)).toLocaleString() + ' USDT';
      document.getElementById('calc-fee-est').textContent = '~$' + feeEst.toFixed(2) + ' USDT';
    }

    function renderPastTimeline() {
      const container = document.getElementById('past-timeline-container');
      container.innerHTML = '';
      const query = (document.getElementById('timeline-search-input')?.value || '').trim().toUpperCase();

      const ledger = MASTER_DATA.historical_ledger || [];
      const sliceDays = ledger.slice(-30).reverse();

      sliceDays.forEach(day => {
        let trades = day.trades || [];
        if (query) {
          trades = trades.filter(t => t.symbol.includes(query) || (t.reason && t.reason.includes(query)));
          if (trades.length === 0 && !day.date.includes(query)) return;
        }

        const dayDiv = document.createElement('div');
        dayDiv.className = 'p-3.5 rounded-xl bg-[#0e131d] border border-[#1e283b] space-y-2';

        const regimeBadge = day.regime === 'CASH_GUARD'
          ? '<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 text-[10px] font-bold">🚨 CASH_GUARD</span>'
          : '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">🟢 ' + day.regime + '</span>';

        let tradesHtml = '';
        if (trades.length === 0) {
          tradesHtml = `
            <div class="text-[11px] text-slate-400 flex items-center gap-2">
              <span class="h-2 w-2 rounded-full bg-blue-400"></span>
              <span>ไม่มีการปรับพอร์ต — ถือเหรียญเดิมรันเทรนด์ต่อตามเกราะ Buffer (Zero Churning)</span>
            </div>
          `;
        } else {
          trades.forEach(t => {
            const isBuy = t.side === 'BUY';
            tradesHtml += `
              <div class="flex items-center justify-between text-xs font-mono p-1.5 rounded bg-[#131926] border border-[#1f293d]">
                <div class="flex items-center gap-2">
                  <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${isBuy ? 'bg-emerald-500 text-white' : 'bg-rose-500 text-white'}">${t.side}</span>
                  <strong class="text-white">${t.symbol}</strong>
                  <span class="text-slate-400 text-[11px]">($${formatPrice(t.price)})</span>
                </div>
                <div class="text-right">
                  <span class="font-bold text-slate-200">$${t.notional.toLocaleString()} USDT</span>
                  <span class="text-[10px] text-slate-400 block font-sans">${t.reason || ''}</span>
                </div>
              </div>
            `;
          });
        }

        dayDiv.innerHTML = `
          <div class="flex items-center justify-between border-b border-[#182030] pb-2">
            <div class="flex items-center gap-2">
              <span class="font-bold text-white font-mono text-xs">📅 ${day.date}</span>
              ${regimeBadge}
            </div>
            <div class="text-xs font-mono text-slate-400">
              NAV รวม: <strong class="text-emerald-400">$${day.nav.toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong>
            </div>
          </div>
          <div class="space-y-1 pt-1">
            ${tradesHtml}
          </div>
        `;
        container.appendChild(dayDiv);
      });
    }

    function renderRawCoinsTable() {
      const tbody = document.getElementById('raw-coins-tbody');
      tbody.innerHTML = '';
      const list = MASTER_DATA.live_snapshot.coins_table || [];

      list.forEach(c => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[#151d2d] transition';
        const pCls = c.price_change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400';
        let sigBadge = 'bg-slate-700/30 text-slate-400';
        if (c.signal === 'BUY') sigBadge = 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold';
        else if (c.signal === 'HOLD') sigBadge = 'bg-blue-500/20 text-blue-400 border border-blue-500/30 font-bold';
        else if (c.signal === 'WATCHLIST') sigBadge = 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
        else if (c.signal === 'SELL') sigBadge = 'bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold';

        tr.innerHTML = `
          <td class="py-2 px-3 text-slate-400">#${c.rank || '-'}</td>
          <td class="py-2 px-3 font-bold text-white">${c.symbol}</td>
          <td class="py-2 px-3 text-center"><span class="px-2 py-0.5 rounded text-[10px] ${sigBadge}">${c.signal_badge}</span></td>
          <td class="py-2 px-3 text-right font-bold text-white">$${formatPrice(c.close)}</td>
          <td class="py-2 px-3 text-right font-bold ${pCls}">${c.price_change_24h >= 0 ? '+' : ''}${c.price_change_24h.toFixed(1)}%</td>
          <td class="py-2 px-3 text-right text-slate-300">${c.r14 ? (c.r14 * 100).toFixed(1) + '%' : '-'}</td>
          <td class="py-2 px-3 text-right text-slate-300">${(c.r30 * 100).toFixed(0)}%</td>
          <td class="py-2 px-3 text-right text-emerald-400 font-bold">+${(c.momentum_score * 100).toFixed(0)}%</td>
          <td class="py-2 px-3 text-center text-[10px]">${c.trend_ok ? '<span class="text-emerald-400 font-bold">✓ PASS</span>' : '<span class="text-rose-400 font-bold">✗ FAIL</span>'}</td>
          <td class="py-2 px-3 text-[11px] text-slate-400 font-sans max-w-xs truncate">${c.action_reason}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function formatPrice(p) {
      if (!p) return '0.00';
      if (p >= 1000) return Number(p).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (p >= 1) return Number(p).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 });
      return Number(p).toFixed(6);
    }
  </script>
</body>
</html>
"""


def generate_html():
    with open(COMBINED_DATA_PATH, "r", encoding="utf-8") as f:
        combined = json.load(f)

    json_str = json.dumps(combined, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__COMBINED_DATA__", json_str)

    OUT_HTML.write_text(html, encoding="utf-8")
    if PARENT_HTML.parent.exists():
        PARENT_HTML.write_text(html, encoding="utf-8")

    print(f"[+] Successfully generated Dynamic Strategy-Aware Dashboard HTML:")
    print(f"    - Output: {OUT_HTML} ({len(html):,} bytes)")
    print(f"    - Parent: {PARENT_HTML} ({len(html):,} bytes)")


if __name__ == "__main__":
    generate_html()
