import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Olist Customer Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA = Path("olist_output")

REQUIRED = {
    "kpi": "kpi.csv",
    "monthly": "monthly_kpi.csv",
    "category": "category_kpi.csv",
    "state": "state_kpi.csv",
    "segment": "segment_priority.csv",
    "rfm_diag": "rfm_diagnostic.csv",
    "late_review": "late_review_impact.csv",
    "model_cmp": "model_comparison.csv",
    "model_result": "model_result.csv",
    "risk": "risk_summary.csv",
    "insight": "insight_table.csv",
}


def _empty_df():
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_data():
    data = {}
    missing = []
    for key, file in REQUIRED.items():
        path = DATA / file
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            data[key] = _empty_df()
            missing.append(file)
    return data, missing


data, missing_files = load_data()
kpi = data["kpi"]
monthly = data["monthly"]
category = data["category"]
state = data["state"]
segment = data["segment"]
rfm_diag = data["rfm_diag"]
late_review = data["late_review"]
model_cmp = data["model_cmp"]
model_result = data["model_result"]
risk = data["risk"]
insight = data["insight"]

# -----------------------------
# Safe data preparation
# -----------------------------
def clean_label(x):
    return str(x).replace("_", " ").title()


def safe_col(df, col, default=None):
    return col in df.columns


def metric_value(name, default=0):
    if kpi.empty or "metric" not in kpi.columns or "value" not in kpi.columns:
        return default
    found = kpi.loc[kpi["metric"].astype(str).eq(name), "value"]
    if found.empty:
        return default
    try:
        return float(found.iloc[0])
    except Exception:
        return found.iloc[0]


def diag_value(name, default=0):
    if rfm_diag.empty or "metric" not in rfm_diag.columns or "value" not in rfm_diag.columns:
        return default
    found = rfm_diag.loc[rfm_diag["metric"].astype(str).eq(name), "value"]
    if found.empty:
        return default
    try:
        return float(found.iloc[0])
    except Exception:
        return found.iloc[0]


def fmt_num(x):
    try:
        x = float(x)
        if abs(x) >= 1_000_000:
            return f"{x/1_000_000:.2f}M"
        if abs(x) >= 1_000:
            return f"{x/1_000:.1f}K"
        return f"{x:,.0f}"
    except Exception:
        return str(x)


def fmt_money(x):
    try:
        x = float(x)
        if abs(x) >= 1_000_000:
            return f"R$ {x/1_000_000:.2f}M"
        if abs(x) >= 1_000:
            return f"R$ {x/1_000:.1f}K"
        return f"R$ {x:,.0f}"
    except Exception:
        return str(x)


def fmt_pct(x):
    try:
        return f"{float(x)*100:.1f}%"
    except Exception:
        return str(x)


def fmt_float(x):
    try:
        return f"{float(x):.2f}"
    except Exception:
        return str(x)


# enrich data defensively
if not category.empty and "main_category" in category.columns:
    category = category.copy()
    category["category_label"] = category["main_category"].apply(clean_label)

if not state.empty and "customer_state" in state.columns:
    state = state.copy()
    state["state_label"] = state["customer_state"].astype(str)

if not segment.empty:
    segment = segment.copy()
    if "revenue_share" not in segment.columns and "total_monetary" in segment.columns:
        total = segment["total_monetary"].sum()
        segment["revenue_share"] = segment["total_monetary"] / total if total else 0
    if "customer_share" not in segment.columns and "customers" in segment.columns:
        total = segment["customers"].sum()
        segment["customer_share"] = segment["customers"] / total if total else 0
    if "priority_score" not in segment.columns:
        segment["priority_score"] = segment.get("revenue_share", 0)
    if "segment" in segment.columns:
        segment["segment_label"] = segment["segment"].apply(clean_label)

if not late_review.empty and "delivery_status" not in late_review.columns and "is_late" in late_review.columns:
    late_review = late_review.copy()
    late_review["delivery_status"] = late_review["is_late"].map({False: "On Time", True: "Late", "False": "On Time", "True": "Late"}).fillna(late_review["is_late"].astype(str))

if not risk.empty and "risk_level" in risk.columns:
    risk = risk.copy()
    risk["risk_label"] = risk["risk_level"].astype(str)

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 5% 3%, rgba(139,92,246,0.32) 0%, rgba(139,92,246,0.02) 26%, transparent 42%),
        radial-gradient(circle at 95% 12%, rgba(6,182,212,0.20) 0%, rgba(6,182,212,0.02) 25%, transparent 45%),
        linear-gradient(135deg, #070A14 0%, #0B1020 45%, #12182B 100%);
    color: #F8FAFC;
}

.block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1380px; }

section[data-testid="stSidebar"] {
    background: rgba(8, 12, 26, 0.92);
    border-right: 1px solid rgba(148,163,184,0.12);
}
section[data-testid="stSidebar"] * { color: #E5E7EB; }

[data-testid="stSidebar"] .stRadio > div { gap: 10px; }
[data-testid="stSidebar"] label { font-weight: 700; }

.hero {
    padding: 34px 34px 26px 34px;
    border-radius: 30px;
    background: linear-gradient(135deg, rgba(17,24,39,0.92), rgba(30,41,59,0.68));
    border: 1px solid rgba(148,163,184,0.14);
    box-shadow: 0 30px 80px rgba(0,0,0,0.36);
    margin-bottom: 22px;
}
.hero h1 { font-size: 40px; line-height: 1.05; margin: 0; letter-spacing: -1.2px; }
.hero p { color: #A5B4FC; font-size: 15px; margin-top: 10px; margin-bottom: 0; }

.metric-card {
    min-height: 134px;
    border-radius: 26px;
    padding: 22px 24px;
    border: 1px solid rgba(255,255,255,0.12);
    background: linear-gradient(135deg, rgba(168,85,247,0.95), rgba(59,130,246,0.88));
    box-shadow: 0 24px 65px rgba(0,0,0,0.36);
}
.metric-card.cyan { background: linear-gradient(135deg, rgba(6,182,212,0.96), rgba(37,99,235,0.90)); }
.metric-card.dark { background: linear-gradient(135deg, rgba(30,41,59,0.92), rgba(15,23,42,0.98)); }
.metric-card.red { background: linear-gradient(135deg, rgba(244,63,94,0.88), rgba(168,85,247,0.72)); }
.metric-label { font-size: 13px; font-weight: 800; color: rgba(255,255,255,0.78); margin-bottom: 10px; }
.metric-value { font-size: 34px; font-weight: 900; color: #FFFFFF; letter-spacing: -0.6px; }
.metric-note { font-size: 12px; color: rgba(255,255,255,0.68); margin-top: 9px; }

.panel {
    background: rgba(15,23,42,0.76);
    border: 1px solid rgba(148,163,184,0.13);
    border-radius: 26px;
    padding: 22px 24px 16px 24px;
    box-shadow: 0 24px 65px rgba(0,0,0,0.25);
    margin-bottom: 18px;
}
.panel-title {
    font-size: 18px;
    font-weight: 900;
    color: #F8FAFC;
    margin-bottom: 8px;
    letter-spacing: -0.2px;
}
.panel-subtitle { color:#94A3B8; font-size: 13px; margin-bottom: 12px; }

.insight-card {
    padding: 20px 22px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.74));
    border: 1px solid rgba(148,163,184,0.14);
    box-shadow: 0 18px 46px rgba(0,0,0,0.22);
    height: 100%;
}
.tag {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(139,92,246,0.18);
    border: 1px solid rgba(139,92,246,0.45);
    color: #DDD6FE;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 12px;
}
.card-title { font-size: 20px; font-weight: 900; color: #FFFFFF; margin-bottom: 8px; }
.card-body { color:#CBD5E1; font-size: 14px; line-height: 1.55; }
.card-rec { color:#A7F3D0; font-weight: 700; }

.rank-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 15px 16px;
    border-radius: 18px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 10px;
}
.rank-left { display: flex; align-items:center; gap: 12px; }
.rank-no {
    width: 34px; height: 34px; border-radius: 12px;
    display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg, #8B5CF6, #06B6D4);
    font-weight: 900;
}
.rank-name { font-weight: 850; color:#F8FAFC; }
.rank-caption { color:#94A3B8; font-size:12px; margin-top:2px; }
.rank-value { font-weight: 900; color:#A7F3D0; }

.small-metric {
    padding: 16px 18px;
    border-radius: 20px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
}
.small-metric .label { color:#94A3B8; font-size: 12px; font-weight: 800; }
.small-metric .value { color:#F8FAFC; font-size: 24px; font-weight: 900; margin-top:4px; }


.section-note {
    padding: 16px 18px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(6,182,212,0.10), rgba(139,92,246,0.10));
    border: 1px solid rgba(148,163,184,0.16);
    color: #CBD5E1;
    font-size: 14px;
    line-height: 1.55;
    margin: 0 0 18px 0;
}
.section-note b { color: #F8FAFC; }
.section-note span { color: #A7F3D0; font-weight: 800; }

/* hide dataframe-like affordances globally if any accidental table appears */
div[data-testid="stDataFrame"] { display: none !important; }

.js-plotly-plot .modebar { display: none !important; }
</style>
""",
    unsafe_allow_html=True,
)

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}
FONT = dict(family="Inter", color="#E5E7EB")


def style_fig(fig, height=390, legend=True):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        margin=dict(l=10, r=10, t=35, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) if legend else dict(visible=False),
        hoverlabel=dict(bgcolor="#111827", bordercolor="rgba(255,255,255,.12)", font_size=13),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False, title_font=dict(size=12), tickfont=dict(size=12))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False, title_font=dict(size=12), tickfont=dict(size=12))
    return fig


def metric_card(label, value, note="", kind=""):
    return f"""
    <div class="metric-card {kind}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


def panel_open(title, subtitle=""):
    st.markdown(f'<div class="panel"><div class="panel-title">{title}</div><div class="panel-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def panel_close():
    st.markdown('</div>', unsafe_allow_html=True)


def section_note(title, role, purpose):
    st.markdown(
        f"""
        <div class="section-note">
            <b>{title}</b><br>
            <span>Mewakili:</span> {role}<br>
            <span>Fungsi dashboard:</span> {purpose}
        </div>
        """,
        unsafe_allow_html=True,
    )



def ranking_cards(df, name_col, value_col, caption_col=None, money=False, pct=False, top=5):
    if df.empty or name_col not in df.columns or value_col not in df.columns:
        st.info("Data belum tersedia.")
        return
    show = df.head(top).copy()
    for i, row in enumerate(show.to_dict("records"), start=1):
        name = clean_label(row.get(name_col, "-"))
        val = row.get(value_col, 0)
        if money:
            val_text = fmt_money(val)
        elif pct:
            val_text = fmt_pct(val)
        else:
            val_text = fmt_num(val)
        caption = ""
        if caption_col and caption_col in row:
            caption = f'<div class="rank-caption">{caption_col.replace("_", " ").title()}: {fmt_float(row.get(caption_col))}</div>'
        st.markdown(
            f"""
            <div class="rank-card">
                <div class="rank-left">
                    <div class="rank-no">{i}</div>
                    <div><div class="rank-name">{name}</div>{caption}</div>
                </div>
                <div class="rank-value">{val_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown("## ◈ CRM Dashboard")
st.sidebar.caption("Olist Customer Intelligence")
page = st.sidebar.radio(
    "REPORT",
    ["Executive Overview", "Customer Segmentation", "Delivery Risk", "Business Insight"],
)
st.sidebar.markdown("---")
st.sidebar.markdown("### PROJECT OUTPUT")
st.sidebar.markdown("Business KPI")
st.sidebar.markdown("RFM Segmentation")
st.sidebar.markdown("Risk Model")
st.sidebar.markdown("Insight")

if missing_files:
    st.sidebar.warning("Missing data: " + ", ".join(missing_files))

st.markdown(
    """
    <div class="hero">
        <h1>Olist Customer Intelligence Dashboard</h1>
        <p>Business Intelligence • RFM Segmentation • Delivery Risk • Customer Review Insight</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Executive Overview
# -----------------------------
if page == "Executive Overview":
    section_note("Executive Overview", "Kecerdasan Bisnis + Intuisi/Wawasan Data", "Meringkas performa bisnis utama: GMV, order, keterlambatan, review, kategori produk, dan wilayah pasar.")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Total GMV", fmt_money(metric_value("Total GMV")), "Delivered transaction value", ""), unsafe_allow_html=True)
    c2.markdown(metric_card("Delivered Orders", fmt_num(metric_value("Delivered Orders")), "Completed orders", "cyan"), unsafe_allow_html=True)
    c3.markdown(metric_card("Late Delivery Rate", fmt_pct(metric_value("Late Delivery Rate")), "Operational risk", "dark"), unsafe_allow_html=True)
    c4.markdown(metric_card("Avg Review Score", fmt_float(metric_value("Average Review Score")), "Customer experience proxy", "dark"), unsafe_allow_html=True)

    left, right = st.columns([1.55, 1])
    with left:
        panel_open("GMV and Orders Momentum", "Monthly revenue movement and order volume.")
        if not monthly.empty and {"order_month", "gmv", "orders"}.issubset(monthly.columns):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["gmv"], name="GMV", mode="lines+markers", fill="tozeroy"))
            fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["orders"], name="Orders", mode="lines+markers", yaxis="y2"))
            fig.update_layout(
                yaxis=dict(title="GMV"),
                yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
            )
            fig = style_fig(fig, 420)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    with right:
        panel_open("Top Markets", "Customer states contributing the most GMV.")
        ranking_cards(state.sort_values("gmv", ascending=False) if "gmv" in state.columns else state, "customer_state", "gmv", money=True, top=7)
        panel_close()

    left, right = st.columns([1.2, 1])
    with left:
        panel_open("Category Revenue Map", "Treemap view of product category contribution.")
        if not category.empty and {"category_label", "gmv"}.issubset(category.columns):
            fig = px.treemap(category.head(18), path=["category_label"], values="gmv")
            fig.update_traces(textinfo="label+value", hovertemplate="%{label}<br>GMV=%{value:,.0f}<extra></extra>")
            fig = style_fig(fig, 430, legend=False)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()
    with right:
        panel_open("Category Ranking", "Top categories by GMV.")
        ranking_cards(category.sort_values("gmv", ascending=False) if "gmv" in category.columns else category, "main_category", "gmv", "avg_review", money=True, top=7)
        panel_close()

# -----------------------------
# Customer Segmentation
# -----------------------------
elif page == "Customer Segmentation":
    section_note("Customer Segmentation", "Analisis Segmentasi Pelanggan", "Menampilkan hasil RFM, prioritas segmen, dan aksi bisnis tanpa tabel panjang.")
    c1, c2, c3 = st.columns(3)
    c1.markdown(metric_card("RFM Customers", fmt_num(diag_value("Total Customers")), "Customer-level segmentation", ""), unsafe_allow_html=True)
    c2.markdown(metric_card("One-Time Rate", fmt_pct(diag_value("One-Time Customer Rate")), "RFM limitation to explain", "cyan"), unsafe_allow_html=True)
    c3.markdown(metric_card("Avg Frequency", fmt_float(diag_value("Average Frequency")), "Repeat behavior indicator", "dark"), unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-note">
            <b>Segment reading guide</b><br>
            <span>Big Spenders</span> = pelanggan bernilai transaksi tinggi; 
            <span>New Customers</span> = pelanggan baru yang perlu didorong repeat order; 
            <span>Champions</span> = pelanggan terbaik tapi jumlahnya kecil; 
            <span>At Risk/Hibernating</span> = pelanggan lama/pasif yang perlu retensi atau reaktivasi selektif.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 1])
    with left:
        panel_open("Revenue Share by Segment", "Donut view of monetary contribution by customer segment.")
        if not segment.empty and {"segment_label", "revenue_share"}.issubset(segment.columns):
            fig = px.pie(segment, names="segment_label", values="revenue_share", hole=0.64)
            fig.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="%{label}<br>Share=%{percent}<extra></extra>")
            fig = style_fig(fig, 440)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    with right:
        panel_open("Segment Priority", "Priority score combines revenue, monetary value, frequency, and recency.")
        if not segment.empty and {"segment_label", "priority_score"}.issubset(segment.columns):
            fig = px.bar(segment.sort_values("priority_score"), x="priority_score", y="segment_label", orientation="h")
            fig = style_fig(fig, 440, legend=False)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    left, right = st.columns([1.25, 1])
    with left:
        panel_open("Segment Value Landscape", "Bubble chart: average monetary value vs average frequency.")
        if not segment.empty and {"avg_frequency", "avg_monetary", "customers", "segment_label"}.issubset(segment.columns):
            fig = px.scatter(
                segment,
                x="avg_frequency",
                y="avg_monetary",
                size="customers",
                hover_name="segment_label",
                size_max=55,
            )
            fig = style_fig(fig, 420, legend=False)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    with right:
        panel_open("Action Priority", "Top segments and recommended business actions.")
        if not segment.empty and {"segment", "priority_score"}.issubset(segment.columns):
            show = segment.sort_values("priority_score", ascending=False).head(5)
            for i, row in enumerate(show.to_dict("records"), start=1):
                action = row.get("recommended_action", "Prioritize based on segment value")
                st.markdown(
                    f"""
                    <div class="rank-card">
                        <div class="rank-left">
                            <div class="rank-no">{i}</div>
                            <div>
                                <div class="rank-name">{clean_label(row.get('segment','-'))}</div>
                                <div class="rank-caption">{action}</div>
                            </div>
                        </div>
                        <div class="rank-value">{fmt_float(row.get('priority_score', 0))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        panel_close()

# -----------------------------
# Delivery Risk
# -----------------------------
elif page == "Delivery Risk":
    section_note("Delivery Risk", "Pemodelan Data Bisnis", "Membaca dampak keterlambatan terhadap review dan membandingkan model risiko keterlambatan.")
    selected_model = "-"
    roc = 0
    ap = 0
    if not model_result.empty:
        selected_model = model_result.get("selected_model", pd.Series(["-"])).iloc[0]
        roc = model_result.get("roc_auc", pd.Series([0])).iloc[0]
        ap = model_result.get("average_precision", pd.Series([0])).iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.markdown(metric_card("Best Model", str(selected_model), "Selected from model comparison", ""), unsafe_allow_html=True)
    c2.markdown(metric_card("ROC AUC", fmt_float(roc), "Risk ranking ability", "cyan"), unsafe_allow_html=True)
    c3.markdown(metric_card("Average Precision", fmt_float(ap), "Minority-class focused", "dark"), unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        panel_open("Review Impact of Late Delivery", "Late orders show lower average review score.")
        if not late_review.empty and {"delivery_status", "avg_review"}.issubset(late_review.columns):
            fig = px.bar(late_review, x="delivery_status", y="avg_review", text="avg_review")
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig = style_fig(fig, 410, legend=False)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    with right:
        panel_open("Risk Level Calibration", "Actual late rate by predicted risk bucket.")
        if not risk.empty and {"risk_level", "actual_late_rate"}.issubset(risk.columns):
            fig = px.bar(risk, x="risk_level", y="actual_late_rate", text="actual_late_rate")
            fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
            fig = style_fig(fig, 410, legend=False)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    left, right = st.columns([1.25, 1])
    with left:
        panel_open("Model Comparison", "Average precision and ROC AUC across candidate models.")
        if not model_cmp.empty and {"model", "average_precision", "roc_auc"}.issubset(model_cmp.columns):
            cmp = model_cmp.copy()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=cmp["model"], y=cmp["average_precision"], name="Average Precision"))
            fig.add_trace(go.Scatter(x=cmp["model"], y=cmp["roc_auc"], name="ROC AUC", mode="lines+markers", yaxis="y2"))
            fig.update_layout(yaxis=dict(title="Average Precision"), yaxis2=dict(title="ROC AUC", overlaying="y", side="right", showgrid=False))
            fig = style_fig(fig, 420)
            st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    with right:
        panel_open("Risk Bucket Summary", "Orders and observed late rate by bucket.")
        if not risk.empty:
            for row in risk.to_dict("records"):
                level = row.get("risk_level", "-")
                orders = row.get("orders", 0)
                rate = row.get("actual_late_rate", 0)
                st.markdown(
                    f"""
                    <div class="rank-card">
                        <div class="rank-left">
                            <div class="rank-no">!</div>
                            <div>
                                <div class="rank-name">{level}</div>
                                <div class="rank-caption">Orders: {fmt_num(orders)}</div>
                            </div>
                        </div>
                        <div class="rank-value">{fmt_pct(rate)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        panel_close()

# -----------------------------
# Business Insight
# -----------------------------
elif page == "Business Insight":
    section_note("Business Insight", "Intuisi dan Wawasan Data", "Mengubah output KPI, segmentasi, dan model risiko menjadi rekomendasi keputusan bisnis.")
    if insight.empty:
        st.info("Insight data belum tersedia.")
    else:
        # prefer cards, no table
        rows = insight.to_dict("records")
        for start in range(0, len(rows), 2):
            cols = st.columns(2)
            for col, row in zip(cols, rows[start:start+2]):
                with col:
                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <div class="tag">{row.get('finding','Insight')}</div>
                            <div class="card-title">{row.get('evidence','-')}</div>
                            <div class="card-body"><b>Interpretation:</b> {row.get('interpretation','-')}</div>
                            <div class="card-body card-rec"><b>Recommendation:</b> {row.get('recommendation','-')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        panel_open("Top Segment Focus", "No table: top segment cards only.")
        if not segment.empty:
            show = segment.sort_values("priority_score", ascending=False).head(4) if "priority_score" in segment.columns else segment.head(4)
            for i, row in enumerate(show.to_dict("records"), start=1):
                st.markdown(
                    f"""
                    <div class="rank-card">
                        <div class="rank-left"><div class="rank-no">{i}</div><div><div class="rank-name">{clean_label(row.get('segment','-'))}</div><div class="rank-caption">{row.get('recommended_action','')}</div></div></div>
                        <div class="rank-value">{fmt_float(row.get('priority_score', row.get('revenue_share', 0)))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        panel_close()
    with right:
        panel_open("Model Snapshot", "Selected model and key evaluation metrics.")
        st.markdown(
            f"""
            <div class="small-metric"><div class="label">Selected model</div><div class="value">{selected_model if 'selected_model' in locals() else (model_result.get('selected_model', pd.Series(['-'])).iloc[0] if not model_result.empty and 'selected_model' in model_result.columns else '-')}</div></div><br>
            <div class="small-metric"><div class="label">ROC AUC</div><div class="value">{fmt_float(model_result.get('roc_auc', pd.Series([0])).iloc[0] if not model_result.empty else 0)}</div></div><br>
            <div class="small-metric"><div class="label">Average precision</div><div class="value">{fmt_float(model_result.get('average_precision', pd.Series([0])).iloc[0] if not model_result.empty else 0)}</div></div>
            """,
            unsafe_allow_html=True,
        )
        panel_close()
