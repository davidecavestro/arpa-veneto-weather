# Arpa Veneto Weather integration for Home Assistant
Home Assistant unofficial integration for Arpa Veneto Weather current conditions and forecast bulletins

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![Community Forum][forum-shield]][forum]


This integration adds support for retrieving the Forecast data from the
[Arpav bulletin endpoint](https://api.arpa.veneto.it/REST/v1/bollettini_meteo_simboli_en)
and current conditions from
[Arpav meteogram endpoint](https://api.arpa.veneto.it/REST/v1/meteo_meteogrammi_tabella).

For this integration you must choose an Arpav forecast zone for forecast data and a weather station for current conditions.

#### This integration will set up the following platforms.

Platform | Description
-- | --
`weather` | A Home Assistant `weather` entity, with current data and twice-daily forecast data.
`sensor` | A Home Assistant `sensor` entity, with all available sensor data from the API.

Minimum required version of Home Assistant is **2024.11.0** as this integration uses the new Weather entity forecast types.

## Installation through HACS (Recommended Method)

If you are not familiar with HACS, or haven't installed it,
I would recommend to [look through the HACS documentation](https://hacs.xyz/), before continuing.

Register `davidecavestro/arpa-veneto-weather` as an
[HACS custom repository](https://www.hacs.xyz/docs/faq/custom_repositories/).

## Manual installation

1. Create a new folder in your configuration folder (where the `configuration.yaml` lives) called `custom_components`
2. Download the [latest version](https://github.com/davidecavestro/arpa-veneto-weather/releases)
into the `custom_components` folder so that the full path from your config
folder is `custom_components/arpa_veneto_weather/`
3. Restart Home Assistant.
4. Once Home Assistant is started, from the UI go to
_Configuration > Integrations > Add Integrations_.
Search for "Arpa Veneto Weather".
After selecting, it could take up to a minute.

## Configuration

To add Arpa Veneto Weather to your installation, do the following:

- Go to Configuration and Integrations
- Click the + ADD INTEGRATION button in the lower right corner.
- Search for *Arpa Veneto Weather** and click the integration.
- When loaded, there will be a configuration wizard, where you must enter:

  | Parameter | Required | Default Value | Description |
  | --------- | -------- | ------------- | ----------- |
  | `Comune ID` | Yes | None | Set the municipality to use for a a forecast zone lookup, based on [synthetic forecast by zone](https://meteo.arpa.veneto.it/?page=comuni_geo). |
  | `Zone ID` | Yes | None | Set the forecast zone. |
  | `Station ID` | Yes | None | Choose the Weather Station for getting current conditions among the available ones. Check [the meteo variables page](https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/meteo-idro-nivo/variabili_meteo). |

- Complete the wizard to save your data.
  If all goes well you should now have a new Weather entity with data from Arpav Forecast
- **Please Note**: You can configure multiple instances of the Integration.

## Enable Debug Logging

If logs are needed for debugging or reporting an issue, use the following configuration.yaml:

```yaml
logger:
  default: error
  logs:
    custom_components.arpa-veneto-weather: debug
```

## Expose raw data

In order to get the raw data for advanced stuff in HA, from the UI go to
_Configuration > Integrations > Arpa Veneto Weather_.
<br>
Press the _CONFIGURE_ button on the integration entry.
<br>
Enable the option you need among:

<dl>
<dt>
Expose JSON extra attribute for internal forecast data
</dt>
<dd>
JSON representation of the internal data structure serving forecasts
</dd>
<dt>
Expose JSON extra attribute for raw original forecast data
</dt>
<dd>
JSON representation of the raw forecast data, as obtained from the bulletin remote endpoint
</dd>
<dt>
Expose extra attributes for raw original sensor data
</dt>
<dd>
Raw data from the meteogram remote endpoint, exposed both as single attributes (prefixed with <i>raw_</i> leading to related value) plus the list of raw objects representing last available sensor observation, along with description, unit of measure, date/time.
</dd>
</dl>

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by ARPAV (Agenzia Regionale
per la Prevenzione e Protezione Ambientale del Veneto).

The data and information provided through this integration are sourced from the ARPAV API,
which is publicly available and licensed under the Creative Commons Attribution 4.0 Italy
(CC BY 4.0) license unless otherwise specified.

### Terms of Use

All trademarks, logos, and distinctive signs visible on ARPAV's website are the property of
ARPAV and cannot be used without prior authorization.

Any reproduction, distribution, modification, or use of ARPAV's content must attribute the
source by citing "ARPAV" and providing the URL: http://www.arpa.veneto.it.

This project utilizes ARPAV's data strictly within the terms of the
[Creative Commons Attribution 4.0 Italy license](https://creativecommons.org/licenses/by/4.0/deed.it).

### Limitations of Liability

ARPAV disclaims all responsibility for the accuracy, completeness, and timeliness of the data
provided via their API, and for any issues arising from its use. Users should refer to ARPAV's
official site for authoritative information.

For more details about ARPAV's copyright and licensing terms, visit their
[website](http://www.arpa.veneto.it/).



***

[commits-shield]: https://img.shields.io/github/commit-activity/y/davidecavestro/arpa-veneto-weather.svg?style=flat-square
[commits]: https://github.com/davidecavestro/arpa-veneto-weather/commits/main
[hacs]: https://www.hacs.xyz/docs/faq/custom_repositories/
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=flat-square
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/davidecavestro/arpa-veneto-weather.svg?style=flat-square
[releases-shield]: https://img.shields.io/github/release/davidecavestro/arpa-veneto-weather.svg?style=flat-square
[releases]: https://github.com/davidecavestro/arpa-veneto-weather/releases
