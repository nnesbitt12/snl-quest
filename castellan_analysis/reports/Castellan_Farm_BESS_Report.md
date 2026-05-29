# Castellan Farm — Solar + BESS Project Analysis

_Generated 2026-05-29 using QuESt BTM (engine: **quest**) + project financial model._

> **Currency:** CAD. All results depend on the editable assumptions in `assumptions/` and the curated inputs in `input_data/`. See **Limitations** below before relying on these numbers.

## 1. Headline results

| Metric | Value |
|---|---|
| Total project CAPEX | $189,959 (bess_less_solar) |
| Year-1 total savings | $22,149/yr |
| — PV self-consumption savings | $4,157/yr |
| — Battery dispatch savings | $17,992/yr |
| Annual O&M | $2,000/yr |
| Simple payback | 9.03 years |
| NPV @ 8.0% over 20 yr | $21,605 |
| IRR | 9.4% |
| Avg. monthly peak-demand reduction | 30.5 kW |
| Solar self-consumption (no batt → batt) | 42.3% → 60.6% |

## 2. Battery sizing recommendation

Across the swept range, NPV is maximised at **1300 kWh / 150 kW** (NPV $36,565). Existing pack is ~650 kWh; recommendation is the NPV-maximising size across the swept range under current assumptions.

|   battery_kwh |   battery_kw |   battery_savings_cad |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|--------------:|-------------:|----------------------:|--------------------:|----------:|----------:|-----------------------:|
|           325 |        37.5  |                 14704 |               18861 |    -12273 |      7.15 |                  10.68 |
|           488 |        56.31 |                 16966 |               21123 |     11035 |      8.75 |                   9.49 |
|           650 |        75    |                 17992 |               22149 |     21605 |      9.45 |                   9.03 |
|           812 |        93.69 |                 18547 |               22704 |     27328 |      9.82 |                   8.8  |
|           975 |       112.5  |                 18918 |               23075 |     31151 |     10.07 |                   8.65 |
|          1300 |       150    |                 19444 |               23601 |     36565 |     10.42 |                   8.45 |

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
| BOM base (bess_less_solar) | $246,700 |
| Battery (new) | $0 |
| Adders (EPC / interconnection / engineering / other) | $0 |
| Contingency | $24,670 |
| Subtotal (pre-incentive) | $271,370 |
| Clean-Tech ITC (30%) | −$81,411 |
| **Total CAPEX (net)** | **$189,959** |

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
|      1 |             22148.9 |    2000    |             20148.9 |           -169810    |                  -171303    |
|      2 |             22421.3 |    2040    |             20381.3 |           -149429    |                  -153829    |
|      3 |             22690.2 |    2080.8  |             20609.3 |           -128819    |                  -137469    |
|      4 |             22954.9 |    2122.42 |             20832.5 |           -107987    |                  -122156    |
|      5 |             23215.2 |    2164.86 |             21050.3 |            -86936.6  |                  -107830    |
|      6 |             23470.4 |    2208.16 |             21262.2 |            -65674.4  |                   -94430.7  |
|      7 |             23720   |    2252.32 |             21467.7 |            -44206.6  |                   -81904.5  |
|      8 |             23963.5 |    2297.37 |             21666.1 |            -22540.5  |                   -70199    |
|      9 |             24200.3 |    2343.32 |             21856.9 |              -683.57 |                   -59265.1  |
|     10 |             24429.6 |    2390.19 |             22039.5 |             21355.9  |                   -49056.5  |
|     11 |             24651   |    2437.99 |             22213   |             43568.9  |                   -39529.8  |
|     12 |             24863.7 |    2486.75 |             22376.9 |             65945.8  |                   -30643.6  |
|     13 |             25066.9 |    2536.48 |             22530.4 |             88476.2  |                   -22359.2  |
|     14 |             25260   |    2587.21 |             22672.7 |            111149    |                   -14640    |
|     15 |             25442   |    2638.96 |             22803.1 |            133952    |                    -7451.53 |
|     16 |             25612.3 |    2691.74 |             22920.5 |            156873    |                     -761.24 |
|     17 |             25769.9 |    2745.57 |             23024.3 |            179897    |                     5461.51 |
|     18 |             25913.9 |    2800.48 |             23113.4 |            203010    |                    11245.6  |
|     19 |             26043.3 |    2856.49 |             23186.8 |            226197    |                    16618.3  |
|     20 |             26157.2 |    2913.62 |             23243.5 |            249441    |                    21605.1  |

## 6. Sensitivity analysis
### 6.1 CAPEX (multiplier on total CAPEX)

|   capex_multiplier |   total_capex_cad |   npv_cad |   irr_pct |   simple_payback_years |
|-------------------:|------------------:|----------:|----------:|-----------------------:|
|                0.8 |            151967 |     59597 |     12.77 |                   7.29 |
|                0.9 |            170963 |     40601 |     10.96 |                   8.16 |
|                1   |            189959 |     21605 |      9.45 |                   9.03 |
|                1.1 |            208955 |      2609 |      8.16 |                   9.89 |
|                1.2 |            227951 |    -16387 |      7.05 |                  10.75 |

### 6.2 Electricity rate (multiplier on savings)

|   rate_multiplier |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|------------------:|--------------------:|----------:|----------:|-----------------------:|
|               0.8 |               17719 |    -25249 |      6.21 |                  11.46 |
|               0.9 |               19934 |     -1822 |      7.87 |                  10.1  |
|               1   |               22149 |     21605 |      9.45 |                   9.03 |
|               1.1 |               24364 |     45032 |     10.95 |                   8.17 |
|               1.2 |               26579 |     68459 |     12.4  |                   7.46 |
|               1.5 |               33223 |    138740 |     16.5  |                   5.92 |

### 6.3 Battery degradation rate

|   battery_degradation_rate |   npv_cad |   irr_pct |   simple_payback_years |
|---------------------------:|----------:|----------:|-----------------------:|
|                       0    |     56636 |     11.38 |                   8.43 |
|                       0.01 |     39121 |     10.47 |                   8.7  |
|                       0.02 |     21605 |      9.45 |                   9.03 |
|                       0.03 |      4090 |      8.29 |                   9.42 |
|                       0.05 |    -30941 |      5.3  |                  10.53 |

### 6.4 Discount rate

|   discount_rate |   npv_cad |   irr_pct |   simple_payback_years |
|----------------:|----------:|----------:|-----------------------:|
|            0.04 |    105656 |      9.45 |                   9.03 |
|            0.06 |     58338 |      9.45 |                   9.03 |
|            0.08 |     21605 |      9.45 |                   9.03 |
|            0.1  |     -7304 |      9.45 |                   9.03 |
|            0.12 |    -30359 |      9.45 |                   9.03 |

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
