# Order Flow Arrows (ATAS Indicator)

A lightweight **tick-by-tick order-flow indicator** for the **ATAS trading platform**.
It compares **Bid vs Ask delta** on each bar and plots:

- ✅ **Up-arrow** above the bar when bullish pressure is present
- ✅ **Down-arrow** below the bar when bearish pressure is present

This indicator works on **real-time and historical data**, supports user-editable settings, and includes an optional sound alert.

---

## Features

| Feature | Description |
|--------|-------------|
| Tick-by-tick calculation | Updates live as new ticks arrive |
| Delta-based signals | Uses (Bid Volume – Ask Volume) |
| OHLC confirmation | Requires bar direction to confirm signal |
| Customizable | Colors, arrow offset, delta threshold |
| Optional alert | Sound alert on new signal |
| Works on history | No external data needed |

---

## Signal Logic

