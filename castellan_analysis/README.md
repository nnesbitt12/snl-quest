# Castellan Farm — Solar + BESS Project Analysis

A reproducible workflow that evaluates the Castellan Farm behind-the-meter
solar + battery project using **Sandia QuESt BTM** for the dispatch
optimization and a purpose-built **financial model** for project economics.

It answers: how big should the battery be, how much does it save (energy, peak
demand, solar self-consumption), what does it cost (from the BOM), and what are
the payback / NPV / IRR — with sensitivity cases on size, CAPEX, rates,
degradation and discount rate.

---

## 1. How QuESt is used

QuESt 2.0 (this repo) is normally launched as a desktop app with
`python -m quest`. This workflow instead drives QuESt's optimization engine
**headlessly**:

* `scripts/quest_btm_runner.py` imports QuESt's `BtmOptimizer`
  (`quest/snl_libraries/snl_btm/btm/es_gui/tools/btm/btm_optimizer.py`) — the
  same Pyomo linear program behind the QuESt BTM GUI — and runs it
  month-by-month over the project's load, solar, rate and battery inputs.
* QuESt reports each month's bill **with** and **without** energy storage, which
  gives the **battery case** and the **baseline case** directly.
* If QuESt's solver (GLPK) is not installed, the runner falls back to a built-in
  **heuristic** dispatch engine so the workflow still runs (clearly flagged in
  the output; results are approximate and conservative).

Where QuESt is not suitable — CAPEX build-up, escalation, degradation, NPV/IRR,
sensitivities — the separate `financial_model.py` and `sensitivity.py` modules
take over, consuming QuESt's savings as their input.

---

## 2. How to run

```bash
# 0. From the repo root, install dependencies (+ a GLPK solver — see requirements.txt)
pip install -r castellan_analysis/requirements.txt
sudo apt-get install glpk-utils        # or: brew install glpk / conda install glpk

cd castellan_analysis/scripts

# 1. One-time: convert the raw uploads in input_data/raw/ into curated inputs
python prepare_inputs.py

# 2. Run the full analysis (dispatch + financials + sensitivities + report)
python run_analysis.py
```

Outputs land in `../outputs/` and the report in
`../reports/Castellan_Farm_BESS_Report.md`.

### Adjusting the model

Every knob lives in the editable JSON files in `assumptions/` (and the rate
knobs in `rate_assumptions.json`). The most common ones can also be overridden
on the command line:

```bash
python run_analysis.py \
  --battery-kwh 650 --battery-kw 75 --rte 0.88 --degradation 0.02 \
  --installed-cost 330900 --epc-cost 0 --interconnection-cost 0 \
  --engineering-cost 0 --contingency 0.10 \
  --maintenance 2000 --discount-rate 0.08 --project-life 20 --escalation 0.03 \
  --engine quest
```

`python run_analysis.py --help` lists them all. Use `--no-sensitivity` for a
faster run, and `--bom-scenario {current_total,optimized_target,line_items_included}`
to choose the CAPEX basis. After editing `rate_assumptions.json` or the raw
data, re-run `prepare_inputs.py`.

---

## 3. Required input file formats

`prepare_inputs.py` generates these from the raw uploads, but you can also drop
in your own files (same format) and skip straight to `run_analysis.py`.

| File | Format |
|---|---|
| `input_data/farm_load_8760.csv` | Two columns: `datetime, load_kW`. Hourly, one model year (~8760 rows). |
| `input_data/solar_production.csv` | Two columns: `datetime, pv_kW`. Same hourly index as the load. |
| `input_data/bom.csv` | Columns: `category, item, description, qty, scope, necessity, unit_cost, total_cost, capex_opex, included, notes`. `included` is a boolean (CAPEX in/out). Missing `total_cost` is back-filled from `qty * unit_cost`. |
| `input_data/rate_structure.json` | QuESt rate format: `energy rate structure` (12×24 weekday/weekend schedules + `energy rates`), `demand rate structure`, `net metering`. Generated from `assumptions/rate_assumptions.json`. |

The raw source files live in `input_data/raw/`:
the customer interval-usage workbook, the BOM workbook, and the historical-data
PDF.

**Validation / error handling** (`data_loader.py`) raises clear, specific errors
for: missing files or columns, unparseable timestamps (`DateFormatError`),
missing/non-numeric values (`MissingDataError`), BOM line items with no usable
cost (`BomError`), and load/solar series whose intervals don't match or don't
overlap (`IntervalMismatchError`).

---

## 4. Assumptions

All editable; see the `_comment` / `_note` fields inside each file.

* **`assumptions/battery.json`** — energy capacity (kWh), power (kW), round-trip
  efficiency, usable SOC window (depth of discharge), self-discharge, annual
  degradation, and whether/what battery CAPEX and replacement to include. The
  existing ~650 kWh pack is treated as a **sunk cost** (excluded from CAPEX) by
  default, per the BOM.
* **`assumptions/financial.json`** — discount rate, project life, electricity &
  O&M escalation, annual maintenance, PV degradation, BOM scenario, contingency,
  and CAPEX adders/overrides.
* **`assumptions/operating.json`** — model year, solver, engine selection,
  intraday-shape toggle, and the modelled-solar parameters (75 kW, latitude,
  capacity factor, monthly factors).
* **`assumptions/rate_assumptions.json`** — Ontario RPP **Time-of-Use** energy
  rates (off-peak 9.8¢, mid-peak 15.7¢, on-peak 20.3¢; ULO 3.9¢ option),
  seasonal TOU period definitions, an optional `$/kW` demand charge, and net
  metering (flat NEM-1.0 credit by default).

---

## 5. Outputs

Written to `outputs/`:

| File | Contents |
|---|---|
| `summary_metrics.json` | All headline numbers (savings, CAPEX, NPV, IRR, payback, sizing recommendation). |
| `monthly_results.csv` | Per-month bills/energy/demand/NEM and peak kW, with and without the battery. |
| `hourly_dispatch.csv` | 8760-hour dispatch: load, PV, charge, discharge, SOC, net load. |
| `cashflow.csv` | Year-by-year savings, O&M, net & cumulative (discounted) cash flow. |
| `capex_line_items.csv` | BOM items counted in CAPEX. |
| `sensitivity_*.csv` | One file per sweep (battery size, CAPEX, rate, degradation, discount rate). |

And the human-readable report in `reports/Castellan_Farm_BESS_Report.md`
covering headline results, sizing recommendation, energy/savings/demand, CAPEX,
cash flow, sensitivities, assumptions and limitations.

---

## 6. Limitations

1. **Load data is daily-resolution.** The metered workbook repeats one value
   across all 24 hours of each day, so there is no intrinsic intraday load
   shape. TOU energy arbitrage is still valued (prices vary intraday) but
   within-day load peaks / load-following are not represented. Set
   `apply_intraday_load_shape: true` in `operating.json` to overlay a generic
   farm shape (preserving daily energy).
2. **Solar is modelled, not measured.** A clear-sky profile scaled to a typical
   Ontario capacity factor (~14.5%, ~95 MWh/yr for 75 kW). Replace
   `solar_production.csv` with PVWatts or measured data for a firm estimate.
3. **Rate is an assumption.** RPP TOU energy rates with no demand charge and a
   flat net-metering export credit. Delivery, regulatory and global-adjustment
   charges are **not** modelled. Under RPP TOU there is no `$/kW` demand charge,
   so **peak-demand-reduction savings are $0** by default (and the optimizer may
   raise peak load while charging off-peak); set `demand_charge_cad_per_kw` to
   value peak shaving on a demand-billed tariff.
4. **Net-metering modelling.** Default is NEM-1.0 (flat export credit), which
   avoids the unphysical grid-charge-to-export arbitrage that QuESt's NEM-2.0
   (retail-rate export) allows. Ontario net metering's no-cash-profit and
   credit-expiry rules are not enforced exactly.
5. **Monthly independent optimization.** QuESt optimizes each month separately
   from a fixed initial SOC; no cross-month co-optimization or in-dispatch
   ageing.
6. **Linear sensitivity approximations.** Degradation and rate cases scale
   year-1 savings rather than re-optimizing each year; battery-size cases *are*
   re-optimized.
7. **Holiday calendar.** QuESt's scheduler uses US federal holidays; Ontario
   statutory holidays differ slightly, marginally shifting which days bill at
   weekend (off-peak) rates.

---

## 7. Project structure

```
castellan_analysis/
├── input_data/
│   ├── raw/                     # original customer uploads (BOM, usage, PDF)
│   ├── farm_load_8760.csv       # generated hourly load
│   ├── solar_production.csv     # generated 75 kW PV estimate
│   ├── bom.csv                  # structured BOM
│   ├── bom_summary.json         # authoritative BOM totals from the workbook
│   └── rate_structure.json      # QuESt-format rate (generated)
├── assumptions/                 # editable JSON knobs
├── scripts/
│   ├── config.py                # paths & JSON helpers
│   ├── data_loader.py           # loading + validation (error handling)
│   ├── prepare_inputs.py        # raw uploads -> curated inputs
│   ├── quest_btm_runner.py      # QuESt BtmOptimizer wrapper (+ heuristic fallback)
│   ├── financial_model.py       # CAPEX, cash flow, NPV/IRR/payback
│   ├── sensitivity.py           # sensitivity sweeps
│   ├── report.py                # markdown report writer
│   └── run_analysis.py          # orchestrator (CLI)
├── outputs/                     # generated CSV/JSON
├── reports/                     # generated markdown report
└── requirements.txt
```
