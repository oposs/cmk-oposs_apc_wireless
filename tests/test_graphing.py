"""Metric names: prefixed, declared, and translated from the old names."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.agent_based.v2 import Metric
from cmk.graphing.v1 import graphs, metrics, perfometers, translations

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_apc_wireless"


def _load(path):
    name = "test_graphing_" + path.stem + "_" + path.parent.name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_apc_wireless.py")


@pytest.fixture(scope="module")
def graphing_objects():
    objects = []
    for path in sorted((PLUGIN / "graphing").glob("*.py")):
        objects.extend(vars(_load(path)).values())
    return objects


@pytest.fixture(scope="module")
def declared(graphing_objects):
    return {o.name for o in graphing_objects if isinstance(o, metrics.Metric)}


@pytest.fixture(scope="module")
def emitted(check):
    """Every metric the two checks yield for a sensor with both readings."""
    section = check.parse_oposs_apc_wireless([[["Rack 12 top", "231", "41"]], [["1"]]])
    out = list(check.check_oposs_apc_wireless_temperature(
        "Rack 12 top", check.check_plugin_oposs_apc_wireless_temperature.check_default_parameters, section))
    out += list(check.check_oposs_apc_wireless_humidity(
        "Rack 12 top", check.check_plugin_oposs_apc_wireless_humidity.check_default_parameters, section))
    return [m.name for m in out if isinstance(m, Metric)]


def test_emitted_metrics(emitted):
    assert emitted == ["oposs_apc_temperature", "oposs_apc_humidity"]


def test_every_emitted_metric_is_declared(emitted, declared):
    assert sorted(set(emitted) - declared) == []


def test_every_declared_metric_is_emitted(emitted, declared):
    assert sorted(declared - set(emitted)) == []


def test_every_declared_name_is_prefixed(graphing_objects):
    kinds = (metrics.Metric, graphs.Graph, perfometers.Perfometer, translations.Translation)
    names = [o.name for o in graphing_objects if isinstance(o, kinds)]
    assert names
    assert [n for n in names if not n.startswith("oposs_apc_")] == []


def test_graphs_and_perfometers_use_declared_metrics(graphing_objects, declared):
    used = set()
    for o in graphing_objects:
        if isinstance(o, graphs.Graph):
            used.update(o.simple_lines)
        elif isinstance(o, perfometers.Perfometer):
            used.update(o.segments)
    assert used
    assert sorted(used - declared) == []


def test_old_names_translate_to_declared_metrics(graphing_objects, declared):
    found = {
        o.name: o for o in graphing_objects if isinstance(o, translations.Translation)
    }
    expected = {
        "oposs_apc_wireless_temperature": ("temp", "oposs_apc_temperature"),
        "oposs_apc_wireless_humidity": ("humidity", "oposs_apc_humidity"),
    }
    assert set(found) == set(expected)
    for name, (old, new) in expected.items():
        translation = found[name]
        # The lookup key is the check command a live service runs today.
        assert translation.check_commands == [translations.PassiveCheck(name)]
        assert translation.translations == {old: translations.RenameTo(new)}
        assert new in declared
