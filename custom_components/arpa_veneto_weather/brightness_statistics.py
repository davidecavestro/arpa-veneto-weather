"""Archive of the ARPAV night sky brightness as long-term statistics.

The brightness network publishes its readings in a single batch a day, around
09:30 standard time, so a night value only becomes available the morning after:
it can never describe the current sky, but it is a genuine measurement of the
night that has just passed.

Its honest use is therefore as history. Home Assistant cannot back-date states,
but it can import long-term statistics with their real timestamps, so the
readings are archived as hourly external statistics. The API exposes roughly the
last 72 hours, which are re-imported every time: writing the same hour twice
overwrites it, so a missed day recovers by itself.

This is entirely separate from the real-time path: no entity and no automation
is fed by these statistics. They serve to recalibrate the sky thresholds on the
values a given area actually reaches, and to check after the fact what the
forecast fallback got right.
"""

import logging
from datetime import UTC, datetime, timedelta, timezone

import aiohttp

from homeassistant.components.recorder.models import StatisticMeanType, StatisticMetaData
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.util import slugify

from .const import API_BASE, DOMAIN
from .coordinator import sort_locations_by_distance

_LOGGER = logging.getLogger(__name__)

# ARPAV timestamps carry no offset and are on a fixed +0100 all year round
ARPAV_TZ = timezone(timedelta(hours=1))

UNIT_OF_MEASUREMENT = "mag/arcsec²"

# how many of the nearest stations to archive
DEFAULT_STATIONS = 3

# several stations of the network publish nothing at all, so looking only at the
# nearest ones would archive less than asked
MAX_STATIONS_TRIED = 6

# an hour described by fewer readings than this is not worth archiving
MIN_READINGS_PER_HOUR = 3


async def async_archive_brightness(hass, latitude, longitude, stations=DEFAULT_STATIONS):
    """Archive the brightness readings the API exposes, nearest stations first.

    :return: the number of hourly statistics imported
    """

    if "recorder" not in hass.config.components:
        _LOGGER.debug("The recorder is not enabled: nothing to archive")
        return 0

    imported = 0
    archived = 0
    async with aiohttp.ClientSession() as session:
        network = await _fetch(session, f"{API_BASE}/meteo_meteogrammi?rete=MGRAMMIBRI&coordcd=20067&orario=0")
        nearest = sort_locations_by_distance(network.get("data", []), latitude, longitude)

        for station in nearest[:MAX_STATIONS_TRIED]:
            if archived >= stations:
                break

            codseqst = station.get("codseqst")
            if codseqst is None:
                continue

            readings = await _fetch(session, f"{API_BASE}/meteo_brillanza_tabella?codseqst={codseqst}")
            hourly = _hourly_statistics(readings.get("data", []))
            if not hourly:
                _LOGGER.debug("No usable brightness reading from station %s", codseqst)
                continue

            async_add_external_statistics(hass, _metadata(station), hourly)
            imported += len(hourly)
            archived += 1

    return imported


async def _fetch(session, url):
    """Return the JSON payload of an endpoint."""

    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


def _hourly_statistics(readings):
    """Aggregate the readings of a station into hourly statistics."""

    by_hour = {}
    for item in readings:
        try:
            value = float(item.get("valore"))
        except (TypeError, ValueError):
            continue

        # 0 marks a reading with no valid measurement, e.g. during daylight
        if value <= 0:
            continue

        try:
            observed_at = datetime.strptime(item["dataora"], "%Y-%m-%dT%H:%M:%S")
        except (KeyError, TypeError, ValueError):
            continue

        hour = observed_at.replace(
            minute=0, second=0, microsecond=0, tzinfo=ARPAV_TZ).astimezone(UTC)
        by_hour.setdefault(hour, []).append(value)

    return [
        {
            "start": hour,
            "mean": round(sum(values) / len(values), 2),
            "min": min(values),
            "max": max(values),
        }
        for hour, values in sorted(by_hour.items())
        if len(values) >= MIN_READINGS_PER_HOUR
    ]


def _metadata(station):
    """Return the statistic metadata describing a brightness station."""

    name = station.get("nome_stazione") or str(station.get("codseqst"))

    return StatisticMetaData(
        mean_type=StatisticMeanType.ARITHMETIC,
        has_sum=False,
        name=f"Night sky brightness in {name}",
        source=DOMAIN,
        statistic_id=f"{DOMAIN}:sky_brightness_{slugify(name)}",
        unit_class=None,
        unit_of_measurement=UNIT_OF_MEASUREMENT,
    )
