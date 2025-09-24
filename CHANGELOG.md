## [0.7.0] - 2025-09-24
### :sparkles: New Features
- [`5ba99ec`](https://github.com/davidecavestro/arpa-veneto-weather/commit/5ba99ec9e983f1bf38ce4392fd1f64d6ad4793a0) - add pressure sensor *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :bug: Bug Fixes
- [`e1e892e`](https://github.com/davidecavestro/arpa-veneto-weather/commit/e1e892e20d2fc1b036248a63b438e832832e0697) - force precipitation probability to int *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`c0cbb29`](https://github.com/davidecavestro/arpa-veneto-weather/commit/c0cbb294ec53dc9dbf8add5ac0eef7622c180ee3) - change device info to service *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`4892ef4`](https://github.com/davidecavestro/arpa-veneto-weather/commit/4892ef4dba9782598ed0975245ed956fb9948508) - use Rome timezone to compute precipitations since midnight (see #8)  *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.6.0] - 2025-09-19
### :sparkles: New Features
- [`fafb4dc`](https://github.com/davidecavestro/arpa-veneto-weather/commit/fafb4dc97e2860a3dc43f0064608be73c0159bfc) - expose cumulative precipitation plus hourly intensity *(PR [#8](https://github.com/davidecavestro/arpa-veneto-weather/pull/8) by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`f405c99`](https://github.com/davidecavestro/arpa-veneto-weather/commit/f405c997e2e12c692c37cac4ed4408af94c7fe30) - beef up docs *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`e9704e5`](https://github.com/davidecavestro/arpa-veneto-weather/commit/e9704e5adedfae8e051bbb08726abd608e0a5dd9) - add missing deps to devcontainer *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`cfda9c9`](https://github.com/davidecavestro/arpa-veneto-weather/commit/cfda9c91e0719889ca3dddaf19bde42a313e0064) - use python 3.13 for linting *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.5.4] - 2025-09-14
### :bug: Bug Fixes
- [`f753a38`](https://github.com/davidecavestro/arpa-veneto-weather/commit/f753a38718cfdf9c6a05e97f59fc740efca0d3f8) - possible NPW on condition detection for missing data *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`accb82a`](https://github.com/davidecavestro/arpa-veneto-weather/commit/accb82aacbc5637a380e028158b08039b742f70e) - bump up HA version on requirements and switch to Trixie for dev *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.5.3] - 2025-09-03
### :wrench: Chores
- [`5ca9a97`](https://github.com/davidecavestro/arpa-veneto-weather/commit/5ca9a971b81c7b1eee5b9641c57d5b948ec080e9) - add device *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.5.2] - 2025-09-03
### :wrench: Chores
- [ 40a5d3 ](https://github.com/davidecavestro/arpa-veneto-weather/commit/40a5d3cf5cc8538664134488106f0947aa299fbb) - set custom thresholds with NumberSelector *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [ 4e9473 ](https://github.com/davidecavestro/arpa-veneto-weather/commit/4e9473f6b200c831d79fd7c6f9ab37a4df379e81) - use visibility to determine fog, wind for windy *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.5.1] - 2025-09-01
### :bug: Bug Fixes
- [`2116408`](https://github.com/davidecavestro/arpa-veneto-weather/commit/211640846471236488f7d588d2c07179a5f38651) - sky status from sensors broken during night *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.5.0] - 2025-09-01
### :sparkles: New Features
- [`7128e27`](https://github.com/davidecavestro/arpa-veneto-weather/commit/7128e2740ae0caf16c7e381344d05372028d3297) - compute current sky state from available sensors *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.4.0] - 2025-06-17
### :sparkles: New Features
- [`ea5c663`](https://github.com/davidecavestro/arpa-veneto-weather/commit/ea5c663d52eeb333f500acfc2fd33ba24936899f) - optionally expose raw sensor data *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.3.0] - 2025-06-15
### :wrench: Chores
- [`76ca91b`](https://github.com/davidecavestro/arpa-veneto-weather/commit/76ca91b7ab6de97e16935c436d6c9cb6092792e4) - add iot_class and integration_type to manifest *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`a7098bc`](https://github.com/davidecavestro/arpa-veneto-weather/commit/a7098bc55df3dd196922d2c464e84a41d396d0b1) - remove version from manifest *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`caa9654`](https://github.com/davidecavestro/arpa-veneto-weather/commit/caa965413c927dba514f277b4aa020fd189bb7c7) - restore version into manifest.json for dev time *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`06b1312`](https://github.com/davidecavestro/arpa-veneto-weather/commit/06b1312643cfe108b4a995048bbb7cebced717c5) - remove the iot_class attribute *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`dfdadc0`](https://github.com/davidecavestro/arpa-veneto-weather/commit/dfdadc08e165fbd5d1366bb7629c097bbd691804) - add forecast_reliability weather_description attrs to internal forecast representation *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`5a755aa`](https://github.com/davidecavestro/arpa-veneto-weather/commit/5a755aa4da13aac2ed2bebb230c6f4bc7f549b83) - add precipitation_description attr to internal forecast representation *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.7] - 2025-01-18
### :bug: Bug Fixes
- [`da879b4`](https://github.com/davidecavestro/arpa-veneto-weather/commit/da879b47cf8469d2151a97769805890b9b3a1f6e) - use the mean temp when exposing twice-daily ranges as daily forecasts *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`c055574`](https://github.com/davidecavestro/arpa-veneto-weather/commit/c0555748d8341148825045302e0e9f6732eedf51) - add hacs validation *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`39a60bb`](https://github.com/davidecavestro/arpa-veneto-weather/commit/39a60bb5cee6eded1bb17608f43f9b43dcc68a2f) - validate HACS just on-demand until some brand img is properly published *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.6] - 2025-01-17
### :bug: Bug Fixes
- [`af193f3`](https://github.com/davidecavestro/arpa-veneto-weather/commit/af193f33afd715dc549247cab3dac5dde2c135c8) - [#3](https://github.com/davidecavestro/arpa-veneto-weather/pull/3) provide min/max temp just when available *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.5] - 2025-01-15
### :bug: Bug Fixes
- [`de68889`](https://github.com/davidecavestro/arpa-veneto-weather/commit/de68889368aaa636515052effa194c450a734271) - missing forecast due to lack of temperature data [#3](https://github.com/davidecavestro/arpa-veneto-weather/pull/3) *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.4] - 2025-01-02
### :bug: Bug Fixes
- [`9f0ef59`](https://github.com/davidecavestro/arpa-veneto-weather/commit/9f0ef59a19cfb161ffbd046eec0c76d642f94dec) - support UV expressed in w/m2 *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.3] - 2025-01-02
### :bug: Bug Fixes
- [`5f838f2`](https://github.com/davidecavestro/arpa-veneto-weather/commit/5f838f27b2291906860a5a44f9b9db1b57cd8a75) - support UV expressed in w/m2 *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.2] - 2025-01-01
### :bug: Bug Fixes
- [`038ac61`](https://github.com/davidecavestro/arpa-veneto-weather/commit/038ac6184440a6c1362b102928df6a57748aeb1a) - temperature. visibility and precipitation missing from weather entity *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`7b62d73`](https://github.com/davidecavestro/arpa-veneto-weather/commit/7b62d73605666b362f75cab6a605d4b4e5268467) - typo on visibility IT translation *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`1a14c61`](https://github.com/davidecavestro/arpa-veneto-weather/commit/1a14c61f71b688f8f1dc66b7984207b5e1a747af) - uv index from data in MJ/m2 is wrong *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`4d8aaa8`](https://github.com/davidecavestro/arpa-veneto-weather/commit/4d8aaa8de679a356e4a3ba6494f95739234e1a2c) - code cleanup *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.1] - 2024-12-15
### :bug: Bug Fixes
- [`dec3666`](https://github.com/davidecavestro/arpa-veneto-weather/commit/dec3666e6213bf6f3db310beab9afb3cb9c053b7) - UV index unit of measure *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.2.0] - 2024-12-14
### :sparkles: New Features
- [`7e52aba`](https://github.com/davidecavestro/arpa-veneto-weather/commit/7e52aba5ffc1192c49b4afa750491fb8aacec123) - add uv_index and refine unit of measures for sensors *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.1.2] - 2024-12-08
### :bug: Bug Fixes
- [`5f1bdc2`](https://github.com/davidecavestro/arpa-veneto-weather/commit/5f1bdc21ec095418037b96c2e8b0f6a5aa145b8f) - wrong UM for weather entity wind speed and visibility *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`190f5f1`](https://github.com/davidecavestro/arpa-veneto-weather/commit/190f5f144aca5088f4c2e8a3344c5c1169b424c9) - docs reformat *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`1d0fb15`](https://github.com/davidecavestro/arpa-veneto-weather/commit/1d0fb15d093f2774995ac7f6910eead205e99cce) - refine hacs docs *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.1.1] - 2024-12-08
### :bug: Bug Fixes
- [`87ffbc3`](https://github.com/davidecavestro/arpa-veneto-weather/commit/87ffbc33688db1798c9b012628634f8199da5a91) - wrong unit of measure on sensors *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [0.1.0] - 2024-12-08
### :sparkles: New Features
- [`8db02ca`](https://github.com/davidecavestro/arpa-veneto-weather/commit/8db02cac3d41bbdf7fda670130e2b22103d8b38f) - expose forecast and current conditions from arpav rest api *(commit by [@davidecavestro](https://github.com/davidecavestro))*

[0.1.0]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.0.0...0.1.0
[0.1.1]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.1.0...0.1.1
[0.1.2]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.1.1...0.1.2
[0.2.0]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.1.2...0.2.0
[0.2.1]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.0...0.2.1
[0.2.2]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.1...0.2.2
[0.2.3]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.2...0.2.3
[0.2.4]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.3...0.2.4
[0.2.5]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.4...0.2.5
[0.2.6]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.5...0.2.6
[0.2.7]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.6...0.2.7
[0.3.0]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.2.7...0.3.0
[0.4.0]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.3.0...0.4.0
[0.5.0]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.4.0...0.5.0
[0.5.1]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.5.0...0.5.1
[0.5.3]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.5.2...0.5.3
[0.5.4]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.5.3...0.5.4
[0.6.0]: https://github.com/davidecavestro/arpa-veneto-weather/compare/0.5.4...0.6.0
