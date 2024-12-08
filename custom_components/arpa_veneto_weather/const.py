"""Constants for Arpa Veneto Weather component."""

DOMAIN = "arpa_veneto_weather"

API_BASE = "https://api.arpa.veneto.it/REST/v1"

SENSOR_TYPES = {
    "temperature": {
        "name": "Temperature",
        "unit": "°C",
        "device_class": "temperature",
    },
    "humidity": {
        "name": "Humidity",
        "unit": "%",
        "device_class": "humidity",
    },
    "visibility": {
        "name": "Visibility",
        "unit": "m",
        "device_class": "visibility",
    },
    "precipitation": {
        "name": "Precipitation",
        "unit": "&",
        "device_class": "precipitation",
    },
    "wind_bearing": {
        "name": "Wind bearing",
        "unit": "°",
        "device_class": "precipitation",
    },
    "wind_speed": {
        "name": "Wind speed",
        "unit": "m/s",
    },
}
