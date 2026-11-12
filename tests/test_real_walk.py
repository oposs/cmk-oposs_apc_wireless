"""Tests against a real SNMP walk of an APC NetBotz Rack Monitor 250 (NBRK0250).

The walk came from a production device, set to Celsius, with one wireless
sensor that the device has no reading from. It is cut down to the OIDs the
plugin fetches plus sysDescr and sysObjectID, and anonymized: the serial
number in sysDescr and the sensor name (it carries the sensor's radio
address) are replaced.

In the walk that sensor is inactive: wirelessSensorStatusCommStatus (column
11) is inactive(0) and wirelessSensorStatusAlarmStatus (column 23) is 4096,
bit 13 "sensor inactive". The plugin does not fetch these columns, so they
are left out below.

For comparison the same walk shows the wired probe of the rack monitor at
33 °C and 22 % in emsProbeStatusTable (.1.3.6.1.4.1.318.1.1.10.3.13) and in
the table Checkmk's own apc_symmetra_temp and apc_humidity read
(.1.3.6.1.4.1.318.1.1.10.4.2.3.1). The plugin does not read that probe.
"""

import importlib.util
import pathlib
import re
import sys

import pytest
from cmk.agent_based.v2 import Result, Service, State

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/agent_based/oposs_apc_wireless.py"

WALK = """\
.1.3.6.1.2.1.1.1.0 APC Web/SNMP Management Card (MB:v4.1.0 PF:v6.8.2 PN:apc_hw05_aos_682.bin AF1:v6.8.0 AN1:apc_hw05_nb250_680.bin MN:NBRK0250 HR:HW05 SN: XX0000000000 MD:09/20/2020)
.1.3.6.1.2.1.1.2.0 .1.3.6.1.4.1.318.1.3.8.5
.1.3.6.1.4.1.318.1.1.10.3.12.11.0 1
.1.3.6.1.4.1.318.1.1.10.5.1.1.1.3.1 Wireless_000001
.1.3.6.1.4.1.318.1.1.10.5.1.1.1.5.1 -2147483647
.1.3.6.1.4.1.318.1.1.10.5.1.1.1.8.1 -1
"""

SENSOR = "Wireless_000001"
TEMP_DEFAULTS = {"levels": ("fixed", (25.0, 30.0))}


def _walk():
    rows = {}
    for line in WALK.splitlines():
        oid, _, value = line.partition(" ")
        rows[oid] = value
    return rows


def _table(walk, base, columns):
    """Build a string table the way Checkmk fetches an SNMPTree: one row per
    index, one value per column, in the order the columns are given."""
    indices = []
    for oid in walk:
        for column in columns:
            prefix = f"{base}.{column}."
            if oid.startswith(prefix):
                index = oid[len(prefix):]
                if index not in indices:
                    indices.append(index)
    return [[walk.get(f"{base}.{column}.{index}", "") for column in columns]
            for index in indices]


@pytest.fixture(scope="module")
def check():
    name = "test_oposs_apc_wireless_real_walk"
    spec = importlib.util.spec_from_file_location(name, CHECK)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(name, None)


@pytest.fixture(scope="module")
def string_table(check):
    walk = _walk()
    tables = []
    for tree in check.snmp_section_oposs_apc_wireless.fetch:
        columns = [o.column for o in tree.oids]
        if all(c.endswith(".0") for c in columns):
            tables.append([[walk.get(f"{tree.base}.{c}", "") for c in columns]])
        else:
            tables.append(_table(walk, tree.base, columns))
    return tables


@pytest.fixture(scope="module")
def section(check, string_table):
    return check.parse_oposs_apc_wireless(string_table)


def test_detects_the_real_device(check):
    walk = _walk()
    detect = check.snmp_section_oposs_apc_wireless.detect
    assert any(
        all(bool(re.fullmatch(regex, walk.get(oid, ""), re.DOTALL)) is expected
            for oid, regex, expected in conjunction)
        for conjunction in detect
    )


def test_real_device_is_set_to_celsius(string_table):
    # emsStatusSysTempUnits celsius(1); the wired probe reads 33 in both
    # emsProbeStatusTable and the table that reports degrees Celsius only.
    assert string_table[1] == [["1"]]


def test_parse_real_walk(section):
    assert section == {
        SENSOR: {"temperature": None, "humidity": None, "no_reading": True},
    }


def test_sensor_without_reading_keeps_its_temperature_service(check, section):
    assert list(check.discover_oposs_apc_wireless_temperature(section)) == [Service(item=SENSOR)]


def test_sensor_without_reading_has_no_humidity_service(check, section):
    assert list(check.discover_oposs_apc_wireless_humidity(section)) == []


def test_sensor_without_reading_is_unknown(check, section):
    assert list(check.check_oposs_apc_wireless_temperature(SENSOR, TEMP_DEFAULTS, section)) == [
        Result(state=State.UNKNOWN,
               summary="The device has no temperature reading from this sensor"),
    ]


def test_sentinel_is_not_converted_on_a_fahrenheit_device(check):
    section = check.parse_oposs_apc_wireless([[[SENSOR, "-2147483647", "-1"]], [["2"]]])
    assert section[SENSOR]["no_reading"] is True
    assert section[SENSOR]["temperature"] is None
