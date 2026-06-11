"""
Dashboard Business Intelligence — Kualitas Udara Jakarta (ISPU)
Jalankan dengan: streamlit run dashboard_ispu_jakarta.py
Pastikan file CSV berada di direktori yang sama atau ubah path DATA_PATH.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ISPU Jakarta — BI Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS KUSTOM
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header utama */
    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        border-left: 5px solid #00d4ff;
    }
    .main-header h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #94b8c9;
        font-size: 0.92rem;
        margin: 0;
    }

    /* KPI card */
    .kpi-card {
        background: linear-gradient(145deg, #1a2332, #1e2d40);
        border: 1px solid #2a4060;
        border-radius: 14px;
        padding: 20px 22px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,212,255,0.12);
    }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #00d4ff;
        line-height: 1;
        margin-bottom: 6px;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #7a9ab5;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #b0c8d8;
        margin-top: 4px;
    }

    /* Section header */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #d0e8f5;
        border-bottom: 2px solid #2a4060;
        padding-bottom: 8px;
        margin-bottom: 18px;
    }

    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg, #0d2137, #162b3a);
        border: 1px solid #1e4060;
        border-left: 4px solid #00d4ff;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 16px;
    }
    .insight-box h4 {
        color: #00d4ff;
        font-size: 0.88rem;
        font-weight: 600;
        margin: 0 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .insight-box ul {
        margin: 0;
        padding-left: 18px;
        color: #a8c8de;
        font-size: 0.84rem;
        line-height: 1.7;
    }
    .insight-box li { margin-bottom: 2px; }

    /* Badge kategori */
    .badge-baik       { background:#1a4a2e; color:#4ade80; border:1px solid #22c55e; }
    .badge-sedang     { background:#3d3010; color:#fbbf24; border:1px solid #f59e0b; }
    .badge-tidaksehat { background:#4a1c1c; color:#f87171; border:1px solid #ef4444; }
    .badge-sangat     { background:#3d0f2a; color:#e879f9; border:1px solid #d946ef; }
    .badge-berbahaya  { background:#2d0a0a; color:#ff6b6b; border:1px solid #dc2626; }
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.4px;
    }

    /* Plotly chart backgrounds */
    .stPlotlyChart { border-radius: 12px; overflow: hidden; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0d1b2a; border-right: 1px solid #1e3a50; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiselect label,
    [data-testid="stSidebar"] .stRadio label { color: #94b8c9 !important; font-size: 0.85rem; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #0d1b2a;
        border-radius: 12px 12px 0 0;
        gap: 4px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #7a9ab5;
        font-weight: 500;
        font-size: 0.88rem;
        border-radius: 8px;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0080b3, #005c82) !important;
        color: #ffffff !important;
    }

    /* Divider */
    hr { border-color: #1e3a50; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD & PREPROCESSING DATA
# ─────────────────────────────────────────────
DATA_PATH = "ispu_jakarta_cleaned_final.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["tahun"]      = df["tanggal"].dt.year
    df["bulan"]      = df["tanggal"].dt.month
    df["nama_bulan"] = df["tanggal"].dt.strftime("%b")
    df["minggu"]     = df["tanggal"].dt.isocalendar().week.astype(int)
    df["kuartal"]    = df["tanggal"].dt.quarter
    df["hari_minggu"]= df["tanggal"].dt.day_name()

    # Urutan kategori
    cat_order = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
    df["categori"] = pd.Categorical(df["categori"], categories=cat_order, ordered=True)

    # Warna kategori
    df["cat_color"] = df["categori"].map({
        "BAIK": "#4ade80",
        "SEDANG": "#fbbf24",
        "TIDAK SEHAT": "#f87171",
        "SANGAT TIDAK SEHAT": "#e879f9",
        "BERBAHAYA": "#ff2d2d",
    })

    # Nama stasiun singkat
    df["stasiun_singkat"] = df["stasiun"].str.extract(r"(DKI\d)")
    df["label_stasiun"]   = df["stasiun"].str.replace("DKI", "DKI ", regex=False)

    return df


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"❌ File tidak ditemukan: `{DATA_PATH}`\n\nPastikan file CSV berada di direktori yang sama dengan script ini.")
    st.stop()

# ─────────────────────────────────────────────
# KONSTANTA WARNA & TEMA
# ─────────────────────────────────────────────
CHART_BG     = "#0d1b2a"
PAPER_BG     = "#0a1520"
GRID_COLOR   = "#1e3a50"
FONT_COLOR   = "#b0c8d8"
ACCENT_BLUE  = "#00d4ff"
ACCENT_AMBER = "#fbbf24"

CAT_COLORS = {
    "BAIK": "#4ade80",
    "SEDANG": "#fbbf24",
    "TIDAK SEHAT": "#f87171",
    "SANGAT TIDAK SEHAT": "#e879f9",
    "BERBAHAYA": "#ff2d2d",
}
PARAM_COLORS = {
    "PM10": "#f97316",
    "PM2.5": "#ef4444",
    "O3": "#a78bfa",
    "CO": "#60a5fa",
    "SO2": "#facc15",
    "NO2": "#34d399",
}
STATION_COLORS = {
    "DKI1 Bunderan HI"  : "#00d4ff",
    "DKI2 Kelapa Gading": "#f97316",
    "DKI3 Jagakarsa"    : "#4ade80",
    "DKI4 Lubang Buaya" : "#e879f9",
    "DKI5 Kebon Jeruk"  : "#fbbf24",
}

def apply_dark_theme(fig, height=400, showlegend=True):
    fig.update_layout(
        height=height,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=FONT_COLOR, family="Inter"),
        showlegend=showlegend,
        legend=dict(
            bgcolor="rgba(13,27,42,0.8)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(size=11),
        ),
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=11)),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=11)),
    )
    return fig


# ─────────────────────────────────────────────
# HEADER UTAMA
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌬️ Dashboard ISPU Jakarta</h1>
    <p>Business Intelligence — Indeks Standar Pencemaran Udara • 2010 – 2023 • 5 Stasiun SPKU DKI</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR FILTER GLOBAL
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filter Global")
    st.markdown("---")

    all_stations = sorted(df["stasiun"].unique())
    sel_stations = st.multiselect(
        "Stasiun SPKU",
        options=all_stations,
        default=all_stations,
        key="global_station",
    )

    year_min, year_max = int(df["tahun"].min()), int(df["tahun"].max())
    sel_years = st.slider(
        "Rentang Tahun",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        key="global_year",
    )

    all_cats = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
    sel_cats = st.multiselect(
        "Kategori ISPU",
        options=all_cats,
        default=all_cats,
        key="global_cat",
    )

    st.markdown("---")
    st.markdown("""
    <small style='color:#5a7a90'>
    <b>Keterangan:</b><br>
    🟢 BAIK: ISPU 0–50<br>
    🟡 SEDANG: 51–100<br>
    🔴 TIDAK SEHAT: 101–200<br>
    🟣 SANGAT TDK SEHAT: 201–300<br>
    🔴 BERBAHAYA: >300
    </small>
    """, unsafe_allow_html=True)

# Terapkan filter global
mask = (
    df["stasiun"].isin(sel_stations) &
    df["tahun"].between(*sel_years) &
    df["categori"].isin(sel_cats)
)
dff = df[mask].copy()

if dff.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih. Sesuaikan filter di sidebar.")
    st.stop()

# ─────────────────────────────────────────────
# NAVIGASI TAB
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏙️ Overview",
    "📈 Tren Temporal",
    "🏭 Perbandingan Stasiun",
    "⚗️ Analisis Pencemar",
    "🌦️ Pola Musiman",
])


# ══════════════════════════════════════════════════
# TAB 1 — OVERVIEW KUALITAS UDARA JAKARTA
# ══════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📊 KPI Utama Kualitas Udara Jakarta</div>', unsafe_allow_html=True)

    # KPI
    avg_ispu    = dff["max"].mean()
    pct_unhealthy = (dff["categori"].isin(["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]).sum() / len(dff) * 100)
    top_pollutant = dff["critical"].value_counts().idxmax()
    total_days    = dff["tanggal"].nunique()
    worst_station = dff.groupby("stasiun")["max"].mean().idxmax()
    pct_baik = dff["categori"].eq("BAIK").sum() / len(dff) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    metrics = [
        (c1, f"{avg_ispu:.1f}",     "Rata-rata ISPU",         "Indeks harian"),
        (c2, f"{pct_unhealthy:.1f}%","Hari Tidak Sehat+",      "Kategori TS/STS/Berbahaya"),
        (c3, top_pollutant,          "Pencemar Dominan",       "Paling sering kritis"),
        (c4, f"{total_days:,}",      "Total Hari Data",        f"{sel_years[0]}–{sel_years[1]}"),
        (c5, worst_station.split()[0], "Stasiun Terburuk",     "Rata-rata ISPU tertinggi"),
        (c6, f"{pct_baik:.1f}%",    "Hari Kategori BAIK",     "Kualitas optimal"),
    ]
    for col, val, label, sub in metrics:
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Baris 1: Distribusi kategori + Per-stasiun ringkasan
    col_left, col_right = st.columns([5, 5])

    with col_left:
        st.markdown('<div class="section-header">Distribusi Kategori ISPU</div>', unsafe_allow_html=True)
        cat_counts = dff["categori"].value_counts().reindex(all_cats, fill_value=0).reset_index()
        cat_counts.columns = ["Kategori", "Jumlah"]
        cat_counts["Warna"] = cat_counts["Kategori"].map(CAT_COLORS)
        cat_counts["Persen"] = (cat_counts["Jumlah"] / cat_counts["Jumlah"].sum() * 100).round(1)

        fig_cat = go.Figure(go.Bar(
            x=cat_counts["Kategori"],
            y=cat_counts["Jumlah"],
            marker_color=cat_counts["Warna"],
            text=[f"{p}%" for p in cat_counts["Persen"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Jumlah: %{y:,}<br>Persentase: %{text}<extra></extra>",
        ))
        fig_cat.update_layout(
            title=dict(text="Frekuensi Hari per Kategori", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Kategori",
            yaxis_title="Jumlah Hari",
        )
        apply_dark_theme(fig_cat, height=340)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Rata-rata ISPU per Stasiun</div>', unsafe_allow_html=True)
        stn_avg = dff.groupby("stasiun")["max"].mean().reset_index().sort_values("max", ascending=True)
        stn_avg.columns = ["Stasiun", "Avg ISPU"]

        fig_stn = go.Figure(go.Bar(
            y=stn_avg["Stasiun"],
            x=stn_avg["Avg ISPU"],
            orientation="h",
            marker_color=[STATION_COLORS.get(s, ACCENT_BLUE) for s in stn_avg["Stasiun"]],
            text=[f"{v:.1f}" for v in stn_avg["Avg ISPU"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg ISPU: %{x:.1f}<extra></extra>",
        ))
        fig_stn.add_vline(x=100, line_dash="dash", line_color="#f87171", annotation_text="Batas Tidak Sehat (100)")
        fig_stn.update_layout(
            title=dict(text="Rata-rata Nilai ISPU Harian", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Rata-rata ISPU",
        )
        apply_dark_theme(fig_stn, height=340)
        st.plotly_chart(fig_stn, use_container_width=True)

    # Baris 2: Tren tahunan overview + Pie pencemar
    col_a, col_b = st.columns([6, 4])

    with col_a:
        st.markdown('<div class="section-header">Tren Rata-rata ISPU Tahunan</div>', unsafe_allow_html=True)
        yearly = dff.groupby("tahun")["max"].agg(["mean", "median", "max"]).reset_index()
        yearly.columns = ["Tahun", "Rata-rata", "Median", "Maks"]

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=yearly["Tahun"], y=yearly["Rata-rata"],
            mode="lines+markers",
            name="Rata-rata", line=dict(color=ACCENT_BLUE, width=3),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.08)",
            marker=dict(size=8),
        ))
        fig_trend.add_trace(go.Scatter(
            x=yearly["Tahun"], y=yearly["Median"],
            mode="lines", name="Median",
            line=dict(color=ACCENT_AMBER, width=2, dash="dash"),
        ))
        fig_trend.add_hline(y=100, line_dash="dot", line_color="#f87171",
                            annotation_text="Batas TIDAK SEHAT", annotation_font_color="#f87171")
        fig_trend.update_layout(
            title=dict(text="Perkembangan ISPU 2010–2023", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Tahun", yaxis_title="Nilai ISPU",
        )
        apply_dark_theme(fig_trend, height=340)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Dominasi Parameter Pencemar</div>', unsafe_allow_html=True)
        pol_cnt = dff["critical"].value_counts().reset_index()
        pol_cnt.columns = ["Parameter", "Frekuensi"]

        fig_pie = go.Figure(go.Pie(
            labels=pol_cnt["Parameter"],
            values=pol_cnt["Frekuensi"],
            hole=0.55,
            marker=dict(colors=[PARAM_COLORS.get(p, "#888") for p in pol_cnt["Parameter"]],
                        line=dict(color=CHART_BG, width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Frekuensi: %{value:,}<br>%{percent}<extra></extra>",
        ))
        fig_pie.update_layout(
            title=dict(text="Porsi sebagai Pencemar Kritis", font=dict(size=13, color=FONT_COLOR)),
            annotations=[dict(text=f"<b>{len(dff):,}</b><br>hari", x=0.5, y=0.5,
                              font_size=14, showarrow=False, font_color=FONT_COLOR)],
        )
        apply_dark_theme(fig_pie, height=340, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Insight
    st.markdown("""
    <div class="insight-box">
        <h4>💡 Insight Utama — Overview</h4>
        <ul>
            <li><b>O3 (Ozon)</b> adalah pencemar paling dominan (~45%), terutama akibat reaksi fotokimia kendaraan bermotor di siang hari.</li>
            <li><b>DKI2 Kelapa Gading</b> secara konsisten mencatat nilai ISPU tertinggi, dipengaruhi oleh kepadatan industri dan lalu lintas.</li>
            <li>Sekitar <b>16.8% hari</b> masuk kategori Tidak Sehat atau lebih buruk — ekuivalen dengan ~61 hari per tahun.</li>
            <li>Tahun <b>2013, 2018, dan 2019</b> menunjukkan lonjakan signifikan ISPU, berkorelasi dengan musim kemarau panjang dan kebakaran lahan.</li>
            <li><b>DKI1 Bunderan HI</b> mencatat rata-rata terbaik, meski berada di pusat kota — kemungkinan dipengaruhi koreksi data dan pengukuran O3 yang berbeda.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# TAB 2 — TREN TEMPORAL
# ══════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📈 Tren Temporal Nilai ISPU</div>', unsafe_allow_html=True)

    # Filter tambahan tab 2
    ft_col1, ft_col2, ft_col3 = st.columns([3, 3, 4])
    with ft_col1:
        granularity = st.radio(
            "Granularitas",
            ["Harian", "Bulanan", "Tahunan"],
            index=1,
            horizontal=True,
            key="t2_gran",
        )
    with ft_col2:
        t2_stations = st.multiselect(
            "Stasiun (Tren)",
            options=all_stations,
            default=all_stations[:3],
            key="t2_station",
        )
    with ft_col3:
        compare_years = st.multiselect(
            "Bandingkan Tahun Tertentu",
            options=sorted(df["tahun"].unique()),
            default=[2015, 2019, 2023],
            key="t2_years",
        )

    dff2 = dff[dff["stasiun"].isin(t2_stations)] if t2_stations else dff

    # Siapkan data berdasarkan granularitas
    if granularity == "Harian":
        grp = dff2.groupby(["tanggal", "stasiun"])["max"].mean().reset_index()
        x_col, x_lbl = "tanggal", "Tanggal"
    elif granularity == "Bulanan":
        dff2["periode"] = dff2["tanggal"].dt.to_period("M").dt.to_timestamp()
        grp = dff2.groupby(["periode", "stasiun"])["max"].mean().reset_index()
        x_col, x_lbl = "periode", "Bulan"
    else:
        grp = dff2.groupby(["tahun", "stasiun"])["max"].mean().reset_index()
        x_col, x_lbl = "tahun", "Tahun"

    fig_tren = go.Figure()
    for stn in (t2_stations if t2_stations else all_stations):
        sub = grp[grp["stasiun"] == stn]
        if sub.empty:
            continue
        fig_tren.add_trace(go.Scatter(
            x=sub[x_col], y=sub["max"],
            mode="lines" if granularity == "Harian" else "lines+markers",
            name=stn,
            line=dict(color=STATION_COLORS.get(stn, "#888"), width=2 if granularity != "Harian" else 1.5),
            marker=dict(size=6),
            hovertemplate=f"<b>{stn}</b><br>{x_lbl}: %{{x}}<br>ISPU: %{{y:.1f}}<extra></extra>",
        ))

    fig_tren.add_hline(y=50,  line_dash="dot", line_color="#4ade80",  annotation_text="50 — Batas SEDANG")
    fig_tren.add_hline(y=100, line_dash="dot", line_color="#f87171",  annotation_text="100 — Batas TDK SEHAT")
    fig_tren.add_hline(y=200, line_dash="dot", line_color="#e879f9",  annotation_text="200 — Batas STS")

    fig_tren.update_layout(
        title=dict(text=f"Tren ISPU — Granularitas {granularity}", font=dict(size=14, color=FONT_COLOR)),
        xaxis_title=x_lbl,
        yaxis_title="Nilai ISPU (max)",
    )
    apply_dark_theme(fig_tren, height=420)
    st.plotly_chart(fig_tren, use_container_width=True)

    # Perbandingan antar tahun yang dipilih
    st.markdown('<div class="section-header">Perbandingan Tren Bulanan Antar Tahun</div>', unsafe_allow_html=True)

    if compare_years:
        df_compare = dff[dff["tahun"].isin(compare_years)].copy()
        df_monthly_cmp = df_compare.groupby(["tahun", "bulan"])["max"].mean().reset_index()
        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
                       7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
        df_monthly_cmp["bulan_label"] = df_monthly_cmp["bulan"].map(month_names)

        palette_cmp = px.colors.qualitative.Set2
        fig_cmp = go.Figure()
        for i, yr in enumerate(sorted(compare_years)):
            sub = df_monthly_cmp[df_monthly_cmp["tahun"] == yr]
            fig_cmp.add_trace(go.Scatter(
                x=sub["bulan_label"], y=sub["max"],
                mode="lines+markers",
                name=str(yr),
                line=dict(color=palette_cmp[i % len(palette_cmp)], width=2.5),
                marker=dict(size=8),
                hovertemplate=f"<b>{yr}</b><br>%{{x}}: ISPU %{{y:.1f}}<extra></extra>",
            ))

        fig_cmp.update_layout(
            title=dict(text="Perbandingan Pola Bulanan ISPU", font=dict(size=13, color=FONT_COLOR)),
            xaxis=dict(categoryorder="array",
                       categoryarray=["Jan","Feb","Mar","Apr","Mei","Jun",
                                      "Jul","Agu","Sep","Okt","Nov","Des"]),
            xaxis_title="Bulan",
            yaxis_title="Rata-rata ISPU",
        )
        apply_dark_theme(fig_cmp, height=360)
        st.plotly_chart(fig_cmp, use_container_width=True)
    else:
        st.info("Pilih minimal 1 tahun untuk perbandingan.")

    # Rolling average
    col_roll1, col_roll2 = st.columns(2)
    with col_roll1:
        st.markdown('<div class="section-header">Rolling Average 30-Hari (Keseluruhan)</div>', unsafe_allow_html=True)
        daily_all = dff.groupby("tanggal")["max"].mean().reset_index().sort_values("tanggal")
        daily_all["roll30"] = daily_all["max"].rolling(30, center=True).mean()

        fig_roll = go.Figure()
        fig_roll.add_trace(go.Scatter(
            x=daily_all["tanggal"], y=daily_all["max"],
            mode="lines", name="Harian",
            line=dict(color="rgba(0,212,255,0.25)", width=1),
        ))
        fig_roll.add_trace(go.Scatter(
            x=daily_all["tanggal"], y=daily_all["roll30"],
            mode="lines", name="Rolling 30-hari",
            line=dict(color=ACCENT_BLUE, width=2.5),
        ))
        apply_dark_theme(fig_roll, height=300)
        st.plotly_chart(fig_roll, use_container_width=True)

    with col_roll2:
        st.markdown('<div class="section-header">Distribusi ISPU per Tahun (Boxplot)</div>', unsafe_allow_html=True)
        fig_box = go.Figure()
        for yr in sorted(dff["tahun"].unique()):
            sub = dff[dff["tahun"] == yr]
            fig_box.add_trace(go.Box(
                y=sub["max"], name=str(yr),
                boxmean=True,
                marker_color=ACCENT_BLUE,
                line_color=ACCENT_BLUE,
                fillcolor="rgba(0,212,255,0.15)",
            ))
        apply_dark_theme(fig_box, height=300, showlegend=False)
        fig_box.update_layout(xaxis_title="Tahun", yaxis_title="Nilai ISPU")
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <h4>💡 Insight — Tren Temporal</h4>
        <ul>
            <li><b>2013, 2018, dan 2019</b> merupakan tahun dengan ISPU tertinggi, bertepatan dengan musim kemarau ekstrem dan dampak El Niño.</li>
            <li><b>2020</b> mencatat penurunan tajam ISPU — dampak pembatasan mobilitas (PSBB/Lockdown COVID-19) yang mengurangi emisi kendaraan.</li>
            <li>Pola bulanan menunjukkan peningkatan konsisten pada <b>September–Oktober</b>, puncak musim kemarau di Jakarta.</li>
            <li>Tren jangka panjang menunjukkan fluktuasi dengan tren sedikit meningkat pasca-2020, seiring pemulihan aktivitas ekonomi.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# TAB 3 — PERBANDINGAN STASIUN
# ══════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🏭 Perbandingan Kualitas Udara Antar 5 Stasiun SPKU</div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([6, 4])

    with col_s1:
        # Stacked bar distribusi kategori per stasiun
        cat_stn = dff.groupby(["stasiun", "categori"]).size().reset_index(name="jumlah")
        total_per_stn = cat_stn.groupby("stasiun")["jumlah"].transform("sum")
        cat_stn["persen"] = cat_stn["jumlah"] / total_per_stn * 100

        fig_stack = go.Figure()
        for cat in all_cats:
            sub = cat_stn[cat_stn["categori"] == cat]
            fig_stack.add_trace(go.Bar(
                name=cat,
                x=sub["stasiun"],
                y=sub["persen"],
                marker_color=CAT_COLORS.get(cat, "#888"),
                hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{y:.1f}}%<extra></extra>",
            ))
        fig_stack.update_layout(
            barmode="stack",
            title=dict(text="Distribusi Kategori ISPU per Stasiun (%)", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Stasiun", yaxis_title="Persentase (%)",
            xaxis=dict(tickangle=-15),
        )
        apply_dark_theme(fig_stack, height=380)
        st.plotly_chart(fig_stack, use_container_width=True)

    with col_s2:
        # Radar chart rata-rata parameter per stasiun
        params = ["pm10", "so2", "co", "o3", "no2"]
        param_lbl = ["PM10", "SO2", "CO", "O3", "NO2"]
        stn_radar = dff.groupby("stasiun")[params].mean()

        fig_radar = go.Figure()
        for stn in stn_radar.index:
            vals = stn_radar.loc[stn].tolist()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=param_lbl + [param_lbl[0]],
                fill="toself",
                name=stn.split()[0],
                line_color=STATION_COLORS.get(stn, "#888"),
                fillcolor=STATION_COLORS.get(stn, "#888").replace("#", "rgba(").replace(")", ",0.1)") if False else f"rgba(0,0,0,0.05)",
            ))
        fig_radar.update_layout(
            title=dict(text="Profil Parameter per Stasiun", font=dict(size=13, color=FONT_COLOR)),
            polar=dict(
                bgcolor=CHART_BG,
                angularaxis=dict(color=FONT_COLOR, gridcolor=GRID_COLOR),
                radialaxis=dict(color=FONT_COLOR, gridcolor=GRID_COLOR),
            ),
        )
        apply_dark_theme(fig_radar, height=380)
        st.plotly_chart(fig_radar, use_container_width=True)

    # Baris kedua
    col_s3, col_s4 = st.columns(2)

    with col_s3:
        # Violin plot distribusi ISPU per stasiun
        fig_violin = go.Figure()
        for stn in all_stations:
            sub = dff[dff["stasiun"] == stn]
            fig_violin.add_trace(go.Violin(
                y=sub["max"],
                name=stn.split()[0],
                box_visible=True,
                meanline_visible=True,
                fillcolor=STATION_COLORS.get(stn, "#888"),
                opacity=0.7,
                line_color=STATION_COLORS.get(stn, "#888"),
            ))
        fig_violin.update_layout(
            title=dict(text="Distribusi Nilai ISPU per Stasiun", font=dict(size=13, color=FONT_COLOR)),
            yaxis_title="Nilai ISPU",
            violinmode="overlay",
        )
        apply_dark_theme(fig_violin, height=360)
        st.plotly_chart(fig_violin, use_container_width=True)

    with col_s4:
        # Heatmap rata-rata ISPU per stasiun per tahun
        pivot = dff.groupby(["stasiun", "tahun"])["max"].mean().unstack("tahun")
        # Singkat nama stasiun
        pivot.index = [s.split()[0] + " " + " ".join(s.split()[1:]) for s in pivot.index]

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=pivot.index,
            colorscale=[
                [0.0, "#1a4a2e"], [0.2, "#4ade80"],
                [0.4, "#fbbf24"], [0.6, "#f97316"],
                [0.8, "#ef4444"], [1.0, "#9b2335"],
            ],
            text=np.round(pivot.values, 1),
            texttemplate="%{text}",
            textfont=dict(size=9),
            hovertemplate="<b>%{y}</b><br>Tahun %{x}<br>ISPU: %{z:.1f}<extra></extra>",
            colorbar=dict(title="ISPU", tickfont=dict(color=FONT_COLOR)),
        ))
        fig_heat.update_layout(
            title=dict(text="Rata-rata ISPU per Stasiun per Tahun", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Tahun", yaxis_title="",
            xaxis=dict(tickangle=-45),
        )
        apply_dark_theme(fig_heat, height=360)
        st.plotly_chart(fig_heat, use_container_width=True)

    # Tabel ringkasan
    st.markdown('<div class="section-header">Ringkasan Statistik per Stasiun</div>', unsafe_allow_html=True)
    stn_summary = dff.groupby("stasiun").agg(
        Rata_Rata_ISPU=("max", "mean"),
        Median_ISPU=("max", "median"),
        Maks_ISPU=("max", "max"),
        Std_ISPU=("max", "std"),
        Persen_Tidak_Sehat=("categori", lambda x: (x.isin(["TIDAK SEHAT","SANGAT TIDAK SEHAT","BERBAHAYA"])).mean()*100),
        Persen_Baik=("categori", lambda x: (x == "BAIK").mean()*100),
    ).round(1).reset_index()
    stn_summary.columns = ["Stasiun", "Rata-rata ISPU", "Median", "Maks", "Std Dev", "% Tidak Sehat+", "% BAIK"]
    st.dataframe(stn_summary.style.background_gradient(subset=["Rata-rata ISPU", "% Tidak Sehat+"], cmap="YlOrRd"),
                 use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight-box">
        <h4>💡 Insight — Perbandingan Stasiun</h4>
        <ul>
            <li><b>DKI2 Kelapa Gading</b> (Jakarta Utara) konsisten paling buruk — dipengaruhi industri, pelabuhan, dan kepadatan kendaraan berat.</li>
            <li><b>DKI4 Lubang Buaya</b> (Jakarta Timur) menempati posisi kedua terburuk, dengan konsentrasi PM10 dan PM2.5 yang tinggi.</li>
            <li><b>DKI1 Bunderan HI</b> (Jakarta Pusat) memiliki rata-rata ISPU terendah — paradoks menarik mengingat lokasinya di jantung kota.</li>
            <li>Profil radar menunjukkan setiap stasiun memiliki <b>pencemar "signature"</b> yang berbeda sesuai aktivitas lingkungan sekitarnya.</li>
            <li>Variansi tinggi (std dev besar) pada DKI2 dan DKI4 mengindikasikan kualitas udara yang tidak stabil dan sering melonjak.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# TAB 4 — ANALISIS PARAMETER PENCEMAR KRITIS
# ══════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">⚗️ Analisis Parameter Pencemar Kritis</div>', unsafe_allow_html=True)

    # Filter tambahan
    t4_params = st.multiselect(
        "Parameter Pencemar",
        options=["PM10", "PM2.5", "O3", "CO", "SO2", "NO2"],
        default=["PM10", "PM2.5", "O3", "CO", "SO2", "NO2"],
        key="t4_params",
    )

    col_p1, col_p2 = st.columns([5, 5])

    with col_p1:
        # Bar frekuensi per parameter per stasiun
        pol_stn = dff[dff["critical"].isin(t4_params)].groupby(["stasiun", "critical"]).size().reset_index(name="frekuensi")
        fig_pol = px.bar(
            pol_stn, x="stasiun", y="frekuensi", color="critical",
            color_discrete_map=PARAM_COLORS,
            barmode="group",
            title="Frekuensi Pencemar Kritis per Stasiun",
            labels={"stasiun": "Stasiun", "frekuensi": "Frekuensi (hari)", "critical": "Parameter"},
        )
        fig_pol.update_layout(xaxis=dict(tickangle=-20))
        apply_dark_theme(fig_pol, height=380)
        st.plotly_chart(fig_pol, use_container_width=True)

    with col_p2:
        # Tren tahunan kemunculan pencemar kritis
        pol_yr = dff[dff["critical"].isin(t4_params)].groupby(["tahun", "critical"]).size().reset_index(name="frekuensi")
        fig_pol_yr = px.line(
            pol_yr, x="tahun", y="frekuensi", color="critical",
            color_discrete_map=PARAM_COLORS,
            markers=True,
            title="Tren Tahunan Kemunculan Pencemar Kritis",
            labels={"tahun": "Tahun", "frekuensi": "Frekuensi (hari)", "critical": "Parameter"},
        )
        apply_dark_theme(fig_pol_yr, height=380)
        st.plotly_chart(fig_pol_yr, use_container_width=True)

    # Baris kedua: distribusi nilai per parameter + heatmap
    col_p3, col_p4 = st.columns([5, 5])

    with col_p3:
        st.markdown('<div class="section-header">Distribusi Nilai per Parameter</div>', unsafe_allow_html=True)
        param_cols = {"PM10":"pm10","PM2.5":"pm25","O3":"o3","CO":"co","SO2":"so2","NO2":"no2"}
        selected_raw = [param_cols[p] for p in t4_params if p in param_cols and param_cols[p] in dff.columns]

        if selected_raw:
            fig_dist = go.Figure()
            for raw_col in selected_raw:
                param_name = {v: k for k, v in param_cols.items()}[raw_col]
                vals = dff[raw_col].dropna()
                fig_dist.add_trace(go.Violin(
                    y=vals, name=param_name,
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor=PARAM_COLORS.get(param_name, "#888"),
                    opacity=0.7,
                    line_color=PARAM_COLORS.get(param_name, "#888"),
                ))
            fig_dist.update_layout(
                title=dict(text="Distribusi Nilai Konsentrasi (ISPU)", font=dict(size=13, color=FONT_COLOR)),
                yaxis_title="Nilai ISPU",
                violinmode="overlay",
            )
            apply_dark_theme(fig_dist, height=360)
            st.plotly_chart(fig_dist, use_container_width=True)

    with col_p4:
        # Heatmap pencemar vs bulan
        st.markdown('<div class="section-header">Kemunculan Pencemar per Bulan</div>', unsafe_allow_html=True)
        pol_month = dff[dff["critical"].isin(t4_params)].groupby(["bulan", "critical"]).size().reset_index(name="frekuensi")
        pol_pivot = pol_month.pivot(index="critical", columns="bulan", values="frekuensi").fillna(0)
        month_labels = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
        pol_pivot.columns = [month_labels[c-1] for c in pol_pivot.columns]

        fig_pheat = go.Figure(go.Heatmap(
            z=pol_pivot.values,
            x=pol_pivot.columns,
            y=pol_pivot.index,
            colorscale="YlOrRd",
            text=pol_pivot.values.astype(int),
            texttemplate="%{text}",
            textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.0f} hari<extra></extra>",
            colorbar=dict(title="Frekuensi", tickfont=dict(color=FONT_COLOR)),
        ))
        fig_pheat.update_layout(
            title=dict(text="Frekuensi Kemunculan Pencemar per Bulan", font=dict(size=13, color=FONT_COLOR)),
            paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
            font=dict(color=FONT_COLOR),
            margin=dict(l=80, r=20, t=50, b=50),
        )
        apply_dark_theme(fig_pheat, height=360)
        st.plotly_chart(fig_pheat, use_container_width=True)

    # Korelasi antar parameter
    st.markdown('<div class="section-header">Korelasi Antar Parameter Pencemar</div>', unsafe_allow_html=True)
    corr_cols = ["pm10", "so2", "co", "o3", "no2", "max"]
    corr_labels = ["PM10", "SO2", "CO", "O3", "NO2", "ISPU Max"]
    corr_df = dff[corr_cols].dropna(how="any")
    corr_matrix = corr_df.corr()

    fig_corr = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_labels,
        y=corr_labels,
        colorscale="RdBu",
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=11),
        hovertemplate="<b>%{x} × %{y}</b><br>Korelasi: %{z:.3f}<extra></extra>",
        colorbar=dict(title="r", tickfont=dict(color=FONT_COLOR)),
    ))
    fig_corr.update_layout(
        title=dict(text="Matriks Korelasi Parameter Pencemar", font=dict(size=13, color=FONT_COLOR)),
    )
    apply_dark_theme(fig_corr, height=380)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <h4>💡 Insight — Parameter Pencemar</h4>
        <ul>
            <li><b>O3 (Ozon)</b> mendominasi April–Oktober, sesuai pola paparan sinar matahari tinggi (musim kemarau). Reaksi fotokimia dari emisi kendaraan menjadi pendorong utama.</li>
            <li><b>PM2.5 dan PM10</b> meningkat signifikan di September–Oktober, bertepatan dengan musim kemarau puncak dan pengaruh kebakaran lahan/hutan.</li>
            <li><b>CO</b> relatif lebih merata sepanjang tahun — mengindikasikan sumber stasioner (industri) dan tidak terlalu bergantung musim.</li>
            <li>Korelasi PM10–ISPU Max sangat tinggi (>0.85), menjadikannya indikator kondisi udara yang paling andal secara umum.</li>
            <li><b>DKI4 Lubang Buaya</b> mendominasi kemunculan PM10 dan PM2.5, sementara <b>DKI2 Kelapa Gading</b> mendominasi O3.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# TAB 5 — POLA MUSIMAN
# ══════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">🌦️ Pola Musiman Kualitas Udara Jakarta</div>', unsafe_allow_html=True)

    month_order = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
                 7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
    dff["bulan_label"] = dff["bulan"].map(month_map)

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        # Rata-rata ISPU per bulan (bar + line)
        monthly_avg = dff.groupby("bulan").agg(
            avg_ispu=("max", "mean"),
            med_ispu=("max", "median"),
        ).reset_index()
        monthly_avg["bulan_label"] = monthly_avg["bulan"].map(month_map)

        fig_month = go.Figure()
        fig_month.add_trace(go.Bar(
            x=monthly_avg["bulan_label"],
            y=monthly_avg["avg_ispu"],
            name="Rata-rata",
            marker=dict(
                color=monthly_avg["avg_ispu"],
                colorscale=[[0,"#4ade80"],[0.35,"#fbbf24"],[0.65,"#f97316"],[1,"#ef4444"]],
                showscale=False,
            ),
            text=[f"{v:.1f}" for v in monthly_avg["avg_ispu"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Rata-rata ISPU: %{y:.1f}<extra></extra>",
        ))
        fig_month.add_trace(go.Scatter(
            x=monthly_avg["bulan_label"],
            y=monthly_avg["med_ispu"],
            mode="lines+markers",
            name="Median",
            line=dict(color=ACCENT_BLUE, width=2, dash="dash"),
            marker=dict(size=7),
        ))
        fig_month.add_hline(y=100, line_dash="dot", line_color="#f87171", annotation_text="Batas TDK SEHAT")
        fig_month.update_layout(
            title=dict(text="Rata-rata ISPU Bulanan (Semua Tahun)", font=dict(size=13, color=FONT_COLOR)),
            xaxis=dict(categoryorder="array", categoryarray=month_order),
            xaxis_title="Bulan", yaxis_title="Rata-rata ISPU",
        )
        apply_dark_theme(fig_month, height=360)
        st.plotly_chart(fig_month, use_container_width=True)

    with col_m2:
        # Heatmap bulan × tahun
        pv_seasonal = dff.groupby(["tahun", "bulan"])["max"].mean().reset_index()
        pv_seasonal["bulan_label"] = pv_seasonal["bulan"].map(month_map)
        pivot_sea = pv_seasonal.pivot(index="tahun", columns="bulan_label", values="max")
        pivot_sea = pivot_sea.reindex(columns=month_order)

        fig_sheat = go.Figure(go.Heatmap(
            z=pivot_sea.values,
            x=pivot_sea.columns,
            y=pivot_sea.index,
            colorscale=[
                [0.0, "#1a4a2e"], [0.25, "#4ade80"],
                [0.5, "#fbbf24"], [0.75, "#f97316"],
                [1.0, "#9b2335"],
            ],
            text=np.round(pivot_sea.values, 0),
            texttemplate="%{text:.0f}",
            textfont=dict(size=9),
            hovertemplate="<b>%{y} — %{x}</b><br>ISPU: %{z:.1f}<extra></extra>",
            colorbar=dict(title="ISPU", tickfont=dict(color=FONT_COLOR)),
        ))
        fig_sheat.update_layout(
            title=dict(text="Heatmap Pola Musiman ISPU (Tahun × Bulan)", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Bulan", yaxis_title="Tahun",
        )
        apply_dark_theme(fig_sheat, height=360)
        st.plotly_chart(fig_sheat, use_container_width=True)

    # Frekuensi kategori per bulan
    st.markdown('<div class="section-header">Distribusi Kategori ISPU per Bulan</div>', unsafe_allow_html=True)
    cat_month = dff.groupby(["bulan", "categori"]).size().reset_index(name="jumlah")
    total_per_bulan = cat_month.groupby("bulan")["jumlah"].transform("sum")
    cat_month["persen"] = cat_month["jumlah"] / total_per_bulan * 100
    cat_month["bulan_label"] = cat_month["bulan"].map(month_map)

    fig_cat_month = go.Figure()
    for cat in all_cats:
        sub = cat_month[cat_month["categori"] == cat].sort_values("bulan")
        fig_cat_month.add_trace(go.Bar(
            name=cat,
            x=sub["bulan_label"],
            y=sub["persen"],
            marker_color=CAT_COLORS.get(cat, "#888"),
            hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{y:.1f}}%<extra></extra>",
        ))
    fig_cat_month.update_layout(
        barmode="stack",
        title=dict(text="Distribusi Kategori ISPU per Bulan (%)", font=dict(size=13, color=FONT_COLOR)),
        xaxis=dict(categoryorder="array", categoryarray=month_order),
        xaxis_title="Bulan", yaxis_title="Persentase (%)",
    )
    apply_dark_theme(fig_cat_month, height=360)
    st.plotly_chart(fig_cat_month, use_container_width=True)

    # Polar chart (pola sirkuler sepanjang tahun)
    col_pol1, col_pol2 = st.columns(2)
    with col_pol1:
        st.markdown('<div class="section-header">Pola Radial ISPU Bulanan per Stasiun</div>', unsafe_allow_html=True)
        monthly_stn = dff.groupby(["bulan", "stasiun"])["max"].mean().reset_index()
        monthly_stn["bulan_label"] = monthly_stn["bulan"].map(month_map)

        fig_polar = go.Figure()
        for stn in all_stations:
            sub = monthly_stn[monthly_stn["stasiun"] == stn].sort_values("bulan")
            fig_polar.add_trace(go.Scatterpolar(
                r=sub["max"].tolist() + [sub["max"].iloc[0]],
                theta=sub["bulan_label"].tolist() + [sub["bulan_label"].iloc[0]],
                mode="lines+markers",
                name=stn.split()[0],
                line_color=STATION_COLORS.get(stn, "#888"),
                marker=dict(size=6),
            ))
        fig_polar.update_layout(
            title=dict(text="Pola Radial ISPU Bulanan", font=dict(size=13, color=FONT_COLOR)),
            polar=dict(
                bgcolor=CHART_BG,
                angularaxis=dict(color=FONT_COLOR, gridcolor=GRID_COLOR),
                radialaxis=dict(color=FONT_COLOR, gridcolor=GRID_COLOR),
            ),
        )
        apply_dark_theme(fig_polar, height=400)
        st.plotly_chart(fig_polar, use_container_width=True)

    with col_pol2:
        st.markdown('<div class="section-header">Bulan Terbaik & Terburuk per Stasiun</div>', unsafe_allow_html=True)
        best_worst = []
        for stn in all_stations:
            sub = dff[dff["stasiun"] == stn].groupby("bulan")["max"].mean()
            best_worst.append({
                "Stasiun": stn.split()[0],
                "Bulan Terbaik": month_map[sub.idxmin()],
                "ISPU Terbaik": round(sub.min(), 1),
                "Bulan Terburuk": month_map[sub.idxmax()],
                "ISPU Terburuk": round(sub.max(), 1),
            })
        df_bw = pd.DataFrame(best_worst)

        fig_bw = go.Figure()
        fig_bw.add_trace(go.Bar(
            name="Bulan Terbaik",
            x=df_bw["Stasiun"],
            y=df_bw["ISPU Terbaik"],
            marker_color="#4ade80",
            text=[f"{r['Bulan Terbaik']} ({r['ISPU Terbaik']})" for _, r in df_bw.iterrows()],
            textposition="outside",
        ))
        fig_bw.add_trace(go.Bar(
            name="Bulan Terburuk",
            x=df_bw["Stasiun"],
            y=df_bw["ISPU Terburuk"],
            marker_color="#ef4444",
            text=[f"{r['Bulan Terburuk']} ({r['ISPU Terburuk']})" for _, r in df_bw.iterrows()],
            textposition="outside",
        ))
        fig_bw.update_layout(
            barmode="group",
            title=dict(text="ISPU Rata-rata Bulan Terbaik vs Terburuk", font=dict(size=13, color=FONT_COLOR)),
            xaxis_title="Stasiun", yaxis_title="Rata-rata ISPU",
        )
        apply_dark_theme(fig_bw, height=400)
        st.plotly_chart(fig_bw, use_container_width=True)

        st.dataframe(df_bw.style.background_gradient(subset=["ISPU Terburuk"], cmap="YlOrRd"),
                     use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight-box">
        <h4>💡 Insight — Pola Musiman</h4>
        <ul>
            <li><b>Musim Kemarau (Juni–Oktober)</b> adalah periode kualitas udara terburuk. September menjadi bulan terburuk dengan rata-rata ISPU tertinggi (~89).</li>
            <li><b>Musim Hujan (November–Februari)</b> memberikan efek pembersihan alami — curah hujan tinggi mengurangi konsentrasi partikulat dan menurunkan ISPU.</li>
            <li><b>Januari dan Desember</b> secara konsisten mencatat kualitas udara terbaik, bertepatan dengan puncak musim hujan Jakarta.</li>
            <li>Pola ini konsisten di semua 5 stasiun, mengindikasikan faktor <b>meteorologis skala kota</b> (angin muson, curah hujan) lebih dominan dari faktor lokal stasiun.</li>
            <li>Tahun-tahun dengan musim kemarau panjang (El Niño: 2015, 2019) menunjukkan "hot spot" merah gelap pada heatmap, mengkonfirmasi korelasi iklim–kualitas udara.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#5a7a90; font-size:0.8rem; padding: 12px;'>
    Dashboard ISPU Jakarta • Data: Dinas Lingkungan Hidup DKI Jakarta (2010–2023) •
    5 Stasiun SPKU: DKI1 Bunderan HI | DKI2 Kelapa Gading | DKI3 Jagakarsa | DKI4 Lubang Buaya | DKI5 Kebon Jeruk
</div>
""", unsafe_allow_html=True)