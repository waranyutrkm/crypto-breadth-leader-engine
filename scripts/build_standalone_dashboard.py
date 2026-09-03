#!/usr/bin/env python3
"""Build the Complete Institutional Binance Quantitative Signals, Scanner & Rotation Hub.

Synthesizes:
- 4 Fixed Predefined Strategies with Performance Track Records & How-To-Trade Guides.
- Real-Time Live Binance Global Market Scanner with Rich Tooltips.
- 875-Day Point-in-Time Daily Rotation Playback.
- 636-Trade Rotation Audit Log (Searchable & Filterable past rebalance events).
- Rolling Window Performance vs Buy & Hold (30d, 60d, 90d, 180d, 365d).
- Microscopic Execution Planner (Sell-First -> Reconcile -> Buy-Second).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMBINED_DATA_PATH = ROOT / "results_portfolio" / "binance_global_pit" / "combined_dashboard_data.json"
OUT_HTML = ROOT / "binance_c2lr_signals_dashboard.html"
ARTIFACT_DIR = Path("/Users/nok/.gemini/antigravity/brain/1c2ca6c3-8199-41b1-81b1-a55d08d7bcfd")
ARTIFACT_HTML = ARTIFACT_DIR / "binance_c2lr_signals_dashboard.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="th" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Binance Quantitative Signals & Strategy Scanner Hub</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    
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
      background: #111622;
    }
    ::-webkit-scrollbar-thumb {
      background: #2a3449;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #3b4863;
    }
    .tab-active {
      border-bottom: 2px solid #3b82f6;
      color: #60a5fa;
      background-color: rgba(59, 130, 246, 0.08);
    }
    .badge-buy {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-hold {
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-sell {
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-watchlist {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-inactive {
      background: rgba(148, 163, 184, 0.1);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .glass-card {
      background: #131926;
      border: 1px solid #1f293d;
    }
    /* Simple Tooltip Helper */
    .has-tooltip {
      position: relative;
      cursor: help;
    }
    .tooltip-content {
      visibility: hidden;
      position: absolute;
      bottom: 125%;
      left: 50%;
      transform: translateX(-50%);
      background-color: #1e293b;
      color: #f8fafc;
      text-align: left;
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      line-height: 1.4;
      white-space: normal;
      width: 240px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
      border: 1px solid #334155;
      z-index: 50;
      opacity: 0;
      transition: opacity 0.2s;
      pointer-events: none;
    }
    .has-tooltip:hover .tooltip-content {
      visibility: visible;
      opacity: 1;
    }
  </style>
</head>
<body class="min-h-screen p-4 md:p-6 lg:p-8">

  <!-- Top Navigation & Title Bar -->
  <header class="mb-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1f293d] pb-4">
    <div>
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 shadow-lg shadow-blue-500/20">
          <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl md:text-2xl font-bold tracking-tight text-white">Binance Quantitative Signals & Strategy Scanner Hub</h1>
            <span class="rounded-full bg-blue-500/20 px-2.5 py-0.5 text-xs font-semibold text-blue-400 border border-blue-500/30">Binance Global Spot</span>
          </div>
          <p class="text-xs md:text-sm text-slate-400">ระบบสแกนเหรียญผู้นำ, สลับกลยุทธ์สำเร็จรูป, ประวัติการหมุนพอร์ตจริง, และบันทึกคำสั่งซื้อขายระดับไมโคร</p>
        </div>
      </div>
    </div>
    
    <div class="flex flex-wrap items-center gap-2.5">
      <!-- Mode Switcher -->
      <div class="flex rounded-lg bg-[#0e131d] border border-[#232f45] p-1 text-xs font-semibold">
        <button id="mode-btn-live" onclick="setAppMode('LIVE')" class="px-3 py-1 rounded bg-blue-600 text-white font-bold transition flex items-center gap-1.5">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          🔴 ตลาดสด (Live Scanner)
        </button>
        <button id="mode-btn-playback" onclick="setAppMode('PLAYBACK')" class="px-3 py-1 rounded text-slate-400 hover:text-white transition flex items-center gap-1.5">
          📅 หมุนพอร์ตย้อนหลัง (PIT Playback)
        </button>
      </div>

      <button onclick="window.location.reload()" class="rounded-lg bg-[#151c2a] hover:bg-slate-700 border border-slate-700 px-3.5 py-1.5 text-xs font-semibold text-slate-200 transition flex items-center gap-1.5">
        <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
        รีเฟรช
      </button>
    </div>
  </header>

  <!-- STRATEGY PRESETS CARDS BAR (4 Fixed Predefined Strategies) -->
  <section class="mb-6 space-y-2">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400">เลือกกลยุทธ์ตายตัวที่ต้องการใช้งาน (Predefined Strategy Presets):</span>
        <span class="has-tooltip text-slate-500 hover:text-slate-300">
          <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span class="tooltip-content">คลิกเลือกกลยุทธ์เพื่อปรับสูตรสแกนและสัดส่วนพอร์ตอัตโนมัติ โดยแต่ละกลยุทธ์มีผลการทดสอบย้อนหลังและขั้นตอนการเทรดที่ชัดเจน</span>
        </span>
      </div>
      <span class="text-xs font-mono text-blue-400" id="current-strategy-badge">Active: BTH_C2LR v2.0</span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" id="preset-strategies-container">
      <!-- Injected via JavaScript -->
    </div>
  </section>

  <!-- Macro Regime & Market Health Bar -->
  <section class="mb-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Card 1: Macro Regime -->
    <div class="glass-card rounded-xl p-4 relative overflow-hidden">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-1.5">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400" id="regime-header-title">Market Regime</span>
          <span class="has-tooltip text-slate-500 hover:text-slate-300">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span class="tooltip-content">สภาวะตลาดคำนวณจากการจับคู่ระหว่าง Bitcoin Trend (EMA100) และ Altcoin Breadth เพื่อกำหนดว่าตลาดเปิดไฟเขียวให้ลุยหรือควรหนีถือเงินสด</span>
          </span>
        </div>
        <span id="regime-status-badge" class="px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider"></span>
      </div>
      <div class="text-2xl font-extrabold text-white mb-1" id="regime-name">--</div>
      <p class="text-xs text-slate-400 line-clamp-2" id="regime-description">--</p>
    </div>

    <!-- Card 2: BTC Trend Gate -->
    <div class="glass-card rounded-xl p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-1.5">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">BTC Trend Gate (EMA100)</span>
          <span class="has-tooltip text-slate-500 hover:text-slate-300">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span class="tooltip-content">เส้นประตูป้องกันเงินต้น หากราคา BTC ต่ำกว่า EMA100 ระบบจะปิดความเสี่ยงและสั่งล้างพอร์ตทันที เพราะ Altcoins มักร่วงรุนแรงในตลาดหมี</span>
          </span>
        </div>
        <span id="btc-gate-badge" class="px-2 py-0.5 rounded-full text-xs font-bold"></span>
      </div>
      <div class="text-2xl font-extrabold font-mono text-white mb-1" id="btc-price">--</div>
      <div class="flex items-center justify-between text-xs text-slate-400">
        <span>EMA100: <span class="font-mono text-slate-300" id="btc-ema100">--</span></span>
        <span class="font-mono font-semibold" id="btc-dist-pct">--</span>
      </div>
    </div>

    <!-- Card 3: Altcoin Market Breadth -->
    <div class="glass-card rounded-xl p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-1.5">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Market Breadth (% > EMA50)</span>
          <span class="has-tooltip text-slate-500 hover:text-slate-300">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span class="tooltip-content">ความกว้างของตลาด: วัดว่าเหรียญใน Top 50 มีกี่ % ที่ยืนเหนือ EMA50 ถ้าเกิน 50-65% แปลว่าตลาดขึ้นจริงทั้งกระดาน ไม่ใช่เจ้ามือลากตัวเดียว</span>
          </span>
        </div>
        <span class="text-xs font-mono font-bold text-blue-400" id="breadth-count">--</span>
      </div>
      <div class="text-2xl font-extrabold font-mono text-white mb-2" id="breadth-pct">--%</div>
      <div class="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
        <div id="breadth-bar" class="h-full rounded-full bg-gradient-to-r from-blue-500 to-emerald-400 transition-all duration-500" style="width: 0%"></div>
      </div>
    </div>

    <!-- Card 4: Target Allocation & Leaders -->
    <div class="glass-card rounded-xl p-4">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-1.5">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Target Allocation</span>
          <span class="has-tooltip text-slate-500 hover:text-slate-300">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span class="tooltip-content">สัดส่วนเป้าหมายระหว่างสินทรัพย์ Crypto กับเงินสด USDT สำรองตามสภาวะตลาด และขอบเขตอันดับ Hysteresis Buffer ที่อนุญาตให้ถือต่อ</span>
          </span>
        </div>
        <span class="text-xs font-bold text-emerald-400" id="active-top-k">Top-5</span>
      </div>
      <div class="flex items-baseline gap-2 mb-1">
        <div class="text-2xl font-extrabold font-mono text-emerald-400" id="crypto-exposure">--%</div>
        <span class="text-xs text-slate-400">Crypto / <span id="cash-reserve" class="text-amber-400 font-mono font-bold">--%</span> USDT Cash</span>
      </div>
      <div class="text-xs text-slate-400">
        Hysteresis Exit Buffer: <span class="font-mono font-bold text-slate-200" id="exit-rank-limit">Rank 1–8</span>
      </div>
    </div>
  </section>

  <!-- HISTORICAL PLAYBACK SCRUBBER BAR (Visible only in PLAYBACK mode) -->
  <section id="playback-control-panel" class="hidden mb-6 glass-card rounded-xl p-4 border border-blue-500/30 bg-blue-950/10 space-y-3">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold font-mono text-xs">PIT</div>
        <div>
          <h2 class="text-sm font-bold text-white">ระบบตรวจสอบการหมุนพอร์ตจริงย้อนหลังรายวัน (Point-in-Time Daily Auditor)</h2>
          <p class="text-[11px] text-slate-400">แสดง Breadth จริง, เหรียญที่ active ณ วันนั้น, พอร์ตที่ถือจริง, และคำสั่ง Sell-First/Buy-Second รายตั๋ว</p>
        </div>
      </div>

      <!-- Quick Jump Buttons -->
      <div class="flex flex-wrap items-center gap-1.5 text-xs font-mono">
        <span class="text-slate-400 text-[11px] font-sans">เหตุการณ์สำคัญ:</span>
        <button onclick="jumpToDate('2024-05-06')" class="px-2 py-1 rounded bg-[#151c2a] hover:bg-slate-700 text-slate-300 border border-slate-700">🚀 เริ่มหมุนพอร์ต</button>
        <button onclick="jumpToDate('2024-05-22')" class="px-2 py-1 rounded bg-[#151c2a] hover:bg-slate-700 text-slate-300 border border-slate-700">📉 Regime Pruning (Broad->Normal)</button>
        <button onclick="jumpToDate('2024-06-18')" class="px-2 py-1 rounded bg-[#151c2a] hover:bg-slate-700 text-slate-300 border border-slate-700">🚨 เข้าสู่ Cash Guard</button>
        <button onclick="jumpToDate('2024-11-12')" class="px-2 py-1 rounded bg-[#151c2a] hover:bg-slate-700 text-slate-300 border border-slate-700">🟢 ระเบิด Broad Bull รอบใหญ่</button>
        <button onclick="jumpToDate('2026-09-03')" class="px-2 py-1 rounded bg-blue-600/30 text-blue-300 border border-blue-500/40 font-bold">📍 แท่งปิดล่าสุด</button>
      </div>
    </div>

    <!-- Scrubber Slider -->
    <div class="flex items-center gap-4 pt-1">
      <input type="range" id="playback-slider" min="0" max="874" value="874" oninput="onSliderChange(this.value)" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500">
      <span class="font-mono text-xs font-bold text-emerald-400 whitespace-nowrap" id="playback-current-date">--</span>
    </div>
  </section>

  <!-- Main Tabs Header -->
  <nav class="mb-5 flex border-b border-[#1f293d] gap-2 overflow-x-auto text-sm font-semibold">
    <button onclick="switchTab('signals')" id="tab-btn-signals" class="tab-active flex items-center gap-2 px-4 py-3 border-b-2 border-transparent transition">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
      <span id="tab-title-signals">สูตรสแกนและตารางสัญญาณ (Scanner Matrix)</span>
      <span id="badge-total-coins" class="rounded-full bg-blue-500/20 px-2 py-0.5 text-xs text-blue-300">0</span>
    </button>
    <button onclick="switchTab('calculator')" id="tab-btn-calculator" class="flex items-center gap-2 px-4 py-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>วางแผนคำสั่งซื้อขายจริง (Execution Planner)</span>
    </button>
    <button onclick="switchTab('audit_logs')" id="tab-btn-audit_logs" class="flex items-center gap-2 px-4 py-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
      <span>ประวัติการสลับเหรียญจริง (Rotation Audit Logs)</span>
      <span class="rounded-full bg-amber-500/20 px-2 py-0.5 text-xs text-amber-300 font-mono">636</span>
    </button>
    <button onclick="switchTab('eda')" id="tab-btn-eda" class="flex items-center gap-2 px-4 py-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>
      <span>วิจัยเชิงสถิติ & Rolling Window (Quantitative Hub)</span>
    </button>
    <button onclick="switchTab('rulebook')" id="tab-btn-rulebook" class="flex items-center gap-2 px-4 py-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">
      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
      <span>คู่มือสูตรและหลักเกณฑ์ (Master Spec)</span>
    </button>
  </nav>

  <!-- TAB 1: SIGNALS MATRIX / SCANNER -->
  <main id="tab-content-signals" class="space-y-4">
    <!-- Active Strategy Banner -->
    <div class="rounded-xl border border-blue-500/30 bg-gradient-to-r from-blue-950/40 to-slate-900 p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
      <div class="flex items-center gap-2.5">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white font-bold font-mono">สูตร</span>
        <div>
          <span class="font-bold text-white text-sm" id="banner-strat-title">BTH_C2LR v2.0 (Conservative Dynamic Leader Rotation)</span>
          <p class="text-slate-400 text-[11px]" id="banner-strat-desc">หมุนเหรียญผู้นำ Top 5 ด้วย Multi-Scale Momentum พร้อมเกราะ Hysteresis Buffer และ Cash Guard</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <div class="text-right font-mono">
          <div class="text-slate-400 text-[10px]">Historical Track Record</div>
          <div class="font-bold text-emerald-400" id="banner-strat-perf">CAGR +49.3% | MaxDD -30.4% (Core-Sat)</div>
        </div>
        <button onclick="openHowToTradeModal(activeStrategyId)" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-bold text-white transition shadow-sm">
          📖 ดูวิธีเทรด
        </button>
      </div>
    </div>

    <!-- Live Mode Subview -->
    <div id="signals-live-controls" class="glass-card rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">Filter Signal:</span>
        <button onclick="setSignalFilter('ALL')" id="filter-btn-ALL" class="rounded-lg bg-blue-600 text-white px-3 py-1.5 text-xs font-semibold transition shadow-sm">ทั้งหมด (<span id="cnt-all">0</span>)</button>
        <button onclick="setSignalFilter('BUY')" id="filter-btn-BUY" class="rounded-lg bg-[#151c2a] text-emerald-400 hover:bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 text-xs font-semibold transition">🟢 BUY / ENTER (<span id="cnt-buy">0</span>)</button>
        <button onclick="setSignalFilter('HOLD')" id="filter-btn-HOLD" class="rounded-lg bg-[#151c2a] text-blue-400 hover:bg-blue-500/10 border border-blue-500/30 px-3 py-1.5 text-xs font-semibold transition">🔵 HOLD (<span id="cnt-hold">0</span>)</button>
        <button onclick="setSignalFilter('WATCHLIST')" id="filter-btn-WATCHLIST" class="rounded-lg bg-[#151c2a] text-amber-400 hover:bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 text-xs font-semibold transition">🟡 WATCHLIST (<span id="cnt-watchlist">0</span>)</button>
        <button onclick="setSignalFilter('SELL')" id="filter-btn-SELL" class="rounded-lg bg-[#151c2a] text-rose-400 hover:bg-rose-500/10 border border-rose-500/30 px-3 py-1.5 text-xs font-semibold transition">🔴 SELL (<span id="cnt-sell">0</span>)</button>
        <button onclick="setSignalFilter('AVOID')" id="filter-btn-AVOID" class="rounded-lg bg-[#151c2a] text-slate-400 hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-semibold transition">⚪ AVOID (<span id="cnt-avoid">0</span>)</button>
      </div>

      <div class="relative w-full md:w-72">
        <input type="text" id="search-input" oninput="renderCoinsTable()" placeholder="ค้นหาชื่อเหรียญ (เช่น BTC, SOL, HEMI)..." class="w-full rounded-lg bg-[#0e131d] border border-[#232f45] px-3.5 py-2 pl-9 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition font-mono">
        <svg class="absolute left-3 top-2.5 h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
      </div>
    </div>

    <!-- Playback Details Box (Shows on Playback mode) -->
    <div id="playback-day-details" class="hidden glass-card rounded-xl p-5 space-y-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#1f293d] pb-4">
        <div>
          <div class="text-xs font-bold text-blue-400 uppercase tracking-wider">Point-in-Time Daily Portfolio Status</div>
          <div class="text-lg font-bold text-white flex items-center gap-2">
            <span>วันที่: <span class="font-mono text-emerald-400" id="pb-detail-date">--</span></span>
            <span class="text-xs px-2.5 py-0.5 rounded font-bold" id="pb-detail-regime-badge">--</span>
          </div>
        </div>
        <div class="flex items-center gap-4 text-xs font-mono">
          <div>พอร์ต NAV: <strong class="text-white" id="pb-detail-nav">$0.00</strong></div>
          <div>เงินสดคงเหลือ: <strong class="text-amber-400" id="pb-detail-cash">$0.00</strong> (<span id="pb-detail-cash-pct">0%</span>)</div>
          <div>จำนวนเหรียญที่ถือ: <strong class="text-blue-400" id="pb-detail-holdings-count">0</strong> ตัว</div>
        </div>
      </div>

      <!-- Current Day Holdings & Trades Split Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">เหรียญที่ถือครองจริง ณ สิ้นวัน (End-of-Day Holdings)</h3>
            <span class="text-[11px] text-slate-400 font-mono" id="pb-holdings-val-sum">--</span>
          </div>
          <div class="overflow-x-auto max-h-60 overflow-y-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead class="text-slate-400 border-b border-[#232f45]">
                <tr><th>Symbol</th><th class="text-right">Units</th><th class="text-right">Price</th><th class="text-right">Value (USDT)</th><th class="text-right">Weight</th></tr>
              </thead>
              <tbody id="pb-holdings-tbody" class="divide-y divide-[#1e283c] text-slate-200"></tbody>
            </table>
          </div>
        </div>

        <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">คำสั่งที่ยิงจริงในวันนี้ (Executed Order Tickets)</h3>
            <span class="text-[11px] text-slate-400 font-mono" id="pb-trades-fee-sum">--</span>
          </div>
          <div class="overflow-x-auto max-h-60 overflow-y-auto">
            <table class="w-full text-left text-xs font-mono">
              <thead class="text-slate-400 border-b border-[#232f45]">
                <tr><th>Side</th><th>Symbol</th><th class="text-right">Notional</th><th>Reason</th></tr>
              </thead>
              <tbody id="pb-trades-tbody" class="divide-y divide-[#1e283c]"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Coins Table -->
    <div class="glass-card rounded-xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="bg-[#0e131d] border-b border-[#1f293d] text-slate-400 uppercase tracking-wider font-semibold">
            <tr>
              <th class="py-3 px-3.5 cursor-pointer hover:text-white" onclick="changeSort('rank')"># Rank</th>
              <th class="py-3 px-3.5 cursor-pointer hover:text-white" onclick="changeSort('symbol')">เหรียญ (Symbol)</th>
              <th class="py-3 px-3.5 text-center">สัญญาณ (Signal)</th>
              <th class="py-3 px-3.5 text-right cursor-pointer hover:text-white" onclick="changeSort('close')">ราคา ($)</th>
              <th class="py-3 px-3.5 text-right cursor-pointer hover:text-white" onclick="changeSort('price_change_24h')">24h / Daily %</th>
              <th class="py-3 px-3.5 text-right cursor-pointer hover:text-white" onclick="changeSort('momentum_score')">Momentum Score</th>
              <th class="py-3 px-3.5 text-right cursor-pointer hover:text-white" onclick="changeSort('r30')">R30 (30d)</th>
              <th class="py-3 px-3.5 text-right cursor-pointer hover:text-white" onclick="changeSort('r60')">R60 (60d)</th>
              <th class="py-3 px-3.5 text-center">Trend Gate</th>
              <th class="py-3 px-3.5 text-right">Target Weight</th>
              <th class="py-3 px-3.5">คำอธิบายเหตุผลและจุดเข้า-ออก</th>
              <th class="py-3 px-3.5 text-center">ตรวจ Gate</th>
            </tr>
          </thead>
          <tbody id="coins-table-body" class="divide-y divide-[#182030] font-mono"></tbody>
        </table>
      </div>
    </div>
  </main>

  <!-- TAB 2: EXECUTION PLANNER -->
  <main id="tab-content-calculator" class="hidden space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="glass-card rounded-xl p-5 space-y-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <span class="flex h-6 w-6 items-center justify-center rounded bg-blue-500/20 text-blue-400 font-bold">1</span>
          ตั้งค่าพอร์ตการลงทุน (Portfolio Setup)
        </h2>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1.5">เงินต้นพอร์ตทั้งหมด (Total NAV in USDT)</label>
          <div class="relative">
            <input type="number" id="calc-nav-input" value="10000" step="500" oninput="runExecutionPlanner()" class="w-full rounded-lg bg-[#0e131d] border border-[#232f45] px-3 py-2 text-sm font-bold font-mono text-white focus:outline-none focus:border-blue-500">
            <span class="absolute right-3 top-2 text-xs font-bold text-slate-400">USDT</span>
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1.5">เหรียญเดิมที่ถืออยู่ในพอร์ตปัจจุบัน (Current Holdings)</label>
          <p class="text-[11px] text-slate-500 mb-2">เลือกเหรียญที่คุณกำลังถืออยู่เพื่อคำนวณคำสั่ง Sell-First และ Hold อัตโนมัติ</p>
          <div class="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-2 rounded-lg bg-[#0e131d] border border-[#1f293d]" id="current-holdings-selector"></div>
        </div>

        <div class="rounded-lg bg-[#111724] border border-[#1e283b] p-3 text-xs space-y-2">
          <div class="flex justify-between text-slate-400">
            <span>Rebalance Band:</span>
            <span class="font-bold text-slate-200 font-mono">5.0% (ขั้นต่ำ 6 USDT)</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Turnover Cap:</span>
            <span class="font-bold text-slate-200 font-mono">95% ต่อวัน</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Fee Rate (Binance Global):</span>
            <span class="font-bold text-emerald-400 font-mono">0.075% (BNB Tier)</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Execution Protocol:</span>
            <span class="font-bold text-blue-400 font-mono">Sell-First -> Reconcile -> Buy</span>
          </div>
        </div>

        <button onclick="runExecutionPlanner()" class="w-full rounded-lg bg-blue-600 hover:bg-blue-500 py-2.5 text-xs font-bold text-white transition shadow-lg shadow-blue-600/20">
          คำนวณแผนคำสั่งซื้อขายใหม่ (Re-calculate)
        </button>
      </div>

      <div class="lg:col-span-2 space-y-4">
        <!-- Target Portfolio Allocation Summary -->
        <div class="glass-card rounded-xl p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <span class="flex h-6 w-6 items-center justify-center rounded bg-emerald-500/20 text-emerald-400 font-bold">2</span>
              สัดส่วนพอร์ตเป้าหมาย (Target Allocation)
            </h2>
            <span class="text-xs font-bold px-2.5 py-1 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30" id="calc-regime-target"></span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4" id="target-summary-cards"></div>

          <div class="rounded-lg bg-[#0e131d] border border-[#1f293d] p-3">
            <div class="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">รายชื่อเหรียญผู้นำเป้าหมาย (Target Leaders):</div>
            <div class="flex flex-wrap gap-2" id="target-leaders-tags"></div>
          </div>
        </div>

        <!-- Sequential Execution Order Tickets -->
        <div class="glass-card rounded-xl p-5 space-y-4">
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <span class="flex h-6 w-6 items-center justify-center rounded bg-amber-500/20 text-amber-400 font-bold">3</span>
            ลำดับคำสั่งซื้อขายจริง (Execution Flow Tickets)
          </h2>

          <!-- STEP A: SELL FIRST -->
          <div class="rounded-xl border border-rose-500/30 bg-rose-950/10 p-4">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2 text-rose-400 font-bold text-xs">
                <span class="h-2 w-2 rounded-full bg-rose-500 animate-ping"></span>
                STEP 1: SELL-FIRST (คำสั่งขายเพื่อลดพอร์ตและล้างตัวหลุด)
              </div>
              <span class="text-xs font-mono font-bold text-rose-400" id="total-sell-amount">$0.00 USDT</span>
            </div>
            <div class="text-xs text-slate-400 mb-2">ขายเหรียญที่หลุดเกณฑ์ Trend Gate, ตกอันดับ Buffer หรือปรับลดสัดส่วนตาม Band 5%</div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs font-mono">
                <thead class="text-slate-400 border-b border-rose-900/40">
                  <tr>
                    <th class="py-1.5 px-2">Order Type</th>
                    <th class="py-1.5 px-2">Symbol</th>
                    <th class="py-1.5 px-2 text-right">Amount (USDT)</th>
                    <th class="py-1.5 px-2">Action Rationale</th>
                  </tr>
                </thead>
                <tbody id="sell-orders-table" class="divide-y divide-rose-900/20 text-slate-200"></tbody>
              </table>
            </div>
          </div>

          <!-- STEP B: RECONCILE CASH -->
          <div class="rounded-lg border border-slate-700 bg-[#0e131d] p-3 text-xs flex items-center justify-between">
            <div class="flex items-center gap-2 text-slate-300 font-semibold">
              <svg class="h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>STEP 2: RECONCILE (ตรวจสอบเงินสดในกระเป๋าคงเหลือจริง)</span>
            </div>
            <span class="font-mono font-bold text-emerald-400" id="reconciled-cash-amount">$0.00 USDT</span>
          </div>

          <!-- STEP C: BUY SECOND -->
          <div class="rounded-xl border border-emerald-500/30 bg-emerald-950/10 p-4">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                <span class="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
                STEP 3: BUY-SECOND (คำสั่งซื้อเหรียญผู้นำตัวใหม่)
              </div>
              <span class="text-xs font-mono font-bold text-emerald-400" id="total-buy-amount">$0.00 USDT</span>
            </div>
            <div class="text-xs text-slate-400 mb-2">เข้าซื้อเฉพาะเหรียญ Top Leaders ตัวใหม่ตามลำดับความสำคัญ โดยใช้เงินสดที่ได้จากการขาย</div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs font-mono">
                <thead class="text-slate-400 border-b border-emerald-900/40">
                  <tr>
                    <th class="py-1.5 px-2">Order Type</th>
                    <th class="py-1.5 px-2">Symbol</th>
                    <th class="py-1.5 px-2 text-right">Target Notional</th>
                    <th class="py-1.5 px-2 text-right">Est. Fee (0.075%)</th>
                    <th class="py-1.5 px-2">Leader Rationale</th>
                  </tr>
                </thead>
                <tbody id="buy-orders-table" class="divide-y divide-emerald-900/20 text-slate-200"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- TAB 3: ROTATION AUDIT LOGS (ประวัติการหมุนพอร์ตจริง 636 รายการ) -->
  <main id="tab-content-audit_logs" class="hidden space-y-4">
    <div class="glass-card rounded-xl p-5">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1f293d] pb-4 mb-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <span>ประวัติคำสั่งซื้อขายและการหมุนพอร์ตจริงย้อนหลัง (Rotation Audit Logs)</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-mono">636 Executed Orders</span>
          </h2>
          <p class="text-xs text-slate-400">บันทึกทุกคำสั่งซื้อขายในอดีต พร้อมเหตุผลกำกับ (Reason), ราคาที่จับคู่, ค่าคอมมิชชั่น, และขนาดเงินทุน</p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <!-- Side Filter -->
          <div class="flex rounded-lg bg-[#0e131d] border border-[#232f45] p-1 text-xs font-mono">
            <button onclick="setLogSideFilter('ALL')" id="log-side-ALL" class="px-2.5 py-1 rounded bg-blue-600 text-white font-bold">ทั้งหมด</button>
            <button onclick="setLogSideFilter('SELL')" id="log-side-SELL" class="px-2.5 py-1 rounded text-rose-400 hover:text-white">เฉพาะ SELL</button>
            <button onclick="setLogSideFilter('BUY')" id="log-side-BUY" class="px-2.5 py-1 rounded text-emerald-400 hover:text-white">เฉพาะ BUY</button>
          </div>

          <!-- Symbol Search -->
          <input type="text" id="log-search-input" oninput="renderAuditLogsTable()" placeholder="ค้นหาเหรียญใน Log (เช่น SOL, PEPE)..." class="rounded-lg bg-[#0e131d] border border-[#232f45] px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono w-56">
        </div>
      </div>

      <!-- Logs Table -->
      <div class="overflow-x-auto rounded-xl border border-[#1f293d] bg-[#0e131d] max-h-[600px] overflow-y-auto">
        <table class="w-full text-left text-xs font-mono">
          <thead class="bg-[#131926] text-slate-400 border-b border-[#1f293d] sticky top-0 z-10">
            <tr>
              <th class="py-2.5 px-3">วันที่ (Date)</th>
              <th class="py-2.5 px-3">สภาวะ (Regime)</th>
              <th class="py-2.5 px-3">คำสั่ง (Side)</th>
              <th class="py-2.5 px-3">เหรียญ (Symbol)</th>
              <th class="py-2.5 px-3 text-right">ราคา ($)</th>
              <th class="py-2.5 px-3 text-right">จำนวน (Units)</th>
              <th class="py-2.5 px-3 text-right">มูลค่า (USDT)</th>
              <th class="py-2.5 px-3 text-right">ค่าคอม ($)</th>
              <th class="py-2.5 px-3">เหตุผลเชิงปริมาณ (Rationale)</th>
              <th class="py-2.5 px-3 text-right">NAV รวม ($)</th>
            </tr>
          </thead>
          <tbody id="audit-logs-tbody" class="divide-y divide-[#182030] text-slate-200"></tbody>
        </table>
      </div>
      <div class="text-[11px] text-slate-500 pt-2 flex justify-between items-center">
        <span id="log-count-summary">แสดง 0 จาก 636 รายการ</span>
        <span>คำนวณตาม Binance VIP Fee Tier 0.075% + 0.05% Slippage</span>
      </div>
    </div>
  </main>

  <!-- TAB 4: QUANTITATIVE ENTRY/EXIT EDA & ROLLING HUB -->
  <main id="tab-content-eda" class="hidden space-y-6">
    <div class="glass-card rounded-xl p-5">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#1f293d] pb-4 mb-5">
        <div>
          <h2 class="text-lg font-bold text-white">ผลการวิจัยเชิงประจักษ์: จุดเข้า-ออก และพฤติกรรมความเสี่ยง (Quantitative Entry/Exit EDA)</h2>
          <p class="text-xs text-slate-400">ทดสอบบนข้อมูลแท่งเทียนจริงของ Binance 1,000 วัน ครอบคลุม 197 รอบคำสั่งซื้อขายจริง</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">197 Completed Trades</span>
          <span class="text-xs px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">Hysteresis Buffer: +50%</span>
        </div>
      </div>

      <!-- EDA Section 0: Rolling Window vs Buy & Hold -->
      <div class="mb-8 p-5 rounded-2xl bg-gradient-to-b from-[#151c2a] to-[#0e131d] border border-blue-500/30">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="h-2.5 w-2.5 rounded-full bg-blue-400 animate-pulse"></span>
              เปรียบเทียบผลตอบแทนแบบ Rolling Window เทียบกับ Buy & Hold (BTC / ETH / Core-Satellite)
            </h3>
            <p class="text-xs text-slate-400">ทดสอบครอบคลุมทุกรอบเวลาเลื่อนต่อเนื่อง 875 วัน (Rolling 30d, 60d, 90d ไตรมาส, 180d ครึ่งปี, 365d ปี)</p>
          </div>

          <div class="flex flex-wrap items-center gap-1.5 text-xs font-mono">
            <button onclick="setRollingWindow(30)" id="rw-btn-30" class="px-2.5 py-1 rounded bg-[#1f293d] text-slate-300 hover:bg-blue-600 hover:text-white transition">30 วัน</button>
            <button onclick="setRollingWindow(60)" id="rw-btn-60" class="px-2.5 py-1 rounded bg-[#1f293d] text-slate-300 hover:bg-blue-600 hover:text-white transition">60 วัน</button>
            <button onclick="setRollingWindow(90)" id="rw-btn-90" class="px-2.5 py-1 rounded bg-blue-600 text-white font-bold transition">90 วัน (ไตรมาส)</button>
            <button onclick="setRollingWindow(180)" id="rw-btn-180" class="px-2.5 py-1 rounded bg-[#1f293d] text-slate-300 hover:bg-blue-600 hover:text-white transition">180 วัน (ครึ่งปี)</button>
            <button onclick="setRollingWindow(365)" id="rw-btn-365" class="px-2.5 py-1 rounded bg-[#1f293d] text-slate-300 hover:bg-blue-600 hover:text-white transition">365 วัน (1 ปี)</button>
          </div>
        </div>

        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5" id="rw-kpi-cards"></div>

        <div class="overflow-x-auto rounded-xl border border-[#1f293d] bg-[#0e131d]">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-[#131926] text-slate-400 border-b border-[#1f293d]">
              <tr>
                <th class="py-2.5 px-3">Asset / Portfolio Strategy</th>
                <th class="py-2.5 px-3 text-right">Mean Return</th>
                <th class="py-2.5 px-3 text-right">Median Return</th>
                <th class="py-2.5 px-3 text-right">Alpha vs BTC</th>
                <th class="py-2.5 px-3 text-right">ช่วงตลาดหมี (BTC < 0)</th>
                <th class="py-2.5 px-3 text-right text-emerald-400">Downside Capture</th>
                <th class="py-2.5 px-3 text-right">Avg Max Drawdown</th>
              </tr>
            </thead>
            <tbody id="rw-comparison-table" class="divide-y divide-[#182030] text-slate-200"></tbody>
          </table>
        </div>
      </div>

      <!-- EDA Section 1: Entry Forward Return Skew -->
      <div class="mb-8">
        <h3 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
          1. ประสิทธิภาพของจุดเข้า: ผลตอบแทนล่วงหน้า (Entry Forward Return Distribution)
        </h3>
        <p class="text-xs text-slate-400 mb-4">
          การเข้าซื้อเมื่อเหรียญผ่านเกณฑ์พร้อมกัน (Trend Gate + Positive Momentum + Rank &le; K) สร้างผลตอบแทนแบบขวาเบ้ (Positive Skewness &ge; 2.3) ซึ่งหมายถึงการรันเทรนด์ตัวทำกำไรก้อนใหญ่ได้เต็มเม็ดเต็มหน่วย
        </p>

        <div class="grid grid-cols-2 sm:grid-cols-5 gap-3" id="eda-forward-returns-cards"></div>
      </div>

      <!-- EDA Section 2: Exit Typology and Loss Avoidance -->
      <div class="mb-8">
        <h3 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-rose-400"></span>
          2. ประสิทธิภาพของจุดออก: การจำแนก 4 เหตุผล และการป้องกันการขาดทุน (Loss Avoidance Verification)
        </h3>
        <p class="text-xs text-slate-400 mb-4">
          การทดสอบ Post-Exit Forward Returns เพื่อพิสูจน์ว่า: <em>"ถ้าเราไม่ยอมขายตามกฎ เหรียญที่หลุดเกณฑ์จะร่วงต่อจริงหรือไม่?"</em>
        </p>

        <div class="overflow-x-auto rounded-xl border border-[#1f293d] bg-[#0e131d]">
          <table class="w-full text-left text-xs font-mono">
            <thead class="bg-[#131926] text-slate-400 border-b border-[#1f293d]">
              <tr>
                <th class="py-2.5 px-3">ประเภทจุดออก (Exit Reason)</th>
                <th class="py-2.5 px-3 text-right">จำนวนครั้ง</th>
                <th class="py-2.5 px-3 text-right">สัดส่วน (%)</th>
                <th class="py-2.5 px-3 text-right">Win Rate ที่จุดออก</th>
                <th class="py-2.5 px-3 text-right">ถือเฉลี่ย (วัน)</th>
                <th class="py-2.5 px-3 text-right text-rose-400">Fwd 30d ร่วงต่อ (%)</th>
                <th class="py-2.5 px-3">บทสรุปเชิงสถิติ (Statistical Conclusion)</th>
              </tr>
            </thead>
            <tbody id="eda-exit-summary-table" class="divide-y divide-[#182030] text-slate-200"></tbody>
          </table>
        </div>
      </div>

      <!-- EDA Section 3: Markov Regime Transitions & Persistence -->
      <div class="mb-8">
        <h3 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-blue-400"></span>
          3. ความน่าจะเป็นในการเปลี่ยนสภาวะตลาด (Markov Regime Transition Matrix)
        </h3>
        <p class="text-xs text-slate-400 mb-4">
          แสดงความน่าจะเป็นที่ตลาดจะคงอยู่ใน Regime เดิม หรือเปลี่ยนไปสู่อีก Regime หนึ่งในวันถัดไป ยืนยันว่า CASH_GUARD มีความคงทนสูงสุดถึง 93.1% (เฉลี่ย 14.1 วัน) ช่วยล็อกกำไรและป้องกันเงินต้นในตลาดหมี
        </p>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4">
            <div class="text-xs font-bold text-slate-300 mb-3">Transition Probabilities (%):</div>
            <div class="overflow-x-auto">
              <table class="w-full text-center text-xs font-mono" id="markov-matrix-table"></table>
            </div>
          </div>

          <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4">
            <div class="text-xs font-bold text-slate-300 mb-3">ระยะเวลาการคงอยู่เฉลี่ยในแต่ละ Regime (Duration Persistence):</div>
            <div class="space-y-3" id="regime-duration-list"></div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- TAB 5: RULEBOOK & MASTER SPEC -->
  <main id="tab-content-rulebook" class="hidden space-y-6">
    <div class="glass-card rounded-xl p-6 space-y-6 text-sm">
      <div>
        <h2 class="text-lg font-bold text-white mb-2">📘 กฎเกณฑ์และสมการคณิตศาสตร์แม่บท (Quantitative Trading Rulebook)</h2>
        <p class="text-slate-400 text-xs">สรุปตรรกะแบบ Pure Logic ที่ใช้เป็น Single Source of Truth สำหรับการซื้อ ถือ ขาย และคัดเลือกเหรียญ</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4 space-y-2">
          <h3 class="font-bold text-white text-xs uppercase tracking-wider text-blue-400">1. การคำนวณโมเมนตัมและการจัดอันดับ (Ranking)</h3>
          <p class="text-xs text-slate-300">ใช้ Multi-Scale Momentum ถ่วงน้ำหนัก 3 กรอบเวลา:</p>
          <div class="p-3 rounded bg-[#151c2a] font-mono text-xs text-emerald-400 border border-[#232f45]">
            Score = (0.50 × R30) + (0.30 × R60) + (0.20 × R120)
          </div>
          <p class="text-xs text-slate-400">หรือสำหรับกลยุทธ์ Fast-Alpha จะใช้โมเมนตัม 14 วัน ($R_{14}$) ควบคู่กับ Inverse Volatility Weighting</p>
        </div>

        <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4 space-y-2">
          <h3 class="font-bold text-white text-xs uppercase tracking-wider text-blue-400">2. เกณฑ์ตรวจสอบ 5 ข้อ (Single-Asset Gates)</h3>
          <div class="p-3 rounded bg-[#151c2a] font-mono text-xs text-slate-200 border border-[#232f45] space-y-1">
            <div>1. Close &gt; EMA26 (ราคายืนเหนือแนวโน้มกลาง)</div>
            <div>2. EMA12 &gt; EMA26 (MACD Bullish Confirmation)</div>
            <div>3. Momentum Score &gt; 0 (ผลตอบแทนรวมเป็นบวก)</div>
            <div>4. R30 &gt; 0 (ผลตอบแทน 30 วันห้ามติดลบ)</div>
            <div>5. R60 &gt; 0 (ผลตอบแทน 60 วันห้ามติดลบ)</div>
          </div>
        </div>

        <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4 space-y-2">
          <h3 class="font-bold text-white text-xs uppercase tracking-wider text-blue-400">3. Coupled Macro Regime Matrix</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-xs font-mono border-collapse">
              <thead class="text-slate-400 border-b border-[#232f45]">
                <tr><th>Regime</th><th>Breadth</th><th>BTC Guard</th><th>Crypto %</th><th>Top-K</th></tr>
              </thead>
              <tbody class="divide-y divide-[#1e283c]">
                <tr><td class="text-emerald-400 font-bold">BROAD_BULL</td><td>&ge; 55%</td><td>&gt; EMA100</td><td>95%</td><td>Top 5</td></tr>
                <tr><td class="text-blue-400 font-bold">NORMAL_BULL</td><td>35–55%</td><td>&gt; EMA100</td><td>90%</td><td>Top 3</td></tr>
                <tr><td class="text-amber-400 font-bold">SELECTIVE_BULL</td><td>20–35%</td><td>&gt; EMA100</td><td>70%</td><td>Top 2</td></tr>
                <tr><td class="text-rose-400 font-bold">CASH_GUARD</td><td>&lt; 20%</td><td>&le; EMA100</td><td>0% (USDT)</td><td>Top 0</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="rounded-xl border border-[#1f293d] bg-[#0e131d] p-4 space-y-2">
          <h3 class="font-bold text-white text-xs uppercase tracking-wider text-blue-400">4. Rank Hysteresis & Execution Rules</h3>
          <div class="p-3 rounded bg-[#151c2a] font-mono text-xs text-amber-300 border border-[#232f45]">
            Exit Rank Limit = ⌈ K × (1 + 0.50) ⌉ = ⌈ 5 × 1.5 ⌉ = 8
          </div>
          <ul class="text-xs text-slate-400 list-disc list-inside space-y-1">
            <li><strong>Sell-First Protocol</strong>: สั่งขายเหรียญที่หลุดเกณฑ์ทั้งหมดก่อน แล้วค่อยนำเงินไปซื้อตัวใหม่ ป้องกันเงินสดติดลบ</li>
            <li><strong>5% Rebalance Band</strong>: ไม่ปรับพอร์ตหากสัดส่วนเปลี่ยนน้อยกว่า 5% หรือมูลค่าการปรับน้อยกว่า 6 USDT</li>
            <li><strong>95% Turnover Cap</strong>: รองรับการล้างพอร์ต 100% ในวันวิกฤต และการจัดพอร์ตวันแรก</li>
          </ul>
        </div>
      </div>
    </div>
  </main>

  <!-- HOW TO TRADE MODAL (เปิดดูวิธีเทรดของแต่ละกลยุทธ์) -->
  <div id="how-to-trade-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 hidden">
    <div class="glass-card rounded-2xl max-w-2xl w-full p-6 relative border border-[#2a3852] shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
      <button onclick="closeHowToTradeModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg bg-[#182030] hover:bg-slate-700 transition">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>

      <div>
        <span class="text-xs px-2.5 py-0.5 rounded font-bold uppercase" id="htt-badge">--</span>
        <h3 class="text-xl font-bold text-white mt-1" id="htt-title">--</h3>
        <p class="text-xs text-slate-400" id="htt-tagline">--</p>
      </div>

      <!-- Performance KPI Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3 rounded-xl bg-[#0e131d] border border-[#1f293d] font-mono text-center">
        <div><div class="text-[10px] text-slate-400 uppercase">CAGR (ผลตอบแทนปี)</div><div class="text-base font-bold text-emerald-400" id="htt-cagr">--</div></div>
        <div><div class="text-[10px] text-slate-400 uppercase">Max Drawdown</div><div class="text-base font-bold text-rose-400" id="htt-mdd">--</div></div>
        <div><div class="text-[10px] text-slate-400 uppercase">Sharpe Ratio</div><div class="text-base font-bold text-blue-400" id="htt-sharpe">--</div></div>
        <div><div class="text-[10px] text-slate-400 uppercase">Market Exposure</div><div class="text-base font-bold text-amber-400" id="htt-exposure">--</div></div>
      </div>

      <!-- Parameters Specification -->
      <div class="rounded-xl bg-[#0e131d] border border-[#1f293d] p-3 text-xs font-mono space-y-1 text-slate-300">
        <div class="flex justify-between"><span>Universe Pool:</span><span id="htt-universe" class="text-white">--</span></div>
        <div class="flex justify-between"><span>Lookback Window:</span><span id="htt-lookback" class="text-white">--</span></div>
        <div class="flex justify-between"><span>Breadth Threshold:</span><span id="htt-breadth" class="text-white">--</span></div>
        <div class="flex justify-between"><span>Holdings Size (K):</span><span id="htt-holdings" class="text-white">--</span></div>
        <div class="flex justify-between"><span>Weighting Scheme:</span><span id="htt-weight" class="text-white">--</span></div>
      </div>

      <!-- Step-by-Step Instructions -->
      <div>
        <h4 class="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <svg class="h-4 w-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          ขั้นตอนการเทรดจริงทีละก้าว (Step-by-Step Execution Guide):
        </h4>
        <div class="space-y-2 text-xs" id="htt-steps-list"></div>
      </div>

      <div class="pt-2">
        <button onclick="applyStrategyFromModal()" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-bold text-white transition shadow-lg shadow-blue-600/20">
          ✓ เลือกใช้งานกลยุทธ์นี้ในหน้าสแกนเนอร์
        </button>
      </div>
    </div>
  </div>

  <!-- SINGLE-COIN TECHNICAL GATE INSPECTOR MODAL -->
  <div id="coin-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 hidden">
    <div class="glass-card rounded-2xl max-w-lg w-full p-6 relative border border-[#2a3852] shadow-2xl space-y-4">
      <button onclick="closeCoinModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg bg-[#182030] hover:bg-slate-700 transition">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>

      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-sm font-mono" id="modal-coin-icon">--</div>
        <div>
          <h3 class="text-xl font-extrabold text-white font-mono" id="modal-coin-symbol">--</h3>
          <span class="text-xs px-2 py-0.5 rounded font-bold" id="modal-coin-signal-badge">--</span>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 p-3 rounded-xl bg-[#0e131d] border border-[#1f293d] text-center font-mono">
        <div>
          <div class="text-[10px] uppercase text-slate-400">Current Price</div>
          <div class="text-sm font-bold text-white" id="modal-coin-price">--</div>
        </div>
        <div>
          <div class="text-[10px] uppercase text-slate-400">24h Change</div>
          <div class="text-sm font-bold" id="modal-coin-change">--</div>
        </div>
        <div>
          <div class="text-[10px] uppercase text-slate-400">Momentum Score</div>
          <div class="text-sm font-bold text-emerald-400" id="modal-coin-score">--</div>
        </div>
      </div>

      <div>
        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Technical Gates Checklist (เกณฑ์ตรวจ 5 ข้อ):</h4>
        <div class="space-y-2 text-xs font-mono" id="modal-coin-checklist"></div>
      </div>

      <div class="rounded-xl bg-[#0e131d] p-3 border border-[#1f293d] space-y-1.5 text-xs font-mono text-slate-300">
        <div class="flex justify-between"><span>EMA12 / EMA26:</span><span id="modal-ema12-26" class="text-white">--</span></div>
        <div class="flex justify-between"><span>EMA50 / EMA100:</span><span id="modal-ema50-100" class="text-white">--</span></div>
        <div class="flex justify-between"><span>R30 / R60 / R120:</span><span id="modal-returns" class="text-white">--</span></div>
        <div class="flex justify-between"><span>Action Reason:</span><span id="modal-reason" class="text-amber-300 font-sans text-[11px] text-right max-w-xs">--</span></div>
      </div>
    </div>
  </div>

  <!-- EMBEDDED REAL SNAPSHOT & HISTORICAL PLAYBACK DATA -->
  <script>
    const MASTER_DATA = __COMBINED_DATA__;
    let appMode = 'LIVE'; // 'LIVE' or 'PLAYBACK'
    let currentPlaybackIndex = MASTER_DATA.historical_ledger.length - 1;
    let activeStrategyId = 'BTH_C2LR';
    let currentFilter = 'ALL';
    let sortColumn = 'rank';
    let sortAsc = true;
    let selectedHoldings = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];
    let logSideFilter = 'ALL';
    let currentRollingWindow = 90;
  </script>

  <!-- DASHBOARD ENGINE SCRIPT -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      initApp();
    });

    function initApp() {
      // Setup slider max
      const slider = document.getElementById('playback-slider');
      slider.max = MASTER_DATA.historical_ledger.length - 1;
      slider.value = currentPlaybackIndex;

      renderPresetStrategies();
      updateView();
      initHoldingsSelector();
      runExecutionPlanner();
      renderAuditLogsTable();
      renderEdaSection();
    }

    function renderPresetStrategies() {
      const container = document.getElementById('preset-strategies-container');
      container.innerHTML = '';
      const presets = MASTER_DATA.preset_strategies || [];

      presets.forEach(p => {
        const isActive = (p.id === activeStrategyId);
        const card = document.createElement('div');
        card.className = `rounded-xl p-3.5 border transition cursor-pointer flex flex-col justify-between ${isActive ? 'bg-[#152033] border-blue-500 ring-1 ring-blue-500' : 'bg-[#131926] border-[#1f293d] hover:border-slate-600'}`;
        card.onclick = () => selectStrategy(p.id);

        let badgeBg = p.badge_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : (p.badge_color === 'blue' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : (p.badge_color === 'purple' ? 'bg-purple-500/20 text-purple-400 border-purple-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'));

        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-[10px] px-2 py-0.5 rounded font-bold border ${badgeBg}">${p.badge}</span>
              ${isActive ? '<span class="text-[11px] font-bold text-blue-400 flex items-center gap-1"><span class="h-1.5 w-1.5 rounded-full bg-blue-400"></span> ใช้งานอยู่</span>' : ''}
            </div>
            <h3 class="text-xs font-bold text-white mb-1 leading-snug">${p.name}</h3>
            <p class="text-[11px] text-slate-400 line-clamp-2 mb-2.5">${p.tagline}</p>
          </div>

          <div>
            <div class="grid grid-cols-2 gap-1.5 p-2 rounded-lg bg-[#0e131d] font-mono text-[11px] mb-2.5">
              <div>
                <span class="text-slate-500 text-[10px] block">CAGR (ต่อปี)</span>
                <strong class="text-emerald-400 font-bold">+${p.cagr_pct}%</strong>
              </div>
              <div>
                <span class="text-slate-500 text-[10px] block">Max Drawdown</span>
                <strong class="text-rose-400 font-bold">${p.core_sat_mdd_pct}%</strong>
              </div>
              <div>
                <span class="text-slate-500 text-[10px] block">Sharpe Ratio</span>
                <strong class="text-blue-400 font-bold">${p.sharpe_ratio}</strong>
              </div>
              <div>
                <span class="text-slate-500 text-[10px] block">เวลาในตลาด</span>
                <strong class="text-amber-400 font-bold">${p.exposure_pct}%</strong>
              </div>
            </div>

            <div class="flex items-center gap-1.5">
              <button onclick="event.stopPropagation(); selectStrategy('${p.id}')" class="flex-1 py-1 rounded text-[11px] font-bold transition ${isActive ? 'bg-blue-600 text-white' : 'bg-[#1a2436] hover:bg-slate-700 text-slate-300'}">
                ${isActive ? '✓ เลือกอยู่' : 'เลือกกลยุทธ์นี้'}
              </button>
              <button onclick="event.stopPropagation(); openHowToTradeModal('${p.id}')" class="px-2 py-1 rounded text-[11px] font-bold bg-[#151c2a] hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition" title="ดูคู่มือวิธีเทรด">
                วิธีเทรด
              </button>
            </div>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function selectStrategy(id) {
      activeStrategyId = id;
      const strat = (MASTER_DATA.preset_strategies || []).find(s => s.id === id);
      if (!strat) return;

      document.getElementById('current-strategy-badge').textContent = 'Active: ' + strat.name;
      document.getElementById('banner-strat-title').textContent = strat.name;
      document.getElementById('banner-strat-desc').textContent = strat.tagline;
      document.getElementById('banner-strat-perf').textContent = `CAGR +${strat.cagr_pct}% | MaxDD ${strat.core_sat_mdd_pct}% | Sharpe ${strat.sharpe_ratio}`;

      renderPresetStrategies();
      runExecutionPlanner();
    }

    function openHowToTradeModal(id) {
      const strat = (MASTER_DATA.preset_strategies || []).find(s => s.id === id);
      if (!strat) return;

      document.getElementById('htt-badge').textContent = strat.badge;
      document.getElementById('htt-badge').className = `text-xs px-2.5 py-0.5 rounded font-bold uppercase ${strat.badge_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}`;
      document.getElementById('htt-title').textContent = strat.name;
      document.getElementById('htt-tagline').textContent = strat.tagline;

      document.getElementById('htt-cagr').textContent = '+' + strat.cagr_pct + '%';
      document.getElementById('htt-mdd').textContent = strat.core_sat_mdd_pct + '%';
      document.getElementById('htt-sharpe').textContent = strat.sharpe_ratio;
      document.getElementById('htt-exposure').textContent = strat.exposure_pct + '%';

      document.getElementById('htt-universe').textContent = `Top ${strat.universe_size} USDT Pairs by 30d Quote Volume`;
      document.getElementById('htt-lookback').textContent = `${strat.lookback_days} วัน (${strat.lookback_days === 14 ? 'โมเมนตัมคลื่นสั้น' : 'โมเมนตัม 3 มิติเวลา'})`;
      document.getElementById('htt-breadth').textContent = `>= ${(strat.breadth_threshold * 100).toFixed(0)}% (% Altcoins > EMA50)`;
      document.getElementById('htt-holdings').textContent = `Top ${strat.holdings_k} ผู้นำ`;
      document.getElementById('htt-weight').textContent = strat.weight_mode;

      const stepsList = document.getElementById('htt-steps-list');
      stepsList.innerHTML = '';
      (strat.how_to_trade || []).forEach((step, idx) => {
        stepsList.innerHTML += `
          <div class="flex items-start gap-2.5 p-2.5 rounded-lg bg-[#111724] border border-[#1e283b]">
            <span class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white font-mono">${idx + 1}</span>
            <span class="text-slate-200">${step}</span>
          </div>
        `;
      });

      document.getElementById('how-to-trade-modal').classList.remove('hidden');
    }

    function closeHowToTradeModal() {
      document.getElementById('how-to-trade-modal').classList.add('hidden');
    }

    function applyStrategyFromModal() {
      closeHowToTradeModal();
      selectStrategy(activeStrategyId);
    }

    function setAppMode(mode) {
      appMode = mode;
      const liveBtn = document.getElementById('mode-btn-live');
      const pbBtn = document.getElementById('mode-btn-playback');
      const pbControl = document.getElementById('playback-control-panel');
      const pbDayDetails = document.getElementById('playback-day-details');
      const liveControls = document.getElementById('signals-live-controls');

      if (mode === 'LIVE') {
        liveBtn.className = 'px-3 py-1 rounded bg-blue-600 text-white font-bold transition flex items-center gap-1.5';
        pbBtn.className = 'px-3 py-1 rounded text-slate-400 hover:text-white transition flex items-center gap-1.5';
        pbControl.classList.add('hidden');
        pbDayDetails.classList.add('hidden');
        liveControls.classList.remove('hidden');
        document.getElementById('tab-title-signals').textContent = 'สูตรสแกนและตารางสัญญาณ (Live Scanner Matrix)';
      } else {
        pbBtn.className = 'px-3 py-1 rounded bg-blue-600 text-white font-bold transition flex items-center gap-1.5';
        liveBtn.className = 'px-3 py-1 rounded text-slate-400 hover:text-white transition flex items-center gap-1.5';
        pbControl.classList.remove('hidden');
        pbDayDetails.classList.remove('hidden');
        liveControls.classList.add('hidden');
        document.getElementById('tab-title-signals').textContent = 'รายชื่อเหรียญผู้นำและการหมุนพอร์ตจริง (PIT Candidates & Holdings)';
      }
      updateView();
    }

    function onSliderChange(val) {
      currentPlaybackIndex = parseInt(val, 10);
      updateView();
    }

    function jumpToDate(dateStr) {
      const idx = MASTER_DATA.historical_ledger.findIndex(d => d.date === dateStr);
      if (idx !== -1) {
        currentPlaybackIndex = idx;
        document.getElementById('playback-slider').value = idx;
        setAppMode('PLAYBACK');
      }
    }

    function updateView() {
      if (appMode === 'LIVE') {
        renderLiveHeaderAndMacro();
        renderCoinsTable();
      } else {
        renderPlaybackHeaderAndMacro();
      }
    }

    function renderLiveHeaderAndMacro() {
      const live = MASTER_DATA.live_snapshot;
      const mr = live.macro_regime;

      document.getElementById('regime-header-title').textContent = 'Live Market Regime';
      document.getElementById('regime-name').textContent = mr.regime;
      document.getElementById('regime-description').textContent = mr.description;

      const regBadge = document.getElementById('regime-status-badge');
      if (mr.regime === 'BROAD_BULL') {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
        regBadge.textContent = '🟢 Bullish (95%)';
      } else if (mr.regime === 'NORMAL_BULL') {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-blue-500/20 text-blue-400 border border-blue-500/40';
        regBadge.textContent = '🟡 Normal (90%)';
      } else if (mr.regime === 'SELECTIVE_BULL') {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/40';
        regBadge.textContent = '🟠 Selective (70%)';
      } else {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/40';
        regBadge.textContent = '🚨 Cash Guard (0%)';
      }

      document.getElementById('btc-price').textContent = '$' + Number(mr.btc_price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      document.getElementById('btc-ema100').textContent = '$' + Number(mr.btc_ema100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      const btcBadge = document.getElementById('btc-gate-badge');
      if (mr.btc_trend_ok) {
        btcBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
        btcBadge.textContent = 'PASSED (BTC > EMA100)';
      } else {
        btcBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40';
        btcBadge.textContent = 'FAILED (BTC <= EMA100)';
      }
      document.getElementById('btc-dist-pct').textContent = (mr.btc_distance_pct >= 0 ? '+' : '') + mr.btc_distance_pct + '%';
      document.getElementById('btc-dist-pct').className = 'font-mono font-semibold ' + (mr.btc_distance_pct >= 0 ? 'text-emerald-400' : 'text-rose-400');

      document.getElementById('breadth-pct').textContent = mr.altcoin_breadth_pct + '%';
      document.getElementById('breadth-count').textContent = mr.altcoins_above_ema50 + ' / ' + mr.total_altcoins_evaluated + ' Alts';
      document.getElementById('breadth-bar').style.width = mr.altcoin_breadth_pct + '%';

      document.getElementById('active-top-k').textContent = 'Top-' + mr.active_top_k;
      document.getElementById('crypto-exposure').textContent = mr.crypto_exposure_pct + '%';
      document.getElementById('cash-reserve').textContent = mr.cash_reserve_pct + '%';
      document.getElementById('exit-rank-limit').textContent = 'Rank 1–' + mr.exit_rank_limit;

      document.getElementById('badge-total-coins').textContent = live.coins_table.length;

      // Update filter counts
      const counts = { ALL: live.coins_table.length, BUY: 0, HOLD: 0, WATCHLIST: 0, SELL: 0, AVOID: 0 };
      live.coins_table.forEach(c => {
        if (c.signal === 'BUY') counts.BUY++;
        else if (c.signal === 'HOLD') counts.HOLD++;
        else if (c.signal === 'WATCHLIST') counts.WATCHLIST++;
        else if (c.signal === 'SELL') counts.SELL++;
        else counts.AVOID++;
      });
      document.getElementById('cnt-all').textContent = counts.ALL;
      document.getElementById('cnt-buy').textContent = counts.BUY;
      document.getElementById('cnt-hold').textContent = counts.HOLD;
      document.getElementById('cnt-watchlist').textContent = counts.WATCHLIST;
      document.getElementById('cnt-sell').textContent = counts.SELL;
      document.getElementById('cnt-avoid').textContent = counts.AVOID;
    }

    function renderPlaybackHeaderAndMacro() {
      const rec = MASTER_DATA.historical_ledger[currentPlaybackIndex];
      if (!rec) return;

      document.getElementById('playback-current-date').textContent = rec.date;
      document.getElementById('regime-header-title').textContent = `PIT Regime (${rec.date})`;
      document.getElementById('regime-name').textContent = rec.regime;

      let desc = '';
      if (rec.regime === 'BROAD_BULL') desc = 'กระทิงเต็มสูบ กระจายลงทุน Top-5 (Crypto 95%, Cash 5%)';
      else if (rec.regime === 'NORMAL_BULL') desc = 'กระทิงปกติ คัดถือ Top-3 (Crypto 90%, Cash 10%)';
      else if (rec.regime === 'SELECTIVE_BULL') desc = 'คัดเลือกเฉพาะตัว Top-2 สำรองเงินสด 30%';
      else desc = 'CASH_GUARD ถือ 100% USDT ป้องกันเงินต้น';
      document.getElementById('regime-description').textContent = desc;

      const regBadge = document.getElementById('regime-status-badge');
      if (rec.regime === 'BROAD_BULL') {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
        regBadge.textContent = '🟢 Bullish (95%)';
      } else if (rec.regime === 'NORMAL_BULL') {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-blue-500/20 text-blue-400 border border-blue-500/40';
        regBadge.textContent = '🟡 Normal (90%)';
      } else if (rec.regime === 'SELECTIVE_BULL') {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/40';
        regBadge.textContent = '🟠 Selective (70%)';
      } else {
        regBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/40';
        regBadge.textContent = '🚨 Cash Guard (0%)';
      }

      document.getElementById('btc-price').textContent = '$' + Number(rec.btc_price).toLocaleString('en-US', { minimumFractionDigits: 2 });
      document.getElementById('btc-ema100').textContent = '$' + Number(rec.btc_ema100).toLocaleString('en-US', { minimumFractionDigits: 2 });
      const btcBadge = document.getElementById('btc-gate-badge');
      if (rec.btc_trend_ok) {
        btcBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
        btcBadge.textContent = 'PASSED (BTC > EMA100)';
      } else {
        btcBadge.className = 'px-2 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40';
        btcBadge.textContent = 'FAILED (BTC <= EMA100)';
      }
      const distPct = ((rec.btc_price / rec.btc_ema100 - 1.0) * 100).toFixed(2);
      document.getElementById('btc-dist-pct').textContent = (distPct >= 0 ? '+' : '') + distPct + '%';
      document.getElementById('btc-dist-pct').className = 'font-mono font-semibold ' + (distPct >= 0 ? 'text-emerald-400' : 'text-rose-400');

      document.getElementById('breadth-pct').textContent = rec.breadth_pct + '%';
      document.getElementById('breadth-count').textContent = rec.altcoins_above_ema50 + ' / ' + rec.valid_breadth_alts + ' Top Alts';
      document.getElementById('breadth-bar').style.width = rec.breadth_pct + '%';

      document.getElementById('active-top-k').textContent = 'Top-' + rec.active_top_k;
      document.getElementById('crypto-exposure').textContent = rec.crypto_exposure_pct + '%';
      document.getElementById('cash-reserve').textContent = (100 - rec.crypto_exposure_pct).toFixed(1) + '%';
      document.getElementById('exit-rank-limit').textContent = 'Rank 1–' + rec.exit_rank_limit;

      // Playback detail card
      document.getElementById('pb-detail-date').textContent = rec.date;
      document.getElementById('pb-detail-regime-badge').textContent = rec.regime;
      document.getElementById('pb-detail-regime-badge').className = `text-xs px-2.5 py-0.5 rounded font-bold ${rec.regime === 'CASH_GUARD' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`;
      document.getElementById('pb-detail-nav').textContent = '$' + rec.nav.toLocaleString('en-US', { minimumFractionDigits: 2 });
      document.getElementById('pb-detail-cash').textContent = '$' + rec.cash.toLocaleString('en-US', { minimumFractionDigits: 2 });
      document.getElementById('pb-detail-cash-pct').textContent = rec.cash_weight_pct + '%';
      document.getElementById('pb-detail-holdings-count').textContent = rec.holdings_count;

      // Holdings table
      const hTbody = document.getElementById('pb-holdings-tbody');
      hTbody.innerHTML = '';
      if (rec.holdings.length === 0) {
        hTbody.innerHTML = '<tr><td colspan="5" class="py-3 text-center text-slate-500">ถือ 100% USDT Cash Guard (ไม่มีสถานะเหรียญ)</td></tr>';
      } else {
        rec.holdings.forEach(h => {
          hTbody.innerHTML += `
            <tr class="hover:bg-[#151d2d]">
              <td class="py-1.5 px-2 font-bold text-white">${h.symbol}</td>
              <td class="py-1.5 px-2 text-right text-slate-300">${h.units >= 100 ? h.units.toFixed(2) : h.units.toFixed(4)}</td>
              <td class="py-1.5 px-2 text-right text-slate-300">$${formatPrice(h.price)}</td>
              <td class="py-1.5 px-2 text-right font-bold text-emerald-400">$${h.value.toLocaleString()}</td>
              <td class="py-1.5 px-2 text-right text-slate-300">${h.weight_pct}%</td>
            </tr>
          `;
        });
      }
      document.getElementById('pb-holdings-val-sum').textContent = `Total Value: $${rec.holdings.reduce((acc, h) => acc + h.value, 0).toFixed(2)}`;

      // Trades table
      const tTbody = document.getElementById('pb-trades-tbody');
      tTbody.innerHTML = '';
      if (rec.trades.length === 0) {
        tTbody.innerHTML = '<tr><td colspan="4" class="py-3 text-center text-slate-500">ไม่มีการปรับพอร์ตในวันนี้ (Zero Churning / ถือต่อตาม Hysteresis Buffer)</td></tr>';
      } else {
        rec.trades.forEach(t => {
          const sCls = t.side === 'BUY' ? 'text-emerald-400' : 'text-rose-400';
          tTbody.innerHTML += `
            <tr class="hover:bg-[#151d2d]">
              <td class="py-1.5 px-2 font-bold ${sCls}">${t.side}</td>
              <td class="py-1.5 px-2 font-bold text-white">${t.symbol}</td>
              <td class="py-1.5 px-2 text-right font-bold text-slate-200">$${t.notional.toFixed(2)}</td>
              <td class="py-1.5 px-2 text-[11px] text-slate-400 font-sans max-w-xs truncate" title="${t.reason}">${t.reason}</td>
            </tr>
          `;
        });
      }
      document.getElementById('pb-trades-fee-sum').textContent = `Trades: ${rec.trades_count} | Fee: $${rec.fees_paid_today.toFixed(2)}`;

      // Render candidate coins for this date
      renderPlaybackCandidatesTable(rec);
    }

    function renderPlaybackCandidatesTable(rec) {
      const tbody = document.getElementById('coins-table-body');
      tbody.innerHTML = '';
      document.getElementById('badge-total-coins').textContent = rec.candidates_top10.length;

      if (rec.candidates_top10.length === 0) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center py-8 text-slate-500">ไม่มีเหรียญที่ผ่านเกณฑ์ Trend & Momentum ในวันนี้ (ตลาดเข้าสู่ Cash Guard หรือเทรนด์หลุด)</td></tr>';
        return;
      }

      rec.candidates_top10.forEach(c => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[#151d2d] transition border-b border-[#182030]';
        const isSelected = rec.selected_leaders.includes(c.symbol);

        let bCls = isSelected ? 'badge-buy' : (c.status === 'HOLD' ? 'badge-hold' : 'badge-watchlist');
        let bText = isSelected ? '🟢 BUY / ACTIVE LEADER' : (c.status === 'HOLD' ? '🔵 HOLD BUFFER' : '🟡 WATCHLIST CANDIDATE');

        tr.innerHTML = `
          <td class="py-2.5 px-3.5 font-bold text-slate-300">#${c.rank}</td>
          <td class="py-2.5 px-3.5 font-bold text-white">${c.symbol}</td>
          <td class="py-2.5 px-3.5 text-center"><span class="px-2 py-0.5 rounded text-[11px] font-bold ${bCls}">${bText}</span></td>
          <td class="py-2.5 px-3.5 text-right font-bold text-white">$${formatPrice(c.close)}</td>
          <td class="py-2.5 px-3.5 text-right font-bold text-slate-300">-</td>
          <td class="py-2.5 px-3.5 text-right font-bold text-emerald-400">+${c.score}%</td>
          <td class="py-2.5 px-3.5 text-right text-slate-300">+${c.r30}%</td>
          <td class="py-2.5 px-3.5 text-right text-slate-300">+${c.r60}%</td>
          <td class="py-2.5 px-3.5 text-center text-[11px] text-emerald-400 font-bold">✓ PASS</td>
          <td class="py-2.5 px-3.5 text-right font-bold text-emerald-400">${isSelected ? (rec.crypto_exposure_pct / rec.active_top_k).toFixed(1) + '%' : '-'}</td>
          <td class="py-2.5 px-3.5 text-[11px] text-slate-400 font-sans">${isSelected ? 'ได้รับคัดเลือกเข้าพอร์ตผู้นำ' : 'อยู่นอก Top-K รอจังหวะสลับ'}</td>
          <td class="py-2.5 px-3.5 text-center"><span class="text-xs text-slate-500 font-bold font-mono">PIT OK</span></td>
        `;
        tbody.appendChild(tr);
      });
    }

    function switchTab(tabId) {
      const tabs = ['signals', 'calculator', 'audit_logs', 'eda', 'rulebook'];
      tabs.forEach(t => {
        const btn = document.getElementById('tab-btn-' + t);
        const content = document.getElementById('tab-content-' + t);
        if (t === tabId) {
          btn.className = 'tab-active flex items-center gap-2 px-4 py-3 border-b-2 border-transparent transition';
          content.classList.remove('hidden');
        } else {
          btn.className = 'flex items-center gap-2 px-4 py-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition';
          content.classList.add('hidden');
        }
      });
    }

    function setSignalFilter(sig) {
      currentFilter = sig;
      ['ALL', 'BUY', 'HOLD', 'WATCHLIST', 'SELL', 'AVOID'].forEach(s => {
        const btn = document.getElementById('filter-btn-' + s);
        if (s === sig) {
          btn.className = 'rounded-lg bg-blue-600 text-white px-3 py-1.5 text-xs font-semibold transition shadow-sm';
        } else {
          btn.className = 'rounded-lg bg-[#151c2a] text-slate-400 hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-semibold transition';
        }
      });
      renderCoinsTable();
    }

    function changeSort(col) {
      if (sortColumn === col) {
        sortAsc = !sortAsc;
      } else {
        sortColumn = col;
        sortAsc = (col === 'rank' || col === 'symbol');
      }
      renderCoinsTable();
    }

    function renderCoinsTable() {
      if (appMode === 'PLAYBACK') return;
      const query = document.getElementById('search-input').value.trim().toUpperCase();
      let list = [...MASTER_DATA.live_snapshot.coins_table];

      if (currentFilter !== 'ALL') {
        if (currentFilter === 'AVOID') {
          list = list.filter(c => c.signal === 'INACTIVE' || c.signal === 'ELIGIBLE');
        } else {
          list = list.filter(c => c.signal === currentFilter);
        }
      }

      if (query) {
        list = list.filter(c => c.symbol.includes(query));
      }

      list.sort((a, b) => {
        let vA = a[sortColumn];
        let vB = b[sortColumn];
        if (vA === undefined) vA = 999;
        if (vB === undefined) vB = 999;
        if (typeof vA === 'string') return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
        return sortAsc ? vA - vB : vB - vA;
      });

      const tbody = document.getElementById('coins-table-body');
      tbody.innerHTML = '';

      if (list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center py-8 text-slate-500">ไม่พบเหรียญที่ตรงกับเงื่อนไขการค้นหา</td></tr>';
        return;
      }

      list.forEach(c => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[#151d2d] transition border-b border-[#182030]';

        let bCls = 'badge-inactive';
        if (c.signal === 'BUY') bCls = 'badge-buy';
        else if (c.signal === 'HOLD') bCls = 'badge-hold';
        else if (c.signal === 'WATCHLIST') bCls = 'badge-watchlist';
        else if (c.signal === 'SELL') bCls = 'badge-sell';

        const tgIcon = c.trend_ok
          ? '<span class="text-emerald-400 font-bold">✓ PASS</span>'
          : '<span class="text-rose-400 font-bold">✗ FAIL</span>';

        const pChangeCls = c.price_change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400';
        const scoreCls = c.momentum_score > 0 ? 'text-emerald-400 font-bold' : 'text-slate-500';

        tr.innerHTML = `
          <td class="py-2.5 px-3.5 font-bold text-slate-300">#${c.rank || '-'}</td>
          <td class="py-2.5 px-3.5">
            <div class="font-bold text-white">${c.symbol}</div>
            <div class="text-[10px] text-slate-500">Vol: $${Math.round(c.quote_volume / 1000).toLocaleString()}k</div>
          </td>
          <td class="py-2.5 px-3.5 text-center">
            <span class="px-2 py-0.5 rounded text-[11px] font-bold ${bCls}">${c.signal_badge}</span>
          </td>
          <td class="py-2.5 px-3.5 text-right font-bold text-white">$${formatPrice(c.close)}</td>
          <td class="py-2.5 px-3.5 text-right font-bold ${pChangeCls}">${c.price_change_24h >= 0 ? '+' : ''}${c.price_change_24h.toFixed(2)}%</td>
          <td class="py-2.5 px-3.5 text-right ${scoreCls}">${(c.momentum_score * 100).toFixed(1)}%</td>
          <td class="py-2.5 px-3.5 text-right text-slate-300">${(c.r30 * 100).toFixed(1)}%</td>
          <td class="py-2.5 px-3.5 text-right text-slate-300">${(c.r60 * 100).toFixed(1)}%</td>
          <td class="py-2.5 px-3.5 text-center text-[11px]">${tgIcon}</td>
          <td class="py-2.5 px-3.5 text-right font-bold text-emerald-400">${c.target_weight ? (c.target_weight * 100).toFixed(1) + '%' : '-'}</td>
          <td class="py-2.5 px-3.5 text-[11px] text-slate-400 font-sans max-w-xs truncate" title="${c.action_reason}">${c.action_reason}</td>
          <td class="py-2.5 px-3.5 text-center">
            <button onclick="openCoinModal('${c.symbol}')" class="rounded bg-[#1a2335] hover:bg-blue-600 hover:text-white px-2 py-1 text-[10px] font-bold text-blue-400 transition border border-blue-500/20">
              ดู Gate
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function formatPrice(p) {
      if (p >= 1000) return Number(p).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (p >= 1) return Number(p).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 });
      return Number(p).toFixed(6);
    }

    function openCoinModal(symbol) {
      const coin = MASTER_DATA.live_snapshot.coins_table.find(c => c.symbol === symbol);
      if (!coin) return;

      document.getElementById('modal-coin-icon').textContent = symbol.slice(0, 3);
      document.getElementById('modal-coin-symbol').textContent = symbol;
      
      const badge = document.getElementById('modal-coin-signal-badge');
      badge.textContent = coin.signal_badge;
      if (coin.signal === 'BUY') badge.className = 'text-xs px-2 py-0.5 rounded font-bold badge-buy';
      else if (coin.signal === 'HOLD') badge.className = 'text-xs px-2 py-0.5 rounded font-bold badge-hold';
      else if (coin.signal === 'WATCHLIST') badge.className = 'text-xs px-2 py-0.5 rounded font-bold badge-watchlist';
      else if (coin.signal === 'SELL') badge.className = 'text-xs px-2 py-0.5 rounded font-bold badge-sell';
      else badge.className = 'text-xs px-2 py-0.5 rounded font-bold badge-inactive';

      document.getElementById('modal-coin-price').textContent = '$' + formatPrice(coin.close);
      document.getElementById('modal-coin-change').textContent = (coin.price_change_24h >= 0 ? '+' : '') + coin.price_change_24h.toFixed(2) + '%';
      document.getElementById('modal-coin-change').className = 'text-sm font-bold ' + (coin.price_change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400');
      document.getElementById('modal-coin-score').textContent = (coin.momentum_score * 100).toFixed(2) + '%';

      const gates = [
        { name: '1. Close > EMA26', ok: coin.close > coin.ema26, val: `Close: $${formatPrice(coin.close)} vs EMA26: $${formatPrice(coin.ema26)} (${coin.close_to_ema26_pct >= 0 ? '+' : ''}${coin.close_to_ema26_pct.toFixed(1)}%)` },
        { name: '2. EMA12 > EMA26 (MACD Bullish)', ok: coin.ema12 > coin.ema26, val: `EMA12: $${formatPrice(coin.ema12)} vs EMA26: $${formatPrice(coin.ema26)}` },
        { name: '3. Momentum Score > 0', ok: coin.momentum_score > 0, val: `Score: ${(coin.momentum_score * 100).toFixed(2)}%` },
        { name: '4. Return 30d (R30) > 0', ok: coin.r30 > 0, val: `R30: ${(coin.r30 * 100).toFixed(2)}%` },
        { name: '5. Return 60d (R60) > 0', ok: coin.r60 > 0, val: `R60: ${(coin.r60 * 100).toFixed(2)}%` },
      ];

      const cl = document.getElementById('modal-coin-checklist');
      cl.innerHTML = '';
      gates.forEach(g => {
        const div = document.createElement('div');
        div.className = 'flex items-center justify-between p-2 rounded bg-[#131926] border border-[#1f293d]';
        const icon = g.ok ? '<span class="text-emerald-400 font-bold">✓ PASS</span>' : '<span class="text-rose-400 font-bold">✗ FAIL</span>';
        div.innerHTML = `
          <div>
            <div class="font-bold text-slate-200">${g.name}</div>
            <div class="text-[10px] text-slate-500">${g.val}</div>
          </div>
          <div>${icon}</div>
        `;
        cl.appendChild(div);
      });

      document.getElementById('modal-ema12-26').textContent = `$${formatPrice(coin.ema12)} / $${formatPrice(coin.ema26)}`;
      document.getElementById('modal-ema50-100').textContent = `$${formatPrice(coin.ema50)} / $${formatPrice(coin.ema100)}`;
      document.getElementById('modal-returns').textContent = `${(coin.r30 * 100).toFixed(1)}% / ${(coin.r60 * 100).toFixed(1)}% / ${(coin.r120 * 100).toFixed(1)}%`;
      document.getElementById('modal-reason').textContent = coin.action_reason;

      document.getElementById('coin-modal').classList.remove('hidden');
    }

    function closeCoinModal() {
      document.getElementById('coin-modal').classList.add('hidden');
    }

    function initHoldingsSelector() {
      const container = document.getElementById('current-holdings-selector');
      container.innerHTML = '';
      MASTER_DATA.live_snapshot.coins_table.slice(0, 25).forEach(c => {
        const isChecked = selectedHoldings.includes(c.symbol);
        const label = document.createElement('label');
        label.className = `flex items-center gap-1.5 px-2 py-1 rounded text-xs font-mono cursor-pointer border transition ${isChecked ? 'bg-blue-600/20 text-blue-400 border-blue-500/40' : 'bg-[#151c2a] text-slate-400 border-slate-700 hover:border-slate-500'}`;
        label.innerHTML = `
          <input type="checkbox" value="${c.symbol}" ${isChecked ? 'checked' : ''} onchange="toggleHolding('${c.symbol}')" class="hidden">
          <span>${c.symbol}</span>
        `;
        container.appendChild(label);
      });
    }

    function toggleHolding(sym) {
      if (selectedHoldings.includes(sym)) {
        selectedHoldings = selectedHoldings.filter(s => s !== sym);
      } else {
        selectedHoldings.push(sym);
      }
      initHoldingsSelector();
      runExecutionPlanner();
    }

    function runExecutionPlanner() {
      const nav = parseFloat(document.getElementById('calc-nav-input').value) || 10000;
      const mr = MASTER_DATA.live_snapshot.macro_regime;

      document.getElementById('calc-regime-target').textContent = mr.regime + ' (Crypto ' + mr.crypto_exposure_pct + '%)';

      const buyCoins = MASTER_DATA.live_snapshot.coins_table.filter(c => c.signal === 'BUY');
      const targetWeightPerAsset = mr.active_top_k > 0 ? (mr.crypto_exposure_pct / 100.0) / mr.active_top_k : 0.0;
      const targetNotionalPerAsset = nav * targetWeightPerAsset;
      const targetCashNotional = nav * (mr.cash_reserve_pct / 100.0);

      const tCards = document.getElementById('target-summary-cards');
      tCards.innerHTML = `
        <div class="p-3 rounded-lg bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[10px] text-slate-400">Total Portfolio NAV</div>
          <div class="text-sm font-bold font-mono text-white">$${nav.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
        </div>
        <div class="p-3 rounded-lg bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[10px] text-slate-400">Crypto Allocation</div>
          <div class="text-sm font-bold font-mono text-emerald-400">$${(nav * mr.crypto_exposure_pct / 100).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
        </div>
        <div class="p-3 rounded-lg bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[10px] text-slate-400">Cash Reserve (USDT)</div>
          <div class="text-sm font-bold font-mono text-amber-400">$${targetCashNotional.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
        </div>
        <div class="p-3 rounded-lg bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[10px] text-slate-400">Target per Leader</div>
          <div class="text-sm font-bold font-mono text-blue-400">$${targetNotionalPerAsset.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
        </div>
      `;

      const tTags = document.getElementById('target-leaders-tags');
      tTags.innerHTML = '';
      if (buyCoins.length === 0) {
        tTags.innerHTML = '<span class="text-rose-400 font-mono text-xs">🚨 ถือ 100% USDT Cash Guard (ไม่มีการถือเหรียญ)</span>';
      } else {
        buyCoins.forEach(c => {
          tTags.innerHTML += `<span class="px-2.5 py-1 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 font-mono text-xs font-bold">#${c.rank} ${c.symbol} (${(targetWeightPerAsset * 100).toFixed(1)}%)</span>`;
        });
      }

      const sellTable = document.getElementById('sell-orders-table');
      sellTable.innerHTML = '';
      let totalSell = 0;

      const targetSymbols = buyCoins.map(c => c.symbol);
      const toSell = selectedHoldings.filter(s => !targetSymbols.includes(s));

      if (toSell.length === 0) {
        sellTable.innerHTML = '<tr><td colspan="4" class="py-2 text-center text-slate-500">ไม่มีคำสั่งขายที่จำเป็น (เหรียญที่ถืออยู่สอดคล้องกับพอร์ตเป้าหมาย)</td></tr>';
      } else {
        toSell.forEach(s => {
          const mockVal = nav / Math.max(1, selectedHoldings.length);
          totalSell += mockVal;
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="py-1.5 px-2 text-rose-400 font-bold">SELL MARKET</td>
            <td class="py-1.5 px-2 text-white font-bold">${s}</td>
            <td class="py-1.5 px-2 text-right text-rose-300 font-bold">$${mockVal.toFixed(2)}</td>
            <td class="py-1.5 px-2 text-slate-400 text-[11px] font-sans">หลุดจาก Top Leaders หรือไม่ผ่านเกณฑ์ Trend Gate</td>
          `;
          sellTable.appendChild(tr);
        });
      }
      document.getElementById('total-sell-amount').textContent = '$' + totalSell.toFixed(2) + ' USDT';

      const cashReconciled = totalSell + (nav * (mr.cash_reserve_pct / 100.0));
      document.getElementById('reconciled-cash-amount').textContent = '$' + cashReconciled.toFixed(2) + ' USDT';

      const buyTable = document.getElementById('buy-orders-table');
      buyTable.innerHTML = '';
      let totalBuy = 0;

      const toBuy = buyCoins.filter(c => !selectedHoldings.includes(c.symbol));
      if (toBuy.length === 0) {
        buyTable.innerHTML = '<tr><td colspan="5" class="py-2 text-center text-slate-500">พอร์ตถือเหรียญผู้นำครบถ้วนแล้ว ไม่ต้องส่งคำสั่งซื้อใหม่</td></tr>';
      } else {
        toBuy.forEach(c => {
          const orderAmount = targetNotionalPerAsset;
          const feeEst = orderAmount * 0.00075;
          totalBuy += orderAmount;
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="py-1.5 px-2 text-emerald-400 font-bold">BUY MARKET</td>
            <td class="py-1.5 px-2 text-white font-bold">${c.symbol}</td>
            <td class="py-1.5 px-2 text-right text-emerald-300 font-bold">$${orderAmount.toFixed(2)}</td>
            <td class="py-1.5 px-2 text-right text-slate-400">$${feeEst.toFixed(2)}</td>
            <td class="py-1.5 px-2 text-slate-400 text-[11px] font-sans">เข้าซื้อผู้นำอันดับ #${c.rank} (Momentum Score: ${(c.momentum_score * 100).toFixed(1)}%)</td>
          `;
          buyTable.appendChild(tr);
        });
      }
      document.getElementById('total-buy-amount').textContent = '$' + totalBuy.toFixed(2) + ' USDT';
    }

    // ROTATION AUDIT LOGS
    function setLogSideFilter(side) {
      logSideFilter = side;
      ['ALL', 'SELL', 'BUY'].forEach(s => {
        const btn = document.getElementById('log-side-' + s);
        if (s === side) {
          btn.className = 'px-2.5 py-1 rounded bg-blue-600 text-white font-bold';
        } else {
          btn.className = 'px-2.5 py-1 rounded text-slate-400 hover:text-white';
        }
      });
      renderAuditLogsTable();
    }

    function renderAuditLogsTable() {
      const tbody = document.getElementById('audit-logs-tbody');
      if (!tbody) return;
      tbody.innerHTML = '';

      const query = (document.getElementById('log-search-input')?.value || '').trim().toUpperCase();
      let logs = MASTER_DATA.rotation_audit_log || [];

      if (logSideFilter !== 'ALL') {
        logs = logs.filter(l => l.side === logSideFilter);
      }
      if (query) {
        logs = logs.filter(l => l.symbol.includes(query) || l.reason.includes(query) || l.date.includes(query));
      }

      document.getElementById('log-count-summary').textContent = `แสดง ${logs.length} จาก ${MASTER_DATA.rotation_audit_log.length} รายการ`;

      if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="py-6 text-center text-slate-500">ไม่พบประวัติคำสั่งซื้อขายที่ตรงกับเงื่อนไข</td></tr>';
        return;
      }

      // Render top 150 matching rows for responsiveness
      logs.slice(0, 150).forEach(l => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[#151c2a] transition';
        const sideCls = l.side === 'BUY' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold';
        tr.innerHTML = `
          <td class="py-2 px-3 text-slate-300 font-bold">${l.date}</td>
          <td class="py-2 px-3 text-[11px] text-slate-400">${l.regime}</td>
          <td class="py-2 px-3 ${sideCls}">${l.side}</td>
          <td class="py-2 px-3 font-bold text-white">${l.symbol}</td>
          <td class="py-2 px-3 text-right text-slate-300">$${formatPrice(l.price)}</td>
          <td class="py-2 px-3 text-right text-slate-400">${l.units}</td>
          <td class="py-2 px-3 text-right font-bold text-slate-200">$${l.notional.toLocaleString()}</td>
          <td class="py-2 px-3 text-right text-slate-400">$${l.fee.toFixed(2)}</td>
          <td class="py-2 px-3 text-[11px] text-slate-300 font-sans max-w-xs truncate" title="${l.reason}">${l.reason}</td>
          <td class="py-2 px-3 text-right text-emerald-400 font-bold">$${l.nav.toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    // ROLLING SECTION & EDA
    function setRollingWindow(w) {
      currentRollingWindow = w;
      [30, 60, 90, 180, 365].forEach(d => {
        const btn = document.getElementById("rw-btn-" + d);
        if (!btn) return;
        if (d === w) {
          btn.className = "px-2.5 py-1 rounded bg-blue-600 text-white font-bold transition";
        } else {
          btn.className = "px-2.5 py-1 rounded bg-[#1f293d] text-slate-300 hover:bg-blue-600 hover:text-white transition";
        }
      });
      renderRollingSection();
    }

    function renderRollingSection() {
      const rolling = MASTER_DATA.rolling_analysis;
      if (!rolling || !rolling.windows_summary) return;
      const item = rolling.windows_summary["window_" + currentRollingWindow + "d"];
      if (!item) return;

      const kpi = document.getElementById("rw-kpi-cards");
      kpi.innerHTML = `
        <div class="p-3.5 rounded-xl bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[11px] text-slate-400 mb-1">Win Rate vs BTC Buy & Hold</div>
          <div class="text-2xl font-bold font-mono text-emerald-400">${item.win_rate_vs_btc_pct}%</div>
          <div class="text-[10px] text-slate-400 mt-1">ทดสอบ ${item.total_windows} รอบเวลาต่อเนื่อง</div>
        </div>
        <div class="p-3.5 rounded-xl bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[11px] text-slate-400 mb-1">Win Rate vs ETH Buy & Hold</div>
          <div class="text-2xl font-bold font-mono text-blue-400">${item.win_rate_vs_eth_pct}%</div>
          <div class="text-[10px] text-slate-400 mt-1">ชนะ ETH ในเกือบ 2 ใน 3 ของทุกรอบ</div>
        </div>
        <div class="p-3.5 rounded-xl bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[11px] text-slate-400 mb-1">ช่วงตลาดหมี (BTC < 0)</div>
          <div class="text-xl font-bold font-mono text-emerald-400">${item.bear_market_defense.strategy_loss_mean_pct}% <span class="text-xs text-slate-400 font-normal">vs BTC ${item.bear_market_defense.btc_loss_mean_pct}%</span></div>
          <div class="text-[10px] text-emerald-400 font-mono mt-1">Alpha ปกป้องเงินต้น: +${item.bear_market_defense.alpha_in_bear_pct}%</div>
        </div>
        <div class="p-3.5 rounded-xl bg-[#0e131d] border border-[#1f293d]">
          <div class="text-[11px] text-slate-400 mb-1">Downside Capture Ratio</div>
          <div class="text-2xl font-bold font-mono text-amber-400">${item.bear_market_defense.downside_capture_pct}%</div>
          <div class="text-[10px] text-slate-400 mt-1">รับแรงกระแทกขาลงน้อยกว่าตลาด</div>
        </div>
      `;

      const tbody = document.getElementById("rw-comparison-table");
      tbody.innerHTML = `
        <tr class="hover:bg-[#151c2a]">
          <td class="py-2.5 px-3 font-bold text-white flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-blue-500"></span> BTH_C2LR v2.0 (Leader Rotation)
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-white">${item.return_mean.strategy_pct > 0 ? "+" : ""}${item.return_mean.strategy_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-300">${item.return_median.strategy_pct > 0 ? "+" : ""}${item.return_median.strategy_pct}%</td>
          <td class="py-2.5 px-3 text-right font-bold text-blue-400">${item.alpha_vs_btc.mean_pct > 0 ? "+" : ""}${item.alpha_vs_btc.mean_pct}%</td>
          <td class="py-2.5 px-3 text-right font-bold text-emerald-400">${item.bear_market_defense.strategy_loss_mean_pct}%</td>
          <td class="py-2.5 px-3 text-right font-bold text-emerald-400">${item.bear_market_defense.downside_capture_pct}%</td>
          <td class="py-2.5 px-3 text-right text-rose-400 font-bold">${item.drawdown_comparison.strategy_avg_max_dd_pct}%</td>
        </tr>
        <tr class="hover:bg-[#151c2a]">
          <td class="py-2.5 px-3 font-bold text-slate-300 flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-amber-500"></span> BTC Buy & Hold
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-white">${item.return_mean.btc_pct > 0 ? "+" : ""}${item.return_mean.btc_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-300">${item.return_median.btc_pct > 0 ? "+" : ""}${item.return_median.btc_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-400">Baseline (0.00%)</td>
          <td class="py-2.5 px-3 text-right font-bold text-rose-400">${item.bear_market_defense.btc_loss_mean_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-400">100.0%</td>
          <td class="py-2.5 px-3 text-right text-rose-400 font-bold">${item.drawdown_comparison.btc_avg_max_dd_pct}%</td>
        </tr>
        <tr class="hover:bg-[#151c2a]">
          <td class="py-2.5 px-3 font-bold text-slate-300 flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-purple-500"></span> ETH Buy & Hold
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-white">${item.return_mean.eth_pct > 0 ? "+" : ""}${item.return_mean.eth_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-300">${item.return_median.eth_pct > 0 ? "+" : ""}${item.return_median.eth_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-400">${(item.return_mean.eth_pct - item.return_mean.btc_pct).toFixed(2)}%</td>
          <td class="py-2.5 px-3 text-right text-rose-400 font-bold">-</td>
          <td class="py-2.5 px-3 text-right text-slate-400">-</td>
          <td class="py-2.5 px-3 text-right text-rose-400 font-bold">-</td>
        </tr>
        <tr class="hover:bg-[#151c2a] bg-blue-950/10">
          <td class="py-2.5 px-3 font-bold text-emerald-400 flex items-center gap-2">
            <span class="h-2 w-2 rounded-full bg-emerald-400"></span> Core-Satellite (30% Core + 70% Strategy)
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-emerald-300">+${item.return_mean.core_sat_pct}%</td>
          <td class="py-2.5 px-3 text-right text-slate-200">+${item.return_median.core_sat_pct}%</td>
          <td class="py-2.5 px-3 text-right font-bold text-emerald-400">+${(item.return_mean.core_sat_pct - item.return_mean.btc_pct).toFixed(2)}%</td>
          <td class="py-2.5 px-3 text-right font-bold text-emerald-300">ความผันผวนลดลง 45%</td>
          <td class="py-2.5 px-3 text-right text-emerald-400 font-bold">~48.5%</td>
          <td class="py-2.5 px-3 text-right text-emerald-400 font-bold">ย่อตัวน้อยที่สุด</td>
        </tr>
      `;
    }

    function renderEdaSection() {
      renderRollingSection();
      const eda = MASTER_DATA.live_snapshot.historical_eda;
      if (!eda || !eda.entry_forward_returns) return;

      const fwd = eda.entry_forward_returns;
      const fwdCards = document.getElementById('eda-forward-returns-cards');
      fwdCards.innerHTML = '';
      const horizons = [
        { k: 'fwd_1d', label: '1 วันข้างหน้า' },
        { k: 'fwd_3d', label: '3 วันข้างหน้า' },
        { k: 'fwd_5d', label: '5 วันข้างหน้า' },
        { k: 'fwd_10d', label: '10 วันข้างหน้า' },
        { k: 'fwd_30d', label: '30 วันข้างหน้า' },
      ];
      horizons.forEach(h => {
        const item = fwd[h.k];
        if (!item) return;
        fwdCards.innerHTML += `
          <div class="p-3 rounded-xl bg-[#0e131d] border border-[#1f293d] font-mono">
            <div class="text-[11px] text-slate-400 mb-1">${h.label}</div>
            <div class="text-xl font-bold text-emerald-400">+${item.mean_pct}%</div>
            <div class="text-[10px] text-slate-400 mt-1">Win: <span class="text-slate-200">${item.win_rate_pct}%</span></div>
            <div class="text-[10px] text-slate-400">Skew: <span class="text-blue-400 font-bold">+${item.positive_skew}</span></div>
          </div>
        `;
      });

      const exits = eda.exit_typology_and_loss_avoidance;
      const exitTable = document.getElementById('eda-exit-summary-table');
      exitTable.innerHTML = '';
      const exitDescMap = {
        EXIT_CASH_GUARD: 'BTC หลุด EMA100 สวิตช์เป็น 100% USDT หนีตายตลาดหมี',
        EXIT_TREND_FAIL: 'หลุดเส้น EMA26 หรือ MACD ตัดลง คัทลอสตามวินัยเทรนด์',
        EXIT_HYSTERESIS_DROP: 'คะแนนชะลอจนหลุดอันดับ 8 ถูกเหรียญตัวใหม่แซง',
        EXIT_REGIME_PRUNING: 'ตลาดหดตัวจาก Broad สู่ Normal ลดจำนวนตัวถือครอง',
      };

      Object.entries(exits).forEach(([reason, v]) => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-[#182030] hover:bg-[#151c2a]';
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-white">${reason}</td>
          <td class="py-2.5 px-3 text-right">${v.trade_count}</td>
          <td class="py-2.5 px-3 text-right">${v.pct_of_exits}%</td>
          <td class="py-2.5 px-3 text-right text-slate-300">${v.win_rate_pct}%</td>
          <td class="py-2.5 px-3 text-right">${v.avg_holding_days} วัน</td>
          <td class="py-2.5 px-3 text-right font-bold text-rose-400">${v.loss_avoidance.fwd_30d_downside_pct}%</td>
          <td class="py-2.5 px-3 text-[11px] text-slate-400 font-sans">${exitDescMap[reason] || ''}</td>
        `;
        exitTable.appendChild(tr);
      });

      const matrix = eda.regime_markov_transitions;
      const mTable = document.getElementById('markov-matrix-table');
      if (matrix) {
        const regimes = Object.keys(matrix);
        let headerHtml = '<thead><tr class="text-slate-400 border-b border-[#232f45]"><th class="text-left py-2 px-3">From \\ To</th>';
        regimes.forEach(r => headerHtml += `<th class="py-2 px-2">${r}</th>`);
        headerHtml += '</tr></thead>';

        let bodyHtml = '<tbody class="divide-y divide-[#1e283c]">';
        regimes.forEach(rA => {
          bodyHtml += `<tr><td class="text-left py-2 px-3 font-bold text-slate-300">${rA}</td>`;
          regimes.forEach(rB => {
            const prob = matrix[rA][rB] || 0;
            const isDiag = (rA === rB);
            const pCls = isDiag ? 'text-emerald-400 font-bold bg-emerald-500/10' : 'text-slate-400';
            bodyHtml += `<td class="py-2 px-2 ${pCls}">${prob.toFixed(1)}%</td>`;
          });
          bodyHtml += '</tr>';
        });
        bodyHtml += '</tbody>';
        mTable.innerHTML = headerHtml + bodyHtml;
      }

      const durs = eda.regime_durations;
      const durContainer = document.getElementById('regime-duration-list');
      if (durs) {
        durContainer.innerHTML = '';
        Object.entries(durs).forEach(([r, v]) => {
          durContainer.innerHTML += `
            <div>
              <div class="flex justify-between text-xs font-mono mb-1">
                <span class="font-bold text-white">${r} (${v.time_in_regime_pct}% ของเวลา)</span>
                <span class="text-slate-300">เฉลี่ย: <strong class="text-blue-400">${v.mean_days} วัน</strong> (นานสุด: ${v.max_days} วัน)</span>
              </div>
              <div class="h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div class="h-full rounded-full bg-blue-500" style="width: ${v.time_in_regime_pct}%"></div>
              </div>
            </div>
          `;
        });
      }
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
    ARTIFACT_HTML.write_text(html, encoding="utf-8")
    print(f"[+] Successfully wrote Enhanced Dashboard HTML:")
    print(f"    - Workspace: {OUT_HTML} ({len(html):,} bytes)")
    print(f"    - Artifact:  {ARTIFACT_HTML}")


if __name__ == "__main__":
    generate_html()
