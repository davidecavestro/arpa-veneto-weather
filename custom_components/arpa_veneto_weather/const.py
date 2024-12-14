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
        "device_class": "measure",
    },
}

CARDINAL_DIRECTIONS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                       'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
