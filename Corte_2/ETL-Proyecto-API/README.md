# 🌤️ Análisis Climático de Colombia
> Sistema ETL automatizado para monitoreo climático en tiempo real de las 31 capitales departamentales de Colombia, con dashboard interactivo, modelo de regresión lineal y despliegue en la nube.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mineriadedatos2026a-e8anvqzyxjnfbdb45z5vdn.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automatizado-green)

---

## 🎯 Objetivo
Construir un sistema ETL sólido que permita:
- Extraer datos meteorológicos de las 31 capitales colombianas cada 5 minutos de forma automatizada.
- Transformar y normalizar la información para una base de datos relacional.
- Guardar mediciones históricas en PostgreSQL (Supabase).
- Visualizar tendencias de temperatura, humedad y viento en un dashboard Streamlit interactivo.
- Detectar anomalías climáticas y generar alertas automáticas.
- Predecir la temperatura máxima usando modelos de regresión lineal simple y múltiple.

---

## 🧠 Arquitectura de la Solución

```
OpenWeatherMap API
        ↓
  extractor.py (ETL)
        ↓
  GitHub Actions (cada 5 min)
        ↓
  Supabase PostgreSQL (nube)
        ↓
  Streamlit Cloud (dashboard)
```

**Flujo completo:**
1. GitHub Actions ejecuta `extractor.py` cada 5 minutos automáticamente
2. El extractor llama a la API de OpenWeatherMap para las 31 capitales
3. Los datos se limpian, transforman y cargan en Supabase (PostgreSQL)
4. El dashboard de Streamlit Cloud lee los datos y los visualiza en tiempo real
5. Docker Compose permite correr todo el sistema localmente con un solo comando

---

## 📦 Estructura del Proyecto

```
ETL-Proyecto-API/
├── .github/
│   └── workflows/
│       └── etl_scheduler.yml     # GitHub Actions — ETL automático cada 5 min
├── dashboard/
│   └── app.py                    # Dashboard Streamlit con 6 pestañas
├── etl/
│   ├── extractor.py              # Script ETL principal
│   └── schema.sql                # Esquema de la base de datos
├── notebooks/
│   └── analisis_climatico_ml.ipynb  # Análisis ML con regresión lineal
├── data/                         # Datos intermedios y CSV exportados
├── logs/                         # Registros de ejecución del ETL
├── ml/                           # Modelos entrenados (.pkl)
├── Dockerfile.etl                # Imagen Docker para el ETL
├── Dockerfile.dashboard          # Imagen Docker para el dashboard
├── docker-compose.yml            # Orquestación de servicios
├── scheduler.py                  # Scheduler local (sin Docker)
├── requirements.txt              # Dependencias Python
└── .env                          # Variables de entorno (no subir a Git)
```

---

## 🗄️ Base de Datos

### Tablas

| Tabla | Descripción |
|---|---|
| `ciudades` | Nombre, departamento, país, latitud y longitud de cada capital |
| `mediciones` | Historial de observaciones climáticas por ciudad cada 5 minutos |
| `alertas_climaticas` | Eventos cuando se detectan condiciones extremas |

### Variables climáticas almacenadas
`temperatura`, `temp_min`, `temp_max`, `sensacion_termica`, `humedad`, `presion`, `velocidad_viento`, `direccion_viento`, `descripcion`, `nubosidad`

### Alertas automáticas
- 🔥 **Calor extremo**: temperatura > 35°C
- 🧊 **Frío extremo**: temperatura < 5°C
- 💧 **Humedad alta**: humedad > 90%
- 🌬️ **Viento fuerte**: velocidad > 15 m/s

---

## 📊 Dashboard

**URL:** https://mineriadedatos2026a-yqzsgkv8rhyyavuayccwfv.streamlit.app/

| Pestaña | Contenido |
|---|---|
| 🗺️ Mapa en Vivo | Mapa interactivo de Colombia con temperatura, humedad o viento |
| 📈 Tendencias | Evolución temporal de variables climáticas por ciudad |
| 🔬 Análisis | Matriz de correlación, boxplot, scatter, radar chart |
| ⚠️ Alertas | Centro de alertas con distribución y ranking por ciudad |
| 📋 Datos Crudos | Tabla filtrable con descarga CSV |
| 🤖 Regresión Lineal | Modelos Simple y Múltiple con gráficas y conclusiones automáticas |

---

## 🤖 Modelos de Machine Learning

### Regresión Lineal Simple
- **Variable predictora:** temperatura actual
- **Variable objetivo:** temp_max
- **Ecuación:** `temp_max = β₀ + β₁ × temperatura`
- **R² obtenido:** ~0.9995 (99.95% varianza explicada)
- **MAE:** ~0.12°C

### Regresión Lineal Múltiple
- **Variables predictoras:** temperatura, sensación térmica, humedad, presión, velocidad del viento, nubosidad, latitud
- **Variable objetivo:** temp_max
- **R² obtenido:** ~0.9925

### Métricas de evaluación
| Métrica | Descripción |
|---|---|
| R² | Coeficiente de determinación — % de varianza explicada |
| MAE | Error Absoluto Medio en °C |
| RMSE | Raíz del Error Cuadrático Medio en °C |

> ⚠️ **Nota:** Se detectó y corrigió data leakage al eliminar `temp_min` y `rango_termico` que derivaban matemáticamente de `temp_max`.

---

## 🚀 Setup Local

### Requisitos previos
- Python 3.12+
- Docker Desktop
- Git

### Paso 1 — Clonar el repositorio
```bash
git clone https://github.com/OscarLeon-60/Mineria_de_Datos_2026A.git
cd Mineria_de_Datos_2026A/Corte_2/ETL-Proyecto-API
```

### Paso 2 — Crear el archivo `.env`
```env
OPENWEATHER_API_KEY=tu_api_key
DB_HOST=localhost
DB_NAME=clima_db
DB_USER=clima_user
DB_PASSWORD=clima1234
DB_PORT=5432
```

### Paso 3 — Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Paso 4 — Levantar con Docker Compose
```bash
docker compose up --build
```
Esto levanta PostgreSQL, crea las tablas automáticamente, ejecuta el ETL y lanza el dashboard en `http://localhost:8501`

### Paso 5 — O ejecutar manualmente sin Docker
```bash
# Iniciar PostgreSQL local
sudo service postgresql start

# Crear tablas
psql -U clima_user -d clima_db -h localhost -p 5434 -f etl/schema.sql

# Ejecutar ETL una vez
python3 etl/extractor.py

# Ejecutar ETL cada hora automáticamente
python3 scheduler.py

# Lanzar dashboard
streamlit run dashboard/app.py
```

### Paso 6 — Verificar datos en la BD
```sql
SELECT * FROM ciudades LIMIT 10;
SELECT * FROM mediciones ORDER BY fecha_consulta DESC LIMIT 10;
SELECT * FROM alertas_climaticas ORDER BY fecha DESC LIMIT 10;
```

---

## ☁️ Despliegue en la Nube

| Servicio | Plataforma | URL |
|---|---|---|
| Base de datos | Supabase (PostgreSQL) | aws-1-us-west-2.pooler.supabase.com |
| Dashboard | Streamlit Cloud | Ver badge arriba |
| ETL automatizado | GitHub Actions | Cada 5 minutos |

### Configurar secrets en GitHub Actions
Ve a **Settings → Secrets → Actions** y agrega:
```
OPENWEATHER_API_KEY
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

### Configurar secrets en Streamlit Cloud
Ve a **Settings → Secrets** y agrega:
```toml
OPENWEATHER_API_KEY = "tu_api_key"
DB_HOST = "tu_host_supabase"
DB_PORT = "6543"
DB_NAME = "postgres"
DB_USER = "postgres.tu_usuario"
DB_PASSWORD = "tu_password"
```

---

## 🌆 Ciudades Monitoreadas
Las 31 capitales departamentales de Colombia:

| Departamento | Capital | Departamento | Capital |
|---|---|---|---|
| Amazonas | Leticia | Nariño | Pasto |
| Antioquia | Medellín | Norte de Santander | Cúcuta |
| Arauca | Arauca | Quindío | Armenia |
| Atlántico | Barranquilla | Risaralda | Pereira |
| Bolívar | Cartagena | San Andrés y Providencia | San Andrés |
| Boyacá | Tunja | Santander | Bucaramanga |
| Caldas | Manizales | Sucre | Sincelejo |
| Caquetá | Florencia | Tolima | Ibagué |
| Casanare | Yopal | Valle del Cauca | Cali |
| Cauca | Popayán | Vaupés | Mitú |
| Cesar | Valledupar | Vichada | Puerto Carreño |
| Chocó | Quibdó | Cundinamarca | Bogotá |
| Córdoba | Montería | Guainía | Inírida |
| Guaviare | San José del Guaviare | Meta | Villavicencio |
| Huila | Neiva | La Guajira | Riohacha |
| Magdalena | Santa Marta | | |

---

## 💡 Ideas de Análisis
- Detectar anomalías climáticas por ciudad y departamento
- Comparar patrones climáticos entre regiones (costa, altiplano, Amazonía)
- Predecir temperatura máxima y mínima con modelos de ML
- Analizar correlaciones entre temperatura, humedad, presión y viento
- Identificar ciudades con mayor frecuencia de alertas climáticas

---

## 📚 Tecnologías Usadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal |
| PostgreSQL 15 | Base de datos relacional |
| Supabase | PostgreSQL en la nube |
| Streamlit | Dashboard web |
| Plotly | Gráficas interactivas |
| Scikit-learn | Modelos de ML |
| Docker / Docker Compose | Contenedores y orquestación |
| GitHub Actions | Automatización del ETL |
| OpenWeatherMap API | Fuente de datos climáticos |
| Jupyter Notebook | Análisis exploratorio y ML |

---

## ✅ Nota Final
El proyecto está configurado para trabajar con las 31 capitales colombianas. Si deseas agregar más municipios, modifica la lista `CITIES` en `etl/extractor.py` con nuevas entradas en formato `("Ciudad,CO", "Departamento", "Nombre Display")`.

---

*Proyecto desarrollado para la asignatura de Minería de Datos 2026A*
