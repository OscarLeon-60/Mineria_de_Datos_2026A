# 🌤️ Análisis Climático de Colombia

Bienvenido al proyecto de monitoreo climático para ciudades y departamentos de Colombia. Aquí se recopilan datos en tiempo real desde OpenWeather, se almacenan en PostgreSQL y se exploran con un dashboard interactivo.

## 🎯 Objetivo

Construir un sistema ETL sólido que permita:
- Extraer datos meteorológicos de varias ciudades colombianas cada hora.
- Transformar y normalizar la información para una base de datos relacional.
- Guardar mediciones históricas en PostgreSQL.
- Visualizar tendencias de temperatura, humedad y viento en un dashboard Streamlit.
- Analizar patrones y posibles anomalías climáticas.

## 📦 Qué incluye este proyecto

- `etl/extractor.py`: script Python que consulta OpenWeather y guarda ciudades + mediciones en PostgreSQL.
- `etl/schema.sql`: esquema de base de datos para `ciudades`, `mediciones` y `alertas_climaticas`.
- `Dockerfile.etl`: imagen para el servicio ETL.
- `Dockerfile.dashboard`: imagen para el dashboard Streamlit.
- `docker-compose.yml`: orquesta PostgreSQL, ETL y dashboard.
- `dashboard/`: código del dashboard.
- `data/`: datos intermedios opcionales.
- `logs/`: registros de ejecución del extractor.
- `requirements.txt`: dependencias necesarias.

## 🧠 Arquitectura de la solución

1. **PostgreSQL** en Docker: persiste ciudades, mediciones y alertas.
2. **ETL**: extrae datos de OpenWeather y los carga en la base.
3. **Dashboard**: visualiza los datos desde PostgreSQL con Streamlit.

## � Despliegue y herramientas

En esta etapa trabajamos con **Supabase** como plataforma de backend y **Streamlit** para desplegar el dashboard. Supabase permite gestionar la base de datos PostgreSQL y almacenar datos en la nube, mientras que Streamlit ofrece una interfaz de visualización rápida y profesional.

## �🗄️ Estructura de la base de datos

- `ciudades`: almacena cada ciudad con nombre, departamento, país y coordenadas.
- `mediciones`: historial de observaciones climáticas por ciudad.
- `alertas_climaticas`: registra eventos cuando se detectan condiciones inusuales.

## 🚀 Setup local

1. Crear el archivo `.env` en la raíz con:
```text
OPENWEATHER_API_KEY=tu_api_key
DB_NAME=clima_db
DB_USER=clima_user
DB_PASSWORD=clima1234
DB_PORT=5432
```

2. Crear entorno virtual e instalar dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Levantar PostgreSQL con Docker Compose:
```bash
docker compose up -d postgres
```

4. Ejecutar el extractor:
```bash
python etl/extractor.py
```

5. Verificar que los datos llegaron a la base:
```sql
SELECT * FROM ciudades LIMIT 10;
SELECT * FROM mediciones ORDER BY fecha_consulta DESC LIMIT 10;
```

## 🌆 Enfoque del proyecto

Este proyecto está centrado en el análisis climático de **ciudades y departamentos de Colombia**. El objetivo es mostrar cómo se puede seguir el clima en tiempo real y analizar variaciones dentro del país.

## 📊 Posibles ampliaciones

- Más ciudades y departamentos de Colombia.
- Alertas por picos de temperatura, humedad o viento.
- Dashboard con gráficos de tendencia y mapas.
- Modelos de regresión lineal para predecir temperatura mínima y máxima.
- Informe final con hallazgos y recomendaciones.

## 💡 Ideas de análisis

- Detectar anomalías climáticas por ciudad.
- Comparar patrones de clima entre departamentos.
- Predecir temperatura máxima y mínima.
- Analizar correlaciones entre temperatura, humedad y viento.

## ✅ Nota final

El proyecto ya está configurado para trabajar con ciudades colombianas. Si deseas sumar más municipios, solo modifica la lista `CITIES` en `etl/extractor.py` con nuevas entradas dentro de Colombia.
