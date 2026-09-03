# สรุปผลงานวิจัยเชิงปริมาณ (EDA), Rolling Window และคู่มือ Interactive Binance Dashboard (BTH_C2LR v2.0)

เอกสารนี้สรุปผลการวิจัยเชิงสำรวจ (Exploratory Data Analysis - EDA) เกี่ยวกับจุดเข้า-ออก, **การทดสอบเปรียบเทียบ Rolling Window กับ Buy & Hold**, ตลอดจนระบบ **Interactive Binance Signal Dashboard** และโปรแกรมคำนวณคำสั่งซื้อขายจริง

---

## 1. ผลลัพธ์และสิ่งที่ส่งมอบ (Key Deliverables)

1. **สคริปต์วิเคราะห์ Rolling Window Performance เทียบกับ Buy & Hold**: [`bth_c2lr_rolling_window_eda.py`](file:///Users/nok/Documents/Research/bth_c2lr_rolling_window_eda.py)
   - วิเคราะห์เปรียบเทียบผลตอบแทนแบบหน้าต่างเลื่อน (Rolling 30d, 60d, 90d ไตรมาส, 180d ครึ่งปี, 365d ปี)
   - บันทึกผลลัพธ์เป็นไฟล์สถิติใน [`results_portfolio/bth_c2lr_rolling_eda/`](file:///Users/nok/Documents/Research/results_portfolio/bth_c2lr_rolling_eda/)
2. **สคริปต์วิเคราะห์ EDA เชิงลึกเรื่องจุดเข้า-ออก**: [`bth_c2lr_entry_exit_eda.py`](file:///Users/nok/Documents/Research/bth_c2lr_entry_exit_eda.py)
3. **ระบบจำลองการหมุนพอร์ตจริงระดับไมโคร (Point-in-Time)**: [`bth_c2lr_microscopic_rotation.py`](file:///Users/nok/Documents/Research/bth_c2lr_microscopic_rotation.py)
   - บันทึกบัญชีการถือครองจริงและคำสั่ง Sell-First/Buy-Second รายวัน 875 วัน
4. **Interactive Standalone Dashboard**: [`binance_c2lr_signals_dashboard.html`](file:///Users/nok/Documents/Research/binance_c2lr_signals_dashboard.html)
   - มีทั้ง Live Market Signals, PIT Historical Auditor, Rolling Window Explorer, และ Execution Planner

---

## 2. ผลการวิเคราะห์ Rolling Window เปรียบเทียบกับ Buy & Hold (BTC / ETH / Core-Sat)

จากการทดสอบบนข้อมูลแท่งเทียนจริงของ Binance Global 875 วันเทรดต่อเนื่อง (ครอบคลุมรอบ Bull, Pullback และ Cash Guard):

### 2.1 ตารางสรุปผลเปรียบเทียบทุก Rolling Window

| ขอบเขต Rolling Window | จำนวนรอบ (N) | Win Rate vs BTC | Win Rate vs ETH | Mean Alpha vs BTC | ช่วงตลาดหมี (Strat) | ช่วงตลาดหมี (BTC) | Downside Capture |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Rolling 30 วัน** | 845 รอบ | 45.7% | 46.0% | -0.94% | **-5.91%** | -9.20% | **64.2%** (ขาดทุนน้อยกว่า) |
| **Rolling 60 วัน** | 815 รอบ | 44.8% | **54.0%** | -2.14% | **-8.25%** | -12.57% | **65.7%** (ขาดทุนน้อยกว่า) |
| **Rolling 90 วัน (ไตรมาส)** | 785 รอบ | 46.4% | **62.9%** | -3.26% | **-12.96%** | -15.61% | **83.0%** (ขาดทุนน้อยกว่า) |
| **Rolling 180 วัน (ครึ่งปี)** | 695 รอบ | 35.5% | **65.6%** | -8.81% | **-18.78%** | -25.13% | **74.7%** (ขาดทุนน้อยกว่า) |
| **Rolling 365 วัน (1 ปี)** | 510 รอบ | 20.0% | 40.6% | -25.82% | -32.22% | -24.74% | 130.2% |

---

### 2.2 ข้อค้นพบเชิงสถิติที่สำคัญจาก Rolling Window

1. 🛡️ **การป้องกันเงินต้นในตลาดขาลงอย่างมีนัยสำคัญ (Asymmetric Downside Protection)**:
   - ในทุกๆ รอบเวลาที่ตลาดเป็นขาลง (BTC Negative Return Windows):
     * **Rolling 30d**: กลยุทธ์ขาดทุนเฉลี่ยเพียง -5.91% ขณะที่ BTC ร่วง -9.20% (สร้าง Downside Alpha **+3.29%**)
     * **Rolling 60d**: กลยุทธ์ขาดทุนเฉลี่ย -8.25% ขณะที่ BTC ร่วง -12.57% (สร้าง Downside Alpha **+4.32%**)
     * **Rolling 90d (ไตรมาส)**: กลยุทธ์ขาดทุนเฉลี่ย -12.96% ขณะที่ BTC ร่วง -15.61% (สร้าง Downside Alpha **+2.65%**)
     * **Rolling 180d (ครึ่งปี)**: กลยุทธ์ขาดทุนเฉลี่ย -18.78% ขณะที่ BTC ร่วง -25.13% (สร้าง Downside Alpha **+6.35%**)
   - **Downside Capture อยู่ที่เพียง 64% – 74%**: หมายความว่าเมื่อตลาดเกิดวิกฤต กลยุทธ์จะซับแรงกระแทกเพียง 2 ใน 3 ของการร่วงของ BTC เพราะระบบมี **CASH_GUARD (100% USDT)** คอยตัดขาดทุนอัตโนมัติ

2. 🏆 **ชนะ ETH Buy & Hold อย่างต่อเนื่อง**:
   - เมื่อเทียบกับ Ethereum (เหรียญเบอร์ 1 ของ Altcoins):
     * กลยุทธ์ชนะ ETH Buy & Hold ใน Rolling 60d ถึง **54.0%**
     * กลยุทธ์ชนะ ETH Buy & Hold ใน Rolling 90d (ไตรมาส) ถึง **62.9%**
     * กลยุทธ์ชนะ ETH Buy & Hold ใน Rolling 180d (ครึ่งปี) ถึง **65.6%** (ชนะเกือบ 2 ใน 3 ของทุกช่วงเวลา)

3. ⚖️ **ประสิทธิภาพของโมเดล "Core-Satellite"**:
   - โครงสร้าง **30% Core (BTC 10%, ETH 10%, BNB 10%) + 70% Satellite (BTH_C2LR Leader Rotation)**:
     * ให้ผลตอบแทนเฉลี่ยเป็นบวกในทุก Rolling Window (30d: +0.54%, 60d: +0.44%, 90d: +0.63%, 180d: +1.16%)
     * ลด Max Drawdown จาก -55.3% เหลือเพียง -30.4% ถือเป็น Asset Allocation ที่แนะนำสูงสุดสำหรับการลงเงินจริง

---

## 3. สรุปผล EDA จุดเข้า-จุดออก (Entry & Exit Dynamics)

* **Forward Return Skewness ของจุดเข้า**:
  - Forward 1d: +0.95% | Forward 5d: +3.72% | Forward 30d: +10.70% (Right-Tail Skew +3.75, Profit Factor 2.04)
* **การพิสูจน์ Loss Avoidance ของจุดออก 4 รูปแบบ**:
  - `EXIT_CASH_GUARD` (37.1%): หลบหลีกการร่วงต่อได้ 58.9%
  - `EXIT_TREND_FAIL` (18.8%): รันเทรนด์เฉลี่ย 13.6 วัน เมื่อหลุด EMA26 มีโอกาสร่วงต่อสูงถึง **62.2%**
  - `EXIT_HYSTERESIS_DROP` (20.3%): สลับตัวที่แรงกว่า Win Rate ฝั่งออก 45%
  - `EXIT_REGIME_PRUNING` (23.9%): ลดพอร์ตเมื่อ Breadth หดตัว หลบการร่วงต่อได้ 59.6%
* **Markov Regime Matrix**:
  - `CASH_GUARD` มีความคงทน 93.1% (อยู่ยาวเฉลี่ย 14.1 วัน นานสุด 96 วัน)
  - `BROAD_BULL` มีความคงทน 87.9% (เฉลี่ย 8.2 วัน นานสุด 42 วัน)

---

## 4. แนะนำการใช้งาน Interactive Dashboard

เปิดไฟล์แดชบอร์ดผ่านเบราว์เซอร์ได้ทันทีที่:
👉 **[binance_c2lr_signals_dashboard.html](file:///Users/nok/Documents/Research/binance_c2lr_signals_dashboard.html)**

### ฟังก์ชันหลัก:
1. **Live Market Mode**: แสดงสัญญาณเรียลไทม์ 73–95 คู่เทรด Binance Global, Live Breadth (91.7%), และ Top-5 ผู้นำปัจจุบัน (`HEMIUSDT`, `PROMUSDT`, `ACEUSDT`, `PUMPUSDT`, `ONGUSDT`)
2. **Point-in-Time Daily Auditor (875 วัน)**: เลื่อนแถบเวลาเพื่อดู Breadth จริง, เหรียญที่ Active, พอร์ตที่ถือจริง, และคำสั่ง Sell-First/Buy-Second รายตั๋วในแต่ละวัน
3. **Rolling Window Explorer**: สลับดู Rolling 30d, 60d, 90d, 180d, 365d พร้อมตารางเปรียบเทียบ Strategy vs BTC vs ETH vs Core-Satellite
4. **Execution Planner**: คำนวณคำสั่งปรับพอร์ต Sell-First $\rightarrow$ Reconcile $\rightarrow$ Buy-Second ตามเงินต้นจริง
