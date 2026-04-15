# Análisis Climático de Colombia

Proyecto ETL para monitorear, almacenar y visualizar datos climáticos en tiempo real de varias ciudades colombianas desde OpenWeather. Este sistema está diseñado para capturar información de ciudades y departamentos de Colombia, guardarla en PostgreSQL, generar alertas climáticas y ofrecer un dashboard interactivo con análisis y modelos de predicción.

## Objetivo

Construir un flujo de datos confiable que permita:
- Extraer datos meteorológicos de ciudades colombianas cada hora.
- Transformar y normalizar la información en un esquema de base de datos relacional.
- Cargar mediciones en PostgreSQL con registro histórico.
- Visualizar patrones de temperatura, humedad y viento en un dashboard Streamlit.
- Evaluar tendencias de temperatura usando regresión lineal.

## Qué se incluye

- `etl/extractor.py`: script Python que consulta la API de OpenWeather, procesa los datos y guarda ciudades + mediciones en PostgreSQL.
- `etl/schema.sql`: definición de tablas para `ciudades`, `mediciones` y `alertas_climaticas`.
- `Dockerfile.etl`: construcción de la imagen para el servicio ETL.
- `Dockerfile.dashboard`: construcción de la imagen para el dashboard Streamlit.
- `docker-compose.yml`: orquestación de servicios PostgreSQL, ETL y dashboard.
- `dashboard/`: carpeta con el código del dashboard Streamlit.
- `data/`: volumen local opcional para datos intermedios.
- `logs/`: registros de ejecución del extractor.
- `requirements.txt`: dependencias Python necesarias.

## Arquitectura de la solución

1. `POSTGRESQL` en Docker: almacena información de ciudades, mediciones históricas y alertas.
2. `ETL` en Docker: ejecuta el extractor, consume OpenWeather y persiste los datos.
3. `Dashboard` en Docker: visualiza los datos desde PostgreSQL a través de Streamlit.

## Estructura de la base de datos

- `ciudades`: registros únicos de cada ciudad con nombre, país, coordenadas y departamento.
- `mediciones`: histórico de observaciones por ciudad con temperatura, humedad, viento y descripción.
- `alertas_climaticas`: eventos generados cuando se detectan condiciones críticas o anomalías.

## Setup local

1. Crear archivo `.env` en la raíz con las variables:
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

3. Levantar la base de datos y servicios con Docker Compose:
```bash
docker compose up -d postgres
```

4. Ejecutar el extractor localmente:
```bash
python etl/extractor.py
```

5. Verificar resultados:
- `SELECT * FROM ciudades LIMIT 10;`
- `SELECT * FROM mediciones ORDER BY fecha_consulta DESC LIMIT 10;`

## Cómo evoluciona el proyecto

A partir de esta base puedes ampliar el sistema con:
- cobertura de más ciudades y departamentos de Colombia
- generador de alertas por extremos de temperatura, humedad o velocidad de viento
- dashboard con mapas interactivos y series de tiempo
- modelo de regresión lineal para predecir temperatura máxima y mínima
- informes y presentación para mostrar hallazgos y recomendaciones

## Sugerencias de análisis

- detectar anomalías climáticas por ciudad
- comparar patrones estacionales
- predecir temperatura máxima y mínima
- analizar correlación entre temperatura, humedad y viento

## Nota

El extractor está configurado para consultar datos de varias ciudades y departamentos de Colombia. Para ampliar el análisis, ajusta la lista de `CITIES` en `etl/extractor.py` con más ciudades colombianas según lo necesario.
