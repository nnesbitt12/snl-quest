"""
Convert the raw customer uploads into curated, validated analysis inputs.

Run once (or whenever the raw data / rate assumptions change):

    python scripts/prepare_inputs.py

It produces, in ``input_data/``:

* ``farm_load_8760.csv``    - hourly load profile (datetime, load_kW) for the model year
* ``solar_production.csv``  - modelled 75 kW Ontario PV profile (datetime, pv_kW)
* ``bom.csv``               - structured bill of materials
* ``bom_summary.json``      - authoritative BOM totals / scope breakdown from the workbook
* ``rate_structure.json``   - QuESt-format rate structure expanded from rate_assumptions.json

Each step is independent and prints a short summary so the conversions can be
audited.

LIMITATION: the metered usage workbook is daily-resolution (one value repeated
across the 24 hours of each day). The hourly load profile therefore has no
intrinsic intraday shape unless ``apply_intraday_load_shape`` is enabled in
assumptions/operating.json. See README.md.
"""
from __future__ import annotations

import calendar
import json
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    INPUT_DIR,
    RAW_USAGE_XLSX,
    RAW_BOM_XLSX,
    LOAD_CSV,
    SOLAR_CSV,
    BOM_CSV,
    RATE_JSON,
    OPERATING_JSON,
    RATE_ASSUMPTIONS_JSON,
    load_json,
)

# Generic farm intraday shape (24 normalised weights summing to 24), used only
# when apply_intraday_load_shape is enabled. Mild daytime emphasis.
_INTRADAY_SHAPE = np.array(
    [0.7, 0.65, 0.6, 0.6, 0.6, 0.7, 0.9, 1.1, 1.2, 1.25, 1.3, 1.3,
     1.3, 1.3, 1.25, 1.2, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.8, 0.75]
)
_INTRADAY_SHAPE = _INTRADAY_SHAPE * 24.0 / _INTRADAY_SHAPE.sum()

KNOWN_CATEGORIES = {
    "Main Equipment", "PV DC Side", "Battery DC", "AC Power", "Protection",
    "Grounding", "Controls", "Engineering", "Studies", "Labour",
}


# ---------------------------------------------------------------------------
# Load profile
# ---------------------------------------------------------------------------
def build_load_profile(operating: dict) -> pd.Series:
    """Build an 8760 hourly load profile (kW) for the model year from raw data."""
    if not RAW_USAGE_XLSX.is_file():
        raise FileNotFoundError(f"Raw usage workbook not found: {RAW_USAGE_XLSX}")

    raw = pd.read_excel(RAW_USAGE_XLSX, sheet_name=0, header=5)
    raw = raw.iloc[:, :6]
    raw.columns = ["from_date", "from_time", "year", "month", "metered", "adjusted"]
    col = "metered" if operating.get("load_source_column", "metered") == "metered" else "adjusted"
    raw = raw.dropna(subset=["from_date", col]).copy()

    # Combine date + time into an hourly timestamp.
    dates = pd.to_datetime(raw["from_date"], errors="coerce")
    times = pd.to_timedelta(raw["from_time"].astype(str), errors="coerce")
    ts = dates + times.fillna(pd.Timedelta(0))
    series = pd.Series(pd.to_numeric(raw[col], errors="coerce").to_numpy(float), index=ts)
    series = series.dropna()
    series = series[~series.index.duplicated(keep="first")].sort_index()

    model_year = int(operating.get("model_year", 2025))

    # Representative 12-month window = most recent year of data available.
    last = series.index.max()
    window_start = last - pd.DateOffset(years=1) + pd.Timedelta(hours=1)
    window = series[series.index >= window_start]

    # Lookup tables for filling the model-year calendar.
    by_md_h = window.groupby(
        [window.index.month, window.index.day, window.index.hour]
    ).mean()
    by_m_h = series.groupby([series.index.month, series.index.hour]).mean()
    overall_mean = float(series.mean())

    # Build the full model-year hourly index.
    target_index = pd.date_range(
        start=f"{model_year}-01-01 00:00", end=f"{model_year}-12-31 23:00", freq="h"
    )
    values = []
    for ts_i in target_index:
        key = (ts_i.month, ts_i.day, ts_i.hour)
        if key in by_md_h.index:
            values.append(by_md_h.loc[key])
        elif (ts_i.month, ts_i.hour) in by_m_h.index:
            values.append(by_m_h.loc[(ts_i.month, ts_i.hour)])
        else:
            values.append(overall_mean)
    profile = pd.Series(np.array(values, dtype=float), index=target_index, name="load_kW")

    # Calibrate each calendar month to actual billed kWh, if provided.
    cal = operating.get("monthly_kwh_calibration")
    if cal:
        for key, target in cal.items():
            if str(key).startswith("_"):
                continue
            m = int(key)
            mask = profile.index.month == m
            current = profile[mask].sum()
            if current > 0:
                profile.loc[mask] = profile.loc[mask] * (float(target) / current)

    if operating.get("apply_intraday_load_shape", False):
        # Preserve each day's mean energy while applying a generic intraday shape.
        daily_mean = profile.groupby(profile.index.normalize()).transform("mean")
        shape = _INTRADAY_SHAPE[profile.index.hour]
        profile = daily_mean * shape
        profile.name = "load_kW"

    return profile.clip(lower=0.0)


# ---------------------------------------------------------------------------
# Solar profile
# ---------------------------------------------------------------------------
def build_solar_profile(index: pd.DatetimeIndex, operating: dict) -> pd.Series:
    """Model an hourly PV profile (kW) for an Ontario array (clear-sky + monthly scaling)."""
    solar = operating.get("solar", {})
    capacity = float(solar.get("pv_system_kw", 75))
    lat = np.radians(float(solar.get("latitude_deg", 44.0)))
    target_cf = float(solar.get("target_capacity_factor", 0.145))
    monthly = np.asarray(
        solar.get("monthly_irradiance_factors", [1.0] * 12), dtype=float
    )

    doy = index.dayofyear.to_numpy()
    decl = np.radians(23.45) * np.sin(2 * np.pi * (284 + doy) / 365.0)
    solar_hour = index.hour.to_numpy() + 0.5
    hra = np.radians(15.0 * (solar_hour - 12.0))
    elev = np.arcsin(
        np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(hra)
    )
    clear = np.clip(np.sin(elev), 0.0, None)
    raw = clear * monthly[index.month.to_numpy() - 1]

    target_annual = target_cf * capacity * len(index)  # kWh over the year
    scale = target_annual / raw.sum() if raw.sum() > 0 else 0.0
    pv = np.clip(raw * scale, 0.0, capacity)
    return pd.Series(pv, index=index, name="pv_kW")


# ---------------------------------------------------------------------------
# Rate structure (QuESt format)
# ---------------------------------------------------------------------------
def build_rate_structure(rate: dict) -> dict:
    """Expand the human-friendly rate knobs into a QuESt-format rate structure."""
    plan = rate.get("plan", "tou").lower()
    er = rate["energy_rates_cad_per_kwh"]
    tp = rate["tou_periods"]
    months = list(range(1, 13))
    hours = list(range(24))

    if plan == "flat":
        energy_rates = {"0": er["flat"]}
        weekday = [[0] * 24 for _ in months]
        weekend = [[0] * 24 for _ in months]
    elif plan == "custom_tou":
        # Explicit peak/mid/off hours and rates, no seasonal variation.
        ct = rate["custom_tou"]
        r = ct["rates_cad_per_kwh"]
        energy_rates = {"0": r["off"], "1": r["mid"], "2": r["peak"]}
        peak_h, mid_h = set(ct["peak_hours"]), set(ct["mid_hours"])
        weekday = [[2 if h in peak_h else (1 if h in mid_h else 0) for h in hours]
                   for _ in months]
        weekend = ([[0] * 24 for _ in months] if ct.get("weekend_all_off", True)
                   else [row[:] for row in weekday])
    elif plan == "ulo":
        # 0=ULO overnight, 1=weekend off-peak, 2=mid-peak, 3=on-peak (approximate).
        energy_rates = {"0": er["ulo_overnight"], "1": er["off_peak"],
                        "2": er["mid_peak"], "3": er["on_peak"]}
        overnight = set(rate.get("ulo_overnight_hours", []))
        on_pk = set(rate.get("ulo_on_peak_hours_weekday", []))
        weekday, weekend = [], []
        for _m in months:
            weekday.append([0 if h in overnight else (3 if h in on_pk else 2) for h in hours])
            weekend.append([0 if h in overnight else 1 for h in hours])
    else:  # tou
        energy_rates = {"0": er["off_peak"], "1": er["mid_peak"], "2": er["on_peak"]}
        summer = set(tp["summer_months"])
        on_s, mid_s = set(tp["on_peak_hours_summer"]), set(tp["mid_peak_hours_summer"])
        on_w, mid_w = set(tp["on_peak_hours_winter"]), set(tp["mid_peak_hours_winter"])
        weekday, weekend = [], []
        for m in months:
            on_pk, mid_pk = (on_s, mid_s) if m in summer else (on_w, mid_w)
            weekday.append([2 if h in on_pk else (1 if h in mid_pk else 0) for h in hours])
            weekend.append([0] * 24)  # weekends/holidays are off-peak in Ontario

    demand = float(rate.get("demand_charge_cad_per_kw", 0.0))
    flat_rates = {calendar.month_abbr[m]: demand for m in months}
    nem = rate.get("net_metering", {})
    # credit_mode 'retail' -> QuESt NEM 2.0 (type True, sell at retail TOU);
    # 'flat' -> QuESt NEM 1.0 (type False, sell at a single sell price).
    nem_retail = nem.get("credit_mode", "flat").lower() == "retail" and nem.get("enabled", True)

    return {
        "name": rate.get("name", "Custom rate"),
        "utility": rate.get("utility", "Unknown"),
        "energy rate structure": {
            "weekday schedule": weekday,
            "weekend schedule": weekend,
            "energy rates": energy_rates,
        },
        "demand rate structure": {
            "weekday schedule": [[0] * 24 for _ in months],
            "weekend schedule": [[0] * 24 for _ in months],
            "time of use rates": {"0": 0.0},
            "flat rates": flat_rates,
        },
        "net metering": {
            "type": bool(nem_retail),
            "energy sell price": float(nem.get("sell_price_cad_per_kwh", 0.0)),
        },
    }


# ---------------------------------------------------------------------------
# Bill of materials
# ---------------------------------------------------------------------------
def build_bom() -> tuple[pd.DataFrame, dict]:
    """Extract a structured BOM and authoritative totals from the workbook."""
    if not RAW_BOM_XLSX.is_file():
        raise FileNotFoundError(f"Raw BOM workbook not found: {RAW_BOM_XLSX}")

    sheet = pd.read_excel(RAW_BOM_XLSX, sheet_name="BOM with Cost-Down", header=3)
    sheet.columns = [str(c).strip() for c in sheet.columns]

    rows = []
    summary = {"active_bom_total_cad": None, "optimized_target_cad": None,
               "scope_breakdown": {}}
    for _, r in sheet.iterrows():
        category = str(r.get("Category", "")).strip()
        item = str(r.get("Item", "")).strip()

        # Capture authoritative totals embedded in the workbook (the "Active
        # BOM Total →" / "Optimized Target →" labels sit in the Qty column).
        marker = str(r.get("Qty", "")).strip()
        cost_val = pd.to_numeric(r.get("Current Est. ($CAD)"), errors="coerce")
        if marker == "Active BOM Total →":
            summary["active_bom_total_cad"] = float(cost_val) if pd.notna(cost_val) else None
        if marker == "Optimized Target →":
            summary["optimized_target_cad"] = float(cost_val) if pd.notna(cost_val) else None

        if category not in KNOWN_CATEGORIES or item.lower() in ("", "nan"):
            continue

        scope = str(r.get("Scope", "")).strip()
        necessity = str(r.get("Necessity", "")).strip()
        qty = r.get("Qty")
        total = pd.to_numeric(r.get("Current Est. ($CAD)"), errors="coerce")
        total = float(total) if pd.notna(total) else 0.0
        qty_num = pd.to_numeric(qty, errors="coerce")
        unit = total / qty_num if pd.notna(qty_num) and qty_num else total

        # An item counts toward project CAPEX unless it is client-owned
        # (EXISTING) or flagged for removal (ELIMINATE).
        included = scope.upper() != "EXISTING" and necessity.upper() != "ELIMINATE"

        rows.append({
            "category": category,
            "item": item,
            "description": str(r.get("Description", "")).strip(),
            "qty": "" if pd.isna(qty) else qty,
            "scope": scope,
            "necessity": necessity,
            "unit_cost": round(unit, 2),
            "total_cost": round(total, 2),
            "capex_opex": "CAPEX",
            "included": included,
            "notes": str(r.get("Notes / Source", "")).strip(),
        })

    bom = pd.DataFrame(rows)

    # Scope breakdown (PV / BATTERY / SHARED) over included items.
    inc = bom[bom["included"]]
    summary["scope_breakdown"] = {
        s: round(float(inc.loc[inc["scope"] == s, "total_cost"].sum()), 2)
        for s in sorted(inc["scope"].unique())
    }
    summary["line_items_included_total_cad"] = round(float(inc["total_cost"].sum()), 2)
    return bom, summary


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def main() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    operating = load_json(OPERATING_JSON)
    rate_assumptions = load_json(RATE_ASSUMPTIONS_JSON)

    print("Building load profile from", RAW_USAGE_XLSX.name, "...")
    load = build_load_profile(operating)
    load.to_frame().to_csv(LOAD_CSV, index_label="datetime")
    print(f"  -> {LOAD_CSV.name}: {len(load)} hours, "
          f"annual {load.sum():,.0f} kWh, peak {load.max():,.1f} kW, "
          f"intraday_shape={operating.get('apply_intraday_load_shape', False)}")

    print(f"Modelling solar profile ({operating['solar']['pv_system_kw']} kW estimate) ...")
    solar = build_solar_profile(load.index, operating)
    solar.to_frame().to_csv(SOLAR_CSV, index_label="datetime")
    cf = solar.sum() / (operating['solar']['pv_system_kw'] * len(solar))
    print(f"  -> {SOLAR_CSV.name}: annual {solar.sum():,.0f} kWh, "
          f"capacity factor {cf:.1%}")

    print("Expanding rate structure from", RATE_ASSUMPTIONS_JSON.name, "...")
    rate_struct = build_rate_structure(rate_assumptions)
    with open(RATE_JSON, "w", encoding="utf-8") as fh:
        json.dump(rate_struct, fh, indent=2)
    print(f"  -> {RATE_JSON.name}: plan={rate_assumptions.get('plan')}, "
          f"rates={rate_struct['energy rate structure']['energy rates']}")

    print("Extracting BOM from", RAW_BOM_XLSX.name, "...")
    bom, summary = build_bom()
    bom.to_csv(BOM_CSV, index=False)
    with open(INPUT_DIR / "bom_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(f"  -> {BOM_CSV.name}: {len(bom)} line items, "
          f"included subtotal ${summary['line_items_included_total_cad']:,.0f}; "
          f"workbook active total ${summary['active_bom_total_cad']:,.0f}")
    print("Done.")


if __name__ == "__main__":
    main()
