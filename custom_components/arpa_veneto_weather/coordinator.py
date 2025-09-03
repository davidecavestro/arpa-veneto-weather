"""Coordinator for consuming REST api endpoints on Arpa Veneto Weather component."""
import logging
import re

import aiohttp
from . import const
from .const import (
    API_BASE, CARDINAL_DIRECTIONS, DOMAIN
)

from .thresholds import DayThresholds, NightThresholds

from astral import LocationInfo
from astral.sun import sun, elevation
from astral.moon import phase
from datetime import datetime
from math import radians, cos, sin, asin, sqrt


from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)


_LOGGER = logging.getLogger(__name__)

class ArpaVenetoDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for ARPA Veneto."""

    def __init__(self, hass, config_entry, update_interval):
        """Initialize the data update coordinator."""
        self.station_id = config_entry.data.get("station_id")
        self.zone_id = config_entry.data.get("zone_id")
        self.latitude = config_entry.data.get("station_latitude")
        self.longitude = config_entry.data.get("station_longitude")
        self.infer_condition = config_entry.options.get(const.CONF_INFER_CONDITION)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.station_id}",
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch the latest data from the API."""
        _LOGGER.warning("Fetching data")
        sensor_data, sensor_data_raw = await self.fetch_station_data(self.station_id)
        forecast_data, forecast_raw = await _fetch_forecast_data(self.zone_id)

        day_cfg = DayThresholds()
        night_cfg = NightThresholds()
        # Determine the current condition based on configuration
        match self.infer_condition:
            case const.CONF_INFER_CONDITION_FROM_SENSORS:
                sensor_data["condition"] = await self._compute_condition_from_sensors(self.latitude, self.longitude, sensor_data)
            case const.CONF_INFER_CONDITION_FROM_SENSORS_WITH_CUSTOM_THRESHOLDS:
                opts = self.config_entry.options
                if opts.get("override_thresholds"):
                    day_cfg = DayThresholds(
                        clear_ratio=opts.get(
                            "day_clear_ratio", const.CONF_INFER_CONDITION_DAY_CLEAR_THRESHOLD_DEFAULT),
                        partly_ratio=opts.get(
                            "day_partly_ratio", const.CONF_INFER_CONDITION_DAY_PARTLY_THRESHOLD_DEFAULT),
                    )
                    night_cfg = NightThresholds(
                        cloudy_humidity=opts.get(
                            "night_cloudy_humidity", const.CONF_INFER_CONDITION_NIGHT_CLEAR_THRESHOLD_DEFAULT),
                        dark_moon=opts.get(
                            "night_dark_moon", const.CONF_INFER_CONDITION_NIGHT_PARTLY_THRESHOLD_DEFAULT),
                    )

                sensor_data["condition"] = await self._compute_condition_from_sensors(self.latitude, self.longitude, sensor_data, day_cfg, night_cfg)
            case _:  # CONF_INFER_CONDITION_DISABLED or any other value
                pass  # Do not compute condition

        return {
            "forecast": forecast_data,
            "forecast_raw": forecast_raw,
            "sensors": sensor_data,  # Include sensor data like temperature
            "sensors_raw": sensor_data_raw,
        }

    async def fetch_station_data(self, station_id):
        """Fetch data from the station."""
        url = f"{API_BASE}/meteo_meteogrammi_tabella?codseqst={station_id}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise UpdateFailed(f"Error fetching data: {response.status}")
            data = await response.json()

        # Dictionary to store the max-time item per type
        latest_by_type = {}

        for item in data.get("data", []):
            t = item["tipo"]
            if t not in latest_by_type or item["dataora"] > latest_by_type[t]["dataora"]:
                latest_by_type[t] = item
                dataora = item["dataora"]

        # Convert back to list
        filtered_data = list(latest_by_type.values())

        extracted_data = {}
        # Extract temperature, humidity, and other data
        for entry in filtered_data:
            extracted_data["station_name"] = entry.get("nome_stazione")

            tipo = entry.get("tipo")
            valore = entry.get("valore")
            # latitudine = entry.get("latitudine")
            # longitudine = entry.get("longitudine")

            if tipo.startswith("TARIA"):
                extracted_data["temperature"] = float(valore)
            elif tipo.startswith("UMID"):
                extracted_data["humidity"] = int(valore)
            elif tipo == "VISIB":
                extracted_data["visibility"] = round(int(valore) / 1000, 2)
            elif tipo == "PREC":
                extracted_data["precipitation"] = float(valore)
            elif tipo.startswith("DVENTO"):
                degrees = int(valore)
                extracted_data["native_wind_bearing"] = degrees
                extracted_data["wind_bearing"] = CARDINAL_DIRECTIONS[int((degrees + 11.25)/22.5)]
            elif tipo.startswith("VVENTO"):
                extracted_data["wind_speed"] = round(float(valore) * 3.6, 2)
            elif tipo == "RADSOL":
                # Assuming UV Fraction = 6% => 0.06
                if (entry.get("unitnm") == "MJ/m2"):
                    # For MJ/m², the scaling factor is 40 because it includes cumulative energy and time
                    extracted_data["uv_index"] = round(float(valore) * 0.06 * 40)
                    extracted_data["ghi"] = round(mj_to_wm2(float(valore), 3600))
                elif (entry.get("unitnm") == "w/m2"):
                    # For W/m², the scaling factor is 0.04 because it represents instantaneous power
                    extracted_data["uv_index"] = round(float(valore) * 0.06 * 0.04)
                    extracted_data["ghi"] = round(float(valore))

        extracted_data["last_update"] = datetime.now().isoformat()
        extracted_data["dt"] = dataora

        return extracted_data, filtered_data

    async def _compute_condition_from_sensors(self, lat, long, sensor_data, day_cfg=DayThresholds(), night_cfg=NightThresholds()):
        """Compute the current condition based on sensor data."""

        dt = await self._local_dt(sensor_data.get("dt"))
        return await self.classify_sky(lat, long, dt, sensor_data, day_cfg, night_cfg)

    async def _local_dt(self, dt_str):
        """Convert a datetime string to a localized datetime object."""
        # tz = await self.hass.async_add_executor_job(pytz.timezone, 'Europe/Rome')
        # dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        # return tz.localize(dt)

        return datetime.strptime(dt_str + " +0100", "%Y-%m-%dT%H:%M:%S %z")

    async def classify_sky(self, lat, lon, dt, sensor_data, day_cfg: DayThresholds, night_cfg: NightThresholds):
        """Classifies the sky condition.

        Based on:
        - Day: incident solar radiation (normalized to solar elevation)
        - Night: sky brightness (mag/arcsec²) corrected for Moon phase

        :param lat: latitude (float)
        :param lon: longitude (float)
        :param dt: datetime with tzinfo
        :param sensor_data: sensor data containing "ghi" [W/m²]
        :return: string ["clear", "partlycloudy", "cloudy", "unknown"]
        """

        temperature = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        wind_speed = sensor_data.get("wind_speed")
        precipitation = sensor_data.get("precipitation")
        visibility = sensor_data.get("visibility")

        ghi = sensor_data.get("ghi")

        # Precipitation overrides everything
        if precipitation > 0:
            if temperature <= 5:
                return "snow"
            elif temperature <= 0:
                return "snowy-rainy"
            if precipitation > 20:
                return "pouring"
            return "rainy"

        # Visibility overrides wind and
        if visibility is not None:
            if visibility < 1:
                return "fog"
            if visibility < 2 and humidity > 99:
                return "fog"

        if wind_speed and wind_speed > 30:
            return "windy"

        city = LocationInfo(latitude=lat, longitude=lon)
        s = sun(city.observer, date=dt.date(), tzinfo=dt.tzinfo)

        is_day = s["sunrise"] <= dt <= s["sunset"]

        if is_day:
            if ghi is None:
                return "unknown"

            # Sun elevation in degrees
            h_sun = elevation(city.observer, dt)

            if h_sun <= 0:
                return "unknown"  # Sun below horizon (transitions)

            # Theoretical maximum irradiance (approximated)
            ghi_clear = 1000 * sin(radians(h_sun))

            # Normalization
            ghi_ratio = ghi / ghi_clear if ghi_clear > 0 else 0

            # Empirical thresholds (to be calibrated on ARPA data)
            if ghi_ratio > day_cfg.clear:
                return "sunny"
            elif ghi_ratio > day_cfg.partly_cloudy:
                return "partlycloudy"
            else:
                if wind_speed and wind_speed > 30:
                    return "windy-variant"
                return "cloudy"

        else:
            sky_brightness = await self.get_night_sky_brightness(lat, lon)
            if sky_brightness is None:
                return "unknown"

            illum = moon_illumination(dt)
            if illum > 50:
                offset = -2
            elif illum > 10:
                offset = -1
            else:
                offset = 0

            if sky_brightness + offset > night_cfg.clear:
                return "clear"
            elif sky_brightness + offset > night_cfg.partly_cloudy:
                return "partlycloudy"
            else:
                if wind_speed and wind_speed > 30:
                    return "windy-variant"
                return "cloudy"

    async def get_night_sky_brightness(self, lat, lon):
        """Approximate night sky brightness (mag/arcsec²) based on location."""

        url = f"{API_BASE}/meteo_meteogrammi?rete=MGRAMMIBRI&coordcd=20067&orario=0"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise UpdateFailed(f"Error fetching data: {response.status}")
            data = await response.json()

        nearest_station = find_nearest_location(data.get("data", []), lat, lon)

        url = f"{API_BASE}/meteo_brillanza_tabella?codseqst={nearest_station.get('codseqst')}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise UpdateFailed(f"Error fetching data: {response.status}")
            data = await response.json()

        latest = {}
        for item in data.get("data", []):
            if item["dataora"] > latest.get("dataora", ""):
                latest = item

        sky_brightness = latest.get("valore")

        return float(sky_brightness)


def find_nearest_location(locations, target_lat, target_lon):
    """Find the nearest location from a list based on latitude and longitude."""
    return min(
        locations,
        key=lambda x: haversine(x['latitudine'], x['longitudine'], target_lat, target_lon)
    )

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the distance in kilometers between two points."""
    # Convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers

    return c * r

def mj_to_wm2(mj_per_m2, seconds=3600):
    """Convert MJ/m² per interval to W/m² (mean irradiance).

    Default assumes an hourly interval.
    """
    return (mj_per_m2 * 1e6) / seconds


def moon_illumination(dt):
    """Approximate Moon illumination (0–100%).

    dt: datetime
    """
    p = phase(dt)  # 0=new, 14=full
    return (1 - cos(radians(p * 360 / 29.53))) / 2 * 100


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

def _get_forecast_temperature_dict(entry):
    """Convert a temperature into a dict with templow if it's a range."""
    # Use a generator to filter keys starting with "temperatura"
    first_valid_value = next(
        (value for key, value in entry.items() if key.startswith(
            "temperatura") and value not in (None, "")),
        None
    )
    retval = None
    if (first_valid_value is None):
        retval = {"tempmiss": True}
    elif "/" in first_valid_value:
        min_temp, max_temp = map(float, first_valid_value.split('/'))
        retval = {"native_templow": min_temp, "native_temperature": max_temp}
    elif first_valid_value != "":
        retval = {"native_temperature": float(first_valid_value)}

    return retval

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

    return forecasts, data

def _assemble_forecast_dict(entry):

    static_props = {
        "datetime": _get_forecast_datetime(entry["scadenza"], entry["intervallo"]),
        "type": _get_forecast_type(entry["intervallo"]),
        "condition": _get_forecast_condition(entry["simbolo"]),
        "precipitation_probability": _parse_precipitation_prob(entry["prob precipitazioni"]),
        "forecast_reliability": entry["attendibilita"],
        "weather_description": entry["testo"],
        "precipitation_description": entry["precipitazioni"],
    }

    temperature_dict = _get_forecast_temperature_dict(entry)
    daytime_dict = {} if static_props["type"] == "daily" else _get_forecast_daytime_dict(
        entry["intervallo"])
    props_dict = static_props | temperature_dict | daytime_dict

    return props_dict
