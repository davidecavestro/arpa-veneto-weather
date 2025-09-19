"""Constants for Arpa Veneto Weather component."""

DOMAIN = "arpa_veneto_weather"

KEY_COORDINATOR = "coordinator"
KEY_UNSUBSCRIBER = "options_unsubscriber"

API_BASE = "https://api.arpa.veneto.it/REST/v1"

CONF_EXPOSE_FORECAST_JSON = "expose_forecast_json"
CONF_EXPOSE_FORECAST_RAW = "expose_forecast_raw"
CONF_EXPOSE_SENSORS_RAW = "expose_sensors_raw"
CONF_INFER_CONDITION = "infer_condition"
CONF_INFER_CONDITION_FROM_SENSORS = "infer_condition_from_sensors"
CONF_INFER_CONDITION_FROM_SENSORS_WITH_CUSTOM_THRESHOLDS = "infer_condition_from_sensors_with_custom_thresholds"
CONF_INFER_CONDITION_DISABLED = "infer_condition_disabled"

CONF_INFER_CONDITION_DAY_CLEAR_THRESHOLD = "day_clear_threshold"
CONF_INFER_CONDITION_DAY_CLEAR_THRESHOLD_DEFAULT = 0.75
CONF_INFER_CONDITION_DAY_PARTLY_THRESHOLD = "day_partly_threshold"
CONF_INFER_CONDITION_DAY_PARTLY_THRESHOLD_DEFAULT = 0.40
CONF_INFER_CONDITION_NIGHT_CLEAR_THRESHOLD = "night_clear_threshold"
CONF_INFER_CONDITION_NIGHT_CLEAR_THRESHOLD_DEFAULT = 20.5
CONF_INFER_CONDITION_NIGHT_PARTLY_THRESHOLD = "night_partly_threshold"
CONF_INFER_CONDITION_NIGHT_PARTLY_THRESHOLD_DEFAULT = 18.5


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
        "name": "Precipitation in 5 minutes",
        "unit": "mm/5min",
        "device_class": "precipitation",
    },
    "precipitation_probability": {
        "name": "Precipitation probability",
        "unit": "%",
        "device_class": "probability",
    },
    "precipitation_hourly": {
        "name": "Precipitation intensity (mm/h)",
        "unit": "mm/h",
        "device_class": "precipitation",
    },
    "precipitation_cumulative_1h": {
        "name": "Precipitation cumulative 1h",
        "unit": "mm",
        "device_class": "precipitation",
    },
    "precipitation_cumulative_3h": {
        "name": "Precipitation cumulative 3h",
        "unit": "mm",
        "device_class": "precipitation",
    },
    "precipitation_cumulative_6h": {
        "name": "Precipitation cumulative 6h",
        "unit": "mm",
        "device_class": "precipitation",
    },
    "precipitation_cumulative_12h": {
        "name": "Precipitation cumulative 12h",
        "unit": "mm",
        "device_class": "precipitation",
    },
    "precipitation_cumulative_24h": {
        "name": "Precipitation cumulative 24h",
        "unit": "mm",
        "device_class": "precipitation",
    },
    "precipitation_cumulative_today": {
        "name": "Precipitation cumulative today",
        "unit": "mm",
        "device_class": "precipitation",
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
