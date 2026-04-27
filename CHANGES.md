# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### New

### Changed

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


