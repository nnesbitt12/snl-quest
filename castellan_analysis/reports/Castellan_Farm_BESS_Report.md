# Castellan Farm — Solar + BESS Project Analysis

_Generated 2026-05-29 using QuESt BTM (engine: **quest**) + project financial model._

> **Currency:** CAD. All results depend on the editable assumptions in `assumptions/` and the curated inputs in `input_data/`. See **Limitations** below before relying on these numbers.

## 1. Headline results

| Metric | Value |
|---|---|
| Total project CAPEX | $78,309 (battery_scope_only) |
| Year-1 total savings | $14,188/yr |
| — PV self-consumption savings | $3,004/yr |
| — Battery dispatch savings | $11,184/yr |
| Annual O&M | $2,000/yr |
| Simple payback | 6.24 years |
| NPV @ 8.0% over 20 yr | $49,555 |
| IRR | 15.5% |
| Avg. monthly peak-demand reduction | 22.4 kW |
| Solar self-consumption (no batt → batt) | 40.0% → 57.7% |

## 2. Battery sizing recommendation

Across the swept range, NPV is maximised at **1300 kWh / 150 kW** (NPV $55,429). Existing pack is ~650 kWh; recommendation is the NPV-maximising size across the swept range under current assumptions.

|   battery_kwh |   battery_kw |   battery_savings_cad |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|--------------:|-------------:|----------------------:|--------------------:|----------:|----------:|-----------------------:|
|           325 |        37.5  |                  9670 |               12674 |     33956 |     13.24 |                   7.09 |
|           488 |        56.31 |                 10870 |               13874 |     46319 |     15.01 |                   6.4  |
|           650 |        75    |                 11184 |               14188 |     49555 |     15.47 |                   6.24 |
|           812 |        93.69 |                 11393 |               14397 |     51703 |     15.77 |                   6.14 |
|           975 |       112.5  |                 11541 |               14545 |     53230 |     15.98 |                   6.07 |
|          1300 |       150    |                 11754 |               14759 |     55429 |     16.29 |                   5.97 |

## 3. Energy, savings and demand

- **Annual farm load:** 175,530 kWh (peak 115 kW)
- **Annual PV generation (modelled):** 63,510 kWh
- **Status-quo utility bill (grid only):** $21,534/yr
- **PV-only bill (baseline case):** $18,530/yr
- **PV + battery bill (battery case):** $7,346/yr
- **Annual energy-charge savings (battery):** $8,178/yr
- **Annual demand-charge savings (battery):** $3,231/yr

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
|      1 |             14188.5 |    2000    |             12188.5 |            -66120.5  |                   -67023.4  |
|      2 |             14368.2 |    2040    |             12328.2 |            -53792.3  |                   -56453.9  |
|      3 |             14546   |    2080.8  |             12465.2 |            -41327.1  |                   -46558.6  |
|      4 |             14721.6 |    2122.42 |             12599.2 |            -28727.9  |                   -37297.8  |
|      5 |             14894.6 |    2164.86 |             12729.7 |            -15998.2  |                   -28634.2  |
|      6 |             15064.7 |    2208.16 |             12856.5 |             -3141.65 |                   -20532.4  |
|      7 |             15231.6 |    2252.32 |             12979.3 |              9837.62 |                   -12959.1  |
|      8 |             15395   |    2297.37 |             13097.6 |             22935.2  |                    -5882.91 |
|      9 |             15554.4 |    2343.32 |             13211.1 |             36146.3  |                      725.93 |
|     10 |             15709.6 |    2390.19 |             13319.4 |             49465.7  |                     6895.4  |
|     11 |             15860.1 |    2437.99 |             13422.1 |             62887.8  |                    12651.9  |
|     12 |             16005.5 |    2486.75 |             13518.7 |             76406.5  |                    18020.4  |
|     13 |             16145.3 |    2536.48 |             13608.8 |             90015.3  |                    23024.3  |
|     14 |             16279.1 |    2587.21 |             13691.9 |            103707    |                    27685.9  |
|     15 |             16406.4 |    2638.96 |             13767.5 |            117475    |                    32025.9  |
|     16 |             16526.7 |    2691.74 |             13835   |            131310    |                    36064.2  |
|     17 |             16639.5 |    2745.57 |             13893.9 |            145204    |                    39819.3  |
|     18 |             16744.1 |    2800.48 |             13943.6 |            159147    |                    43308.7  |
|     19 |             16840   |    2856.49 |             13983.5 |            173131    |                    46548.8  |
|     20 |             16926.7 |    2913.62 |             14013   |            187144    |                    49555.3  |

## 6. Sensitivity analysis
### 6.1 CAPEX (multiplier on total CAPEX)

|   capex_multiplier |   total_capex_cad |   npv_cad |   irr_pct |   simple_payback_years |
|-------------------:|------------------:|----------:|----------:|-----------------------:|
|                0.8 |           62647.2 |     65217 |     19.8  |                   5.03 |
|                0.9 |           70478.1 |     57386 |     17.42 |                   5.64 |
|                1   |           78309   |     49555 |     15.47 |                   6.24 |
|                1.1 |           86139.9 |     41724 |     13.82 |                   6.85 |
|                1.2 |           93970.8 |     33894 |     12.41 |                   7.44 |

### 6.2 Electricity rate (multiplier on savings)

|   rate_multiplier |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|------------------:|--------------------:|----------:|----------:|-----------------------:|
|               0.8 |               11351 |     19441 |     11.1  |                   8.07 |
|               0.9 |               12770 |     34498 |     13.33 |                   7.04 |
|               1   |               14188 |     49555 |     15.47 |                   6.24 |
|               1.1 |               15607 |     64612 |     17.53 |                   5.61 |
|               1.2 |               17026 |     79669 |     19.54 |                   5.09 |
|               1.5 |               21283 |    124841 |     25.35 |                   3.99 |

### 6.3 Battery degradation rate

|   battery_degradation_rate |   npv_cad |   irr_pct |   simple_payback_years |
|---------------------------:|----------:|----------:|-----------------------:|
|                       0    |     71331 |     17.46 |                   5.96 |
|                       0.01 |     60443 |     16.51 |                   6.09 |
|                       0.02 |     49555 |     15.47 |                   6.24 |
|                       0.03 |     38667 |     14.3  |                   6.41 |
|                       0.05 |     16891 |     11.38 |                   6.83 |

### 6.4 Discount rate

|   discount_rate |   npv_cad |   irr_pct |   simple_payback_years |
|----------------:|----------:|----------:|-----------------------:|
|            0.04 |    100319 |     15.47 |                   6.24 |
|            0.06 |     71742 |     15.47 |                   6.24 |
|            0.08 |     49555 |     15.47 |                   6.24 |
|            0.1  |     32093 |     15.47 |                   6.24 |
|            0.12 |     18165 |     15.47 |                   6.24 |

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
- Energy rates by TOU period: period 0: 0.02, period 1: 0.09, period 2: 0.27
- Net metering: flat credit (NEM 1.0) @ 0.02 $/kWh

**Solar:** existing 50 kW array, modelled (clear-sky + monthly scaling), ~63,510 kWh/yr. Replace `input_data/solar_production.csv` with measured / PVWatts data when available.

## 8. Limitations

1. **Load data is daily-resolution.** The metered usage workbook repeats a single value across all 24 hours of each day, so the load profile has no intrinsic intraday shape. TOU energy arbitrage is still valued (prices vary intraday) but within-day load peaks and load-following are not represented. Enable `apply_intraday_load_shape` to overlay a generic farm shape.
2. **Solar is modelled, not measured.** PV output is a clear-sky estimate scaled to a typical Ontario capacity factor; actual generation will vary with weather, soiling, shading and array orientation.
3. **Rate covers energy commodity only.** The configured TOU energy rates are modelled with a flat net-metering export credit. Delivery, regulatory, fixed and global-adjustment charges are **not** included; actual bill savings may differ, especially where those charges scale with peak kW/kWh.
4. **Monthly independent optimization.** QuESt BTM optimizes each month separately with a fixed initial state of charge; it does not co-optimize across month boundaries or model ageing within the dispatch.
5. **Degradation & rate sensitivities are linear approximations.** Year-1 savings are scaled by capacity retention and price multipliers rather than re-optimized each year (battery-size cases _are_ re-optimized).
6. **Holiday calendar.** QuESt's schedule builder uses US federal holidays; Ontario statutory holidays differ slightly, marginally affecting which days are billed at weekend (off-peak) rates.
