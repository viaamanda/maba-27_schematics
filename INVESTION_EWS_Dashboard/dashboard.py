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
GOLD = "#8A6500"
BG = "#FFF2A7"
PANEL = "#FFFDF7"
TEXT = "#472F26"
MUTED = BROWN
BLUE = "#3E78A8"
RED = MAROON
PLOT_BG = "rgba(190,222,255,0.16)"

st.set_page_config(
    page_title="Volatility Intelligence",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Tema tetap dengan elemen dekoratif dan kontrol tanggal terbaca.
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
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {{ display:none!important; }}
[data-testid="stMainBlockContainer"] {{ padding:1.1rem 1.15rem; max-width:100%; }}
[data-testid="stDateInput"] input {{
  background:#FFFDF7!important; color:{GOLD}!important; -webkit-text-fill-color:{GOLD}!important;
  border:1px solid {BROWN}!important; border-radius:5px!important; font-weight:650!important;
}}
[data-baseweb="popover"], [data-baseweb="calendar"] {{ background:#FFFDF7!important; color:{BROWN}!important; }}
[data-baseweb="calendar"] [role="gridcell"] {{ color:{GOLD}!important; }}
[data-testid="stCaptionContainer"] {{ color:{BROWN}!important; }}
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
.metric-card {{ position:relative; display:flex; flex-direction:column; background:linear-gradient(140deg,rgba(255,253,247,.95),rgba(255,248,214,.94)); border:1.5px solid rgba(71,47,38,.27); border-radius:8px; padding:17px 19px; min-height:148px; height:100%; box-shadow:0 7px 19px rgba(71,47,38,.08); transition:transform .2s,box-shadow .2s; }}
.metric-card:hover {{ transform:translateY(-3px); box-shadow:0 13px 25px rgba(71,47,38,.13); }}
.metric-label {{ color:{MUTED}; font-size:.75rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; }}
.metric-value {{ color:{BROWN}; font:800 clamp(1.15rem,1.65vw,1.75rem) Manrope,sans-serif; margin:12px 0 9px; line-height:1.28; overflow-wrap:anywhere; }}
.metric-note {{ color:{MUTED}; font-size:.84rem; line-height:1.45; margin-top:auto; }}
.section-head {{ display:flex; align-items:center; gap:10px; margin:11px 0 6px; }}
.section-head.compact {{ margin-top:2px; }}
.section-head span {{ display:inline-flex; align-items:center; justify-content:center; min-width:38px; height:34px; background:{BASELINE}; border:1.5px solid rgba(71,47,38,.3); border-radius:5px; font-weight:850; color:{BROWN}; }}
.section-head .section-number {{ display:inline-flex; align-items:center; justify-content:center; min-width:38px; height:34px; background:{BASELINE}; border:1.5px solid rgba(71,47,38,.3); border-radius:5px; font-size:1.08rem; }}
.date-highlight {{ color:{GOLD}!important; font-weight:700; }}
.section-head h3 {{ margin:0; font-size:1.08rem; color:{BROWN}; }}
.panel {{ border:1px solid rgba(71,47,38,.22); border-radius:7px; padding:15px 17px; background:rgba(255,253,247,.68); color:{BROWN}; height:100%; }}
.business-note {{ background:linear-gradient(112deg,rgba(255,242,167,.75),rgba(190,222,255,.43)); border:1.5px solid rgba(71,47,38,.25); border-left:5px solid {MAROON}; border-radius:7px; padding:18px; color:{BROWN}; line-height:1.65; }}
.dashboard-title {{ margin:4px 0 10px; padding:15px 20px; border:1.5px solid rgba(71,47,38,.24); border-radius:7px; background:rgba(255,253,247,.88); box-shadow:0 7px 19px rgba(71,47,38,.08); font-size:clamp(1.6rem,2.4vw,2.2rem); }}
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
        for candidate in path.parent.glob(f"{file_stem} (*){extension}")
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


def display_label(value):
    return str(value).replace("_", " ")


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
    return f"<span style='display:inline-block;border:1.5px solid {col};padding:7px 11px;border-radius:4px;color:{col};font-weight:850;background:rgba(255,253,247,.7)'>{display_label(label)}</span>"


# Read project CSV artifacts.
shap_global = read_csv("xai_shap_feature_importance.csv")
shap_val = read_csv("xai_shap_values_validation.csv")
future = read_csv("xai_proyeksi_future_5d.csv")
analysis_metrics = read_csv("model_evaluation_metrics.csv")
test_pred = read_csv("test_ews_predictions.csv")
test_detail = read_csv("prediksi_target_volatilitas_y_test.csv")
validation_pred = read_csv("validation_predictions.csv")  # optional: actual vs CatBoost vs naive baseline
training_market = read_csv("raw/dataset peserta.csv")

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


st.markdown(
    "<h1 class='dashboard-title'> Volatility Intelligence</h1>",
    unsafe_allow_html=True,
)

base_source = test_pred if test_pred is not None and not test_pred.empty else test_detail
if base_source is not None and not base_source.empty:
    date_column = "Date" if "Date" in base_source.columns else "Tanggal"
    date_min, date_max = base_source[date_column].min().date(), base_source[date_column].max().date()
    selected_range = st.date_input(
        "Rentang tanggal",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )
else:
    selected_range = None

# Prepare globally filtered test rows for the dashboard.
filtered_test = select_test_date_range(test_pred, selected_range) if test_pred is not None else None
filtered_detail = select_test_date_range(test_detail, selected_range) if test_detail is not None else None

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

    kpis = st.columns(3, gap="medium")
    card_data = [
        ("LEVEL IHSG TERKINI", f"{ihsg_value:,.2f}" if pd.notna(ihsg_value) else "—", f"Perubahan harian: {pct(ihsg_change)}" if pd.notna(ihsg_change) else "Perubahan harian belum tersedia"),
        ("PROYEKSI VOLATILITAS 5 HARI", pct(forecast_value), f"Tanggal sinyal EWS: {pd.Timestamp(date_val).strftime('%d %b %Y') if pd.notna(date_val) else '—'}"),
        ("STATUS EWS", risk_value, f"Tanggal sinyal: {pd.Timestamp(date_val).strftime('%d %b %Y') if pd.notna(date_val) else '—'}"),
    ]
    for col, (label, value, note) in zip(kpis, card_data):
        with col:
            risk_style = f"color:{risk_color(value)};font-size:clamp(.98rem,1.3vw,1.45rem)" if label == "STATUS EWS" else ""
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value' style='{risk_style}'>{display_label(value)}</div><div class='metric-note'>{note}</div></div>",
                unsafe_allow_html=True,
            )

    left, right = st.columns([0.9, 1.6], gap="medium")
    with left:
        st.markdown("<div class='section-head'><span class='section-number'>01</span><h3>Risk Gauge & Ringkasan Sinyal</h3></div>", unsafe_allow_html=True)
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
            recent_dates = chart["Date"].dropna().sort_values().tail(5)
            if not recent_dates.empty:
                fig.add_vrect(
                    x0=recent_dates.iloc[0] - pd.Timedelta(hours=12),
                    x1=recent_dates.iloc[-1] + pd.Timedelta(hours=12),
                    fillcolor="rgba(255,165,0,.19)",
                    line_width=1,
                    line_color=ORANGE,
                    annotation_text="5 observasi terakhir",
                    annotation_position="top left",
                    layer="below",
                )
                recent_mask = chart["Date"].isin(recent_dates)
                fig.add_trace(go.Scatter(
                    x=chart.loc[recent_mask, "Date"],
                    y=chart.loc[recent_mask, "CatBoost_Pred_Vol_5d"] * 100,
                    mode="markers",
                    name="Rentang 5 observasi terakhir",
                    marker=dict(color=ORANGE, size=8, line=dict(color=PANEL, width=1.5)),
                    hovertemplate="Jendela terbaru · %{x|%d %b %Y}<br>Prediksi: %{y:.3f}%<extra></extra>",
                ))
            # Optional baseline series is plotted only when genuinely present in the provided CSV.
            bcol = next((c for c in ["Baseline_Naif_Pred", "Baseline_Pred", "Baseline_Vol_5d"] if c in chart.columns), None)
            if bcol:
                fig.add_trace(go.Scatter(x=chart["Date"], y=chart[bcol] * 100, mode="lines", name="Baseline naif", line=dict(color=BASELINE, width=2.6, dash="dot")))
            fig.update_layout(xaxis_title="Tanggal", yaxis_title="Prediksi volatilitas (%)", hovermode="x unified")
            plot_theme(fig, 340, plot_bg="rgba(190,222,255,.14)")
            fig.update_xaxes(tickfont=dict(color=GOLD), title_font=dict(color=GOLD))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<span class='legend-pill legend-red'>Marun: prediksi CatBoost</span><span class='legend-pill' style='background:#FFE1B3'>Oranye: lima observasi terbaru</span><span class='legend-pill legend-yellow'>Kuning: baseline (jika tersedia)</span>", unsafe_allow_html=True)
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
    if validation_metrics:
        baseline_metrics, catboost_metrics = validation_metrics
        metric_cards = st.columns(3, gap="medium")
        for col, (label, key, precision, suffix) in zip(
            metric_cards,
            [
                ("RMSE", "RMSE", 6, ""),
                ("MAE", "MAE", 6, ""),
                ("MAPE", "MAPE (%)", 2, "%"),
            ],
        ):
            baseline_value = float(baseline_metrics[key])
            catboost_value = float(catboost_metrics[key])
            if label == "MAPE":
                difference = baseline_value - catboost_value
                direction = "Turun" if difference >= 0 else "Naik"
                change = f"{direction} {abs(difference):.2f} poin persentase"
            else:
                reduction = metric_reduction_percent(
                    baseline_metrics, catboost_metrics, key, f"{label}_Reduction_Pct"
                )
                direction = "Turun" if reduction >= 0 else "Naik"
                change = f"{direction} {abs(reduction):.2f}% dari baseline"
            with col:
                st.markdown(
                    f"<div class='metric-card'><div class='metric-label'>{label} · VALIDASI</div>"
                    f"<div class='metric-value' style='font-size:1.35rem'>CatBoost {catboost_value:.{precision}f}{suffix}</div>"
                    f"<div class='metric-note'>Baseline {baseline_value:.{precision}f}{suffix}<br>{change}</div></div>",
                    unsafe_allow_html=True,
                )
        metrics_source_note = (
            "Metrik dihitung dari seri validasi yang sama dengan grafik."
            if metrics_calculated_from_predictions
            else "Metrik berasal dari ekspor notebook untuk periode validasi."
        )
        validation_count = len(validation_pred) if validation_pred is not None else 0
        test_count = len(test_pred) if test_pred is not None else 0
        future_count = len(future) if future is not None else 0
        st.caption(
            f"{metrics_source_note} Cakupan: {validation_count:,} observasi validasi (2022–2024) · "
            f"{test_count:,} observasi test EWS (2025–2026) · {future_count} tanggal proyeksi."
        )
    else:
        st.info("Metrik validasi belum tersedia. Jalankan notebook analisis agar metrik dapat ditampilkan.")

# ============================= SHAP & PROJECTION =============================
if "Explainable AI & Projection" in dashboard_sections:
    selected_xai_row = None
    st.markdown("<div class='section-head'><span>05</span><h3>Explainable AI · SHAP</h3></div>", unsafe_allow_html=True)
    st.caption("Ringkasan tiga fitur global teratas dan kontribusi SHAP lokal untuk tanggal historis atau proyeksi yang dipilih.")

    if shap_global is None:
        st.error("File xai_shap_feature_importance.csv tidak ditemukan di folder data/.")
        st.stop()

    glob = shap_global.sort_values("Rank").copy()
    top3 = glob.head(3)
    st.markdown("<div class='section-head compact'><span>05a</span><h3>Tiga Fitur dengan Mean Absolute SHAP Tertinggi</h3></div>", unsafe_allow_html=True)
    top_cols = st.columns(3, gap="medium")
    for col, (_, row) in zip(top_cols, top3.iterrows()):
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>RANK {int(row['Rank'])}</div><div class='metric-value' style='font-size:1.28rem'>{display_label(row['Feature'])}</div><div class='metric-note'>Mean |SHAP|: {float(row['Mean_Abs_SHAP']):.5f}<br>Importance relatif: {float(row['Percentage_Importance (%)']):.2f}%</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'><span>05b</span><h3>SHAP Lokal · Pilih Tanggal</h3></div>", unsafe_allow_html=True)
    options = []
    if shap_val is not None and "Date" in shap_val.columns:
        options.extend([(d, "Validation") for d in shap_val["Date"].dropna().dt.date.unique()])
    if future is not None and "Tanggal" in future.columns:
        options.extend([(d, "Proyeksi") for d in future["Tanggal"].dropna().dt.date.unique()])
    options = sorted(set(options), key=lambda x: (x[0], x[1]))

    if options:
        default_idx = len(options) - 1
        if filtered_detail is not None and not filtered_detail.empty:
            signal_day = pd.Timestamp(filtered_detail.iloc[-1]["Tanggal"]).date()
            matching_options = [
                index for index, option in enumerate(options) if option[0] == signal_day
            ]
            if matching_options:
                default_idx = next(
                    (
                        index for index in matching_options
                        if options[index][1] == "Proyeksi"
                    ),
                    matching_options[-1],
                )
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
            selected_xai_row = shap_row
            shap_cols = [c for c in shap_row.index if c.startswith("SHAP_") and pd.notna(shap_row[c])]
            local = pd.DataFrame({"Feature": [display_label(c.removeprefix("SHAP_")) for c in shap_cols], "SHAP": [float(shap_row[c]) for c in shap_cols]})
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
                display_table = local.sort_values("Abs_SHAP", ascending=False).head(5).rename(
                    columns=lambda column: display_label(column)
                )
                st.dataframe(style_table(display_table), use_container_width=True, hide_index=True, height=260)
                st.download_button("⬇Unduh kontribusi tanggal ini", local.to_csv(index=False).encode("utf-8-sig"), f"local_shap_{chosen_date}.csv", "text/csv")
    else:
        st.warning("Tidak ditemukan tanggal SHAP dalam file validasi maupun proyeksi.")

# ============================= TRAINING-BASED PORTFOLIO SIMULATION =============================
if filtered_detail is not None and not filtered_detail.empty:
    st.markdown("<div class='section-head'><span>06</span><h3>Simulasi Eksposur & Rekomendasi EWS/XAI</h3></div>", unsafe_allow_html=True)
    latest = filtered_detail.iloc[-1]
    signal = str(latest.get("Status_Risiko", "Tidak tersedia"))
    forecast_vol = pd.to_numeric(latest.get("Prediksi_Target_Volatilitas_Y"), errors="coerce")
    selected_day = latest.get("Tanggal", pd.NaT)

    if "HIGH" in signal.upper() or "DARURAT" in signal.upper() or "BAHAYA" in signal.upper():
        suggested_hedge = 100
        recommendation = "Sinyal tinggi: tinjau penurunan eksposur ekuitas, kebutuhan lindung nilai, dan batas likuiditas bersama komite risiko."
    elif "MODERATE" in signal.upper() or "WASPADA" in signal.upper():
        suggested_hedge = 20
        recommendation = "Sinyal moderat: evaluasi hedge parsial, batas stop-loss, dan alokasi defensif; tinjau kembali saat sinyal berubah."
    else:
        suggested_hedge = 0
        recommendation = "Sinyal rendah: pertahankan pemantauan berkala dan evaluasi ulang bila proyeksi volatilitas atau pendorong SHAP meningkat."

    training_stats = None
    if training_market is not None and {"Date", "IHSG", "Target_Volatilitas_Y"}.issubset(training_market.columns):
        train = training_market.copy()
        train["IHSG"] = pd.to_numeric(train["IHSG"], errors="coerce")
        train["Target_Volatilitas_Y"] = pd.to_numeric(train["Target_Volatilitas_Y"], errors="coerce")
        train = train[
            train["Date"].notna()
            & (train["Date"] >= pd.Timestamp("2010-02-03"))
            & (train["Date"] <= pd.Timestamp("2021-12-31"))
            & train["IHSG"].gt(0)
            & train["Target_Volatilitas_Y"].notna()
        ].sort_values("Date")
        # Match the notebook's chronological training split and five-observation purge.
        train = train.iloc[:-5].copy()
        train["Forward_5d_Return"] = train["IHSG"].shift(-5).div(train["IHSG"]).sub(1)
        losses = (-train["Forward_5d_Return"].dropna()).clip(lower=0)
        if not losses.empty and train["Target_Volatilitas_Y"].gt(0).any():
            training_stats = {
                "count": int(losses.count()),
                "start": train["Date"].min(),
                "end": train["Date"].max(),
                "mean_target_vol": float(train["Target_Volatilitas_Y"].mean()),
                "losses": losses,
            }

    if training_stats is None:
        st.warning("Dataset training berlabel belum tersedia; simulasi berbasis training tidak dapat dihitung.")
    elif pd.isna(forecast_vol) or forecast_vol < 0:
        st.warning("Prediksi volatilitas tidak tersedia atau tidak valid untuk menghitung simulasi.")
    else:
        losses = training_stats["losses"]
        input_col, result_col = st.columns([.9, 1.5], gap="large")
        with input_col:
            st.markdown("<h4>Parameter portofolio</h4>", unsafe_allow_html=True)
            aum_trillion = st.slider("AUM (Rp triliun)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
            equity_pct = st.slider("Eksposur ekuitas (%)", min_value=0, max_value=100, value=100, step=5)
            confidence = st.select_slider("Tingkat keyakinan VaR", options=[90, 95, 99], value=99, format_func=lambda value: f"{value}%")
            hedge_pct = st.slider("Porsi eksposur yang di-hedge (%)", min_value=0, max_value=100, value=suggested_hedge, step=5)

        base_var_rate = float(losses.quantile(confidence / 100, interpolation="higher"))
        base_es_rate = float(losses[losses >= base_var_rate].mean()) if (losses >= base_var_rate).any() else base_var_rate
        vol_scale = float(forecast_vol) / training_stats["mean_target_vol"]
        scaled_var_rate = base_var_rate * vol_scale
        scaled_es_rate = base_es_rate * vol_scale
        aum_idr = aum_trillion * 1_000_000_000_000
        equity_exposure = aum_idr * equity_pct / 100
        hedged_exposure = equity_exposure * hedge_pct / 100
        var_no_hedge = equity_exposure * scaled_var_rate
        var_after_hedge = var_no_hedge * (1 - hedge_pct / 100)
        es_amount = equity_exposure * scaled_es_rate

        with result_col:
            st.markdown("<h4>Estimasi eksposur portofolio</h4>", unsafe_allow_html=True)
            result_rows = [
                [
                    ("EKUITAS TERPAPAR", f"Rp {equity_exposure / 1e9:,.0f} M", f"{equity_pct}% dari AUM"),
                    (f"VaR {confidence}% · 5 HARI", f"Rp {var_no_hedge / 1e9:,.1f} M", "Sebelum hedge · training-scaled"),
                ],
                [
                    ("VaR SETELAH HEDGE", f"Rp {var_after_hedge / 1e9:,.1f} M", f"Hedge {hedge_pct}% · simulasi proporsional"),
                    ("VOLATILITAS PREDIKSI 5 HARI", f"{forecast_vol:.3%}", "Proyeksi volatilitas model"),
                ],
            ]
            for result_data in result_rows:
                result_cards = st.columns(2, gap="small")
                for col, (label, value, note) in zip(result_cards, result_data):
                    with col:
                        st.markdown(
                            f"<div class='metric-card'><div class='metric-label'>{label}</div>"
                            f"<div class='metric-value' style='font-size:1.25rem'>{value}</div>"
                            f"<div class='metric-note'>{note}</div></div>",
                            unsafe_allow_html=True,
                        )
            st.markdown(
                f"<div class='panel' style='margin-top:10px'><b>Estimasi expected shortfall {confidence}% · 5 hari</b>"
                f"<span style='float:right;font-weight:800'>Rp {es_amount / 1e9:,.1f} M</span><br>"
                f"<span class='small-muted'>Skenario ekor kerugian setelah skala volatilitas model; bukan estimasi harga instrumen hedge.</span></div>",
                unsafe_allow_html=True,
            )

        xai_row = selected_xai_row
        if xai_row is None and future is not None and not future.empty:
            xai_row = future.iloc[-1]
        positive_drivers, negative_drivers = [], []
        xai_date = "tidak tersedia"
        if xai_row is not None:
            xai_date_value = xai_row.get("Tanggal", xai_row.get("Date", pd.NaT))
            if pd.notna(xai_date_value):
                xai_date = pd.Timestamp(xai_date_value).strftime("%d %b %Y")
            local_values = [
                (display_label(column.removeprefix("SHAP_")), float(xai_row[column]))
                for column in xai_row.index
                if column.startswith("SHAP_") and pd.notna(xai_row[column])
            ]
            strongest = sorted(local_values, key=lambda item: abs(item[1]), reverse=True)[:5]
            positive_drivers = [f"{name} ({value:+.4f})" for name, value in strongest if value > 0][:3]
            negative_drivers = [f"{name} ({value:+.4f})" for name, value in strongest if value < 0][:3]

        driver_up = ", ".join(positive_drivers) if positive_drivers else "Tidak ada kontribusi positif terkuat yang tersedia."
        driver_down = ", ".join(negative_drivers) if negative_drivers else "Tidak ada kontribusi negatif terkuat yang tersedia."
        xai_action = (
            f"Fokuskan peninjauan pada pendorong model {positive_drivers[0]}."
            if positive_drivers
            else "Gunakan kontribusi SHAP sebagai konteks pemantauan, tanpa pendorong positif dominan yang teridentifikasi."
        )
        st.markdown(
            f"<div class='business-note'><b>{badge_for_risk(signal)} · Rekomendasi untuk ditinjau</b><br><br>{recommendation}"
            f"<br><b>Fokus peninjauan berbasis XAI:</b> {xai_action}"
            f"<br><br><b>Pendorong model menurut SHAP ({xai_date}):</b> {driver_up}"
            f"<br><b>Faktor penahan prediksi:</b> {driver_down}"
            f"<br><br><small>SHAP menjelaskan kontribusi terhadap keluaran model, bukan sebab-akibat ekonomi. VaR/ES memakai return IHSG forward 5 hari pada subset training notebook "
            f"({training_stats['start']:%d %b %Y}–{training_stats['end']:%d %b %Y}; {training_stats['count']:,} observasi) yang diskalakan dengan rasio proyeksi volatilitas terhadap rata-rata target training ({vol_scale:.2f}×)."
            " Dampak hedge dihitung proporsional secara hipotetis dan belum mencakup biaya, basis risk, maupun payoff instrumen aktual.</small></div>",
            unsafe_allow_html=True,
        )

        report = pd.DataFrame([{
            "Tanggal_Sinyal": pd.Timestamp(selected_day).strftime("%Y-%m-%d"),
            "Tanggal_XAI": xai_date,
            "Sinyal_EWS": signal,
            "Prediksi_Volatilitas_5d": float(forecast_vol),
            "Periode_Training": f"{training_stats['start']:%Y-%m-%d} s/d {training_stats['end']:%Y-%m-%d}",
            "Observasi_Return_5d_Training": training_stats["count"],
            "VaR_Rate_Training": base_var_rate,
            "Skala_Volatilitas_Model": vol_scale,
            "Tingkat_Keyakinan_Persen": confidence,
            "AUM_Rp": aum_idr,
            "Eksposur_Ekuitas_Persen": equity_pct,
            "Eksposur_Ekuitas_Rp": equity_exposure,
            "Porsi_Hedge_Persen": hedge_pct,
            "Nilai_Eksposur_Dihedge_Rp": hedged_exposure,
            "VaR_Sebelum_Hedge_Rp": var_no_hedge,
            "VaR_Setelah_Hedge_Rp": var_after_hedge,
            "Expected_Shortfall_Rp": es_amount,
            "Pendorong_SHAP": "; ".join(positive_drivers),
            "Faktor_Penahan_SHAP": "; ".join(negative_drivers),
            "Asumsi": "Historical simulation return IHSG forward 5 hari pada subset training, diskalakan dengan rasio proyeksi vol terhadap rata-rata target training; dampak hedge proporsional hipotetis.",
        }])
        st.download_button("⬇Unduh ringkasan simulasi (CSV)", report.to_csv(index=False).encode("utf-8-sig"), "investion_hedging_simulation.csv", "text/csv")
else:
    st.warning("Data EWS belum tersedia untuk menghitung simulasi portofolio.")

st.divider()
st.caption("MABA 27 · inception")
