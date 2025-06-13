"""Main entity for Arpa Veneto Weather component."""
from __future__ import annotations
from collections import defaultdict

from homeassistant.components.weather import WeatherEntity, WeatherEntityFeature, Forecast
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, API_BASE


async def async_get_forecast(session):
    """Fetch weather forecast data."""
    url = f"{API_BASE}/bollettini_meteo_giornate"
    async with session.get(url) as response:
        response.raise_for_status()
        data = await response.json()
        return [entry for entry in data if entry["zonaid"] == 13]


async def async_get_current_conditions(session, station_id):
    """Fetch current weather conditions."""
    url = f"{API_BASE}/meteo_meteogrammi_tabella?codseqst={station_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        data = await response.json()
        return data[0] if data else {}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up ARPA Veneto sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ArpaVenetoWeatherEntity(coordinator, config_entry)])


class ArpaVenetoWeatherEntity(CoordinatorEntity, WeatherEntity):
    """Representation of the ARPA Veneto weather entity."""

    def __init__(self, coordinator, config_entry):
        """Init the entity with config data."""
        super().__init__(coordinator)  # Initialize the CoordinatorEntity
        self.comune_name = config_entry.data['comune_name']
        self.comune_id = config_entry.data['comune_id']
        self.station_name = config_entry.data['station_name']
        self.station_id = config_entry.data['station_id']

        self._attr_unique_id = f"weather.arpav_{self.comune_id}_{self.station_id}"

        self._attr_has_entity_name = True
        self._attr_translation_key = 'arpav'
        self._attr_attribution = "Weather data by ARPA Veneto"

        self._attr_translation_placeholders = {
            "comune_name": self.comune_name,
            "station_name": self.station_name,
        }
        self._attr_available = False  # Default to unavailable

    @property
    def native_temperature(self):
        """Return the temperature from the sensor data."""
        return self.coordinator.data["sensors"].get("temperature")

    @property
    def humidity(self):
        """Return the humidity from the coordinator data."""
        return self.coordinator.data["sensors"].get("humidity")

    @property
    def native_visibility(self):
        """Return the visibility from the coordinator data."""
        return self.coordinator.data["sensors"].get("visibility")

    @property
    def native_precipitation(self):
        """Return the precipitation from the coordinator data."""
        return self.coordinator.data["sensors"].get("precipitation")

    @property
    def wind_bearing(self):
        """Return the wind bearing from the coordinator data."""
        return self.coordinator.data["sensors"].get("wind_bearing")

    @property
    def native_wind_speed(self):
        """Return the wind speed from the coordinator data."""
        return self.coordinator.data["sensors"].get("wind_speed")

    @property
    def uv_index(self):
        """Return the UV index from the coordinator data."""
        return self.coordinator.data["sensors"].get("uv_index")

    @property
    def supported_features(self) -> WeatherEntityFeature:
        """Determine supported features."""
        return WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_TWICE_DAILY

    def _forecasts(self):
        return self.coordinator.data.get("forecast", [])

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the twice-daily forecast."""
        forecasts = self._forecasts()
        self._attr_available = forecasts is not None and len(forecasts) > 0

        return [f for f in forecasts if f.get('type') == 'twice_daily']

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        forecasts = self._forecasts()
        self._attr_available = forecasts is not None and len(forecasts) > 0

        # Step 1: Group by date
        grouped_data = defaultdict(list)
        for entry in forecasts:
            # Extract the date (ignoring time)
            date = (entry["datetime"]).date()
            grouped_data[date].append(entry)

        # Step 2: Process each group to generate the desired output
        result = []
        for date, entries in grouped_data.items():
            # Find all 'twice_daily' entries with is_daytime=True
            daytime_entries = [e for e in entries if e.get(
                "type") == "twice_daily" and e.get("is_daytime")]

            if daytime_entries:
                # Take the first daytime entry for the date
                selected_entry = daytime_entries[0].copy()

                # Calculate temperatures, considering native_templow if available
                temperatures = [
                    (e["native_temperature"] + e["native_templow"]) / 2
                    if "native_templow" in e
                    else e["native_temperature"]
                    for e in entries
                    if "native_temperature" in e
                ]
                # Calculate max temperature and min temperature for the date
                selected_entry["native_temperature"] = max(temperatures)
                if len(temperatures) > 1:
                    selected_entry["native_templow"] = min(temperatures)
                elif "native_templow" in selected_entry:  # no hightly forecast -> no min
                    del selected_entry["native_templow"]

                # Replace datetime with the date as string
                selected_entry["datetime"] = str(date)
                # Make it a daily entry
                selected_entry["type"] = "daily"
            else:
                selected_entry = entries[0]

            result.append(selected_entry)

        # return [f for f in forecasts if f.get('type') == 'daily']
        return result
        
    @property
    def extra_state_attributes(self):
        """Return additional state attributes with forecast summary for today, tomorrow, and day after."""
        forecasts = self._forecasts()
        if not forecasts or len(forecasts) < 3:
            return {}
    
        def get_attr(entry, key):
            return entry.get(key) or ""
    
        today = forecasts[0]
        tomorrow = forecasts[1]
        day_after = forecasts[2]
    
        return {
            "forecast_today_description": get_attr(today, "weather_description"),
            "forecast_today_precipitation": get_attr(today, "precipitation_description"),
            "forecast_today_precipitation_probability": get_attr(today, "precipitation_probability"),
            "forecast_today_reliability": get_attr(today, "forecast_reliability"),
    
            "forecast_tomorrow_description": get_attr(tomorrow, "weather_description"),
            "forecast_tomorrow_precipitation": get_attr(tomorrow, "precipitation_description"),
            "forecast_tomorrow_precipitation_probability": get_attr(tomorrow, "precipitation_probability"),
            "forecast_tomorrow_reliability": get_attr(tomorrow, "forecast_reliability"),
    
            "forecast_day_after_tomorrow_description": get_attr(day_after, "weather_description"),
            "forecast_day_after_tomorrow_precipitation": get_attr(day_after, "precipitation_description"),
            "forecast_day_after_tomorrow_precipitation_probability": get_attr(day_after, "precipitation_probability"),
            "forecast_day_after_tomorrow_reliability": get_attr(day_after, "forecast_reliability"),
    }
        
