"""
Central configuration and path handling for the Castellan Farm BESS analysis.

This module resolves all project paths relative to the ``castellan_analysis``
folder (so the workflow runs regardless of the current working directory) and
provides small helpers for loading the editable JSON assumption files.

Nothing here talks to QuESt directly; it is pure plumbing used by every other
script in ``scripts/``.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
# scripts/  ->  castellan_analysis/  (project root for this analysis)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "input_data"
RAW_DIR = INPUT_DIR / "raw"
ASSUMPTIONS_DIR = PROJECT_ROOT / "assumptions"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORT_DIR = PROJECT_ROOT / "reports"

# Generated / curated input files (produced by prepare_inputs.py)
LOAD_CSV = INPUT_DIR / "farm_load_8760.csv"
SOLAR_CSV = INPUT_DIR / "solar_production.csv"
BOM_CSV = INPUT_DIR / "bom.csv"
RATE_JSON = INPUT_DIR / "rate_structure.json"

# Raw uploads (source of truth, converted by prepare_inputs.py)
RAW_USAGE_XLSX = RAW_DIR / "Castellan_Historical_Usage.xlsx"
RAW_BOM_XLSX = RAW_DIR / "BOM_Residential_Solar_BESS_CostDown.xlsx"

# Editable assumption files
BATTERY_JSON = ASSUMPTIONS_DIR / "battery.json"
FINANCIAL_JSON = ASSUMPTIONS_DIR / "financial.json"
OPERATING_JSON = ASSUMPTIONS_DIR / "operating.json"
RATE_ASSUMPTIONS_JSON = ASSUMPTIONS_DIR / "rate_assumptions.json"

# Location of the bundled QuESt BTM library so its modules can be imported.
QUEST_BTM_LIB = PROJECT_ROOT.parent / "quest" / "snl_libraries" / "snl_btm"


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file, raising a clear error if it is missing or malformed."""
    if not Path(path).is_file():
        raise FileNotFoundError(
            f"Required configuration file not found: {path}\n"
            "Run `python scripts/prepare_inputs.py` first, or restore the file."
        )
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse JSON file {path}: {exc}") from exc


def ensure_output_dirs() -> None:
    """Create the outputs/ and reports/ folders if they do not yet exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def register_quest_btm_path() -> None:
    """Add the bundled QuESt BTM library to ``sys.path`` for ``import btm``."""
    import sys

    lib = str(QUEST_BTM_LIB)
    if QUEST_BTM_LIB.is_dir() and lib not in sys.path:
        sys.path.insert(0, lib)
