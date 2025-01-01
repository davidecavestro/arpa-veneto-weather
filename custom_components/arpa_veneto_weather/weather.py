"""Main entity for Arpa Veneto Weather component."""
from __future__ import annotations

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
        return WeatherEntityFeature.FORECAST_TWICE_DAILY

    # @property
    # def extra_state_attributes(self):
    #     """Return additional attributes."""
    #     return {
    #         "station_id": self.station_id,
    #         "comune_id": self.comune_id,
    #         "temperature": self.temperature,
    #         "humidity": self.humidity,
    #         "visibility": self.visibility,
    #         "precipitation": self.precipitation,
    #         "wind_bearing": self.wind_bearing,
    #         "wind_speed": self.wind_speed,
    #         "uv_index": self.uv_index,
    #         "unit_of_measurement_wind_speed": UnitOfSpeed.KILOMETERS_PER_HOUR,
    #         "unit_of_measurement_visibility": UnitOfLength.KILOMETERS,
    #     }

    def _forecasts(self):
        return self.coordinator.data.get("forecast", [])

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the twice-daily forecast."""
        forecasts = self._forecasts()
        self._attr_available = forecasts is not None and len(forecasts) > 0

        return [f for f in forecasts if f.get('type') == 'twice_daily']
