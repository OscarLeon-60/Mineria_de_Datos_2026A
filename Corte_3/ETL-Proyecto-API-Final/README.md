# 🌤️ Análisis Climático de Colombia

> Sistema ETL automatizado para monitoreo climático en tiempo real de las capitales departamentales de Colombia, utilizando procesos ETL, visualización interactiva y modelos de Machine Learning para análisis predictivo y clasificación climática.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mineriadedatos2026a-yqzsgkv8rhyyavuayccwfv.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automatizado-green)

---

# Enlace del Video Explicando cada Punto y Formato Excel

https://drive.google.com/drive/folders/1wW5vYyT1CbZajV1jG1Fi82AZz7YWTvi3?usp=sharing

# 📌 Descripción del Proyecto

Este proyecto implementa un sistema ETL automatizado para la extracción, transformación y carga de datos meteorológicos de las capitales departamentales de Colombia utilizando APIs climáticas en tiempo real.

La información recolectada es almacenada en PostgreSQL mediante Supabase y posteriormente analizada mediante técnicas de Machine Learning como:

- Regresión Lineal
- Árbol de Decisión para Regresión
- Regresión Logística Binaria
- Árbol de Decisión para Clasificación Binaria

Además, se desarrolló un dashboard interactivo en Streamlit para visualizar variables climáticas, tendencias históricas y resultados de modelos predictivos.

---

# 🎯 Justificación del Proyecto

El cambio climático ha generado variaciones importantes en las condiciones meteorológicas a nivel mundial, afectando diferentes regiones de Colombia mediante cambios de temperatura, lluvias intensas, sequías y fenómenos extremos.

Debido a esto, surge la necesidad de contar con herramientas tecnológicas que permitan recolectar, almacenar, analizar y visualizar datos climáticos en tiempo real para facilitar la toma de decisiones y el análisis de patrones ambientales.

Este proyecto busca integrar procesos ETL, almacenamiento en la nube, visualización interactiva y técnicas de Machine Learning para construir una solución automatizada capaz de monitorear variables climáticas en múltiples ciudades colombianas.

Además, el proyecto permite aplicar conocimientos de minería de datos, análisis estadístico, automatización y modelos predictivos sobre datos reales obtenidos desde APIs meteorológicas.

---

# 🎯 Objetivo General

Desarrollar un sistema ETL automatizado para el monitoreo climático de Colombia, integrando almacenamiento en la nube, visualización interactiva y modelos de Machine Learning para análisis predictivo y clasificación climática.

---

# 🎯 Objetivos Específicos

- Extraer datos climáticos automáticamente desde APIs meteorológicas.
- Transformar y normalizar los datos para análisis estadístico.
- Almacenar información histórica en PostgreSQL mediante Supabase.
- Visualizar datos climáticos en tiempo real con Streamlit.
- Implementar modelos de regresión y clasificación.
- Analizar correlaciones y patrones climáticos en Colombia.

---

# 🧠 Arquitectura de la Solución

```text
OpenWeatherMap API
        ↓
 extractor.py (ETL)
        ↓
 GitHub Actions
        ↓
 Supabase PostgreSQL
        ↓
 Streamlit Dashboard
        ↓
 Machine Learning
```

---

# ⚙️ Metodología Implementada

El proyecto fue desarrollado bajo una metodología ETL dividida en tres etapas principales:

## 1. Extracción

Se consumen datos meteorológicos desde la API de OpenWeatherMap para múltiples ciudades colombianas.

## 2. Transformación

Los datos son limpiados, normalizados y estructurados para facilitar su almacenamiento y análisis.

## 3. Carga

La información transformada es almacenada en PostgreSQL utilizando Supabase como servicio en la nube.

Posteriormente se aplicaron técnicas de Machine Learning para regresión y clasificación utilizando Scikit-learn.

---

# 📦 Estructura del Proyecto

```text
ETL-Proyecto-API-Final/
│
├── dashboard/
│   └── app.py
│
├── etl/
│   ├── extractor.py
│   └── schema.sql
│
├── notebooks/
│   ├── Regresion_Lineal/
│   ├── Arbol_Regresion/
│   ├── Regresion_Logistica/
│   └── Arbol_Clasificacion/
│
├── data/
├── logs/
├── ml/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🗄️ Base de Datos

## Tablas principales

| Tabla | Descripción |
|---|---|
| ciudades | Información de ciudades monitoreadas |
| mediciones | Datos climáticos históricos |
| alertas_climaticas | Registro de alertas automáticas |

---

# 🌡️ Variables Climáticas

Las principales variables utilizadas son:

- temperatura
- temp_min
- temp_max
- humedad
- presion
- velocidad_viento
- direccion_viento
- sensacion_termica
- nubosidad
- descripcion_clima

---

# 📊 Dashboard Interactivo

El sistema cuenta con un dashboard desarrollado en Streamlit que permite:

- Visualizar mapas climáticos en tiempo real
- Analizar tendencias históricas
- Consultar alertas climáticas
- Explorar correlaciones
- Visualizar resultados de Machine Learning

---

# 🤖 Modelos de Machine Learning

## 📈 Regresión Lineal

Modelo utilizado para predecir temperaturas máximas utilizando variables climáticas relacionadas.

### Métricas utilizadas

- R²
- MAE
- MSE
- RMSE

---

## 🌳 Árbol de Decisión para Regresión

Modelo utilizado para mejorar la predicción de variables numéricas mediante divisiones jerárquicas de los datos.

### Características

- Mejor manejo de relaciones no lineales
- Evaluación mediante profundidad del árbol
- Uso de GridSearchCV para hiperparámetros

---

## 🔵 Regresión Logística Binaria

Modelo de clasificación binaria utilizado para determinar condiciones climáticas como:

- Soleado / No Soleado
- Lluvia / No Lluvia

### Métricas utilizadas

- Accuracy
- Precision
- Recall
- F1-Score
- Matriz de Confusión

---

## 🌳 Árbol de Decisión para Clasificación

Modelo utilizado para clasificar estados climáticos utilizando reglas de decisión.

### Características

- Criterios Gini y Entropy
- Clasificación binaria
- Interpretación visual sencilla

---

# ⚡ Valor Agregado Implementado

## Oversampling con Resample

Se aplicó balanceo de clases utilizando técnicas de oversampling para evitar sesgos en clasificación binaria.

## GridSearchCV

Se utilizó GridSearchCV para optimizar hiperparámetros como:

- max_depth
- min_samples_split
- criterion
- splitter

---

# 📈 Resultados del Proyecto

- Automatización completa del proceso ETL.
- Monitoreo climático de ciudades colombianas.
- Dashboard interactivo funcional en la nube.
- Modelos de regresión con alta precisión.
- Modelos de clasificación binaria implementados correctamente.
- Balanceo de clases mediante oversampling.
- Optimización de modelos con GridSearchCV.

---

# 📦 Productos Generados

Durante el desarrollo del proyecto se generaron los siguientes productos:

- Sistema ETL automatizado para extracción climática.
- Base de datos PostgreSQL en Supabase.
- Dashboard interactivo en Streamlit Cloud.
- Notebook de Regresión Lineal.
- Notebook de Árbol de Decisión para Regresión.
- Notebook de Regresión Logística Binaria.
- Notebook de Árbol de Decisión para Clasificación.
- Modelos entrenados de Machine Learning.
- Repositorio GitHub documentado.
- Automatización mediante GitHub Actions.

---

# 🧪 Tecnologías Utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Desarrollo principal |
| PostgreSQL | Base de datos |
| Supabase | Base de datos en la nube |
| Streamlit | Dashboard |
| Scikit-learn | Machine Learning |
| Pandas | Procesamiento de datos |
| Plotly | Visualización |
| Docker | Contenedores |
| GitHub Actions | Automatización |

---

# ☁️ Despliegue

## Servicios utilizados

| Servicio | Plataforma |
|---|---|
| Base de datos | Supabase |
| Dashboard | Streamlit Cloud |
| Automatización | GitHub Actions |

---

# 🚀 Ejecución Local

## Crear entorno virtual

```bash
python -m venv venv
```

## Activar entorno virtual

### Windows

```bash
venv\Scripts\activate
```

### Linux / WSL

```bash
source venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar ETL

```bash
python etl/extractor.py
```

## Ejecutar Dashboard

```bash
streamlit run dashboard/app.py
```

---

# 📚 Conclusiones

El proyecto permitió integrar procesos ETL, bases de datos en la nube y técnicas de Machine Learning para realizar análisis climático automatizado sobre ciudades colombianas.

Los modelos implementados permitieron realizar predicciones numéricas y clasificaciones binarias con resultados satisfactorios, mejorando la comprensión de patrones climáticos y facilitando el análisis de datos meteorológicos en tiempo real.

---

# 👨‍💻 Autor

Proyecto desarrollado para la asignatura de Minería de Datos 2026A.

Alan Zapata
Oscar Fabián León Triana