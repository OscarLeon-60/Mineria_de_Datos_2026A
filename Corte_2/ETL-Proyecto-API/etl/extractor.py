import requests
import os
import pandas as pd
import logging
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# ==============================
# RUTAS
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ==============================
# CONFIGURACIÓN
# ==============================

load_dotenv(os.path.join(BASE_DIR, ".env"))
API_KEY = os.getenv("OPENWEATHER_API_KEY")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "clima_db"),
    "user":     os.getenv("DB_USER", "clima_user"),
    "password": os.getenv("DB_PASSWORD", "clima1234"),
    "port":     int(os.getenv("DB_PORT", 5432))
}

log_filename = os.path.join(LOGS_DIR, "clima_colombia.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("🚀 INICIANDO PROCESO ETL")
logging.info("===== INICIO DEL PROCESO ETL =====")

CITIES = [
    ("Leticia,CO",               "Amazonas",                 "Leticia"),
    ("Medellin,CO",              "Antioquia",                "Medellín"),
    ("Arauca,CO",                "Arauca",                   "Arauca"),
    ("Barranquilla,CO",          "Atlántico",                "Barranquilla"),
    ("Cartagena,CO",             "Bolívar",                  "Cartagena"),
    ("Tunja,CO",                 "Boyacá",                   "Tunja"),
    ("Manizales,CO",             "Caldas",                   "Manizales"),
    ("Florencia,CO",             "Caquetá",                  "Florencia"),
    ("Yopal,CO",                 "Casanare",                 "Yopal"),
    ("Popayan,CO",               "Cauca",                    "Popayán"),
    ("Valledupar,CO",            "Cesar",                    "Valledupar"),
    ("Quibdo,CO",                "Chocó",                    "Quibdó"),
    ("Monteria,CO",              "Córdoba",                  "Montería"),
    ("Bogota,CO",                "Cundinamarca",             "Bogotá"),
    ("Inirida,CO",               "Guainía",                  "Inírida"),
    ("San Jose del Guaviare,CO", "Guaviare",                 "San José del Guaviare"),
    ("Neiva,CO",                 "Huila",                    "Neiva"),
    ("Riohacha,CO",              "La Guajira",               "Riohacha"),
    ("Santa Marta,CO",           "Magdalena",                "Santa Marta"),
    ("Villavicencio,CO",         "Meta",                     "Villavicencio"),
    ("Pasto,CO",                 "Nariño",                   "Pasto"),
    ("Cucuta,CO",                "Norte de Santander",       "Cúcuta"),
    ("Armenia,CO",               "Quindío",                  "Armenia"),
    ("Pereira,CO",               "Risaralda",                "Pereira"),
    ("San Andres,CO",            "San Andrés y Providencia", "San Andrés"),
    ("Bucaramanga,CO",           "Santander",                "Bucaramanga"),
    ("Sincelejo,CO",             "Sucre",                    "Sincelejo"),
    ("Ibague,CO",                "Tolima",                   "Ibagué"),
    ("Cali,CO",                  "Valle del Cauca",          "Cali"),
    ("Mitu,CO",                  "Vaupés",                   "Mitú"),
    ("Puerto Carreno,CO",        "Vichada",                  "Puerto Carreño"),
]

try:
    conexion = psycopg2.connect(**DB_CONFIG)
    cursor = conexion.cursor()
    print("✅ Conectado a PostgreSQL")
    logging.info("Conectado a PostgreSQL")
except Exception as e:
    print(f"❌ No se pudo conectar a PostgreSQL: {e}")
    logging.critical(f"Fallo conexión BD: {e}")
    exit(1)

data_list           = []
ciudades_procesadas = 0
alertas_generadas   = 0
errores             = 0

for city_api, departamento, display_name in CITIES:
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city_api}&appid={API_KEY}&units=metric&lang=es"
        )
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            nombre_ciudad  = data["name"]
            temperatura    = data["main"]["temp"]
            temp_min       = data["main"]["temp_min"]
            temp_max       = data["main"]["temp_max"]
            sensacion      = data["main"]["feels_like"]
            humedad        = data["main"]["humidity"]
            presion        = data["main"]["pressure"]
            viento         = data["wind"]["speed"]
            dir_viento     = data["wind"].get("deg", 0)
            descripcion    = data["weather"][0]["description"]
            nubosidad      = data["clouds"]["all"]
            latitud        = data["coord"]["lat"]
            longitud       = data["coord"]["lon"]

            # ✅ Fecha en hora Colombia (UTC-5) sin timezone info para BD
            fecha_consulta = datetime.now(tz=ZoneInfo("America/Bogota")).replace(tzinfo=None)

            print(f"✔ {display_name:<30} | {temperatura:>5.1f}°C | Humedad: {humedad}% | Viento: {viento} m/s | {fecha_consulta:%Y-%m-%d %H:%M:%S}")
            logging.info(f"{display_name} - Temp:{temperatura} TMin:{temp_min} TMax:{temp_max} Hum:{humedad} Viento:{viento}")

            data_list.append({
                "fecha_consulta":    fecha_consulta,
                "ciudad":            nombre_ciudad,
                "departamento":      departamento,
                "pais":              "Colombia",
                "latitud":           latitud,
                "longitud":          longitud,
                "temperatura":       temperatura,
                "temp_min":          temp_min,
                "temp_max":          temp_max,
                "sensacion_termica": sensacion,
                "humedad":           humedad,
                "presion":           presion,
                "velocidad_viento":  viento,
                "direccion_viento":  dir_viento,
                "descripcion":       descripcion,
                "nubosidad":         nubosidad,
            })

            cursor.execute(
                "SELECT id FROM ciudades WHERE nombre = %s AND departamento = %s",
                (nombre_ciudad, departamento)
            )
            resultado = cursor.fetchone()

            if resultado:
                ciudad_id = resultado[0]
            else:
                cursor.execute(
                    """
                    INSERT INTO ciudades (nombre, departamento, pais, latitud, longitud)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (nombre_ciudad, departamento, "Colombia", latitud, longitud)
                )
                ciudad_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO mediciones (
                    ciudad_id, fecha_consulta,
                    temperatura, temp_min, temp_max, sensacion_termica,
                    humedad, presion,
                    velocidad_viento, direccion_viento,
                    descripcion, nubosidad
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ciudad_id, fecha_consulta,
                    temperatura, temp_min, temp_max, sensacion,
                    humedad, presion,
                    viento, dir_viento,
                    descripcion, nubosidad
                )
            )

            if temperatura > 35:
                print(f"   🔥 ALERTA: Calor extremo en {display_name} ({temperatura}°C)")
                cursor.execute(
                    "INSERT INTO alertas_climaticas (ciudad_id, fecha, tipo_alerta, descripcion) VALUES (%s, %s, %s, %s)",
                    (ciudad_id, fecha_consulta, "Alta Temperatura", f"Temperatura extrema: {temperatura}°C")
                )
                alertas_generadas += 1

            if temperatura < 5:
                print(f"   🧊 ALERTA: Frío extremo en {display_name} ({temperatura}°C)")
                cursor.execute(
                    "INSERT INTO alertas_climaticas (ciudad_id, fecha, tipo_alerta, descripcion) VALUES (%s, %s, %s, %s)",
                    (ciudad_id, fecha_consulta, "Baja Temperatura", f"Temperatura muy baja: {temperatura}°C")
                )
                alertas_generadas += 1

            if humedad > 90:
                print(f"   💧 ALERTA: Humedad alta en {display_name} ({humedad}%)")
                cursor.execute(
                    "INSERT INTO alertas_climaticas (ciudad_id, fecha, tipo_alerta, descripcion) VALUES (%s, %s, %s, %s)",
                    (ciudad_id, fecha_consulta, "Alta Humedad", f"Humedad extrema: {humedad}%")
                )
                alertas_generadas += 1

            if viento > 15:
                print(f"   🌬️  ALERTA: Viento fuerte en {display_name} ({viento} m/s)")
                cursor.execute(
                    "INSERT INTO alertas_climaticas (ciudad_id, fecha, tipo_alerta, descripcion) VALUES (%s, %s, %s, %s)",
                    (ciudad_id, fecha_consulta, "Viento Fuerte", f"Velocidad de viento: {viento} m/s")
                )
                alertas_generadas += 1

            ciudades_procesadas += 1

        else:
            print(f"❌ Error HTTP {response.status_code} en {display_name}")
            logging.error(f"HTTP {response.status_code} - {city_api}")
            errores += 1

    except requests.exceptions.ConnectionError:
        print(f"⚠ Sin conexión para {display_name}")
        logging.error(f"ConnectionError - {city_api}")
        conexion.rollback()
        errores += 1

    except Exception as e:
        conexion.rollback()
        print(f"⚠ Error en {display_name}: {e}")
        logging.error(f"Error en {city_api}: {e}")
        errores += 1

df = pd.DataFrame(data_list)
output_path = os.path.join(DATA_DIR, "clima_colombia.csv")

if not df.empty:
    if os.path.exists(output_path):
        df.to_csv(output_path, mode="a", header=False, index=False)
    else:
        df.to_csv(output_path, index=False)
    print("\n✅ Datos guardados/actualizados en CSV")
    logging.info("Datos guardados en CSV")
else:
    print("\n⚠ No hay datos para guardar en CSV")

conexion.commit()
cursor.close()
conexion.close()

print("\n===================================")
print(f"  Ciudades procesadas : {ciudades_procesadas}/{len(CITIES)}")
print(f"  Alertas generadas   : {alertas_generadas}")
print(f"  Errores             : {errores}")
print("  🚀 PROCESO ETL FINALIZADO")
print("===================================\n")

logging.info(f"Total ciudades: {ciudades_procesadas}")
logging.info(f"Total alertas: {alertas_generadas}")
logging.info(f"Total errores: {errores}")
logging.info("===== FIN DEL PROCESO ETL =====")