"""Provenance of the observations feeding the entities.

A single weather station in Home Assistant is fed by several ARPAV networks
(meteogram, air quality, night sky brightness) and by the forecast bulletin,
each with its own location and its own publishing latency. Every value
therefore carries the origin it was observed by, exposed as extra state
attributes, so that a measurement can be told apart from a forecast.
"""

from dataclasses import dataclass


@dataclass
class Provenance:
    """Where a single observation comes from."""

    source: str
    """Machine readable origin, one of the SOURCE_* constants."""

    name: str | None = None
    """Human readable origin, typically the name of the reporting station."""

    observed_at: str | None = None
    """Timestamp of the observation, as reported by the origin."""

    rule: str | None = None
    """For the computed condition only: the criterion that decided it."""

    def as_attributes(self) -> dict:
        """Return the provenance as extra state attributes, skipping empty fields."""

        attributes = {
            "source": self.source,
            "source_name": self.name,
            "source_observed_at": self.observed_at,
            "source_rule": self.rule,
        }
        return {key: value for key, value in attributes.items() if value is not None}
