"""
Run the Sandia QuESt BTM (Behind-the-Meter) Cost-Savings model for the
Castellan account (200027805928), filled out with the customer's own
interval data and a rate structure derived from 22 months of bills.

It drives QuESt's own `BtmOptimizer` (quest/snl_libraries/snl_btm) month by
month for each battery configuration and reports the demand-charge,
energy-charge and total-bill savings, exactly as the QuESt BTM tool would.

Requires: pyomo + a MILP/LP solver (glpk -> `glpsol`).
Usage:    python run_castellan_btm.py
"""
import os, sys, json
import pandas as pd, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
# Make the QuESt BTM package importable (it is rooted at .../snl_btm)
sys.path.insert(0, os.path.join(REPO, 'quest', 'snl_libraries', 'snl_btm'))

from btm.es_gui.tools.btm.btm_optimizer import BtmOptimizer


def read_load_profile(path, month):
    """Month slice of an 8760-hr annual load CSV (col 0 = datetime, col -1 = kW).
    Mirrors QuESt's readutdata.read_load_profile: the datetime column is
    overwritten with a 2019 hourly range and filtered by calendar month."""
    load_df = pd.read_csv(path)
    data_col = load_df.columns[-1]
    idx = pd.date_range(start='2019-01-01 00:00', periods=len(load_df), freq='h')
    return load_df.loc[idx.month == int(month), data_col].values

LOAD_CSV = os.path.join(HERE, 'castellan_load_2025.csv')
RATE_JSON = os.path.join(HERE, 'castellan_ontario_gs50_rate.json')
ESS_JSON = os.path.join(HERE, 'ess_params.json')
SOLVER = 'glpk'

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def build_month_schedule(rate, month_idx, n_hours):
    """Replicate QuESt's per-month hourly schedule from the 12x24 rate tables.
    For this rate everything is a single period, so schedules are all zeros,
    but we build them generically so the file stays faithful to QuESt."""
    e_wk = rate['energy rate structure']['weekday schedule'][month_idx]
    d_wk = rate['demand rate structure']['weekday schedule'][month_idx]
    days = n_hours // 24
    tou_e = []
    tou_d = []
    for _ in range(days):
        tou_e.extend(e_wk)
        tou_d.extend(d_wk)
    return tou_e[:n_hours], tou_d[:n_hours]


def run_config(ess, rate):
    rows = []
    for mi, mname in enumerate(MONTHS):
        load = read_load_profile(LOAD_CSV, mi + 1)
        n = len(load)
        tou_e_sch, tou_d_sch = build_month_schedule(rate, mi, n)

        energy_rates = rate['energy rate structure']['energy rates']
        demand_tou_rates = rate['demand rate structure']['time of use rates']
        flat_rate = rate['demand rate structure']['flat rates'][mname]

        opt = BtmOptimizer(solver=SOLVER)
        opt.tou_energy_schedule = tou_e_sch
        opt.tou_energy_rate = [energy_rates[str(k)] for k in range(len(energy_rates))]
        opt.tou_demand_schedule = tou_d_sch
        opt.tou_demand_rate = [demand_tou_rates[str(k)] for k in range(len(demand_tou_rates))]
        opt.flat_demand_rate = flat_rate
        opt.load_profile = list(load)
        opt.pv_profile = [0.0] * n
        opt.nem_type = 0
        opt.nem_rate = 0.0

        # ESS parameters (set on the Pyomo model, as QuESt's handler does)
        opt.set_model_parameters(
            Power_rating=ess['Power_rating'],
            Energy_capacity=ess['Energy_capacity'],
            Round_trip_efficiency=ess['Round_trip_efficiency'],
            Transformer_rating=ess['Transformer_rating'],
            State_of_charge_min=ess['State_of_charge_min'],
            State_of_charge_max=ess['State_of_charge_max'],
            State_of_charge_init=ess['State_of_charge_init'],
        )

        opt.run()
        rows.append({
            'month': mname,
            'bill_no_es': opt.total_bill_without_es,
            'bill_es': opt.total_bill_with_es,
            'demand_no_es': opt.demand_charge_without_es,
            'demand_es': opt.demand_charge_with_es,
            'energy_no_es': opt.energy_charge_without_es,
            'energy_es': opt.energy_charge_with_es,
        })
    return pd.DataFrame(rows)


def main():
    rate = json.load(open(RATE_JSON))
    ess_configs = json.load(open(ESS_JSON))
    print(f"QuESt BTM Cost-Savings  |  rate: {rate['name']}  |  solver: {SOLVER}\n")
    summary = []
    for ess in ess_configs:
        df = run_config(ess, rate)
        save = df['bill_no_es'].sum() - df['bill_es'].sum()
        dsave = df['demand_no_es'].sum() - df['demand_es'].sum()
        print(f"=== {ess['label']} (RTE {ess['Round_trip_efficiency']}) ===")
        print(f"    Annual bill  without BESS : ${df['bill_no_es'].sum():,.0f}")
        print(f"    Annual bill  with    BESS : ${df['bill_es'].sum():,.0f}")
        print(f"    Annual SAVINGS            : ${save:,.0f}  (demand ${dsave:,.0f})\n")
        summary.append({'config': ess['label'], 'annual_savings': round(save),
                        'demand_savings': round(dsave)})
        df.to_csv(os.path.join(HERE, f"results_{ess['label'].split()[0]}.csv"), index=False)
    pd.DataFrame(summary).to_csv(os.path.join(HERE, 'results_summary.csv'), index=False)
    print("Wrote results_summary.csv and per-config monthly CSVs.")


if __name__ == '__main__':
    main()
