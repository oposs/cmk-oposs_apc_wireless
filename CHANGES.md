# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### New

### Changed

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


