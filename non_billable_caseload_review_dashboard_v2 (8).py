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
            radial-gradient(circle at top left, rgba(34, 99, 120, 0.20), transparent 35%),
            linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
        color: #f8fafc;
    }
    .main-title {
        padding: 1.25rem 1.35rem;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(15, 23, 42, .95), rgba(30, 41, 59, .88));
        border: 1px solid rgba(148, 163, 184, .35);
        box-shadow: 0 14px 35px rgba(0,0,0,.35);
        margin-bottom: 1rem;
    }
    .main-title h1 {
        margin: 0;
        font-size: 2.25rem;
        letter-spacing: .02em;
        color: #f8fafc;
    }
    .main-title p {
        margin: .35rem 0 0 0;
        color: #cbd5e1;
        font-size: 1.05rem;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(248, 250, 252, .10), rgba(148, 163, 184, .07));
        border: 1px solid rgba(203, 213, 225, .25);
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(0,0,0,.22);
        min-height: 115px;
    }
    .metric-label {
        font-size: .82rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: .45rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: .85rem;
        color: #94a3b8;
        margin-top: .35rem;
    }
    .section-box {
        padding: 1rem;
        border-radius: 18px;
        background: rgba(15, 23, 42, .58);
        border: 1px solid rgba(148, 163, 184, .22);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 14px;
        border: 1px solid rgba(203, 213, 225, .35);
        background: linear-gradient(135deg, #334155, #1e293b);
        color: white;
        font-weight: 700;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #93c5fd;
        color: white;
    }
    h2, h3 { color: #f8fafc; }
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

    # Make date columns easier to read in the printed view.
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


def metric_card(label: str, value: object, sub: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
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
# Dashboard Metrics
# ----------------------------
st.markdown("## Executive KPI Summary")
cols = st.columns(4)
with cols[0]:
    metric_card("Total Caseload Count", f"{total_caseload:,}", "From caseload file")
with cols[1]:
    metric_card("Total Services Rendered", f"{total_services_rendered:,}", "All rows in MyServicesList")
with cols[2]:
    metric_card("Successful Engagements", f"{successful_engagement_rows:,}", "Rows excluding non-billables, No Show, and Cancel")
with cols[3]:
    metric_card("Non-Billable Totals", f"{non_billable_total_rows:,}", "Non-billable codes plus No Show/Cancel")

cols2 = st.columns(4)
with cols2[0]:
    metric_card("Attempt Only / No Contact", f"{attempt_only_count:,}", "Clients with only attempts/non-billable activity")
with cols2[1]:
    metric_card("No Show / Cancel Total", f"{no_show_cancel_total:,}", "Rows with Status = No Show or Cancel")
with cols2[2]:
    metric_card("No Engagement / No Attempts", f"{no_engagement_count:,}", "Caseload clients missing from MS file")
with cols2[3]:
    metric_card("Total Units", f"{total_units:,.0f}", "Units documented in MyServicesList")

# ----------------------------
# Charts
# ----------------------------
st.markdown("## Dashboard Charts")

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
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
    fig_bar.update_layout(xaxis_tickangle=-35, height=520, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
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
        hole=0.35,
    )
    st.plotly_chart(fig_pie_1, use_container_width=True)

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
    hole=0.35,
)
st.plotly_chart(fig_pie_2, use_container_width=True)

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
    if st.button("No Show / Cancel Total", use_container_width=True):
        st.session_state.selected_view = "No Show / Cancel Total"
with button_cols[4]:
    if st.button("No Engagement / No Attempts", use_container_width=True):
        st.session_state.selected_view = "No Engagement / No Attempts"

view_map = {
    "Successful Engagements": successful_list,
    "Non-Billable Totals": nonbillable_list,
    "Attempt Only / No Contact": attempt_summary,
    "No Show / Cancel Total": noshow_cancel_list,
    "No Engagement / No Attempts": no_engagement_list,
}

selected_df = view_map[st.session_state.selected_view]
st.markdown(f"### {st.session_state.selected_view}")
st.dataframe(selected_df, use_container_width=True, hide_index=True)

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
        "No Show Cancel Total": noshow_cancel_list,
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
