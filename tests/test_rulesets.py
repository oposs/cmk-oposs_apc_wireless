"""The rule forms build, and every check default has a matching form field."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.rulesets.v1.form_specs import LevelDirection
from cmk.rulesets.v1.rule_specs import HostAndItemCondition

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_apc_wireless"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rulesets():
    return _load(PLUGIN / "rulesets/apc_wireless.py", "test_oposs_apc_wireless_rulesets")


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_apc_wireless.py", "test_oposs_apc_wireless_check_rs")


PAIRS = [
    ("check_plugin_oposs_apc_wireless_temperature", "rule_spec_oposs_apc_wireless_temperature"),
    ("check_plugin_oposs_apc_wireless_humidity", "rule_spec_oposs_apc_wireless_humidity"),
]


@pytest.mark.parametrize("plugin_name, rule_name", PAIRS)
def test_ruleset_name_matches(rulesets, check, plugin_name, rule_name):
    assert getattr(check, plugin_name).check_ruleset_name == getattr(rulesets, rule_name).name


@pytest.mark.parametrize("plugin_name, rule_name", PAIRS)
def test_defaults_match_form(rulesets, check, plugin_name, rule_name):
    defaults = getattr(check, plugin_name).check_default_parameters
    form = getattr(rulesets, rule_name).parameter_form()
    assert set(defaults) == set(form.elements)
    for key, default in defaults.items():
        spec = form.elements[key].parameter_form
        assert ("fixed", spec.prefill_fixed_levels.value) == default, key


@pytest.mark.parametrize("_plugin_name, rule_name", PAIRS)
def test_rules_take_the_sensor_name(rulesets, _plugin_name, rule_name):
    # Both checks yield Service(item=...), so the rule needs an item condition
    assert isinstance(getattr(rulesets, rule_name).condition, HostAndItemCondition)


def test_humidity_level_directions(rulesets):
    form = rulesets.rule_spec_oposs_apc_wireless_humidity.parameter_form()
    assert form.elements["levels_upper"].parameter_form.level_direction == LevelDirection.UPPER
    assert form.elements["levels_lower"].parameter_form.level_direction == LevelDirection.LOWER
