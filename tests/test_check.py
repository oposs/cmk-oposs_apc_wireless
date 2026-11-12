"""Tests for the SNMP section and the two check plugins.

The sensor rows come from a real SNMP walk of the PowerNet-MIB
wirelessSensorStatusTable (.1.3.6.1.4.1.318.1.1.10.5.1.1.1), quoted in
cmk/plugins/apc/agent_based/apc_netbotz_sensors.py on Checkmk master (commit
2e2295f8). Checkmk 2.3 has no such file, and its apc_netbotz_sensors section
does not read the wireless sensors. The walk:

    .1.3.6.1.4.1.318.1.1.10.5.1.1.1.3.1 Rack 12 top     wirelessSensorStatusName
    .1.3.6.1.4.1.318.1.1.10.5.1.1.1.3.2 Rack 12 bottom
    .1.3.6.1.4.1.318.1.1.10.5.1.1.1.5.1 231             wirelessSensorStatusTemperature
    .1.3.6.1.4.1.318.1.1.10.5.1.1.1.5.2 224
    .1.3.6.1.4.1.318.1.1.10.5.1.1.1.8.1 41              wirelessSensorStatusHumidity
    .1.3.6.1.4.1.318.1.1.10.5.1.1.1.8.2 0

"Rack 12 top" is an NBWS100H (temperature and humidity), "Rack 12 bottom"
an NBWS100T (temperature only), which reports a humidity of 0. Temperatures
are tenths of a degree, humidity whole percent.

The scale of the temperatures is the one the device is set to, given by
emsStatusSysTempUnits (.1.3.6.1.4.1.318.1.1.10.3.12.11.0): celsius(1) or
fahrenheit(2). PowerNet-MIB on wirelessSensorStatusTemperature:

    "The current temperature are displayed in tenths of degrees in the scale
    shown in the emsStatusSysTempUnits OID (Celsius or Fahrenheit)."
"""

import importlib.util
import json
import pathlib
import re
import sys

import pytest
from cmk.agent_based.v2 import Metric, Result, Service, State

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/agent_based/oposs_apc_wireless.py"

SYS_OBJECT_ID = ".1.3.6.1.2.1.1.2.0"

# Rows as the parse function receives them: name, temperature, humidity.
TOP = ["Rack 12 top", "231", "41"]
BOTTOM = ["Rack 12 bottom", "224", "0"]

# emsStatusSysTempUnits as the parse function receives it.
CELSIUS = [["1"]]
FAHRENHEIT = [["2"]]

TEMP_DEFAULTS = {"levels": ("fixed", (25.0, 30.0))}
HUM_DEFAULTS = {
    "levels_upper": ("fixed", (60.0, 65.0)),
    "levels_lower": ("fixed", (40.0, 35.0)),
}


@pytest.fixture(scope="module")
def check():
    name = "test_oposs_apc_wireless_check"
    spec = importlib.util.spec_from_file_location(name, CHECK)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(name, None)


def _detects(spec, oid_values):
    """Evaluate an SNMP detect spec the way Checkmk does: OR of ANDs."""
    for conjunction in spec:
        if all(
            bool(re.fullmatch(regex, oid_values.get(oid, ""), re.DOTALL)) is expected
            for oid, regex, expected in conjunction
        ):
            return True
    return False


def _fetch(check):
    """The sensor table, the first SNMPTree of the section."""
    return check.snmp_section_oposs_apc_wireless.fetch[0]


def _parse(check, rows, units=CELSIUS):
    return check.parse_oposs_apc_wireless([rows, units])


def _temp(check, row, params=TEMP_DEFAULTS, units=CELSIUS):
    section = _parse(check, [row], units)
    return list(check.check_oposs_apc_wireless_temperature(row[0], params, section))


def _hum(check, row, params=HUM_DEFAULTS):
    section = _parse(check, [row])
    return list(check.check_oposs_apc_wireless_humidity(row[0], params, section))


def _state(results):
    return max((r.state for r in results if isinstance(r, Result)), key=int)


# ---------------------------------------------------------------------------
# SNMP section
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sys_object_id", [
    ".1.3.6.1.4.1.318.1.3.27",      # APC Smart-UPS with network management card
])
def test_detects_apc_devices(check, sys_object_id):
    detect = check.snmp_section_oposs_apc_wireless.detect
    assert _detects(detect, {SYS_OBJECT_ID: sys_object_id})


@pytest.mark.parametrize("sys_object_id", [
    ".1.3.6.1.4.1.8072.3.2.10",     # net-snmp on Linux
    ".1.3.6.1.4.1.3180.1.3",        # a different enterprise that shares the digits
    "",
])
def test_ignores_other_devices(check, sys_object_id):
    detect = check.snmp_section_oposs_apc_wireless.detect
    assert not _detects(detect, {SYS_OBJECT_ID: sys_object_id})


def test_fetches_the_wireless_sensor_table(check):
    fetch = _fetch(check)
    assert fetch.base == ".1.3.6.1.4.1.318.1.1.10.5.1.1.1"
    assert [o.column for o in fetch.oids][:2] == ["3", "5"]  # Name, Temperature


def test_fetches_humidity_from_the_humidity_column(check):
    fetch = _fetch(check)
    assert [o.column for o in fetch.oids] == ["3", "5", "8"]


def test_fetches_the_temperature_scale(check):
    (_sensors, units) = check.snmp_section_oposs_apc_wireless.fetch
    assert units.base == ".1.3.6.1.4.1.318.1.1.10.3.12"
    assert [o.column for o in units.oids] == ["11.0"]  # emsStatusSysTempUnits


def test_parse_real_walk(check):
    assert _parse(check, [TOP, BOTTOM]) == {
        "Rack 12 top": {"temperature": 23.1, "humidity": 41.0},
        "Rack 12 bottom": {"temperature": 22.4, "humidity": None},
    }


def test_parse_fahrenheit_device(check):
    # The same sensors on a device set to Fahrenheit: 73.6 °F and 72.3 °F.
    section = _parse(check, [["Rack 12 top", "736", "41"], ["Rack 12 bottom", "723", "0"]],
                     FAHRENHEIT)
    assert section["Rack 12 top"]["temperature"] == pytest.approx(23.1111, abs=1e-3)
    assert section["Rack 12 bottom"]["temperature"] == pytest.approx(22.3889, abs=1e-3)
    assert section["Rack 12 top"]["humidity"] == 41.0


@pytest.mark.parametrize("units", [
    [],                             # device without emsStatusSysTempUnits
    [[""]],
    [["3"]],                        # not in the MIB
])
def test_parse_without_a_known_scale_assumes_celsius(check, units):
    assert _parse(check, [TOP], units)["Rack 12 top"]["temperature"] == 23.1


def test_parse_negative_temperature(check):
    section = _parse(check, [["Freezer", "-185", "-1"]])
    assert section == {"Freezer": {"temperature": -18.5, "humidity": None}}


@pytest.mark.parametrize("row", [
    [],
    ["Rack 12 top", "231"],         # short row
    ["", "231", "41"],              # sensor without a name
    ["   ", "231", "41"],
])
def test_parse_skips_unusable_rows(check, row):
    assert _parse(check, [row]) == {}


def test_parse_garbage_values(check):
    section = _parse(check, [["Rack 1", "n/a", ""]])
    assert section == {"Rack 1": {"temperature": None, "humidity": None}}


def test_parse_strips_the_name(check):
    assert list(_parse(check, [[" Rack 12 top ", "231", "41"]])) == ["Rack 12 top"]


def test_parse_empty_table(check):
    assert _parse(check, []) == {}


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def test_discover_temperature(check):
    section = _parse(check, [TOP, BOTTOM])
    assert list(check.discover_oposs_apc_wireless_temperature(section)) == [
        Service(item="Rack 12 top"),
        Service(item="Rack 12 bottom"),
    ]


def test_discover_skips_missing_values(check):
    section = _parse(check, [["Rack 1", "n/a", "-1"]])
    assert list(check.discover_oposs_apc_wireless_temperature(section)) == []
    assert list(check.discover_oposs_apc_wireless_humidity(section)) == []


def test_discover_humidity_sensor(check):
    section = _parse(check, [TOP])
    assert list(check.discover_oposs_apc_wireless_humidity(section)) == [Service(item="Rack 12 top")]


def test_temperature_only_sensor_has_no_humidity_service(check):
    section = _parse(check, [BOTTOM])
    assert list(check.discover_oposs_apc_wireless_humidity(section)) == []


def test_discover_nothing_from_an_empty_section(check):
    assert list(check.discover_oposs_apc_wireless_temperature({})) == []
    assert list(check.discover_oposs_apc_wireless_humidity({})) == []


# ---------------------------------------------------------------------------
# Temperature check
# ---------------------------------------------------------------------------

def test_temperature_ok(check):
    assert _temp(check, TOP) == [
        Result(state=State.OK, summary="Temperature: 23.1 °C"),
        Metric("oposs_apc_temperature", 23.1, levels=(25.0, 30.0)),
    ]


@pytest.mark.parametrize("raw, state", [
    ("249", State.OK),
    ("250", State.WARN),            # warn at 25.0 degrees
    ("299", State.WARN),
    ("300", State.CRIT),            # crit at 30.0 degrees
    ("-50", State.OK),
])
def test_temperature_levels(check, raw, state):
    assert _state(_temp(check, ["Rack 1", raw, "41"])) == state


def test_temperature_custom_levels(check):
    results = _temp(check, TOP, {"levels": ("fixed", (20.0, 23.0))})
    assert _state(results) == State.CRIT
    assert "warn/crit at 20.0 °C/23.0 °C" in results[0].summary


def test_temperature_without_levels(check):
    results = _temp(check, ["Rack 1", "450", "41"], {"levels": ("no_levels", None)})
    assert results == [
        Result(state=State.OK, summary="Temperature: 45.0 °C"),
        Metric("oposs_apc_temperature", 45.0),
    ]


def test_temperature_fahrenheit_device(check):
    # 86.0 °F is 30.0 °C, the default crit level.
    assert _temp(check, ["Rack 1", "860", "41"], units=FAHRENHEIT) == [
        Result(state=State.CRIT, summary="Temperature: 30.0 °C (warn/crit at 25.0 °C/30.0 °C)"),
        Metric("oposs_apc_temperature", 30.0, levels=(25.0, 30.0)),
    ]


def test_temperature_fahrenheit_device_ok(check):
    # 73.6 °F would be CRIT if it were read as °C.
    assert _state(_temp(check, ["Rack 1", "736", "41"], units=FAHRENHEIT)) == State.OK


def test_temperature_missing_item(check):
    section = _parse(check, [TOP])
    assert list(check.check_oposs_apc_wireless_temperature("Gone", TEMP_DEFAULTS, section)) == []


def test_temperature_unreadable_value(check):
    assert _temp(check, ["Rack 1", "n/a", "41"]) == []


# ---------------------------------------------------------------------------
# Humidity check
# ---------------------------------------------------------------------------

def test_humidity_ok(check):
    assert _hum(check, TOP) == [
        Result(state=State.OK, summary="Humidity: 41%"),
        Metric("oposs_apc_humidity", 41.0, levels=(60.0, 65.0)),
    ]


@pytest.mark.parametrize("raw, state", [
    ("34", State.CRIT),             # crit below 35
    ("35", State.WARN),
    ("39", State.WARN),             # warn below 40
    ("40", State.OK),
    ("59", State.OK),
    ("60", State.WARN),             # warn at 60
    ("65", State.CRIT),             # crit at 65
    ("100", State.CRIT),
])
def test_humidity_levels(check, raw, state):
    assert _state(_hum(check, ["Rack 1", "231", raw])) == state


def test_humidity_level_text(check):
    (result, _metric) = _hum(check, ["Rack 1", "231", "37"])
    assert result.summary == "Humidity: 37% (warn/crit below 40%/35%)"


def test_humidity_without_levels(check):
    params = {"levels_upper": ("no_levels", None), "levels_lower": ("no_levels", None)}
    assert _hum(check, ["Rack 1", "231", "99"], params) == [
        Result(state=State.OK, summary="Humidity: 99%"),
        Metric("oposs_apc_humidity", 99.0),
    ]


def test_humidity_not_measured(check):
    assert _hum(check, ["Rack 1", "231", "-1"]) == []


def test_humidity_missing_item(check):
    section = _parse(check, [TOP])
    assert list(check.check_oposs_apc_wireless_humidity("Gone", HUM_DEFAULTS, section)) == []


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------

def test_check_plugins(check):
    temp = check.check_plugin_oposs_apc_wireless_temperature
    hum = check.check_plugin_oposs_apc_wireless_humidity
    assert temp.service_name == "Temperature %s"
    assert hum.service_name == "Humidity %s"
    assert temp.sections == hum.sections == ["oposs_apc_wireless"]
    assert temp.check_default_parameters == TEMP_DEFAULTS
    assert hum.check_default_parameters == HUM_DEFAULTS


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

def test_check_carries_the_released_version():
    # The publish check fails on main when a version file disagrees with
    # the newest released CHANGES.md heading.
    check = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_apc_wireless/agent_based/oposs_apc_wireless.py"
    released = re.search(r"^## (\d+\.\d+\.\d+)", (ROOT / "CHANGES.md").read_text(),
                         flags=re.MULTILINE).group(1)
    assert re.search(rf'^__version__ = "{re.escape(released)}"$', check.read_text(), flags=re.MULTILINE)


def test_release_writes_version_into_check(tmp_path):
    """Apply the version_files entry of .github/repo-infra.json to the check
    module, as Create release PR does (a multiline regex, first match)"""
    config = json.loads((ROOT / ".github/repo-infra.json").read_text())
    (spec,) = [f for f in config["version_files"] if (ROOT / f["path"]) == CHECK]
    stamped = re.sub(spec["pattern"], spec["replacement"].replace("$VERSION", "9.8.7"),
                     CHECK.read_text(), count=1, flags=re.MULTILINE)
    assert re.search(spec["verify"].replace("$VERSION", re.escape("9.8.7")), stamped, flags=re.MULTILINE)
    copy = tmp_path / "stamped_check.py"
    copy.write_text(stamped)
    module_spec = importlib.util.spec_from_file_location("stamped_check", copy)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    assert module.__version__ == "9.8.7"
