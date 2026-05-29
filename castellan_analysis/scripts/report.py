"""Markdown report generation for the Castellan Farm BESS analysis."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


def _money(x) -> str:
    if x is None:
        return "n/a"
    return f"${x:,.0f}"


def _pct(x) -> str:
    return "n/a" if x is None else f"{x:.1f}%"


def _df_md(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub-flavoured markdown table."""
    try:
        return df.to_markdown(index=False)
    except Exception:  # pragma: no cover - tabulate may be unavailable
        header = "| " + " | ".join(map(str, df.columns)) + " |"
        sep = "| " + " | ".join("---" for _ in df.columns) + " |"
        rows = ["| " + " | ".join(map(str, r)) + " |" for r in df.to_numpy()]
        return "\n".join([header, sep, *rows])


def write_report(path: Path, summary: dict, battery: dict, financial: dict,
                 operating: dict, rate: dict, cashflow: pd.DataFrame,
                 sensitivities: dict, bom: pd.DataFrame) -> None:
    m = summary["metrics"]
    capex = summary["capex"]
    rec = summary.get("sizing_recommendation")
    energy_rates = rate["energy rate structure"]["energy rates"]

    lines: list[str] = []
    a = lines.append

    a(f"# Castellan Farm — Solar + BESS Project Analysis")
    a("")
    a(f"_Generated {date.today().isoformat()} using QuESt BTM "
      f"(engine: **{summary['engine']}**) + project financial model._")
    a("")
    a("> **Currency:** CAD. All results depend on the editable assumptions in "
      "`assumptions/` and the curated inputs in `input_data/`. See "
      "**Limitations** below before relying on these numbers.")
    a("")

    # ---- Headline results -------------------------------------------------
    a("## 1. Headline results")
    a("")
    a("| Metric | Value |")
    a("|---|---|")
    a(f"| Total project CAPEX | {_money(capex['total_capex_cad'])} ({capex['bom_scenario']}) |")
    a(f"| Year-1 total savings | {_money(summary['annual_total_savings_cad'])}/yr |")
    a(f"| — PV self-consumption savings | {_money(summary['annual_pv_savings_cad'])}/yr |")
    a(f"| — Battery dispatch savings | {_money(summary['annual_battery_savings_cad'])}/yr |")
    a(f"| Annual O&M | {_money(summary['annual_maintenance_cad'])}/yr |")
    payback_txt = (f"{m['simple_payback_years']} years"
                   if m['simple_payback_years'] is not None
                   else f"Not within {m['project_life_years']} yr")
    a(f"| Simple payback | {payback_txt} |")
    a(f"| NPV @ {m['discount_rate_pct']}% over {m['project_life_years']} yr | {_money(m['npv_cad'])} |")
    a(f"| IRR | {_pct(m['irr_pct'])} |")
    a(f"| Avg. monthly peak-demand reduction | {summary['avg_monthly_peak_reduction_kw']} kW |")
    a(f"| Solar self-consumption (no batt → batt) | "
      f"{summary['solar_self_consumption_no_battery_pct']}% → "
      f"{summary['solar_self_consumption_with_battery_pct']}% |")
    a("")

    # ---- Battery sizing ---------------------------------------------------
    a("## 2. Battery sizing recommendation")
    a("")
    if rec:
        a(f"Across the swept range, NPV is maximised at **{rec['recommended_kwh']:.0f} kWh "
          f"/ {rec['recommended_kw']:.0f} kW** "
          f"(NPV {_money(rec['npv_at_recommended_cad'])}). {rec['note']}")
        a("")
        a(_df_md(sensitivities["battery_size"]))
    else:
        a("_Sensitivity sweeps were skipped (`--no-sensitivity`)._")
    a("")

    # ---- Energy & savings -------------------------------------------------
    a("## 3. Energy, savings and demand")
    a("")
    a(f"- **Annual farm load:** {summary['annual_load_kwh']:,.0f} kWh "
      f"(peak {summary['peak_load_kw']:,.0f} kW)")
    a(f"- **Annual PV generation (modelled):** {summary['annual_pv_kwh']:,.0f} kWh")
    a(f"- **Status-quo utility bill (grid only):** {_money(summary['status_quo_bill_cad'])}/yr")
    a(f"- **PV-only bill (baseline case):** {_money(summary['pv_only_bill_cad'])}/yr")
    a(f"- **PV + battery bill (battery case):** {_money(summary['project_bill_cad'])}/yr")
    a(f"- **Annual energy-charge savings (battery):** {_money(summary['annual_energy_savings_cad'])}/yr")
    a(f"- **Annual demand-charge savings (battery):** {_money(summary['annual_demand_savings_cad'])}/yr")
    a("")
    if abs(summary.get("annual_demand_savings_cad", 0)) < 1:
        a("> **Peak-demand note:** this tariff has no demand ($/kW) charge, so "
          "peak-demand reduction carries **$0** value and the optimizer may even "
          "raise peak load while charging off-peak. Set `demand_charge_cad_per_kw` "
          "in `assumptions/rate_assumptions.json` (and re-run `prepare_inputs.py`) "
          "to value peak shaving on a demand-billed tariff.")
        a("")

    # ---- CAPEX ------------------------------------------------------------
    a("## 4. CAPEX (from BOM)")
    a("")
    a("| Component | CAD |")
    a("|---|---|")
    a(f"| BOM base ({capex['bom_scenario']}) | {_money(capex['bom_base_cad'])} |")
    a(f"| Battery (new) | {_money(capex['battery_capex_cad'])} |")
    a(f"| Adders (EPC / interconnection / engineering / other) | {_money(capex['adders_cad'])} |")
    a(f"| Contingency | {_money(capex['contingency_cad'])} |")
    if capex.get("itc_rate"):
        a(f"| Subtotal (pre-incentive) | {_money(capex.get('pre_itc_capex_cad'))} |")
        a(f"| Clean-Tech ITC ({capex['itc_rate']:.0%}) | −{_money(capex.get('itc_credit_cad'))} |")
    a(f"| **Total CAPEX (net)** | **{_money(capex['total_capex_cad'])}** |")
    a("")
    a("Top included BOM line items:")
    a("")
    top = bom[bom["included"]].nlargest(10, "total_cost")[
        ["category", "item", "qty", "scope", "total_cost"]]
    a(_df_md(top))
    a("")

    # ---- Cashflow ---------------------------------------------------------
    a("## 5. Cash flow")
    a("")
    cf_show = cashflow[["year", "gross_savings_cad", "opex_cad",
                        "net_cash_flow_cad", "cumulative_net_cad",
                        "cumulative_discounted_cad"]]
    a(_df_md(cf_show))
    a("")

    # ---- Sensitivity ------------------------------------------------------
    if sensitivities:
        a("## 6. Sensitivity analysis")
        titles = {
            "capex": "CAPEX (multiplier on total CAPEX)",
            "electricity_rate": "Electricity rate (multiplier on savings)",
            "degradation": "Battery degradation rate",
            "discount_rate": "Discount rate",
        }
        for key, title in titles.items():
            if key in sensitivities:
                a(f"### 6.{list(titles).index(key)+1} {title}")
                a("")
                a(_df_md(sensitivities[key]))
                a("")

    # ---- Assumptions ------------------------------------------------------
    a("## 7. Assumptions used")
    a("")
    a("**Battery**")
    a(f"- Energy capacity: {battery['energy_capacity_kwh']} kWh; power: {battery['power_rating_kw']} kW")
    a(f"- Round-trip efficiency: {battery['round_trip_efficiency']:.0%}; "
      f"usable SOC: {battery['state_of_charge_min']:.0%}–{battery['state_of_charge_max']:.0%} "
      f"({(battery['state_of_charge_max']-battery['state_of_charge_min']):.0%} usable DoD)")
    a(f"- Annual degradation: {battery['annual_degradation_rate']:.1%}; "
      f"battery in CAPEX: {battery['battery_capex_included']} "
      f"(existing pack treated as sunk cost unless set true)")
    a("")
    a("**Financial**")
    a(f"- Discount rate: {financial['discount_rate']:.1%}; project life: {financial['project_life_years']} yr")
    a(f"- Electricity escalation: {financial['electricity_escalation_rate']:.1%}; "
      f"O&M escalation: {financial['opex_escalation_rate']:.1%}")
    a(f"- Annual O&M: {_money(financial['annual_maintenance_cad'])}; "
      f"contingency: {financial['contingency_pct']:.0%}; "
      f"PV degradation: {financial['pv_degradation_rate']:.1%}")
    a("")
    a(f"**Utility rate** — {rate.get('name', 'custom')} (CAD/kWh)")
    rate_vals = ", ".join(f"period {k}: {v}" for k, v in energy_rates.items())
    a(f"- Energy rates by TOU period: {rate_vals}")
    a(f"- Net metering: {'retail (NEM 2.0)' if rate['net metering']['type'] else 'flat credit (NEM 1.0)'} "
      f"@ {rate['net metering']['energy sell price']} $/kWh")
    a("")
    pv_kw = operating.get("solar", {}).get("pv_system_kw", "?")
    a(f"**Solar:** existing {pv_kw} kW array, modelled (clear-sky + monthly scaling), "
      f"~{summary['annual_pv_kwh']:,.0f} kWh/yr. Replace `input_data/solar_production.csv` "
      "with measured / PVWatts data when available.")
    a("")

    # ---- Limitations ------------------------------------------------------
    a("## 8. Limitations")
    a("")
    a("1. **Load data is daily-resolution.** The metered usage workbook repeats a "
      "single value across all 24 hours of each day, so the load profile has no "
      "intrinsic intraday shape. TOU energy arbitrage is still valued (prices vary "
      "intraday) but within-day load peaks and load-following are not represented. "
      "Enable `apply_intraday_load_shape` to overlay a generic farm shape.")
    a("2. **Solar is modelled, not measured.** PV output is a clear-sky estimate "
      "scaled to a typical Ontario capacity factor; actual generation will vary with "
      "weather, soiling, shading and array orientation.")
    a("3. **Rate covers energy commodity only.** The configured TOU energy rates "
      "are modelled with a flat net-metering export credit. Delivery, regulatory, "
      "fixed and global-adjustment charges are **not** included; actual bill savings "
      "may differ, especially where those charges scale with peak kW/kWh.")
    a("4. **Monthly independent optimization.** QuESt BTM optimizes each month "
      "separately with a fixed initial state of charge; it does not co-optimize "
      "across month boundaries or model ageing within the dispatch.")
    a("5. **Degradation & rate sensitivities are linear approximations.** Year-1 "
      "savings are scaled by capacity retention and price multipliers rather than "
      "re-optimized each year (battery-size cases _are_ re-optimized).")
    a("6. **Holiday calendar.** QuESt's schedule builder uses US federal holidays; "
      "Ontario statutory holidays differ slightly, marginally affecting which days "
      "are billed at weekend (off-peak) rates.")
    a("")

    path.write_text("\n".join(lines), encoding="utf-8")
