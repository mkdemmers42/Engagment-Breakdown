import re
import html
from io import BytesIO
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# Non-Billable Caseload Review Dashboard v2
# Employee-Specific Supervisory Accountability Dashboard
# Executive Command Center - No Sidebar
# ============================================================

st.set_page_config(
    page_title="Non-Billable Caseload Review Dashboard v2",
    page_icon="📋",
    layout="wide",
)

# ----------------------------
# Styling
# ----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 32%),
            radial-gradient(circle at top right, rgba(20, 184, 166, 0.14), transparent 30%),
            radial-gradient(circle at bottom left, rgba(168, 85, 247, 0.10), transparent 36%),
            linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%);
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }

    .main-title {
        padding: 1.45rem 1.65rem;
        border-radius: 26px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, .96), rgba(30, 41, 59, .88)),
            radial-gradient(circle at top right, rgba(56, 189, 248, .14), transparent 45%);
        border: 1px solid rgba(148, 163, 184, .32);
        box-shadow: 0 18px 45px rgba(0,0,0,.42);
        margin-bottom: 1rem;
    }

    .main-title h1 {
        margin: 0;
        font-size: 2.35rem;
        letter-spacing: .01em;
        color: #f8fafc;
        font-weight: 900;
    }

    .main-title p {
        margin: .45rem 0 0 0;
        color: #cbd5e1;
        font-size: 1.05rem;
    }

    .review-header {
        background:
            linear-gradient(135deg, rgba(15,23,42,.75), rgba(30,41,59,.55));
        border: 1px solid rgba(148,163,184,.24);
        padding: 16px 20px;
        border-radius: 20px;
        margin: 16px 0 20px 0;
        color: #e2e8f0;
        font-size: 16px;
        box-shadow: 0 12px 28px rgba(0,0,0,.24);
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        border-radius: 22px;
        padding: 1.15rem .95rem;
        min-height: 128px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 1px solid rgba(203, 213, 225, .24);
        background:
            radial-gradient(circle at center, var(--glow-soft), transparent 62%),
            linear-gradient(135deg, rgba(15, 23, 42, .92), rgba(30, 41, 59, .78));
        box-shadow:
            0 0 0 1px var(--outline),
            0 0 12px var(--glow),
            0 14px 30px rgba(0,0,0,.30);
    }

    .metric-card::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 22px;
        background:
            linear-gradient(135deg, rgba(255,255,255,.08), transparent 45%);
        pointer-events: none;
    }

    .metric-icon {
        position: absolute;
        top: 12px;
        right: 14px;
        font-size: 1.15rem;
        opacity: .82;
        filter: drop-shadow(0 0 8px var(--glow));
    }

    .metric-value {
        font-size: 2.6rem;
        font-weight: 950;
        color: #ffffff;
        line-height: 1;
        margin-bottom: .55rem;
        letter-spacing: -.03em;
    }

    .metric-label {
        font-size: .88rem;
        color: #dbeafe;
        text-transform: uppercase;
        letter-spacing: .075em;
        font-weight: 800;
        line-height: 1.25;
    }

    .metric-blue {
        --outline: rgba(96, 165, 250, .48);
        --glow: rgba(59, 130, 246, .34);
        --glow-soft: rgba(59, 130, 246, .20);
    }

    .metric-indigo {
        --outline: rgba(129, 140, 248, .48);
        --glow: rgba(99, 102, 241, .34);
        --glow-soft: rgba(99, 102, 241, .20);
    }

    .metric-teal {
        --outline: rgba(45, 212, 191, .45);
        --glow: rgba(20, 184, 166, .32);
        --glow-soft: rgba(20, 184, 166, .20);
    }

    .metric-green {
        --outline: rgba(74, 222, 128, .48);
        --glow: rgba(34, 197, 94, .34);
        --glow-soft: rgba(34, 197, 94, .22);
    }

    .metric-orange {
        --outline: rgba(251, 146, 60, .52);
        --glow: rgba(249, 115, 22, .36);
        --glow-soft: rgba(249, 115, 22, .23);
    }

    .metric-rose {
        --outline: rgba(251, 113, 133, .52);
        --glow: rgba(244, 63, 94, .36);
        --glow-soft: rgba(244, 63, 94, .23);
    }

    .metric-red {
        --outline: rgba(248, 113, 113, .58);
        --glow: rgba(239, 68, 68, .42);
        --glow-soft: rgba(239, 68, 68, .26);
    }

    .section-box {
        padding: 1.1rem;
        border-radius: 22px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, .78), rgba(30, 41, 59, .56));
        border: 1px solid rgba(148, 163, 184, .22);
        margin-top: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 14px 34px rgba(0,0,0,.28);
    }

    .chart-panel {
        padding: 1.1rem;
        border-radius: 22px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, .74), rgba(30, 41, 59, .52));
        border: 1px solid rgba(148, 163, 184, .22);
        box-shadow: 0 14px 34px rgba(0,0,0,.25);
        margin-bottom: 1rem;
    }

    div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(96, 165, 250, .20);
    background: rgba(15, 23, 42, .72) !important;
    box-shadow: 0 8px 20px rgba(0,0,0,.22);
}

div[data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] {
    background: rgba(15, 23, 42, .72) !important;
}

div[data-testid="stDataFrame"] div[role="grid"] {
    background: rgba(15, 23, 42, .72) !important;
    color: #e5e7eb !important;
}

div[data-testid="stDataFrame"] div[role="columnheader"] {
    background: rgba(30, 41, 59, .95) !important;
    color: #f8fafc !important;
    font-weight: 800 !important;
    border-bottom: 1px solid rgba(96,165,250,.18) !important;
}

div[data-testid="stDataFrame"] div[role="gridcell"] {
    background: rgba(15, 23, 42, .72) !important;
    color: #dbeafe !important;
    border-color: rgba(148,163,184,.08) !important;
}

    .stButton > button {
    border-radius: 18px;
    border: 1px solid rgba(96, 165, 250, .38);
    background:
        radial-gradient(circle at center, rgba(59, 130, 246, .14), transparent 62%),
        linear-gradient(135deg, rgba(15, 23, 42, .88), rgba(30, 41, 59, .72));
    color: #f8fafc;
    font-weight: 900;
    min-height: 58px;
    box-shadow:
        0 0 0 1px rgba(96, 165, 250, .24),
        0 0 12px rgba(59, 130, 246, .22),
        0 10px 22px rgba(0,0,0,.26);
}

.stButton > button:hover {
    border-color: rgba(147, 197, 253, .75);
    color: #ffffff;
    box-shadow:
        0 0 0 1px rgba(147, 197, 253, .45),
        0 0 18px rgba(59, 130, 246, .34),
        0 12px 26px rgba(0,0,0,.30);
    transform: translateY(-1px);
}

.stDownloadButton > button {
    border-radius: 15px;
    border: 1px solid rgba(203, 213, 225, .34);
    background: linear-gradient(135deg, #334155, #1e293b);
    color: white;
    font-weight: 800;
    min-height: 44px;
    box-shadow: 0 8px 18px rgba(0,0,0,.20);
}

.stDownloadButton > button:hover {
    border-color: #93c5fd;
    color: white;
    box-shadow: 0 0 20px rgba(59, 130, 246, .28);
}

div[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, .72);
    border: 1px solid rgba(59, 130, 246, .35);
    border-radius: 18px;
    padding: .85rem;
    box-shadow: 0 8px 20px rgba(0,0,0,.20);
}

div[data-testid="stFileUploader"] section {
    background: rgba(30, 41, 59, .88) !important;
    border: 1px dashed rgba(96, 165, 250, .35) !important;
    border-radius: 14px !important;
}

div[data-testid="stFileUploader"] section:hover {
    border: 1px dashed rgba(147, 197, 253, .65) !important;
    background: rgba(51, 65, 85, .92) !important;
}

div[data-testid="stFileUploader"] small {
    color: #cbd5e1 !important;
}

div[data-testid="stFileUploader"] p {
    color: #dbeafe !important;
    font-weight: 600 !important;
}

div[data-testid="stFileUploader"] span {
    color: #93c5fd !important;
    font-weight: 700 !important;
}

div[data-testid="stFileUploader"] section button {
    background: #d1d5db !important;
    border: 1px solid #9ca3af !important;
}

div[data-testid="stFileUploader"] section button div,
div[data-testid="stFileUploader"] section button span,
div[data-testid="stFileUploader"] section button p {
    color: #000000 !important;
    fill: #000000 !important;
    font-weight: 700 !important;
}

div[data-testid="stFileUploader"] section button svg {
    color: #000000 !important;
    fill: #000000 !important;
}

    h2, h3 {
        color: #f8fafc;
        letter-spacing: -.01em;
    }

    .stAlert {
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Constants
# ----------------------------
NON_BILLABLE_BASE_CODES = {
    "Client Non Billable Srvc Must Document",
    "Non-billable Attempted Contact",
}
ATTEMPT_STATUSES = {"No Show", "Cancel"}

DISPLAY_COLUMNS = [
    "Client Name",
    "DateOfService",
    "ProcedureBase",
    "ProcedureCodeName",
    "ProgramName",
    "Status",
    "Staff",
    "Units",
]

# ----------------------------
# Helper Functions
# ----------------------------
def clean_client_name(name: object) -> str:
    """Remove SmartCare ID parentheses and normalize spacing/case for comparison."""
    if pd.isna(name):
        return ""
    text = str(name).strip()
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.upper()


def display_client_name(name: object) -> str:
    if pd.isna(name):
        return ""
    return re.sub(r"\s+", " ", str(name).strip())


def procedure_base(proc: object) -> str:
    """Remove trailing duration such as ' 60 Min' to group procedures cleanly."""
    if pd.isna(proc):
        return "Unknown"
    text = re.sub(r"\s+", " ", str(proc).strip())
    text = re.sub(r"\s+\d+\s*Min$", "", text, flags=re.IGNORECASE)
    return text.strip()


def normalize_status(status: object) -> str:
    if pd.isna(status):
        return ""
    return re.sub(r"\s+", " ", str(status).strip())


def read_excel_first_sheet(uploaded_file) -> pd.DataFrame:
    return pd.read_excel(uploaded_file, sheet_name=0)


def validate_columns(df: pd.DataFrame, required: List[str], file_label: str) -> Tuple[bool, List[str]]:
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"{file_label} is missing required column(s): {', '.join(missing)}")
        return False, missing
    return True, []


def clean_excel_sheet_name(sheet_name: object, used_names: set | None = None) -> str:
    """Return an Excel-safe worksheet name."""
    used_names = used_names if used_names is not None else set()
    safe_name = str(sheet_name) if sheet_name is not None else "Sheet"
    safe_name = re.sub(r"[\\/*?:\[\]]", "-", safe_name)
    safe_name = re.sub(r"\s+", " ", safe_name).strip()
    safe_name = safe_name[:31].strip() or "Sheet"

    base_name = safe_name
    counter = 1
    while safe_name in used_names:
        suffix = f"_{counter}"
        safe_name = f"{base_name[:31 - len(suffix)]}{suffix}"
        counter += 1

    used_names.add(safe_name)
    return safe_name


def make_excel_download(sheets: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    used_names = set()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_name = clean_excel_sheet_name(sheet_name, used_names)
            df.to_excel(writer, index=False, sheet_name=safe_name)
    return output.getvalue()


def make_printable_html(title: str, df: pd.DataFrame) -> bytes:
    """Create a clean print-ready HTML file for the selected review list."""
    safe_title = html.escape(str(title))
    print_df = df.copy()

    for col in print_df.columns:
        if pd.api.types.is_datetime64_any_dtype(print_df[col]):
            print_df[col] = print_df[col].dt.strftime("%m/%d/%Y").fillna("")

    table_html = print_df.to_html(index=False, escape=True, border=0, classes="review-table")
    doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{safe_title}</title>
<style>
    body {{
        font-family: Arial, Helvetica, sans-serif;
        margin: 28px;
        color: #111827;
    }}
    h1 {{
        margin-bottom: 4px;
        font-size: 24px;
    }}
    .subtitle {{
        margin-bottom: 18px;
        color: #4b5563;
        font-size: 13px;
    }}
    .print-button {{
        margin: 0 0 18px 0;
        padding: 10px 14px;
        border: 1px solid #111827;
        border-radius: 8px;
        background: #111827;
        color: white;
        font-weight: 700;
        cursor: pointer;
    }}
    table.review-table {{
        border-collapse: collapse;
        width: 100%;
        font-size: 11px;
    }}
    table.review-table th, table.review-table td {{
        border: 1px solid #d1d5db;
        padding: 6px 7px;
        vertical-align: top;
        text-align: left;
    }}
    table.review-table th {{
        background: #e5e7eb;
        font-weight: 700;
    }}
    tr {{ page-break-inside: avoid; }}
    @media print {{
        .print-button {{ display: none; }}
        body {{ margin: 16px; }}
    }}
</style>
</head>
<body>
    <h1>{safe_title}</h1>
    <div class="subtitle">Printable supervisory review list generated from the selected dashboard view.</div>
    <button class="print-button" onclick="window.print()">Print this list</button>
    {table_html}
</body>
</html>
"""
    return doc.encode("utf-8")


def metric_card(label: str, value: object, icon: str = "📊", style_class: str = "metric-blue"):
    st.markdown(
        f"""
        <div class="metric-card {style_class}">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    return df[[c for c in cols if c in df.columns]].copy()

# ----------------------------
# Header
# ----------------------------
st.markdown(
    """
    <div class="main-title">
        <h1>Non-Billable Caseload Review Dashboard v2</h1>
        <p>Employee-specific supervisory accountability and caseload engagement monitoring</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Upload both required Excel files to begin. The dashboard will not calculate until the Employee Caseload file and the Employee MyServicesList file are both uploaded."
)

# ----------------------------
# Upload Section
# ----------------------------
left_upload, right_upload = st.columns(2)
with left_upload:
    caseload_file = st.file_uploader(
        "Upload Employee Caseload Excel Export",
        type=["xlsx", "xls"],
        key="caseload_upload",
        help="Used for client names, total caseload count, Last DOS, and Last Seen by Me.",
    )
with right_upload:
    services_file = st.file_uploader(
        "Upload Employee SmartCare MyServicesList Excel Export",
        type=["xlsx", "xls"],
        key="services_upload",
        help="Used for services rendered, statuses, procedures, staff, dates, and units.",
    )

if not caseload_file or not services_file:
    st.warning("Both files are required before any counts, charts, or lists can be generated.")
    st.stop()

# ----------------------------
# Read and Validate Files
# ----------------------------
try:
    caseload_df = read_excel_first_sheet(caseload_file)
    ms_df = read_excel_first_sheet(services_file)
except Exception as exc:
    st.error(f"Unable to read one or both Excel files. Please verify the uploads are valid Excel exports. Error: {exc}")
    st.stop()

caseload_required = ["Name"]
ms_required = ["ClientName", "DateOfService", "ProcedureCodeName", "ProgramName", "Status", "Staff", "Units"]

ok_case, _ = validate_columns(caseload_df, caseload_required, "Caseload file")
ok_ms, _ = validate_columns(ms_df, ms_required, "MyServicesList file")
if not (ok_case and ok_ms):
    st.stop()

# ----------------------------
# Clean Data
# ----------------------------
caseload_df = caseload_df.copy()
ms_df = ms_df.copy()

caseload_df["ClientDisplayName"] = caseload_df["Name"].apply(display_client_name)
caseload_df["ClientKey"] = caseload_df["Name"].apply(clean_client_name)

if "Last DOS" not in caseload_df.columns:
    caseload_df["Last DOS"] = ""
if "Last Seen by Me" not in caseload_df.columns:
    caseload_df["Last Seen by Me"] = ""

ms_df["ClientDisplayName"] = ms_df["ClientName"].apply(display_client_name)
ms_df["ClientKey"] = ms_df["ClientName"].apply(clean_client_name)
ms_df["Status"] = ms_df["Status"].apply(normalize_status)
ms_df["ProcedureBase"] = ms_df["ProcedureCodeName"].apply(procedure_base)
ms_df["DateOfService"] = pd.to_datetime(ms_df["DateOfService"], errors="coerce")
ms_df["Units"] = pd.to_numeric(ms_df["Units"], errors="coerce").fillna(0)

ms_df["IsNonBillableProcedure"] = ms_df["ProcedureBase"].isin(NON_BILLABLE_BASE_CODES)
ms_df["IsAttemptStatus"] = ms_df["Status"].isin(ATTEMPT_STATUSES)
ms_df["IsSuccessfulEngagement"] = (~ms_df["IsNonBillableProcedure"]) & (~ms_df["IsAttemptStatus"])
ms_df["IsNonBillableTotal"] = ms_df["IsNonBillableProcedure"] | ms_df["IsAttemptStatus"]

# ----------------------------
# Metrics
# ----------------------------
total_caseload = caseload_df["ClientKey"].replace("", pd.NA).dropna().nunique()
total_services_rendered = len(ms_df)
successful_engagement_rows = int(ms_df["IsSuccessfulEngagement"].sum())
non_billable_total_rows = int(ms_df["IsNonBillableTotal"].sum())
no_show_cancel_total = int(ms_df["IsAttemptStatus"].sum())
total_units = ms_df["Units"].sum()

successful_clients = set(ms_df.loc[ms_df["IsSuccessfulEngagement"], "ClientKey"].dropna())
all_ms_clients = set(ms_df["ClientKey"].replace("", pd.NA).dropna())
caseload_clients = set(caseload_df["ClientKey"].replace("", pd.NA).dropna())

attempt_only_clients = []
for client_key, client_rows in ms_df.groupby("ClientKey"):
    if not client_key:
        continue
    has_success = bool(client_rows["IsSuccessfulEngagement"].any())
    has_non_success_activity = bool(client_rows["IsNonBillableTotal"].any())
    if has_non_success_activity and not has_success:
        attempt_only_clients.append(client_key)

no_engagement_clients = sorted(caseload_clients - all_ms_clients)

attempt_only_count = len(set(attempt_only_clients))
no_engagement_count = len(no_engagement_clients)
successful_client_count = len(successful_clients & caseload_clients) if caseload_clients else len(successful_clients)

# ----------------------------
# Build Review Lists
# ----------------------------
successful_list = safe_cols(ms_df.loc[ms_df["IsSuccessfulEngagement"]], DISPLAY_COLUMNS)
nonbillable_list = safe_cols(ms_df.loc[ms_df["IsNonBillableTotal"]], DISPLAY_COLUMNS)
noshow_cancel_list = safe_cols(ms_df.loc[ms_df["IsAttemptStatus"]], DISPLAY_COLUMNS)

attempt_only_base = ms_df[ms_df["ClientKey"].isin(set(attempt_only_clients))].copy()
attempt_summary = (
    attempt_only_base.groupby(["ClientKey", "ClientDisplayName"], dropna=False)
    .agg(
        Total_Attempt_NonBillable_Rows=("ClientKey", "size"),
        No_Show_Count=("Status", lambda s: (s == "No Show").sum()),
        Cancel_Count=("Status", lambda s: (s == "Cancel").sum()),
        Non_Billable_Code_Count=("IsNonBillableProcedure", "sum"),
        Last_Attempt_Activity_Date=("DateOfService", "max"),
        Procedure_Summary=("ProcedureBase", lambda s: ", ".join(sorted(set(map(str, s))))),
        ProgramName=("ProgramName", lambda s: ", ".join(sorted(set(map(str, s.dropna()))))[:250]),
        Staff=("Staff", lambda s: ", ".join(sorted(set(map(str, s.dropna()))))[:250]),
    )
    .reset_index()
)

no_engagement_list = caseload_df[caseload_df["ClientKey"].isin(no_engagement_clients)].copy()
no_engagement_list = no_engagement_list.rename(columns={"ClientDisplayName": "Client Name"})
no_engagement_list["Category"] = "No Engagement / No Contact"
no_engagement_list["Flag"] = "Client appears on caseload file but not on MyServicesList file"
no_engagement_list = safe_cols(no_engagement_list, ["Client Name", "Last DOS", "Last Seen by Me", "Category", "Flag"])

# ----------------------------
# Employee Review Header Values
# ----------------------------
review_employee = "Unknown Employee"
if "Staff" in ms_df.columns and not ms_df["Staff"].dropna().empty:
    review_employee = str(ms_df["Staff"].dropna().iloc[0]).strip()

audit_start = ""
audit_end = ""
if "DateOfService" in ms_df.columns and not ms_df["DateOfService"].dropna().empty:
    audit_start = ms_df["DateOfService"].min().strftime("%m/%d/%Y")
    audit_end = ms_df["DateOfService"].max().strftime("%m/%d/%Y")

# ----------------------------
# Employee Review Header Display
# ----------------------------
st.markdown(
    f"""
    <div class="review-header" style="
        display:flex;
        justify-content:center;
        align-items:center;
        gap:65px;
        text-align:center;
        padding:24px 20px;
        ">
        <span style="font-size:28px; font-weight:900; color:#f8fafc;">
            Employee: {review_employee}
        </span>
        <span style="font-size:28px; font-weight:900; color:#dbeafe;">
            Audit Period: {audit_start} - {audit_end}
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Dashboard Metrics
# ----------------------------
st.markdown("## Executive KPI Summary")

kpi_top = st.columns(4)
with kpi_top[0]:
    metric_card("Total Caseload", f"{total_caseload:,}", "👥", "metric-blue")
with kpi_top[1]:
    metric_card("Total Services Rendered", f"{total_services_rendered:,}", "📋", "metric-indigo")
with kpi_top[2]:
    metric_card("Successful Engagements", f"{successful_engagement_rows:,}", "✅", "metric-teal")
with kpi_top[3]:
    metric_card("Non-Billable Services Rendered", f"{non_billable_total_rows:,}", "📝", "metric-green")

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

kpi_bottom = st.columns(3)
with kpi_bottom[0]:
    metric_card("Attempts Only", f"{attempt_only_count:,}", "📞", "metric-orange")
with kpi_bottom[1]:
    metric_card("No Engagement / No Attempts", f"{no_engagement_count:,}", "🚫", "metric-rose")
with kpi_bottom[2]:
    metric_card("No Show / Cancelled Appointments", f"{no_show_cancel_total:,}", "⚠️", "metric-red")

# ----------------------------
# Charts
# ----------------------------
st.markdown("## Dashboard Charts")

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown("### Service Procedures Performed")

    procedure_counts = (
        ms_df["ProcedureBase"]
        .value_counts()
        .reset_index()
        .rename(columns={"ProcedureBase": "Procedure", "count": "Total"})
    )

    fig_bar = px.bar(
        procedure_counts,
        x="Procedure",
        y="Total",
        text="Total",
        title="All Service Procedures Performed",
    )

    kpi_bar_colors = [
        "rgba(96, 165, 250, 0.28)",
        "rgba(129, 140, 248, 0.28)",
        "rgba(45, 212, 191, 0.28)",
        "rgba(74, 222, 128, 0.28)",
        "rgba(251, 146, 60, 0.28)",
        "rgba(251, 113, 133, 0.28)",
        "rgba(248, 113, 113, 0.28)",
    ]

    kpi_bar_lines = [
        "rgba(96, 165, 250, 0.95)",
        "rgba(129, 140, 248, 0.95)",
        "rgba(45, 212, 191, 0.95)",
        "rgba(74, 222, 128, 0.95)",
        "rgba(251, 146, 60, 0.95)",
        "rgba(251, 113, 133, 0.95)",
        "rgba(248, 113, 113, 0.95)",
    ]

    bar_fill_colors = [
        kpi_bar_colors[i % len(kpi_bar_colors)]
        for i in range(len(procedure_counts))
    ]

    bar_line_colors = [
        kpi_bar_lines[i % len(kpi_bar_lines)]
        for i in range(len(procedure_counts))
    ]

    fig_bar.update_traces(
        marker=dict(
            color=bar_fill_colors,
            line=dict(color=bar_line_colors, width=2.5),
        ),
        textfont=dict(color="#f8fafc", size=14),
        textposition="outside",
        cliponaxis=False,
    )

    fig_bar.update_layout(
        xaxis_tickangle=-35,
        height=540,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,.10)",
        font=dict(color="#e5e7eb"),
        title_font=dict(color="#f8fafc"),
        margin=dict(t=70, b=130, l=55, r=35),
        xaxis=dict(
            showgrid=False,
            linecolor="rgba(148,163,184,.35)",
            tickfont=dict(color="#dbeafe", size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(148,163,184,.12)",
            linecolor="rgba(148,163,184,.25)",
            tickfont=dict(color="#dbeafe", size=12),
        ),
    )

    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown("### Billable Services vs Non-Billable")

    billable_nonbillable = pd.DataFrame(
        {
            "Category": ["Billable Services", "Non-Billable Services"],
            "Total": [successful_engagement_rows, non_billable_total_rows],
        }
    )

    fig_pie_1 = px.pie(
        billable_nonbillable,
        names="Category",
        values="Total",
        title="Billable Services vs Non-Billable Services",
        hole=0.48,
        color="Category",
        color_discrete_map={
            "Billable Services": "rgba(45, 212, 191, 0.42)",
"Non-Billable Services": "rgba(74, 222, 128, 0.42)",
        },
    )

    fig_pie_1.update_traces(
        textfont=dict(color="#f8fafc", size=14),
        marker=dict(
            line=dict(color="rgba(226,232,240,0.55)", width=2.5)
        )
    )

    fig_pie_1.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        title_font=dict(color="#f8fafc"),
        legend=dict(font=dict(color="#dbeafe")),
    )

    st.plotly_chart(fig_pie_1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
st.markdown("### Caseload Engagement Outcome")

caseload_outcome = pd.DataFrame(
    {
        "Category": ["Successful Engagement", "Attempts Only", "No Attempts"],
        "Total": [successful_client_count, attempt_only_count, no_engagement_count],
    }
)

fig_pie_2 = px.pie(
    caseload_outcome,
    names="Category",
    values="Total",
    title="Successful Engagement vs Attempts Only vs No Attempts",
    hole=0.48,
    color="Category",
    color_discrete_map={
        "Successful Engagement": "rgba(45, 212, 191, 0.42)",
"Attempts Only": "rgba(251, 146, 60, 0.42)",
"No Attempts": "rgba(251, 113, 133, 0.42)",
    },
)

fig_pie_2.update_traces(
    textfont=dict(color="#f8fafc", size=17),
    marker=dict(
        line=dict(color="rgba(226,232,240,0.55)", width=2.5)
    )
)

fig_pie_2.update_layout(
    height=650,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e5e7eb"),
    title_font=dict(color="#f8fafc"),
    margin=dict(t=70, b=40, l=40, r=40),
    legend=dict(font=dict(color="#dbeafe", size=15)),
)

st.plotly_chart(fig_pie_2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Buttons / Review Tables
# ----------------------------
st.markdown("## Review Buttons")
if "selected_view" not in st.session_state:
    st.session_state.selected_view = "Successful Engagements"

button_cols = st.columns(5)
with button_cols[0]:
    if st.button("Successful Engagements", use_container_width=True):
        st.session_state.selected_view = "Successful Engagements"
with button_cols[1]:
    if st.button("Non-Billable Totals", use_container_width=True):
        st.session_state.selected_view = "Non-Billable Totals"
with button_cols[2]:
    if st.button("Attempt Only / No Contact", use_container_width=True):
        st.session_state.selected_view = "Attempt Only / No Contact"
with button_cols[3]:
    if st.button("No Show / Cancelled Appointments", use_container_width=True):
        st.session_state.selected_view = "No Show / Cancelled Appointments"
with button_cols[4]:
    if st.button("No Engagement / No Attempts", use_container_width=True):
        st.session_state.selected_view = "No Engagement / No Attempts"

view_map = {
    "Successful Engagements": successful_list,
    "Non-Billable Totals": nonbillable_list,
    "Attempt Only / No Contact": attempt_summary,
    "No Show / Cancelled Appointments": noshow_cancel_list,
    "No Engagement / No Attempts": no_engagement_list,
}

selected_df = view_map[st.session_state.selected_view]

st.markdown(
    f"""
    <div class="section-box">
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:14px;
        ">
            <div style="
                font-size:26px;
                font-weight:900;
                color:#f8fafc;
            ">
                {st.session_state.selected_view} Review List
            </div>
            <div style="
                padding:8px 14px;
                border-radius:999px;
                border:1px solid rgba(96,165,250,.35);
                background:rgba(59,130,246,.12);
                color:#dbeafe;
                font-weight:800;
                font-size:15px;
            ">
                {len(selected_df):,} Records
            </div>
        </div>
    """,
    unsafe_allow_html=True,
)

styled_selected_df = selected_df.style.set_properties(
    **{
        "background-color": "#1e293b",
        "color": "#dbeafe",
        "border-color": "#334155",
    }
).set_table_styles(
    [
        {
    "selector": "th.col_heading",
    "props": [
        ("background-color", "#cbd5e1"),
        ("color", "#000000 !important"),
        ("font-weight", "800"),
        ("text-align", "left"),
    ],
},
        {
            "selector": "tbody tr:nth-child(even)",
            "props": [("background-color", "#334155")],
        },
    ]
)

st.dataframe(
    styled_selected_df,
    use_container_width=True,
    hide_index=True,
    height=430,
)

st.markdown("</div>", unsafe_allow_html=True)

download_col, print_col = st.columns(2)
with download_col:
    st.download_button(
        label=f"Download {st.session_state.selected_view}",
        data=make_excel_download({st.session_state.selected_view: selected_df}),
        file_name=f"{st.session_state.selected_view.replace(' ', '_').replace('/', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with print_col:
    st.download_button(
        label=f"Print-Friendly {st.session_state.selected_view}",
        data=make_printable_html(st.session_state.selected_view, selected_df),
        file_name=f"{st.session_state.selected_view.replace(' ', '_').replace('/', '_')}_PRINT.html",
        mime="text/html",
        use_container_width=True,
    )

# ----------------------------
# Full Export Center
# ----------------------------
st.markdown("## Download Center")
full_audit = make_excel_download(
    {
        "Successful Engagements": successful_list,
        "Non-Billable Totals": nonbillable_list,
        "Attempt Only No Contact": attempt_summary,
        "No Show Cancelled Appts": noshow_cancel_list,
        "No Engagement No Contact": no_engagement_list,
        "Procedure Counts": procedure_counts,
        "Caseload Outcome": caseload_outcome,
        "Billable NonBillable": billable_nonbillable,
    }
)
st.download_button(
    label="Download Full Supervisory Audit Workbook",
    data=full_audit,
    file_name="Non_Billable_Caseload_Review_Dashboard_v2_Audit_Workbook.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
