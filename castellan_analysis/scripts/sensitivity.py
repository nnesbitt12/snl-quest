"""
Sensitivity analysis for the Castellan Farm project.

Each function returns a tidy DataFrame so the cases can be written to CSV and
summarised in the report. Cases covered (per the brief):

* battery size      - re-runs QuESt dispatch at each energy/power point
* CAPEX             - scales total CAPEX (no dispatch re-run needed)
* electricity rate  - scales year-1 savings by a rate multiplier (bill ~ linear in price)
* degradation       - varies the battery annual degradation rate
* discount rate     - varies the discount rate (re-discounts the same cashflows)

Battery-size sweeps re-run the optimization; the others re-use the year-1
savings and only rebuild the financial pro-forma, which keeps run time low.
"""
from __future__ import annotations

import copy
from typing import List

import pandas as pd

import financial_model as fm
import quest_btm_runner as qbtm


def _proforma_metrics(capex, pv_sav, batt_sav, financial, battery) -> dict:
    res = fm.build_proforma(capex, pv_sav, batt_sav, financial, battery)
    return {
        "year1_savings_cad": round(pv_sav + batt_sav, 0),
        "npv_cad": round(res.npv_cad, 0),
        "irr_pct": res.metrics["irr_pct"],
        "simple_payback_years": res.metrics["simple_payback_years"],
    }


def sweep_battery_size(load, solar, rate, base_ess, operating, capex,
                       financial, battery, kwh_points: List[float]) -> pd.DataFrame:
    """Re-run dispatch for a range of battery energy capacities (kWh).

    Power scales with the base C-rate so the duration stays constant.
    """
    base_kwh = float(base_ess["Energy_capacity"])
    base_kw = float(base_ess["Power_rating"])
    c_rate = base_kw / base_kwh if base_kwh else 0.1

    rows = []
    for kwh in kwh_points:
        ess = dict(base_ess)
        ess["Energy_capacity"] = float(kwh)
        ess["Power_rating"] = round(float(kwh) * c_rate, 2)
        dec = qbtm.run_decomposed(load, solar, rate, ess, operating)
        m = _proforma_metrics(capex, dec.pv_savings, dec.battery_savings,
                              financial, battery)
        m.update({"battery_kwh": kwh, "battery_kw": ess["Power_rating"],
                  "battery_savings_cad": round(dec.battery_savings, 0)})
        rows.append(m)
    return pd.DataFrame(rows)[
        ["battery_kwh", "battery_kw", "battery_savings_cad",
         "year1_savings_cad", "npv_cad", "irr_pct", "simple_payback_years"]
    ]


def sweep_capex(capex, pv_sav, batt_sav, financial, battery,
                multipliers: List[float]) -> pd.DataFrame:
    """Scale total CAPEX by each multiplier and recompute the pro-forma."""
    rows = []
    for mult in multipliers:
        c = dict(capex)
        c["total_capex_cad"] = round(capex["total_capex_cad"] * mult, 2)
        m = _proforma_metrics(c, pv_sav, batt_sav, financial, battery)
        m.update({"capex_multiplier": mult, "total_capex_cad": c["total_capex_cad"]})
        rows.append(m)
    return pd.DataFrame(rows)[
        ["capex_multiplier", "total_capex_cad", "npv_cad", "irr_pct",
         "simple_payback_years"]
    ]


def sweep_rate(capex, pv_sav, batt_sav, financial, battery,
               multipliers: List[float]) -> pd.DataFrame:
    """Scale year-1 savings by an electricity-price multiplier."""
    rows = []
    for mult in multipliers:
        m = _proforma_metrics(capex, pv_sav * mult, batt_sav * mult,
                              financial, battery)
        m.update({"rate_multiplier": mult})
        rows.append(m)
    return pd.DataFrame(rows)[
        ["rate_multiplier", "year1_savings_cad", "npv_cad", "irr_pct",
         "simple_payback_years"]
    ]


def sweep_degradation(capex, pv_sav, batt_sav, financial, battery,
                      rates: List[float]) -> pd.DataFrame:
    """Vary the battery annual degradation rate."""
    rows = []
    for deg in rates:
        b = dict(battery)
        b["annual_degradation_rate"] = deg
        m = _proforma_metrics(capex, pv_sav, batt_sav, financial, b)
        m.update({"battery_degradation_rate": deg})
        rows.append(m)
    return pd.DataFrame(rows)[
        ["battery_degradation_rate", "npv_cad", "irr_pct", "simple_payback_years"]
    ]


def sweep_discount_rate(capex, pv_sav, batt_sav, financial, battery,
                        rates: List[float]) -> pd.DataFrame:
    """Vary the discount rate and recompute NPV/IRR/payback."""
    rows = []
    for r in rates:
        f = copy.deepcopy(financial)
        f["discount_rate"] = r
        m = _proforma_metrics(capex, pv_sav, batt_sav, f, battery)
        m.update({"discount_rate": r})
        rows.append(m)
    return pd.DataFrame(rows)[
        ["discount_rate", "npv_cad", "irr_pct", "simple_payback_years"]
    ]
