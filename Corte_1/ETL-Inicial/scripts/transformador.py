#!/usr/bin/env python3
# transformador.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import logging

# ==============================
# Crear carpetas necesarias
# ==============================
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ==============================
# Configurar logging
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/transformador.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==============================
# Transformador
# ==============================
class TransformadorClima:

    def __init__(self, archivo_csv):
        self.archivo_csv = archivo_csv

    def cargar_datos(self):
        logger.info("Cargando datos desde CSV...")
        df = pd.read_csv(self.archivo_csv)
        return df

    def transformar(self, df):
        logger.info("Transformando datos...")

        # Eliminar filas con temperatura nula
        df = df.dropna(subset=["temperatura"])

        # Convertir columnas numéricas
        columnas_numericas = [
            "temperatura",
            "sensacion_termica",
            "humedad",
            "velocidad_viento"
        ]

        for col in columnas_numericas:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Ordenar por temperatura descendente
        df = df.sort_values(by="temperatura", ascending=False)

        logger.info("Transformación completada")
        return df

    def generar_grafica(self, df):
        logger.info("Generando gráfica...")

        plt.figure()
        plt.bar(df["ciudad"], df["temperatura"])
        plt.xlabel("Ciudad")
        plt.ylabel("Temperatura (°C)")
        plt.title("Temperatura Actual por Ciudad")
        plt.xticks(rotation=45)

        ruta_imagen = "data/clima_analysis.png"

        plt.tight_layout()
        plt.savefig(ruta_imagen)
        plt.close()

        logger.info(f"Imagen guardada en {ruta_imagen}")

# ==============================
# Main
# ==============================
if __name__ == "__main__":
    try:
        transformador = TransformadorClima(
            "data/clima.csv"
        )

        df = transformador.cargar_datos()
        df_transformado = transformador.transformar(df)

        transformador.generar_grafica(df_transformado)

        print("\nTransformación completada ✅")
        print("Imagen generada en data/clima_analysis.png")

    except Exception as e:
        logger.error(f"Error en transformación: {str(e)}")