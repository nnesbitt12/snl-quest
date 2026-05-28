"""
Loading and validation of the curated analysis inputs.

All four primary inputs are loaded here with defensive validation:

* farm interval load           -> :func:`load_load_profile`
* solar production             -> :func:`load_solar_profile`
* bill of materials / CAPEX    -> :func:`load_bom`
* QuESt-format rate structure  -> :func:`load_rate_structure`

The loaders raise specific, human-readable exceptions for the failure modes
called out in the project brief: missing files/data, bad date formats, missing
BOM values, and mismatched time intervals between load and solar.
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from config import LOAD_CSV, SOLAR_CSV, BOM_CSV, RATE_JSON, load_json


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class DataValidationError(Exception):
    """Base class for all input-validation problems."""


class MissingDataError(DataValidationError):
    """A required file, column, or value is missing."""


class DateFormatError(DataValidationError):
    """A timestamp column could not be parsed as dates."""


class IntervalMismatchError(DataValidationError):
    """Load and solar series do not share a compatible time index."""


class BomError(DataValidationError):
    """The bill of materials is structurally invalid."""


# ---------------------------------------------------------------------------
# Time-series loaders
# ---------------------------------------------------------------------------
def _read_timeseries_csv(path: Path, value_label: str) -> pd.Series:
    """Read a two-column ``datetime,value`` CSV into an hourly float Series."""
    path = Path(path)
    if not path.is_file():
        raise MissingDataError(
            f"{value_label} file not found: {path}\n"
            "Run `python scripts/prepare_inputs.py` to generate it, or place "
            "your own CSV there (columns: datetime, value)."
        )

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001 - surface any pandas read error clearly
        raise DataValidationError(f"Could not read {path}: {exc}") from exc

    if df.shape[1] < 2:
        raise MissingDataError(
            f"{value_label} file {path} must have at least two columns "
            "(datetime, value)."
        )

    ts_col, val_col = df.columns[0], df.columns[-1]

    # Parse timestamps. Errors='raise' is caught and re-raised with context.
    try:
        ts = pd.to_datetime(df[ts_col], errors="raise")
    except Exception as exc:  # noqa: BLE001
        raise DateFormatError(
            f"Could not parse the timestamp column '{ts_col}' in {path} as "
            f"dates. First values: {df[ts_col].head(3).tolist()}.\n"
            "Use an ISO format such as 2025-01-01 00:00:00."
        ) from exc

    values = pd.to_numeric(df[val_col], errors="coerce")
    n_bad = int(values.isna().sum())
    if n_bad:
        raise MissingDataError(
            f"{value_label} column '{val_col}' in {path} has {n_bad} "
            "missing/non-numeric values. Clean the file and retry."
        )

    series = pd.Series(values.to_numpy(dtype=float), index=pd.DatetimeIndex(ts))
    series = series[~series.index.duplicated(keep="first")].sort_index()
    series.name = value_label
    return series


def load_load_profile(path: Path = LOAD_CSV) -> pd.Series:
    """Load the hourly farm load profile (kW), indexed by timestamp."""
    series = _read_timeseries_csv(path, "load_kW")
    if (series < 0).any():
        raise DataValidationError(
            f"Load profile {path} contains negative kW values, which are not "
            "physical for a consumption profile."
        )
    if not 8000 <= len(series) <= 8784:
        # Not fatal, but almost always indicates a problem worth flagging.
        raise DataValidationError(
            f"Load profile {path} has {len(series)} hourly rows; expected ~8760 "
            "for a full year. Re-generate with prepare_inputs.py."
        )
    return series


def load_solar_profile(path: Path = SOLAR_CSV) -> pd.Series:
    """Load the hourly solar production profile (kW), indexed by timestamp."""
    series = _read_timeseries_csv(path, "pv_kW")
    if (series < -1e-6).any():
        raise DataValidationError(
            f"Solar profile {path} contains negative kW values."
        )
    return series.clip(lower=0.0)


def align_load_and_solar(
    load: pd.Series, solar: pd.Series
) -> Tuple[pd.Series, pd.Series]:
    """Validate and align the load and solar series onto a common hourly index.

    Raises :class:`IntervalMismatchError` when the two series cannot be made to
    share a compatible hourly index (different cadence, no overlap, etc.).
    """

    def _infer_freq_hours(idx: pd.DatetimeIndex) -> float:
        if len(idx) < 2:
            raise IntervalMismatchError("A profile must have at least 2 rows.")
        deltas = np.diff(idx.values).astype("timedelta64[m]").astype(float)
        return float(np.median(deltas)) / 60.0

    load_step = _infer_freq_hours(load.index)
    solar_step = _infer_freq_hours(solar.index)
    if abs(load_step - solar_step) > 1e-6:
        raise IntervalMismatchError(
            f"Load interval (~{load_step:g} h) and solar interval "
            f"(~{solar_step:g} h) differ. Resample both to the same cadence "
            "(the workflow expects hourly data) before running."
        )

    # Align solar onto the load index. Missing hours -> 0 PV (e.g. night/edges).
    aligned_solar = solar.reindex(load.index)
    missing = int(aligned_solar.isna().sum())
    if missing > 0.05 * len(load):
        raise IntervalMismatchError(
            f"Solar profile is missing {missing} of {len(load)} hours present in "
            "the load profile (>5%). The two series do not overlap enough to "
            "align reliably. Check that both cover the same model year."
        )
    aligned_solar = aligned_solar.fillna(0.0)
    aligned_solar.name = "pv_kW"
    return load, aligned_solar


# ---------------------------------------------------------------------------
# Bill of materials
# ---------------------------------------------------------------------------
REQUIRED_BOM_COLUMNS = {"item", "category", "qty", "unit_cost", "total_cost", "included"}


def load_bom(path: Path = BOM_CSV) -> pd.DataFrame:
    """Load and validate the structured bill of materials.

    Required columns: item, category, qty, unit_cost, total_cost, included.
    Missing ``total_cost`` values are back-filled from ``qty * unit_cost`` when
    possible; otherwise a :class:`BomError` is raised.
    """
    path = Path(path)
    if not path.is_file():
        raise MissingDataError(
            f"BOM file not found: {path}. Run prepare_inputs.py to generate it."
        )

    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing_cols = REQUIRED_BOM_COLUMNS - set(df.columns)
    if missing_cols:
        raise BomError(
            f"BOM {path} is missing required columns: {sorted(missing_cols)}.\n"
            f"Found columns: {list(df.columns)}"
        )

    df["item"] = df["item"].astype(str).str.strip()
    df = df[df["item"].astype(bool) & (df["item"].str.lower() != "nan")].copy()

    df["qty_num"] = pd.to_numeric(df["qty"], errors="coerce")
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce")
    df["total_cost"] = pd.to_numeric(df["total_cost"], errors="coerce")

    # Back-fill total_cost from qty * unit_cost where possible.
    fill_mask = df["total_cost"].isna() & df["unit_cost"].notna() & df["qty_num"].notna()
    df.loc[fill_mask, "total_cost"] = df.loc[fill_mask, "qty_num"] * df.loc[fill_mask, "unit_cost"]

    still_missing = df[df["total_cost"].isna()]
    if not still_missing.empty:
        raise BomError(
            "These BOM line items have no usable cost (total_cost missing and "
            "cannot be computed from qty*unit_cost):\n"
            + ", ".join(still_missing["item"].tolist())
        )

    # Normalise the boolean 'included' column.
    df["included"] = (
        df["included"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes", "y", "capex"})
    )
    return df


# ---------------------------------------------------------------------------
# Rate structure
# ---------------------------------------------------------------------------
def load_rate_structure(path: Path = RATE_JSON) -> dict:
    """Load the QuESt-format rate structure JSON and validate its schema."""
    rate = load_json(path)
    required = {"energy rate structure", "demand rate structure", "net metering"}
    missing = required - set(rate.keys())
    if missing:
        raise DataValidationError(
            f"Rate structure {path} is missing top-level keys: {sorted(missing)}.\n"
            "Re-generate it with prepare_inputs.py."
        )

    ers = rate["energy rate structure"]
    for key in ("weekday schedule", "weekend schedule", "energy rates"):
        if key not in ers:
            raise DataValidationError(
                f"Rate structure energy section missing '{key}'."
            )
    for sched_name in ("weekday schedule", "weekend schedule"):
        sched = ers[sched_name]
        if len(sched) != 12 or any(len(month) != 24 for month in sched):
            raise DataValidationError(
                f"Energy '{sched_name}' must be a 12x24 array (got "
                f"{len(sched)} months)."
            )
    return rate
