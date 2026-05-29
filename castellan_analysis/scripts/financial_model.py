"""
Financial model for the Castellan Farm project.

QuESt BTM produces the operational savings (the avoided utility bill). This
module wraps those savings in a project pro-forma: it builds CAPEX from the BOM,
escalates annual savings, applies battery/PV degradation and O&M, optionally
schedules a battery replacement, and computes simple payback, NPV and IRR.

Savings are decomposed into a PV contribution and a battery contribution so
each can degrade at its own rate:

* PV savings      = (status-quo grid-only bill) - (PV-only bill)
* battery savings = (PV-only bill)              - (PV + battery bill)

The project pro-forma evaluates the full upgrade (PV + integration CAPEX) versus
the status-quo bill. The existing ~650 kWh battery is treated as a sunk cost
unless ``battery_capex_included`` is set in battery.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# CAPEX
# ---------------------------------------------------------------------------
def compute_capex(bom_df: pd.DataFrame, bom_summary: dict,
                  financial: dict, battery: dict) -> Dict[str, float]:
    """Compute total project CAPEX from the BOM plus adders and contingency."""
    overrides = financial.get("capex_overrides", {})
    installed_override = overrides.get("installed_cost_cad")

    inc = bom_df[bom_df["included"]]
    if installed_override is not None:
        base = float(installed_override)
        source = "installed_cost_override"
    else:
        scenario = financial.get("bom_scenario", "current_total")
        if scenario == "current_total":
            base = float(bom_summary.get("active_bom_total_cad") or 0.0)
        elif scenario == "optimized_target":
            base = float(bom_summary.get("optimized_target_cad") or 0.0)
        elif scenario == "battery_scope_only":
            base = float(inc.loc[inc["scope"] == "BATTERY", "total_cost"].sum())
        elif scenario == "bess_less_solar":
            base = float(inc.loc[inc["scope"] != "PV", "total_cost"].sum())
        else:  # line_items_included
            base = float(inc["total_cost"].sum())
        source = scenario

    battery_capex = (
        float(battery.get("battery_capex_cad", 0.0))
        if battery.get("battery_capex_included") else 0.0
    )
    adders = (
        float(overrides.get("epc_install_cost_cad", 0.0))
        + float(overrides.get("interconnection_cost_cad", 0.0))
        + float(overrides.get("engineering_cost_cad", 0.0))
        + float(overrides.get("other_adders_cad", 0.0))
    )
    subtotal = base + battery_capex + adders
    contingency = subtotal * float(financial.get("contingency_pct", 0.0))
    pre_itc = subtotal + contingency
    itc_rate = float(financial.get("itc_rate", 0.0))
    itc = pre_itc * itc_rate
    total = pre_itc - itc
    return {
        "bom_base_cad": round(base, 2),
        "bom_scenario": source,
        "battery_capex_cad": round(battery_capex, 2),
        "adders_cad": round(adders, 2),
        "contingency_cad": round(contingency, 2),
        "pre_itc_capex_cad": round(pre_itc, 2),
        "itc_rate": itc_rate,
        "itc_credit_cad": round(itc, 2),
        "total_capex_cad": round(total, 2),
    }


# ---------------------------------------------------------------------------
# IRR / NPV helpers
# ---------------------------------------------------------------------------
def npv(rate: float, cashflows) -> float:
    """Net present value of a cashflow list where cashflows[0] is at t=0."""
    return float(sum(cf / (1.0 + rate) ** t for t, cf in enumerate(cashflows)))


def irr(cashflows, lo: float = -0.95, hi: float = 10.0) -> Optional[float]:
    """Internal rate of return via bisection; None if no sign change / no root."""
    if npv(lo, cashflows) * npv(hi, cashflows) > 0:
        return None  # IRR not bracketed (e.g. project never pays back)
    for _ in range(200):
        mid = (lo + hi) / 2.0
        val = npv(mid, cashflows)
        if abs(val) < 1e-6:
            return mid
        if npv(lo, cashflows) * val < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# Pro-forma
# ---------------------------------------------------------------------------
@dataclass
class FinancialResults:
    capex: Dict[str, float]
    cashflow_table: pd.DataFrame
    npv_cad: float
    irr: Optional[float]
    simple_payback_years: Optional[float]
    year1_savings_cad: float
    metrics: Dict[str, float]


def _simple_payback(capex: float, undiscounted_net_by_year) -> Optional[float]:
    """Year at which cumulative undiscounted net cash flow recovers CAPEX."""
    cumulative = 0.0
    prev = 0.0
    for year, net in enumerate(undiscounted_net_by_year, start=1):
        cumulative += net
        if cumulative >= capex:
            # Linear interpolation within the recovery year.
            needed = capex - prev
            return (year - 1) + (needed / net if net > 0 else 0.0)
        prev = cumulative
    return None  # not recovered within the project life


def build_proforma(capex: Dict[str, float],
                   pv_savings_y1: float,
                   battery_savings_y1: float,
                   financial: dict,
                   battery: dict) -> FinancialResults:
    """Construct the year-by-year cashflow table and headline metrics."""
    n = int(financial.get("project_life_years", 20))
    r = float(financial.get("discount_rate", 0.08))
    esc = float(financial.get("electricity_escalation_rate", 0.03))
    opex0 = float(financial.get("annual_maintenance_cad", 0.0))
    opex_esc = float(financial.get("opex_escalation_rate", 0.0))
    batt_deg = float(battery.get("annual_degradation_rate", 0.0))
    pv_deg = float(financial.get("pv_degradation_rate", 0.0))
    repl_year = int(battery.get("replacement_year", 0) or 0)
    repl_cost = float(battery.get("replacement_cost_cad", 0.0))
    total_capex = float(capex["total_capex_cad"])

    rows = []
    discounted_cfs = [-total_capex]  # t = 0
    undiscounted_net = []
    for y in range(1, n + 1):
        batt_ret = max(0.0, 1.0 - batt_deg * (y - 1))
        pv_ret = max(0.0, 1.0 - pv_deg * (y - 1))
        esc_f = (1.0 + esc) ** (y - 1)
        pv_sav = pv_savings_y1 * pv_ret * esc_f
        batt_sav = battery_savings_y1 * batt_ret * esc_f
        savings = pv_sav + batt_sav
        opex = opex0 * (1.0 + opex_esc) ** (y - 1)
        replacement = repl_cost if (repl_year and y == repl_year) else 0.0
        net = savings - opex - replacement
        disc = net / (1.0 + r) ** y
        discounted_cfs.append(net)
        undiscounted_net.append(net)
        rows.append({
            "year": y,
            "pv_savings_cad": round(pv_sav, 2),
            "battery_savings_cad": round(batt_sav, 2),
            "gross_savings_cad": round(savings, 2),
            "opex_cad": round(opex, 2),
            "replacement_cad": round(replacement, 2),
            "net_cash_flow_cad": round(net, 2),
            "discounted_cash_flow_cad": round(disc, 2),
        })

    table = pd.DataFrame(rows)
    table["cumulative_net_cad"] = table["net_cash_flow_cad"].cumsum() - total_capex
    table["cumulative_discounted_cad"] = (
        table["discounted_cash_flow_cad"].cumsum() - total_capex
    )

    project_npv = npv(r, discounted_cfs)
    project_irr = irr(discounted_cfs)
    payback = _simple_payback(total_capex, undiscounted_net)

    metrics = {
        "total_capex_cad": round(total_capex, 2),
        "year1_savings_cad": round(pv_savings_y1 + battery_savings_y1, 2),
        "npv_cad": round(project_npv, 2),
        "irr_pct": round(project_irr * 100, 2) if project_irr is not None else None,
        "simple_payback_years": round(payback, 2) if payback is not None else None,
        "discount_rate_pct": round(r * 100, 2),
        "project_life_years": n,
    }
    return FinancialResults(
        capex=capex,
        cashflow_table=table,
        npv_cad=project_npv,
        irr=project_irr,
        simple_payback_years=payback,
        year1_savings_cad=pv_savings_y1 + battery_savings_y1,
        metrics=metrics,
    )
