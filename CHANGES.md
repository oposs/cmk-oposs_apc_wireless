# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### New

### Changed

### Fixed

## 0.3.1 - 2026-11-12
### Fixed
- A wireless sensor the NetBotz has no reading from had a "Temperature"
  service that was OK and showed -214748364.7 °C. That service is now
  UNKNOWN with "The device has no temperature reading from this sensor"
  and records no metric.

## 0.3.0 - 2026-11-11
### New
- The "Temperature" services show the right value for sensors on a device
  set to Fahrenheit. Before, a reading of 73.6 °F showed as 73.6 °C and the
  service went CRIT; now it shows 23.1 °C. Readings, levels and graphs stay
  in °C.

## 0.2.0 - 2026-11-06
### New
- The package carries the release version in its check plugin (`__version__`).

### Changed
- Licence is now GNU General Public License v2, matching the headers
  the source files carry. The `LICENSE` file previously held the MIT
  text, which contradicted them.

### Fixed
- The "Humidity" services showed the sensor's high temperature threshold
  in tenths of a degree (for example 300% for a threshold of 30.0 °C)
  instead of the measured humidity, so they were usually CRIT. They now
  show the humidity the sensor reports; the graph keeps the wrong values
  from before the update.
- Temperature-only wireless sensors got a "Humidity" service that was
  CRIT at 0%. After the update such a service is UNKNOWN with "Item not
  found in monitoring data". Run a service discovery on the affected
  hosts to remove the vanished "Humidity ..." services.

## 0.1.2 - 2026-04-27
### Fixed
- Metric translations for legacy stock-Checkmk `apc_symmetra_temp_wireless`
  / `apc_humidity_wireless` history are now keyed on the new
  `oposs_apc_wireless_temperature` / `oposs_apc_wireless_humidity` check
  commands so they actually fire. Previously they were keyed on the stock
  commands and Checkmk's translation lookup (an exact match on the live
  service's current check command) silently missed them — leaving the
  legacy `temp.rrd` / `humidity.rrd` files orphaned in the per-service
  directories. Note: continuous-line merge only happens if the service
  name is unchanged across the rename; if you renamed the service when
  switching off the stock plugin, the legacy RRD lives in a different
  per-service directory and the translation cannot bridge it.

## 0.1.1 - 2026-03-24
### Fixed
- Fix ruleset topic: use `Topic.ENVIRONMENTAL` instead of incorrect `Topic.ENVIRONMENT`

## 0.1.0 - 2026-03-04
### New
- Initial migration from oegig-plugins to Checkmk 2.3.x v2 API
- Single SimpleSNMPSection fetching wireless sensor table (name, temp, humidity)
- 2 check plugins: Temperature, Humidity (both item-based per sensor)
- Graphing definitions for temperature and humidity
- Humidity perfometer (0-100%)
- Metric names prefixed with `oposs_apc_` for namespace isolation
- Custom WATO rulesets for configuring temperature and humidity thresholds


