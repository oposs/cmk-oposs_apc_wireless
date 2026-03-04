#!/usr/bin/env python3
# Copyright (C) 2025 OETIKER+PARTNER AG - License: GNU General Public License v2

"""Metric translations for the APC wireless sensor plugin rename."""

from cmk.graphing.v1 import translations

translation_apc_symmetra_temp_wireless = translations.Translation(
    name="apc_symmetra_temp_wireless",
    check_commands=[translations.PassiveCheck("apc_symmetra_temp_wireless")],
    translations={
        "temp": translations.RenameTo("oposs_apc_temperature"),
    },
)

translation_apc_humidity_wireless = translations.Translation(
    name="apc_humidity_wireless",
    check_commands=[translations.PassiveCheck("apc_humidity_wireless")],
    translations={
        "humidity": translations.RenameTo("oposs_apc_humidity"),
    },
)
