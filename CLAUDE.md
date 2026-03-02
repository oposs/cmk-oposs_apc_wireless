# cmk-oposs_apc_wireless

Checkmk SNMP plugin for APC wireless temperature and humidity sensors.
Migrated from oegig-plugins to Checkmk 2.3.x v2 API.

## Components

- `local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/agent_based/oposs_apc_wireless.py` — SNMP section + 2 check plugins
- `local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/graphing/apc_wireless.py` — metric, graph, perfometer definitions
- `local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/rulesets/apc_wireless.py` — WATO ruleset definitions for threshold configuration
- `.mkp-builder.ini` — MKP packaging config
- `.github/workflows/release.yml` — automated release workflow

## Architecture

- One `SimpleSNMPSection` fetching wireless sensor table (name, temp, humidity)
- Parse function builds dict keyed by sensor name
- 2 `CheckPlugin` module-level variables, both item-based (temperature, humidity)
- Temperature: default thresholds warn=25C, crit=30C
- Humidity: default thresholds upper warn=60%, crit=65%; lower warn=40%, crit=35%
- Custom WATO rulesets for configurable thresholds (SimpleLevels format)
- Metric prefix: `oposs_apc_`
- SNMP detection: sysObjectID starts with `.1.3.6.1.4.1.318.1.3` (APC devices)
