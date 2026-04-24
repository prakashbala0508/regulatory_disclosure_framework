import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from faker import Faker
from PIL import Image
import os

st.set_page_config(
    page_title="Regulatory Disclosure Review Framework",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #1B3A6B 0%, #2C5F9E 100%);
        padding: 2rem 2.5rem; border-radius: 12px;
        margin-bottom: 1.5rem; color: white;
    }
    .main-header h1 { margin: 0; font-size: 1.9rem; font-weight: 700; }
    .main-header p  { margin: 0.4rem 0 0; opacity: 0.85; font-size: 0.9rem; }
    .kpi-card {
        background: white; border-radius: 10px;
        padding: 1.25rem 1.5rem; border-left: 5px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 0.5rem;
    }
    .kpi-card .metric { font-size: 2rem; font-weight: 700; line-height: 1; }
    .kpi-card .label  { font-size: 0.8rem; color: #666; margin-top: 0.25rem; font-weight: 500; }
    .section-title {
        font-size: 1rem; font-weight: 600; color: #1B3A6B;
        border-bottom: 2px solid #C9A84C;
        padding-bottom: 0.4rem; margin: 1.2rem 0 1rem;
    }
    .rule-card {
        background: #F0F4F8; border-left: 4px solid #1B3A6B;
        padding: 1rem 1.2rem; border-radius: 6px; margin-bottom: 0.8rem;
    }
    .rule-card h4 { color: #1B3A6B; margin: 0 0 0.4rem; font-size: 0.95rem; }
    .rule-card p  { color: #444; margin: 0; font-size: 0.85rem; line-height: 1.5; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

SEV_COLORS = {
    "CRITICAL": "#C0392B",
    "HIGH":     "#E67E22",
    "MEDIUM":   "#F39C12",
    "LOW":      "#27AE60",
}

@st.cache_data
def generate_data():
    fake = Faker()
    random.seed(42)
    np.random.seed(42)
    TODAY = datetime.today()

    DISCLOSURE_CATEGORIES = {
        "Criminal - Felony":           {"severity": "CRITICAL", "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 1},
        "Criminal - Misdemeanor":      {"severity": "HIGH",     "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 2},
        "Regulatory Action - FINRA":   {"severity": "CRITICAL", "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 1},
        "Regulatory Action - SEC":     {"severity": "CRITICAL", "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 1},
        "Regulatory Action - State":   {"severity": "HIGH",     "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 2},
        "Civil Judicial Action":       {"severity": "HIGH",     "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 2},
        "Customer Complaint - Awards": {"severity": "HIGH",     "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 2},
        "Customer Complaint - Filed":  {"severity": "MEDIUM",   "rule": "FINRA Rule 4530", "escalate": False, "review_days": 5},
        "Financial - Bankruptcy":      {"severity": "MEDIUM",   "rule": "SEC Rule 17a-3",  "escalate": False, "review_days": 5},
        "Financial - Judgment/Lien":   {"severity": "MEDIUM",   "rule": "SEC Rule 17a-3",  "escalate": False, "review_days": 5},
        "Employment Termination":      {"severity": "MEDIUM",   "rule": "FINRA Rule 4530", "escalate": False, "review_days": 5},
        "Employment - Permitted Res.": {"severity": "LOW",      "rule": "SEC Rule 17a-3",  "escalate": False, "review_days": 10},
        "Investigation - Pending":     {"severity": "HIGH",     "rule": "FINRA Rule 4530", "escalate": True,  "review_days": 2},
        "Outside Business Activity":   {"severity": "LOW",      "rule": "FINRA Rule 3270", "escalate": False, "review_days": 10},
        "Financial - Unsatisfied":     {"severity": "LOW",      "rule": "SEC Rule 17a-3",  "escalate": False, "review_days": 10},
    }
    DEPARTMENTS    = ["Retail Brokerage","Institutional Sales","Investment Banking",
                      "Wealth Management","Compliance","Operations","Research","Trading"]
    REVIEW_STATUSES = ["PENDING","UNDER REVIEW","ESCALATED","CLEARED","REJECTED"]
    REVIEWERS       = ["J. Thompson","M. Patel","S. Williams","A. Garcia","R. Chen"]

    records = []
    for i in range(1, 321):
        category = random.choice(list(DISCLOSURE_CATEGORIES.keys()))
        meta     = DISCLOSURE_CATEGORIES[category]
        report_date  = fake.date_between(start_date="-2y", end_date="today")
        event_date   = report_date - timedelta(days=random.randint(1, 180))
        filing_deadline = event_date + timedelta(days=30)
        days_to_file    = (report_date - event_date).days
        filed_on_time   = "Yes" if days_to_file <= 30 else "No"

        if meta["severity"] == "CRITICAL":
            ow = [5, 10, 40, 30, 15]
        elif meta["severity"] == "HIGH":
            ow = [10, 20, 25, 35, 10]
        elif meta["severity"] == "MEDIUM":
            ow = [15, 25, 10, 45, 5]
        else:
            ow = [20, 15, 5, 55, 5]

        dollar_amt = random.randint(5000, 2500000) if ("Financial" in category or
                     "Customer Complaint - Awards" in category) else 0
        actual_days = random.randint(meta["review_days"] - 1, meta["review_days"] + 8)

        records.append({
            "Record_ID":           f"DR-{i:04d}",
            "Employee_ID":         f"EMP-{random.randint(1,200):04d}",
            "Full_Name":           f"{fake.first_name()} {fake.last_name()}",
            "Department":          random.choice(DEPARTMENTS),
            "Disclosure_Category": category,
            "Severity":            meta["severity"],
            "Governing_Rule":      meta["rule"],
            "Requires_Escalation": "Yes" if meta["escalate"] else "No",
            "Event_Date":          event_date.strftime("%Y-%m-%d"),
            "Report_Date":         report_date.strftime("%Y-%m-%d"),
            "Filing_Deadline":     filing_deadline.strftime("%Y-%m-%d"),
            "Days_To_File":        days_to_file,
            "Filed_On_Time":       filed_on_time,
            "Review_Status":       random.choices(REVIEW_STATUSES, weights=ow)[0],
            "Assigned_Reviewer":   random.choice(REVIEWERS),
            "Dollar_Amount":       dollar_amt,
            "Review_Days_SLA":     meta["review_days"],
            "Actual_Review_Days":  actual_days,
            "SLA_Breached":        "Yes" if actual_days > meta["review_days"] else "No",
        })
    return pd.DataFrame(records), TODAY

df, TODAY = generate_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Disclosure Review Framework")
    st.markdown(f"*As of {TODAY.strftime('%b %d, %Y')}*")
    st.divider()
    st.markdown("**Filter Records**")
    sev_opts  = ["All"] + ["CRITICAL","HIGH","MEDIUM","LOW"]
    sel_sev   = st.selectbox("Severity", sev_opts)
    dept_opts = ["All"] + sorted(df["Department"].unique().tolist())
    sel_dept  = st.selectbox("Department", dept_opts)
    rule_opts = ["All"] + sorted(df["Governing_Rule"].unique().tolist())
    sel_rule  = st.selectbox("Governing Rule", rule_opts)
    show_esc  = st.toggle("Escalation Required Only", value=False)
    show_late = st.toggle("Late Filings Only",         value=False)
    show_sla  = st.toggle("SLA Breached Only",         value=False)
    st.divider()
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Full Dataset (CSV)", csv, "disclosure_records.csv", "text/csv")

# ── Filter Logic ──────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_sev  != "All": fdf = fdf[fdf["Severity"]         == sel_sev]
if sel_dept != "All": fdf = fdf[fdf["Department"]        == sel_dept]
if sel_rule != "All": fdf = fdf[fdf["Governing_Rule"]    == sel_rule]
if show_esc:          fdf = fdf[fdf["Requires_Escalation"] == "Yes"]
if show_late:         fdf = fdf[fdf["Filed_On_Time"]       == "No"]
if show_sla:          fdf = fdf[fdf["SLA_Breached"]        == "Yes"]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>Regulatory Disclosure Review Framework</h1>
    <p>FINRA Rule 4530 &nbsp;|&nbsp; SEC Rule 17a-3 &nbsp;|&nbsp; BrokerCheck Disclosure Analytics &nbsp;|&nbsp; 320 Simulated Records</p>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total      = len(df)
critical_n = len(df[df["Severity"] == "CRITICAL"])
esc_n      = len(df[df["Requires_Escalation"] == "Yes"])
late_n     = len(df[df["Filed_On_Time"] == "No"])
timely_r   = round(len(df[df["Filed_On_Time"] == "Yes"]) / total * 100, 1)
sla_n      = len(df[df["SLA_Breached"] == "Yes"])

k1,k2,k3,k4,k5,k6 = st.columns(6)
for col, val, label, color in [
    (k1, total,          "Total Records",        "#1B3A6B"),
    (k2, critical_n,     "Critical Severity",    "#C0392B"),
    (k3, esc_n,          "Require Escalation",   "#E67E22"),
    (k4, late_n,         "Late Filings",         "#922B21"),
    (k5, f"{timely_r}%", "Timeliness Rate",      "#27AE60"),
    (k6, sla_n,          "SLA Breached",         "#8E44AD"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div class="metric" style="color:{color}">{val}</div>
            <div class="label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
col_a, col_b = st.columns([1, 2])

with col_a:
    st.markdown('<div class="section-title">Severity Distribution</div>', unsafe_allow_html=True)
    sc = df["Severity"].value_counts().reindex(["CRITICAL","HIGH","MEDIUM","LOW"]).reset_index()
    sc.columns = ["Severity","Count"]
    fig1 = px.pie(sc, values="Count", names="Severity",
                  color="Severity", color_discrete_map=SEV_COLORS, hole=0.55)
    fig1.update_traces(textposition="outside", textinfo="percent+label", textfont_size=10)
    fig1.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=300)
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">Disclosures by Category & Severity</div>', unsafe_allow_html=True)
    cat_df = df.groupby(["Disclosure_Category","Severity"]).size().reset_index(name="Count")
    fig2 = px.bar(cat_df, x="Count", y="Disclosure_Category", color="Severity",
                  color_discrete_map=SEV_COLORS, orientation="h", barmode="stack")
    fig2.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10),
                       legend_title="Severity", yaxis_title="",
                       plot_bgcolor="#F7F9FC", paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
col_c, col_d = st.columns([2, 1])

with col_c:
    st.markdown('<div class="section-title">Department Risk Heatmap</div>', unsafe_allow_html=True)
    pivot = (df.groupby(["Department","Severity"])
               .size().unstack(fill_value=0)
               .reindex(columns=["CRITICAL","HIGH","MEDIUM","LOW"], fill_value=0))
    fig3 = px.imshow(pivot, color_continuous_scale="YlOrRd",
                     labels=dict(color="Records"), aspect="auto", text_auto=True)
    fig3.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10))
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.markdown('<div class="section-title">Filing Timeliness (FINRA Rule 4530)</div>', unsafe_allow_html=True)
    tdf = df["Filed_On_Time"].value_counts().reset_index()
    tdf.columns = ["Filed_On_Time","Count"]
    tdf["Color"] = tdf["Filed_On_Time"].map({"Yes":"#27AE60","No":"#C0392B"})
    fig4 = px.bar(tdf, x="Filed_On_Time", y="Count",
                  color="Filed_On_Time",
                  color_discrete_map={"Yes":"#27AE60","No":"#C0392B"},
                  text="Count")
    fig4.update_layout(showlegend=False, height=300,
                       margin=dict(t=10,b=10,l=10,r=10),
                       plot_bgcolor="#F7F9FC", paper_bgcolor="white",
                       xaxis_title="Filed On Time", yaxis_title="Records")
    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Action Required", "Full Register", "Decision Tree", "Review Checklist", "Regulatory Guide"
])

display_cols = ["Record_ID","Full_Name","Department","Disclosure_Category",
                "Severity","Governing_Rule","Requires_Escalation",
                "Filed_On_Time","Review_Status","SLA_Breached","Days_To_File"]

def color_sev(val):
    m = {
        "CRITICAL": "background-color:#fde8e8;color:#C0392B;font-weight:600",
        "HIGH":     "background-color:#fef0e6;color:#E67E22;font-weight:600",
        "MEDIUM":   "background-color:#fef9e7;color:#d68910;font-weight:600",
        "LOW":      "background-color:#eafaf1;color:#1E8449;font-weight:600",
        "Yes":      "background-color:#fde8e8;color:#C0392B;font-weight:600",
        "No":       "background-color:#eafaf1;color:#1E8449;font-weight:600",
    }
    return m.get(val, "")

with tab1:
    st.markdown('<div class="section-title">Records Requiring Immediate Action</div>', unsafe_allow_html=True)
    action = fdf[fdf["Severity"].isin(["CRITICAL","HIGH"]) |
                 (fdf["Requires_Escalation"] == "Yes") |
                 (fdf["Filed_On_Time"] == "No")].sort_values("Severity")
    st.warning(f"{len(action)} records flagged for immediate attention.")
    styled = (action[display_cols].style
              .map(color_sev, subset=["Severity","Requires_Escalation",
                                      "Filed_On_Time","SLA_Breached"]))
    st.dataframe(styled, use_container_width=True, height=400)

with tab2:
    st.markdown('<div class="section-title">Full Disclosure Register</div>', unsafe_allow_html=True)
    styled2 = fdf[display_cols].style.map(color_sev, subset=["Severity"])
    st.dataframe(styled2, use_container_width=True, height=450)

with tab3:
    st.markdown('<div class="section-title">Disclosure Severity Decision Tree</div>', unsafe_allow_html=True)
    tree_path = os.path.join(os.path.dirname(__file__), "reports", "decision_tree.png")
    if os.path.exists(tree_path):
        img = Image.open(tree_path)
        st.image(img, use_column_width=True)
    else:
        st.info("Decision tree image not found. Run Jupyter Cell 5 to generate it.")
    st.markdown("""
    **Text-Based Logic Summary:**
    - **CRITICAL** (Criminal, Regulatory Actions) → Escalate to CCO within 24 hours, file U4 amendment
    - **HIGH** (Civil, Complaints, Investigations) → Escalate to Legal within 48 hours, notify supervisor
    - **MEDIUM** (Financial, Employment) → Standard 5-day SLA review, document findings
    - **LOW** (OBA, Minor Financial) → Routine 10-day SLA review, file if required
    - **Late Filing Detected** → Log Rule 4530 violation, notify Regulatory Affairs immediately
    - **All records** → Retain minimum 6 years per SEC Rule 17a-4
    """)

with tab4:
    st.markdown('<div class="section-title">Standard Disclosure Review Checklist</div>', unsafe_allow_html=True)
    checklist = {
        "Step": list(range(1, 16)),
        "Stage": [
            "Receipt","Receipt","Receipt","Categorization","Categorization",
            "Severity Assessment","Severity Assessment","Filing Check","Filing Check",
            "Substantive Review","Substantive Review","Substantive Review",
            "Disposition","Disposition","Recordkeeping"
        ],
        "Action Item": [
            "Log disclosure in compliance tracking system with date received",
            "Identify governing rule (FINRA 4530, SEC 17a-3, or FINRA 3270)",
            "Confirm employee CRD number and pull current BrokerCheck report",
            "Assign disclosure category from standard BrokerCheck taxonomy",
            "Determine if event is reportable under applicable rule",
            "Assess severity: CRITICAL / HIGH / MEDIUM / LOW",
            "Determine escalation requirement based on severity matrix",
            "Verify event date and calculate 30-day filing deadline",
            "Confirm timely filing; document late filing if applicable",
            "Request and review all supporting documentation",
            "Conduct substantive review per severity SLA",
            "Consult legal counsel if CRITICAL or HIGH severity",
            "Issue disposition: CLEARED, ESCALATED, or REJECTED",
            "File U4 amendment if disclosure changes registration status",
            "Retain all records minimum 6 years per SEC Rule 17a-4"
        ],
        "Governing Rule": [
            "FINRA Rule 4530","FINRA Rule 4530","FINRA Rule 4530",
            "BrokerCheck","FINRA Rule 4530",
            "Internal Policy","Internal Policy",
            "FINRA Rule 4530","FINRA Rule 4530",
            "FINRA Rule 4530","Internal SLA","FINRA Rule 4530",
            "Internal Policy","FINRA Form U4","SEC Rule 17a-4"
        ],
        "SLA": [
            "Same day","Same day","Same day",
            "1 business day","1 business day",
            "1 business day","1 business day",
            "1 business day","1 business day",
            "1-10 days (by severity)","1-10 days","2 business days",
            "Per SLA","30 days from event","Ongoing"
        ],
    }
    st.dataframe(pd.DataFrame(checklist), use_container_width=True, height=500)

with tab5:
    st.markdown('<div class="section-title">Plain-English Regulatory Reference Guide</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="rule-card">
        <h4>FINRA Rule 4530 — Reporting Requirements</h4>
        <p>Firms must report to FINRA within 30 calendar days when a registered person is
        charged with or convicted of any felony, or certain misdemeanors. Firms must also report
        written customer complaints alleging theft or misappropriation, or sales practice
        violations involving more than $5,000. Internal conclusions that a registered person
        violated FINRA rules or securities laws must also be reported.</p>
    </div>
    <div class="rule-card">
        <h4>SEC Rule 17a-3 — Records to Be Made</h4>
        <p>Broker-dealers must create and maintain records on each associated person including
        employment history, a record of any disciplinary actions, and information on any
        financial matters such as bankruptcies, judgments, or liens. These records form the
        foundation for BrokerCheck public disclosures and must be updated promptly when
        information changes.</p>
    </div>
    <div class="rule-card">
        <h4>FINRA Rule 3270 — Outside Business Activities</h4>
        <p>Registered persons must provide prior written notice to their member firm before
        engaging in any outside business activity for compensation. The firm must evaluate
        whether the activity conflicts with the individual's role or creates regulatory risk,
        and must retain records of all OBA notifications and firm responses.</p>
    </div>
    <div class="rule-card">
        <h4>SEC Rule 17a-4 — Record Retention</h4>
        <p>All required records must be retained for a minimum of 6 years, with the first
        2 years in an easily accessible location. Records must be stored in a non-rewriteable,
        non-erasable format (WORM). Failure to maintain records in the required format can
        result in significant regulatory sanctions.</p>
    </div>
    <div class="rule-card">
        <h4>BrokerCheck Disclosure Categories</h4>
        <p>FINRA BrokerCheck organizes disclosures into: Criminal (felony/misdemeanor),
        Regulatory Actions (FINRA/SEC/state), Civil Judicial Actions, Customer Complaints
        and Arbitrations, Employment Separations, Financial Matters (bankruptcy/liens),
        and Investigations. Each category carries different reporting thresholds,
        filing deadlines, and materiality standards that compliance staff must apply
        consistently across all registered individuals.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Record Lookup</div>', unsafe_allow_html=True)
search = st.text_input("Search by name, Employee ID, or Record ID",
                       placeholder="e.g. Smith or DR-0042 or EMP-0100")
if search:
    result = df[
        df["Full_Name"].str.contains(search, case=False) |
        df["Employee_ID"].str.contains(search, case=False) |
        df["Record_ID"].str.contains(search, case=False)
    ]
    if len(result):
        st.dataframe(result[display_cols], use_container_width=True)
    else:
        st.info("No matching records found.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="text-align:center;color:#888;font-size:0.8rem;padding:0.5rem 0">
    Regulatory Disclosure Review Framework &nbsp;|&nbsp;
    Simulated FINRA BrokerCheck Data &nbsp;|&nbsp;
    FINRA Rules 4530 & 3270 | SEC Rule 17a-3 &nbsp;|&nbsp;
    Built with Python and Streamlit
</div>
""", unsafe_allow_html=True)
