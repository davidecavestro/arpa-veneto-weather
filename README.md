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

- Go to _Settings_ then _Devices % services_.
- From the _Integrations_ tab click the ⊕ _Add Integration_ button on the lower right corner.
- Search for *ARPA Veneto Weather* and click the integration.
- When loaded, there will be a configuration wizard, where you must enter:

  | Parameter | Required | Default Value | Description |
  | --------- | -------- | ------------- | ----------- |
  | `Comune ID` | Yes | None | Set the municipality to use for the *forecast zone lookup*, based on [synthetic forecast by zone](https://meteo.arpa.veneto.it/?page=comuni_geo). |
  | `Zone ID` | Yes | None | Set the *forecast zone*. |
  | `Station ID` | Yes | None | Choose the Weather Station for getting *current conditions* among the available ones. Check [the meteo variables page](https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/meteo-idro-nivo/variabili_meteo). |

- Complete the wizard to save your data.
  If all goes well you should now have a new Weather entity with data from Arpav Forecast

> [!TIP]
You can configure multiple instances of the Integration, so properly name them to avoid confusion.

### Preferences

Once you have configured a station, you can control some options from ⚙ (its _Configure_ action):

- **Expose JSON extra attribute for internal forecast data**: Expose additional attributes on the weather entity used internally for forecasts
- **Expose JSON extra attribute for raw original forecast data**: Expose additional attributes on the weather entity based on the data obtained from the remote api call
- **Expose extra attributes for raw original sensor data**: Expose as sensors the data obtaining from the remote api call
- **Compute the current condition**: Expose the weather state as computed from available metrics
- **Choose stations providing air-quality data**: Since the set of [stations differs](https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/aria/qualita-aria-dati-in-diretta) between PM10, PM2.5 and Ozone, the user can choose a specific station for each of them. 
- **Current condition at night**: Choose which source describes the sky while the sun is below the horizon
- **Additional observations**: Optionally choose an aerodrome publishing METAR reports, to observe the sky and to complete the data the chosen station does not provide

## Compute the current weather condition

Since the stations don't provide data for current sky condition, the weather
state has been historically left to _Unknown_.
Since v0.5 this integration optionally computes the current sky condition
with a best-effort approach based on available sensors:
<dl>
<dt>
day - sun above the horizon
</dt>
<dd>
it compares the actual sunlight (Global Horizontal Irradiance) with the maximum expected
for the current sun position, as its elevation over the horizon and the azimuth actually reflects
the <i>latitude</i>, the <i>season</i> and the <i>time</i> of the day.<br>
Based on the nearest realtime data available for <a href="https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/meteo-idro-nivo/variabili_meteo">solar radiation</a>.
It also uses data such as <i>precipitation</i>, <i>wind speed</i> and <i>visibility</i> to make
the best possible estimate of the actual sky conditions.
</dd>
<dt>
night - sun below the horizon
</dt>
<dd>
it compares the actual night sky brightness with the maximum expected, based on the moon phase.<br>
Based on the realtime data available from the nearest station for the <a href="https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/luminosita-del-cielo/brillanza">night sky brightness</a>:
please note that this measure is not typically supplied directly by the chosen station, so we have to fallback to the nearest station providing this data.
</dd>
</dl>

> [!NOTE]
The current weather condition computation is enabled by default since v0.12.<br>
In order to disable it, go to <i>Configuration > Integrations > Arpa Veneto Weather</i>.<br>
Click on the gear on the station you are interested in.<br>
Then choose <i>Compute the current condition: &gt; <b>Don't compute</b></i>.

> [!TIP]
Choose  <i>Compute the current condition</i>: <i>From sensors
using custom thresholds</b></i> to set custom thresholds
for separately switching between <i>clear</i>, <i>partly cloudy</i> and <i>cloudy</i>
during day and night.

### The current condition at night

Daylight is measured by the station itself, so the daytime sky is inferred from
a local, near real-time observation. The night is the hard part, because no
single source works everywhere:

- the **night sky brightness** network publishes its readings in a single daily
  batch (around 09:30, standard time), so at night the latest reading normally
  describes the *previous* night rather than the current one, and is discarded
  as stale;
- the **forecast bulletin** is always available and covers the whole region, but
  it is a forecast, not an observation;
- a **METAR** report is an actual observation of the sky, published every 30
  minutes, but it comes from the nearest aerodrome, which may be tens of
  kilometres away;
- some setups are better off with **no value at all** than with a value that is
  not measured.

The choice is therefore left to the user, under _Current condition at night_:

| Option | Behaviour |
| ------ | --------- |
| _Sky brightness, forecast as a fallback_ | The default, and the historical behaviour: use the brightness reading when it is fresh enough, otherwise the bulletin |
| _Sky brightness only_ | Use the brightness reading when fresh, otherwise leave the condition unknown |
| _METAR observation, forecast as a fallback_ | Use the cloud cover observed by the configured aerodrome, and the bulletin when no report is available |
| _Forecast bulletin_ | Always use the bulletin |
| _Leave it unknown_ | Report no condition unless the station measurements alone decide it (rain, fog, wind) |

Whatever the choice, the weather entity says which one was used through its
`condition_source` attributes: see [Data provenance](#data-provenance).

## Additional observations

ARPAV stations do not observe the state of the sky, and several of them report
neither visibility nor pressure: those sensors stay `unknown`. Aerodromes do
observe all of it, and publish a
[METAR](https://en.wikipedia.org/wiki/METAR) report every 30 minutes, with cloud
cover reported layer by layer.

Under _Additional observations_ you can select one, from the list of aerodromes
around the station, **sorted by distance**. When configured, it provides:

- the **cloud coverage** of the weather entity, as a percentage of the sky;
- the **current condition at night**, if you selected the METAR option above;
- any value **missing** from the chosen ARPAV station, typically visibility and
  pressure, unless you turn that off.

Values taken from a METAR are marked with `source: metar`, so they can always
be told apart from the ones measured by the ARPAV station.

> [!IMPORTANT]
Distance matters more than it seems: an aerodrome 60 km away describes the
general state of the sky well, and local fog or low stratus poorly, which in the
Po valley is exactly the typical winter situation. The distance of each
aerodrome is shown in the selection list.

> [!TIP]
Not every aerodrome reports around the clock: the smaller ones only publish
during their opening hours, and the list says which ones are reporting at the
moment. Choosing one is perfectly fine — reports older than 90 minutes are
ignored, so outside those hours the values simply go back to being missing and
the night condition falls back to whatever you configured. A nearby aerodrome
reporting only by day can still be a better choice than a distant one reporting
always.

> [!NOTE]
Reports are retrieved from the
[Aviation Weather Center](https://aviationweather.gov/data/api/) of the US
National Weather Service, which requires no credentials, and are fetched at most
once every 10 minutes, since a METAR is issued every 30.

## Data provenance

A single weather station in Home Assistant is fed by several distinct ARPAV
networks: the [meteogram](https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/meteo-idro-nivo/variabili_meteo)
network for the observations, the [air quality](https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/aria/qualita-aria-dati-in-diretta)
network, the [night sky brightness](https://www.arpa.veneto.it/dati-ambientali/dati-in-diretta/luminosita-del-cielo/brillanza)
network and the forecast bulletin. They have different locations, different
sampling intervals and different publishing latencies, and not every value is
an observation: some are forecasts.

Every entity therefore reports where its value comes from, as extra state
attributes:

| Attribute | Description |
| --------- | ----------- |
| `source` | Origin of the value: `station`, `air_quality_station`, `sky_brightness_station`, `metar`, `forecast` or `unknown` |
| `source_name` | The reporting station, or the forecast zone |
| `source_observed_at` | When the value was observed at the origin, which can be well before the last update |

The weather entity exposes the same information for the current condition,
prefixed with `condition_`, plus `condition_source_rule`: the criterion that
decided the condition, one of `precipitation`, `visibility`, `wind`,
`solar_radiation`, `sky_brightness`, `cloud_cover` or `forecast`.

> [!TIP]
`condition_source` is the honest way to tell a measured condition from a
forecast one: for example a `cloudy` state coming from
`source: station, source_rule: solar_radiation` is measured sunlight, while
`source: forecast` means the sky could not be measured and the bulletin was
used instead.

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

## Enable Debug Logging

If logs are needed for debugging or reporting an issue, use the following configuration.yaml:

```yaml
logger:
  default: error
  logs:
    custom_components.arpa-veneto-weather: debug
```

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
