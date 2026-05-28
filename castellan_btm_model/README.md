# Castellan BESS — Sandia QuESt BTM model (filled out)

Behind-the-Meter (BTM) **Cost-Savings** model for account **200027805928**
(Cara Castellan), built from the customer's own interval data and bills and
runnable with Sandia QuESt's `BtmOptimizer`.

## What's in here

| File | Purpose |
|------|---------|
| `castellan_load_2025.csv` | Load profile — calendar year **2025** (8,760 hourly kW), the most recent complete 12 months in the interval export. QuESt format: `Date/Time`, `Electricity:Facility [kW](Hourly)`. |
| `castellan_ontario_gs50_rate.json` | Rate structure in QuESt BTM schema — **energy $0.1109/kWh** (single flat period) and a **flat non-coincident demand charge of $25.84/kW-month** in every month. No TOU energy/demand periods, no net metering. |
| `ZeroPV_castellan.json` | "No solar" PV profile (8,760 zeros) in QuESt's PVWatts-style schema. |
| `ess_params.json` | Four battery configurations (power/energy + RTE 0.90, SOC 10–90%, init 50%). |
| `run_castellan_btm.py` | Driver that runs QuESt's `BtmOptimizer` month-by-month for each config and writes results CSVs. |

## How the inputs were derived

* **Load** — 16,248 hrs of metered interval data (Jul 2024–May 2026). Calendar
  2025 is gap-free (8,760 hrs), peak 114.9 kW, 224,726 kWh — used as the
  representative year. The load is a strong winter-heating profile (summer ≈ 1/10
  of winter), and winter peaks are sustained plateaus (avg 6.8 h, up to 72 h
  above 60 kW), so the battery is **energy-limited, not power-limited**.
* **Rate** — reverse-engineered from 22 monthly bills by regressing
  `new charges = a·kWh + b·peak_kW + fixed`. Fit is essentially exact
  (**R² = 0.9994**): energy **$0.1109/kWh**, demand **$25.84/kW-month**,
  fixed ≈ $137/month (fixed charge is omitted from the model — it doesn't change
  with a BESS). ⚠️ Confirm the $25.84/kW figure and whether billed demand is kW
  or 15-min kVA against the actual tariff sheet; it is the single biggest driver
  of value.

## Results (QuESt `BtmOptimizer`, GLPK)

Modeled annual bill **without** BESS (energy + demand only): **$42,688**.

| Config | Annual savings | of which demand |
|--------|---------------:|----------------:|
| Entry — 30 kW / 60 kWh | **$3,624** | $3,646 |
| Value — 50 kW / 150 kWh | **$5,646** | $5,719 |
| Balanced — 100 kW / 200 kWh | **$6,219** | $6,314 |
| Deep-shave — 100 kW / 300 kWh | **$6,858** | $6,977 |

Savings come almost entirely from **demand-charge reduction** — the flat energy
rate leaves no arbitrage value. Returns diminish sharply with energy capacity:
the first 60 kWh captures ~53% of the deep-shave savings.

## Run it

```bash
# needs pyomo + a solver on PATH (glpk -> glpsol)
python run_castellan_btm.py
```

Outputs `results_summary.csv` and a per-config monthly breakdown
(`results_<Config>.csv`) with `bill_no_es`, `bill_es`, `demand_*`, `energy_*`.

In the **QuESt GUI / flow** (`master_btm_flow_2026_program.py`), point the flow
inputs at these files instead:
`load_path → castellan_load_2025.csv`, `rate_path → castellan_ontario_gs50_rate.json`,
`pv_path → ZeroPV_castellan.json`, and set `power`/`energy`/`rte` per config.
