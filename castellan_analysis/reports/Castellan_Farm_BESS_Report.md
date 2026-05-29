# Castellan Farm — Solar + BESS Project Analysis

_Generated 2026-05-29 using QuESt BTM (engine: **quest**) + project financial model._

> **Currency:** CAD. All results depend on the editable assumptions in `assumptions/` and the curated inputs in `input_data/`. See **Limitations** below before relying on these numbers.

## 1. Headline results

| Metric | Value |
|---|---|
| Total project CAPEX | $78,309 (battery_scope_only) |
| Year-1 total savings | $10,586/yr |
| — PV self-consumption savings | $4,102/yr |
| — Battery dispatch savings | $6,484/yr |
| Annual O&M | $2,000/yr |
| Simple payback | 8.65 years |
| NPV @ 8.0% over 20 yr | $14,040 |
| IRR | 10.2% |
| Avg. monthly peak-demand reduction | -26.4 kW |
| Solar self-consumption (no batt → batt) | 40.0% → 40.1% |

## 2. Battery sizing recommendation

Across the swept range, NPV is maximised at **975 kWh / 112 kW** (NPV $14,644). Existing pack is ~650 kWh; recommendation is the NPV-maximising size across the swept range under current assumptions.

|   battery_kwh |   battery_kw |   battery_savings_cad |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|--------------:|-------------:|----------------------:|--------------------:|----------:|----------:|-----------------------:|
|           325 |        37.5  |                  5413 |                9515 |      3010 |      8.49 |                   9.78 |
|           488 |        56.31 |                  6297 |               10399 |     12114 |      9.93 |                   8.83 |
|           650 |        75    |                  6484 |               10586 |     14040 |     10.23 |                   8.65 |
|           812 |        93.69 |                  6537 |               10640 |     14594 |     10.31 |                   8.6  |
|           975 |       112.5  |                  6542 |               10644 |     14644 |     10.32 |                   8.6  |
|          1300 |       150    |                  6542 |               10644 |     14644 |     10.32 |                   8.6  |

## 3. Energy, savings and demand

- **Annual farm load:** 175,530 kWh (peak 115 kW)
- **Annual PV generation (modelled):** 63,510 kWh
- **Status-quo utility bill (grid only):** $12,982/yr
- **PV-only bill (baseline case):** $8,879/yr
- **PV + battery bill (battery case):** $2,396/yr
- **Annual energy-charge savings (battery):** $6,484/yr
- **Annual demand-charge savings (battery):** $0/yr

> **Peak-demand note:** this tariff has no demand ($/kW) charge, so peak-demand reduction carries **$0** value and the optimizer may even raise peak load while charging off-peak. Set `demand_charge_cad_per_kw` in `assumptions/rate_assumptions.json` (and re-run `prepare_inputs.py`) to value peak shaving on a demand-billed tariff.

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
|      1 |             10585.8 |    2000    |             8585.78 |            -69723.2  |                   -70359.2  |
|      2 |             10748.7 |    2040    |             8708.67 |            -61014.6  |                   -62892.9  |
|      3 |             10911.8 |    2080.8  |             8831    |            -52183.6  |                   -55882.6  |
|      4 |             11075   |    2122.42 |             8952.63 |            -43230.9  |                   -49302.1  |
|      5 |             11238.3 |    2164.86 |             9073.4  |            -34157.5  |                   -43126.9  |
|      6 |             11401.3 |    2208.16 |             9193.15 |            -24964.4  |                   -37333.7  |
|      7 |             11564   |    2252.32 |             9311.7  |            -15652.7  |                   -31900.4  |
|      8 |             11726.2 |    2297.37 |             9428.87 |             -6223.8  |                   -26806.3  |
|      9 |             11887.8 |    2343.32 |             9544.46 |              3320.66 |                   -22031.7  |
|     10 |             12048.5 |    2390.19 |             9658.28 |             12978.9  |                   -17558    |
|     11 |             12208.1 |    2437.99 |             9770.1  |             22749    |                   -13367.8  |
|     12 |             12366.4 |    2486.75 |             9879.69 |             32628.7  |                    -9444.44 |
|     13 |             12523.3 |    2536.48 |             9986.83 |             42615.6  |                    -5772.31 |
|     14 |             12678.5 |    2587.21 |            10091.2  |             52706.8  |                    -2336.63 |
|     15 |             12831.6 |    2638.96 |            10192.7  |             62899.5  |                      876.53 |
|     16 |             12982.6 |    2691.74 |            10290.9  |             73190.4  |                     3880.34 |
|     17 |             13131.1 |    2745.57 |            10385.5  |             83575.9  |                     6687.23 |
|     18 |             13276.8 |    2800.48 |            10476.3  |             94052.2  |                     9308.92 |
|     19 |             13419.4 |    2856.49 |            10562.9  |            104615    |                    11756.5  |
|     20 |             13558.7 |    2913.62 |            10645    |            115260    |                    14040.4  |

## 6. Sensitivity analysis
### 6.1 CAPEX (multiplier on total CAPEX)

|   capex_multiplier |   total_capex_cad |   npv_cad |   irr_pct |   simple_payback_years |
|-------------------:|------------------:|----------:|----------:|-----------------------:|
|                0.8 |           62647.2 |     29702 |     13.62 |                   7    |
|                0.9 |           70478.1 |     21871 |     11.77 |                   7.83 |
|                1   |           78309   |     14040 |     10.23 |                   8.65 |
|                1.1 |           86139.9 |      6209 |      8.91 |                   9.47 |
|                1.2 |           93970.8 |     -1621 |      7.78 |                  10.27 |

### 6.2 Electricity rate (multiplier on savings)

|   rate_multiplier |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|------------------:|--------------------:|----------:|----------:|-----------------------:|
|               0.8 |                8469 |     -8971 |      6.48 |                  11.31 |
|               0.9 |                9527 |      2535 |      8.41 |                   9.8  |
|               1   |               10586 |     14040 |     10.23 |                   8.65 |
|               1.1 |               11644 |     25546 |     11.95 |                   7.75 |
|               1.2 |               12703 |     37052 |     13.6  |                   7.01 |
|               1.5 |               15879 |     71568 |     18.27 |                   5.46 |

### 6.3 Battery degradation rate

|   battery_degradation_rate |   npv_cad |   irr_pct |   simple_payback_years |
|---------------------------:|----------:|----------:|-----------------------:|
|                       0    |     26664 |     11.84 |                   8.19 |
|                       0.01 |     20352 |     11.07 |                   8.4  |
|                       0.02 |     14040 |     10.23 |                   8.65 |
|                       0.03 |      7729 |      9.3  |                   8.94 |
|                       0.05 |     -4895 |      7.05 |                   9.67 |

### 6.4 Discount rate

|   discount_rate |   npv_cad |   irr_pct |   simple_payback_years |
|----------------:|----------:|----------:|-----------------------:|
|            0.04 |     51293 |     10.23 |                   8.65 |
|            0.06 |     30303 |     10.23 |                   8.65 |
|            0.08 |     14040 |     10.23 |                   8.65 |
|            0.1  |      1265 |     10.23 |                   8.65 |
|            0.12 |     -8904 |     10.23 |                   8.65 |

## 7. Assumptions used

**Battery**
- Energy capacity: 650 kWh; power: 75 kW
- Round-trip efficiency: 88%; usable SOC: 10%–90% (80% usable DoD)
- Annual degradation: 2.0%; battery in CAPEX: False (existing pack treated as sunk cost unless set true)

**Financial**
- Discount rate: 8.0%; project life: 20 yr
- Electricity escalation: 3.0%; O&M escalation: 2.0%
- Annual O&M: $2,000; contingency: 10%; PV degradation: 0.5%

**Utility rate** — Castellan actual TOU (CAD/kWh)
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
