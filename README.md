# APC Wireless Sensors Checkmk Plugin

Checkmk SNMP plugin for monitoring APC wireless temperature and humidity sensors.

## Features

Monitors APC wireless sensor pods via SNMP with 2 services per sensor:

| Service | Type | Metrics | Default Thresholds |
|---------|------|---------|-------------------|
| Temperature | Per-sensor | Temperature in C | warn 25C, crit 30C (configurable) |
| Humidity | Per-sensor | Humidity in % | upper warn 60%, crit 65%; lower warn 40%, crit 35% (configurable) |

## SNMP Detection

The plugin detects APC devices where sysObjectID (`.1.3.6.1.2.1.1.2.0`)
starts with `.1.3.6.1.4.1.318.1.3`.

Sensor data is fetched from the wireless sensor table at
`.1.3.6.1.4.1.318.1.1.10.5.1.1.1` (columns: name, temperature, humidity).

## Installation

### MKP Package (recommended)

Download the latest `.mkp` file from the
[Releases](https://github.com/oposs/cmk-oposs_apc_wireless/releases) page and
install it:

```bash
mkp install oposs_apc_wireless-<version>.mkp
```

### Manual Installation

Copy the plugin files into your Checkmk site:

```
local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/
├── agent_based/
│   └── oposs_apc_wireless.py
├── graphing/
│   └── apc_wireless.py
└── rulesets/
    └── apc_wireless.py
```

## Troubleshooting

Test SNMP connectivity:

```bash
snmpwalk -v2c -c <community> <host> .1.3.6.1.4.1.318.1.1.10.5.1.1.1
```

## License

MIT - OETIKER+PARTNER AG
