import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# ==============================
# CONFIGURACIÓN
# ==============================

load_dotenv()

st.set_page_config(
    page_title="Análisis Climático Colombia",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# ESTILOS CSS
# ==============================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main { background-color: #0a0f1e; }

    .stApp {
        background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a1628 100%);
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
    }

    /* HEADER */
    .header-container {
        background: linear-gradient(135deg, #0d1b2a, #1a2d4a);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(0,212,255,0.05) 0%, transparent 60%);
        pointer-events: none;
    }
    .header-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #00d4ff;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 0.3rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .header-badge {
        display: inline-block;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        color: #00d4ff;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 1rem;
    }

    /* KPI CARDS */
    .kpi-card {
        background: linear-gradient(135deg, #111827, #1a2d4a);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #0066ff);
        border-radius: 0 0 16px 16px;
    }
    .kpi-value {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    .kpi-label {
        color: #8899aa;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 0.4rem;
    }
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* SECTION HEADERS */
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 0.5rem 0;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        margin-bottom: 1.2rem;
    }

    /* ALERT CARDS */
    .alert-card {
        background: rgba(255, 60, 60, 0.08);
        border: 1px solid rgba(255, 60, 60, 0.3);
        border-left: 4px solid #ff3c3c;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.6rem;
        color: #ffaaaa;
        font-size: 0.85rem;
    }
    .alert-card.humedad {
        background: rgba(0, 150, 255, 0.08);
        border-color: rgba(0, 150, 255, 0.3);
        border-left-color: #0096ff;
        color: #aaddff;
    }
    .alert-card.viento {
        background: rgba(150, 255, 150, 0.08);
        border-color: rgba(150, 255, 150, 0.3);
        border-left-color: #96ff96;
        color: #aaffaa;
    }
    .alert-card.frio {
        background: rgba(150, 200, 255, 0.08);
        border-color: rgba(150, 200, 255, 0.3);
        border-left-color: #96c8ff;
        color: #cce5ff;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a, #0a1220) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.1);
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        color: #8899aa;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 212, 255, 0.15) !important;
        color: #00d4ff !important;
    }

    /* DIVIDER */
    hr { border-color: rgba(0, 212, 255, 0.1) !important; }

    /* HIDE DEFAULT ELEMENTS */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==============================
# CONEXIÓN BD
# ==============================

@st.cache_resource
def get_engine():
    try:
        host     = st.secrets["DB_HOST"]
        db       = st.secrets["DB_NAME"]
        user     = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
        port     = st.secrets["DB_PORT"]
    except:
        host     = os.getenv("DB_HOST", "localhost")
        db       = os.getenv("DB_NAME", "clima_db")
        user     = os.getenv("DB_USER", "clima_user")
        password = os.getenv("DB_PASSWORD", "clima1234")
        port     = os.getenv("DB_PORT", "5432")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


def localize_to_bogota(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if df[col].dt.tz is None:
                df[col] = df[col].dt.tz_localize("America/Bogota")
            else:
                df[col] = df[col].dt.tz_convert("America/Bogota")
    return df

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    query = """
        SELECT
            m.id, m.fecha_consulta,
            m.temperatura, m.temp_min, m.temp_max, m.sensacion_termica,
            m.humedad, m.presion,
            m.velocidad_viento, m.direccion_viento,
            m.descripcion, m.nubosidad,
            c.nombre AS ciudad, c.departamento, c.pais,
            c.latitud, c.longitud
        FROM mediciones m
        JOIN ciudades c ON m.ciudad_id = c.id
        ORDER BY m.fecha_consulta DESC
    """
    df = pd.read_sql(query, engine)
    return localize_to_bogota(df, ["fecha_consulta"])


@st.cache_data(ttl=300)
def load_alertas():
    engine = get_engine()
    query = """
        SELECT a.*, c.nombre AS ciudad, c.departamento
        FROM alertas_climaticas a
        JOIN ciudades c ON a.ciudad_id = c.id
        ORDER BY a.fecha DESC
        LIMIT 100
    """
    df = pd.read_sql(query, engine)
    return localize_to_bogota(df, ["fecha"])


@st.cache_data(ttl=300)
def load_ultima_medicion():
    engine = get_engine()
    query = """
        SELECT DISTINCT ON (c.id)
            c.nombre AS ciudad, c.departamento,
            c.latitud, c.longitud,
            m.temperatura, m.temp_min, m.temp_max,
            m.humedad, m.velocidad_viento,
            m.descripcion, m.nubosidad,
            m.fecha_consulta
        FROM mediciones m
        JOIN ciudades c ON m.ciudad_id = c.id
        ORDER BY c.id, m.fecha_consulta DESC
    """
    df = pd.read_sql(query, engine)
    return localize_to_bogota(df, ["fecha_consulta"])


# ==============================
# CARGA DE DATOS
# ==============================

try:
    df          = load_data()
    df_alertas  = load_alertas()
    df_ultima   = load_ultima_medicion()
    connected   = True
except Exception as e:
    st.error(f"⚠️ No se pudo conectar a la base de datos: {e}")
    st.info("Asegúrate de que PostgreSQL esté corriendo y el ETL haya ejecutado al menos una vez.")
    connected = False
    st.stop()

# ==============================
# SIDEBAR
# ==============================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:3rem;'>🌦️</div>
        <div style='font-family: Syne, sans-serif; font-size:1.1rem; font-weight:800; color:#fff;'>
            Clima Colombia
        </div>
        <div style='color:#00d4ff; font-size:0.7rem; letter-spacing:2px; text-transform:uppercase; margin-top:4px;'>
            Dashboard Analítico
        </div>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    st.markdown("**🗺️ Filtros**")

    departamentos = ["Todos"] + sorted(df["departamento"].unique().tolist())
    dep_sel = st.selectbox("Departamento", departamentos)

    ciudades_filtradas = df["ciudad"].unique().tolist()
    if dep_sel != "Todos":
        ciudades_filtradas = df[df["departamento"] == dep_sel]["ciudad"].unique().tolist()

    ciudad_sel = st.multiselect("Ciudades", sorted(ciudades_filtradas), default=ciudades_filtradas[:5])

    st.markdown("---")
    st.markdown("**📅 Rango de Fechas**")
    fecha_min = df["fecha_consulta"].min().date()
    fecha_max = df["fecha_consulta"].max().date()
    fecha_ini = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
    fecha_fin = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)

    st.markdown("---")
    st.markdown("**⚙️ Opciones**")
    auto_refresh = st.toggle("Auto-refresh (5 min)", value=False)
    if auto_refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    ultima_act = df["fecha_consulta"].max()
    st.markdown(f"""
    <div style='color:#556677; font-size:0.75rem; text-align:center;'>
        Última actualización<br/>
        <span style='color:#00d4ff;'>{ultima_act.strftime('%d/%m/%Y %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# FILTRAR DATOS
# ==============================

df_f = df.copy()
if ciudad_sel:
    df_f = df_f[df_f["ciudad"].isin(ciudad_sel)]
df_f = df_f[
    (df_f["fecha_consulta"].dt.date >= fecha_ini) &
    (df_f["fecha_consulta"].dt.date <= fecha_fin)
]

# ==============================
# HEADER
# ==============================

st.markdown("""
<div class='header-container'>
    <div class='header-title'>🌍 Análisis Climático Colombia</div>
    <div class='header-subtitle'>Sistema de Monitoreo en Tiempo Real · 31 Capitales</div>
    <div class='header-badge'>📡 ETL Activo · OpenWeatherMap API</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# KPIs
# ==============================

col1, col2, col3, col4, col5 = st.columns(5)

temp_prom   = df_ultima["temperatura"].mean()
temp_max    = df_ultima["temperatura"].max()
temp_min    = df_ultima["temperatura"].min()
hum_prom    = df_ultima["humedad"].mean()
total_alert = len(df_alertas)

ciudad_max = df_ultima.loc[df_ultima["temperatura"].idxmax(), "ciudad"]
ciudad_min = df_ultima.loc[df_ultima["temperatura"].idxmin(), "ciudad"]

with col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>🌡️</div>
        <div class='kpi-value'>{temp_prom:.1f}°C</div>
        <div class='kpi-label'>Temp. Promedio</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>🔥</div>
        <div class='kpi-value'>{temp_max:.1f}°C</div>
        <div class='kpi-label'>Más Caliente · {ciudad_max}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>🧊</div>
        <div class='kpi-value'>{temp_min:.1f}°C</div>
        <div class='kpi-label'>Más Fría · {ciudad_min}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>💧</div>
        <div class='kpi-value'>{hum_prom:.0f}%</div>
        <div class='kpi-label'>Humedad Promedio</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>⚠️</div>
        <div class='kpi-value'>{total_alert}</div>
        <div class='kpi-label'>Alertas Totales</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ==============================
# TABS PRINCIPALES
# ==============================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️  Mapa en Vivo",
    "📈  Tendencias",
    "🔬  Análisis",
    "⚠️  Alertas",
    "📋  Datos Crudos"
])

PLOT_BG    = "rgba(10,15,30,0)"
PAPER_BG   = "rgba(10,15,30,0)"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "#aabbcc"
ACCENT     = "#00d4ff"

# ---- TAB 1: MAPA ----
with tab1:
    st.markdown("<div class='section-header'>🗺️ Temperatura Actual por Capital</div>", unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([3, 1])

    with col_m1:
        var_mapa = st.radio(
            "Variable a visualizar",
            ["temperatura", "humedad", "velocidad_viento"],
            horizontal=True,
            format_func=lambda x: {"temperatura":"🌡️ Temperatura","humedad":"💧 Humedad","velocidad_viento":"💨 Viento"}[x]
        )

        color_scales = {"temperatura": "RdYlBu_r", "humedad": "Blues", "velocidad_viento": "Greens"}
        unidades     = {"temperatura": "°C", "humedad": "%", "velocidad_viento": "m/s"}

        fig_map = px.scatter_mapbox(
            df_ultima,
            lat="latitud", lon="longitud",
            color=var_mapa,
            size=var_mapa,
            size_max=25,
            hover_name="ciudad",
            hover_data={
                "departamento": True,
                "temperatura": ":.1f",
                "humedad": True,
                "velocidad_viento": ":.1f",
                "descripcion": True,
                "latitud": False, "longitud": False
            },
            color_continuous_scale=color_scales[var_mapa],
            mapbox_style="carto-darkmatter",
            zoom=4.5,
            center={"lat": 4.5709, "lon": -74.2973},
            title=f"{var_mapa.replace('_',' ').title()} Actual ({unidades[var_mapa]})"
        )
        fig_map.update_layout(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font_color=FONT_COLOR,
            margin=dict(l=0, r=0, t=40, b=0),
            height=520,
            coloraxis_colorbar=dict(
                title=dict(
                    text=unidades[var_mapa],
                    font=dict(color=FONT_COLOR)
                ),
                tickfont=dict(color=FONT_COLOR)
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_m2:
        st.markdown("<div class='section-header'>🏆 Ranking</div>", unsafe_allow_html=True)
        ranking = df_ultima[["ciudad", var_mapa]].sort_values(var_mapa, ascending=False).reset_index(drop=True)
        ranking.index += 1
        ranking.columns = ["Ciudad", unidades[var_mapa]]
        st.dataframe(ranking, use_container_width=True, height=480)


# ---- TAB 2: TENDENCIAS ----
with tab2:
    st.markdown("<div class='section-header'>📈 Evolución Temporal</div>", unsafe_allow_html=True)

    if df_f.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            # Temperatura por ciudad
            fig_temp = px.line(
                df_f.sort_values("fecha_consulta"),
                x="fecha_consulta", y="temperatura",
                color="ciudad",
                title="🌡️ Temperatura (°C) por Ciudad",
                labels={"fecha_consulta": "Fecha", "temperatura": "°C", "ciudad": "Ciudad"}
            )
            fig_temp.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                font_color=FONT_COLOR, height=380,
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(gridcolor=GRID_COLOR),
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_temp, use_container_width=True)

        with col_t2:
            # Humedad por ciudad
            fig_hum = px.line(
                df_f.sort_values("fecha_consulta"),
                x="fecha_consulta", y="humedad",
                color="ciudad",
                title="💧 Humedad (%) por Ciudad",
                labels={"fecha_consulta": "Fecha", "humedad": "%", "ciudad": "Ciudad"}
            )
            fig_hum.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                font_color=FONT_COLOR, height=380,
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(gridcolor=GRID_COLOR),
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_hum, use_container_width=True)

        # Temperatura min/max/promedio por día
        st.markdown("<div class='section-header'>📊 Temperatura Diaria (Min / Prom / Max)</div>", unsafe_allow_html=True)

        df_f["fecha"] = df_f["fecha_consulta"].dt.date
        df_diario = df_f.groupby("fecha").agg(
            temp_min=("temperatura", "min"),
            temp_prom=("temperatura", "mean"),
            temp_max=("temperatura", "max")
        ).reset_index()

        fig_band = go.Figure([
            go.Scatter(
                x=df_diario["fecha"], y=df_diario["temp_max"],
                fill=None, mode="lines",
                line=dict(color="rgba(255,100,100,0.8)", width=2),
                name="Máx"
            ),
            go.Scatter(
                x=df_diario["fecha"], y=df_diario["temp_min"],
                fill="tonexty", mode="lines",
                line=dict(color="rgba(100,180,255,0.8)", width=2),
                fillcolor="rgba(0,212,255,0.08)",
                name="Mín"
            ),
            go.Scatter(
                x=df_diario["fecha"], y=df_diario["temp_prom"],
                mode="lines+markers",
                line=dict(color=ACCENT, width=3),
                marker=dict(size=6, color=ACCENT),
                name="Promedio"
            )
        ])
        fig_band.update_layout(
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_COLOR, height=320,
            xaxis=dict(gridcolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR, title="°C"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_band, use_container_width=True)

        # Viento
        col_t3, col_t4 = st.columns(2)
        with col_t3:
            fig_viento = px.area(
                df_f.sort_values("fecha_consulta"),
                x="fecha_consulta", y="velocidad_viento",
                color="ciudad",
                title="💨 Velocidad del Viento (m/s)",
                labels={"fecha_consulta": "Fecha", "velocidad_viento": "m/s"}
            )
            fig_viento.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                font_color=FONT_COLOR, height=320,
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(gridcolor=GRID_COLOR),
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_viento, use_container_width=True)

        with col_t4:
            fig_presion = px.line(
                df_f.sort_values("fecha_consulta"),
                x="fecha_consulta", y="presion",
                color="ciudad",
                title="🔵 Presión Atmosférica (hPa)",
                labels={"fecha_consulta": "Fecha", "presion": "hPa"}
            )
            fig_presion.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                font_color=FONT_COLOR, height=320,
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(gridcolor=GRID_COLOR),
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_presion, use_container_width=True)


# ---- TAB 3: ANÁLISIS ----
with tab3:
    st.markdown("<div class='section-header'>🔬 Análisis Estadístico y Correlaciones</div>", unsafe_allow_html=True)

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        # Boxplot temperaturas por ciudad
        fig_box = px.box(
            df_f, x="ciudad", y="temperatura",
            color="ciudad",
            title="📦 Distribución de Temperaturas por Ciudad",
            labels={"temperatura": "°C", "ciudad": ""}
        )
        fig_box.update_layout(
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_COLOR, height=400,
            xaxis=dict(gridcolor=GRID_COLOR, tickangle=45),
            yaxis=dict(gridcolor=GRID_COLOR),
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col_a2:
        # Scatter temperatura vs humedad
        fig_scatter = px.scatter(
            df_f, x="temperatura", y="humedad",
            color="ciudad", size="velocidad_viento",
            title="🔗 Temperatura vs Humedad",
            labels={"temperatura": "Temperatura (°C)", "humedad": "Humedad (%)"},
            trendline="ols"
        )
        fig_scatter.update_layout(
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_COLOR, height=400,
            xaxis=dict(gridcolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    col_a3, col_a4 = st.columns(2)

    with col_a3:
        # Heatmap correlación
        vars_corr = ["temperatura", "temp_min", "temp_max", "humedad", "presion", "velocidad_viento", "nubosidad"]
        corr = df_f[vars_corr].corr().round(2)

        fig_heat = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdBu_r",
            zmid=0,
            text=corr.values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        fig_heat.update_layout(
            title="🔥 Matriz de Correlación",
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_COLOR, height=400,
            xaxis=dict(tickangle=45)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_a4:
        # Radar chart por ciudad (últimas mediciones)
        ciudades_radar = df_ultima["ciudad"].tolist()[:8]
        df_radar = df_ultima[df_ultima["ciudad"].isin(ciudades_radar)]

        # Normalizar para radar
        vars_radar = ["temperatura", "humedad", "velocidad_viento", "nubosidad"]
        df_norm = df_radar[vars_radar].copy()
        for col in vars_radar:
            rng = df_norm[col].max() - df_norm[col].min()
            df_norm[col] = (df_norm[col] - df_norm[col].min()) / (rng if rng != 0 else 1)

        fig_radar = go.Figure()
        for i, row in df_radar.iterrows():
            vals = df_norm.loc[i, vars_radar].tolist()
            vals += [vals[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=vars_radar + [vars_radar[0]],
                fill="toself",
                name=row["ciudad"],
                opacity=0.6
            ))
        fig_radar.update_layout(
            title="🕸️ Comparación Multivariable",
            polar=dict(
                radialaxis=dict(visible=True, color=FONT_COLOR),
                bgcolor="rgba(0,0,0,0)"
            ),
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR, height=400,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9))
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Estadísticas descriptivas
    st.markdown("<div class='section-header'>📊 Estadísticas Descriptivas</div>", unsafe_allow_html=True)
    stats = df_f[["temperatura","temp_min","temp_max","humedad","presion","velocidad_viento"]].describe().round(2)
    st.dataframe(stats, use_container_width=True)


# ---- TAB 4: ALERTAS ----
with tab4:
    st.markdown("<div class='section-header'>⚠️ Centro de Alertas Climáticas</div>", unsafe_allow_html=True)

    if df_alertas.empty:
        st.success("✅ Sin alertas registradas actualmente.")
    else:
        col_al1, col_al2 = st.columns([2, 1])

        with col_al1:
            # Últimas alertas
            for _, row in df_alertas.head(20).iterrows():
                tipo = row["tipo_alerta"]
                css_class = ""
                icon = "⚠️"
                if "Temperatura" in tipo and "Alta" in tipo:
                    css_class = ""
                    icon = "🔥"
                elif "Temperatura" in tipo and "Baja" in tipo:
                    css_class = "frio"
                    icon = "🧊"
                elif "Humedad" in tipo:
                    css_class = "humedad"
                    icon = "💧"
                elif "Viento" in tipo:
                    css_class = "viento"
                    icon = "🌬️"

                st.markdown(f"""
                <div class='alert-card {css_class}'>
                    {icon} <strong>{row['ciudad']}</strong> — {row['tipo_alerta']}
                    &nbsp;·&nbsp; {row['descripcion']}
                    &nbsp;·&nbsp; <span style='opacity:0.6'>{pd.to_datetime(row['fecha']).strftime('%d/%m %H:%M')}</span>
                </div>
                """, unsafe_allow_html=True)

        with col_al2:
            # Donut por tipo de alerta
            conteo = df_alertas["tipo_alerta"].value_counts().reset_index()
            conteo.columns = ["Tipo", "Total"]

            fig_donut = px.pie(
                conteo, names="Tipo", values="Total",
                title="Distribución de Alertas",
                hole=0.55,
                color_discrete_sequence=["#ff4444", "#0096ff", "#96ff96", "#96c8ff"]
            )
            fig_donut.update_layout(
                paper_bgcolor=PAPER_BG,
                font_color=FONT_COLOR, height=350,
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            # Alertas por ciudad
            por_ciudad = df_alertas["ciudad"].value_counts().head(10).reset_index()
            por_ciudad.columns = ["Ciudad", "Alertas"]
            fig_bar_al = px.bar(
                por_ciudad, x="Alertas", y="Ciudad",
                orientation="h",
                title="Top 10 ciudades con alertas",
                color="Alertas",
                color_continuous_scale="Reds"
            )
            fig_bar_al.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                font_color=FONT_COLOR, height=320,
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(gridcolor=GRID_COLOR),
                showlegend=False, coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar_al, use_container_width=True)


# ---- TAB 5: DATOS CRUDOS ----
with tab5:
    st.markdown("<div class='section-header'>📋 Datos Crudos</div>", unsafe_allow_html=True)

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("Total registros", len(df_f))
    with col_d2:
        st.metric("Ciudades", df_f["ciudad"].nunique())
    with col_d3:
        st.metric("Rango temporal", f"{(df_f['fecha_consulta'].max() - df_f['fecha_consulta'].min()).days} días")

    st.markdown("<br/>", unsafe_allow_html=True)

    cols_show = ["fecha_consulta","ciudad","departamento","temperatura","temp_min",
                 "temp_max","humedad","presion","velocidad_viento","descripcion"]
    st.dataframe(
        df_f[cols_show].sort_values("fecha_consulta", ascending=False),
        use_container_width=True,
        height=500
    )

    csv = df_f.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar CSV completo",
        data=csv,
        file_name=f"clima_colombia_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

# ==============================
# FOOTER
# ==============================

st.markdown("""
<hr/>
<div style='text-align:center; color:#334455; font-size:0.75rem; padding:1rem 0;'>
    🌍 Análisis Climático Colombia · Datos: OpenWeatherMap API · 
    Construido con Streamlit + Plotly + PostgreSQL
</div>
""", unsafe_allow_html=True)