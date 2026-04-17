import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
import streamlit.components.v1 as components
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# ML
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

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

components.html("""
<style>
    #toggle-btn {
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 999999;
        background: linear-gradient(135deg, #0d1b2a, #1a2d4a);
        border: 1px solid rgba(0, 212, 255, 0.4);
        border-radius: 8px;
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #00d4ff;
        font-size: 1.4rem;
        transition: all 0.2s ease;
    }
    #toggle-btn:hover {
        background: rgba(0, 212, 255, 0.15);
        border-color: #00d4ff;
        box-shadow: 0 0 12px rgba(0,212,255,0.3);
    }
</style>

<div id="toggle-btn" onclick="toggleSidebar()">☰</div>

<script>
function toggleSidebar() {
    // Busca el botón real de colapsar en el documento padre
    const buttons = window.parent.document.querySelectorAll('button');
    for (let btn of buttons) {
        if (btn.getAttribute('data-testid') === 'baseButton-headerNoPadding' ||
            btn.getAttribute('kind') === 'header' ||
            btn.closest('[data-testid="collapsedControl"]') ||
            btn.closest('[data-testid="stSidebarCollapseButton"]')) {
            btn.click();
            return;
        }
    }
    // Fallback: buscar por aria-label
    const allBtns = window.parent.document.querySelectorAll('button[aria-label]');
    for (let btn of allBtns) {
        const label = btn.getAttribute('aria-label').toLowerCase();
        if (label.includes('sidebar') || label.includes('collapse') || label.includes('expand')) {
            btn.click();
            return;
        }
    }
}
</script>
""", height=60)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #0a0f1e; }
    .stApp { background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a1628 100%); }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

    .header-container {
        background: linear-gradient(135deg, #0d1b2a, #1a2d4a);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 20px; padding: 2rem 2.5rem;
        margin-bottom: 2rem; position: relative; overflow: hidden;
    }
    .header-container::before {
        content: ''; position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(0,212,255,0.05) 0%, transparent 60%);
        pointer-events: none;
    }
    .header-title {
        font-family: 'Syne', sans-serif; font-size: 2.4rem;
        font-weight: 800; color: #ffffff; margin: 0; letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #00d4ff; font-size: 0.95rem; font-weight: 500;
        margin-top: 0.3rem; letter-spacing: 2px; text-transform: uppercase;
    }
    .header-badge {
        display: inline-block; background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3); color: #00d4ff;
        padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.75rem;
        font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-top: 1rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #111827, #1a2d4a);
        border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 16px;
        padding: 1.4rem 1.6rem; text-align: center; position: relative; overflow: hidden;
    }
    .kpi-card::after {
        content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #00d4ff, #0066ff); border-radius: 0 0 16px 16px;
    }
    .kpi-value { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; color: #ffffff; line-height: 1; }
    .kpi-label { color: #8899aa; font-size: 0.78rem; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 0.4rem; }
    .kpi-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .section-header {
        font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700;
        color: #ffffff; letter-spacing: 2px; text-transform: uppercase;
        padding: 0.5rem 0; border-bottom: 2px solid rgba(0, 212, 255, 0.3); margin-bottom: 1.2rem;
    }
    .alert-card {
        background: rgba(255, 60, 60, 0.08); border: 1px solid rgba(255, 60, 60, 0.3);
        border-left: 4px solid #ff3c3c; border-radius: 10px; padding: 0.8rem 1.2rem;
        margin-bottom: 0.6rem; color: #ffaaaa; font-size: 0.85rem;
    }
    .alert-card.humedad { background: rgba(0,150,255,0.08); border-color: rgba(0,150,255,0.3); border-left-color: #0096ff; color: #aaddff; }
    .alert-card.viento  { background: rgba(150,255,150,0.08); border-color: rgba(150,255,150,0.3); border-left-color: #96ff96; color: #aaffaa; }
    .alert-card.frio    { background: rgba(150,200,255,0.08); border-color: rgba(150,200,255,0.3); border-left-color: #96c8ff; color: #cce5ff; }
    .conclusion-box {
        background: rgba(0,212,255,0.05); border: 1px solid rgba(0,212,255,0.2);
        border-left: 4px solid #00d4ff; border-radius: 10px; padding: 1rem 1.5rem;
        margin-bottom: 0.8rem; color: #cce8ff; font-size: 0.9rem;
    }
    .ecuacion-box {
        background: rgba(0,212,255,0.05); border: 1px solid rgba(0,212,255,0.2);
        border-radius: 10px; padding: 1rem 1.5rem; margin: 1rem 0;
        color: #00d4ff; font-family: monospace; font-size: 1rem;
    }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a, #0a1220) !important; border-right: 1px solid rgba(0,212,255,0.1); }
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; font-family: 'DM Sans', sans-serif; font-weight: 500; color: #8899aa; }
    .stTabs [aria-selected="true"] { background: rgba(0,212,255,0.15) !important; color: #00d4ff !important; }
    hr { border-color: rgba(0,212,255,0.1) !important; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==============================
# CONEXIÓN BD
# ==============================

@st.cache_resource
def get_engine():
    try:
        host=st.secrets["DB_HOST"]; db=st.secrets["DB_NAME"]
        user=st.secrets["DB_USER"]; password=st.secrets["DB_PASSWORD"]; port=st.secrets["DB_PORT"]
    except:
        host=os.getenv("DB_HOST","localhost"); db=os.getenv("DB_NAME","clima_db")
        user=os.getenv("DB_USER","clima_user"); password=os.getenv("DB_PASSWORD","clima1234"); port=os.getenv("DB_PORT","5432")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    return pd.read_sql("""
        SELECT m.id, m.fecha_consulta, m.temperatura, m.temp_min, m.temp_max, m.sensacion_termica,
            m.humedad, m.presion, m.velocidad_viento, m.direccion_viento, m.descripcion, m.nubosidad,
            c.nombre AS ciudad, c.departamento, c.pais, c.latitud, c.longitud
        FROM mediciones m JOIN ciudades c ON m.ciudad_id = c.id
        ORDER BY m.fecha_consulta DESC
    """, engine)

@st.cache_data(ttl=300)
def load_alertas():
    engine = get_engine()
    return pd.read_sql("""
        SELECT a.*, c.nombre AS ciudad, c.departamento
        FROM alertas_climaticas a JOIN ciudades c ON a.ciudad_id = c.id
        ORDER BY a.fecha DESC LIMIT 100
    """, engine)

@st.cache_data(ttl=300)
def load_ultima_medicion():
    engine = get_engine()
    return pd.read_sql("""
        SELECT DISTINCT ON (c.id) c.nombre AS ciudad, c.departamento, c.latitud, c.longitud,
            m.temperatura, m.temp_min, m.temp_max, m.humedad, m.velocidad_viento,
            m.descripcion, m.nubosidad, m.fecha_consulta
        FROM mediciones m JOIN ciudades c ON m.ciudad_id = c.id
        ORDER BY c.id, m.fecha_consulta DESC
    """, engine)

# ==============================
# CARGA DE DATOS
# ==============================

try:
    df         = load_data()
    df_alertas = load_alertas()
    df_ultima  = load_ultima_medicion()
except Exception as e:
    st.error(f"⚠️ No se pudo conectar a la base de datos: {e}")
    st.stop()

# ==============================
# SIDEBAR
# ==============================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:3rem;'>🌦️</div>
        <div style='font-family: Syne, sans-serif; font-size:1.1rem; font-weight:800; color:#fff;'>Clima Colombia</div>
        <div style='color:#00d4ff; font-size:0.7rem; letter-spacing:2px; text-transform:uppercase; margin-top:4px;'>Dashboard Analítico</div>
    </div><hr/>
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
    st.markdown(f"""
    <div style='color:#556677; font-size:0.75rem; text-align:center;'>
        Última actualización<br/>
        <span style='color:#00d4ff;'>{df["fecha_consulta"].max().strftime('%d/%m/%Y %H:%M')}</span>
    </div>""", unsafe_allow_html=True)

# ==============================
# FILTRAR DATOS
# ==============================

df_f = df.copy()
if ciudad_sel:
    df_f = df_f[df_f["ciudad"].isin(ciudad_sel)]
df_f = df_f[(df_f["fecha_consulta"].dt.date >= fecha_ini) & (df_f["fecha_consulta"].dt.date <= fecha_fin)]

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
ciudad_max = df_ultima.loc[df_ultima["temperatura"].idxmax(), "ciudad"]
ciudad_min = df_ultima.loc[df_ultima["temperatura"].idxmin(), "ciudad"]

with col1: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>🌡️</div><div class='kpi-value'>{df_ultima["temperatura"].mean():.1f}°C</div><div class='kpi-label'>Temp. Promedio</div></div>""", unsafe_allow_html=True)
with col2: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>🔥</div><div class='kpi-value'>{df_ultima["temperatura"].max():.1f}°C</div><div class='kpi-label'>Más Caliente · {ciudad_max}</div></div>""", unsafe_allow_html=True)
with col3: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>🧊</div><div class='kpi-value'>{df_ultima["temperatura"].min():.1f}°C</div><div class='kpi-label'>Más Fría · {ciudad_min}</div></div>""", unsafe_allow_html=True)
with col4: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>💧</div><div class='kpi-value'>{df_ultima["humedad"].mean():.0f}%</div><div class='kpi-label'>Humedad Promedio</div></div>""", unsafe_allow_html=True)
with col5: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>⚠️</div><div class='kpi-value'>{len(df_alertas)}</div><div class='kpi-label'>Alertas Totales</div></div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ==============================
# TABS PRINCIPALES
# ==============================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️  Mapa en Vivo", "📈  Tendencias", "🔬  Análisis",
    "⚠️  Alertas", "📋  Datos Crudos", "🤖  Regresión Lineal"
])

PLOT_BG = PAPER_BG = "rgba(10,15,30,0)"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "#aabbcc"
ACCENT = "#00d4ff"

# ---- TAB 1: MAPA ----
with tab1:
    st.markdown("<div class='section-header'>🗺️ Temperatura Actual por Capital</div>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns([3, 1])
    with col_m1:
        var_mapa = st.radio("Variable a visualizar", ["temperatura","humedad","velocidad_viento"], horizontal=True,
            format_func=lambda x: {"temperatura":"🌡️ Temperatura","humedad":"💧 Humedad","velocidad_viento":"💨 Viento"}[x])
        color_scales = {"temperatura":"RdYlBu_r","humedad":"Blues","velocidad_viento":"Greens"}
        unidades     = {"temperatura":"°C","humedad":"%","velocidad_viento":"m/s"}
        fig_map = px.scatter_mapbox(df_ultima, lat="latitud", lon="longitud", color=var_mapa, size=var_mapa,
            size_max=25, hover_name="ciudad",
            hover_data={"departamento":True,"temperatura":":.1f","humedad":True,"velocidad_viento":":.1f","descripcion":True,"latitud":False,"longitud":False},
            color_continuous_scale=color_scales[var_mapa], mapbox_style="carto-darkmatter",
            zoom=4.5, center={"lat":4.5709,"lon":-74.2973},
            title=f"{var_mapa.replace('_',' ').title()} Actual ({unidades[var_mapa]})")
        fig_map.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font_color=FONT_COLOR,
            margin=dict(l=0,r=0,t=40,b=0), height=520,
            coloraxis_colorbar=dict(title=dict(text=unidades[var_mapa],font=dict(color=FONT_COLOR)),tickfont=dict(color=FONT_COLOR)))
        st.plotly_chart(fig_map, use_container_width=True)
    with col_m2:
        st.markdown("<div class='section-header'>🏆 Ranking</div>", unsafe_allow_html=True)
        ranking = df_ultima[["ciudad",var_mapa]].sort_values(var_mapa,ascending=False).reset_index(drop=True)
        ranking.index += 1; ranking.columns = ["Ciudad",unidades[var_mapa]]
        st.dataframe(ranking, use_container_width=True, height=480)

# ---- TAB 2: TENDENCIAS ----
with tab2:
    st.markdown("<div class='section-header'>📈 Evolución Temporal</div>", unsafe_allow_html=True)
    if df_f.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            fig_temp = px.line(df_f.sort_values("fecha_consulta"), x="fecha_consulta", y="temperatura", color="ciudad",
                title="🌡️ Temperatura (°C) por Ciudad", labels={"fecha_consulta":"Fecha","temperatura":"°C","ciudad":"Ciudad"})
            fig_temp.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=380,
                xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_temp, use_container_width=True)
        with col_t2:
            fig_hum = px.line(df_f.sort_values("fecha_consulta"), x="fecha_consulta", y="humedad", color="ciudad",
                title="💧 Humedad (%) por Ciudad", labels={"fecha_consulta":"Fecha","humedad":"%","ciudad":"Ciudad"})
            fig_hum.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=380,
                xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_hum, use_container_width=True)

        st.markdown("<div class='section-header'>📊 Temperatura Diaria (Min / Prom / Max)</div>", unsafe_allow_html=True)
        df_f["fecha"] = df_f["fecha_consulta"].dt.date
        df_diario = df_f.groupby("fecha").agg(temp_min=("temperatura","min"),temp_prom=("temperatura","mean"),temp_max=("temperatura","max")).reset_index()
        fig_band = go.Figure([
            go.Scatter(x=df_diario["fecha"],y=df_diario["temp_max"],fill=None,mode="lines",line=dict(color="rgba(255,100,100,0.8)",width=2),name="Máx"),
            go.Scatter(x=df_diario["fecha"],y=df_diario["temp_min"],fill="tonexty",mode="lines",line=dict(color="rgba(100,180,255,0.8)",width=2),fillcolor="rgba(0,212,255,0.08)",name="Mín"),
            go.Scatter(x=df_diario["fecha"],y=df_diario["temp_prom"],mode="lines+markers",line=dict(color=ACCENT,width=3),marker=dict(size=6,color=ACCENT),name="Promedio")
        ])
        fig_band.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=320,
            xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR,title="°C"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),hovermode="x unified")
        st.plotly_chart(fig_band, use_container_width=True)

        col_t3, col_t4 = st.columns(2)
        with col_t3:
            fig_viento = px.area(df_f.sort_values("fecha_consulta"),x="fecha_consulta",y="velocidad_viento",color="ciudad",
                title="💨 Velocidad del Viento (m/s)",labels={"fecha_consulta":"Fecha","velocidad_viento":"m/s"})
            fig_viento.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=320,
                xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_viento, use_container_width=True)
        with col_t4:
            fig_presion = px.line(df_f.sort_values("fecha_consulta"),x="fecha_consulta",y="presion",color="ciudad",
                title="🔵 Presión Atmosférica (hPa)",labels={"fecha_consulta":"Fecha","presion":"hPa"})
            fig_presion.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=320,
                xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_presion, use_container_width=True)

# ---- TAB 3: ANÁLISIS ----
with tab3:
    st.markdown("<div class='section-header'>🔬 Análisis Estadístico y Correlaciones</div>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        fig_box = px.box(df_f,x="ciudad",y="temperatura",color="ciudad",title="📦 Distribución de Temperaturas por Ciudad",labels={"temperatura":"°C","ciudad":""})
        fig_box.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=400,xaxis=dict(gridcolor=GRID_COLOR,tickangle=45),yaxis=dict(gridcolor=GRID_COLOR),showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
    with col_a2:
        fig_scatter = px.scatter(df_f,x="temperatura",y="humedad",color="ciudad",size="velocidad_viento",title="🔗 Temperatura vs Humedad",labels={"temperatura":"Temperatura (°C)","humedad":"Humedad (%)"},trendline="ols")
        fig_scatter.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=400,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_scatter, use_container_width=True)

    col_a3, col_a4 = st.columns(2)
    with col_a3:
        vars_corr = ["temperatura","temp_min","temp_max","humedad","presion","velocidad_viento","nubosidad"]
        corr = df_f[vars_corr].corr().round(2)
        fig_heat = go.Figure(data=go.Heatmap(z=corr.values,x=corr.columns,y=corr.index,colorscale="RdBu_r",zmid=0,text=corr.values,texttemplate="%{text}",textfont={"size":10},hoverongaps=False))
        fig_heat.update_layout(title="🔥 Matriz de Correlación",paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=400,xaxis=dict(tickangle=45))
        st.plotly_chart(fig_heat, use_container_width=True)
    with col_a4:
        ciudades_radar = df_ultima["ciudad"].tolist()[:8]
        df_radar = df_ultima[df_ultima["ciudad"].isin(ciudades_radar)]
        vars_radar = ["temperatura","humedad","velocidad_viento","nubosidad"]
        df_norm = df_radar[vars_radar].copy()
        for col in vars_radar:
            rng = df_norm[col].max()-df_norm[col].min()
            df_norm[col] = (df_norm[col]-df_norm[col].min())/(rng if rng!=0 else 1)
        fig_radar = go.Figure()
        for i, row in df_radar.iterrows():
            vals = df_norm.loc[i,vars_radar].tolist(); vals += [vals[0]]
            fig_radar.add_trace(go.Scatterpolar(r=vals,theta=vars_radar+[vars_radar[0]],fill="toself",name=row["ciudad"],opacity=0.6))
        fig_radar.update_layout(title="🕸️ Comparación Multivariable",polar=dict(radialaxis=dict(visible=True,color=FONT_COLOR),bgcolor="rgba(0,0,0,0)"),paper_bgcolor=PAPER_BG,font_color=FONT_COLOR,height=400,legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9)))
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<div class='section-header'>📊 Estadísticas Descriptivas</div>", unsafe_allow_html=True)
    st.dataframe(df_f[["temperatura","temp_min","temp_max","humedad","presion","velocidad_viento"]].describe().round(2), use_container_width=True)

# ---- TAB 4: ALERTAS ----
with tab4:
    st.markdown("<div class='section-header'>⚠️ Centro de Alertas Climáticas</div>", unsafe_allow_html=True)
    if df_alertas.empty:
        st.success("✅ Sin alertas registradas actualmente.")
    else:
        col_al1, col_al2 = st.columns([2,1])
        with col_al1:
            for _, row in df_alertas.head(20).iterrows():
                tipo = row["tipo_alerta"]
                css_class, icon = "", "⚠️"
                if "Temperatura" in tipo and "Alta" in tipo: icon = "🔥"
                elif "Temperatura" in tipo and "Baja" in tipo: css_class, icon = "frio", "🧊"
                elif "Humedad" in tipo: css_class, icon = "humedad", "💧"
                elif "Viento" in tipo: css_class, icon = "viento", "🌬️"
                st.markdown(f"""<div class='alert-card {css_class}'>{icon} <strong>{row['ciudad']}</strong> — {row['tipo_alerta']} &nbsp;·&nbsp; {row['descripcion']} &nbsp;·&nbsp; <span style='opacity:0.6'>{pd.to_datetime(row['fecha']).strftime('%d/%m %H:%M')}</span></div>""", unsafe_allow_html=True)
        with col_al2:
            conteo = df_alertas["tipo_alerta"].value_counts().reset_index(); conteo.columns = ["Tipo","Total"]
            fig_donut = px.pie(conteo,names="Tipo",values="Total",title="Distribución de Alertas",hole=0.55,color_discrete_sequence=["#ff4444","#0096ff","#96ff96","#96c8ff"])
            fig_donut.update_layout(paper_bgcolor=PAPER_BG,font_color=FONT_COLOR,height=350,legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_donut, use_container_width=True)
            por_ciudad = df_alertas["ciudad"].value_counts().head(10).reset_index(); por_ciudad.columns = ["Ciudad","Alertas"]
            fig_bar_al = px.bar(por_ciudad,x="Alertas",y="Ciudad",orientation="h",title="Top 10 ciudades con alertas",color="Alertas",color_continuous_scale="Reds")
            fig_bar_al.update_layout(paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=320,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),showlegend=False,coloraxis_showscale=False)
            st.plotly_chart(fig_bar_al, use_container_width=True)

# ---- TAB 5: DATOS CRUDOS ----
with tab5:
    st.markdown("<div class='section-header'>📋 Datos Crudos</div>", unsafe_allow_html=True)
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1: st.metric("Total registros", len(df_f))
    with col_d2: st.metric("Ciudades", df_f["ciudad"].nunique())
    with col_d3: st.metric("Rango temporal", f"{(df_f['fecha_consulta'].max()-df_f['fecha_consulta'].min()).days} días")
    st.markdown("<br/>", unsafe_allow_html=True)
    cols_show = ["fecha_consulta","ciudad","departamento","temperatura","temp_min","temp_max","humedad","presion","velocidad_viento","descripcion"]
    st.dataframe(df_f[cols_show].sort_values("fecha_consulta",ascending=False), use_container_width=True, height=500)
    st.download_button(label="⬇️ Descargar CSV completo", data=df_f.to_csv(index=False).encode("utf-8"),
        file_name=f"clima_colombia_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

# ---- TAB 6: REGRESIÓN LINEAL ----
with tab6:
    st.markdown("<div class='section-header'>🤖 Análisis de Regresión Lineal</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1,4])
    with col_btn1:
        if st.button("🔄 Re-ejecutar Modelo", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        st.markdown("""<div style='color:#8899aa;font-size:0.85rem;padding-top:0.6rem;'>
            El modelo se ejecuta automáticamente al abrir esta pestaña.
            Usa el botón para actualizar con los datos más recientes.</div>""", unsafe_allow_html=True)

    # Preprocesamiento ML
    df_ml = df.copy()
    df_ml['fecha_consulta'] = pd.to_datetime(df_ml['fecha_consulta'])
    df_ml.drop_duplicates(subset=['ciudad','fecha_consulta'], inplace=True)
    df_ml.dropna(subset=['temperatura','temp_max','temp_min','humedad','presion','velocidad_viento','nubosidad'], inplace=True)
    Q1_ml=df_ml['temperatura'].quantile(0.25); Q3_ml=df_ml['temperatura'].quantile(0.75); IQR_ml=Q3_ml-Q1_ml
    df_ml = df_ml[(df_ml['temperatura']>=Q1_ml-3*IQR_ml)&(df_ml['temperatura']<=Q3_ml+3*IQR_ml)]
    df_ml['rango_termico'] = df_ml['temp_max']-df_ml['temp_min']

    TARGET_ML   = 'temp_max'
    FEATURES_ML = ['temperatura','sensacion_termica','humedad','presion','velocidad_viento','nubosidad','latitud']

    # Simple
    X_s=df_ml[['temperatura']].values; y_s=df_ml[TARGET_ML].values
    X_s_tr,X_s_te,y_s_tr,y_s_te = train_test_split(X_s,y_s,test_size=0.2,random_state=42)
    lr_s=LinearRegression(); lr_s.fit(X_s_tr,y_s_tr); y_p_s=lr_s.predict(X_s_te)
    r2_s=r2_score(y_s_te,y_p_s); mae_s=mean_absolute_error(y_s_te,y_p_s); rmse_s=np.sqrt(mean_squared_error(y_s_te,y_p_s)); res_s=y_s_te-y_p_s

    # Múltiple
    df_m=df_ml[FEATURES_ML+[TARGET_ML]].dropna(); X_m=df_m[FEATURES_ML].values; y_m=df_m[TARGET_ML].values
    X_m_tr,X_m_te,y_m_tr,y_m_te = train_test_split(X_m,y_m,test_size=0.2,random_state=42)
    sc=StandardScaler(); X_m_tr_sc=sc.fit_transform(X_m_tr); X_m_te_sc=sc.transform(X_m_te)
    lr_m=LinearRegression(); lr_m.fit(X_m_tr_sc,y_m_tr); y_p_m=lr_m.predict(X_m_te_sc)
    r2_m=r2_score(y_m_te,y_p_m); mae_m=mean_absolute_error(y_m_te,y_p_m); rmse_m=np.sqrt(mean_squared_error(y_m_te,y_p_m)); res_m=y_m_te-y_p_m
    coef_df_ml=pd.DataFrame({'Feature':FEATURES_ML,'Coeficiente':lr_m.coef_}).sort_values('Coeficiente',ascending=False)
    mejor_ml = "Simple" if r2_s>=r2_m else "Múltiple"

    # KPIs ML
    st.markdown("<br/>", unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>📊</div><div class='kpi-value'>{len(df_ml):,}</div><div class='kpi-label'>Registros usados</div></div>""", unsafe_allow_html=True)
    with k2: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>📈</div><div class='kpi-value'>{r2_s:.4f}</div><div class='kpi-label'>R² Simple</div></div>""", unsafe_allow_html=True)
    with k3: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>🔬</div><div class='kpi-value'>{r2_m:.4f}</div><div class='kpi-label'>R² Múltiple</div></div>""", unsafe_allow_html=True)
    with k4: st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>🏆</div><div class='kpi-value'>{mejor_ml}</div><div class='kpi-label'>Mejor Modelo</div></div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Sub-pestañas ML
    ml1, ml2, ml3, ml4 = st.tabs(["📈 Simple","🔬 Múltiple","📊 Comparación","🎓 Conclusiones"])

    with ml1:
        st.markdown(f"""<div class='ecuacion-box'>
            📐 temp_max = {lr_s.intercept_:.4f} + {lr_s.coef_[0]:.4f} × temperatura
            &nbsp;|&nbsp; R² = {r2_s:.4f} &nbsp;|&nbsp; MAE = {mae_s:.4f}°C &nbsp;|&nbsp; RMSE = {rmse_s:.4f}°C
        </div>""", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            x_line = np.linspace(X_s_te.min(),X_s_te.max(),100)
            fig_s1 = go.Figure()
            fig_s1.add_trace(go.Scatter(x=X_s_te.flatten(),y=y_s_te,mode='markers',name='Datos reales',marker=dict(color='#00d4ff',size=8,opacity=0.7)))
            fig_s1.add_trace(go.Scatter(x=x_line,y=lr_s.predict(x_line.reshape(-1,1)),mode='lines',name='Regresión',line=dict(color='#ff6b6b',width=3)))
            fig_s1.update_layout(title=f'Scatter + Regresión | R² = {r2_s:.4f}',xaxis_title='Temperatura (°C)',yaxis_title='Temp. Máxima (°C)',
                paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=380,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_s1, use_container_width=True)
        with col_s2:
            fig_s2 = go.Figure()
            fig_s2.add_trace(go.Scatter(x=y_p_s,y=res_s,mode='markers',marker=dict(color='#ffd93d',size=8,opacity=0.7),name='Residuos'))
            fig_s2.add_hline(y=0,line_dash='dash',line_color='#ff6b6b',line_width=2)
            fig_s2.update_layout(title='Gráfica de Residuos',xaxis_title='Valores Predichos (°C)',yaxis_title='Residuos (°C)',
                paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=380,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_s2, use_container_width=True)
        fig_s3 = go.Figure()
        fig_s3.add_trace(go.Histogram(x=res_s,nbinsx=20,marker_color='#6bcb77',opacity=0.8))
        fig_s3.add_vline(x=0,line_dash='dash',line_color='yellow',line_width=2)
        fig_s3.add_vline(x=res_s.mean(),line_dash='dashdot',line_color='#ff6b6b',line_width=2,annotation_text=f'Media:{res_s.mean():.3f}',annotation_position='top right')
        fig_s3.update_layout(title='Distribución de Residuos',xaxis_title='Residuo (°C)',yaxis_title='Frecuencia',
            paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=300,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR))
        st.plotly_chart(fig_s3, use_container_width=True)

    with ml2:
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f"""<div class='kpi-card'><div class='kpi-value'>{r2_m:.4f}</div><div class='kpi-label'>R² Score</div></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class='kpi-card'><div class='kpi-value'>{mae_m:.4f}°C</div><div class='kpi-label'>MAE</div></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class='kpi-card'><div class='kpi-value'>{rmse_m:.4f}°C</div><div class='kpi-label'>RMSE</div></div>""", unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            fig_m1 = go.Figure()
            fig_m1.add_trace(go.Scatter(x=y_m_te,y=y_p_m,mode='markers',name='Predicciones',marker=dict(color='#00d4ff',size=8,opacity=0.7)))
            min_v,max_v = min(y_m_te.min(),y_p_m.min()),max(y_m_te.max(),y_p_m.max())
            fig_m1.add_trace(go.Scatter(x=[min_v,max_v],y=[min_v,max_v],mode='lines',name='Predicción perfecta',line=dict(color='#ff6b6b',dash='dash',width=2)))
            fig_m1.update_layout(title=f'Real vs Predicho | R² = {r2_m:.4f}',xaxis_title='Valores Reales (°C)',yaxis_title='Valores Predichos (°C)',
                paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=380,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR),legend=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_m1, use_container_width=True)
        with col_m2:
            colors_bar = ['#00d4ff' if c>0 else '#ff6b6b' for c in coef_df_ml['Coeficiente']]
            fig_m2 = go.Figure(go.Bar(x=coef_df_ml['Coeficiente'],y=coef_df_ml['Feature'],orientation='h',marker_color=colors_bar,opacity=0.85))
            fig_m2.update_layout(title='Importancia de Variables',xaxis_title='Coeficiente Estandarizado',
                paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=380,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_m2, use_container_width=True)
        col_m3, col_m4 = st.columns(2)
        with col_m3:
            fig_m3 = go.Figure()
            fig_m3.add_trace(go.Scatter(x=y_p_m,y=res_m,mode='markers',marker=dict(color='#6bcb77',size=8,opacity=0.7)))
            fig_m3.add_hline(y=0,line_dash='dash',line_color='#ff6b6b',line_width=2)
            fig_m3.add_hline(y=res_m.std(),line_dash='dot',line_color='gray',line_width=1)
            fig_m3.add_hline(y=-res_m.std(),line_dash='dot',line_color='gray',line_width=1)
            fig_m3.update_layout(title='Residuos vs Predichos',xaxis_title='Valores Predichos (°C)',yaxis_title='Residuos (°C)',
                paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=320,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_m3, use_container_width=True)
        with col_m4:
            fig_m4 = go.Figure()
            fig_m4.add_trace(go.Histogram(x=res_m,nbinsx=20,marker_color='#c77dff',opacity=0.8))
            fig_m4.add_vline(x=0,line_dash='dash',line_color='yellow',line_width=2)
            fig_m4.update_layout(title='Distribución de Residuos — Múltiple',xaxis_title='Residuo (°C)',yaxis_title='Frecuencia',
                paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=320,xaxis=dict(gridcolor=GRID_COLOR),yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_m4, use_container_width=True)

    with ml3:
        resultados_ml = pd.DataFrame({
            'Modelo':['Lineal Simple','Lineal Múltiple'],
            'R²':[r2_s,r2_m],'MAE (°C)':[mae_s,mae_m],'RMSE (°C)':[rmse_s,rmse_m],'Variables':[1,len(FEATURES_ML)]
        }).round(4)
        st.success(f"🏆 Mejor modelo: **{mejor_ml}** con R² = {max(r2_s,r2_m):.4f}")
        col_c1,col_c2,col_c3 = st.columns(3)
        with col_c1:
            fig_c1 = go.Figure(go.Bar(x=resultados_ml['Modelo'],y=resultados_ml['R²'],marker_color=['#00d4ff','#ff6b6b'],opacity=0.85,text=resultados_ml['R²'].round(4),textposition='outside',textfont=dict(color='white')))
            fig_c1.update_layout(title='R² Score',yaxis_range=[resultados_ml['R²'].min()-0.005,1.002],paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=350,yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_c1, use_container_width=True)
        with col_c2:
            fig_c2 = go.Figure(go.Bar(x=resultados_ml['Modelo'],y=resultados_ml['MAE (°C)'],marker_color=['#00d4ff','#ff6b6b'],opacity=0.85,text=resultados_ml['MAE (°C)'].round(4),textposition='outside',textfont=dict(color='white')))
            fig_c2.update_layout(title='MAE (°C)',paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=350,yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_c2, use_container_width=True)
        with col_c3:
            fig_c3 = go.Figure(go.Bar(x=resultados_ml['Modelo'],y=resultados_ml['RMSE (°C)'],marker_color=['#00d4ff','#ff6b6b'],opacity=0.85,text=resultados_ml['RMSE (°C)'].round(4),textposition='outside',textfont=dict(color='white')))
            fig_c3.update_layout(title='RMSE (°C)',paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,font_color=FONT_COLOR,height=350,yaxis=dict(gridcolor=GRID_COLOR))
            st.plotly_chart(fig_c3, use_container_width=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        st.dataframe(resultados_ml, use_container_width=True)

    with ml4:
        coef_hum = coef_df_ml[coef_df_ml['Feature']=='humedad']['Coeficiente'].values[0]
        peor_nombre = "Lineal Múltiple" if r2_s>=r2_m else "Lineal Simple"
        conclusiones = [
            f"✅ Ambos modelos son estadísticamente válidos con R² superior a {min(r2_s,r2_m):.4f} y errores menores a {max(rmse_s,rmse_m):.2f}°C.",
            f"🏆 El modelo <strong>{mejor_ml}</strong> superó al {peor_nombre} con R² = {max(r2_s,r2_m):.4f} vs {min(r2_s,r2_m):.4f}. Con {len(df_ml):,} registros, menos variables generaliza mejor.",
            f"📐 La temperatura es el predictor dominante con coeficiente β = {lr_s.coef_[0]:.4f}, casi igual a 1.",
            f"💧 La humedad tiene efecto negativo (β = {coef_hum:.4f}): a mayor humedad, menor temperatura máxima esperada.",
            f"📈 Con más datos históricos acumulados el modelo múltiple debería superar al simple al capturar mejor las relaciones entre variables.",
            f"⚠️ El data leakage fue detectado y corregido eliminando temp_min y rango_termico que inflaban el R² a 1.0000.",
            f"📊 Dataset actual: {len(df_ml):,} registros | {df_ml['ciudad'].nunique()} ciudades | Desde {df_ml['fecha_consulta'].min().strftime('%Y-%m-%d %H:%M')} hasta {df_ml['fecha_consulta'].max().strftime('%Y-%m-%d %H:%M')}."
        ]
        for c in conclusiones:
            st.markdown(f"<div class='conclusion-box'>{c}</div>", unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================

st.markdown("""
<hr/>
<div style='text-align:center; color:#334455; font-size:0.75rem; padding:1rem 0;'>
    🌍 Análisis Climático Colombia · Datos: OpenWeatherMap API ·
    Construido con Streamlit + Plotly + PostgreSQL + Scikit-learn
</div>
""", unsafe_allow_html=True)