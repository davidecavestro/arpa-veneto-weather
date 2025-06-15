"""The Arpa Veneto Weather integration."""

import asyncio
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import ArpaVenetoDataUpdateCoordinator

from .const import (
    DOMAIN,
    KEY_COORDINATOR,
    KEY_UNSUBSCRIBER
)

# Store the configuration in a dict for easy access
PLATFORMS = ["weather", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ARPA Veneto Weather from a config entry."""

    update_interval = timedelta(minutes=entry.options.get(
        "update_interval", 5))  # Fetch data every 5 minutes
    coordinator = ArpaVenetoDataUpdateCoordinator(
        hass,
        entry,
        update_interval,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        KEY_COORDINATOR: coordinator,
    }

    # Register a listener when options change
    unsub = entry.add_update_listener(options_update_listener)
    hass.data[DOMAIN][entry.entry_id][KEY_UNSUBSCRIBER] = unsub

    # Forward the entry to the weather platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload ARPA Veneto Weather config entry."""
    # await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    # hass.data[DOMAIN].pop(entry.entry_id)
    # return True

    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, component) for component in PLATFORMS]
        )
    )
    if unload_ok:
        # Call the options unsubscriber and remove the configuration
        hass.data[DOMAIN][entry.entry_id][KEY_UNSUBSCRIBER]()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup(hass, config):
    """Register the service."""
    async def handle_refresh_data(call):
        """Handle the service call to refresh data."""
        # Access the integration's coordinator
        entry_id = call.data.get("entry_id")
        coordinators = hass.data[DOMAIN]
        if entry_id in coordinators:
            await coordinators[entry_id].async_request_refresh()

    # Register the service
    hass.services.async_register(
        DOMAIN, "refresh_data", handle_refresh_data
    )
    return True

async def options_update_listener(hass: HomeAssistant, config: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config.entry_id)
