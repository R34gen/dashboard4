import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Olist Customer Intelligence", page_icon="📊", layout="wide")
DATA = Path("olist_output")

@st.cache_data
def load_data():
    kpi = pd.read_csv(DATA / "kpi.csv")
    monthly = pd.read_csv(DATA / "monthly_kpi.csv")
    category = pd.read_csv(DATA / "category_kpi.csv")
    state = pd.read_csv(DATA / "state_kpi.csv")
    segment = pd.read_csv(DATA / "segment_priority.csv")
    rfm_diag = pd.read_csv(DATA / "rfm_diagnostic.csv")
    late_review = pd.read_csv(DATA / "late_review_impact.csv")
    model_cmp = pd.read_csv(DATA / "model_comparison.csv")
    model_result = pd.read_csv(DATA / "model_result.csv")
    risk = pd.read_csv(DATA / "risk_summary.csv")
    insight = pd.read_csv(DATA / "insight_table.csv")
    return kpi, monthly, category, state, segment, rfm_diag, late_review, model_cmp, model_result, risk, insight

kpi, monthly, category, state, segment, rfm_diag, late_review, model_cmp, model_result, risk, insight = load_data()

def get_kpi(metric):
    val = kpi.loc[kpi["metric"] == metric, "value"]
    return val.iloc[0] if len(val) else 0

def fmt_num(x):
    try: return f"{float(x):,.0f}"
    except Exception: return str(x)

def fmt_money(x):
    try: return f"R$ {float(x):,.0f}"
    except Exception: return str(x)

def fmt_pct(x):
    try: return f"{float(x):.2%}"
    except Exception: return str(x)

def fmt_float(x):
    try: return f"{float(x):.2f}"
    except Exception: return str(x)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #3B2A5A 0%, #151A2D 35%, #0D1120 100%);
    color: #EDEBFF;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111426 0%, #161A2F 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * { color: #EDEBFF; }
.main-title { font-size: 30px; font-weight: 800; color: #FFFFFF; margin-bottom: 2px; }
.subtitle { color: #9EA7D8; font-size: 14px; margin-bottom: 20px; }
.metric-card {
    padding: 22px 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(198,74,255,0.92), rgba(81,111,255,0.88));
    box-shadow: 0 18px 45px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.12);
    min-height: 118px;
}
.metric-card.cyan { background: linear-gradient(135deg, rgba(20,225,225,0.92), rgba(83,123,255,0.88)); }
.metric-card.dark { background: linear-gradient(135deg, rgba(28,34,60,0.95), rgba(24,29,50,0.96)); }
.metric-label { color: #DCE2FF; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.metric-value { color: #FFFFFF; font-size: 31px; font-weight: 800; line-height: 1.1; }
.metric-note { color: #B9C2EE; font-size: 12px; margin-top: 6px; }
.panel {
    background: rgba(18, 23, 42, 0.94);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 18px 18px 10px 18px;
    box-shadow: 0 14px 36px rgba(0,0,0,0.30);
    margin-bottom: 16px;
}
.panel-title { font-size: 16px; font-weight: 750; color: #FFFFFF; margin-bottom: 10px; }
.small-tag {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(205, 74, 255, 0.18);
    border: 1px solid rgba(205, 74, 255, 0.45);
    color: #F0C5FF;
    font-size: 12px;
    font-weight: 700;
}
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## CRM Dashboard")
st.sidebar.caption("Olist Customer Intelligence")
page = st.sidebar.radio("REPORT", ["Overview", "Customer Segmentation", "Delivery Risk", "Business Insight"])
st.sidebar.markdown("---")
st.sidebar.markdown("### PROJECT OUTPUT")
st.sidebar.write("Business KPI")
st.sidebar.write("RFM Segmentation")
st.sidebar.write("Risk Model")
st.sidebar.write("Insight")

plot_bg = "rgba(0,0,0,0)"
paper_bg = "rgba(0,0,0,0)"
font_color = "#EDEBFF"

def style_fig(fig, height=360):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=font_color, family="Arial"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig

st.markdown('<div class="main-title">Olist Customer Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Business Intelligence • RFM Segmentation • Delivery Risk • Customer Review Insight</div>', unsafe_allow_html=True)

if page == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total GMV</div><div class="metric-value">{fmt_money(get_kpi('Total GMV'))}</div><div class="metric-note">Delivered transactions</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card cyan"><div class="metric-label">Delivered Orders</div><div class="metric-value">{fmt_num(get_kpi('Delivered Orders'))}</div><div class="metric-note">Completed order base</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card dark"><div class="metric-label">Late Delivery Rate</div><div class="metric-value">{fmt_pct(get_kpi('Late Delivery Rate'))}</div><div class="metric-note">Operational risk</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card dark"><div class="metric-label">Avg Review Score</div><div class="metric-value">{fmt_float(get_kpi('Average Review Score'))}</div><div class="metric-note">Customer experience proxy</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([2, 1])
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Monthly GMV and Orders Trend</div>', unsafe_allow_html=True)
        fig = px.line(monthly, x="order_month", y=["gmv", "orders"], markers=True, labels={"value": "Value", "order_month": "Month", "variable": "Metric"})
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Top Customer States by GMV</div>', unsafe_allow_html=True)
        fig = px.bar(state.head(8).sort_values("gmv"), x="gmv", y="customer_state", orientation="h")
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Top Product Categories by GMV</div>', unsafe_allow_html=True)
        fig = px.bar(category.head(10).sort_values("gmv"), x="gmv", y="main_category", orientation="h")
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">KPI Table</div>', unsafe_allow_html=True)
        st.dataframe(kpi, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Customer Segmentation":
    total_customer = rfm_diag.loc[rfm_diag["metric"] == "Total Customers", "value"].iloc[0]
    one_time_rate = rfm_diag.loc[rfm_diag["metric"] == "One-Time Customer Rate", "value"].iloc[0]
    avg_freq = rfm_diag.loc[rfm_diag["metric"] == "Average Frequency", "value"].iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total RFM Customers</div><div class="metric-value">{fmt_num(total_customer)}</div><div class="metric-note">Customer-level segmentation</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card cyan"><div class="metric-label">One-Time Customer Rate</div><div class="metric-value">{fmt_pct(one_time_rate)}</div><div class="metric-note">Important RFM limitation</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card dark"><div class="metric-label">Average Frequency</div><div class="metric-value">{fmt_float(avg_freq)}</div><div class="metric-note">Repeat behavior indicator</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Revenue Share by Segment</div>', unsafe_allow_html=True)
        fig = px.donut(segment, names="segment", values="revenue_share", hole=0.62)
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Segment Priority Score</div>', unsafe_allow_html=True)
        fig = px.bar(segment.sort_values("priority_score"), x="priority_score", y="segment", orientation="h")
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Segment Summary</div>', unsafe_allow_html=True)
    st.dataframe(segment, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Delivery Risk":
    selected_model = model_result["selected_model"].iloc[0] if "selected_model" in model_result.columns else "-"
    roc_auc = model_result["roc_auc"].iloc[0]
    avg_precision = model_result["average_precision"].iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Selected Model</div><div class="metric-value" style="font-size:24px">{selected_model}</div><div class="metric-note">Best by AP and ROC AUC</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card cyan"><div class="metric-label">ROC AUC</div><div class="metric-value">{fmt_float(roc_auc)}</div><div class="metric-note">Ranking ability</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card dark"><div class="metric-label">Average Precision</div><div class="metric-value">{fmt_float(avg_precision)}</div><div class="metric-note">Minority-class focused</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Late vs On-Time Review Impact</div>', unsafe_allow_html=True)
        fig = px.bar(late_review, x="delivery_status", y="avg_review", text="avg_review")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Risk Level vs Actual Late Rate</div>', unsafe_allow_html=True)
        fig = px.bar(risk, x="risk_level", y="actual_late_rate", text="actual_late_rate")
        fig.update_traces(texttemplate="%{text:.2%}", textposition="outside")
        st.plotly_chart(style_fig(fig, 390), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Model Comparison</div>', unsafe_allow_html=True)
        st.dataframe(model_cmp, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Risk Summary</div>', unsafe_allow_html=True)
        st.dataframe(risk, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Business Insight":
    st.markdown('<div class="panel"><div class="panel-title">Final Business Insight</div>', unsafe_allow_html=True)
    for _, row in insight.iterrows():
        st.markdown(f"""
        <div style="padding:16px;border-radius:14px;background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.08);margin-bottom:12px;">
            <span class="small-tag">{row['finding']}</span>
            <h4 style="margin-top:12px;color:#FFFFFF;">Evidence: {row['evidence']}</h4>
            <p style="color:#C8CFF4;"><b>Interpretation:</b> {row['interpretation']}</p>
            <p style="color:#EDEBFF;"><b>Recommendation:</b> {row['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Top Segment Priority</div>', unsafe_allow_html=True)
        st.dataframe(segment.head(5), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Model Result</div>', unsafe_allow_html=True)
        st.dataframe(model_result, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
