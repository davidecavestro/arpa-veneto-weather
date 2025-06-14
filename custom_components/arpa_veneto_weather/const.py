"""Constants for Arpa Veneto Weather component."""

DOMAIN = "arpa_veneto_weather"

KEY_COORDINATOR = "coordinator"
KEY_UNSUBSCRIBER = "options_unsubscriber"

API_BASE = "https://api.arpa.veneto.it/REST/v1"

CONF_EXPOSE_FORECAST_JSON = "expose_forecast_json"
CONF_EXPOSE_FORECAST_RAW = "expose_forecast_raw"

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
        "unit": "km",
        "device_class": "visibility",
    },
    "precipitation": {
        "name": "Precipitation",
        "unit": "mm",
        "device_class": "precipitation",
    },
    "precipitation_probability": {
        "name": "Precipitation probability",
        "unit": "%",
        "device_class": "probability",
    },
    "wind_bearing": {
        "name": "Wind bearing",
        "device_class": "direction",
    },
    "wind_speed": {
        "name": "Wind speed",
        "unit": "km/h",
        "device_class": "wind",
    },
    "uv_index": {
        "name": "UV index",
        "unit": "UV index",
        "device_class": "uv_index",
    },
}

CARDINAL_DIRECTIONS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                       'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
