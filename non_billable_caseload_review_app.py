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
# ============================================================

st.set_page_config(
    page_title="Non-Billable Caseload Review Dashboard v2",
    page_icon="📊",
    layout="wide",
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
    "ClientName",
    "DateOfService",
    "ProcedureBase",
    "ProcedureCodeName",
    "ProgramName",
    "Status",
    "Staff",
    "Units",
]

# ----------------------------
# Styling
# ----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(90deg, #163b66 0%, #163b66 4.5%, #f7fbff 4.5%, #ffffff 100%);
        color: #0f172a;
    }
    section[data-testid="stSidebar"] { background: #123a67; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }
    h1, h2, h3 { color: #173b67; }
    .hero-title {
        padding: 1.35rem 1.6rem .9rem 1.6rem;
        border-radius: 20px;
        background: rgba(255,255,255,.92);
        border: 1px solid #d7e3f3;
        box-shadow: 0 12px 35px rgba(28, 64, 108, .13);
        margin-bottom: 1rem;
    }
    .hero-title h1 {
        margin: 0;
        font-size: 2.25rem;
        letter-spacing: .035em;
        font-weight: 900;
        text-transform: uppercase;
        color: #173b67;
    }
    .hero-title p {
        margin: .35rem 0 0 0;
        color: #64748b;
        font-size: 1rem;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: .04em;
    }
    .info-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        padding: 1rem 1.25rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #ffffff 0%, #eef6ff 100%);
        border: 1px solid #d5e3f4;
        box-shadow: 0 10px 26px rgba(28, 64, 108, .10);
        margin-bottom: 1rem;
    }
    .info-item {
        display: flex;
        gap: .8rem;
        align-items: center;
        border-right: 1px solid #d5e3f4;
        min-height: 58px;
    }
    .info-item:last-child { border-right: 0; }
    .info-icon {
        width: 46px; height: 46px;
        border-radius: 14px;
        display:flex; align-items:center; justify-content:center;
        background:#eaf3ff;
        color:#1d4f8c;
        font-size: 1.45rem;
    }
    .info-label {
        font-size: .78rem;
        color:#64748b;
        font-weight:800;
        letter-spacing:.04em;
        text-transform: uppercase;
    }
    .info-value {
        font-size: 1.08rem;
        color:#173b67;
        font-weight:900;
        margin-top:.15rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #d8e3f0;
        border-radius: 18px;
        padding: 1rem .9rem;
        box-shadow: 0 10px 24px rgba(28, 64, 108, .10);
        min-height: 132px;
        text-align:center;
    }
    .metric-icon {
        font-size: 1.55rem;
        margin-bottom: .3rem;
    }
    .metric-label {
        font-size: .76rem;
        color: #334155;
        text-transform: uppercase;
        font-weight: 850;
        letter-spacing: .035em;
        min-height: 34px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 950;
        color: #173b67;
        line-height: 1.05;
        margin-top: .15rem;
    }
    .metric-sub {
        font-size: .82rem;
        color: #64748b;
        margin-top: .45rem;
        font-weight: 650;
    }
    .metric-sub .good { color: #188038; font-weight: 900; }
    .metric-sub .warn { color: #b45309; font-weight: 900; }
    .metric-sub .bad { color: #b91c1c; font-weight: 900; }
    .section-header {
        display:flex;
        align-items:center;
        gap:.6rem;
        color:#173b67;
        font-weight:950;
        letter-spacing:.025em;
        text-transform:uppercase;
        margin: 1.2rem 0 .75rem 0;
        border-bottom: 2px solid #a9c5e8;
        padding-bottom: .35rem;
    }
    .chart-card, .table-card {
        background:#ffffff;
        border: 1px solid #d8e3f0;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(28, 64, 108, .09);
        padding: .8rem .9rem;
        margin-bottom: 1rem;
    }
    .selected-title {
        background: linear-gradient(90deg, #173b67, #2f6fac);
        color: white;
        font-weight: 900;
        padding: .8rem 1rem;
        border-radius: 14px 14px 0 0;
        margin-top: .8rem;
        text-transform: uppercase;
        letter-spacing: .02em;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 0 0 14px 14px;
        overflow: hidden;
    }
    .stButton > button {
        border-radius: 16px;
        border: 1px solid #c7d7eb;
        background: #ffffff;
        color: #173b67;
        font-weight: 900;
        min-height: 4.5rem;
        box-shadow: 0 8px 18px rgba(28, 64, 108, .08);
    }
    .stButton > button:hover {
        border-color: #2563eb;
        color: #123a67;
        background: #eef6ff;
    }
    .stDownloadButton > button {
        border-radius: 12px;
        border: 1px solid #b9cde7;
        background: #ffffff;
        color: #173b67;
        font-weight: 850;
    }
    .stDownloadButton > button:hover {
        border-color: #2563eb;
        color: #123a67;
        background: #eef6ff;
    }
    .note-box {
        background:#edf7ff;
        border:1px solid #c7dff7;
        color:#173b67;
        padding:.85rem 1rem;
        border-radius:14px;
        font-weight:650;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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


def safe_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    return df[[c for c in cols if c in df.columns]].copy()


def format_date_series(series: pd.Series) -> pd.Series:
    dates = pd.to_datetime(series, errors="coerce")
    return dates.dt.strftime("%m/%d/%Y").fillna("")


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
            export_df = df.copy()
            for col in export_df.columns:
                if pd.api.types.is_datetime64_any_dtype(export_df[col]):
                    export_df[col] = export_df[col].dt.strftime("%m/%d/%Y")
            export_df.to_excel(writer, index=False, sheet_name=safe_name)
    return output.getvalue()


def make_printable_html(title: str, df: pd.DataFrame, employee_name: str, review_period: str) -> bytes:
    """Create a clean print-ready HTML file for the selected review list."""
    safe_title = html.escape(str(title))
    safe_employee = html.escape(str(employee_name))
    safe_period = html.escape(str(review_period))
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
body {{ font-family: Arial, sans-serif; margin: 28px; color: #173b67; }}
h1 {{ margin-bottom: 4px; }}
.meta {{ color: #475569; margin-bottom: 18px; font-weight: 600; }}
button {{ padding: 10px 14px; border-radius: 8px; border: 1px solid #173b67; background: #173b67; color: white; font-weight: 700; margin-bottom: 18px; }}
.review-table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
.review-table th {{ background: #173b67; color: white; text-align: left; padding: 8px; }}
.review-table td {{ border-bottom: 1px solid #d7e3f3; padding: 7px; vertical-align: top; }}
.review-table tr:nth-child(even) {{ background: #f3f8ff; }}
@media print {{ button {{ display: none; }} body {{ margin: 12mm; }} }}
</style>
</head>
<body>
<button onclick="window.print()">Print this list</button>
<h1>{safe_title}</h1>
<div class="meta">Employee: {safe_employee} &nbsp; | &nbsp; Review Period: {safe_period} &nbsp; | &nbsp; Records: {len(print_df)}</div>
{table_html}
</body>
</html>"""
    return doc.encode("utf-8")


def pct(part: float, whole: float) -> float:
    if not whole:
        return 0.0
    return (part / whole) * 100


def metric_card(label: str, value: object, sub: str = "", icon: str = "📌", tone: str = ""):
    tone_class = tone if tone in {"good", "warn", "bad"} else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-sub"><span class="{tone_class}">{html.escape(str(sub))}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(icon: str, text: str):
    st.markdown(f"<div class='section-header'>{icon} {html.escape(text)}</div>", unsafe_allow_html=True)


# ----------------------------
# Header
# ----------------------------
st.markdown(
    """
    <div class="hero-title">
        <h1>Non-Billable Caseload Review Dashboard</h1>
        <p>Supervisory Engagement & Accountability Overview</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='note-box'>Upload both required Excel files to begin. No counts, charts, or review lists will calculate until both files are uploaded.</div>",
    unsafe_allow_html=True,
)

# ----------------------------
# Upload Section
# ----------------------------
section_header("📁", "Required Uploads")
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

caseload_reference = safe_cols(caseload_df, ["ClientKey", "ClientDisplayName", "Last DOS", "Last Seen by Me"])
caseload_reference = caseload_reference.drop_duplicates(subset=["ClientKey"])
caseload_reference = caseload_reference.rename(
    columns={
        "ClientDisplayName": "Caseload Client Name",
        "Last DOS": "Last DOS",
        "Last Seen by Me": "Last Seen by Me",
    }
)

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

staff_values = [x for x in ms_df["Staff"].dropna().astype(str).unique().tolist() if x.strip()]
employee_name = staff_values[0] if len(staff_values) == 1 else (", ".join(staff_values[:2]) if staff_values else "Employee Not Found")
min_dos = ms_df["DateOfService"].min()
max_dos = ms_df["DateOfService"].max()
review_period = "Unavailable"
review_days = ""
if pd.notna(min_dos) and pd.notna(max_dos):
    review_period = f"{min_dos:%m/%d/%Y} - {max_dos:%m/%d/%Y}"
    review_days = f"{(max_dos - min_dos).days + 1} Days"

# ----------------------------
# Executive Header Strip
# ----------------------------
st.markdown(
    f"""
    <div class="info-strip">
        <div class="info-item">
            <div class="info-icon">👤</div>
            <div><div class="info-label">Reviewing Employee</div><div class="info-value">{html.escape(employee_name)}</div></div>
        </div>
        <div class="info-item">
            <div class="info-icon">📅</div>
            <div><div class="info-label">Audit Period (Date of Service)</div><div class="info-value">{html.escape(review_period)}<br><span style="font-size:.86rem;color:#64748b;">{html.escape(review_days)}</span></div></div>
        </div>
        <div class="info-item">
            <div class="info-icon">📄</div>
            <div><div class="info-label">Files Uploaded</div><div class="info-value">✅ Caseload Export<br>✅ MyServicesList Export</div></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
            "ClientKey", "ClientDisplayName", "Total_Attempt_NonBillable_Rows", "No_Show_Count",
            "Cancel_Count", "Non_Billable_Code_Count", "Last_Attempt_Activity_Date",
            "Procedure_Summary", "ProgramName", "Staff"
        ]
    )

attempt_summary = attempt_summary.merge(caseload_reference, on="ClientKey", how="left")
attempt_summary["Client Name"] = attempt_summary["Caseload Client Name"].fillna(attempt_summary["ClientDisplayName"])
attempt_summary = safe_cols(
    attempt_summary,
    [
        "Client Name",
        "Last DOS",
        "Last Seen by Me",
        "Total_Attempt_NonBillable_Rows",
        "No_Show_Count",
        "Cancel_Count",
        "Non_Billable_Code_Count",
        "Last_Attempt_Activity_Date",
        "Procedure_Summary",
        "ProgramName",
        "Staff",
    ],
)

no_engagement_list = caseload_df[caseload_df["ClientKey"].isin(no_engagement_clients)].copy()
no_engagement_list = no_engagement_list.rename(columns={"ClientDisplayName": "Client Name"})
no_engagement_list["Category"] = "No Engagement / No Contact"
no_engagement_list["Flag"] = "Client appears on caseload file but not on MyServicesList file"
no_engagement_list = safe_cols(no_engagement_list, ["Client Name", "Last DOS", "Last Seen by Me", "Category", "Flag"])

# ----------------------------
# Dashboard Metrics
# ----------------------------
section_header("📊", "Dashboard Summary")
cols = st.columns(7)
with cols[0]:
    metric_card("Total Caseload Count", f"{total_caseload:,}", "100% of Caseload", "👥")
with cols[1]:
    metric_card("Total Services Rendered", f"{total_services_rendered:,}", "All MS rows", "✅", "good")
with cols[2]:
    metric_card("Successful Engagements", f"{successful_engagement_rows:,}", f"{pct(successful_engagement_rows, total_services_rendered):.1f}% of Services", "🤝", "good")
with cols[3]:
    metric_card("Non-Billable Totals", f"{non_billable_total_rows:,}", f"{pct(non_billable_total_rows, total_services_rendered):.1f}% of Services", "📝", "warn")
with cols[4]:
    metric_card("Attempt Only / No Contact", f"{attempt_only_count:,}", f"{pct(attempt_only_count, total_caseload):.1f}% of Caseload", "📞", "bad")
with cols[5]:
    metric_card("No Show / Cancel Total", f"{no_show_cancel_total:,}", f"{pct(no_show_cancel_total, total_services_rendered):.1f}% of Services", "📆", "bad")
with cols[6]:
    metric_card("No Engagement / No Attempts", f"{no_engagement_count:,}", f"{pct(no_engagement_count, total_caseload):.1f}% of Caseload", "🚫", "bad")

# ----------------------------
# Charts before Review Buttons
# ----------------------------
section_header("📈", "Dashboard Charts")

chart_col1, chart_col2, chart_col3 = st.columns([1.15, 1, 1])
with chart_col1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("### Service Procedure Breakdown")
    procedure_counts = (
        ms_df["ProcedureBase"]
        .value_counts()
        .reset_index()
        .rename(columns={"ProcedureBase": "Procedure", "count": "Total"})
    )
    fig_bar = px.bar(
        procedure_counts,
        y="Procedure",
        x="Total",
        text="Total",
        orientation="h",
        title=None,
    )
    fig_bar.update_layout(
        height=430,
        showlegend=False,
        margin=dict(l=10, r=10, t=15, b=10),
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="# of Services",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("### Engagement Overview")
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
        title=None,
        hole=0.35,
    )
    fig_pie_2.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie_2.update_layout(height=430, margin=dict(l=10, r=10, t=15, b=10), legend_title_text="")
    st.plotly_chart(fig_pie_2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col3:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("### Billable vs Non-Billable")
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
        title=None,
        hole=0.35,
    )
    fig_pie_1.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie_1.update_layout(height=430, margin=dict(l=10, r=10, t=15, b=10), legend_title_text="")
    st.plotly_chart(fig_pie_1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Buttons / Review Tables
# ----------------------------
section_header("🔎", "Review Buttons - Detailed Lists")
st.caption("Click a button to view the detailed list. Use Export to Excel or Print List to create a supervision-ready copy.")

if "selected_view" not in st.session_state:
    st.session_state.selected_view = "Successful Engagements"

button_cols = st.columns(5)
with button_cols[0]:
    if st.button(f"✅ Successful Engagements\n\n({successful_engagement_rows:,})", use_container_width=True):
        st.session_state.selected_view = "Successful Engagements"
with button_cols[1]:
    if st.button(f"📝 Non-Billable Totals\n\n({non_billable_total_rows:,})", use_container_width=True):
        st.session_state.selected_view = "Non-Billable Totals"
with button_cols[2]:
    if st.button(f"📞 Attempt Only / No Contact\n\n({attempt_only_count:,})", use_container_width=True):
        st.session_state.selected_view = "Attempt Only / No Contact"
with button_cols[3]:
    if st.button(f"📆 No Show / Cancel Total\n\n({no_show_cancel_total:,})", use_container_width=True):
        st.session_state.selected_view = "No Show / Cancel Total"
with button_cols[4]:
    if st.button(f"🚫 No Engagement / No Attempts\n\n({no_engagement_count:,})", use_container_width=True):
        st.session_state.selected_view = "No Engagement / No Attempts"

view_map = {
    "Successful Engagements": successful_list,
    "Non-Billable Totals": nonbillable_list,
    "Attempt Only / No Contact": attempt_summary,
    "No Show / Cancel Total": noshow_cancel_list,
    "No Engagement / No Attempts": no_engagement_list,
}

selected_df = view_map[st.session_state.selected_view]
st.markdown(f"<div class='selected-title'>{html.escape(st.session_state.selected_view)} ({len(selected_df):,})</div>", unsafe_allow_html=True)
st.dataframe(selected_df, use_container_width=True, hide_index=True)

export_col1, export_col2, export_col3 = st.columns([1, 1, 4])
with export_col1:
    st.download_button(
        label="Export to Excel",
        data=make_excel_download({st.session_state.selected_view: selected_df}),
        file_name=f"{st.session_state.selected_view.replace(' ', '_').replace('/', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
with export_col2:
    st.download_button(
        label="Print List (HTML)",
        data=make_printable_html(st.session_state.selected_view, selected_df, employee_name, review_period),
        file_name=f"{st.session_state.selected_view.replace(' ', '_').replace('/', '_')}_print.html",
        mime="text/html",
    )

# ----------------------------
# Supervisory Concern Lists
# ----------------------------
section_header("⚠️", "Supervisory Concern Lists")
concern_col1, concern_col2 = st.columns(2)
with concern_col1:
    st.markdown("### Attempt Only / No Contact")
    st.dataframe(attempt_summary, use_container_width=True, hide_index=True)
with concern_col2:
    st.markdown("### No Engagement / No Contact")
    st.dataframe(no_engagement_list, use_container_width=True, hide_index=True)

# ----------------------------
# Full Export Center
# ----------------------------
section_header("⬇️", "Download Center")
full_audit = make_excel_download(
    {
        "Successful Engagements": successful_list,
        "Non-Billable Totals": nonbillable_list,
        "Attempt Only No Contact": attempt_summary,
        "No Show Cancel Total": noshow_cancel_list,
        "No Engagement No Attempts": no_engagement_list,
        "Cleaned MyServicesList": ms_df,
        "Caseload Reference": caseload_df,
    }
)
st.download_button(
    label="Download Full Supervisory Audit Workbook",
    data=full_audit,
    file_name="Non_Billable_Caseload_Review_Dashboard_v2_Audit_Workbook.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.markdown(
    f"""
    <div class="note-box">
    Data is based on the uploaded files. Review employee: <b>{html.escape(employee_name)}</b>. Review period: <b>{html.escape(review_period)}</b>. Please verify source data accuracy before making supervisory decisions.
    </div>
    """,
    unsafe_allow_html=True,
)
