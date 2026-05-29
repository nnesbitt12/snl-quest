# Castellan Farm — Solar + BESS Project Analysis

_Generated 2026-05-29 using QuESt BTM (engine: **quest**) + project financial model._

> **Currency:** CAD. All results depend on the editable assumptions in `assumptions/` and the curated inputs in `input_data/`. See **Limitations** below before relying on these numbers.

## 1. Headline results

| Metric | Value |
|---|---|
| Total project CAPEX | $78,309 (battery_scope_only) |
| Year-1 total savings | $22,149/yr |
| — PV self-consumption savings | $4,157/yr |
| — Battery dispatch savings | $17,992/yr |
| Annual O&M | $2,000/yr |
| Simple payback | 3.82 years |
| NPV @ 8.0% over 20 yr | $133,255 |
| IRR | 26.5% |
| Avg. monthly peak-demand reduction | 30.5 kW |
| Solar self-consumption (no batt → batt) | 42.3% → 60.6% |

## 2. Battery sizing recommendation

Across the swept range, NPV is maximised at **1300 kWh / 150 kW** (NPV $148,215). Existing pack is ~650 kWh; recommendation is the NPV-maximising size across the swept range under current assumptions.

|   battery_kwh |   battery_kw |   battery_savings_cad |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|--------------:|-------------:|----------------------:|--------------------:|----------:|----------:|-----------------------:|
|           325 |        37.5  |                 14704 |               18861 |     99377 |     22.09 |                   4.55 |
|           488 |        56.31 |                 16966 |               21123 |    122685 |     25.11 |                   4.02 |
|           650 |        75    |                 17992 |               22149 |    133255 |     26.46 |                   3.82 |
|           812 |        93.69 |                 18547 |               22704 |    138978 |     27.19 |                   3.72 |
|           975 |       112.5  |                 18918 |               23075 |    142801 |     27.68 |                   3.66 |
|          1300 |       150    |                 19444 |               23601 |    148215 |     28.37 |                   3.57 |

## 3. Energy, savings and demand

- **Annual farm load:** 221,889 kWh (peak 126 kW)
- **Annual PV generation (modelled):** 63,510 kWh
- **Status-quo utility bill (grid only):** $42,668/yr
- **PV-only bill (baseline case):** $38,511/yr
- **PV + battery bill (battery case):** $20,519/yr
- **Annual energy-charge savings (battery):** $9,849/yr
- **Annual demand-charge savings (battery):** $8,375/yr

## 4. CAPEX (from BOM)

| Component | CAD |
|---|---|
| BOM base (battery_scope_only) | $101,700 |
| Battery (new) | $0 |
| Adders (EPC / interconnection / engineering / other) | $0 |
| Contingency | $10,170 |
| Subtotal (pre-incentive) | $111,870 |
| Clean-Tech ITC (30%) | −$33,561 |
| **Total CAPEX (net)** | **$78,309** |

Top included BOM line items:

| category       | item                            | qty      | scope   |   total_cost |
|:---------------|:--------------------------------|:---------|:--------|-------------:|
| Labour         | Labour and Trenching            | -        | SHARED  |        77500 |
| Main Equipment | Battery Inverter                | 3        | BATTERY |        35000 |
| Battery DC     | Battery Cables                  | As req'd | BATTERY |        22000 |
| Main Equipment | PV Modules                      | 150      | PV      |        16500 |
| PV DC Side     | PV Wire                         | As req'd | PV      |        15000 |
| PV DC Side     | Cable Management                | As req'd | SHARED  |        15000 |
| Engineering    | Basic SLD + Layout + Prelim BOM | -        | SHARED  |        13000 |
| Battery DC     | Battery Rack Breaker            | 8-12     | BATTERY |        11000 |
| AC Power       | Battery Inverter Cable          | As req'd | BATTERY |        10000 |
| AC Power       | Main Bus Cable                  | As req'd | SHARED  |         9000 |

## 5. Cash flow

|   year |   gross_savings_cad |   opex_cad |   net_cash_flow_cad |   cumulative_net_cad |   cumulative_discounted_cad |
|-------:|--------------------:|-----------:|--------------------:|---------------------:|----------------------------:|
|      1 |             22148.9 |    2000    |             20148.9 |            -58160.1  |                   -59652.6  |
|      2 |             22421.3 |    2040    |             20381.3 |            -37778.8  |                   -42178.9  |
|      3 |             22690.2 |    2080.8  |             20609.3 |            -17169.5  |                   -25818.6  |
|      4 |             22954.9 |    2122.42 |             20832.5 |              3663.07 |                   -10506    |
|      5 |             23215.2 |    2164.86 |             21050.3 |             24713.4  |                     3820.46 |
|      6 |             23470.4 |    2208.16 |             21262.2 |             45975.6  |                    17219.3  |
|      7 |             23720   |    2252.32 |             21467.7 |             67443.4  |                    29745.5  |
|      8 |             23963.5 |    2297.37 |             21666.1 |             89109.5  |                    41451    |
|      9 |             24200.3 |    2343.32 |             21856.9 |            110966    |                    52384.9  |
|     10 |             24429.6 |    2390.19 |             22039.5 |            133006    |                    62593.5  |
|     11 |             24651   |    2437.99 |             22213   |            155219    |                    72120.2  |
|     12 |             24863.7 |    2486.75 |             22376.9 |            177596    |                    81006.4  |
|     13 |             25066.9 |    2536.48 |             22530.4 |            200126    |                    89290.8  |
|     14 |             25260   |    2587.21 |             22672.7 |            222799    |                    97010    |
|     15 |             25442   |    2638.96 |             22803.1 |            245602    |                   104198    |
|     16 |             25612.3 |    2691.74 |             22920.5 |            268523    |                   110889    |
|     17 |             25769.9 |    2745.57 |             23024.3 |            291547    |                   117112    |
|     18 |             25913.9 |    2800.48 |             23113.4 |            314660    |                   122896    |
|     19 |             26043.3 |    2856.49 |             23186.8 |            337847    |                   128268    |
|     20 |             26157.2 |    2913.62 |             23243.5 |            361091    |                   133255    |

## 6. Sensitivity analysis
### 6.1 CAPEX (multiplier on total CAPEX)

|   capex_multiplier |   total_capex_cad |   npv_cad |   irr_pct |   simple_payback_years |
|-------------------:|------------------:|----------:|----------:|-----------------------:|
|                0.8 |           62647.2 |    148917 |     33.07 |                   3.07 |
|                0.9 |           70478.1 |    141086 |     29.42 |                   3.45 |
|                1   |           78309   |    133255 |     26.46 |                   3.82 |
|                1.1 |           86139.9 |    125424 |     24.02 |                   4.2  |
|                1.2 |           93970.8 |    117593 |     21.95 |                   4.57 |

### 6.2 Electricity rate (multiplier on savings)

|   rate_multiplier |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|------------------:|--------------------:|----------:|----------:|-----------------------:|
|               0.8 |               17719 |     86401 |     20.46 |                   4.88 |
|               0.9 |               19934 |    109828 |     23.49 |                   4.29 |
|               1   |               22149 |    133255 |     26.46 |                   3.82 |
|               1.1 |               24364 |    156682 |     29.4  |                   3.45 |
|               1.2 |               26579 |    180109 |     32.3  |                   3.15 |
|               1.5 |               33223 |    250390 |     40.91 |                   2.48 |

### 6.3 Battery degradation rate

|   battery_degradation_rate |   npv_cad |   irr_pct |   simple_payback_years |
|---------------------------:|----------:|----------:|-----------------------:|
|                       0    |    168286 |     28.41 |                   3.73 |
|                       0.01 |    150771 |     27.47 |                   3.78 |
|                       0.02 |    133255 |     26.46 |                   3.82 |
|                       0.03 |    115740 |     25.37 |                   3.88 |
|                       0.05 |     80709 |     22.85 |                   3.99 |

### 6.4 Discount rate

|   discount_rate |   npv_cad |   irr_pct |   simple_payback_years |
|----------------:|----------:|----------:|-----------------------:|
|            0.04 |    217306 |     26.46 |                   3.82 |
|            0.06 |    169988 |     26.46 |                   3.82 |
|            0.08 |    133255 |     26.46 |                   3.82 |
|            0.1  |    104346 |     26.46 |                   3.82 |
|            0.12 |     81291 |     26.46 |                   3.82 |

## 7. Assumptions used

**Battery**
- Energy capacity: 650 kWh; power: 75 kW
- Round-trip efficiency: 88%; usable SOC: 10%–90% (80% usable DoD)
- Annual degradation: 2.0%; battery in CAPEX: False (existing pack treated as sunk cost unless set true)

**Financial**
- Discount rate: 8.0%; project life: 20 yr
- Electricity escalation: 3.0%; O&M escalation: 2.0%
- Annual O&M: $2,000; contingency: 10%; PV degradation: 0.5%

**Utility rate** — Centre Wellington Hydro ULO + GS>50kW demand (CAD/kWh)
- Energy rates by TOU period: period 0: 0.045, period 1: 0.115, period 2: 0.295
- Net metering: flat credit (NEM 1.0) @ 0.02 $/kWh

**Solar:** existing 50 kW array, modelled (clear-sky + monthly scaling), ~63,510 kWh/yr. Replace `input_data/solar_production.csv` with measured / PVWatts data when available.

## 8. Limitations

1. **Load data is daily-resolution.** The metered usage workbook repeats a single value across all 24 hours of each day, so the load profile has no intrinsic intraday shape. TOU energy arbitrage is still valued (prices vary intraday) but within-day load peaks and load-following are not represented. Enable `apply_intraday_load_shape` to overlay a generic farm shape.
2. **Solar is modelled, not measured.** PV output is a clear-sky estimate scaled to a typical Ontario capacity factor; actual generation will vary with weather, soiling, shading and array orientation.
3. **Rate covers energy commodity only.** The configured TOU energy rates are modelled with a flat net-metering export credit. Delivery, regulatory, fixed and global-adjustment charges are **not** included; actual bill savings may differ, especially where those charges scale with peak kW/kWh.
4. **Monthly independent optimization.** QuESt BTM optimizes each month separately with a fixed initial state of charge; it does not co-optimize across month boundaries or model ageing within the dispatch.
5. **Degradation & rate sensitivities are linear approximations.** Year-1 savings are scaled by capacity retention and price multipliers rather than re-optimized each year (battery-size cases _are_ re-optimized).
6. **Holiday calendar.** QuESt's schedule builder uses US federal holidays; Ontario statutory holidays differ slightly, marginally affecting which days are billed at weekend (off-peak) rates.
