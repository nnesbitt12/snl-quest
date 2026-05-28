"""
Run the behind-the-meter dispatch optimization for the Castellan Farm project.

This is the bridge to QuESt: it drives QuESt's own ``BtmOptimizer`` (the Pyomo
linear program behind QuESt BTM) month-by-month over the project's load, solar,
rate and battery inputs, then packages the per-month results into a single
:class:`BtmResults` object that the financial model consumes.

Two engines are available and produce the *same* result schema:

* ``quest``     - uses QuESt's BtmOptimizer + a MILP/LP solver (glpk). Optimal dispatch.
* ``heuristic`` - a solver-free, price-greedy approximation so the workflow runs
                  anywhere QuESt's solver is unavailable. Clearly labelled as approximate.

``engine="auto"`` (the default) uses QuESt if its solver is importable and falls
back to the heuristic otherwise.

The optimizer's own "without energy storage" figures provide the **baseline
case** (no battery); the "with energy storage" figures provide the **battery
case** with optimized dispatch. Both are returned so the two cases can be
compared financially.
"""
from __future__ import annotations

import calendar
import contextlib
import io
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
import pandas as pd

import config


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------
@dataclass
class BtmResults:
    """Standardised output of either dispatch engine."""

    engine: str
    monthly: pd.DataFrame  # index 1..12, bill/energy/demand/nem/peak columns
    dispatch: pd.DataFrame  # 8760 hourly dispatch time series
    ess_params: Dict = field(default_factory=dict)

    # --- annual roll-ups (baseline = without ES, battery = with ES) ----------
    @property
    def annual_bill_baseline(self) -> float:
        return float(self.monthly["bill_without"].sum())

    @property
    def annual_bill_battery(self) -> float:
        return float(self.monthly["bill_with"].sum())

    @property
    def annual_savings(self) -> float:
        return self.annual_bill_baseline - self.annual_bill_battery

    @property
    def annual_energy_savings(self) -> float:
        return float((self.monthly["energy_without"] - self.monthly["energy_with"]).sum())

    @property
    def annual_demand_savings(self) -> float:
        return float((self.monthly["demand_without"] - self.monthly["demand_with"]).sum())

    @property
    def annual_nem_savings(self) -> float:
        # NEM charges are negative (credits); a more-negative "with" value is a saving.
        return float((self.monthly["nem_without"] - self.monthly["nem_with"]).sum())

    @property
    def peak_demand_reduction_kw(self) -> float:
        """Average monthly peak-demand reduction (kW)."""
        return float((self.monthly["peak_without_kw"] - self.monthly["peak_with_kw"]).mean())

    def solar_self_consumption(self) -> Dict[str, float]:
        """PV self-consumption fraction with and without the battery."""
        d = self.dispatch
        total_pv = d["pv_kw"].sum()
        if total_pv <= 0:
            return {"without_battery": float("nan"), "with_battery": float("nan"),
                    "annual_pv_kwh": 0.0}
        export_without = np.maximum(0.0, d["pv_kw"] - d["load_kw"]).sum()
        export_with = np.maximum(0.0, -d["net_with_kw"]).sum()
        return {
            "without_battery": float((total_pv - export_without) / total_pv),
            "with_battery": float((total_pv - export_with) / total_pv),
            "annual_pv_kwh": float(total_pv),
        }


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _hourly_energy_rate(rate: dict, schedule_month: np.ndarray) -> np.ndarray:
    """Map a month's TOU schedule indices to $/kWh energy rates."""
    rates = rate["energy rate structure"]["energy rates"]
    lut = {int(k): float(v) for k, v in rates.items()}
    return np.array([lut[int(i)] for i in schedule_month], dtype=float)


def _build_schedule(rate: dict, model_year: int):
    """Return per-hour TOU energy & demand schedule indices for the model year.

    Uses QuESt's own readutdata.input_df so weekend/holiday handling matches the
    GUI exactly.
    """
    config.register_quest_btm_path()
    from btm.es_gui.tools.btm import readutdata

    ers = rate["energy rate structure"]
    drs = rate["demand rate structure"]
    rate_df = readutdata.input_df(
        model_year,
        ers["weekday schedule"], ers["weekend schedule"],
        drs["weekday schedule"], drs["weekend schedule"],
    )
    return rate_df


# ---------------------------------------------------------------------------
# QuESt engine
# ---------------------------------------------------------------------------
def quest_available(solver: str = "glpk") -> bool:
    """True if QuESt's optimizer and its solver can be loaded here."""
    try:
        config.register_quest_btm_path()
        import pyomo.environ  # noqa: F401
        from pyomo.opt import SolverFactory
        from btm.es_gui.tools.btm.btm_optimizer import BtmOptimizer  # noqa: F401

        return bool(SolverFactory(solver).available())
    except Exception as exc:  # noqa: BLE001
        logging.info("QuESt optimizer unavailable: %s", exc)
        return False


def _run_quest(load, solar, rate, ess_params, operating) -> BtmResults:
    config.register_quest_btm_path()
    from btm.es_gui.tools.btm.btm_optimizer import BtmOptimizer

    model_year = int(operating.get("model_year", 2025))
    solver = operating.get("solver", "glpk")
    rate_df = _build_schedule(rate, model_year)

    energy_rate_lut = rate["energy rate structure"]["energy rates"]
    tou_energy_rate = [float(v) for _, v in energy_rate_lut.items()]
    tou_demand_rate = [float(v) for _, v in rate["demand rate structure"]["time of use rates"].items()]
    flat_rates = rate["demand rate structure"]["flat rates"]
    nem = rate["net metering"]
    nem_type = 2 if nem["type"] else 1
    nem_rate = None if nem["type"] else nem["energy sell price"]

    monthly_rows: List[dict] = []
    dispatch_frames: List[pd.DataFrame] = []

    for ix, month_abbr in enumerate(calendar.month_abbr[1:], start=1):
        month_mask = load.index.month == ix
        load_m = load[month_mask].to_numpy(float)
        solar_m = solar[month_mask].to_numpy(float)
        rd = rate_df.loc[rate_df["month"] == ix]

        op = BtmOptimizer(solver=solver)
        op.tou_energy_schedule = rd["tou_energy_schedule"].to_numpy()
        op.tou_demand_schedule = rd["tou_demand_schedule"].to_numpy()
        op.tou_energy_rate = tou_energy_rate
        op.tou_demand_rate = tou_demand_rate if tou_demand_rate else [0.0]
        op.flat_demand_rate = float(flat_rates[month_abbr])
        op.nem_type = nem_type
        op.nem_rate = nem_rate
        op.load_profile = load_m
        op.pv_profile = solar_m
        op.rate_structure_metadata = {"name": rate.get("name", "rate")}
        op.load_profile_metadata = {"name": "Castellan Farm"}
        op.pv_profile_metadata = {"name": "Ontario 75kW PV"}
        op.set_model_parameters(**ess_params)

        # Solve quietly (the optimizer streams glpsol output to stdout).
        logging.getLogger("pyomo.core").setLevel(logging.ERROR)
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            op.run()

        res = op.results
        net_without = res["Pload"].to_numpy() - res["Ppv"].to_numpy()
        net_with = res["Ptotal"].to_numpy()

        monthly_rows.append({
            "month": ix,
            "bill_without": op.total_bill_without_es,
            "bill_with": op.total_bill_with_es,
            "energy_without": op.energy_charge_without_es,
            "energy_with": op.energy_charge_with_es,
            "demand_without": op.demand_charge_without_es,
            "demand_with": op.demand_charge_with_es,
            "nem_without": op.nem_charge_without_es,
            "nem_with": op.nem_charge_with_es,
            "peak_without_kw": float(np.max(net_without)) if len(net_without) else 0.0,
            "peak_with_kw": float(np.max(net_with)) if len(net_with) else 0.0,
        })

        df = pd.DataFrame({
            "datetime": load[month_mask].index,
            "load_kw": res["Pload"].to_numpy(),
            "pv_kw": res["Ppv"].to_numpy(),
            "charge_kw": res["Pcharge"].to_numpy(),
            "discharge_kw": res["Pdischarge"].to_numpy(),
            "soc_kwh": res["state of charge"].to_numpy(),
            "net_with_kw": net_with,
            "net_without_kw": net_without,
        })
        dispatch_frames.append(df)

    monthly = pd.DataFrame(monthly_rows).set_index("month")
    dispatch = pd.concat(dispatch_frames, ignore_index=True)
    return BtmResults("quest", monthly, dispatch, ess_params)


# ---------------------------------------------------------------------------
# Heuristic engine (solver-free fallback)
# ---------------------------------------------------------------------------
def _bill_components(net, energy_rate, flat_dr, nem_sell):
    """Compute monthly bill components from a net-load array (kW, hourly)."""
    energy_charge = float(np.sum(np.maximum(0.0, net) * energy_rate))
    nem_charge = float(np.sum(np.minimum(0.0, net) * nem_sell))  # negative credit
    demand_charge = float(np.max(net) * flat_dr) if len(net) else 0.0
    return energy_charge, demand_charge, nem_charge


def _run_heuristic(load, solar, rate, ess_params, operating) -> BtmResults:
    model_year = int(operating.get("model_year", 2025))
    rate_df = _build_schedule(rate, model_year)
    nem = rate["net metering"]
    flat_rates = rate["demand rate structure"]["flat rates"]

    cap = float(ess_params["Energy_capacity"])
    pwr = float(ess_params["Power_rating"])
    rte = float(ess_params["Round_trip_efficiency"])
    soc_min = float(ess_params["State_of_charge_min"]) * cap
    soc_max = float(ess_params["State_of_charge_max"]) * cap
    eff = np.sqrt(rte)  # split round-trip efficiency over charge/discharge

    monthly_rows: List[dict] = []
    dispatch_frames: List[pd.DataFrame] = []

    for ix, month_abbr in enumerate(calendar.month_abbr[1:], start=1):
        mask = load.index.month == ix
        load_m = load[mask].to_numpy(float)
        solar_m = solar[mask].to_numpy(float)
        idx = load[mask].index
        rd = rate_df.loc[rate_df["month"] == ix]
        er = _hourly_energy_rate(rate, rd["tou_energy_schedule"].to_numpy())
        nem_sell = er if nem["type"] else np.full(len(er), nem.get("energy sell price", 0.0))

        net0 = load_m - solar_m
        charge = np.zeros(len(load_m))
        discharge = np.zeros(len(load_m))
        soc = np.full(len(load_m), float(ess_params["State_of_charge_init"]) * cap)

        # Greedy daily arbitrage: charge in cheapest hours, discharge in dearest.
        days = pd.Series(idx).dt.normalize().to_numpy()
        for day in np.unique(days):
            h = np.where(days == day)[0]
            order_cheap = h[np.argsort(er[h])]
            order_dear = h[np.argsort(-er[h])]
            stored = 0.0
            # Charge phase
            for t in order_cheap:
                room = min(pwr, (soc_max - soc_min) - stored / eff)
                if room <= 0:
                    break
                charge[t] = max(0.0, room)
                stored += charge[t] * eff
            # Discharge phase (only where it beats the charge price)
            avail = stored
            for t in order_dear:
                if avail <= 0:
                    break
                d = min(pwr, avail, max(0.0, net0[t]))
                discharge[t] = d
                avail -= d

        net_with = net0 + charge - discharge
        e_w, d_w, n_w = _bill_components(net_with, er, float(flat_rates[month_abbr]), nem_sell)
        e0, d0, n0 = _bill_components(net0, er, float(flat_rates[month_abbr]), nem_sell)

        # Rational-operator guard: a greedy schedule can lose money (efficiency
        # losses / new peaks). If so, leave the battery idle this month so the
        # heuristic is a conservative lower bound rather than actively harmful.
        if (e_w + d_w + n_w) > (e0 + d0 + n0):
            charge[:] = 0.0
            discharge[:] = 0.0
            net_with = net0.copy()
            e_w, d_w, n_w = e0, d0, n0

        monthly_rows.append({
            "month": ix,
            "bill_without": e0 + d0 + n0, "bill_with": e_w + d_w + n_w,
            "energy_without": e0, "energy_with": e_w,
            "demand_without": d0, "demand_with": d_w,
            "nem_without": n0, "nem_with": n_w,
            "peak_without_kw": float(np.max(net0)) if len(net0) else 0.0,
            "peak_with_kw": float(np.max(net_with)) if len(net_with) else 0.0,
        })
        dispatch_frames.append(pd.DataFrame({
            "datetime": idx, "load_kw": load_m, "pv_kw": solar_m,
            "charge_kw": charge, "discharge_kw": discharge, "soc_kwh": soc,
            "net_with_kw": net_with, "net_without_kw": net0,
        }))

    monthly = pd.DataFrame(monthly_rows).set_index("month")
    dispatch = pd.concat(dispatch_frames, ignore_index=True)
    return BtmResults("heuristic", monthly, dispatch, ess_params)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def battery_params_from_assumptions(battery: dict) -> Dict[str, float]:
    """Translate battery.json into QuESt BtmOptimizer model parameters."""
    return {
        "Power_rating": float(battery["power_rating_kw"]),
        "Energy_capacity": float(battery["energy_capacity_kwh"]),
        "Round_trip_efficiency": float(battery["round_trip_efficiency"]),
        "Self_discharge_efficiency": float(battery.get("self_discharge_efficiency", 1.0)),
        "State_of_charge_min": float(battery["state_of_charge_min"]),
        "State_of_charge_max": float(battery["state_of_charge_max"]),
        "State_of_charge_init": float(battery["state_of_charge_init"]),
        "Transformer_rating": float(battery.get("transformer_rating_kw", 1_000_000)),
    }


def run_btm(load, solar, rate, ess_params, operating) -> BtmResults:
    """Run the dispatch optimization with the configured/auto-selected engine."""
    engine = operating.get("engine", "auto")
    solver = operating.get("solver", "glpk")

    if engine == "heuristic":
        return _run_heuristic(load, solar, rate, ess_params, operating)
    if engine == "quest":
        return _run_quest(load, solar, rate, ess_params, operating)

    # auto
    if quest_available(solver):
        return _run_quest(load, solar, rate, ess_params, operating)
    logging.warning("Falling back to heuristic dispatch engine (QuESt solver unavailable).")
    return _run_heuristic(load, solar, rate, ess_params, operating)


@dataclass
class ProjectSavings:
    """Savings decomposed into PV and battery contributions vs. status quo."""

    status_quo_bill: float       # grid-only (no PV, no battery)
    pv_only_bill: float          # PV, no battery (the "baseline case")
    project_bill: float          # PV + battery (the "battery case")
    pv_savings: float
    battery_savings: float
    total_savings: float
    project_results: BtmResults  # PV+battery run (dispatch, peaks, self-consumption)


def run_decomposed(load, solar, rate, ess_params, operating) -> ProjectSavings:
    """Run the two optimizations needed to decompose PV vs battery value.

    * Run 1 (PV = 0): its "without ES" bill is the status-quo grid-only bill.
    * Run 2 (PV + battery): "without ES" = PV-only baseline; "with ES" = full project.
    """
    zero_solar = solar * 0.0
    status_quo = run_btm(load, zero_solar, rate, ess_params, operating)
    project = run_btm(load, solar, rate, ess_params, operating)

    status_quo_bill = status_quo.annual_bill_baseline
    pv_only_bill = project.annual_bill_baseline
    project_bill = project.annual_bill_battery
    return ProjectSavings(
        status_quo_bill=status_quo_bill,
        pv_only_bill=pv_only_bill,
        project_bill=project_bill,
        pv_savings=status_quo_bill - pv_only_bill,
        battery_savings=pv_only_bill - project_bill,
        total_savings=status_quo_bill - project_bill,
        project_results=project,
    )
