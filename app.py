import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Customer Intelligence",
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

@st.cache_data(show_spinner=False)
def load_data():
    data, missing = {}, []
    for key, filename in REQUIRED.items():
        path = DATA / filename
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            data[key] = pd.DataFrame()
            missing.append(filename)
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

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def clean_label(x):
    return str(x).replace("_", " ").replace("-", " ").title()

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def fmt_num(x):
    x = safe_float(x)
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"{x/1_000:.1f}K"
    return f"{x:,.0f}"

def fmt_money(x):
    x = safe_float(x)
    if abs(x) >= 1_000_000:
        return f"R$ {x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"R$ {x/1_000:.1f}K"
    return f"R$ {x:,.0f}"

def fmt_pct(x):
    return f"{safe_float(x) * 100:.1f}%"

def fmt_float(x):
    return f"{safe_float(x):.2f}"

def kpi_value(metric, default=0):
    if kpi.empty or not {"metric", "value"}.issubset(kpi.columns):
        return default
    hit = kpi.loc[kpi["metric"].astype(str).eq(metric), "value"]
    return safe_float(hit.iloc[0], default) if not hit.empty else default

def diag_value(metric, default=0):
    if rfm_diag.empty or not {"metric", "value"}.issubset(rfm_diag.columns):
        return default
    hit = rfm_diag.loc[rfm_diag["metric"].astype(str).eq(metric), "value"]
    return safe_float(hit.iloc[0], default) if not hit.empty else default

# -----------------------------------------------------------------------------
# Defensive shaping
# -----------------------------------------------------------------------------
if not category.empty:
    category = category.copy()
    if "main_category" in category.columns:
        category["category_label"] = category["main_category"].apply(clean_label)
    for col in ["gmv", "avg_review", "orders", "late_rate"]:
        if col in category.columns:
            category[col] = pd.to_numeric(category[col], errors="coerce")

if not state.empty:
    state = state.copy()
    if "customer_state" in state.columns:
        state["state_label"] = state["customer_state"].astype(str).str.upper()
    if "gmv" in state.columns:
        state["gmv"] = pd.to_numeric(state["gmv"], errors="coerce")

if not segment.empty:
    segment = segment.copy()
    if "segment" in segment.columns:
        segment["segment_label"] = segment["segment"].apply(clean_label)
    for col in ["customers", "avg_recency", "avg_frequency", "avg_monetary", "total_monetary", "revenue_share", "customer_share", "priority_score"]:
        if col in segment.columns:
            segment[col] = pd.to_numeric(segment[col], errors="coerce")
    if "revenue_share" not in segment.columns and "total_monetary" in segment.columns:
        total = segment["total_monetary"].sum()
        segment["revenue_share"] = segment["total_monetary"] / total if total else 0
    if "customer_share" not in segment.columns and "customers" in segment.columns:
        total = segment["customers"].sum()
        segment["customer_share"] = segment["customers"] / total if total else 0
    if "priority_score" not in segment.columns:
        segment["priority_score"] = segment.get("revenue_share", 0)

if not late_review.empty:
    late_review = late_review.copy()
    if "delivery_status" not in late_review.columns and "is_late" in late_review.columns:
        late_review["delivery_status"] = late_review["is_late"].map({False: "On Time", True: "Late", "False": "On Time", "True": "Late"})
        late_review["delivery_status"] = late_review["delivery_status"].fillna(late_review["is_late"].astype(str))
    for col in ["orders", "avg_review", "low_review_rate", "avg_delivery_days"]:
        if col in late_review.columns:
            late_review[col] = pd.to_numeric(late_review[col], errors="coerce")

if not model_cmp.empty:
    model_cmp = model_cmp.copy()
    for col in ["roc_auc", "average_precision", "precision_late", "recall_late", "f1_late"]:
        if col in model_cmp.columns:
            model_cmp[col] = pd.to_numeric(model_cmp[col], errors="coerce")

if not model_result.empty:
    model_result = model_result.copy()
    for col in ["roc_auc", "average_precision", "late_rate_baseline"]:
        if col in model_result.columns:
            model_result[col] = pd.to_numeric(model_result[col], errors="coerce")

if not risk.empty:
    risk = risk.copy()
    if "risk_level" in risk.columns:
        risk["risk_label"] = risk["risk_level"].apply(clean_label)
    for col in ["orders", "actual_late_rate", "avg_risk_score"]:
        if col in risk.columns:
            risk[col] = pd.to_numeric(risk[col], errors="coerce")

# -----------------------------------------------------------------------------
# Style
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
  background:
    radial-gradient(circle at 0% 0%, rgba(124,58,237,0.28), transparent 31%),
    radial-gradient(circle at 100% 5%, rgba(6,182,212,0.20), transparent 36%),
    linear-gradient(135deg, #060817 0%, #091123 48%, #0B1728 100%);
  color: #F8FAFC;
}
.block-container { padding-top: 0.85rem; padding-bottom: 2.2rem; max-width: 1280px; }
section[data-testid="stSidebar"] {
  width: 265px !important;
  background: rgba(7,10,24,0.98);
  border-right: 1px solid rgba(148,163,184,0.12);
}
section[data-testid="stSidebar"] * { color: #E5E7EB; }
[data-testid="stSidebar"] .stRadio > div { gap: 8px; }
[data-testid="stSidebar"] label { font-weight: 900; }
.hero {
  padding: 24px 30px 20px 30px;
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(17,24,39,0.92), rgba(30,41,59,0.72));
  border: 1px solid rgba(148,163,184,0.14);
  box-shadow: 0 28px 80px rgba(0,0,0,0.35);
  margin-bottom: 18px;
}
.hero h1 { font-size: 36px; line-height: 1.08; margin: 0; letter-spacing: -1.2px; }
.hero p { color: #A5B4FC; font-size: 15px; margin: 11px 0 0 0; }
.context-box {
  padding: 14px 17px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(6,182,212,0.10), rgba(124,58,237,0.10));
  border: 1px solid rgba(148,163,184,0.16);
  color:#CBD5E1;
  line-height:1.54;
  margin-bottom: 16px;
}
.context-box b { color:#F8FAFC; }
.context-box span { color:#A7F3D0; font-weight:900; }
.metric-card {
  min-height: 124px;
  border-radius: 24px;
  padding: 20px 22px;
  border: 1px solid rgba(255,255,255,0.12);
  background: linear-gradient(135deg, rgba(124,58,237,0.96), rgba(37,99,235,0.90));
  box-shadow: 0 24px 60px rgba(0,0,0,0.32);
}
.metric-card.cyan { background: linear-gradient(135deg, rgba(6,182,212,0.96), rgba(37,99,235,0.90)); }
.metric-card.dark { background: linear-gradient(135deg, rgba(30,41,59,0.90), rgba(15,23,42,0.98)); }
.metric-card.green { background: linear-gradient(135deg, rgba(16,185,129,0.80), rgba(6,182,212,0.70)); }
.metric-label { font-size:13px; font-weight:900; color:rgba(255,255,255,0.76); margin-bottom:9px; }
.metric-value { font-size:32px; font-weight:900; color:#FFFFFF; letter-spacing:-0.7px; }
.metric-note { font-size:12px; color:rgba(255,255,255,0.68); margin-top:8px; }
.panel {
  background: rgba(15,23,42,0.74);
  border: 1px solid rgba(148,163,184,0.13);
  border-radius: 26px;
  padding: 20px 22px 14px 22px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.25);
  margin-bottom: 16px;
}
.panel-title { font-size:18px; font-weight:900; color:#F8FAFC; margin-bottom:7px; }
.panel-subtitle { color:#94A3B8; font-size:13px; margin-bottom:10px; line-height:1.45; }
.rank-card {
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 15px; border-radius:18px;
  background:linear-gradient(135deg, rgba(255,255,255,0.045), rgba(255,255,255,0.025));
  border:1px solid rgba(255,255,255,0.08);
  margin-bottom:9px;
}
.rank-left { display:flex; align-items:center; gap:12px; }
.rank-no {
  width:34px; height:34px; border-radius:12px;
  display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg, #8B5CF6, #06B6D4);
  font-weight:900;
}
.rank-name { font-weight:900; color:#F8FAFC; }
.rank-caption { color:#94A3B8; font-size:12px; margin-top:2px; }
.rank-value { font-weight:900; color:#A7F3D0; }
.insight-card {
  padding:20px 22px; border-radius:22px;
  background:linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.74));
  border:1px solid rgba(148,163,184,0.14);
  box-shadow:0 18px 46px rgba(0,0,0,0.22);
  height:100%;
}
.tag {
  display:inline-block; padding:7px 11px; border-radius:999px;
  background:rgba(124,58,237,0.18);
  border:1px solid rgba(124,58,237,0.45);
  color:#DDD6FE; font-size:12px; font-weight:900; margin-bottom:12px;
}
.card-title { font-size:20px; font-weight:900; color:#FFFFFF; margin-bottom:8px; }
.card-body { color:#CBD5E1; font-size:14px; line-height:1.55; }
.card-rec { color:#A7F3D0; font-weight:800; }
.warn-mini { color:#FCD34D; font-size:13px; font-weight:800; }
div[data-testid="stDataFrame"] { display:none !important; }
.js-plotly-plot .modebar { display:none !important; }
</style>
""", unsafe_allow_html=True)

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}
FONT = dict(family="Inter", color="#E5E7EB")

# -----------------------------------------------------------------------------
# Components
# -----------------------------------------------------------------------------
def metric_card(label, value, note="", kind=""):
    return f"""
    <div class="metric-card {kind}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """

def context_box(title, role, purpose):
    st.markdown(f"""
    <div class="context-box">
        <b>{title}</b><br>
        <span>Mewakili:</span> {role}<br>
        <span>Fungsi:</span> {purpose}
    </div>
    """, unsafe_allow_html=True)

def panel_open(title, subtitle=""):
    st.markdown(f'<div class="panel"><div class="panel-title">{title}</div><div class="panel-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def panel_close():
    st.markdown('</div>', unsafe_allow_html=True)

def style_fig(fig, height=390, legend=True):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        margin=dict(l=6, r=6, t=28, b=6),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) if legend else dict(visible=False),
        hoverlabel=dict(bgcolor="#111827", bordercolor="rgba(255,255,255,.12)", font_size=13),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False, title_font=dict(size=12), tickfont=dict(size=12))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False, title_font=dict(size=12), tickfont=dict(size=12))
    return fig

def ranking_cards(df, name_col, value_col, caption_col=None, money=False, pct=False, top=6):
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
            cap_val = row.get(caption_col)
            if caption_col == "avg_review":
                caption = f"Avg Review: {fmt_float(cap_val)}"
            elif caption_col == "orders":
                caption = f"Orders: {fmt_num(cap_val)}"
            elif caption_col == "late_rate":
                caption = f"Late Rate: {fmt_pct(cap_val)}"
            else:
                caption = str(cap_val)
        st.markdown(f"""
        <div class="rank-card">
            <div class="rank-left">
                <div class="rank-no">{i}</div>
                <div>
                    <div class="rank-name">{name}</div>
                    <div class="rank-caption">{caption}</div>
                </div>
            </div>
            <div class="rank-value">{val_text}</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar and header
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ◈ CRM Dashboard")
st.sidebar.caption("Customer Intelligence")
page = st.sidebar.radio(
    "REPORT",
    ["Executive Overview", "Customer Segmentation", "Delivery Risk", "Business Insight"],
)
st.sidebar.markdown("---")
st.sidebar.markdown("### PROJECT OUTPUT")
st.sidebar.write("Business KPI")
st.sidebar.write("RFM Segmentation")
st.sidebar.write("Service Risk")
st.sidebar.write("Decision Insight")

st.markdown("""
<div class="hero">
    <h1>Customer Intelligence Dashboard</h1>
    <p>Business Intelligence • RFM Segmentation • Service Risk • Customer Review Insight</p>
</div>
""", unsafe_allow_html=True)

if missing_files:
    st.warning("Missing data files: " + ", ".join(missing_files))

# -----------------------------------------------------------------------------
# Page 1: Executive Overview
# -----------------------------------------------------------------------------
if page == "Executive Overview":
    context_box(
        "Executive Overview",
        "Kecerdasan Bisnis + Intuisi/Wawasan Data",
        "Membaca performa bisnis utama: GMV, order, keterlambatan, review, kategori produk, dan wilayah pasar."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Total GMV", fmt_money(kpi_value("Total GMV")), "Delivered transaction value"), unsafe_allow_html=True)
    c2.markdown(metric_card("Delivered Orders", fmt_num(kpi_value("Delivered Orders")), "Completed orders", "cyan"), unsafe_allow_html=True)
    c3.markdown(metric_card("Late Delivery Rate", fmt_pct(kpi_value("Late Delivery Rate")), "Operational risk", "dark"), unsafe_allow_html=True)
    c4.markdown(metric_card("Avg Review Score", fmt_float(kpi_value("Average Review Score")), "Customer experience proxy", "dark"), unsafe_allow_html=True)

    left, right = st.columns([1.45, 1])
    with left:
        panel_open("GMV and Orders Momentum", "Tren bulanan untuk membaca momentum pendapatan dan volume order.")
        if not monthly.empty and {"order_month", "gmv", "orders"}.issubset(monthly.columns):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["gmv"], name="GMV", mode="lines+markers", fill="tozeroy", line=dict(width=3)))
            fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["orders"], name="Orders", mode="lines+markers", yaxis="y2", line=dict(width=3)))
            fig.update_layout(
                yaxis=dict(title="GMV", tickprefix="R$ ", tickformat="~s"),
                yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
            )
            st.plotly_chart(style_fig(fig, 390), use_container_width=True, config=PLOT_CONFIG)
        panel_close()
    with right:
        panel_open("Top Markets", "Wilayah customer dengan kontribusi GMV terbesar.")
        ranking_cards(state.sort_values("gmv", ascending=False) if "gmv" in state.columns else state, "customer_state", "gmv", money=True, top=6)
        panel_close()

    left, right = st.columns([1.25, 1])
    with left:
        panel_open("Category Performance Portfolio")
        needed = {"category_label", "gmv", "avg_review", "orders", "late_rate"}
        if not category.empty and needed.issubset(category.columns):
            cat_show = category.sort_values("gmv", ascending=False).head(16).copy()
            fig = px.scatter(
                cat_show,
                x="avg_review",
                y="gmv",
                size="orders",
                color="late_rate",
                hover_name="category_label",
                labels={"avg_review": "Average Review", "gmv": "GMV", "orders": "Orders", "late_rate": "Late Rate"},
                size_max=45,
                color_continuous_scale="Bluered",
            )
            fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,.42)")))
            fig.update_yaxes(tickprefix="R$ ", tickformat="~s")
            st.plotly_chart(style_fig(fig, 420, legend=True), use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info("Category portfolio needs category_label, gmv, avg_review, orders, and late_rate.")
        panel_close()
    with right:
        panel_open("Category Priority", "Kategori terbesar sebagai kandidat fokus stok dan promosi.")
        ranking_cards(category.sort_values("gmv", ascending=False) if "gmv" in category.columns else category, "main_category", "gmv", "avg_review", money=True, top=6)
        panel_close()

# -----------------------------------------------------------------------------
# Page 2: Customer Segmentation
# -----------------------------------------------------------------------------
elif page == "Customer Segmentation":
    context_box(
        "Customer Segmentation",
        "Analisis Segmentasi Pelanggan",
        "Membaca prioritas pelanggan berbasis RFM dan menerjemahkannya menjadi aksi bisnis."
    )
    c1, c2, c3 = st.columns(3)
    c1.markdown(metric_card("RFM Customers", fmt_num(diag_value("Total Customers")), "Customer-level segmentation"), unsafe_allow_html=True)
    c2.markdown(metric_card("One-Time Rate", fmt_pct(diag_value("One-Time Customer Rate")), "Batasan utama RFM", "cyan"), unsafe_allow_html=True)
    c3.markdown(metric_card("Avg Frequency", fmt_float(diag_value("Average Frequency")), "Repeat behavior indicator", "dark"), unsafe_allow_html=True)

    st.markdown("""
    <div class="context-box">
        <b>Kenapa 6 segmen?</b><br>
        Segmentasi ini bukan clustering, melainkan <span>RFM rule-based business segmentation</span>. Lima segmen menangkap pola perilaku utama, dan <span>Regular Customers</span> dipakai sebagai default untuk pelanggan yang tidak masuk pola ekstrem. Ini sengaja dibuat agar rekomendasi bisnis langsung bisa dipakai.
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        panel_open("Revenue Contribution by Segment", "Kontribusi revenue per segmen. Bar lebih jelas daripada donut/heatmap untuk ranking.")
        if not segment.empty and {"segment_label", "revenue_share"}.issubset(segment.columns):
            seg_show = segment.sort_values("revenue_share", ascending=True).copy()
            fig = px.bar(seg_show, x="revenue_share", y="segment_label", orientation="h", text="revenue_share", labels={"revenue_share": "Revenue Share", "segment_label": "Segment"})
            fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
            fig.update_xaxes(tickformat=".0%")
            st.plotly_chart(style_fig(fig, 405, legend=False), use_container_width=True, config=PLOT_CONFIG)
        panel_close()
    with right:
        panel_open("Segment Priority", "Skor prioritas menggabungkan revenue, monetary value, frequency, dan recency.")
        if not segment.empty and {"segment_label", "priority_score"}.issubset(segment.columns):
            fig = px.bar(segment.sort_values("priority_score"), x="priority_score", y="segment_label", orientation="h", text="priority_score", labels={"priority_score": "Priority Score", "segment_label": "Segment"})
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            st.plotly_chart(style_fig(fig, 405, legend=False), use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    panel_open("Action Priority", "Kartu aksi segmen. Tidak memakai tabel mentah.")
    if not segment.empty and {"segment", "priority_score"}.issubset(segment.columns):
        cols = st.columns(2)
        show = segment.sort_values("priority_score", ascending=False).head(6)
        for i, row in enumerate(show.to_dict("records"), start=1):
            action = row.get("recommended_action", "Prioritize based on segment value")
            customers = row.get("customers", 0)
            revenue_share = row.get("revenue_share", 0)
            html = f"""
            <div class="rank-card">
                <div class="rank-left">
                    <div class="rank-no">{i}</div>
                    <div>
                        <div class="rank-name">{clean_label(row.get('segment','-'))}</div>
                        <div class="rank-caption">{action} • Customers: {fmt_num(customers)} • Revenue: {fmt_pct(revenue_share)}</div>
                    </div>
                </div>
                <div class="rank-value">{fmt_float(row.get('priority_score', 0))}</div>
            </div>
            """
            cols[(i-1) % 2].markdown(html, unsafe_allow_html=True)
    panel_close()

# -----------------------------------------------------------------------------
# Page 3: Delivery Risk
# -----------------------------------------------------------------------------
elif page == "Delivery Risk":
    context_box(
        "Delivery Risk",
        "Pemodelan Data Bisnis",
        "Menilai dampak keterlambatan terhadap review dan membandingkan model sebagai alat bantu prioritas monitoring, bukan sistem prediksi final."
    )
    selected_model = "-"
    roc = ap = baseline = 0
    if not model_result.empty:
        selected_model = model_result.get("selected_model", pd.Series(["-"])).iloc[0]
        roc = model_result.get("roc_auc", pd.Series([0])).iloc[0]
        ap = model_result.get("average_precision", pd.Series([0])).iloc[0]
        baseline = model_result.get("late_rate_baseline", pd.Series([0])).iloc[0]

    # review gap
    ontime_review = late_review.loc[late_review.get("delivery_status", pd.Series([])).astype(str).str.lower().eq("on time"), "avg_review"] if not late_review.empty and "delivery_status" in late_review.columns else pd.Series([])
    late_review_val = late_review.loc[late_review.get("delivery_status", pd.Series([])).astype(str).str.lower().eq("late"), "avg_review"] if not late_review.empty and "delivery_status" in late_review.columns else pd.Series([])
    gap = safe_float(ontime_review.iloc[0]) - safe_float(late_review_val.iloc[0]) if not ontime_review.empty and not late_review_val.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Review Gap", f"-{fmt_float(gap)}", "Late vs on-time review impact"), unsafe_allow_html=True)
    c2.markdown(metric_card("Best Model", str(selected_model), "Selected from comparison", "cyan"), unsafe_allow_html=True)
    c3.markdown(metric_card("ROC AUC", fmt_float(roc), "Ranking ability", "dark"), unsafe_allow_html=True)
    c4.markdown(metric_card("Average Precision", fmt_float(ap), f"Baseline late rate: {fmt_pct(baseline)}", "dark"), unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        panel_open("Service Impact: Late Delivery vs Review", "Kesimpulan bisnis utama: keterlambatan berkaitan dengan review lebih rendah.")
        if not late_review.empty and {"delivery_status", "avg_review"}.issubset(late_review.columns):
            lr = late_review.copy()
            lr["delivery_label"] = lr["delivery_status"].apply(clean_label)
            fig = px.bar(lr, x="delivery_label", y="avg_review", text="avg_review", labels={"delivery_label": "Delivery Status", "avg_review": "Average Review"})
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_yaxes(range=[0, 5])
            st.plotly_chart(style_fig(fig, 380, legend=False), use_container_width=True, config=PLOT_CONFIG)
        panel_close()
    with right:
        panel_open("Model Comparison", "Perbandingan metode: Logistic Regression, Decision Tree, dan Random Forest.")
        if not model_cmp.empty and {"model", "average_precision", "roc_auc"}.issubset(model_cmp.columns):
            cmp = model_cmp.sort_values("average_precision", ascending=False).copy()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=cmp["model"], y=cmp["average_precision"], name="Average Precision"))
            fig.add_trace(go.Scatter(x=cmp["model"], y=cmp["roc_auc"], name="ROC AUC", mode="lines+markers", yaxis="y2", line=dict(width=3)))
            fig.update_layout(yaxis=dict(title="Average Precision"), yaxis2=dict(title="ROC AUC", overlaying="y", side="right", showgrid=False))
            st.plotly_chart(style_fig(fig, 380), use_container_width=True, config=PLOT_CONFIG)
        panel_close()

    left, right = st.columns(2)
    with left:
        panel_open("Risk Model Boundary", "Bagian ini sengaja dibuat defensible agar tidak overclaim.")
        st.markdown(f"""
        <div class="insight-card">
            <div class="tag">Honest model reading</div>
            <div class="card-title">{selected_model} is a screening model</div>
            <div class="card-body">Model membantu memberi prioritas monitoring, bukan menggantikan keputusan operasional.</div>
            <div class="card-body"><b>Why cautious?</b> Average Precision hanya {fmt_float(ap)}, sehingga model belum layak disebut sistem prediksi final.</div>
            <div class="card-body card-rec">Keputusan utama tetap berdasarkan service impact: late orders punya review lebih rendah.</div>
        </div>
        """, unsafe_allow_html=True)
        panel_close()
    with right:
        panel_open("Risk Bucket Note", "Bucket dengan jumlah order terlalu kecil tidak dijadikan insight utama.")
        if not risk.empty and {"risk_level", "orders", "actual_late_rate"}.issubset(risk.columns):
            total_orders = risk["orders"].sum()
            valid = risk.copy()
            valid["share"] = valid["orders"] / total_orders if total_orders else 0
            for row in valid.to_dict("records"):
                level = clean_label(row.get("risk_level", "-"))
                orders = row.get("orders", 0)
                rate = row.get("actual_late_rate", 0)
                small = safe_float(row.get("share", 0)) < 0.01
                note = "Do not headline" if small else "Monitoring bucket"
                st.markdown(f"""
                <div class="rank-card">
                    <div class="rank-left">
                        <div class="rank-no">!</div>
                        <div>
                            <div class="rank-name">{level}</div>
                            <div class="rank-caption">Orders: {fmt_num(orders)} • {note}</div>
                        </div>
                    </div>
                    <div class="rank-value">{fmt_pct(rate)}</div>
                </div>
                """, unsafe_allow_html=True)
        panel_close()

# -----------------------------------------------------------------------------
# Page 4: Business Insight
# -----------------------------------------------------------------------------
elif page == "Business Insight":
    context_box(
        "Business Insight",
        "Intuisi dan Wawasan Data",
        "Mengubah KPI, segmentasi, dan risiko layanan menjadi keputusan bisnis yang dapat dijelaskan."
    )

    # Prefer generated high-level cards; fall back to insight_table content.
    top_cat = clean_label(category.sort_values("gmv", ascending=False).iloc[0]["main_category"]) if not category.empty and {"main_category", "gmv"}.issubset(category.columns) else "Top Category"
    top_state = str(state.sort_values("gmv", ascending=False).iloc[0]["customer_state"]).upper() if not state.empty and {"customer_state", "gmv"}.issubset(state.columns) else "Top State"
    top_seg = clean_label(segment.sort_values("priority_score", ascending=False).iloc[0]["segment"]) if not segment.empty and {"segment", "priority_score"}.issubset(segment.columns) else "Top Segment"

    decisions = [
        ("Commercial focus", top_cat, "Kategori dengan GMV tertinggi menjadi kandidat prioritas stok, promosi, dan campaign produk.", "Fokuskan promosi dan inventory planning pada kategori utama, bukan semua kategori sekaligus."),
        ("Market focus", top_state, "GMV terkonsentrasi pada wilayah tertentu, sehingga pasar tidak tersebar merata.", "Prioritaskan campaign dan evaluasi logistik pada wilayah dengan kontribusi terbesar."),
        ("Customer focus", top_seg, "Prioritas pelanggan ditentukan dari kombinasi revenue share, monetary, frequency, dan recency.", "Gunakan aksi berbeda per segmen: high-value offer, repeat-order campaign, atau reaktivasi selektif."),
        ("Service focus", "Late delivery lowers review", "Order terlambat memiliki rata-rata review lebih rendah dibanding order tepat waktu.", "Perbaiki SLA seller/logistik dan gunakan model sebagai screening monitoring, bukan keputusan otomatis."),
    ]

    for i in range(0, len(decisions), 2):
        cols = st.columns(2)
        for j, (tag, title, interpretation, recommendation) in enumerate(decisions[i:i+2]):
            cols[j].markdown(f"""
            <div class="insight-card">
                <div class="tag">{tag}</div>
                <div class="card-title">{title}</div>
                <div class="card-body"><b>Interpretation:</b> {interpretation}</div>
                <div class="card-body card-rec"><b>Recommendation:</b> {recommendation}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="context-box">
        <b>Kesimpulan</b><br>
        Dashboard ini tidak menjual model sebagai “akurat sempurna”. Nilai utamanya adalah <span>customer intelligence pipeline</span>: membaca performa bisnis, mengelompokkan pelanggan, menguji risiko layanan terhadap review, lalu mengubahnya menjadi rekomendasi keputusan.
    </div>
    """, unsafe_allow_html=True)
