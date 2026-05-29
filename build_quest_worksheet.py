"""
Generates a fillable Excel workbook documenting the QuESt (Sandia National
Laboratories) energy-storage models: Valuation, Behind-the-Meter (BTM),
Technology Selection, and Performance.

All parameters, defaults, units, market/output scenarios, governing
equations, and outputs are extracted from the QuESt source code in this repo.
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ----------------------------------------------------------------------------
# Styling helpers
# ----------------------------------------------------------------------------
TITLE_FONT   = Font(bold=True, size=16, color="FFFFFF")
H_FONT       = Font(bold=True, size=11, color="FFFFFF")
SUB_FONT     = Font(bold=True, size=12, color="1F3864")
NOTE_FONT    = Font(italic=True, size=9, color="595959")
EQ_FONT      = Font(name="Consolas", size=10, color="1F3864")

TITLE_FILL   = PatternFill("solid", fgColor="1F3864")   # dark blue
HEAD_FILL    = PatternFill("solid", fgColor="2E75B6")   # blue
FILL_FILL    = PatternFill("solid", fgColor="FFF2CC")   # light yellow (fill-in)
DEF_FILL     = PatternFill("solid", fgColor="E2EFDA")   # light green (defaults)
SCEN_FILL    = PatternFill("solid", fgColor="DDEBF7")   # light blue band

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
WRAP_C = Alignment(wrap_text=True, vertical="center", horizontal="center")


def style_header_row(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = H_FONT
        cell.fill = HEAD_FILL
        cell.alignment = WRAP_C
        cell.border = BORDER


def title_block(ws, title, subtitle, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(row=1, column=1, value=title)
    c.font = TITLE_FONT
    c.fill = TITLE_FILL
    c.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[1].height = 30
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    s = ws.cell(row=2, column=1, value=subtitle)
    s.font = NOTE_FONT
    s.alignment = WRAP


def set_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def put_table(ws, start_row, headers, rows, fill_cols=None, def_cols=None,
              row_height=None):
    """Write a header + data table. fill_cols/def_cols are 0-based column
    indices to shade yellow (fill-in) / green (default)."""
    fill_cols = fill_cols or []
    def_cols = def_cols or []
    for j, h in enumerate(headers, start=1):
        cell = ws.cell(row=start_row, column=j, value=h)
        cell.font = H_FONT
        cell.fill = HEAD_FILL
        cell.alignment = WRAP_C
        cell.border = BORDER
    r = start_row + 1
    for row in rows:
        for j, val in enumerate(row, start=1):
            cell = ws.cell(row=r, column=j, value=val)
            cell.alignment = WRAP
            cell.border = BORDER
            if (j - 1) in fill_cols:
                cell.fill = FILL_FILL
            elif (j - 1) in def_cols:
                cell.fill = DEF_FILL
        if row_height:
            ws.row_dimensions[r].height = row_height
        r += 1
    return r


wb = openpyxl.Workbook()

# ============================================================================
# 0. OVERVIEW / README
# ============================================================================
ws = wb.active
ws.title = "Overview"
set_widths(ws, [3, 26, 90])
title_block(ws, "QuESt — Sandia Energy Storage Models  ·  Fillable Worksheet",
            "Extracted from the SNL QuESt source code (snl-quest). Inputs you fill in are shaded YELLOW; "
            "model defaults are shaded GREEN. One tab per model. Last built from repo source.", 3)

ws.cell(row=4, column=2, value="Tab").font = SUB_FONT
ws.cell(row=4, column=3, value="What it covers").font = SUB_FONT
overview_rows = [
    ("Valuation – Inputs", "Energy-storage device & model parameters plus price/time-series inputs for the Valuation Optimizer. Fill in your device and prices."),
    ("Valuation – Scenarios", "The 8 market formulations (arbitrage + 7 ISO pay-for-performance/regulation markets), each with its objective (revenue) equation and required extra parameters. These are the 'output scenarios' you choose between."),
    ("Valuation – Equations", "Decision variables, state-of-charge dynamics, and all constraints shared across scenarios. Plus the outputs the model returns."),
    ("BTM – Inputs", "Behind-the-meter device parameters and the rate-structure / load / PV / net-metering inputs for the bill-savings model."),
    ("BTM – Equations & Outputs", "Bill-minimization objective, constraints, and the cost-savings outputs (demand, energy, and NEM charges with vs. without storage)."),
    ("Tech Selection", "Inputs (grid location, application, size, duration, target cost, factor weights) and the feasibility / ranking scoring formulas."),
    ("Performance", "Physics-based battery cell model parameters and the EnergyPlus co-simulation inputs/outputs (SOC, charge/discharge power, heat loss, temperatures)."),
]
r = 5
for tab, desc in overview_rows:
    a = ws.cell(row=r, column=2, value=tab); a.font = Font(bold=True); a.alignment = WRAP; a.border = BORDER
    b = ws.cell(row=r, column=3, value=desc); b.alignment = WRAP; b.border = BORDER
    ws.row_dimensions[r].height = 42
    r += 1

r += 1
legend = ws.cell(row=r, column=2, value="Legend")
legend.font = SUB_FONT
r += 1
lg = ws.cell(row=r, column=2, value="Fill-in cell"); lg.fill = FILL_FILL; lg.border = BORDER
ws.cell(row=r, column=3, value="Enter your own value here.").alignment = WRAP
r += 1
lg = ws.cell(row=r, column=2, value="Default value"); lg.fill = DEF_FILL; lg.border = BORDER
ws.cell(row=r, column=3, value="QuESt's built-in default if you leave it blank.").alignment = WRAP
r += 2
note = ws.cell(row=r, column=2, value="Note")
note.font = SUB_FONT
ws.cell(row=r+1, column=3, value=(
    "Time-series inputs (prices, load, PV) are hourly arrays. In QuESt they come from the Data Manager. "
    "Use the 'TimeSeries (paste)' columns or attach your own hourly data; the worksheet documents the meaning, "
    "units, and sign convention of each series.")).alignment = WRAP
ws.row_dimensions[r+1].height = 48
ws.freeze_panes = "A4"

# ============================================================================
# 1. VALUATION – INPUTS
# ============================================================================
ws = wb.create_sheet("Valuation – Inputs")
set_widths(ws, [34, 26, 14, 12, 12, 40, 18])
title_block(ws, "QuESt Valuation — Device & Model Parameters",
            "Maximizes net market revenue of an energy-storage device. Fill the 'Your value' column; blank = default used.", 7)

sec = ws.cell(row=4, column=1, value="A. Device & model parameters (scalars)")
sec.font = SUB_FONT
headers = ["Parameter", "Model variable", "Units", "Default", "Your value", "Description", "Used in scenarios"]
val_params = [
    ("Power rating", "Power_rating", "MW", 20, None, "Max energy charged or discharged in one hour.", "all"),
    ("Energy capacity", "Energy_capacity", "MWh", 5, None, "Usable energy storage capacity.", "all"),
    ("Self-discharge efficiency", "Self_discharge_efficiency", "frac/h", 1.00, None, "Fraction of energy retained over one time step (1.0 = no loss).", "all"),
    ("Round-trip efficiency", "Round_trip_efficiency", "frac", 0.85, None, "Fraction of charged energy actually stored.", "all"),
    ("Initial state of charge", "State_of_charge_init", "frac", 0.50, None, "SOC at start (and forced equal at end) as fraction of capacity.", "all"),
    ("Minimum state of charge", "State_of_charge_min", "frac", 0.00, None, "Lower SOC bound as fraction of capacity.", "all"),
    ("Maximum state of charge", "State_of_charge_max", "frac", 1.00, None, "Upper SOC bound as fraction of capacity.", "all"),
    ("Reserve for discharging", "Reserve_reg_min", "frac", 0.00, None, "Fraction of regulation bid reserved to raise SOC minimum.", "regulation markets"),
    ("Reserve for charging", "Reserve_reg_max", "frac", 0.00, None, "Fraction of regulation bid reserved to lower SOC maximum.", "regulation markets"),
    ("Discount / interest rate", "R", "1/h", 0.00, None, "Hourly discount rate applied as e^(-t*R) to each period's revenue.", "all"),
    ("Fraction reg-up deployed", "fraction_reg_up", "frac", 0.25, None, "Share of reg-up reserve actually dispatched (affects SOC & energy revenue).", "ercot, pjm, miso, isone, nyiso, spp, caiso"),
    ("Fraction reg-down deployed", "fraction_reg_down", "frac", 0.25, None, "Share of reg-down reserve actually dispatched.", "ercot, pjm, miso, isone, nyiso, spp, caiso"),
    ("Performance score", "perf_score", "frac", 0.95, None, "Regulation performance/accuracy score (single product).", "pjm, miso, isone, nyiso"),
    ("Performance score reg-up", "perf_score_ru", "frac", 0.95, None, "Performance score for reg-up service.", "caiso"),
    ("Performance score reg-down", "perf_score_rd", "frac", 0.95, None, "Performance score for reg-down service.", "caiso"),
    ("Make-whole adder", "Make_whole", "frac", 0.03, None, "MISO make-whole credit multiplier on regulation revenue.", "miso"),
    ("Cost of charging", "cost_charge", "$/MWh", 0.0, None, "Optional adder cost per MWh charged.", "all (optional)"),
    ("Cost of discharging", "cost_discharge", "$/MWh", 0.0, None, "Optional adder cost per MWh discharged.", "all (optional)"),
]
r = put_table(ws, 5, headers, val_params, fill_cols=[4], def_cols=[3], row_height=30)

r += 1
sec = ws.cell(row=r, column=1, value="B. Price / time-series inputs (hourly arrays)")
sec.font = SUB_FONT
r += 1
ts_headers = ["Series", "Model variable", "Units", "Sign / meaning", "Required for scenarios", "TimeSeries (paste hourly)"]
ts_rows = [
    ("Electricity price (LMP)", "price_electricity", "$/MWh", "Buy at price when charging, sell when discharging (arbitrage).", "all", ""),
    ("Regulation capacity price", "price_regulation", "$/MWh", "Capacity clearing price for regulation (pay-for-performance).", "pjm, miso, isone, nyiso", ""),
    ("Regulation-up price", "price_reg_up", "$/MWh", "Reg-up capacity clearing price.", "ercot, spp, caiso", ""),
    ("Regulation-down price", "price_reg_down", "$/MWh", "Reg-down capacity clearing price.", "ercot, spp, caiso", ""),
    ("Regulation service price", "price_reg_service", "$/MWh", "Mileage/performance ('movement') price, single product.", "pjm, isone", ""),
    ("Reg service-up price", "price_reg_serv_up", "$/MWh", "Mileage/performance price for reg-up.", "caiso", ""),
    ("Reg service-down price", "price_reg_serv_down", "$/MWh", "Mileage/performance price for reg-down.", "caiso", ""),
    ("Mileage multiplier", "mileage_mult (mi_mult)", "ratio", "Mileage ratio multiplying the service price (single product).", "pjm, isone", ""),
    ("Mileage multiplier reg-up", "mileage_mult_ru", "ratio", "Mileage ratio for reg-up service.", "caiso", ""),
    ("Mileage multiplier reg-down", "mileage_mult_rd", "ratio", "Mileage ratio for reg-down service.", "caiso", ""),
]
r = put_table(ws, r, ts_headers, ts_rows, fill_cols=[5], row_height=30)
ws.freeze_panes = "A5"

# ============================================================================
# 2. VALUATION – SCENARIOS (market types + objective equations)
# ============================================================================
ws = wb.create_sheet("Valuation – Scenarios")
set_widths(ws, [6, 22, 24, 70, 34])
title_block(ws, "QuESt Valuation — Market Scenarios (output scenarios)",
            "Pick ONE market_type. Each maximizes net revenue over the horizon: max  Σ_t (objective_t)·e^(-t·R). "
            "Arbitrage term = price[t]·(q_d[t] − q_r[t]) in every scenario; the regulation term differs below.", 5)

headers = ["Pick", "market_type", "Market", "Objective per period t  (added to the arbitrage term, all ×e^(−t·R))", "Extra parameters needed"]
scen_rows = [
    ("☐", "arbitrage", "Energy arbitrage only", "price[t]·q_d[t] − price[t]·q_r[t]", "—"),
    ("☐", "ercot_arbreg", "ERCOT arbitrage + regulation", "+ price_reg_up[t]·q_ru[t] + price_reg_down[t]·q_rd[t] + price[t]·q_ru[t]·frac_up[t] − price[t]·q_rd[t]·frac_down[t]", "price_reg_up, price_reg_down, fraction_reg_up/down"),
    ("☐", "pjm_pfp", "PJM pay-for-performance", "+ q_reg[t]·perf_score[t]·( mi_mult[t]·price_reg_service[t] + price_regulation[t] )", "price_regulation, price_reg_service, mileage_mult, perf_score, frac_up/down"),
    ("☐", "miso_pfp", "MISO pay-for-performance", "+ (1 + Make_whole)·q_reg[t]·perf_score[t]·price_regulation[t]", "price_regulation, perf_score, Make_whole, frac_up/down"),
    ("☐", "isone_pfp", "ISO-NE pay-for-performance", "+ q_reg[t]·( mi_mult[t]·price_reg_service[t] + price_regulation[t] )·perf_score[t]", "price_regulation, price_reg_service, mileage_mult, frac_up/down"),
    ("☐", "nyiso_pfp", "NYISO pay-for-performance", "+ price[t]·frac_up[t]·q_reg[t] − price[t]·frac_down[t]·q_reg[t] + q_reg[t]·price_regulation[t]·(1 − 1.1·(1 − perf_score[t]))", "price_regulation, perf_score, frac_up/down"),
    ("☐", "spp_pfp", "SPP pay-for-performance", "+ price_reg_up[t]·q_ru[t] + price_reg_down[t]·q_rd[t] + price[t]·q_ru[t]·frac_up[t] − price[t]·q_rd[t]·frac_down[t]", "price_reg_up, price_reg_down, frac_up/down"),
    ("☐", "caiso_pfp", "CAISO pay-for-performance", "+ price_reg_up[t]·q_ru[t] + price_reg_down[t]·q_rd[t] + price[t]·q_ru[t]·frac_up[t] − price[t]·q_rd[t]·frac_down[t] + perf_score_ru[t]·mi_mult_ru[t]·price_reg_serv_up[t] + perf_score_rd[t]·mi_mult_rd[t]·price_reg_serv_down[t]", "price_reg_up/down, price_reg_serv_up/down, mileage_mult_ru/rd, perf_score_ru/rd, frac_up/down"),
]
r = put_table(ws, 4, headers, scen_rows, fill_cols=[0], row_height=58)
for rr in range(5, r):
    ws.cell(row=rr, column=4).font = EQ_FONT
ws.freeze_panes = "A4"

# ============================================================================
# 3. VALUATION – EQUATIONS (vars, SOC, constraints, outputs)
# ============================================================================
ws = wb.create_sheet("Valuation – Equations")
set_widths(ws, [30, 18, 70])
title_block(ws, "QuESt Valuation — Variables, Constraints & Outputs",
            "Reference (not fill-in). Optimizer = Pyomo LP solved with the chosen solver (default glpk). t indexes hourly periods.", 3)

ws.cell(row=4, column=1, value="A. Decision variables (per period t)").font = SUB_FONT
r = put_table(ws, 5, ["Variable", "Symbol", "Meaning (units MWh unless noted)"], [
    ("Charge (arbitrage)", "q_r[t]", "Energy bought/charged for arbitrage."),
    ("Discharge (arbitrage)", "q_d[t]", "Energy sold/discharged for arbitrage."),
    ("Regulation up", "q_ru[t]", "Capacity offered into reg-up (two-product markets)."),
    ("Regulation down", "q_rd[t]", "Capacity offered into reg-down (two-product markets)."),
    ("Regulation (single)", "q_reg[t]", "Capacity offered into single-product regulation."),
    ("State of charge", "s[t]", "Stored energy at time t (MWh)."),
], row_height=24)

r += 1
ws.cell(row=r, column=1, value="B. State-of-charge dynamics & constraints").font = SUB_FONT
r += 1
eqs = [
    ("SOC balance (arbitrage)", "η_sd·s[t] + η_rt·q_r[t] − q_d[t] = s[t+1]"),
    ("SOC balance (regulation)", "η_sd·s[t] + η_rt·q_r[t] − q_d[t] + η_rt·frac_down·q_(reg|rd)[t] − frac_up·q_(reg|ru)[t] = s[t+1]"),
    ("Initial SOC", "s[0] = State_of_charge_init · Energy_capacity"),
    ("Final SOC", "s[last] = State_of_charge_init · Energy_capacity"),
    ("SOC minimum", "s[t] ≥ State_of_charge_min · Energy_capacity   (+ Reserve_reg_min·q_reg for reg markets)"),
    ("SOC maximum", "s[t] ≤ State_of_charge_max · Energy_capacity   (− η_rt·Reserve_reg_max·q_reg for reg markets)"),
    ("Power limit (arbitrage)", "Power_rating ≥ q_r[t] + q_d[t]"),
    ("Power limit (1-product)", "Power_rating ≥ q_r[t] + q_d[t] + q_reg[t]"),
    ("Power limit (2-product)", "Power_rating ≥ q_r[t] + q_d[t] + q_ru[t] + q_rd[t]"),
]
for name, eq in eqs:
    a = ws.cell(row=r, column=1, value=name); a.alignment = WRAP; a.border = BORDER; a.font = Font(bold=True)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    b = ws.cell(row=r, column=2, value=eq); b.alignment = WRAP; b.border = BORDER; b.font = EQ_FONT
    ws.cell(row=r, column=3).border = BORDER
    ws.row_dimensions[r].height = 22
    r += 1
ws.cell(row=r, column=1, value="η_sd = Self_discharge_efficiency, η_rt = Round_trip_efficiency").font = NOTE_FONT

r += 2
ws.cell(row=r, column=1, value="C. Outputs returned").font = SUB_FONT
r += 1
r = put_table(ws, r, ["Output", "Type", "Description"], [
    ("q_r, q_d, q_ru, q_rd, q_reg", "hourly series", "Optimal charge/discharge/regulation schedule."),
    ("state of charge", "hourly series", "SOC trajectory (MWh)."),
    ("price of electricity", "hourly series", "Echo of the input LMP."),
    ("rev_arb", "cumulative series", "Cumulative arbitrage revenue ($)."),
    ("rev_reg", "cumulative series", "Cumulative regulation revenue ($)."),
    ("revenue", "cumulative series", "rev_arb + rev_reg ($)."),
    ("gross_revenue", "scalar", "Total net revenue over the horizon ($) = revenue[-1]."),
], row_height=22)
ws.freeze_panes = "A4"

# ============================================================================
# 4. BTM – INPUTS
# ============================================================================
ws = wb.create_sheet("BTM – Inputs")
set_widths(ws, [30, 26, 12, 14, 14, 48])
title_block(ws, "QuESt BTM — Behind-the-Meter Cost-Savings: Inputs",
            "Minimizes a customer's electricity bill (energy + demand charges, net of net-metering) using storage + PV.", 6)

ws.cell(row=4, column=1, value="A. Device parameters").font = SUB_FONT
btm_dev = [
    ("Energy capacity", "Energy_capacity", "kWh", 100, None, "Max energy the ESS can store."),
    ("Power rating", "Power_rating", "kW", 100, None, "Max charge/discharge rate."),
    ("Transformer rating", "Transformer_rating", "kW", 1000000, None, "Max power that can be exchanged with the grid."),
    ("Self-discharge efficiency", "Self_discharge_efficiency", "%/h", 100, None, "% of stored energy retained hourly."),
    ("Round-trip efficiency", "Round_trip_efficiency", "%", 85, None, "% of charged energy retained."),
    ("Minimum state of charge", "State_of_charge_min", "%", 0, None, "Min SOC as % of capacity."),
    ("Maximum state of charge", "State_of_charge_max", "%", 100, None, "Max SOC as % of capacity."),
    ("Initial state of charge", "State_of_charge_init", "%", 50, None, "Starting (and final) SOC as % of capacity."),
]
r = put_table(ws, 5, ["Parameter", "Model variable", "Units", "Default", "Your value", "Description"],
              btm_dev, fill_cols=[4], def_cols=[3], row_height=24)

r += 1
ws.cell(row=r, column=1, value="B. Rate structure, profiles & net metering").font = SUB_FONT
r += 1
btm_rate = [
    ("TOU energy rate", "tou_energy_rate", "$/kWh", "List of energy rates, one per TOU period.", ""),
    ("TOU energy schedule", "tou_energy_schedule", "index", "For each hour of the month, which TOU energy-rate period applies.", ""),
    ("TOU demand rate", "tou_demand_rate", "$/kW", "List of demand charges, one per TOU demand period.", ""),
    ("TOU demand schedule", "tou_demand_schedule", "index", "For each hour, which TOU demand period applies.", ""),
    ("Flat demand rate", "flat_demand_rate", "$/kW", "Monthly (12-value) flat demand charge on peak power.", ""),
    ("Net-metering type", "nem_type", "0/1/2", "0 = none, 1 = NEM 1.0, 2 = NEM 2.0.", ""),
    ("Net-metering sell rate", "nem_rate", "$/kWh", "Export/sell rate credited for net energy exported.", ""),
    ("Load profile", "load_profile", "kW", "Hourly building/customer demand.", ""),
    ("PV profile", "pv_profile", "kW", "Hourly on-site PV generation.", ""),
    ("Cost of charging", "cost_charge", "$/kWh", "Optional charging cost adder.", ""),
    ("Cost of discharging", "cost_discharge", "$/kWh", "Optional discharging cost adder.", ""),
]
r = put_table(ws, r, ["Input", "Model variable", "Units", "Description", "TimeSeries / values (paste)"],
              btm_rate, fill_cols=[4], row_height=26)
ws.freeze_panes = "A5"

# ============================================================================
# 5. BTM – EQUATIONS & OUTPUTS
# ============================================================================
ws = wb.create_sheet("BTM – Equations & Outputs")
set_widths(ws, [30, 18, 72])
title_block(ws, "QuESt BTM — Objective, Constraints & Outputs",
            "Objective MINIMIZES the monthly bill. pnet[t] = load[t] − pv[t]. Solved as an LP (default glpk).", 3)

ws.cell(row=4, column=1, value="A. Objective (minimize total bill)").font = SUB_FONT
ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=3)
c = ws.cell(row=5, column=1, value=(
    "bill = pfpk·flat_demand_rate + Σ_p ptpk[p]·tou_demand_rate[p] "
    "+ Σ_t [ xnet[t]·(tou_energy_rate[t] − nem_sell_rate[t]) + (pnet[t] + pcha[t] − pdis[t])·nem_sell_rate[t] ]"))
c.font = EQ_FONT; c.alignment = WRAP; c.border = BORDER
ws.row_dimensions[5].height = 44

ws.cell(row=7, column=1, value="B. Decision variables").font = SUB_FONT
r = put_table(ws, 8, ["Variable", "Symbol", "Meaning"], [
    ("Charge power", "pcha[t]", "Charging power at hour t (kW), bounded by Power_rating."),
    ("Discharge power", "pdis[t]", "Discharging power at hour t (kW), bounded by Power_rating."),
    ("State of charge", "s[t]", "Stored energy (kWh), bounded by SOC min/max."),
    ("Flat peak demand", "pfpk", "Billing peak net power across the month (kW)."),
    ("TOU peak demand", "ptpk[p]", "Billing peak net power within TOU demand period p (kW)."),
    ("Net export", "xnet[t]", "Non-negative net power exchanged for NEM accounting (kW)."),
], row_height=24)

r += 1
ws.cell(row=r, column=1, value="C. Constraints").font = SUB_FONT
r += 1
for name, eq in [
    ("SOC dynamics", "η_sd·s[t−1] + η_rt·pcha[t] − pdis[t] = s[t]   (s[−1]=SOC_init·E_cap)"),
    ("Final SOC", "s[last] = State_of_charge_init · Energy_capacity"),
    ("Flat peak demand", "pnet[t] + pcha[t] − pdis[t] − pfpk ≤ 0"),
    ("TOU peak demand", "mask_p[t]·(pnet[t] + pcha[t] − pdis[t]) ≤ ptpk[p]"),
    ("NEM net export", "pnet[t] + pcha[t] − pdis[t] ≤ xnet[t]"),
]:
    a = ws.cell(row=r, column=1, value=name); a.font = Font(bold=True); a.border = BORDER; a.alignment = WRAP
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    b = ws.cell(row=r, column=2, value=eq); b.font = EQ_FONT; b.border = BORDER; b.alignment = WRAP
    ws.cell(row=r, column=3).border = BORDER
    ws.row_dimensions[r].height = 22
    r += 1

r += 1
ws.cell(row=r, column=1, value="D. Outputs returned").font = SUB_FONT
r += 1
r = put_table(ws, r, ["Output", "Type", "Description"], [
    ("Pload, Ppv", "hourly series", "Echo of input load and PV."),
    ("Pcharge, Pdischarge, Ptotal", "hourly series", "Optimal storage dispatch and net facility power."),
    ("state of charge", "hourly series", "SOC trajectory (kWh)."),
    ("demand charge with/without ES", "scalars", "Flat + TOU demand charges, with vs. without storage."),
    ("energy charge with/without ES", "scalars", "TOU energy charges, with vs. without storage."),
    ("NEM charge with/without ES", "scalars", "Net-metering credits (negative), with vs. without storage."),
    ("Total bill savings", "scalar", "Difference between without-ES and with-ES total bill ($)."),
], row_height=24)
ws.freeze_panes = "A4"

# ============================================================================
# 6. TECH SELECTION
# ============================================================================
ws = wb.create_sheet("Tech Selection")
set_widths(ws, [26, 22, 16, 50, 26])
title_block(ws, "QuESt Technology Selection — Inputs & Scoring",
            "Ranks energy-storage technologies by a feasibility score for your application. Fill the 'Your choice/value' column.", 5)

ws.cell(row=4, column=1, value="A. Inputs").font = SUB_FONT
ts_in = [
    ("Grid location", "location", "choice", "Where the system connects.", "Transmission/central | Distribution | BTM: commercial/industrial | BTM: residential"),
    ("Application", "application", "choice", "Use case (e.g. peak shaving, deferral, arbitrage); options depend on location.", "(from application DB)"),
    ("System size", "system_size", "choice", "Nameplate size class.", "Wholesale (100 MW) | Utility (10 MW) | Distribution & microgrid (1 MW) | Commercial & industrial (100 kW) | Residential (10 kW)"),
    ("Discharge duration", "discharge_duration", "choice", "Hours of discharge at rated power.", "Up to 0.5 hr | 1–10 hrs"),
    ("Type of application", "app_type", "choice", "Energy- vs power-oriented (sets target-cost units).", "Energy | Power"),
    ("Target cost", "target_cost", "$/kWh or $/kW", "Desired capital cost; cost score = 0.5 at this value.", "Energy default 1000 $/kWh; Power default 1500 $/kW"),
    ("Application weight", "weight_application", "0–1", "Weight of application score (default equal).", "default 1.0"),
    ("Location weight", "weight_location", "0–1", "Weight of location score.", "default 1.0"),
    ("Cost weight", "weight_cost", "0–1", "Weight of cost score (set 0 to ignore).", "default 1.0"),
    ("Maturity weight", "weight_maturity", "0–1", "Maturity multiplier weight.", "default 1.0"),
]
r = put_table(ws, 5, ["Input", "Model variable", "Type", "Description", "Your choice/value"],
              ts_in, fill_cols=[4], row_height=34)

r += 1
ws.cell(row=r, column=1, value="B. Scoring formulas").font = SUB_FONT
r += 1
for name, eq in [
    ("Cost score", "cost_score = target_cost / (capital_cost + target_cost)   (= 0.5 at target_cost)"),
    ("Total feasibility", "total_score = weighted_geometric_mean(application, location, cost) × maturity_score"),
    ("Weights", "Each factor weighted; a weight of 0 removes that factor. Maturity caps market-readiness."),
]:
    a = ws.cell(row=r, column=1, value=name); a.font = Font(bold=True); a.border = BORDER; a.alignment = WRAP
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
    b = ws.cell(row=r, column=2, value=eq); b.font = EQ_FONT; b.border = BORDER; b.alignment = WRAP
    for cc in range(3, 6):
        ws.cell(row=r, column=cc).border = BORDER
    ws.row_dimensions[r].height = 22
    r += 1

r += 1
ws.cell(row=r, column=1, value="C. Output: ranking table (one row per technology)").font = SUB_FONT
r += 1
r = put_table(ws, r, ["Technology", "Application score", "Location score", "Cost score", "Maturity score"], [
    ("(e.g. Li-ion, Lead-carbon, Nickel, Flywheel, Flow, …)", "", "", "", ""),
], fill_cols=[1, 2, 3, 4], row_height=22)
ws.cell(row=r, column=1, value="The model also reports a Total score and a feasibility plot; higher = better fit.").font = NOTE_FONT
ws.freeze_panes = "A5"

# ============================================================================
# 7. PERFORMANCE
# ============================================================================
ws = wb.create_sheet("Performance")
set_widths(ws, [30, 20, 14, 14, 14, 50])
title_block(ws, "QuESt Performance — Battery + Building Co-Simulation",
            "Physics-based cell model co-simulated with EnergyPlus to evaluate thermal performance in a climate/building.", 6)

ws.cell(row=4, column=1, value="A. Battery cell model parameters").font = SUB_FONT
perf = [
    ("Energy capacity", "eCap", "—", None, None, "Pack energy capacity."),
    ("Power rating", "pRat", "—", None, None, "Pack power rating."),
    ("Cells in series", "n_s", "count", None, None, "Number of series-connected cells."),
    ("Cells in parallel", "n_p", "count", None, None, "Number of parallel strings."),
    ("Charge rate", "q_rate", "—", 2.5, None, "Cell charge-rate parameter."),
    ("Rated voltage", "v_rate", "V", 3.6, None, "Nominal cell voltage."),
    ("Internal resistance", "r", "ohm", 0.02, None, "Cell ohmic resistance (joule heating)."),
    ("Polarization constant", "k", "—", 0.005, None, "Polarization/SOC-dependent heating constant."),
    ("Time step", "tau", "h", 0.25, None, "Simulation time step (hours)."),
]
r = put_table(ws, 5, ["Parameter", "Model variable", "Units", "Default", "Your value", "Description"],
              perf, fill_cols=[4], def_cols=[3], row_height=24)

r += 1
ws.cell(row=r, column=1, value="B. Simulation (co-simulation) inputs").font = SUB_FONT
r += 1
r = put_table(ws, r, ["Input", "Model variable", "Type", "Description", "", "Your value / file"], [
    ("Building model", "idf", "EnergyPlus .idf", "Building energy model the ESS sits in.", "", ""),
    ("Weather", "weather", "EPW file", "Climate file (from NSRDB via Data Manager).", "", ""),
    ("Heating setpoint", "h_setpoint", "°C", "HVAC heating setpoint.", "", ""),
    ("Cooling setpoint", "c_setpoint", "°C", "HVAC cooling setpoint.", "", ""),
    ("Load profile", "load", "kW series", "Demand seen by the storage system.", "", ""),
    ("Charge/discharge profile", "charge_discharge", "kW series", "Dispatch schedule to simulate.", "", ""),
], fill_cols=[5], row_height=24)

r += 1
ws.cell(row=r, column=1, value="C. Outputs returned").font = SUB_FONT
r += 1
r = put_table(ws, r, ["Output", "Type", "Description"], [
    ("SOC", "hourly series", "Battery state of charge."),
    ("Charge Power / Discharge Power", "hourly series", "Power flows during simulation."),
    ("Heat Loss", "hourly series", "Battery + power-electronics heat dissipation."),
    ("EnergyPlus variables", "hourly series", "Zone/battery temperatures and HVAC response."),
], row_height=24)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
ws.cell(row=r, column=1, value="Note: the Performance tool requires EnergyPlus installed in the QuESt directory; weather files come from the Data Manager (NSRDB).").font = NOTE_FONT
ws.freeze_panes = "A5"

out = "/home/user/snl-quest/QuESt_Sandia_Models_Worksheet.xlsx"
wb.save(out)
print("Saved:", out)
print("Sheets:", wb.sheetnames)
