"""Coordinator for consuming REST api endpoints on Arpa Veneto Weather component."""
import logging
import re

import aiohttp
from .const import API_BASE, DOMAIN


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
        forecast_data = await fetch_forecast_data(self.zone_id)
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
            extracted_data["visibility"] = int(entry.get("valore"))
        elif entry.get("tipo") == "PREC":
            extracted_data["precipitation"] = float(entry.get("valore"))
        elif entry.get("tipo") == "DVENTO10M":
            extracted_data["wind_bearing"] = int(entry.get("valore"))
        elif entry.get("tipo") == "VVENTO10M":
            extracted_data["wind_speed"] = float(entry.get("valore"))

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

def get_forecast_condition(condition_text):
    """Determine the forecast condition from text."""
    for condition, symbols in condition_lookup.items():
        if any(symbol in condition_text for symbol in symbols):
            return condition
    return None  # or a default value if no match is found

def parse_temperature_range(temp_range):
    """Convert a temperature range string to a mean value."""
    if temp_range == "":
        return None
    if "/" in temp_range:
        low, high = map(float, temp_range.split("/"))
        return (low + high) / 2
    return float(temp_range)

def parse_precipitation_prob(prob):
    """Strip the suffix from  a probability text."""
    if prob == "":
        return None
    return re.sub('%$', '', prob)


def _get_forecast_type(intervallo):
    """Determine the forecast type (once or twice daily)."""
    return {
        "night/morning": "twice_daily",
        "afternoon/evening": "twice_daily",
        "": "daily"
    }.get(intervallo)

def get_forecast_daytime(intervallo):
    """Determine if the intervallo is about day or night."""
    return {
        "night/morning": False,
        "afternoon/evening": True,
        "": True
    }.get(intervallo)

def get_forecast_datetime(scadenza, intervallo):
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

async def fetch_forecast_data(zone_id):
    """Fetch data from the station."""
    url = f"{API_BASE}/bollettini_meteo_simboli_en?zona={zone_id}"
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status != 200:
            raise UpdateFailed(f"Error fetching data: {response.status}")
        data = await response.json()

    forecasts = [
        {
            "datetime": get_forecast_datetime(entry["scadenza"], entry["intervallo"]),
            "type": _get_forecast_type(entry["intervallo"]),
            "is_daytime": get_forecast_daytime(entry["intervallo"]),
            "temperature": parse_temperature_range(entry["temperatura"]),
            "condition": get_forecast_condition(entry["simbolo"]),
            "precipitation_probability": parse_precipitation_prob(entry["prob precipitazioni"]),
        }
        for entry in data.get("data", [])
    ]

    return forecasts
