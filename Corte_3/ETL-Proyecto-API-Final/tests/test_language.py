import sys
import unittest
import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "dashboard"))

from i18n import alert_description, alert_type, display_frame, weather_description


def sample_data():
    rows = []
    for i in range(40):
        rows.append({
            "id": i,
            "fecha_consulta": pd.Timestamp("2026-01-01") + pd.Timedelta(hours=i),
            "temperatura": 20 + i / 10,
            "temp_min": 18 + i / 10,
            "temp_max": 22 + i / 10 + (i % 3) / 10,
            "sensacion_termica": 19 + i / 10,
            "humedad": 60 + i % 10,
            "presion": 1000 + i % 7,
            "velocidad_viento": 2 + i % 5,
            "direccion_viento": 180,
            "descripcion": "cielo claro",
            "nubosidad": 10 + i % 15,
            "ciudad": "Bogotá" if i % 2 else "Medellín",
            "departamento": "Cundinamarca" if i % 2 else "Antioquia",
            "pais": "Colombia",
            "latitud": 4.7 if i % 2 else 6.2,
            "longitud": -74.0 if i % 2 else -75.5,
        })
    data = pd.DataFrame(rows)
    alerts = pd.DataFrame([{
        "ciudad": "Bogotá", "tipo_alerta": "Alta Temperatura",
        "descripcion": "Temperatura extrema: 36°C",
        "fecha": pd.Timestamp("2026-01-02"),
    }])
    return data, alerts


class TranslationTests(unittest.TestCase):
    def test_external_values_and_original_data(self):
        frame = pd.DataFrame({"ciudad": ["Bogotá"], "descripcion": ["cielo claro"]})
        translated = display_frame(frame, "en")
        self.assertEqual(translated.iloc[0].to_dict(), {"City": "Bogotá", "Description": "clear sky"})
        self.assertEqual(frame.iloc[0]["descripcion"], "cielo claro")
        self.assertEqual(weather_description("descripción desconocida", "en"), "descripción desconocida")
        self.assertEqual(alert_type("Alta Temperatura", "en"), "High temperature")
        self.assertEqual(alert_description("Temperatura extrema: 36°C", "en"), "Extreme temperature: 36°C")
        self.assertEqual(alert_description("Temperatura extrema: 36°C", "es"), "Temperatura extrema: 36°C")

    def test_language_switch_preserves_filters_and_translates_dashboard(self):
        data, alerts = sample_data()

        def read_sql(query, engine):
            if "alertas_climaticas" in query:
                return alerts.copy()
            if "DISTINCT ON" in query:
                return data.drop_duplicates("ciudad").copy()
            return data.copy()

        st.cache_data.clear()
        st.cache_resource.clear()
        with patch("sqlalchemy.create_engine", return_value=object()), patch("pandas.read_sql", side_effect=read_sql):
            app = AppTest.from_file(str(PROJECT / "dashboard" / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception, str(app.exception))
            self.assertIn("🗺️  Mapa en Vivo", [tab.label for tab in app.tabs])
            app.selectbox(key="department").select("Antioquia").run()
            self.assertFalse(app.exception, str(app.exception))
            app.radio(key="map_variable").set_value("humedad").run()
            self.assertFalse(app.exception, str(app.exception))
            app.selectbox(key="language").select("en").run()
            self.assertFalse(app.exception, str(app.exception))
            self.assertEqual(app.selectbox(key="department").value, "Antioquia")
            self.assertEqual(app.radio(key="map_variable").value, "humedad")
            self.assertIn("🗺️  Live Map", [tab.label for tab in app.tabs])
            self.assertIn("🤖  Linear Regression", [tab.label for tab in app.tabs])
            markdown = "\n".join(element.value for element in app.markdown)
            self.assertIn("Colombia Climate Analysis", markdown)
            self.assertIn("High temperature", markdown)
            self.assertIn("Extreme temperature: 36°C", markdown)
            self.assertIn("Linear Regression Analysis", markdown)
            figures = [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")]
            self.assertIn("Current Humidity (%)", figures[0]["layout"]["title"]["text"])
            self.assertTrue(any("Correlation Matrix" in figure["layout"].get("title", {}).get("text", "") for figure in figures))
            tables = [element.value for element in app.dataframe]
            self.assertTrue(any("Description" in table.columns and "clear sky" in table["Description"].values for table in tables))
            app.selectbox(key="language").select("es").run()
            self.assertFalse(app.exception, str(app.exception))
            self.assertEqual(app.selectbox(key="department").value, "Antioquia")
            self.assertIn("🗺️  Mapa en Vivo", [tab.label for tab in app.tabs])

    def test_language_selector_works_when_database_is_unavailable(self):
        st.cache_data.clear()
        st.cache_resource.clear()
        with patch("sqlalchemy.create_engine", return_value=object()), patch("pandas.read_sql", side_effect=RuntimeError("offline")):
            app = AppTest.from_file(str(PROJECT / "dashboard" / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception, str(app.exception))
            self.assertIn("No se pudo conectar", app.error[0].value)
            app.selectbox(key="language").select("en").run()
            self.assertFalse(app.exception, str(app.exception))
            self.assertIn("Could not connect", app.error[0].value)


if __name__ == "__main__":
    unittest.main()
