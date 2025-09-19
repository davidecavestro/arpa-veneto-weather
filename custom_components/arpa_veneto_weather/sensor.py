"""Sensors for Arpa Veneto Weather component."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from .const import (
    DOMAIN,
    SENSOR_TYPES,
    KEY_COORDINATOR
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up ARPA Veneto sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][KEY_COORDINATOR]

    # create a sensor for each sensor type in SENSOR_TYPES
    sensors = []
    for sensor_type in SENSOR_TYPES:
        sensors.append(ArpaVenetoSensor(coordinator, config_entry, sensor_type))
    async_add_entities(sensors)

class ArpaVenetoSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Representation of an ARPA Veneto sensor."""

    def __init__(self, coordinator, config_entry, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)  # Initialize the CoordinatorEntity
        self.coordinator = coordinator
        self._config_entry = config_entry
        self.station_id = config_entry.data.get("station_id")
        self.station_name = config_entry.data.get("station_name")
        self.sensor_type = sensor_type
        self._attr_device_class = SENSOR_TYPES[sensor_type].get("device_class")
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type].get("unit")

        self._attr_unique_id = f"arpav_{sensor_type}_{self.station_id}"

        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_type
        self._attr_translation_placeholders = {"station_name": self.station_name}

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="Arpa Veneto Weather",
        )

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
