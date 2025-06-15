"""Config flow to configure Arpa Veneto Weather component."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import CONF_EXPOSE_FORECAST_JSON, CONF_EXPOSE_FORECAST_RAW, DOMAIN, API_BASE


async def fetch_zone_names():
    """Fetch human-readable names for each zonaid."""
    async with aiohttp.ClientSession() as session, session.get(f"{API_BASE}/bollettini_meteo_simboli_en") as response:
        response.raise_for_status()
        json_data = await response.json()
        data = json_data.get("data", [])

        # Map each zonaid to the first matching zona (zone name)
        zone_id_to_name = {}
        for entry in data:
            zonaid = entry["zonaid"]
            if zonaid not in zone_id_to_name:
                zone_id_to_name[zonaid] = entry["zona"]

        return dict(sorted(zone_id_to_name.items(), key=lambda item: item[1]))

async def fetch_zones():
    """Fetch the list of comuni and their corresponding data."""
    async with aiohttp.ClientSession() as session, session.get(f"{API_BASE}/meteo_comuni") as response:
        response.raise_for_status()
        json_data = await response.json()
        data = json_data.get("data", [])

        # Map comune names to their IDs and zonaid
        comune_id_to_name = {entry["id"]: f"{entry['comune']} ({entry['provincia'].title()})"
                             for entry in sorted(data, key=lambda x: x["comune"])}
        comuneid_to_zonaid = {entry["id"]: entry["zonaid"] for entry in data}
        zone_id_to_name = {
            entry["zonaid"]: f"Zona {entry['zonaid']}" for entry in data
        }  # Placeholder for readable zone names

        return comune_id_to_name, comuneid_to_zonaid, zone_id_to_name


async def fetch_stations():
    """Fetch the list of stations and their codes."""
    async with aiohttp.ClientSession() as session, session.get(
        f"{API_BASE}/meteo_meteogrammi?rete=MGRAMMI&coordcd=18&orario=0"
    ) as response:
        response.raise_for_status()
        json_data = await response.json()
        # Access the "data" key which contains the list of stations
        data = json_data.get("data", [])
        return {entry["codseqst"]: f"{entry['nome_stazione']} ({entry['provincia'].title()})" for entry in sorted(data, key=lambda x: x["nome_stazione"])}


class ArpaVenetoWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ARPA Veneto Weather."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Implement OptionsFlow."""
        return ArpaVenetoWeatherOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the first step: comune selection."""
        if user_input is not None:
            # Save the selected comune ID and move to zone selection
            self.selected_comune_id = user_input["comune_id"]
            self.selected_comune_name = self.comune_id_to_name[self.selected_comune_id]
            self.zone_id_to_name = await fetch_zone_names()
            return await self.async_step_zone()

        # Fetch zone data
        self.comune_id_to_name, _, _ = await fetch_zones()

        schema = vol.Schema(
            {vol.Required("comune_id"): vol.In(self.comune_id_to_name)}
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_zone(self, user_input=None):
        """Handle the zone selection step."""
        if user_input is not None:
            # Save the selected zone
            self.selected_comune_id = user_input["comune_id"]
            self.selected_zone_id = user_input["zone_id"]
            self.selected_zone_name = self.zone_id_to_name[self.selected_zone_id]

            # Proceed to station selection
            return await self.async_step_station()

        # Fetch all available zones
        _, id_to_zonaid, _ = await fetch_zones()

        # Map comune_id to preselected zonaid
        preselected_zonaid = id_to_zonaid[self.selected_comune_id]

        # Prepopulate the dropdowns
        schema = vol.Schema(
            {
                vol.Required("comune_id", default=self.selected_comune_id): vol.In(
                    self.comune_id_to_name
                ),
                vol.Required("zone_id", default=preselected_zonaid): vol.In(
                    self.zone_id_to_name
                ),
            }
        )

        return self.async_show_form(
            step_id="zone",
            data_schema=schema,
            description_placeholders={
                "selected_comune": self.comune_id_to_name[self.selected_comune_id],
            },
        )

    async def async_step_station(self, user_input=None):
        """Handle the station selection step."""
        if user_input is not None:
            # Save the selected station
            self.selected_station_id = user_input["station_id"]
            self.selected_station_name = self.station_id_to_name[self.selected_station_id]
            self.station_id_to_name[self.selected_station_id]

            # Create the final entry
            return self.async_create_entry(
                title=f"{self.selected_comune_name} / Stazione di {self.selected_station_name} ",
                data={
                    "comune_id": self.selected_comune_id,
                    "comune_name": self.selected_comune_name,
                    "zone_id": self.selected_zone_id,
                    "zone_name": self.selected_zone_name,
                    "station_id": self.selected_station_id,
                    "station_name": self.selected_station_name,
                },
            )

        # Fetch all stations
        self.station_id_to_name = await fetch_stations()

        schema = vol.Schema(
            {
                vol.Required("station_id"): vol.In(self.station_id_to_name),
            }
        )

        return self.async_show_form(
            step_id="station",
            data_schema=schema,
        )

class ArpaVenetoWeatherOptionsFlowHandler(config_entries.OptionsFlow):
    """Reconfigure integration options.

    Available options are:
        * update interval.
        * enable internal forecast JSON attribute
        * enable raw forecast JSON attribute
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Construct."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="Configure options", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_EXPOSE_FORECAST_JSON,
                        default=self.config_entry.options.get(
                            CONF_EXPOSE_FORECAST_JSON) or False
                    ): bool,
                    vol.Optional(
                        CONF_EXPOSE_FORECAST_RAW,
                        default=self.config_entry.options.get(
                            CONF_EXPOSE_FORECAST_RAW) or False
                    ): bool,
                }
            ),
        )
