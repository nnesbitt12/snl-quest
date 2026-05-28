# Castellan Farm — Solar + BESS Project Analysis

_Generated 2026-05-28 using QuESt BTM (engine: **quest**) + project financial model._

> **Currency:** CAD. All results depend on the editable assumptions in `assumptions/` and the curated inputs in `input_data/`. See **Limitations** below before relying on these numbers.

## 1. Headline results

| Metric | Value |
|---|---|
| Total project CAPEX | $363,990 (current_total) |
| Year-1 total savings | $13,787/yr |
| — PV self-consumption savings | $10,966/yr |
| — Battery dispatch savings | $2,821/yr |
| Annual O&M | $2,000/yr |
| Simple payback | Not within 20 yr |
| NPV @ 8.0% over 20 yr | $-228,637 |
| IRR | -1.9% |
| Avg. monthly peak-demand reduction | -36.4 kW |
| Solar self-consumption (no batt → batt) | 33.3% → 33.4% |

## 2. Battery sizing recommendation

Across the swept range, NPV is maximised at **1300 kWh / 150 kW** (NPV $-227,867). Existing pack is ~650 kWh; recommendation is the NPV-maximising size across the swept range under current assumptions.

|   battery_kwh |   battery_kw |   battery_savings_cad |   year1_savings_cad |   npv_cad |   irr_pct | simple_payback_years   |
|--------------:|-------------:|----------------------:|--------------------:|----------:|----------:|:-----------------------|
|           325 |        37.5  |                  2130 |               13096 |   -235754 |     -2.36 |                        |
|           488 |        56.31 |                  2653 |               13619 |   -230368 |     -2.04 |                        |
|           650 |        75    |                  2821 |               13787 |   -228637 |     -1.94 |                        |
|           812 |        93.69 |                  2869 |               13835 |   -228140 |     -1.91 |                        |
|           975 |       112.5  |                  2889 |               13855 |   -227930 |     -1.9  |                        |
|          1300 |       150    |                  2895 |               13862 |   -227867 |     -1.89 |                        |

## 3. Energy, savings and demand

- **Annual farm load:** 175,530 kWh (peak 115 kW)
- **Annual PV generation (modelled):** 95,265 kWh
- **Status-quo utility bill (grid only):** $22,289/yr
- **PV-only bill (baseline case):** $11,323/yr
- **PV + battery bill (battery case):** $8,503/yr
- **Annual energy-charge savings (battery):** $2,833/yr
- **Annual demand-charge savings (battery):** $0/yr

> **Peak-demand note:** under an Ontario RPP Time-of-Use tariff there is no demand ($/kW) charge, so peak-demand reduction carries **$0** value and the optimizer may even raise peak load while charging off-peak. Set `demand_charge_cad_per_kw` in `assumptions/rate_assumptions.json` (and re-run `prepare_inputs.py`) to value peak shaving on a demand-billed tariff.

## 4. CAPEX (from BOM)

| Component | CAD |
|---|---|
| BOM base (current_total) | $330,900 |
| Battery (new) | $0 |
| Adders (EPC / interconnection / engineering / other) | $0 |
| Contingency | $33,090 |
| **Total CAPEX** | **$363,990** |

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
|      1 |             13786.8 |    2000    |             11786.8 |            -352203   |                     -353076 |
|      2 |             14085.8 |    2040    |             12045.8 |            -340157   |                     -342749 |
|      3 |             14390.4 |    2080.8  |             12309.6 |            -327848   |                     -332977 |
|      4 |             14700.5 |    2122.42 |             12578.1 |            -315270   |                     -323732 |
|      5 |             15016.4 |    2164.86 |             12851.5 |            -302418   |                     -314985 |
|      6 |             15337.9 |    2208.16 |             13129.7 |            -289288   |                     -306711 |
|      7 |             15665.2 |    2252.32 |             13412.9 |            -275876   |                     -298885 |
|      8 |             15998.3 |    2297.37 |             13701   |            -262175   |                     -291483 |
|      9 |             16337.4 |    2343.32 |             13994   |            -248181   |                     -284482 |
|     10 |             16682.3 |    2390.19 |             14292.1 |            -233888   |                     -277862 |
|     11 |             17033.3 |    2437.99 |             14595.3 |            -219293   |                     -271603 |
|     12 |             17390.3 |    2486.75 |             14903.6 |            -204389   |                     -265684 |
|     13 |             17753.4 |    2536.48 |             15216.9 |            -189173   |                     -260089 |
|     14 |             18122.7 |    2587.21 |             15535.5 |            -173637   |                     -254800 |
|     15 |             18498.1 |    2638.96 |             15859.1 |            -157778   |                     -249800 |
|     16 |             18879.7 |    2691.74 |             16188   |            -141590   |                     -245075 |
|     17 |             19267.6 |    2745.57 |             16522   |            -125068   |                     -240610 |
|     18 |             19661.7 |    2800.48 |             16861.3 |            -108207   |                     -236390 |
|     19 |             20062.2 |    2856.49 |             17205.7 |             -91001   |                     -232404 |
|     20 |             20469   |    2913.62 |             17555.4 |             -73445.6 |                     -228637 |

## 6. Sensitivity analysis
### 6.1 CAPEX (multiplier on total CAPEX)

|   capex_multiplier |   total_capex_cad |   npv_cad |   irr_pct | simple_payback_years   |
|-------------------:|------------------:|----------:|----------:|:-----------------------|
|                0.8 |            291192 |   -155839 |     -0.02 |                        |
|                0.9 |            327591 |   -192238 |     -1.05 |                        |
|                1   |            363990 |   -228637 |     -1.94 |                        |
|                1.1 |            400389 |   -265036 |     -2.72 |                        |
|                1.2 |            436788 |   -301435 |     -3.41 |                        |

### 6.2 Electricity rate (multiplier on savings)

|   rate_multiplier |   year1_savings_cad |   npv_cad |   irr_pct |   simple_payback_years |
|------------------:|--------------------:|----------:|----------:|-----------------------:|
|               0.8 |               11029 |   -260249 |     -4.06 |                 nan    |
|               0.9 |               12408 |   -244443 |     -2.95 |                 nan    |
|               1   |               13787 |   -228637 |     -1.94 |                 nan    |
|               1.1 |               15165 |   -212831 |     -1.01 |                 nan    |
|               1.2 |               16544 |   -197025 |     -0.14 |                 nan    |
|               1.5 |               20680 |   -149607 |      2.19 |                  16.45 |

### 6.3 Battery degradation rate

|   battery_degradation_rate |   npv_cad |   irr_pct | simple_payback_years   |
|---------------------------:|----------:|----------:|:-----------------------|
|                       0    |   -223145 |     -1.47 |                        |
|                       0.01 |   -225891 |     -1.7  |                        |
|                       0.02 |   -228637 |     -1.94 |                        |
|                       0.03 |   -231383 |     -2.18 |                        |
|                       0.05 |   -236875 |     -2.7  |                        |

### 6.4 Discount rate

|   discount_rate |   npv_cad |   irr_pct | simple_payback_years   |
|----------------:|----------:|----------:|:-----------------------|
|            0.04 |   -171861 |     -1.94 |                        |
|            0.06 |   -203917 |     -1.94 |                        |
|            0.08 |   -228637 |     -1.94 |                        |
|            0.1  |   -247962 |     -1.94 |                        |
|            0.12 |   -263273 |     -1.94 |                        |

## 7. Assumptions used

**Battery**
- Energy capacity: 650 kWh; power: 75 kW
- Round-trip efficiency: 88%; usable SOC: 10%–90% (80% usable DoD)
- Annual degradation: 2.0%; battery in CAPEX: False (existing pack treated as sunk cost unless set true)

**Financial**
- Discount rate: 8.0%; project life: 20 yr
- Electricity escalation: 3.0%; O&M escalation: 2.0%
- Annual O&M: $2,000; contingency: 10%; PV degradation: 0.5%

**Utility rate** (Ontario RPP Time-of-Use, CAD/kWh)
- Off-peak 0.098, mid-peak 0.157, on-peak 0.203
- Net metering: flat credit (NEM 1.0) @ 0.098 $/kWh

**Solar:** modelled 75 kW Ontario array (clear-sky + monthly scaling), ~95,265 kWh/yr. Replace `input_data/solar_production.csv` with measured / PVWatts data when available.

## 8. Limitations

1. **Load data is daily-resolution.** The metered usage workbook repeats a single value across all 24 hours of each day, so the load profile has no intrinsic intraday shape. TOU energy arbitrage is still valued (prices vary intraday) but within-day load peaks and load-following are not represented. Enable `apply_intraday_load_shape` to overlay a generic farm shape.
2. **Solar is modelled, not measured.** PV output is a clear-sky estimate scaled to a typical Ontario capacity factor; actual generation will vary with weather, soiling, shading and array orientation.
3. **Rate is an assumption.** Ontario RPP TOU energy rates were used with no demand charge; net metering is modelled as a flat export credit. Confirm the site's actual tariff, including any global adjustment, delivery and regulatory charges, which are not modelled here.
4. **Monthly independent optimization.** QuESt BTM optimizes each month separately with a fixed initial state of charge; it does not co-optimize across month boundaries or model ageing within the dispatch.
5. **Degradation & rate sensitivities are linear approximations.** Year-1 savings are scaled by capacity retention and price multipliers rather than re-optimized each year (battery-size cases _are_ re-optimized).
6. **Holiday calendar.** QuESt's schedule builder uses US federal holidays; Ontario statutory holidays differ slightly, marginally affecting which days are billed at weekend (off-peak) rates.
