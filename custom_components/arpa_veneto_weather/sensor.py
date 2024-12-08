"""Sensors for Arpa Veneto Weather component."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSOR_TYPES

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up ARPA Veneto sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        ArpaVenetoSensor(coordinator, config_entry, "temperature"),
        ArpaVenetoSensor(coordinator, config_entry, "humidity"),
        ArpaVenetoSensor(coordinator, config_entry, "visibility"),
        ArpaVenetoSensor(coordinator, config_entry, "precipitation"),
        ArpaVenetoSensor(coordinator, config_entry, "wind_bearing"),
        ArpaVenetoSensor(coordinator, config_entry, "wind_speed"),
    ]
    async_add_entities(sensors)

class ArpaVenetoSensor(CoordinatorEntity, SensorEntity):
    """Representation of an ARPA Veneto sensor."""

    def __init__(self, coordinator, config_entry, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)  # Initialize the CoordinatorEntity
        self.coordinator = coordinator
        self.station_id = config_entry.data.get("station_id")
        self.sensor_type = sensor_type
        self._attr_name = f"ARPA Veneto {SENSOR_TYPES[sensor_type]['name']} ({self.station_id})"
        self._attr_device_class = SENSOR_TYPES[sensor_type].get("device_class")
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type].get("unit")

        self._attr_unique_id = f"arpav_{sensor_type}_{config_entry.entry_id}"
        self._attr_name = f"{sensor_type.capitalize()} in {
            config_entry.data['station_name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data["sensors"].get(self.sensor_type)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "station_id": self.station_id,
            "last_update": self.coordinator.data["sensors"].get("last_update"),
        }

    async def async_update(self):
        """Update the sensor state."""
        await self.coordinator.async_request_refresh()
