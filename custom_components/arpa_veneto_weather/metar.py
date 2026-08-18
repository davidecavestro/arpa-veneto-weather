"""Optional METAR observations, used to complete the ARPAV data.

ARPAV weather stations do not observe the state of the sky, and several of them
publish neither visibility nor pressure. Aerodromes do: a METAR is an actual
observation, issued every 30 minutes with a few minutes of latency, and it
reports cloud cover layer by layer.

Reports come from the Aviation Weather Center of the US National Weather
Service (https://aviationweather.gov/data/api/), which serves them as JSON
with cloud layers already decoded and needs no credentials.

The trade-off is distance: an aerodrome tens of kilometres away describes the
synoptic sky well and local fog or low stratus badly, so choosing a station is
left to the user, who knows how far it is and what the local weather does.
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from math import exp

import aiohttp

from .const import CARDINAL_DIRECTIONS

_LOGGER = logging.getLogger(__name__)

API_BASE = "https://aviationweather.gov/api/data"

# a METAR is issued every 30 minutes, so polling faster is pointless
MIN_FETCH_INTERVAL = timedelta(minutes=10)

# aerodromes with limited opening hours simply stop reporting, and a report from
# hours ago no longer describes the current weather
MAX_OBSERVATION_AGE = timedelta(minutes=90)

# how far around the station to look for aerodromes, in degrees
SEARCH_RANGE_DEGREES = 1.5

# cloud cover as eighths of the sky, as reported by the layer abbreviations
CLOUD_COVER_OKTAS = {
    "SKC": 0,   # sky clear
    "CLR": 0,   # clear below 12000 ft
    "NCD": 0,   # no cloud detected
    "NSC": 0,   # no significant cloud
    "CAVOK": 0,  # ceiling and visibility OK
    "FEW": 2,   # 1 to 2 eighths
    "SCT": 4,   # 3 to 4 eighths, scattered
    "BKN": 6,   # 5 to 7 eighths, broken
    "OVC": 8,   # 8 eighths, overcast
    "OVX": 8,   # sky obscured
    "VV": 8,    # vertical visibility only
}

# a clear sky is reported explicitly, so an empty layer list means "not observed"
CLEAR_SKY_TOKENS = ("CAVOK", "NCD", "NSC", "SKC", "CLR")

KNOTS_TO_KMH = 1.852
STATUTE_MILES_TO_KM = 1.609344


@dataclass
class MetarStation:
    """An aerodrome issuing METAR reports."""

    icao: str
    name: str
    latitude: float
    longitude: float
    distance_km: float
    reporting: bool = True
    """Whether a report is available right now, which for some aerodromes
    depends on their opening hours."""

    @property
    def label(self) -> str:
        """Return a description including the distance from the weather station."""

        label = f"{self.icao} - {self.name} ({self.distance_km:.1f} km)"
        if not self.reporting:
            label += " - not reporting right now"

        return label


@dataclass
class MetarObservation:
    """The observations of a single METAR report."""

    icao: str
    observed_at: str | None = None
    cloud_coverage: int | None = None
    weather: str | None = None
    values: dict = field(default_factory=dict)
    raw: str | None = None

    @property
    def name(self) -> str:
        """Return the origin to expose as the source of these values."""

        return f"METAR {self.icao}"

    @property
    def is_current(self) -> bool:
        """Return whether the report is recent enough to describe the weather now."""

        if not self.observed_at:
            return False

        try:
            observed_at = datetime.fromisoformat(self.observed_at)
        except (TypeError, ValueError):
            return False

        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=UTC)

        return datetime.now(UTC) - observed_at <= MAX_OBSERVATION_AGE


async def async_fetch_stations(latitude, longitude, distance_of):
    """Return the aerodromes issuing METAR around a location, nearest first.

    Some aerodromes are registered as METAR sites but publish nothing, and
    others only during their opening hours, so the ones reporting at the moment
    come first.

    :param distance_of: callable returning the distance in km from the station
    """

    span = SEARCH_RANGE_DEGREES
    bbox = f"{latitude - span},{longitude - span},{latitude + span},{longitude + span}"
    url = f"{API_BASE}/stationinfo?bbox={bbox}&format=json"

    async with aiohttp.ClientSession() as session, session.get(url) as response:
        response.raise_for_status()
        data = await response.json()

    stations = []
    for entry in data:
        icao = entry.get("icaoId")
        latitudine = entry.get("lat")
        longitudine = entry.get("lon")
        # some entries only issue TAF forecasts, or carry no usable position
        if not icao or latitudine is None or longitudine is None:
            continue
        if "METAR" not in (entry.get("siteType") or []):
            continue

        stations.append(MetarStation(
            icao=icao,
            name=entry.get("site") or icao,
            latitude=latitudine,
            longitude=longitudine,
            distance_km=distance_of(latitudine, longitudine),
        ))

    reporting = await _async_reporting_icaos([station.icao for station in stations])
    for station in stations:
        station.reporting = station.icao in reporting

    # the nearest aerodrome is of no use while it is not publishing anything
    return sorted(stations, key=lambda station: (not station.reporting, station.distance_km))


async def _async_reporting_icaos(icaos):
    """Return which of the given aerodromes have a report available right now."""

    if not icaos:
        return set()

    url = f"{API_BASE}/metar?ids={','.join(icaos)}&format=json"

    try:
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
    except (aiohttp.ClientError, TimeoutError) as err:
        # without this detail the list is still usable, just less informative
        _LOGGER.debug("Unable to tell which aerodromes are reporting: %s", err)
        return set(icaos)

    return {report.get("icaoId") for report in data}


async def async_fetch_observation(icao):
    """Return the latest METAR observation of an aerodrome, or None."""

    url = f"{API_BASE}/metar?ids={icao}&format=json"

    try:
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
    except (aiohttp.ClientError, TimeoutError) as err:
        # an optional data source must never take the whole update down
        _LOGGER.warning("Unable to fetch the METAR report of %s: %s", icao, err)
        return None

    if not data:
        _LOGGER.debug("No METAR report available for %s", icao)
        return None

    return _parse_observation(data[0])


def _parse_observation(report):
    """Turn a METAR report into the observations it provides."""

    raw = report.get("rawOb") or ""
    values = {}

    visibility = _visibility_km(report.get("visib"))
    if visibility is not None:
        values["visibility"] = visibility

    for key, value in (("pressure", report.get("altim")),
                       ("temperature", report.get("temp"))):
        if value is not None:
            values[key] = float(value)

    humidity = _relative_humidity(report.get("temp"), report.get("dewp"))
    if humidity is not None:
        values["humidity"] = humidity

    wind_speed = report.get("wspd")
    if wind_speed is not None:
        values["wind_speed"] = round(float(wind_speed) * KNOTS_TO_KMH, 2)

    bearing = report.get("wdir")
    # a variable wind direction is reported as VRB and has no bearing
    if isinstance(bearing, (int, float)):
        values["native_wind_bearing"] = int(bearing)
        values["wind_bearing"] = CARDINAL_DIRECTIONS[int((int(bearing) + 11.25) / 22.5)]

    return MetarObservation(
        icao=report.get("icaoId"),
        observed_at=_observed_at(report),
        cloud_coverage=_cloud_coverage(report.get("clouds"), raw),
        weather=report.get("wxString"),
        values=values,
        raw=raw or None,
    )


def condition(observation, is_day):
    """Return the Home Assistant condition described by a METAR, or None.

    Present weather wins over cloud cover: a broken sky raining is rainy.
    """

    if observation is None:
        return None

    weather = (observation.weather or "").upper()

    if "TS" in weather:
        return "lightning-rainy" if any(code in weather for code in ("RA", "DZ", "SN")) else "lightning"
    if "SN" in weather or "SG" in weather:
        return "snowy-rainy" if any(code in weather for code in ("RA", "DZ")) else "snowy"
    if "FZRA" in weather or "FZDZ" in weather or "PL" in weather or "IC" in weather:
        return "snowy-rainy"
    if "GR" in weather or "GS" in weather:
        return "hail"
    if "RA" in weather or "DZ" in weather:
        return "pouring" if weather.startswith("+") else "rainy"
    if "FG" in weather or "BR" in weather or "HZ" in weather or "FU" in weather:
        return "fog"

    coverage = observation.cloud_coverage
    if coverage is None:
        return None

    if coverage <= 12:  # nothing, or at most a couple of eighths
        return "sunny" if is_day else "clear-night"
    if coverage <= 50:  # few to scattered
        return "partlycloudy"
    return "cloudy"


def _cloud_coverage(layers, raw):
    """Return the total cloud cover as a percentage, or None if not observed."""

    oktas = [
        CLOUD_COVER_OKTAS[cover]
        for layer in (layers or [])
        if (cover := (layer.get("cover") or "").upper()) in CLOUD_COVER_OKTAS
    ]

    if oktas:
        # the total cover is the one of the most covering layer
        return round(max(oktas) * 100 / 8)

    # with no layer reported, only an explicit "clear" token means a clear sky
    if any(token in raw.upper() for token in CLEAR_SKY_TOKENS):
        return 0

    return None


def _visibility_km(visibility):
    """Return the reported visibility in km, or None.

    METAR visibility is reported in statute miles, and a trailing "+" marks a
    lower bound ("6+" means 6 miles or more), which is kept as the value.
    """

    if visibility is None:
        return None

    try:
        miles = float(str(visibility).replace("+", "").strip())
    except (TypeError, ValueError):
        return None

    return round(miles * STATUTE_MILES_TO_KM, 2)


def _relative_humidity(temperature, dew_point):
    """Return the relative humidity from temperature and dew point, or None."""

    if temperature is None or dew_point is None:
        return None

    # Magnus-Tetens approximation
    a, b = 17.625, 243.04
    try:
        temperature = float(temperature)
        dew_point = float(dew_point)
    except (TypeError, ValueError):
        return None

    saturation = exp(a * dew_point / (b + dew_point) - a * temperature / (b + temperature))

    return min(100, max(0, round(100 * saturation)))


def _observed_at(report):
    """Return the observation time of a report as an ISO string, or None."""

    report_time = report.get("reportTime")
    if report_time:
        # e.g. "2026-08-18T11:00:00.000Z"
        try:
            return datetime.fromisoformat(report_time.replace("Z", "+00:00")).isoformat()
        except (AttributeError, TypeError, ValueError):
            pass

    observation_time = report.get("obsTime")
    if observation_time:
        try:
            return datetime.fromtimestamp(int(observation_time)).astimezone().isoformat()
        except (TypeError, ValueError, OSError):
            pass

    return None
