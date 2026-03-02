#!/usr/bin/env python3

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic,
)


def _form_spec_temperature():
    return Dictionary(
        elements={
            "levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Temperature upper levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="\u00b0C"),
                    prefill_fixed_levels=DefaultValue((25.0, 30.0)),
                ),
                required=True,
            ),
        },
    )


rule_spec_oposs_apc_wireless_temperature = CheckParameters(
    name="oposs_apc_wireless_temperature",
    title=Title("APC Wireless Temperature Levels"),
    topic=Topic.ENVIRONMENT,
    parameter_form=_form_spec_temperature,
    condition=HostAndItemCondition(item_title=Title("Sensor name")),
)


def _form_spec_humidity():
    return Dictionary(
        elements={
            "levels_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Humidity upper levels"),
                    help_text=Help("Alert when humidity rises above these levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((60.0, 65.0)),
                ),
                required=True,
            ),
            "levels_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Humidity lower levels"),
                    help_text=Help("Alert when humidity drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((40.0, 35.0)),
                ),
                required=True,
            ),
        },
    )


rule_spec_oposs_apc_wireless_humidity = CheckParameters(
    name="oposs_apc_wireless_humidity",
    title=Title("APC Wireless Humidity Levels"),
    topic=Topic.ENVIRONMENT,
    parameter_form=_form_spec_humidity,
    condition=HostAndItemCondition(item_title=Title("Sensor name")),
)
