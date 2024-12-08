"""Main entity for Arpa Veneto Weather component."""
from __future__ import annotations

from homeassistant.components.weather import WeatherEntity, WeatherEntityFeature, Forecast
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfSpeed, UnitOfLength

from .const import DOMAIN

API_BASE = "https://api.arpa.veneto.it/REST/v1"


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
        self._attr_name = f"Weather for {config_entry.data['comune_name']} with station {
            config_entry.data['station_name']}"
        self._attr_unique_id = f"arpav_weather_{config_entry.entry_id}"

    @property
    def name(self):
        """Return the name of the weather entity."""
        return self._attr_name

    @property
    def temperature(self):
        """Return the temperature from the sensor data."""
        return self.coordinator.data["sensors"].get("temperature")

    @property
    def humidity(self):
        """Return the humidity from the coordinator data."""
        return self.coordinator.data["sensors"].get("humidity")

    @property
    def visibility(self):
        """Return the visibility from the coordinator data."""
        return self.coordinator.data["sensors"].get("visibility")

    @property
    def precipitation(self):
        """Return the precipitation from the coordinator data."""
        return self.coordinator.data["sensors"].get("precipitation")

    @property
    def wind_bearing(self):
        """Return the wind bearing from the coordinator data."""
        return self.coordinator.data["sensors"].get("wind_bearing")

    @property
    def wind_speed(self):
        """Return the wind speed from the coordinator data."""
        return self.coordinator.data["sensors"].get("wind_speed")

    @property
    def supported_features(self) -> WeatherEntityFeature:
        """Determine supported features."""
        return WeatherEntityFeature.FORECAST_TWICE_DAILY

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "visibility": self.visibility,
            "precipitation": self.precipitation,
            "wind_bearing": self.wind_bearing,
            "wind_speed": self.wind_speed,
            "unit_of_measurement_wind_speed": UnitOfSpeed.METERS_PER_SECOND,
            "unit_of_measurement_visibility": UnitOfLength.METERS,
        }

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the twice-daily forecast."""
        forecasts = self.coordinator.data.get("forecast", [])
        return [
            {
                "datetime": entry["datetime"],
                "temperature": entry["temperature"],
                "condition": entry["condition"],
                "precipitation_probability": entry["precipitation_probability"],
                "is_daytime": entry["is_daytime"],
                "type": entry["type"],
            }
            for entry in forecasts
        ]
