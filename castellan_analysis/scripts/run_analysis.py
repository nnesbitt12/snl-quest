"""
End-to-end Castellan Farm BESS analysis runner.

Loads the curated inputs, runs the QuESt behind-the-meter dispatch optimization
(baseline vs. battery), builds the financial pro-forma and sensitivity cases,
then writes CSV outputs and a markdown report.

Usage
-----
    python scripts/prepare_inputs.py        # one-time: build input_data/
    python scripts/run_analysis.py          # run the full analysis

Common overrides (anything not passed falls back to the assumption files)::

    python scripts/run_analysis.py \
        --battery-kwh 650 --battery-kw 75 \
        --discount-rate 0.08 --project-life 20 \
        --escalation 0.03 --degradation 0.02 \
        --installed-cost 330900 --contingency 0.10 \
        --maintenance 2000 --engine quest

Run ``python scripts/run_analysis.py --help`` for the full list.
"""
from __future__ import annotations

import argparse
import json
import logging

import pandas as pd

import config
import data_loader as dl
import financial_model as fm
import quest_btm_runner as qbtm
import sensitivity as sens
from report import write_report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Castellan Farm BESS analysis")
    # Battery
    p.add_argument("--battery-kwh", type=float, help="Battery energy capacity (kWh)")
    p.add_argument("--battery-kw", type=float, help="Battery power rating (kW)")
    p.add_argument("--rte", type=float, help="Round-trip efficiency (0-1)")
    p.add_argument("--degradation", type=float, help="Battery annual degradation rate (0-1)")
    # CAPEX
    p.add_argument("--installed-cost", type=float, help="Override total installed cost (CAD)")
    p.add_argument("--epc-cost", type=float, help="EPC / installation adder (CAD)")
    p.add_argument("--interconnection-cost", type=float, help="Interconnection adder (CAD)")
    p.add_argument("--engineering-cost", type=float, help="Engineering adder (CAD)")
    p.add_argument("--contingency", type=float, help="Contingency fraction (0-1)")
    p.add_argument("--bom-scenario", choices=["current_total", "optimized_target", "line_items_included"])
    # Financial
    p.add_argument("--maintenance", type=float, help="Annual O&M (CAD)")
    p.add_argument("--discount-rate", type=float, help="Discount rate (0-1)")
    p.add_argument("--project-life", type=int, help="Project life (years)")
    p.add_argument("--escalation", type=float, help="Electricity escalation rate (0-1)")
    # Operating
    p.add_argument("--engine", choices=["auto", "quest", "heuristic"], help="Dispatch engine")
    p.add_argument("--no-sensitivity", action="store_true", help="Skip sensitivity sweeps")
    return p.parse_args()


def apply_overrides(args, battery, financial, operating) -> None:
    """Mutate the assumption dicts in place with any CLI overrides."""
    if args.battery_kwh is not None:
        battery["energy_capacity_kwh"] = args.battery_kwh
    if args.battery_kw is not None:
        battery["power_rating_kw"] = args.battery_kw
    if args.rte is not None:
        battery["round_trip_efficiency"] = args.rte
    if args.degradation is not None:
        battery["annual_degradation_rate"] = args.degradation

    ov = financial.setdefault("capex_overrides", {})
    if args.installed_cost is not None:
        ov["installed_cost_cad"] = args.installed_cost
    if args.epc_cost is not None:
        ov["epc_install_cost_cad"] = args.epc_cost
    if args.interconnection_cost is not None:
        ov["interconnection_cost_cad"] = args.interconnection_cost
    if args.engineering_cost is not None:
        ov["engineering_cost_cad"] = args.engineering_cost
    if args.contingency is not None:
        financial["contingency_pct"] = args.contingency
    if args.bom_scenario is not None:
        financial["bom_scenario"] = args.bom_scenario
    if args.maintenance is not None:
        financial["annual_maintenance_cad"] = args.maintenance
    if args.discount_rate is not None:
        financial["discount_rate"] = args.discount_rate
    if args.project_life is not None:
        financial["project_life_years"] = args.project_life
    if args.escalation is not None:
        financial["electricity_escalation_rate"] = args.escalation

    if args.engine is not None:
        operating["engine"] = args.engine


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    args = parse_args()
    config.ensure_output_dirs()

    # --- assumptions -------------------------------------------------------
    battery = config.load_json(config.BATTERY_JSON)
    financial = config.load_json(config.FINANCIAL_JSON)
    operating = config.load_json(config.OPERATING_JSON)
    bom_summary = config.load_json(config.INPUT_DIR / "bom_summary.json")
    apply_overrides(args, battery, financial, operating)

    # --- inputs ------------------------------------------------------------
    load = dl.load_load_profile()
    solar = dl.load_solar_profile()
    load, solar = dl.align_load_and_solar(load, solar)
    rate = dl.load_rate_structure()
    bom = dl.load_bom()
    ess = qbtm.battery_params_from_assumptions(battery)

    print(f"Inputs: load {load.sum():,.0f} kWh/yr (peak {load.max():,.0f} kW), "
          f"PV {solar.sum():,.0f} kWh/yr, battery {battery['energy_capacity_kwh']:.0f} kWh "
          f"/ {battery['power_rating_kw']:.0f} kW")

    # --- dispatch (baseline vs battery) -----------------------------------
    print("Running QuESt behind-the-meter dispatch (status quo, PV-only, PV+battery)...")
    dec = qbtm.run_decomposed(load, solar, rate, ess, operating)
    proj = dec.project_results
    sc = proj.solar_self_consumption()
    print(f"  Engine: {proj.engine}")
    print(f"  Status-quo bill: ${dec.status_quo_bill:,.0f} | "
          f"PV-only: ${dec.pv_only_bill:,.0f} | PV+battery: ${dec.project_bill:,.0f}")
    print(f"  PV savings ${dec.pv_savings:,.0f}/yr | "
          f"Battery savings ${dec.battery_savings:,.0f}/yr | "
          f"Total ${dec.total_savings:,.0f}/yr")

    # --- financials --------------------------------------------------------
    capex = fm.compute_capex(bom, bom_summary, financial, battery)
    fin = fm.build_proforma(capex, dec.pv_savings, dec.battery_savings, financial, battery)
    print(f"  CAPEX: ${capex['total_capex_cad']:,.0f} ({capex['bom_scenario']}) | "
          f"NPV: ${fin.npv_cad:,.0f} | "
          f"IRR: {fin.metrics['irr_pct']}% | "
          f"Payback: {fin.metrics['simple_payback_years']} yr")

    # --- sensitivity -------------------------------------------------------
    sensitivities = {}
    if not args.no_sensitivity:
        print("Running sensitivity sweeps...")
        base_kwh = float(ess["Energy_capacity"])
        sizes = sorted({round(base_kwh * f) for f in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)})
        sensitivities["battery_size"] = sens.sweep_battery_size(
            load, solar, rate, ess, operating, capex, financial, battery, sizes)
        sensitivities["capex"] = sens.sweep_capex(
            capex, dec.pv_savings, dec.battery_savings, financial, battery,
            [0.8, 0.9, 1.0, 1.1, 1.2])
        sensitivities["electricity_rate"] = sens.sweep_rate(
            capex, dec.pv_savings, dec.battery_savings, financial, battery,
            [0.8, 0.9, 1.0, 1.1, 1.2, 1.5])
        sensitivities["degradation"] = sens.sweep_degradation(
            capex, dec.pv_savings, dec.battery_savings, financial, battery,
            [0.0, 0.01, 0.02, 0.03, 0.05])
        sensitivities["discount_rate"] = sens.sweep_discount_rate(
            capex, dec.pv_savings, dec.battery_savings, financial, battery,
            [0.04, 0.06, 0.08, 0.10, 0.12])

        # Battery sizing recommendation = energy capacity that maximises NPV.
        bs = sensitivities["battery_size"]
        rec = bs.loc[bs["npv_cad"].idxmax()]
        sizing_recommendation = {
            "recommended_kwh": float(rec["battery_kwh"]),
            "recommended_kw": float(rec["battery_kw"]),
            "npv_at_recommended_cad": float(rec["npv_cad"]),
            "note": "Existing pack is ~650 kWh; recommendation is the NPV-maximising "
                    "size across the swept range under current assumptions.",
        }
    else:
        sizing_recommendation = None

    # --- write outputs -----------------------------------------------------
    out = config.OUTPUT_DIR
    proj.monthly.to_csv(out / "monthly_results.csv")
    proj.dispatch.to_csv(out / "hourly_dispatch.csv", index=False)
    fin.cashflow_table.to_csv(out / "cashflow.csv", index=False)
    bom[bom["included"]].to_csv(out / "capex_line_items.csv", index=False)
    for name, df in sensitivities.items():
        df.to_csv(out / f"sensitivity_{name}.csv", index=False)

    summary = {
        "engine": proj.engine,
        "annual_load_kwh": round(float(load.sum()), 0),
        "peak_load_kw": round(float(load.max()), 1),
        "annual_pv_kwh": round(sc["annual_pv_kwh"], 0),
        "status_quo_bill_cad": round(dec.status_quo_bill, 0),
        "pv_only_bill_cad": round(dec.pv_only_bill, 0),
        "project_bill_cad": round(dec.project_bill, 0),
        "annual_pv_savings_cad": round(dec.pv_savings, 0),
        "annual_battery_savings_cad": round(dec.battery_savings, 0),
        "annual_total_savings_cad": round(dec.total_savings, 0),
        "annual_energy_savings_cad": round(proj.annual_energy_savings, 0),
        "annual_demand_savings_cad": round(proj.annual_demand_savings, 0),
        "avg_monthly_peak_reduction_kw": round(proj.peak_demand_reduction_kw, 1),
        "solar_self_consumption_no_battery_pct": round(sc["without_battery"] * 100, 1),
        "solar_self_consumption_with_battery_pct": round(sc["with_battery"] * 100, 1),
        "capex": capex,
        "annual_maintenance_cad": financial["annual_maintenance_cad"],
        "metrics": fin.metrics,
        "sizing_recommendation": sizing_recommendation,
    }
    with open(out / "summary_metrics.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    # --- report ------------------------------------------------------------
    report_path = config.REPORT_DIR / "Castellan_Farm_BESS_Report.md"
    write_report(report_path, summary, battery, financial, operating, rate,
                 fin.cashflow_table, sensitivities, bom)
    print(f"\nOutputs written to {out}")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
