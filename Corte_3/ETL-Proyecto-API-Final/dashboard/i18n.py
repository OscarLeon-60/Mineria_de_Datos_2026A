"""Presentation-only translations; database fields remain unchanged."""

import re


FIELD_NAMES = {
    "id": "ID",
    "fecha_consulta": "Observation time",
    "fecha": "Date",
    "ciudad": "City",
    "departamento": "Department",
    "pais": "Country",
    "latitud": "Latitude",
    "longitud": "Longitude",
    "temperatura": "Temperature",
    "temp_min": "Minimum temperature",
    "temp_max": "Maximum temperature",
    "temp_prom": "Average temperature",
    "sensacion_termica": "Feels like",
    "humedad": "Humidity",
    "presion": "Pressure",
    "velocidad_viento": "Wind speed",
    "direccion_viento": "Wind direction",
    "descripcion": "Description",
    "nubosidad": "Cloudiness",
    "abs_lat": "Absolute latitude",
    "hora": "Hour",
}

WEATHER = {
    "cielo claro": "clear sky",
    "algo de nubes": "few clouds",
    "nubes dispersas": "scattered clouds",
    "nubes dispersas: 25-50%": "scattered clouds: 25-50%",
    "nubes: 51-84%": "broken clouds: 51-84%",
    "nubes: 85-100%": "overcast clouds: 85-100%",
    "nubes": "clouds",
    "muy nuboso": "broken clouds",
    "nubes rotas": "broken clouds",
    "nubes cubiertas": "overcast clouds",
    "lluvia ligera": "light rain",
    "lluvia moderada": "moderate rain",
    "lluvia intensa": "heavy rain",
    "lluvia de gran intensidad": "heavy intensity rain",
    "lluvia muy fuerte": "very heavy rain",
    "lluvia extrema": "extreme rain",
    "lluvia helada": "freezing rain",
    "chubasco ligero": "light shower rain",
    "chubasco": "shower rain",
    "chubasco de gran intensidad": "heavy shower rain",
    "chubasco irregular": "ragged shower rain",
    "lluvia": "rain",
    "llovizna": "drizzle",
    "llovizna ligera": "light drizzle",
    "llovizna de intensidad ligera": "light drizzle",
    "llovizna de gran intensidad": "heavy drizzle",
    "lluvia ligera de llovizna": "light drizzle rain",
    "lluvia de llovizna": "drizzle rain",
    "lluvia intensa de llovizna": "heavy drizzle rain",
    "tormenta": "thunderstorm",
    "tormenta con lluvia": "thunderstorm with rain",
    "tormenta con lluvia ligera": "thunderstorm with light rain",
    "tormenta con lluvia intensa": "thunderstorm with heavy rain",
    "tormenta ligera": "light thunderstorm",
    "tormenta fuerte": "heavy thunderstorm",
    "tormenta irregular": "ragged thunderstorm",
    "tormenta con llovizna ligera": "thunderstorm with light drizzle",
    "tormenta con llovizna": "thunderstorm with drizzle",
    "tormenta con llovizna intensa": "thunderstorm with heavy drizzle",
    "niebla": "fog",
    "neblina": "mist",
    "bruma": "haze",
    "humo": "smoke",
    "polvo": "dust",
    "nieve": "snow",
    "nieve ligera": "light snow",
    "nieve intensa": "heavy snow",
    "aguanieve": "sleet",
    "lluvia y nieve": "rain and snow",
}

ALERTS = {
    "Alta Temperatura": "High temperature",
    "Baja Temperatura": "Low temperature",
    "Alta Humedad": "High humidity",
    "Viento Fuerte": "Strong wind",
}

ALERT_DESCRIPTIONS = {
    "Temperatura extrema": "Extreme temperature",
    "Temperatura muy baja": "Very low temperature",
    "Humedad extrema": "Extreme humidity",
    "Velocidad de viento": "Wind speed",
}


def translate_text(spanish, english, language):
    return english if language == "en" else spanish


def field_name(name, language):
    return FIELD_NAMES.get(name, name) if language == "en" else name


def weather_description(value, language):
    if language != "en" or not isinstance(value, str):
        return value
    return WEATHER.get(value.lower(), value)


def alert_type(value, language):
    return ALERTS.get(value, value) if language == "en" else value


def alert_description(value, language):
    if language != "en" or not isinstance(value, str):
        return value
    for spanish, english in ALERT_DESCRIPTIONS.items():
        if re.match(rf"^{re.escape(spanish)}:", value):
            return english + value[len(spanish):]
    return value


def display_frame(frame, language):
    result = frame.copy()
    if "descripcion" in result.columns:
        result["descripcion"] = result["descripcion"].map(
            lambda value: weather_description(value, language)
        )
    return result.rename(columns=lambda column: field_name(column, language))
