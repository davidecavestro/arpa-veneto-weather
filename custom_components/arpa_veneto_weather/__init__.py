"""The Arpa Veneto Weather integration."""

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_change

from .brightness_statistics import async_archive_brightness
from .coordinator import ArpaVenetoDataUpdateCoordinator

from .const import (
    CONF_ARCHIVE_BRIGHTNESS,
    DOMAIN,
    KEY_COORDINATOR,
    KEY_UNSUBSCRIBER
)

_LOGGER = logging.getLogger(__name__)

# Store the configuration in a dict for easy access
PLATFORMS = ["weather", "sensor"]

# The brightness batch is published around 09:30 standard time: this local hour
# is past it both in winter and in summer time
BRIGHTNESS_ARCHIVE_HOUR = 11
BRIGHTNESS_ARCHIVE_MINUTE = 15

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

    if entry.options.get(CONF_ARCHIVE_BRIGHTNESS):
        _async_schedule_brightness_archive(hass, entry, coordinator)

    # Forward the entry to the weather platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


def _async_schedule_brightness_archive(hass: HomeAssistant, entry: ConfigEntry, coordinator):
    """Archive the night sky brightness once a day, and on startup."""

    async def archive(_now=None):
        """Import the readings the API exposes as long-term statistics."""
        try:
            imported = await async_archive_brightness(
                hass, coordinator.latitude, coordinator.longitude)
        except (aiohttp.ClientError, TimeoutError, HomeAssistantError) as err:
            # a history archive is never worth failing a setup or an update for
            _LOGGER.warning("Unable to archive the night sky brightness: %s", err)
            return

        _LOGGER.debug("Archived %s hourly night sky brightness statistics", imported)

    entry.async_on_unload(
        async_track_time_change(
            hass,
            archive,
            hour=BRIGHTNESS_ARCHIVE_HOUR,
            minute=BRIGHTNESS_ARCHIVE_MINUTE,
            second=0,
        )
    )

    # the API exposes about 72 hours, so this recovers the days spent offline
    entry.async_create_background_task(hass, archive(), f"{DOMAIN}_archive_brightness")


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
        for coordinator in _called_coordinators(hass, call):
            await coordinator.async_request_refresh()

    async def handle_archive_brightness(call):
        """Handle the service call to archive the night sky brightness."""
        for coordinator in _called_coordinators(hass, call):
            imported = await async_archive_brightness(
                hass, coordinator.latitude, coordinator.longitude)
            _LOGGER.debug("Archived %s hourly night sky brightness statistics", imported)

    # Register the services
    hass.services.async_register(
        DOMAIN, "refresh_data", handle_refresh_data
    )
    hass.services.async_register(
        DOMAIN, "archive_brightness", handle_archive_brightness
    )
    return True


def _called_coordinators(hass: HomeAssistant, call):
    """Return the coordinators a service call is meant for."""

    # one coordinator per configured station
    entries = hass.data.get(DOMAIN, {})
    entry_id = call.data.get("entry_id")
    # without an explicit entry, the call is meant for every station
    entry_ids = [entry_id] if entry_id else list(entries)

    return [coordinator for target in entry_ids
            if (coordinator := entries.get(target, {}).get(KEY_COORDINATOR)) is not None]

async def options_update_listener(hass: HomeAssistant, config: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config.entry_id)
