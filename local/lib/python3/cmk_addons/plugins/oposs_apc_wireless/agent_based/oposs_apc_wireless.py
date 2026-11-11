from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
    SNMPSection,
    SNMPTree,
    check_levels,
    startswith,
)

# Create release PR writes the released version here (version_files in
# .github/repo-infra.json)
__version__ = "0.3.0"

Section = dict[str, dict[str, float | None]]


# emsStatusSysTempUnits: the scale the device is set to show temperatures in
_FAHRENHEIT = "2"


def parse_oposs_apc_wireless(string_table: list) -> Section:
    """Parse SNMP data from APC wireless temperature/humidity sensors.

    The sensors report temperatures in the scale the device is set to
    (emsStatusSysTempUnits). Without that value they are taken as Celsius.
    """
    sensors, units = string_table
    fahrenheit = bool(units and units[0] and units[0][0].strip() == _FAHRENHEIT)
    section: Section = {}
    for row in sensors:
        if len(row) < 3:
            continue
        name = row[0].strip()
        if not name:
            continue
        try:
            temp = int(row[1]) / 10.0
            if fahrenheit:
                temp = (temp - 32.0) * 5.0 / 9.0
        except (ValueError, TypeError):
            temp = None
        try:
            humidity = int(row[2])
            # A temperature-only sensor (NBWS100T) reports 0
            if humidity <= 0:
                humidity = None
            else:
                humidity = float(humidity)
        except (ValueError, TypeError):
            humidity = None
        section[name] = {"temperature": temp, "humidity": humidity}
    return section


snmp_section_oposs_apc_wireless = SNMPSection(
    name="oposs_apc_wireless",
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.318.1.3"),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.318.1.1.10.5.1.1.1",
            oids=["3", "5", "8"],  # Name, Temperature, Humidity
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.318.1.1.10.3.12",
            oids=["11.0"],  # emsStatusSysTempUnits
        ),
    ],
    parse_function=parse_oposs_apc_wireless,
)


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------

def discover_oposs_apc_wireless_temperature(
    section: Section,
) -> DiscoveryResult:
    for name, data in section.items():
        if data.get("temperature") is not None:
            yield Service(item=name)


def check_oposs_apc_wireless_temperature(
    item: str, params: dict, section: Section,
) -> CheckResult:
    data = section.get(item)
    if not data or data.get("temperature") is None:
        return
    yield from check_levels(
        value=data["temperature"],
        levels_upper=params.get("levels"),
        metric_name="oposs_apc_temperature",
        render_func=lambda v: f"{v:.1f} \u00b0C",
        label="Temperature",
    )


check_plugin_oposs_apc_wireless_temperature = CheckPlugin(
    name="oposs_apc_wireless_temperature",
    sections=["oposs_apc_wireless"],
    service_name="Temperature %s",
    discovery_function=discover_oposs_apc_wireless_temperature,
    check_function=check_oposs_apc_wireless_temperature,
    check_default_parameters={"levels": ("fixed", (25.0, 30.0))},
    check_ruleset_name="oposs_apc_wireless_temperature",
)


# ---------------------------------------------------------------------------
# Humidity
# ---------------------------------------------------------------------------

def discover_oposs_apc_wireless_humidity(
    section: Section,
) -> DiscoveryResult:
    for name, data in section.items():
        if data.get("humidity") is not None:
            yield Service(item=name)


def check_oposs_apc_wireless_humidity(
    item: str, params: dict, section: Section,
) -> CheckResult:
    data = section.get(item)
    if not data or data.get("humidity") is None:
        return
    yield from check_levels(
        value=data["humidity"],
        levels_upper=params.get("levels_upper"),
        levels_lower=params.get("levels_lower"),
        metric_name="oposs_apc_humidity",
        render_func=lambda v: f"{v:.0f}%",
        label="Humidity",
    )


check_plugin_oposs_apc_wireless_humidity = CheckPlugin(
    name="oposs_apc_wireless_humidity",
    sections=["oposs_apc_wireless"],
    service_name="Humidity %s",
    discovery_function=discover_oposs_apc_wireless_humidity,
    check_function=check_oposs_apc_wireless_humidity,
    check_default_parameters={
        "levels_upper": ("fixed", (60.0, 65.0)),
        "levels_lower": ("fixed", (40.0, 35.0)),
    },
    check_ruleset_name="oposs_apc_wireless_humidity",
)
