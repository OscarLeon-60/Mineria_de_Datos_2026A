#!/usr/bin/env python3
import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging
import time

# ==============================
# Cargar variables de entorno
# ==============================
load_dotenv()

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
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==============================
# Clase Extractor
# ==============================
class WeatherstackExtractor:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.base_url = os.getenv('WEATHERSTACK_BASE_URL')
        ciudades_env = os.getenv('CIUDADES')

        if not ciudades_env:
            raise ValueError("CIUDADES no configuradas en .env")

        self.ciudades = ciudades_env.split(',')

        if not self.api_key:
            raise ValueError("API_KEY no configurada en .env")

        if not self.base_url:
            raise ValueError("WEATHERSTACK_BASE_URL no configurada en .env")

    def extraer_clima(self, ciudad):
        try:
            url = f"{self.base_url}/current"
            params = {
                'access_key': self.api_key,
                'query': ciudad.strip()
            }

            for intento in range(3):
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 429:
                    logger.warning(f"Rate limit alcanzado para {ciudad}. Esperando 5 segundos...")
                    time.sleep(5)
                    continue

                response.raise_for_status()
                break
            else:
                logger.error(f"No se pudo obtener datos para {ciudad} después de 3 intentos")
                return None

            data = response.json()

            if 'error' in data:
                logger.error(f"Error en API para {ciudad}: {data['error'].get('info', 'Error desconocido')}")
                return None

            logger.info(f"Datos extraídos para {ciudad}")
            return data

        except Exception as e:
            logger.error(f"Error extrayendo datos para {ciudad}: {str(e)}")
            return None

    def procesar_respuesta(self, response_data):
        try:
            current = response_data.get('current', {})
            location = response_data.get('location', {})

            return {
                'ciudad': location.get('name'),
                'pais': location.get('country'),
                'latitud': location.get('lat'),
                'longitud': location.get('lon'),
                'temperatura': current.get('temperature'),
                'sensacion_termica': current.get('feelslike'),
                'humedad': current.get('humidity'),
                'velocidad_viento': current.get('wind_speed'),
                'descripcion': current.get('weather_descriptions', ['N/A'])[0],
                'fecha_extraccion': datetime.now().isoformat(),
                'codigo_tiempo': current.get('weather_code')
            }

        except Exception as e:
            logger.error(f"Error procesando respuesta: {str(e)}")
            return None

    def ejecutar_extraccion(self):
        datos_extraidos = []

        logger.info(f"Iniciando extracción para {len(self.ciudades)} ciudades...")

        for ciudad in self.ciudades:
            response = self.extraer_clima(ciudad)
            if response:
                datos_procesados = self.procesar_respuesta(response)
                if datos_procesados:
                    datos_extraidos.append(datos_procesados)

        return datos_extraidos


# ==============================
# Main
# ==============================
if __name__ == "__main__":
    try:
        extractor = WeatherstackExtractor()
        datos = extractor.ejecutar_extraccion()

        # Guardar JSON
        with open('data/clima_raw.json', 'w') as f:
            json.dump(datos, f, indent=2)

        logger.info("Datos guardados en data/clima_raw.json")

        # Guardar CSV
        df = pd.DataFrame(datos)
        df.to_csv('data/clima.csv', index=False)

        logger.info("Datos guardados en data/clima.csv")

        print("\n" + "=" * 50)
        print("RESUMEN DE EXTRACCIÓN")
        print("=" * 50)
        print(df.to_string())
        print("=" * 50)

    except Exception as e:
        logger.error(f"Error en extracción: {str(e)}")