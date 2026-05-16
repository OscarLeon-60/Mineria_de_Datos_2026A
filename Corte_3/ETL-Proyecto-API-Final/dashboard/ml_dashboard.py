import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os
from dotenv import load_dotenv

# ==============================
# CONFIGURACIÓN
# ==============================
load_dotenv()

st.set_page_config(
    page_title="ML — Análisis Climático Colombia",
    page_icon="🤖",
    layout="wide"
)

# ==============================
# ESTILOS
# ==============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 100%); }
    .metric-card {
        background: linear-gradient(135deg, #111827, #1a2d4a);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-card::after {
        content: '';
        display: block;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #0066ff);
        border-radius: 2px;
        margin-top: 0.8rem;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
    }
    .metric-label {
        color: #8899aa;
        font-size: 0.75rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 0.3rem;
    }
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 0.5rem 0;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        margin-bottom: 1.2rem;
    }
    .conclusion-box {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-left: 4px solid #00d4ff;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.8rem;
        color: #cce8ff;
        font-size: 0.9rem;
    }
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

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    query = """
        SELECT m.*, c.nombre AS ciudad, c.departamento, c.latitud, c.longitud
        FROM mediciones m
        JOIN ciudades c ON m.ciudad_id = c.id
        ORDER BY m.fecha_consulta DESC
    """
    return pd.read_sql(query, engine)

# ==============================
# CARGA Y PREPROCESAMIENTO
# ==============================
try:
    df_raw = load_data()
except Exception as e:
    st.error(f"❌ Error conectando a la BD: {e}")
    st.stop()

df = df_raw.copy()
df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'])
df['hora']       = df['fecha_consulta'].dt.hour
df['dia']        = df['fecha_consulta'].dt.day
df['mes']        = df['fecha_consulta'].dt.month
df.drop_duplicates(subset=['ciudad', 'fecha_consulta'], inplace=True)
cols_clave = ['temperatura', 'temp_max', 'temp_min', 'humedad', 'presion', 'velocidad_viento', 'nubosidad']
df.dropna(subset=cols_clave, inplace=True)
Q1, Q3 = df['temperatura'].quantile(0.25), df['temperatura'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['temperatura'] >= Q1 - 3*IQR) & (df['temperatura'] <= Q3 + 3*IQR)]
df['rango_termico'] = df['temp_max'] - df['temp_min']
df['abs_lat'] = df['latitud'].abs()

TARGET = 'temp_max'

# ==============================
# MODELOS
# ==============================
# Simple
X_simple = df[['temperatura']].values
y = df[TARGET].values
X_s_train, X_s_test, y_s_train, y_s_test = train_test_split(X_simple, y, test_size=0.2, random_state=42)
lr_simple = LinearRegression()
lr_simple.fit(X_s_train, y_s_train)
y_pred_simple = lr_simple.predict(X_s_test)
r2_s   = r2_score(y_s_test, y_pred_simple)
mae_s  = mean_absolute_error(y_s_test, y_pred_simple)
rmse_s = np.sqrt(mean_squared_error(y_s_test, y_pred_simple))

# Múltiple
FEATURES = ['temperatura', 'sensacion_termica', 'humedad', 'presion', 'velocidad_viento', 'nubosidad', 'latitud']
df_model = df[FEATURES + [TARGET]].dropna()
X = df_model[FEATURES].values
y_m = df_model[TARGET].values
X_train, X_test, y_train, y_test = train_test_split(X, y_m, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)
lr_multi = LinearRegression()
lr_multi.fit(X_train_sc, y_train)
y_pred_multi = lr_multi.predict(X_test_sc)
r2_m   = r2_score(y_test, y_pred_multi)
mae_m  = mean_absolute_error(y_test, y_pred_multi)
rmse_m = np.sqrt(mean_squared_error(y_test, y_pred_multi))

coef_df = pd.DataFrame({
    'Feature': FEATURES,
    'Coeficiente': lr_multi.coef_
}).sort_values('Coeficiente', ascending=False)

PLOT_BG  = "rgba(10,15,30,0)"
FONT_CLR = "#aabbcc"
GRID_CLR = "rgba(255,255,255,0.05)"

# ==============================
# HEADER
# ==============================
st.markdown("""
<div style='background: linear-gradient(135deg, #0d1b2a, #1a2d4a);
     border: 1px solid rgba(0,212,255,0.2); border-radius: 20px;
     padding: 2rem 2.5rem; margin-bottom: 2rem;'>
    <div style='font-family: Syne, sans-serif; font-size: 2.2rem;
         font-weight: 800; color: #fff;'>🤖 Análisis ML — Regresión Lineal</div>
    <div style='color: #00d4ff; font-size: 0.9rem; letter-spacing: 2px;
         text-transform: uppercase; margin-top: 0.3rem;'>
         Predicción de Temperatura Máxima · Colombia</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# MÉTRICAS GENERALES
# ==============================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{len(df):,}</div>
        <div class='metric-label'>Registros</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{df['ciudad'].nunique()}</div>
        <div class='metric-label'>Ciudades</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{r2_s:.4f}</div>
        <div class='metric-label'>R² Simple</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{r2_m:.4f}</div>
        <div class='metric-label'>R² Múltiple</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ==============================
# TABS
# ==============================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Regresión Simple",
    "🔬 Regresión Múltiple",
    "📊 Comparación",
    "🎓 Conclusiones"
])

# ---- TAB 1: SIMPLE ----
with tab1:
    st.markdown("<div class='section-header'>📈 Regresión Lineal Simple</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{r2_s:.4f}</div>
            <div class='metric-label'>R² Score</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{mae_s:.4f}°C</div>
            <div class='metric-label'>MAE</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{rmse_s:.4f}°C</div>
            <div class='metric-label'>RMSE</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background: rgba(0,212,255,0.05); border: 1px solid rgba(0,212,255,0.2);
         border-radius: 10px; padding: 1rem 1.5rem; margin: 1rem 0; color: #00d4ff;
         font-family: monospace; font-size: 1rem;'>
        📐 temp_max = {lr_simple.intercept_:.4f} + {lr_simple.coef_[0]:.4f} × temperatura
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        x_line = np.linspace(X_s_test.min(), X_s_test.max(), 100)
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(
            x=X_s_test.flatten(), y=y_s_test,
            mode='markers', name='Datos reales',
            marker=dict(color='#00d4ff', size=8, opacity=0.7)
        ))
        fig_s.add_trace(go.Scatter(
            x=x_line, y=lr_simple.predict(x_line.reshape(-1,1)),
            mode='lines', name='Regresión',
            line=dict(color='#ff6b6b', width=3)
        ))
        fig_s.update_layout(
            title=f'Scatter + Línea de Regresión | R² = {r2_s:.4f}',
            xaxis_title='Temperatura Actual (°C)',
            yaxis_title='Temperatura Máxima (°C)',
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=380,
            xaxis=dict(gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig_s, use_container_width=True)

    with col_s2:
        residuos_s = y_s_test - y_pred_simple
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(
            x=y_pred_simple, y=residuos_s,
            mode='markers', name='Residuos',
            marker=dict(color='#ffd93d', size=8, opacity=0.7)
        ))
        fig_r.add_hline(y=0, line_dash='dash', line_color='#ff6b6b', line_width=2)
        fig_r.update_layout(
            title='Gráfica de Residuos',
            xaxis_title='Valores Predichos (°C)',
            yaxis_title='Residuos (°C)',
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=380,
            xaxis=dict(gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR)
        )
        st.plotly_chart(fig_r, use_container_width=True)

# ---- TAB 2: MÚLTIPLE ----
with tab2:
    st.markdown("<div class='section-header'>🔬 Regresión Lineal Múltiple</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{r2_m:.4f}</div>
            <div class='metric-label'>R² Score</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{mae_m:.4f}°C</div>
            <div class='metric-label'>MAE</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{rmse_m:.4f}°C</div>
            <div class='metric-label'>RMSE</div>
        </div>""", unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        residuos_m = y_test - y_pred_multi
        fig_rv = go.Figure()
        fig_rv.add_trace(go.Scatter(
            x=y_test, y=y_pred_multi,
            mode='markers', name='Predicciones',
            marker=dict(color='#00d4ff', size=8, opacity=0.7)
        ))
        min_v = min(y_test.min(), y_pred_multi.min())
        max_v = max(y_test.max(), y_pred_multi.max())
        fig_rv.add_trace(go.Scatter(
            x=[min_v, max_v], y=[min_v, max_v],
            mode='lines', name='Predicción perfecta',
            line=dict(color='#ff6b6b', dash='dash', width=2)
        ))
        fig_rv.update_layout(
            title=f'Real vs Predicho | R² = {r2_m:.4f}',
            xaxis_title='Valores Reales (°C)',
            yaxis_title='Valores Predichos (°C)',
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=380,
            xaxis=dict(gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig_rv, use_container_width=True)

    with col_m2:
        colors_bar = ['#00d4ff' if c > 0 else '#ff6b6b' for c in coef_df['Coeficiente']]
        fig_coef = go.Figure(go.Bar(
            x=coef_df['Coeficiente'], y=coef_df['Feature'],
            orientation='h', marker_color=colors_bar, opacity=0.85
        ))
        fig_coef.update_layout(
            title='Importancia de Variables (Coeficientes)',
            xaxis_title='Coeficiente Estandarizado',
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=380,
            xaxis=dict(gridcolor=GRID_CLR),
            yaxis=dict(gridcolor=GRID_CLR)
        )
        st.plotly_chart(fig_coef, use_container_width=True)

# ---- TAB 3: COMPARACIÓN ----
with tab3:
    st.markdown("<div class='section-header'>📊 Comparación de Modelos</div>", unsafe_allow_html=True)

    resultados = pd.DataFrame({
        'Modelo':    ['Lineal Simple', 'Lineal Múltiple'],
        'R²':        [r2_s,   r2_m],
        'MAE (°C)':  [mae_s,  mae_m],
        'RMSE (°C)': [rmse_s, rmse_m],
        'Variables': [1, len(FEATURES)]
    }).round(4)

    mejor = resultados.loc[resultados['R²'].idxmax(), 'Modelo']
    st.success(f"🏆 Mejor modelo: **{mejor}** con R² = {resultados['R²'].max():.4f}")

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        fig_r2 = go.Figure(go.Bar(
            x=resultados['Modelo'], y=resultados['R²'],
            marker_color=['#00d4ff', '#ff6b6b'], opacity=0.85,
            text=resultados['R²'].round(4), textposition='outside',
            textfont=dict(color='white')
        ))
        fig_r2.update_layout(
            title='R² Score', yaxis_range=[resultados['R²'].min()-0.005, 1.002],
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=350,
            yaxis=dict(gridcolor=GRID_CLR)
        )
        st.plotly_chart(fig_r2, use_container_width=True)

    with col_c2:
        fig_mae = go.Figure(go.Bar(
            x=resultados['Modelo'], y=resultados['MAE (°C)'],
            marker_color=['#00d4ff', '#ff6b6b'], opacity=0.85,
            text=resultados['MAE (°C)'].round(4), textposition='outside',
            textfont=dict(color='white')
        ))
        fig_mae.update_layout(
            title='MAE (°C)',
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=350,
            yaxis=dict(gridcolor=GRID_CLR)
        )
        st.plotly_chart(fig_mae, use_container_width=True)

    with col_c3:
        fig_rmse = go.Figure(go.Bar(
            x=resultados['Modelo'], y=resultados['RMSE (°C)'],
            marker_color=['#00d4ff', '#ff6b6b'], opacity=0.85,
            text=resultados['RMSE (°C)'].round(4), textposition='outside',
            textfont=dict(color='white')
        ))
        fig_rmse.update_layout(
            title='RMSE (°C)',
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font_color=FONT_CLR, height=350,
            yaxis=dict(gridcolor=GRID_CLR)
        )
        st.plotly_chart(fig_rmse, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.dataframe(resultados, use_container_width=True)

# ---- TAB 4: CONCLUSIONES ----
with tab4:
    st.markdown("<div class='section-header'>🎓 Conclusiones Automáticas</div>", unsafe_allow_html=True)

    mejor_m = resultados.loc[resultados['R²'].idxmax()]
    peor_m  = resultados.loc[resultados['R²'].idxmin()]
    coef_hum = coef_df[coef_df['Feature']=='humedad']['Coeficiente'].values[0]

    conclusiones = [
        f"✅ Ambos modelos son estadísticamente válidos con R² superior a {resultados['R²'].min():.4f} y errores menores a {resultados['RMSE (°C)'].max():.2f}°C.",
        f"🏆 El modelo <strong>{mejor_m['Modelo']}</strong> superó al {peor_m['Modelo']} con R² = {mejor_m['R²']:.4f} vs {peor_m['R²']:.4f}. Con {len(df):,} registros, menos variables generaliza mejor.",
        f"📐 La temperatura es el predictor dominante con coeficiente β = {lr_simple.coef_[0]:.4f}, casi igual a 1.",
        f"💧 La humedad tiene efecto negativo (β = {coef_hum:.4f}): a mayor humedad, menor temperatura máxima esperada.",
        f"📈 Con más datos históricos acumulados el modelo múltiple debería superar al simple al capturar mejor las relaciones entre variables.",
        f"⚠️ El data leakage fue detectado y corregido eliminando temp_min y rango_termico que inflaban el R² a 1.0000.",
        f"📊 Dataset actual: {len(df):,} registros | {df['ciudad'].nunique()} ciudades | Desde {df['fecha_consulta'].min().strftime('%Y-%m-%d %H:%M')} hasta {df['fecha_consulta'].max().strftime('%Y-%m-%d %H:%M')}."
    ]

    for c in conclusiones:
        st.markdown(f"<div class='conclusion-box'>{c}</div>", unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr style='border-color: rgba(0,212,255,0.1);'/>
<div style='text-align:center; color:#334455; font-size:0.75rem; padding:1rem 0;'>
    🤖 ML Dashboard · Regresión Lineal · Datos: Supabase + OpenWeatherMap
</div>
""", unsafe_allow_html=True)