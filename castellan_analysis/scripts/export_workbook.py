"""
Compile the Castellan Farm analysis into a single multi-sheet Excel workbook.

Reads the curated inputs and generated outputs and writes
``outputs/Castellan_Farm_BESS_Analysis.xlsx`` with one sheet per topic:
Summary, Assumptions, BOM, CAPEX, Monthly Results, Cash Flow, the five
Sensitivity sweeps, and the hourly dispatch.

Run after run_analysis.py:

    python scripts/export_workbook.py
"""
from __future__ import annotations

import json

import pandas as pd

import config

WORKBOOK = config.OUTPUT_DIR / "Castellan_Farm_BESS_Analysis.xlsx"


def _flatten(prefix, obj, rows):
    """Flatten a nested dict/JSON into (metric, value) rows for the Summary sheet."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("_"):
                continue
            _flatten(f"{prefix} / {k}" if prefix else str(k), v, rows)
    else:
        rows.append({"Metric": prefix, "Value": obj})


def _summary_df() -> pd.DataFrame:
    data = config.load_json(config.OUTPUT_DIR / "summary_metrics.json")
    rows: list[dict] = []
    _flatten("", data, rows)
    return pd.DataFrame(rows)


def _assumptions_df() -> pd.DataFrame:
    rows: list[dict] = []
    for label, path in (("battery", config.BATTERY_JSON),
                        ("financial", config.FINANCIAL_JSON),
                        ("operating", config.OPERATING_JSON),
                        ("rate", config.RATE_ASSUMPTIONS_JSON)):
        flat: list[dict] = []
        _flatten("", config.load_json(path), flat)
        for r in flat:
            rows.append({"Group": label, "Parameter": r["Metric"], "Value": r["Value"]})
    return pd.DataFrame(rows)


def _read_csv(name: str) -> pd.DataFrame | None:
    path = config.OUTPUT_DIR / name
    return pd.read_csv(path) if path.is_file() else None


def main() -> None:
    config.ensure_output_dirs()
    bom = pd.read_csv(config.BOM_CSV)
    bom_summary = config.load_json(config.INPUT_DIR / "bom_summary.json")
    bom_totals = pd.DataFrame(
        [{"Metric": k, "Value": v} for k, v in bom_summary.items()
         if not isinstance(v, dict)]
        + [{"Metric": f"scope: {k}", "Value": v}
           for k, v in bom_summary.get("scope_breakdown", {}).items()]
    )

    sheets: dict[str, pd.DataFrame] = {}
    sheets["Summary"] = _summary_df()
    sheets["Assumptions"] = _assumptions_df()
    sheets["BOM (full)"] = bom
    sheets["BOM Totals"] = bom_totals
    sheets["CAPEX line items"] = _read_csv("capex_line_items.csv")
    sheets["Monthly Results"] = _read_csv("monthly_results.csv")
    sheets["Cash Flow"] = _read_csv("cashflow.csv")
    sheets["Sens - Battery Size"] = _read_csv("sensitivity_battery_size.csv")
    sheets["Sens - CAPEX"] = _read_csv("sensitivity_capex.csv")
    sheets["Sens - Electricity Rate"] = _read_csv("sensitivity_electricity_rate.csv")
    sheets["Sens - Degradation"] = _read_csv("sensitivity_degradation.csv")
    sheets["Sens - Discount Rate"] = _read_csv("sensitivity_discount_rate.csv")
    sheets["Hourly Dispatch"] = _read_csv("hourly_dispatch.csv")

    with pd.ExcelWriter(WORKBOOK, engine="openpyxl") as writer:
        for name, df in sheets.items():
            if df is None:
                continue
            df.to_excel(writer, sheet_name=name[:31], index=False)
            # Auto-size columns (cap width so wide text/notes stay readable).
            ws = writer.sheets[name[:31]]
            for col in ws.columns:
                width = max((len(str(c.value)) for c in col if c.value is not None),
                            default=10)
                ws.column_dimensions[col[0].column_letter].width = min(max(width + 2, 10), 60)

    print(f"Workbook written to {WORKBOOK}")


if __name__ == "__main__":
    main()
