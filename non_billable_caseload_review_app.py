
import re
import html
from io import BytesIO
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# Non-Billable Caseload Review Dashboard v2
# Executive Command Center Edition
# Employee-Specific Supervisory Accountability Dashboard
# ============================================================

st.set_page_config(
    page_title="Non-Billable Caseload Review Dashboard v2",
    page_icon="📋",
    layout="wide"
)

# ----------------------------
# Styling - Option A Executive Command Center
# ----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(6, 182, 212, 0.16), transparent 30%),
            radial-gradient(circle at 85% 14%, rgba(124, 58, 237, 0.14), transparent 28%),
            radial-gradient(circle at 50% 92%, rgba(59, 130, 246, 0.10), transparent 35%),
            linear-gradient(135deg, #020617 0%, #07111f 42%, #0f172a 100%);
        color: #f8fafc;
    }

    .main .block-container {
        padding-top: 1.05rem;
        padding-bottom: 2.25rem;
        max-width: 1500px;
    }

    .hero {
        position: relative;
        padding: 1.35rem 1.45rem;
        border-radius: 26px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, .96), rgba(15, 23, 42, .76)),
            radial-gradient(circle at 10% 10%, rgba(6, 182, 212, .18), transparent 32%);
        border: 1px solid rgba(148, 163, 184, .24);
        box-shadow: 0 18px 50px rgba(0,0,0,.34);
        margin-bottom: 1rem;
        overflow: hidden;
    }

    .hero:before {
        content: "";
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(148, 163, 184, .055) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148, 163, 184, .055) 1px, transparent 1px);
        background-size: 34px 34px;
        mask-image: linear-gradient(90deg, rgba(0,0,0,.80), transparent 78%);
        pointer-events: none;
    }

    .hero-content {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1.25rem;
        flex-wrap: wrap;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.25rem;
        letter-spacing: -.04em;
        color: #ffffff;
        font-weight: 900;
    }

    .hero p {
        margin: .4rem 0 0 0;
        color: #cbd5e1;
        font-size: 1.02rem;
        max-width: 750px;
    }

    .hero-badges {
        display: flex;
        gap: .75rem;
        flex-wrap: wrap;
        align-items: stretch;
    }

    .hero-badge {
        min-width: 175px;
        border-radius: 18px;
        border: 1px solid rgba(148,163,184,.23);
        background: rgba(15,23,42,.72);
        padding: .85rem .95rem;
        box-shadow: 0 12px 28px rgba(0,0,0,.18);
    }

    .hero-badge-label {
        color: #94a3b8;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }

    .hero-badge-value {
        color: #ffffff;
        font-size: .92rem;
        font-weight: 800;
    }

    .notice-card {
        padding: .9rem 1rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(14,165,233,.12), rgba(37,99,235,.08));
        border: 1px solid rgba(125,211,252,.25);
        color: #dbeafe;
        margin: .85rem 0 1rem 0;
    }

    .section-panel {
        padding: 1.1rem;
        border-radius: 24px;
        background: rgba(2, 6, 23, .42);
        border: 1px solid rgba(148, 163, 184, .18);
        box-shadow: 0 16px 42px rgba(0,0,0,.20);
        margin: 1rem 0;
    }

    .section-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: .9rem;
    }

    .section-heading h2, .section-heading h3 {
        margin: 0;
        color: #f8fafc;
        font-weight: 900;
        letter-spacing: -.02em;
    }

    .section-kicker {
        color: #94a3b8;
        font-size: .82rem;
        margin-top: .25rem;
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(145deg,
                rgba(var(--accent-rgb), .22) 0%,
                rgba(15,23,42,.94) 42%,
                rgba(var(--accent-rgb), .11) 100%);
        border: 1px solid rgba(var(--accent-rgb), .36);
        border-radius: 24px;
        padding: 1.05rem;
        box-shadow:
            0 18px 36px rgba(0,0,0,.28),
            0 0 30px rgba(var(--accent-rgb), .16),
            inset 0 0 34px rgba(var(--accent-rgb), .08);
        min-height: 142px;
        transition: box-shadow .18s ease, transform .18s ease, border-color .18s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(var(--accent-rgb), .54);
        box-shadow:
            0 22px 42px rgba(0,0,0,.32),
            0 0 44px rgba(var(--accent-rgb), .24),
            inset 0 0 44px rgba(var(--accent-rgb), .11);
    }

    .metric-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: .75rem;
        position: relative;
        z-index: 1;
    }

    .metric-icon {
        width: 44px;
        height: 44px;
        border-radius: 17px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--accent-bg);
        color: var(--accent);
        font-size: 1.35rem;
        border: 1px solid var(--accent-border);
        box-shadow: 0 0 22px var(--shadow);
    }

    .metric-value {
        position: relative;
        z-index: 1;
        font-size: 2.25rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.02;
        margin-top: .75rem;
        letter-spacing: -.04em;
    }

    .metric-label {
        position: relative;
        z-index: 1;
        font-size: .84rem;
        color: #e2e8f0;
        font-weight: 850;
        margin-top: .25rem;
        line-height: 1.25;
    }

    .metric-sub {
        position: relative;
        z-index: 1;
        font-size: .76rem;
        color: #94a3b8;
        margin-top: .42rem;
        line-height: 1.35;
    }

    .metric-cyan {
        --accent: #67e8f9;
        --accent-bg: rgba(6,182,212,.16);
        --accent-border: rgba(103,232,249,.35);
        --shadow: rgba(6,182,212,.25);
        --accent-rgb: 6,182,212;
    }

    .metric-green {
        --accent: #86efac;
        --accent-bg: rgba(34,197,94,.16);
        --accent-border: rgba(134,239,172,.35);
        --shadow: rgba(34,197,94,.20);
        --accent-rgb: 34,197,94;
    }

    .metric-amber {
        --accent: #fcd34d;
        --accent-bg: rgba(245,158,11,.17);
        --accent-border: rgba(252,211,77,.35);
        --shadow: rgba(245,158,11,.22);
        --accent-rgb: 245,158,11;
    }

    .metric-purple {
        --accent: #c4b5fd;
        --accent-bg: rgba(124,58,237,.18);
        --accent-border: rgba(196,181,253,.35);
        --shadow: rgba(124,58,237,.23);
        --accent-rgb: 124,58,237;
    }

    .metric-red {
        --accent: #fda4af;
        --accent-bg: rgba(244,63,94,.16);
        --accent-border: rgba(253,164,175,.35);
        --shadow: rgba(244,63,94,.22);
        --accent-rgb: 244,63,94;
    }

    .chart-card {
        border-radius: 24px;
        background:
            linear-gradient(145deg, rgba(15,23,42,.88), rgba(2,6,23,.58));
        border: 1px solid rgba(148, 163, 184, .18);
        box-shadow: 0 16px 38px rgba(0,0,0,.24);
        padding: .95rem;
        min-height: 100%;
    }

    .chart-title {
        font-size: 1.02rem;
        font-weight: 900;
        color: #ffffff;
        margin: .1rem 0 .6rem .1rem;
        letter-spacing: -.02em;
    }

    .review-button-card {
        width: 100%;
        min-height: 92px;
        padding: .85rem;
        border-radius: 20px;
        border: 1px solid rgba(var(--accent-rgb), .32);
        background:
            linear-gradient(145deg,
                rgba(var(--accent-rgb), .18) 0%,
                rgba(15,23,42,.92) 48%,
                rgba(var(--accent-rgb), .09) 100%);
        box-shadow:
            0 14px 30px rgba(0,0,0,.20),
            0 0 26px rgba(var(--accent-rgb), .14),
            inset 0 0 26px rgba(var(--accent-rgb), .07);
        display: flex;
        align-items: center;
        gap: .8rem;
        margin-bottom: .4rem;
    }

    .review-green { --accent-rgb: 34,197,94; }
    .review-purple { --accent-rgb: 124,58,237; }
    .review-amber { --accent-rgb: 245,158,11; }
    .review-orange { --accent-rgb: 249,115,22; }
    .review-red { --accent-rgb: 244,63,94; }
    .review-cyan { --accent-rgb: 14,165,233; }

    .review-button-icon {
        width: 42px;
        height: 42px;
        flex: 0 0 42px;
        border-radius: 16px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.3rem;
        border: 1px solid rgba(255,255,255,.14);
    }

    .review-button-text {
        color: #ffffff;
        font-weight: 900;
        line-height: 1.15;
        font-size: .93rem;
    }

    .review-button-sub {
        color: #94a3b8;
        font-size: .74rem;
        margin-top: .25rem;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 16px !important;
        border: 1px solid rgba(203, 213, 225, .24) !important;
        background: linear-gradient(135deg, rgba(37,99,235,.82), rgba(30,64,175,.78)) !important;
        color: white !important;
        font-weight: 850 !important;
        min-height: 3rem;
        box-shadow: 0 12px 26px rgba(37,99,235,.18);
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: rgba(125,211,252,.72) !important;
        box-shadow: 0 15px 30px rgba(14,165,233,.22);
        transform: translateY(-1px);
    }

    div[data-testid="stFileUploader"] {
        background: linear-gradient(145deg, rgba(15,23,42,.86), rgba(30,41,59,.52));
        border: 1px solid rgba(125,211,252,.20);
        border-radius: 22px;
        padding: .9rem;
        box-shadow: 0 16px 34px rgba(0,0,0,.20);
    }

    div[data-testid="stFileUploader"] label {
        color: #e2e8f0 !important;
        font-weight: 850;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, .18);
        box-shadow: 0 14px 30px rgba(0,0,0,.16);
    }

    .download-strip {
        padding: 1rem;
        border-radius: 22px;
        background:
            linear-gradient(135deg, rgba(15,23,42,.85), rgba(30,41,59,.55));
        border: 1px solid rgba(148,163,184,.18);
        box-shadow: 0 16px 38px rgba(0,0,0,.22);
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    .small-muted {
        color: #94a3b8;
        font-size: .84rem;
    }

    .stAlert {
        border-radius: 18px;
    }

    hr {
        border-color: rgba(148, 163, 184, .18);
    }

    @media (max-width: 900px) {
        .hero h1 {
            font-size: 1.65rem;
        }
        .hero-content {
            display: block;
        }
        .hero-badges {
            margin-top: 1rem;
        }
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
ATTEMPT_STATUSES = {"No Show", "Cancel", "Cancelation", "Cancellation"}

DISPLAY_COLUMNS = [
    "ClientName",
    "DateOfService",
    "ProcedureBase",
    "ProcedureCodeName",
    "ProgramName",
    "Status",
    "Staff",
    "Units",
]

PLOTLY_TEMPLATE = "plotly_dark"

CHART_COLORS = {
    "Billable Services": "#22d3ee",
    "Non-Billable Services": "#8b5cf6",
    "Successful Engagement": "#4ade80",
    "Attempts Only": "#f59e0b",
    "No Attempts": "#ef6666",
    "No Engagement / No Attempts": "#ef6666",
    "Non-Billable Activity": "#a78bfa",
    "Attempt Activity": "#f59e0b",
}

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
    return text.strip() or "Unknown"


def normalize_status(status: object) -> str:
    if pd.isna(status):
        return ""
    text = re.sub(r"\s+", " ", str(status).strip())
    if text.lower() in {"cancelled", "canceled", "cancelation", "cancellation"}:
        return "Cancel"
    return text


def read_excel_first_sheet(uploaded_file) -> pd.DataFrame:
    return pd.read_excel(uploaded_file, sheet_name=0)


def validate_columns(df: pd.DataFrame, required: List[str], file_label: str) -> Tuple[bool, List[str]]:
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"{file_label} is missing required column(s): {', '.join(missing)}")
        return False, missing
    return True, []


def clean_excel_sheet_name(sheet_name: object, used_names: set | None = None) -> str:
    """Return an Excel-safe worksheet name.

    Excel sheet names cannot contain: \ / * ? : [ ]
    They also must be 31 characters or fewer and cannot be blank.
    """
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


def metric_card(label: str, value: object, sub: str = "", icon: str = "📊", style_class: str = "metric-cyan"):
    st.markdown(
        f"""
        <div class="metric-card {style_class}">
            <div class="metric-top">
                <div class="metric-icon">{icon}</div>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    return df[[c for c in cols if c in df.columns]].copy()


def render_chart_card(title: str):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)


def apply_plotly_layout(fig, height: int = 460):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter, Arial"),
        title=dict(font=dict(color="#ffffff", size=16)),
        legend=dict(font=dict(color="#cbd5e1")),
        margin=dict(l=18, r=18, t=50, b=30),
    )
    return fig


def percentage(numerator: int | float, denominator: int | float) -> str:
    if not denominator:
        return "0.0%"
    return f"{(numerator / denominator) * 100:.1f}%"


# ----------------------------
# Header
# ----------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-content">
            <div>
                <h1>Non-Billable Caseload Review Dashboard v2</h1>
                <p>Employee-specific supervisory accountability and caseload engagement monitoring with status-based service review.</p>
            </div>
            <div class="hero-badges">
                <div class="hero-badge">
                    <div class="hero-badge-label">Reviewing Employee</div>
                    <div class="hero-badge-value">Pending Upload</div>
                </div>
                <div class="hero-badge">
                    <div class="hero-badge-label">Audit Period</div>
                    <div class="hero-badge-value">Pending Upload</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="notice-card">
        <b>Upload both required Excel files to begin.</b> The dashboard will not calculate until the Employee Caseload file and the Employee MyServicesList file are both uploaded.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Upload Section
# ----------------------------
st.markdown(
    """
    <div class="section-heading">
        <div>
            <h2>Upload Center</h2>
            <div class="section-kicker">Drop in the caseload export and employee-specific MyServicesList export.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
if not attempt_only_base.empty:
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
else:
    attempt_summary = pd.DataFrame(
        columns=[
            "ClientKey",
            "ClientDisplayName",
            "Total_Attempt_NonBillable_Rows",
            "No_Show_Count",
            "Cancel_Count",
            "Non_Billable_Code_Count",
            "Last_Attempt_Activity_Date",
            "Procedure_Summary",
            "ProgramName",
            "Staff",
        ]
    )

no_engagement_list = caseload_df[caseload_df["ClientKey"].isin(no_engagement_clients)].copy()
no_engagement_list = no_engagement_list.rename(columns={"ClientDisplayName": "Client Name"})
no_engagement_list["Category"] = "No Engagement / No Contact"
no_engagement_list["Flag"] = "Client appears on caseload file but not on MyServicesList file"
no_engagement_list = safe_cols(no_engagement_list, ["Client Name", "Last DOS", "Last Seen by Me", "Category", "Flag"])

all_caseload_list = caseload_df.copy()
all_caseload_list = all_caseload_list.rename(columns={"ClientDisplayName": "Client Name"})
all_caseload_list["Has Employee Activity"] = all_caseload_list["ClientKey"].isin(all_ms_clients)
all_caseload_list["Has Successful Engagement"] = all_caseload_list["ClientKey"].isin(successful_clients)
all_caseload_list["Category"] = all_caseload_list.apply(
    lambda r: "Successful Engagement"
    if r["Has Successful Engagement"]
    else ("Attempt / Non-Billable Only" if r["Has Employee Activity"] else "No Engagement / No Attempts"),
    axis=1,
)
all_caseload_list = safe_cols(
    all_caseload_list,
    ["Client Name", "Last DOS", "Last Seen by Me", "Category", "Has Employee Activity", "Has Successful Engagement"],
)

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
# Live Employee Review Header Display
# ----------------------------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div>
                <h1>Executive Review Dashboard</h1>
                <p>Status-trumped service review for employee-specific engagement, attempts, non-billables, and untouched caseload clients.</p>
            </div>
            <div class="hero-badges">
                <div class="hero-badge">
                    <div class="hero-badge-label">Reviewing Employee</div>
                    <div class="hero-badge-value">{html.escape(review_employee)}</div>
                </div>
                <div class="hero-badge">
                    <div class="hero-badge-label">Audit Period</div>
                    <div class="hero-badge-value">{html.escape(audit_start)} - {html.escape(audit_end)}</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Dashboard Metrics
# ----------------------------
st.markdown(
    """
    <div class="section-heading">
        <div>
            <h2>Executive KPI Summary</h2>
            <div class="section-kicker">High-level review counts from the caseload and employee-specific MyServicesList file.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI order requested:
# 1. Total Caseload
# 2. Total Services Rendered
# 3. Successful Engagements
# 4. Non-Billable Services Rendered
# 5. Attempts Only
# 6. No Engagement / No Attempts
# 7. No Show / Cancel Total

kpi_row_1 = st.columns(4)
with kpi_row_1[0]:
    metric_card(
        "Total Caseload",
        f"{total_caseload:,}",
        "Clients on caseload",
        "👥",
        "metric-cyan",
    )
with kpi_row_1[1]:
    metric_card(
        "Total Services Rendered",
        f"{total_services_rendered:,}",
        "All rows in MyServicesList",
        "🧾",
        "metric-cyan",
    )
with kpi_row_1[2]:
    metric_card(
        "Successful Engagements",
        f"{successful_client_count:,}",
        f"{percentage(successful_client_count, total_caseload)} of caseload",
        "✅",
        "metric-green",
    )
with kpi_row_1[3]:
    metric_card(
        "Non-Billable Services Rendered",
        f"{non_billable_total_rows:,}",
        "Rows with non-billable code or attempt status",
        "📄",
        "metric-purple",
    )

kpi_row_2 = st.columns(3)
with kpi_row_2[0]:
    metric_card(
        "Attempts Only",
        f"{attempt_only_count:,}",
        f"{percentage(attempt_only_count, total_caseload)} of caseload",
        "📞",
        "metric-amber",
    )
with kpi_row_2[1]:
    metric_card(
        "No Engagement / No Attempts",
        f"{no_engagement_count:,}",
        f"{percentage(no_engagement_count, total_caseload)} of caseload",
        "🚩",
        "metric-red",
    )
with kpi_row_2[2]:
    metric_card(
        "No Show / Cancel Total",
        f"{no_show_cancel_total:,}",
        "Rows with attempt status",
        "⚠️",
        "metric-amber",
    )

# ----------------------------
# Charts
# ----------------------------
st.markdown(
    """
    <div class="section-heading" style="margin-top: 1.2rem;">
        <div>
            <h2>Dashboard Charts</h2>
            <div class="section-kicker">Visual breakdown of procedure activity, billable status, and caseload engagement outcome.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

chart_col1, chart_col2, chart_col3 = st.columns([1.35, 1, 1])

with chart_col1:
    with st.container(border=False):
        render_chart_card("Procedures by Count")
        procedure_counts = (
            ms_df["ProcedureBase"]
            .value_counts(dropna=False)
            .rename_axis("Procedure")
            .reset_index(name="Total")
        )
        procedure_counts_chart = procedure_counts.head(12).sort_values("Total", ascending=True)
        fig_bar = px.bar(
            procedure_counts_chart,
            x="Total",
            y="Procedure",
            orientation="h",
            text="Total",
            title="All Service Procedures Performed",
            color="Total",
            color_continuous_scale=["#1e3a8a", "#06b6d4"],
        )
        fig_bar.update_traces(textposition="outside", marker_line_width=0)
        fig_bar.update_layout(showlegend=False, coloraxis_showscale=False)
        apply_plotly_layout(fig_bar, height=430)
        st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    render_chart_card("Billable vs Non-Billable")
    billable_nonbillable = pd.DataFrame(
        {
            "Category": ["Billable Services", "Non-Billable Services"],
            "Total": [successful_engagement_rows, non_billable_total_rows],
        }
    )
    billable_nonbillable = billable_nonbillable[billable_nonbillable["Total"] > 0]
    fig_pie_1 = px.pie(
        billable_nonbillable,
        names="Category",
        values="Total",
        title="Billable Services vs Non-Billable Services",
        hole=0.46,
        color="Category",
        color_discrete_map=CHART_COLORS,
    )
    fig_pie_1.update_traces(textposition="inside", textinfo="value+percent", pull=[0.02] * len(billable_nonbillable))
    apply_plotly_layout(fig_pie_1, height=430)
    st.plotly_chart(fig_pie_1, use_container_width=True)

with chart_col3:
    render_chart_card("Caseload Engagement Outcome")
    caseload_outcome = pd.DataFrame(
        {
            "Category": ["Successful Engagement", "Attempts Only", "No Attempts"],
            "Total": [successful_client_count, attempt_only_count, no_engagement_count],
        }
    )
    caseload_outcome = caseload_outcome[caseload_outcome["Total"] > 0]
    fig_pie_2 = px.pie(
        caseload_outcome,
        names="Category",
        values="Total",
        title="Successful Engagement vs Attempts Only vs No Attempts",
        hole=0.42,
        color="Category",
        color_discrete_map=CHART_COLORS,
    )
    fig_pie_2.update_traces(textposition="inside", textinfo="percent", pull=[0.02] * len(caseload_outcome))
    apply_plotly_layout(fig_pie_2, height=430)
    st.plotly_chart(fig_pie_2, use_container_width=True)

# ----------------------------
# Review Buttons / Tables
# ----------------------------
st.markdown(
    """
    <div class="section-heading" style="margin-top: 1.35rem;">
        <div>
            <h2>Review Detailed Caseload Data</h2>
            <div class="section-kicker">Choose a review category below. The selected list can be downloaded or opened as a print-friendly report.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "selected_view" not in st.session_state:
    st.session_state.selected_view = "Successful Engagements"

button_cols = st.columns(6)
button_specs = [
    ("Successful Engagements", "✅", "Billable/show activity", "rgba(34,197,94,.15)", "review-green"),
    ("Non-Billable Totals", "📄", "Non-billable + attempts", "rgba(124,58,237,.15)", "review-purple"),
    ("Attempt Only / No Contact", "📞", "Only attempt/non-success activity", "rgba(245,158,11,.16)", "review-amber"),
    ("No Show / Cancel Total", "⚠️", "Attempt status rows", "rgba(249,115,22,.16)", "review-orange"),
    ("No Engagement / No Attempts", "🚩", "Missing from MyServicesList", "rgba(244,63,94,.16)", "review-red"),
    ("All Caseload", "👥", "Full caseload review", "rgba(14,165,233,.16)", "review-cyan"),
]

for col, (label, icon, sub, bg, review_class) in zip(button_cols, button_specs):
    with col:
        st.markdown(
            f"""
            <div class="review-button-card {review_class}">
                <div class="review-button-icon" style="background:{bg};">{icon}</div>
                <div>
                    <div class="review-button-text">{label}</div>
                    <div class="review-button-sub">{sub}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(label, key=f"btn_{label}", use_container_width=True):
            st.session_state.selected_view = label

view_map = {
    "Successful Engagements": successful_list,
    "Non-Billable Totals": nonbillable_list,
    "Attempt Only / No Contact": attempt_summary,
    "No Show / Cancel Total": noshow_cancel_list,
    "No Engagement / No Attempts": no_engagement_list,
    "All Caseload": all_caseload_list,
}

selected_df = view_map[st.session_state.selected_view]

st.markdown(
    f"""
    <div class="section-heading" style="margin-top: 1.25rem;">
        <div>
            <h3>{html.escape(st.session_state.selected_view)}</h3>
            <div class="section-kicker">{len(selected_df):,} row(s) in this selected review view.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.dataframe(selected_df, use_container_width=True, hide_index=True)

download_col, print_col = st.columns(2)
safe_selected_name = st.session_state.selected_view.replace(" ", "_").replace("/", "_")
with download_col:
    st.download_button(
        label=f"⬇️ Download {st.session_state.selected_view}",
        data=make_excel_download({st.session_state.selected_view: selected_df}),
        file_name=f"{safe_selected_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with print_col:
    st.download_button(
        label=f"🖨️ Print-Friendly {st.session_state.selected_view}",
        data=make_printable_html(st.session_state.selected_view, selected_df),
        file_name=f"{safe_selected_name}_PRINT.html",
        mime="text/html",
        use_container_width=True,
    )

# ----------------------------
# Full Export Center
# ----------------------------
st.markdown(
    """
    <div class="section-heading" style="margin-top: 1.35rem;">
        <div>
            <h2>Download Center</h2>
            <div class="section-kicker">Export the full supervisory audit workbook with all review lists and chart source tables.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

full_audit = make_excel_download(
    {
        "Successful Engagements": successful_list,
        "Non-Billable Totals": nonbillable_list,
        "Attempt Only No Contact": attempt_summary,
        "No Show Cancel Total": noshow_cancel_list,
        "No Engagement No Contact": no_engagement_list,
        "All Caseload": all_caseload_list,
        "Procedure Counts": procedure_counts,
        "Caseload Outcome": caseload_outcome,
        "Billable NonBillable": billable_nonbillable,
    }
)

st.download_button(
    label="📚 Download Full Supervisory Audit Workbook",
    data=full_audit,
    file_name="Non_Billable_Caseload_Review_Dashboard_v2_Executive_Audit_Workbook.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.markdown(
    """
    <div class="small-muted" style="text-align:center; margin-top: 1.6rem;">
        Non-Billable Caseload Review Dashboard v2 • Executive Command Center Edition
    </div>
    """,
    unsafe_allow_html=True,
)
