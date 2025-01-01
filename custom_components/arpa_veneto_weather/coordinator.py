"""Coordinator for consuming REST api endpoints on Arpa Veneto Weather component."""
import logging
import re

import aiohttp
from .const import API_BASE, CARDINAL_DIRECTIONS, DOMAIN


from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed


from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class ArpaVenetoDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for ARPA Veneto."""

    def __init__(self, hass, config_entry, update_interval):
        """Initialize the data update coordinator."""
        self.station_id = config_entry.data.get("station_id")
        self.zone_id = config_entry.data.get("zone_id")
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.station_id}",
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch the latest data from the API."""
        sensor_data = await fetch_station_data(self.station_id)
        forecast_data = await _fetch_forecast_data(self.zone_id)
        return {
            "forecast": forecast_data,
            "sensors": sensor_data,  # Include sensor data like temperature
        }


async def fetch_station_data(station_id):
    """Fetch data from the station."""
    url = f"{API_BASE}/meteo_meteogrammi_tabella?codseqst={station_id}"
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status != 200:
            raise UpdateFailed(f"Error fetching data: {response.status}")
        data = await response.json()

    extracted_data = {}
    # Extract temperature, humidity, and other data
    for entry in data.get("data", []):
        extracted_data["station_name"] = entry.get("nome_stazione")
        if entry.get("tipo") == "TARIA2M":
            extracted_data["temperature"] = float(entry.get("valore"))
        elif entry.get("tipo") == "UMID2M":
            extracted_data["humidity"] = int(entry.get("valore"))
        elif entry.get("tipo") == "VISIB":
            extracted_data["visibility"] = round(int(entry.get("valore")) / 1000, 2)
        elif entry.get("tipo") == "PREC":
            extracted_data["precipitation"] = float(entry.get("valore"))
        elif entry.get("tipo") == "DVENTO10M":
            degrees = int(entry.get("valore"))
            extracted_data["native_wind_bearing"] = degrees
            extracted_data["wind_bearing"] = CARDINAL_DIRECTIONS[int((degrees + 11.25)/22.5)]
        elif entry.get("tipo") == "VVENTO10M":
            extracted_data["wind_speed"] = round(float(entry.get("valore")) * 3.6, 2)
        elif entry.get("tipo") == "RADSOL":
            if (entry.get("unitnm") == "MJ/m2"):
                extracted_data["uv_index"] = round(float(entry.get("valore")) * 0.06 * 40)
            else:
                extracted_data["uv_index"] = round(float(entry.get("valore")) / 0.025)

    extracted_data["last_update"] = datetime.now().isoformat()

    return extracted_data

condition_lookup = {
    "pouring": ["b6.png", "b7.png", "b8.png", "b9.png", "b10.png"],
    "clear-night": ["a1N"],
    "cloudy": ["a4", "a5", "a6"],
    "partlycloudy": ["a3"],
    "fog": ["f1.png", "f2.png", "f3.png", "f4.png"],
    "lightning-rainy": [
        "c1.png", "c2.png", "c3.png", "c5.png", "c6.png",
        "c7.png", "c8.png", "c9.png", "c10.png"
    ],
    "rainy": ["b1.png", "b2.png", "b3.png", "b4.png", "b5.png"],
    "snowy": [
        "d1.png", "d2.png", "d3.png", "d4.png", "d5.png", "d6.png",
        "d7.png", "d8.png", "d9.png", "d10.png"
    ],
    "snowy-rainy": [
        "e1.png", "e2.png", "e3.png", "e4.png", "e5.png", "e6.png",
        "e7.png", "e8.png", "e9.png", "e10.png"
    ],
    "sunny": ["a1", "a2"],
}

def _get_forecast_condition(condition_text):
    """Determine the forecast condition from text."""
    for condition, symbols in condition_lookup.items():
        if any(symbol in condition_text for symbol in symbols):
            return condition
    return None  # or a default value if no match is found

def _get_forecast_temperature_dict(temp_range):
    """Convert a temperature into a dict with templow if it's a range."""
    min_temp = None
    max_temp = None

    if "/" in temp_range:
        min_temp, max_temp = map(float, temp_range.split('/'))
    elif temp_range != "":
        max_temp = float(temp_range)

    return {"templow": min_temp, "temperature": max_temp}

def _parse_precipitation_prob(prob):
    """Strip the suffix from  a probability text."""
    if prob == "":
        return None
    return re.sub('%$', '', prob)


def _get_forecast_type(intervallo):
    """Determine the forecast type (once or twice daily)."""
    if not intervallo:
        return "daily"

    return {
        "night/morning": "twice_daily",
        "afternoon/evening": "twice_daily",
    }.get(intervallo)

def _get_forecast_daytime_dict(intervallo):
    """Determine if the intervallo is about day or night."""
    if not intervallo:
        # return {}
        day_time = True
    else:
        day_time = {
            "night/morning": False, "afternoon/evening": True,
        }.get(intervallo)

    return {"is_daytime": day_time}

def _get_forecast_datetime(scadenza, intervallo):
    """Parse the date string into a date object."""
    date = datetime.strptime(scadenza, "%Y-%m-%d").date()

    # Map intervallo to specific times
    time_mapping = {
        "night/morning": "08:00:00",
        "afternoon/evening": "16:00:00",
        "": "12:00:00"
    }

    # Get the time for the given intervallo
    time_str = time_mapping.get(intervallo.lower())
    if not time_str:
        raise ValueError(f"Unknown intervallo: {intervallo}")

    # Combine date and time into a datetime object
    datetime_str = f"{date} {time_str}"
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

async def _fetch_forecast_data(zone_id):
    """Fetch data from the station."""
    url = f"{API_BASE}/bollettini_meteo_simboli_en?zona={zone_id}"
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status != 200:
            raise UpdateFailed(f"Error fetching data: {response.status}")
        data = await response.json()

    forecasts = [
        _assemble_forecast_dict(entry)
        for entry in data.get("data", [])
    ]

    return forecasts

def _assemble_forecast_dict(entry):

    static_props = {
        "datetime": _get_forecast_datetime(entry["scadenza"], entry["intervallo"]),
        "type": _get_forecast_type(entry["intervallo"]),
        "condition": _get_forecast_condition(entry["simbolo"]),
        "precipitation_probability": _parse_precipitation_prob(entry["prob precipitazioni"]),
    }

    temperature_dict = _get_forecast_temperature_dict(entry["temperatura"])
    daytime_dict = _get_forecast_daytime_dict(entry["intervallo"])
    props_dict = static_props | temperature_dict | daytime_dict

    return props_dict
