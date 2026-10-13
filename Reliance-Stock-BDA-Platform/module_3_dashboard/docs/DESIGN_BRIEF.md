# Stock sight · design brief

*Market foresight for Reliance Industries.* One page. Written before coding; the tokens below are the ones
`theme.py` ships.

## 1. Brand guide (one line each)

| | |
|---|---|
| **Name** | Stock sight. Lowercase "sight". Never "cockpit", "HUD", "terminal". |
| **Logo mark** | A 24 px eye: the upper lid is an arc, the lower lid is a rising price line, the pupil is a filled accent dot. Inline SVG, single colour (accent), no gradient. |
| **Wordmark** | "Stock sight" in Space Grotesk 600, tracking −0.02em, text colour. The mark sits left of it in accent. |
| **Display font** | Space Grotesk (wordmark, page titles, section titles). |
| **UI font** | Inter (everything else). |
| **Number font** | JetBrains Mono with `tnum` on, for every number that can change. |
| **Accent** | Electric teal `#19D3C5`. Used for brand, focus rings, active nav item, the forecast series. Never for a signal. |
| **Voice** | Confident, plain, numbers first. "Composite 53.5 sits in the HOLD band." Not "Our AI believes…". No emoji in headings. |

## 2. Palette tokens (dark-first) with contrast ratios

Contrast is WCAG 2.x, measured against the three backgrounds. AA for normal text is 4.5:1, large text 3:1.

| Token | Hex | On ink | On surface-1 | On surface-2 | Use |
|---|---|---:|---:|---:|---|
| `ink` | `#0A0E14` | – | – | – | Page background (deep blue-black, not flat black) |
| `surface1` | `#111722` | – | – | – | Cards, sidebar, chart plot area |
| `surface2` | `#182130` | – | – | – | Nested controls, table header, hover |
| `border` | `#232D3F` | 1.4 | 1.3 | 1.2 | Hairlines only, never text |
| `text` | `#E8EDF5` | 16.5 | 15.3 | 13.8 | Primary text and numbers |
| `text2` | `#9AA6B8` | 7.8 | 7.3 | 6.6 | Secondary text, labels |
| `muted` | `#7F8B9E` | 5.6 | 5.2 | 4.7 | Captions, timestamps (still AA) |
| `accent` | `#19D3C5` | 10.3 | 9.5 | 8.6 | Brand, focus, active nav, forecast series |
| `up` | `#22C55E` | 8.5 | 7.9 | 7.1 | BUY, positive change, candles up |
| `down` | `#F2555A` | 5.7 | 5.3 | 4.8 | SELL, negative change, candles down |
| `warn` | `#F5A524` | 9.5 | 8.8 | 7.9 | HOLD, stale data, caution |
| `neutral` | `#9AA6B8` | 7.8 | 7.3 | 6.6 | FLAT, no-change |
| `violet` | `#A78BFA` | 7.1 | 6.6 | 5.9 | Secondary chart series (VWAP) |
| `blue` | `#60A5FA` | 7.6 | 7.1 | 6.4 | Tertiary chart series (EMA) |

Why teal: green/amber/red are already spoken for by BUY/HOLD/SELL, and blue reads as "link" on the web.
Teal is the one saturated hue left that is unmistakably "the product" and never "a signal". Why `#F2555A`
over the stock `#EF4444`: the latter drops to 4.3:1 on surface-2 and fails AA.

Colour is never the only channel: every signed number carries a `+`/`−` and every direction a `▲`/`▼`/`▬`.

## 3. Type scale (five sizes, nothing else)

| Token | Size | Font | Use |
|---|---|---|---|
| `xl` | 44 px / 2.75rem, 700 | JetBrains Mono | Hero numbers (last close, predicted close, P&L) |
| `l` | 22 px / 1.375rem, 600 | Space Grotesk (titles) · JetBrains Mono (tile values) | Page titles, metric values |
| `m` | 15 px / 0.9375rem, 400 | Inter | Body, table cells |
| `s` | 13 px / 0.8125rem, 500 | Inter | Captions, secondary values, ticker tape |
| `xs` | 11 px / 0.6875rem, 600, uppercase, +0.08em | Inter | Labels above numbers, chips, badges |

Numbers: rupees in the Indian system (`₹17,621.12`, `₹1,00,000`), percentages always signed (`+0.15%`),
volumes compact (`1.16 Cr`), tables right-aligned.

## 4. Motion rules

* Everything ≤ 300 ms, `cubic-bezier(.2,.7,.2,1)`. Nothing loops except the live dot and the ticker tape.
* Headline numbers count up on load (300 ms, from the previous value if known, else from 0).
* Live dot pulses (1.6 s) only while NSE is open; static dot otherwise.
* Cards fade/slide in 8 px with a 40 ms stagger, max 10 steps.
* Signal badge transitions background/colour over 250 ms when the signal changes.
* Backtest: Plotly `layout.transition` 250 ms, fixed x-range so bars draw forward; markers animate in.
* Ticker tape pauses on hover.
* `@media (prefers-reduced-motion: reduce)` turns all of the above off (numbers render final values).

## 5. Component list (`components.py`)

| Helper | Purpose |
|---|---|
| `app_bar(signal, as_of)` | Sticky top bar: mark + wordmark · `RELIANCE · NSE` · market status with dot · as-of · signal badge |
| `ticker_tape(items)` | Scrolling strip under the bar, pauses on hover |
| `metric(label, value, delta, spark, help)` | Tile: xs label, l value (mono), signed delta, optional sparkline |
| `hero_number(label, value, sub)` | xl number with count-up |
| `signal_badge(signal, size)` | BUY/HOLD/SELL chip with transition |
| `sentiment_chip(label, polarity)` | POSITIVE/NEGATIVE/NEUTRAL chip + polarity bar |
| `section(title, caption)` | Display-font section title with hairline, no emoji |
| `freshness_tag(path)` | "updated 3h ago · 4,174 rows" from the file on disk |
| `source_note(source, timestamp)` | Small "from reliance_predictions.csv · 2026-10-13 15:15" line under headline numbers |
| `range_bar(low, high, value, labels)` | 52-week / day-range position bar |
| `confidence_ring(pct)` | SVG ring for model confidence |
| `gauge(value, thresholds)` | Semicircle composite gauge with SELL/HOLD/BUY/STRONG BUY bands |
| `waterfall(T,F,N,R)` | Contribution bars: 0.40T + 0.20F + 0.25N + 0.15R = S |
| `fan_chart(close_hist, pred, low, high)` | Last N closes + forecast point + ±MAE fan |
| `sparkline(values)` | Tiny line, accent colour |
| `calendar_heatmap(returns)` | Daily returns heatmap |
| `news_card(row)` | Source, date, headline, polarity bar, chip |
| `table(df, name)` | `st.dataframe` with column_config + CSV download |
| `date_range(df, col)` | Date-range filter widget returning the slice |
| `empty_state(title, hint)` | Proper "no data" block with the file that is missing |
| `chart(fig)` | `st.plotly_chart(fig, theme=None)` with the Stock sight template |
| `footer()` | "Stock sight · v1 · built on Hadoop · Spark · Hive · HBase · Kafka" |

## 6. Wireframes (ASCII)

### Home / Overview
```
┌ ◉ Stock sight │ RELIANCE · NSE ───────────────── ● Market closed · 22:41 IST · as of 31 Dec 2025 · [HOLD] ┐
├ ▸ ₹17,621.12 ▼1.48% · RSI 27.2 · Composite 53.5 · HOLD · "Jio Platforms targets…" [POSITIVE] ▸▸▸ (tape) ┤
│                                                                                                          │
│ LAST CLOSE                 DAY CHANGE          DAY RANGE               52-WEEK RANGE          VOLUME     │
│ ₹17,621.12                 ▼ −263.81  −1.48%   17,260.80 ─●── 17,853    15,535 ──●────── 21,497  1.16 Cr │
│ as of 31 Dec 2025 · prices.csv                                                               1.28× ▁▂▅▃▇ │
│                                                                                                          │
│ ┌ TOMORROW'S CALL · target 01 Jan 2026 ───────────────────────┐ ┌ TODAY'S BRIEF ────────────────────┐   │
│ │ ₹17,647.55   ▬ +26.43 (+0.15%)   [ HOLD ]   confidence ◔ 55% │ │ • Closed below VWAP, 11th session │   │
│ │ ╭─ fan: last 30 closes → point + ±₹239.94 band ───────────╮ │ │ • RSI 27.2 is oversold (<30)      │   │
│ │ │        ╲╱╲__                                             │ │ │ • Composite 53.5 → HOLD band      │   │
│ │ │             ╲╲_   ▓▓▓                                    │ │ │ • EMA20 < EMA50, vol 1.28× avg    │   │
│ │ ╰──────────────────────────────────────────────────────────╯ │ └───────────────────────────────────┘   │
│ │ from reliance_predictions.csv · 2026-10-13 15:15             │ ┌ COMPOSITE ────────────────────────┐   │
│ └──────────────────────────────────────────────────────────────┘ │   ◜ 53.5 ◝  SELL│HOLD│BUY│STRONG  │   │
│ ┌ HOW THE SCORE ADDS UP ─────────────────────────────────────┐   │ T 21.3 ▇▇▇▇ F 13.9 ▇▇ N 12.5 ▇▇ R 5.7▇│   │
│ │ 0.40·T  ▇▇▇▇▇▇▇▇ 21.3 │ 0.20·F ▇▇▇▇ 13.9 │ 0.25·N ▇▇▇▇ 12.5 │ 0.15·R ▇ 5.7 │ = S 53.5                │   │
│ └────────────────────────────────────────────────────────────┘   └───────────────────────────────────┘   │
│ PIPELINE  ● prices 4,174 rows · 8h  ● news 5 · 7h  ● features · 8h  ● scores · 7h  ● predictions · 7h   │
│ NEWS & SENTIMENT   [card][card][card][card][card]   ⚠ news dates (Sep–Oct 2026) don't overlap prices     │
└ Stock sight · v1 · built on Hadoop · Spark · Hive · HBase · Kafka ───────────────────────────────────────┘
```

### Pipeline & Data
```
│ app bar + tape                                                                                 │
│ Pipeline & Data                                                                                │
│ [Sources] → [HDFS raw] → [Pig · MapReduce] → [Spark SQL · scores] → [MLlib] → [HBase · Hive] → [UI]│
│ STAGE TABLE: stage · file · status ● · rows · date coverage · last modified            [CSV]   │
│ DATA QUALITY: missing values 0 · date gaps 0 · news→price join 0 / 5 (0%) ⚠ explained         │
│ ┌ Source 1: prices ──┐ ┌ Source 2: news feed (cards + overlap warning) ─┐ ┌ Source 3: macro ─┐│
│ │ 4 metrics + table  │ │                                                 │ │ 4 metrics + table ││
│ TABS: HDFS zones | Hive schemas | Raw previews (date filter + CSV on each)                     │
```

### Technicals
```
│ app bar + tape                                                                                 │
│ Technicals     range (60D|180D|1Y|All) [from–to]     overlays (EMA 20)(EMA 50)(VWAP)(BB)       │
│ ┌ candles + overlays ───────────────────────────────────────────────── ₹ ┐                     │
│ │ volume                                                                 │  synced x           │
│ │ RSI 14  ── 70 ─────────────────────────────── 30 ──                    │                     │
│ │ MACD · signal · histogram                                              │                     │
│ INDICATOR SUMMARY  RSI 27.2 · Oversold · +65 → T    EMA 20<50 · Downtrend · +20 → T  …  [CSV]   │
│ SCORES  T 53.3  F 69.5  N 50.0  R 38.2  → S 53.5 (waterfall)      MOMENTUM 30d −10.6% 60d 90d  │
│ CALENDAR HEATMAP of daily returns (last 12 months)                                             │
```

### Prediction
```
│ app bar + tape                                                                                 │
│ Prediction                                                                                     │
│ ₹17,647.55  ▬ +26.43 (+0.15%)  [HOLD]  ◔ 55%   interval ₹17,407.61 – ₹17,887.49   target 1 Jan │
│ fan chart                      from reliance_predictions.csv · created 2026-10-13 15:15        │
│ MODEL CARD              Model          Naive (tomorrow = today)      Edge                       │
│   MAE                   ₹239.94        ₹239.84                       −0.04% (worse)             │
│   RMSE                  ₹308.01        ₹307.94                       worse                      │
│   Directional accuracy  48.4%          50.0% coin-flip               −1.6 pts                   │
│ FEATURE IMPORTANCES (bars)         PREDICTION HISTORY table [CSV]   SERVING LOG (HBase mock)    │
```

### Backtest
```
│ app bar + tape                                                                                 │
│ Backtest replay      horizon (1M|2M|3M)                                                        │
│ ┌ ⏮ Home ─ ▶ Space ─ ⏭ → ─ speed (1s|3s|5s|10s) ─ ═══════●═════ Day 12 / 23 · 2025-12-16 ─┐  │
│ NET P&L ₹+2,422.50 (+2.42%)   SESSION ▲ +₹787.50   EQUITY ₹1,02,422.50   WIN RATE 66.7% (2W/1L) │
│ ┌ candles drawing forward + EMA20 + ▲BUY ▼SELL markers + forecast + band ┐ ┌ TOMORROW'S CALL ┐ │
│ │ volume                                                                  │ │ ₹1,302 ▲ [BUY]  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │ action banner   │ │
│ ┌ equity curve vs buy & hold ───────┐ ┌ open trade card ─┐ ┌ ledger (win/loss tint) [CSV] ┐  │
│ audit log expander                          toast: "BUY 75 @ ₹1,285.50" / "SELL +₹1,252.50"    │
```
