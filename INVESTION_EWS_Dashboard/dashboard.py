from pathlib import Path
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

# Palette pilihan pengguna
AZURE = "#BEDEFF"
BASELINE = "#FFF2A7"  # baseline naif
ORANGE = "#FFA500"
MAROON = "#930031"
BROWN = "#472F26"
BG = "#FFF2A7"
PANEL = "#FFFDF7"
TEXT = "#472F26"
MUTED = "#5F493F"
BLUE = "#3E78A8"
RED = MAROON
PLOT_BG = "rgba(190,222,255,0.16)"

st.set_page_config(
    page_title="INVESTION | Volatility Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Tema cerah, elemen astronomi dekoratif, kontrol tanggal terbaca, dan ikon sidebar kontras.
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {{ color-scheme: light; --bg:{BG}; --azure:{AZURE}; --yellow:{BASELINE}; --brown:{BROWN}; --maroon:{MAROON}; }}
html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif; color:{TEXT}; }}
.stApp {{
  background-color:{BG};
  background-image:
    radial-gradient(circle at 8% 12%, rgba(255,255,255,.78) 0 2px, transparent 3px),
    radial-gradient(circle at 19% 34%, rgba(71,47,38,.18) 0 1px, transparent 2px),
    radial-gradient(circle at 84% 18%, rgba(255,255,255,.88) 0 2px, transparent 3px),
    radial-gradient(circle at 91% 52%, rgba(62,120,168,.15) 0 2px, transparent 3px),
    radial-gradient(ellipse at 4% 2%, rgba(190,222,255,.96), transparent 34%),
    radial-gradient(ellipse at 94% 92%, rgba(255,255,255,.8), transparent 30%),
    linear-gradient(128deg, #FFF2A7 0%, #FFF8D6 42%, #E9F5FF 78%, #FFF2A7 100%);
  background-attachment: fixed;
  color:{TEXT};
}}
[data-testid="stHeader"] {{ background:rgba(255,242,167,.72); }}
[data-testid="stMainBlockContainer"] {{ padding:0.65rem 1.15rem 1.1rem; max-width:100%; }}
/* Sidebar: light azure with framed square navigation controls. */
[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,#D7ECFA 0%,#BEDEFF 56%,#EAF5FF 100%);
  border-right:2px solid rgba(71,47,38,.35);
  box-shadow:8px 0 28px rgba(71,47,38,.09);
}}
[data-testid="stSidebar"] > div:first-child {{ border-right:0; }}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,[data-testid="stSidebar"] small {{ color:{BROWN} !important; }}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {{
  background:#FFFDF7!important; color:{BROWN}!important; -webkit-text-fill-color:{BROWN}!important;
  border:1px solid {BROWN}!important; border-radius:5px!important; font-weight:650!important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div {{ color:{BROWN}!important; }}
[data-baseweb="popover"], [data-baseweb="calendar"] {{ background:#FFFDF7!important; color:{BROWN}!important; }}
[data-baseweb="calendar"] * {{ color:{BROWN}!important; }}
/* Make the open/close sidebar arrow very visible on light and collapsed states. */
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {{
  background:#FFF2A7!important; color:{BROWN}!important; border:2px solid {BROWN}!important;
  border-radius:5px!important; box-shadow:0 3px 10px rgba(71,47,38,.18)!important;
}}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {{ color:{BROWN}!important; stroke:{BROWN}!important; fill:none!important; }}
/* Typography and visual cards */
h1,h2,h3,h4 {{ color:{BROWN}; font-family:'Manrope',sans-serif!important; letter-spacing:-.025em; }}
.eyebrow {{ color:{BROWN}; text-transform:uppercase; letter-spacing:2px; font-size:.75rem; font-weight:800; }}
.hero {{ position:relative; overflow:hidden; border:1px solid rgba(71,47,38,.23); border-radius:16px; padding:27px 30px; background:linear-gradient(105deg,rgba(190,222,255,.92),rgba(255,248,214,.93) 56%,rgba(255,242,167,.94)); box-shadow:0 12px 28px rgba(71,47,38,.10); }}
.hero h1 {{ color:{BROWN}!important; margin:5px 0 7px; font-size:clamp(1.6rem,2.2vw,2.35rem); }}
.hero p {{ color:{BROWN}; margin:0; max-width:900px; font-size:1rem; line-height:1.6; }}
.hero .cosmic-sticker {{ position:absolute; right:32px; top:13px; width:112px; height:112px; border:1.5px solid rgba(71,47,38,.35); border-radius:50%; transform:rotate(-20deg); pointer-events:none; }}
.hero .cosmic-sticker:before {{ content:'✦'; position:absolute; top:1px; right:5px; font-size:25px; color:{MAROON}; }}
.hero .cosmic-sticker:after {{ content:'☾'; position:absolute; left:28px; top:20px; font-size:48px; color:{BLUE}; text-shadow:2px 2px 0 {BASELINE}; }}
.space-chip {{ display:inline-block; padding:6px 10px; border:1px solid rgba(71,47,38,.23); border-radius:5px; background:rgba(255,253,247,.72); margin:7px 7px 0 0; color:{BROWN}; font-weight:650; font-size:.78rem; }}
.metric-card {{ position:relative; display:flex; flex-direction:column; background:linear-gradient(140deg,rgba(255,253,247,.95),rgba(255,248,214,.94)); border:1.5px solid rgba(71,47,38,.27); border-radius:8px; padding:14px 16px; min-height:132px; height:100%; box-shadow:0 7px 19px rgba(71,47,38,.08); transition:transform .2s,box-shadow .2s; }}
.metric-card:hover {{ transform:translateY(-3px); box-shadow:0 13px 25px rgba(71,47,38,.13); }}
.metric-label {{ color:{MUTED}; font-size:.75rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; }}
.metric-value {{ color:{BROWN}; font:800 clamp(1.15rem,1.65vw,1.75rem) Manrope,sans-serif; margin:11px 0 7px; line-height:1.22; overflow-wrap:anywhere; }}
.metric-note {{ color:{MUTED}; font-size:.84rem; line-height:1.45; margin-top:auto; }}
.section-head {{ display:flex; align-items:center; gap:10px; margin:11px 0 6px; }}
.section-head span {{ display:inline-flex; align-items:center; justify-content:center; min-width:38px; height:34px; background:{BASELINE}; border:1.5px solid rgba(71,47,38,.3); border-radius:5px; font-weight:850; color:{BROWN}; }}
.section-head h3 {{ margin:0; font-size:1.08rem; color:{BROWN}; }}
.panel {{ border:1px solid rgba(71,47,38,.22); border-radius:7px; padding:15px 17px; background:rgba(255,253,247,.68); color:{BROWN}; height:100%; }}
.business-note {{ background:linear-gradient(112deg,rgba(255,242,167,.75),rgba(190,222,255,.43)); border:1.5px solid rgba(71,47,38,.25); border-left:5px solid {MAROON}; border-radius:7px; padding:16px; color:{BROWN}; line-height:1.6; }}
.small-muted {{ color:{MUTED}; font-size:.86rem; line-height:1.5; }}
.legend-pill {{ display:inline-block; margin:3px 7px 5px 0; padding:5px 9px; border:1px solid rgba(71,47,38,.2); border-radius:4px; font-size:.78rem; font-weight:700; color:{BROWN}; }}
.legend-blue {{ background:{AZURE}; }} .legend-red {{ background:#F1C8D5; }} .legend-yellow {{ background:{BASELINE}; }}
.stButton>button,.stDownloadButton>button {{ border-radius:5px; border:1.5px solid {BROWN}; background:#FFFDF7; color:{BROWN}; font-weight:700; }}
.stButton>button:hover,.stDownloadButton>button:hover {{ background:{BASELINE}; border-color:{MAROON}; color:{BROWN}; }}
[data-testid="stDataFrame"] {{ background:rgba(255,253,247,.92); border:1.5px solid #8CB9D9; border-radius:7px; }}
[data-testid="stDataFrame"] [role="columnheader"] {{ background:#BEDEFF!important; color:#174A70!important; font-weight:800!important; }}
[data-testid="stDataFrame"] [role="gridcell"] {{ color:#FFF2A7!important; }}
[data-testid="stDataFrame"] [role="row"]:nth-child(even) [role="gridcell"] {{ background:#5F493F!important; }}
[data-testid="stDataFrame"] [role="row"]:nth-child(odd) [role="gridcell"] {{ background:#472F26!important; }}
[data-baseweb="tab-list"] {{ gap:5px; }}
[data-baseweb="tab"] {{ background:rgba(190,222,255,.7); border:1px solid rgba(71,47,38,.22); border-radius:5px 5px 0 0; color:{BROWN}!important; }}
[data-baseweb="tab"][aria-selected="true"] {{ background:{BASELINE}!important; color:{BROWN}!important; }}
div[data-testid="stPlotlyChart"] {{ background:transparent!important; border-radius:8px; }}
[data-testid="stMetric"] {{ background:rgba(255,253,247,.76); border:1px solid rgba(71,47,38,.2); border-radius:7px; padding:13px; }}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"],[data-testid="stMetricDelta"] {{ color:{BROWN}!important; }}
hr {{ border-color:rgba(71,47,38,.22); }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _read_csv(path, modified_time):
    frame = pd.read_csv(path)
    for date_col in ["Date", "Tanggal", "date", "tanggal"]:
        if date_col in frame.columns:
            frame[date_col] = pd.to_datetime(frame[date_col], errors="coerce")
    return frame


def read_csv(name):
    path = DATA / name
    file_stem, extension = path.stem, path.suffix
    duplicate_pattern = re.compile(
        rf"{re.escape(file_stem)} \((\d+)\){re.escape(extension)}"
    )
    candidates = [path] if path.exists() else []
    candidates.extend(
        candidate
        for candidate in DATA.glob(f"{file_stem} (*){extension}")
        if duplicate_pattern.fullmatch(candidate.name)
    )
    if not candidates:
        return None
    path = max(candidates, key=lambda candidate: candidate.stat().st_mtime_ns)
    return _read_csv(str(path), path.stat().st_mtime_ns)


def plot_theme(fig, height=None, plot_bg=PLOT_BG):
    fig.update_layout(
        template="plotly",
        paper_bgcolor="rgba(255,242,167,0)",
        plot_bgcolor=plot_bg,
        font=dict(color=TEXT, family="DM Sans, Segoe UI, sans-serif", size=12),
        margin=dict(l=16, r=16, t=48, b=18),
        legend=dict(title_text="", bgcolor="rgba(255,242,167,0)", font=dict(color=TEXT)),
        hoverlabel=dict(bgcolor=PANEL, font_color=TEXT, bordercolor=BROWN),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(71,47,38,.13)", zerolinecolor="rgba(71,47,38,.24)", tickfont=dict(color=TEXT), title_font=dict(color=TEXT))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(71,47,38,.13)", zerolinecolor="rgba(71,47,38,.24)", tickfont=dict(color=TEXT), title_font=dict(color=TEXT))
    if height:
        fig.update_layout(height=height)
    return fig


def style_table(frame):
    """Use warm gold text on deep rows for readable, high-contrast tables."""
    if frame is None or frame.empty:
        return frame
    return frame.style.set_table_styles([
        {"selector": "table", "props": [("border-collapse", "separate"), ("border-spacing", "0"), ("border", "1px solid #8B6B4E")]},
        {"selector": "th", "props": [("background-color", "#BEDEFF"), ("color", "#472F26"), ("font-weight", "900"), ("border-bottom", "2px solid #3E78A8"), ("padding", "10px 9px")]},
        {"selector": "td", "props": [("color", "#FFF2A7"), ("border-bottom", "1px solid #806B5C"), ("padding", "8px 9px"), ("font-weight", "650")]},
        {"selector": "tbody tr:nth-child(odd)", "props": [("background-color", "#472F26")]},
        {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#5F493F")]},
        {"selector": "tbody tr:hover", "props": [("background-color", "#765B47")]},
    ]).set_properties(**{"color": "#FFF2A7", "font-weight": "650"})


def pct(value):
    return "—" if pd.isna(value) else f"{value:.2%}"


def risk_color(label):
    text = str(label).upper()
    if "HIGH" in text or "DARURAT" in text or "BAHAYA" in text:
        return MAROON
    if "MODERATE" in text or "WASPADA" in text:
        return ORANGE
    if "LOW" in text or "AMAN" in text or "TENANG" in text:
        return BLUE
    return BROWN


def status_column(df):
    if df is None:
        return None
    return next((c for c in ["Status_Risiko", "EWS_Signal", "Sinyal_EWS"] if c in df.columns), None)


def validation_metric_rows(frame, predictions=None):
    required = {"Model", "RMSE", "MAE", "MAPE (%)"}
    if frame is not None and required.issubset(frame.columns):
        labels = frame["Model"].astype(str)
        baseline = frame[labels.str.contains("Baseline Naif", case=False, na=False)]
        catboost = frame[labels.str.contains("CatBoost", case=False, na=False)]
        if not baseline.empty and not catboost.empty:
            return baseline.iloc[0], catboost.iloc[0]

    if predictions is None or predictions.empty:
        return None
    columns = {
        "actual": next(
            (column for column in ["Actual_Volatility", "y_true", "Target_Volatilitas_Y", "Realized_Volatility"] if column in predictions.columns),
            None,
        ),
        "catboost": next(
            (column for column in ["CatBoost_Pred_Vol", "y_pred", "Prediksi_CatBoost"] if column in predictions.columns),
            None,
        ),
        "baseline": next(
            (column for column in ["Baseline_Naif_Pred", "baseline_pred", "Baseline_Pred"] if column in predictions.columns),
            None,
        ),
    }
    if any(column is None for column in columns.values()):
        return None

    values = predictions[list(columns.values())].apply(pd.to_numeric, errors="coerce").dropna()
    if values.empty:
        return None
    actual = values[columns["actual"]].to_numpy(dtype=float)
    catboost = values[columns["catboost"]].to_numpy(dtype=float)
    baseline = values[columns["baseline"]].to_numpy(dtype=float)
    nonzero_actuals = actual > 0

    def calculate_metrics(model_name, estimate):
        mape = (
            float(np.mean(np.abs((actual[nonzero_actuals] - estimate[nonzero_actuals]) / actual[nonzero_actuals])) * 100)
            if nonzero_actuals.any()
            else np.nan
        )
        return pd.Series({
            "Model": model_name,
            "RMSE": float(np.sqrt(np.mean((actual - estimate) ** 2))),
            "MAE": float(np.mean(np.abs(actual - estimate))),
            "MAPE (%)": mape,
        })

    return (
        calculate_metrics("Baseline Naif", baseline),
        calculate_metrics("CatBoost", catboost),
    )


def metric_reduction_percent(baseline, model, metric, export_column):
    exported_reduction = model.get(export_column, np.nan)
    if pd.notna(exported_reduction):
        return float(exported_reduction)
    baseline_value = float(baseline[metric])
    model_value = float(model[metric])
    return (baseline_value - model_value) / baseline_value * 100


def badge_for_risk(label):
    col = risk_color(label)
    return f"<span style='display:inline-block;border:1.5px solid {col};padding:7px 11px;border-radius:4px;color:{col};font-weight:850;background:rgba(255,253,247,.7)'>{label}</span>"


# Read project CSV artifacts.
shap_global = read_csv("xai_shap_feature_importance.csv")
shap_val = read_csv("xai_shap_values_validation.csv")
future = read_csv("xai_proyeksi_future_5d.csv")
analysis_metrics = read_csv("model_evaluation_metrics.csv")
test_pred = read_csv("test_ews_predictions.csv")
test_detail = read_csv("prediksi_target_volatilitas_y_test.csv")
validation_pred = read_csv("validation_predictions.csv")  # optional: actual vs CatBoost vs naive baseline

if future is not None and "Tanggal" in future.columns:
    future = future.dropna(subset=["Tanggal"]).sort_values("Tanggal")
if test_pred is not None and "Date" in test_pred.columns:
    test_pred = test_pred.dropna(subset=["Date"]).sort_values("Date")
if test_detail is not None and "Tanggal" in test_detail.columns:
    test_detail = test_detail.dropna(subset=["Tanggal"]).sort_values("Tanggal")
if shap_val is not None and "Date" in shap_val.columns:
    shap_val = shap_val.dropna(subset=["Date"]).sort_values("Date")
if validation_pred is not None:
    validation_date = next((c for c in ["Date", "Tanggal", "date"] if c in validation_pred.columns), None)
    if validation_date:
        validation_pred[validation_date] = pd.to_datetime(validation_pred[validation_date], errors="coerce")

validation_metrics = validation_metric_rows(analysis_metrics, validation_pred)
metrics_calculated_from_predictions = (
    validation_metric_rows(analysis_metrics) is None and validation_metrics is not None
)


def get_test_source():
    source = test_detail if test_detail is not None else test_pred
    if source is None or source.empty:
        return None
    dcol = "Tanggal" if "Tanggal" in source.columns else "Date"
    return source.sort_values(dcol)


def get_forecast_col(row):
    for c in ["Prediksi_Target_Volatilitas_Y", "CatBoost_Pred_Vol_5d", "Proyeksi_Volatilitas_5d"]:
        if c in row.index and pd.notna(row[c]):
            return c
    return None


def select_test_date_range(source, date_range):
    if source is None or source.empty:
        return source
    dcol = "Tanggal" if "Tanggal" in source.columns else "Date"
    if date_range and len(date_range) == 2:
        return source[(source[dcol].dt.date >= date_range[0]) & (source[dcol].dt.date <= date_range[1])]
    return source


# Sidebar filters. Native collapse control starts closed and can be opened using the high-contrast arrow.
with st.sidebar:
    st.markdown(
        f"""<div class="brand"><div class="brand-icon">✦</div><div><b style="font-size:1.16rem">INVESTION</b><br><small>VOLATILITY INTELLIGENCE</small></div></div>
        <div style="border:1.5px solid rgba(71,47,38,.32);padding:10px 12px;background:rgba(255,253,247,.55);margin-bottom:13px"><b>QUANT RISK DESK</b><br><small>IHSG · CatBoost · 5D forecast</small></div>""",
        unsafe_allow_html=True,
    )
    st.markdown("**FILTER DATA**")
    base_source = test_pred if test_pred is not None and not test_pred.empty else test_detail
    if base_source is not None and not base_source.empty:
        dcol = "Date" if "Date" in base_source.columns else "Tanggal"
        dmin, dmax = base_source[dcol].min().date(), base_source[dcol].max().date()
        selected_range = st.date_input("Rentang tanggal", value=(dmin, dmax), min_value=dmin, max_value=dmax)
    else:
        selected_range = None
    st.markdown("**Status model**")
    st.markdown("<div class='side-status'>CatBoost · coba 7 fix.ipynb<br><small>CSV hasil analisis · folder data/</small></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"<span class='legend-pill legend-yellow'>Baseline · {BASELINE}</span>", unsafe_allow_html=True)
    st.caption("Gunakan kontrol panah di bagian atas aplikasi untuk menyembunyikan atau membuka sidebar.")

# Prepare globally filtered test rows for the dashboard.
filtered_test = select_test_date_range(test_pred, selected_range) if test_pred is not None else None
filtered_detail = select_test_date_range(test_detail, selected_range) if test_detail is not None else None

st.markdown(
    "<div class='eyebrow' style='margin-bottom:4px'>PT INVESTION · EARLY WARNING & MODEL INSIGHTS</div>",
    unsafe_allow_html=True,
)

dashboard_sections = {
    "KPI & EWS",
    "Macroeconomic & Cross-Asset Stress",
    "Explainable AI & Projection",
    "Portfolio Hedging Simulator",
}

# ============================= EWS SUMMARY =============================
if "KPI & EWS" in dashboard_sections:
    if filtered_detail is None or filtered_detail.empty:
        st.error("File prediksi tidak ditemukan atau tidak ada observasi pada rentang tanggal pilihan. Periksa folder data/.")
        st.stop()

    last = filtered_detail.iloc[-1]
    date_val = last.get("Tanggal", pd.NaT)
    forecast_value = float(last.get("Prediksi_Target_Volatilitas_Y", np.nan))
    risk_value = str(last.get("Status_Risiko", "Tidak tersedia"))
    ihsg_value = float(last.get("IHSG", np.nan))
    ihsg_change = np.nan
    if len(filtered_detail) >= 2 and "IHSG" in filtered_detail.columns:
        prev = filtered_detail.iloc[-2]["IHSG"]
        if pd.notna(prev) and prev != 0:
            ihsg_change = ihsg_value / float(prev) - 1

    metric_rows = validation_metrics
    if metric_rows:
        baseline_metrics, catboost_metrics = metric_rows
        rmse_reduction = metric_reduction_percent(
            baseline_metrics,
            catboost_metrics,
            "RMSE",
            "RMSE_Reduction_Pct",
        )
        rmse_kpi = f"{rmse_reduction:.2f}%".replace(".", ",")
        rmse_note = "Penurunan RMSE validasi dibanding baseline naif"
    else:
        rmse_kpi = "—"
        rmse_note = "Jalankan notebook analisis untuk mengekspor metrik validasi"

    kpis = st.columns(4, gap="small")
    card_data = [
        ("LEVEL IHSG TERKINI", f"{ihsg_value:,.2f}" if pd.notna(ihsg_value) else "—", f"Perubahan harian: {pct(ihsg_change)}" if pd.notna(ihsg_change) else "Perubahan harian belum tersedia"),
        ("PROYEKSI VOLATILITAS 5 HARI", pct(forecast_value), f"Tanggal sinyal EWS: {pd.Timestamp(date_val).strftime('%d %b %Y') if pd.notna(date_val) else '—'}"),
        ("SINYAL EWS", risk_value, f"Snapshot per {pd.Timestamp(date_val).strftime('%d %b %Y') if pd.notna(date_val) else 'tanggal terbaru'}"),
        ("PENURUNAN RMSE VS BASELINE", rmse_kpi, rmse_note),
    ]
    for col, (label, value, note) in zip(kpis, card_data):
        with col:
            risk_style = f"color:{risk_color(value)};font-size:clamp(.98rem,1.3vw,1.45rem)" if label == "SINYAL EWS" else ""
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value' style='{risk_style}'>{value}</div><div class='metric-note'>{note}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='section-head'><span>01</span><h3>Risk Gauge & Ringkasan Sinyal</h3></div>", unsafe_allow_html=True)
    left, right = st.columns([0.7, 1.8], gap="medium")
    with left:
        max_gauge = max(2.0, forecast_value * 100 * 1.25) if pd.notna(forecast_value) else 2.0
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=forecast_value * 100 if pd.notna(forecast_value) else 0,
            number={"suffix": "%", "valueformat": ".2f", "font": {"color": BROWN, "size": 34}},
            title={"text": "Proyeksi volatilitas", "font": {"color": BROWN, "size": 15}},
            gauge={
                "axis": {"range": [0, max_gauge], "ticksuffix": "%", "tickcolor": BROWN, "tickfont": {"color": BROWN}},
                "bar": {"color": risk_color(risk_value), "thickness": 0.28},
                "bgcolor": "rgba(190,222,255,.24)", "bordercolor": "rgba(71,47,38,.35)",
                "steps": [
                    {"range": [0, max_gauge / 3], "color": "rgba(190,222,255,.26)"},
                    {"range": [max_gauge / 3, 2 * max_gauge / 3], "color": "rgba(255,242,167,.45)"},
                    {"range": [2 * max_gauge / 3, max_gauge], "color": "rgba(147,0,49,.10)"},
                ],
            },
        ))
        plot_theme(gauge, 250, plot_bg="rgba(255,242,167,0)")
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f"<div class='business-note'><b>{badge_for_risk(risk_value)}</b><br><br>Kategori risiko mengikuti sinyal EWS yang disediakan dari hasil model tim. Gunakan bersama informasi pasar dan batas risiko internal untuk mendukung pemantauan.</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("<div class='section-head'><span>02</span><h3>Lintasan Prediksi Volatilitas · Data Uji</h3></div>", unsafe_allow_html=True)
        if filtered_test is not None and not filtered_test.empty:
            chart = filtered_test.copy()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart["Date"], y=chart["CatBoost_Pred_Vol_5d"] * 100,
                mode="lines", name="Prediksi CatBoost",
                line=dict(color=MAROON, width=2.8),
                hovertemplate="Tanggal: %{x|%d %b %Y}<br>Prediksi: %{y:.3f}%<extra></extra>",
            ))
            # Optional baseline series is plotted only when genuinely present in the provided CSV.
            bcol = next((c for c in ["Baseline_Naif_Pred", "Baseline_Pred", "Baseline_Vol_5d"] if c in chart.columns), None)
            if bcol:
                fig.add_trace(go.Scatter(x=chart["Date"], y=chart[bcol] * 100, mode="lines", name="Baseline naif", line=dict(color=BASELINE, width=2.6, dash="dot")))
            fig.update_layout(xaxis_title="Tanggal", yaxis_title="Prediksi volatilitas (%)", hovermode="x unified")
            plot_theme(fig, 340, plot_bg="rgba(190,222,255,.14)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<span class='legend-pill legend-red'>Marun: prediksi CatBoost data uji</span><span class='legend-pill legend-yellow'>Kuning: baseline (jika tersedia)</span>", unsafe_allow_html=True)
            st.caption("Data uji berisi prediksi EWS; lintasan aktual dan evaluasi model ditampilkan terpisah pada grafik validasi.")
        else:
            st.warning("Tidak ada baris prediksi pada rentang tanggal yang dipilih.")

    st.markdown("<div class='section-head'><span>03</span><h3>Lintasan Prediksi Validasi · Aktual vs CatBoost vs Baseline</h3></div>", unsafe_allow_html=True)
    if validation_pred is not None and not validation_pred.empty:
        validation_date_col = next(
            (column for column in ["Date", "Tanggal", "date"] if column in validation_pred.columns),
            None,
        )
        actual_col = next(
            (column for column in ["Actual_Volatility", "y_true", "Target_Volatilitas_Y", "Realized_Volatility"] if column in validation_pred.columns),
            None,
        )
        prediction_col = next(
            (column for column in ["CatBoost_Pred_Vol", "y_pred", "Prediksi_CatBoost"] if column in validation_pred.columns),
            None,
        )
        baseline_col = next(
            (column for column in ["Baseline_Naif_Pred", "baseline_pred", "Baseline_Pred"] if column in validation_pred.columns),
            None,
        )
        if validation_date_col and actual_col and prediction_col and baseline_col:
            validation_chart = validation_pred[
                [validation_date_col, actual_col, prediction_col, baseline_col]
            ].copy()
            validation_chart = validation_chart.dropna(
                subset=[validation_date_col, actual_col, prediction_col, baseline_col]
            ).sort_values(validation_date_col)
            if not validation_chart.empty:
                actual_values = validation_chart[actual_col].to_numpy(dtype=float)
                catboost_values = validation_chart[prediction_col].to_numpy(dtype=float)
                baseline_values = validation_chart[baseline_col].to_numpy(dtype=float)
                catboost_rmse = float(np.sqrt(np.mean((actual_values - catboost_values) ** 2)))
                baseline_rmse = float(np.sqrt(np.mean((actual_values - baseline_values) ** 2)))
                nonzero_actuals = actual_values > 0
                catboost_mape = float(
                    np.mean(
                        np.abs(
                            (actual_values[nonzero_actuals] - catboost_values[nonzero_actuals])
                            / actual_values[nonzero_actuals]
                        )
                    )
                    * 100
                )
                set2_colors = px.colors.qualitative.Set2

                validation_fig = go.Figure()
                validation_fig.add_trace(go.Scatter(
                    x=validation_chart[validation_date_col],
                    y=actual_values,
                    mode="lines",
                    name="Realized Volatility (Aktual)",
                    line=dict(color=set2_colors[7], width=1.6),
                    hovertemplate="%{x|%d %b %Y}<br>Aktual: %{y:.5f}<extra></extra>",
                ))
                validation_fig.add_trace(go.Scatter(
                    x=validation_chart[validation_date_col],
                    y=catboost_values,
                    mode="lines",
                    name=f"CatBoost Prediksi (RMSE={catboost_rmse:.5f}, MAPE={catboost_mape:.1f}%)",
                    line=dict(color=set2_colors[0], width=1.3),
                    hovertemplate="%{x|%d %b %Y}<br>CatBoost: %{y:.5f}<extra></extra>",
                ))
                validation_fig.add_trace(go.Scatter(
                    x=validation_chart[validation_date_col],
                    y=baseline_values,
                    mode="lines",
                    name=f"Baseline Naif (RMSE={baseline_rmse:.5f})",
                    line=dict(color=set2_colors[1], width=1.5, dash="dot"),
                    opacity=0.6,
                    hovertemplate="%{x|%d %b %Y}<br>Baseline: %{y:.5f}<extra></extra>",
                ))
                validation_fig.update_layout(
                    title="Lintasan Prediksi Realized Volatility IHSG: CatBoost vs Realitas (Data Validasi 2022-2024)",
                    yaxis_title="Volatilitas Realisasi 5-Hari",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                )
                plot_theme(validation_fig, 330, plot_bg="rgba(190,222,255,.08)")
                st.plotly_chart(validation_fig, use_container_width=True)
                st.markdown(
                    "<span class='legend-pill' style='background:#B3B3B3'>Abu-abu: aktual</span>"
                    "<span class='legend-pill' style='background:#B9E3D0'>Toska: prediksi CatBoost</span>"
                    "<span class='legend-pill' style='background:#FAD0C3'>Koral: baseline naif</span>",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"{len(validation_chart):,} observasi validasi. "
                    "Skala, urutan seri, palet Set2, dan metrik dihitung dari seri validasi yang sama dengan notebook."
                )
            else:
                st.warning("CSV lintasan validasi tersedia, tetapi tidak memiliki baris lengkap untuk divisualisasikan.")
        else:
            st.warning(
                "CSV lintasan validasi belum memuat kolom Date, Actual_Volatility, "
                "CatBoost_Pred_Vol, dan Baseline_Naif_Pred."
            )
    else:
        st.info(
            "Jalankan notebook analisis dari sel evaluasi hingga visualisasi lintasan "
            "untuk membuat data/validation_predictions.csv."
        )

    st.markdown("<div class='section-head'><span>04</span><h3>Benchmark Validasi & Cakupan Periode</h3></div>", unsafe_allow_html=True)
    col_bench, col_timeline = st.columns([1.1, 1], gap="large")
    with col_bench:
        metric_rows = validation_metrics
        if metric_rows:
            baseline_metrics, catboost_metrics = metric_rows
            comparison = []
            for label, key, precision in [
                ("RMSE", "RMSE", 6),
                ("MAE", "MAE", 6),
                ("MAPE", "MAPE (%)", 2),
            ]:
                baseline_value = float(baseline_metrics[key])
                catboost_value = float(catboost_metrics[key])
                if label == "MAPE":
                    baseline_text = f"{baseline_value:.{precision}f}%"
                    catboost_text = f"{catboost_value:.{precision}f}%"
                    change_text = f"Turun {baseline_value - catboost_value:.2f} poin"
                else:
                    baseline_text = f"{baseline_value:.{precision}f}"
                    catboost_text = f"{catboost_value:.{precision}f}"
                    reduction = metric_reduction_percent(
                        baseline_metrics,
                        catboost_metrics,
                        key,
                        f"{label}_Reduction_Pct",
                    )
                    change_text = f"Turun {reduction:.2f}%"
                comparison.append({
                    "Metrik": label,
                    "Baseline naif": baseline_text,
                    "CatBoost": catboost_text,
                    "Perubahan": change_text,
                })
            st.dataframe(
                style_table(pd.DataFrame(comparison)),
                use_container_width=True,
                hide_index=True,
            )
            metrics_source_note = (
                "Metrik dihitung dari seri aktual, CatBoost, dan baseline pada CSV lintasan validasi."
                if metrics_calculated_from_predictions
                else "Nilai validasi 2022–2024 dari ekspor metrik notebook."
            )
            st.caption(
                f"{metrics_source_note} MAPE dibandingkan dalam poin persentase; "
                "RMSE dan MAE menunjukkan penurunan relatif."
            )
        else:
            st.info(
                "Metrik validasi belum tersedia. Jalankan notebook analisis "
                "agar model_evaluation_metrics.csv diperbarui."
            )
    with col_timeline:
        validation_count = len(shap_val) if shap_val is not None else 0
        test_count = len(test_pred) if test_pred is not None else 0
        future_count = len(future) if future is not None else 0
        st.markdown(f"""
        <div class='panel' style='margin-bottom:10px'><b>VALIDASI · 2022–2024</b><h2 style='margin:5px 0'>{validation_count:,} baris SHAP</h2><span class='small-muted'>Lintasan aktual, CatBoost, dan baseline divisualisasikan terpisah dari data uji.</span></div>
        <div class='panel' style='margin-bottom:10px'><b>UN-LABELED TEST · 2025–2026</b><h2 style='margin:5px 0'>{test_count:,} baris EWS</h2><span class='small-muted'>Berisi prediksi dan kategori risiko; aktual test tidak diasumsikan tersedia.</span></div>
        <div class='panel'><b>PROYEKSI 5 HARI</b><h2 style='margin:5px 0'>{future_count} titik proyeksi</h2><span class='small-muted'>18–22 Mei 2026 berdasarkan file proyeksi yang dilampirkan.</span></div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-head'><span>05</span><h3>Snapshot EWS · 5 Baris Terbaru</h3></div>", unsafe_allow_html=True)
    show_cols = [c for c in ["Tanggal", "IHSG", "Prediksi_Target_Volatilitas_Y", "Status_Risiko", "Interpretasi_Kondisi_Pasar", "Rekomendasi_Mitigasi_Investasi"] if c in filtered_detail.columns]
    recent = filtered_detail[show_cols].tail(5).copy()
    if "Prediksi_Target_Volatilitas_Y" in recent:
        recent["Prediksi_Target_Volatilitas_Y"] = recent["Prediksi_Target_Volatilitas_Y"].map(lambda v: f"{v:.3%}")
    st.dataframe(style_table(recent), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Unduh snapshot EWS (CSV)", filtered_detail[show_cols].to_csv(index=False).encode("utf-8-sig"), "investion_ews_snapshot.csv", "text/csv")

# ============================= THREE-PILLAR SHAP =============================
if "Macroeconomic & Cross-Asset Stress" in dashboard_sections:
    st.markdown("<div class='section-head'><span>06</span><h3>Dekomposisi SHAP · Tiga Pilar Risiko</h3></div>", unsafe_allow_html=True)
    pcols = ["SHAP_X1_Asym_EWMA_Vol", "SHAP_X2_Global_Contagion_Stress", "SHAP_X3_Macro_Drawdown_Spread"]
    labels_pillar = {pcols[0]: "X1 · Asymmetric EWMA Volatility", pcols[1]: "X2 · Global Contagion Stress", pcols[2]: "X3 · Macro Drawdown Spread"}
    if future is not None and all(c in future.columns for c in pcols):
        future_long = future.melt(id_vars=["Tanggal"], value_vars=pcols, var_name="Pilar", value_name="SHAP")
        future_long["Pilar"] = future_long["Pilar"].map(labels_pillar)
        fig = px.bar(future_long, x="Tanggal", y="SHAP", color="Pilar", barmode="group", color_discrete_sequence=[BLUE, ORANGE, MAROON], labels={"Tanggal": "Tanggal proyeksi", "SHAP": "Kontribusi SHAP"})
        fig.add_hline(y=0, line_color=BROWN, line_width=1)
        plot_theme(fig, 280, plot_bg="rgba(190,222,255,.08)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Warna membedakan pilar; batang di atas garis nol menaikkan prediksi, sedangkan batang di bawahnya menurunkan prediksi.")
    else:
        st.info("Kolom SHAP untuk ketiga pilar belum ditemukan pada file proyeksi.")

# ============================= SHAP & PROJECTION =============================
if "Explainable AI & Projection" in dashboard_sections:
    st.markdown("<div class='section-head'><span>07</span><h3>Explainable AI · SHAP & Proyeksi</h3></div>", unsafe_allow_html=True)
    st.caption("Faktor SHAP terpenting, penjelasan lokal untuk tanggal yang dipilih, dan lintasan proyeksi lima hari.")

    if shap_global is None:
        st.error("File xai_shap_feature_importance.csv tidak ditemukan di folder data/.")
        st.stop()

    glob = shap_global.sort_values("Rank").copy()
    top3 = glob.head(3)
    st.markdown("<div class='section-head'><span>07a</span><h3>Tiga Fitur dengan Mean Absolute SHAP Tertinggi</h3></div>", unsafe_allow_html=True)
    top_cols = st.columns(3, gap="medium")
    for col, (_, row) in zip(top_cols, top3.iterrows()):
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>RANK {int(row['Rank'])}</div><div class='metric-value' style='font-size:1.28rem'>{row['Feature']}</div><div class='metric-note'>Mean |SHAP|: {float(row['Mean_Abs_SHAP']):.5f}<br>Importance relatif: {float(row['Percentage_Importance (%)']):.2f}%</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'><span>07b</span><h3>SHAP Lokal · Pilih Tanggal</h3></div>", unsafe_allow_html=True)
    options = []
    if shap_val is not None and "Date" in shap_val.columns:
        options.extend([(d, "Validation") for d in shap_val["Date"].dropna().dt.date.unique()])
    if future is not None and "Tanggal" in future.columns:
        options.extend([(d, "Proyeksi") for d in future["Tanggal"].dropna().dt.date.unique()])
    options = sorted(set(options), key=lambda x: (x[0], x[1]))

    if options:
        # Default to the latest future projection date, if present.
        default_idx = len(options) - 1
        selected = st.selectbox("Tanggal analisis", options, index=default_idx, format_func=lambda x: f"{x[0]} · {'Proyeksi 5 hari' if x[1] == 'Proyeksi' else 'Validasi'}")
        chosen_date, source_type = selected
        shap_row = None
        if source_type == "Proyeksi" and future is not None:
            match = future[future["Tanggal"].dt.date == chosen_date]
            if not match.empty:
                shap_row = match.iloc[0]
        elif source_type == "Validation" and shap_val is not None:
            match = shap_val[shap_val["Date"].dt.date == chosen_date]
            if not match.empty:
                shap_row = match.iloc[0]

        if shap_row is not None:
            shap_cols = [c for c in shap_row.index if c.startswith("SHAP_") and pd.notna(shap_row[c])]
            local = pd.DataFrame({"Feature": [c.replace("SHAP_", "") for c in shap_cols], "SHAP": [float(shap_row[c]) for c in shap_cols]})
            local["Abs_SHAP"] = local["SHAP"].abs()
            local = local.sort_values("Abs_SHAP", ascending=True).tail(12)
            local["Arah kontribusi"] = np.where(local["SHAP"] >= 0, "Mendorong prediksi naik", "Mendorong prediksi turun")

            local_left, local_right = st.columns([1.7, 1], gap="large")
            with local_left:
                fig = go.Figure(go.Bar(x=local["SHAP"], y=local["Feature"], orientation="h", marker_color=[MAROON if v >= 0 else AZURE for v in local["SHAP"]], text=[f"{v:+.4f}" for v in local["SHAP"]], textposition="outside", hovertemplate="Fitur: %{y}<br>Kontribusi SHAP: %{x:.5f}<extra></extra>"))
                fig.add_vline(x=0, line_color=BROWN, line_width=1.4)
                fig.update_layout(xaxis_title="Kontribusi SHAP (unit output model)", yaxis_title="")
                plot_theme(fig, 340, plot_bg="rgba(190,222,255,.08)")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("<span class='legend-pill legend-blue'>Biru: kontribusi menurunkan prediksi</span><span class='legend-pill' style='background:#F1C8D5'>Marun: kontribusi menaikkan prediksi</span>", unsafe_allow_html=True)
                st.caption("Nilai base value tidak disertakan di file SHAP; visualisasi ini adalah kontribusi lokal bergaya waterfall, bukan waterfall absolut yang lengkap.")
            with local_right:
                strongest = local.reindex(local["Abs_SHAP"].sort_values(ascending=False).index).head(5)
                up = strongest[strongest["SHAP"] > 0]["Feature"].tolist()
                down = strongest[strongest["SHAP"] < 0]["Feature"].tolist()
                up_text = ", ".join(up) if up else "Tidak ada faktor positif di antara lima kontribusi terkuat."
                down_text = ", ".join(down) if down else "Tidak ada faktor negatif di antara lima kontribusi terkuat."
                st.markdown(f"<div class='business-note'><b>Terjemahan bahasa bisnis · {chosen_date}</b><br><br><b>Faktor pendorong:</b><br>{up_text}<br><br><b>Faktor penahan:</b><br>{down_text}<br><br><small>Interpretasi menggambarkan perilaku model dan tidak membuktikan sebab-akibat ekonomi.</small></div>", unsafe_allow_html=True)
                st.markdown("#### Tabel kontribusi lokal")
                st.dataframe(style_table(local.sort_values("Abs_SHAP", ascending=False).head(5)), use_container_width=True, hide_index=True, height=260)
                st.download_button("⬇️ Unduh kontribusi tanggal ini", local.to_csv(index=False).encode("utf-8-sig"), f"local_shap_{chosen_date}.csv", "text/csv")
    else:
        st.warning("Tidak ditemukan tanggal SHAP dalam file validasi maupun proyeksi.")

    st.markdown("<div class='section-head'><span>07c</span><h3>Tren Historis & Proyeksi Lima Hari Ke Depan</h3></div>", unsafe_allow_html=True)
    if future is not None and test_pred is not None and not future.empty and not test_pred.empty:
        future_start = future["Tanggal"].min()
        hist = test_pred[test_pred["Date"] < future_start].copy().tail(80)
        fig = go.Figure()
        if not hist.empty:
            fig.add_trace(go.Scatter(x=hist["Date"], y=hist["CatBoost_Pred_Vol_5d"] * 100, mode="lines", name="Historis · prediksi CatBoost", line=dict(color=MAROON, width=2.5), hovertemplate="%{x|%d %b %Y}<br>%{y:.3f}%<extra></extra>"))
            last_hist = hist.iloc[-1]
            future_dates = [last_hist["Date"]] + future["Tanggal"].tolist()
            future_values = [float(last_hist["CatBoost_Pred_Vol_5d"])] + future["Proyeksi_Volatilitas_5d"].astype(float).tolist()
            fig.add_trace(go.Scatter(x=future_dates, y=np.array(future_values) * 100, mode="lines+markers", name="Proyeksi 5 hari", line=dict(color=ORANGE, width=3, dash="dash"), marker=dict(size=8, color=ORANGE), hovertemplate="%{x|%d %b %Y}<br>Proyeksi: %{y:.3f}%<extra></extra>"))
        else:
            fig.add_trace(go.Scatter(x=future["Tanggal"], y=future["Proyeksi_Volatilitas_5d"] * 100, mode="lines+markers", name="Proyeksi 5 hari", line=dict(color=ORANGE, width=3, dash="dash"), marker=dict(size=9, color=ORANGE)))
        fig.add_vrect(x0=future_start, x1=future["Tanggal"].max(), fillcolor="rgba(255,165,0,.12)", line_width=1, line_color=ORANGE, annotation_text="Jendela proyeksi", annotation_position="top left")
        fig.update_layout(xaxis_title="Tanggal", yaxis_title="Volatilitas diprediksi (%)", hovermode="x unified")
        plot_theme(fig, 340, plot_bg="rgba(190,222,255,.08)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<span class='legend-pill legend-red'>Marun: riwayat prediksi test</span><span class='legend-pill' style='background:#FFE1B3'>Oranye: proyeksi 5 hari</span>", unsafe_allow_html=True)
        future_show = future.copy()
        future_show["Proyeksi (%)"] = future_show["Proyeksi_Volatilitas_5d"].map(lambda x: f"{x:.3%}")
        display_cols = [c for c in ["Tanggal", "IHSG_Terakhir", "Proyeksi (%)", "Sinyal_EWS"] if c in future_show.columns]
        st.dataframe(style_table(future_show[display_cols].head(5)), use_container_width=True, hide_index=True)
        st.download_button("⬇️ Unduh proyeksi lima hari", future.to_csv(index=False).encode("utf-8-sig"), "xai_proyeksi_future_5d.csv", "text/csv")
    else:
        st.info("Proyeksi lima hari atau seri historis test belum tersedia. Letakkan file output terkait ke folder data/.")

# ============================= PORTFOLIO SIMULATOR =============================
if "Portfolio Hedging Simulator" in dashboard_sections:
    st.markdown("<div class='section-head'><span>08</span><h3>Simulasi Hedging Portofolio</h3></div>", unsafe_allow_html=True)
    st.caption("Simulasi eksposur dan lindung nilai berdasarkan sinyal EWS; asumsi perhitungan ditampilkan secara transparan.")

    if filtered_detail is None or filtered_detail.empty:
        st.warning("Data EWS belum tersedia untuk rentang tanggal terpilih.")
        st.stop()

    row = filtered_detail.iloc[-1]
    signal = str(row.get("Status_Risiko", "Tidak tersedia"))
    forecast_vol = float(row.get("Prediksi_Target_Volatilitas_Y", 0.0))
    selected_day = row.get("Tanggal", pd.NaT)

    signal_upper = signal.upper()
    if "HIGH" in signal_upper or "DARURAT" in signal_upper or "BAHAYA" in signal_upper:
        recommended_hedge = 100
        recommendation = "Sinyal risiko tinggi: evaluasi lindung nilai, kurangi konsentrasi, periksa likuiditas, dan eskalasi keputusan kepada komite risiko. Porsi hedge 100% hanya merupakan skenario ilustratif sesuai blueprint, bukan instruksi transaksi."
        action_mix = "Evaluasi put-option hedge · review eksposur secara menyeluruh"
    elif "MODERATE" in signal_upper or "WASPADA" in signal_upper:
        recommended_hedge = 20
        recommendation = "Sinyal risiko moderat: pertimbangkan hedge parsial, perketat stop-loss, dan tinjau alokasi defensif. Validasi biaya serta instrumen lindung nilai sebelum pelaksanaan."
        action_mix = "80% ekuitas · 20% pasar uang (ilustrasi)"
    else:
        recommended_hedge = 0
        recommendation = "Sinyal risiko rendah: pertahankan pemantauan berkala dan evaluasi ulang bila volatilitas atau sinyal EWS meningkat."
        action_mix = "100% ekuitas · 0% hedge (ilustrasi)"

    input_col, result_col = st.columns([.95, 1.45], gap="large")
    with input_col:
        st.markdown("<div class='section-head'><span>01</span><h3>Parameter Portofolio</h3></div>", unsafe_allow_html=True)
        aum_trillion = st.slider("Dana kelolaan (AUM), Rp triliun", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        hedge_pct = st.slider("Porsi lindung nilai simulasi (%)", min_value=0, max_value=100, value=recommended_hedge, step=5)
        st.markdown(f"<div class='panel'><b>Tanggal sinyal</b><h3 style='margin:5px 0'>{pd.Timestamp(selected_day).strftime('%d %B %Y')}</h3><div>{badge_for_risk(signal)}</div><p class='small-muted' style='margin-top:9px'>Prediksi volatilitas 5 hari: <b>{forecast_vol:.3%}</b></p></div>", unsafe_allow_html=True)
        st.markdown("<div class='panel' style='margin-top:10px'><b>Alokasi ilustratif sesuai status</b><p class='small-muted'>" + action_mix + "</p></div>", unsafe_allow_html=True)

    # Gaussian 99% normal approximation; assumes the target is a five-day volatility fraction.
    aum_idr = aum_trillion * 1_000_000_000_000
    var99 = aum_idr * forecast_vol * 2.326
    hedged_amount = aum_idr * hedge_pct / 100
    residual_estimate = var99 * (1 - hedge_pct / 100)

    with result_col:
        st.markdown("<div class='section-head'><span>02</span><h3>Estimasi Eksposur Risiko</h3></div>", unsafe_allow_html=True)
        r1, r2 = st.columns(2, gap="medium")
        with r1:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Estimasi VaR 99% · 5 Hari</div><div class='metric-value' style='font-size:1.55rem'>Rp {var99/1e9:,.2f} M</div><div class='metric-note'>Skenario Gaussian sederhana</div></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Nilai AUM Di-hedge</div><div class='metric-value' style='font-size:1.55rem'>Rp {hedged_amount/1e9:,.0f} M</div><div class='metric-note'>Porsi simulasi: {hedge_pct}%</div></div>", unsafe_allow_html=True)
        r3, r4 = st.columns(2, gap="medium")
        with r3:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Sisa Risiko · Simulasi</div><div class='metric-value' style='font-size:1.55rem'>Rp {residual_estimate/1e9:,.2f} M</div><div class='metric-note'>Asumsi pengurangan proporsional</div></div>", unsafe_allow_html=True)
        with r4:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Potensi Penurunan Eksposur</div><div class='metric-value' style='font-size:1.55rem'>{hedge_pct:.0f}%</div><div class='metric-note'>Asumsi ideal, bukan hasil instrumen aktual</div></div>", unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=["Tanpa hedge", "Setelah hedge · simulasi"],
            y=[var99 / 1e9, residual_estimate / 1e9],
            marker_color=[MAROON, AZURE],
            text=[f"Rp {var99/1e9:,.2f} M", f"Rp {residual_estimate/1e9:,.2f} M"],
            textposition="outside",
            textfont=dict(color=BROWN),
            hovertemplate="%{x}<br>Estimasi risiko: Rp %{y:.2f} miliar<extra></extra>",
        ))
        fig.update_layout(yaxis_title="Estimasi risiko (Rp miliar)")
        plot_theme(fig, 325, plot_bg="rgba(190,222,255,.08)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-head'><span>03</span><h3>Rekomendasi Aksi untuk Diskusi Komite Investasi</h3></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='business-note'><b>{badge_for_risk(signal)}</b><br><br>{recommendation}<br><br><b>Asumsi simulasi:</b> VaR 99% diperkirakan sebagai AUM × proyeksi volatilitas 5-hari × 2,326. Dampak hedge dianggap proporsional pada simulasi ini dan belum memperhitungkan harga opsi, basis risk, likuiditas, komposisi aset, atau perubahan distribusi return.</div>", unsafe_allow_html=True)

    report = pd.DataFrame([{
        "Tanggal": pd.Timestamp(selected_day).strftime("%Y-%m-%d"),
        "Sinyal_EWS": signal,
        "Prediksi_Volatilitas_5d": forecast_vol,
        "AUM_Rp": aum_idr,
        "Estimasi_VaR99_Rp": var99,
        "Proporsi_Hedge_Persen": hedge_pct,
        "Nilai_Hedge_Rp": hedged_amount,
        "Sisa_Estimasi_Risiko_Rp": residual_estimate,
        "Asumsi": "Gaussian 99%, target diasumsikan volatilitas 5-hari; hedge proporsional ilustratif",
    }])
    st.download_button("⬇️ Unduh ringkasan mitigasi (CSV)", report.to_csv(index=False).encode("utf-8-sig"), "investion_hedging_simulation.csv", "text/csv")

st.divider()
st.caption("INVESTION · Visualisasi hasil analisis tim. Semua metrik, klasifikasi EWS, kontribusi SHAP, dan asumsi simulasi harus ditinjau sebelum dipakai untuk keputusan atau presentasi final.")
