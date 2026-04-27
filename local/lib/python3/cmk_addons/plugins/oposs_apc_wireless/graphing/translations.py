#!/usr/bin/env python3
# Copyright (C) 2025 OETIKER+PARTNER AG - License: GNU General Public License v2

"""Metric translations for the APC wireless sensor plugin rename.

The legacy stock Checkmk checks were ``apc_symmetra_temp_wireless`` and
``apc_humidity_wireless``, emitting generic ``temp`` / ``humidity`` metrics.
This plugin re-implements the same probes under
``oposs_apc_wireless_temperature`` and ``oposs_apc_wireless_humidity`` and
emits the prefixed metrics ``oposs_apc_temperature`` /
``oposs_apc_humidity``.

IMPORTANT: ``check_commands`` references the *new* check command (the one
the live service has today). Checkmk's translation lookup is an exact
dict-key match against that command — keying on the legacy name (the now-
unused stock check) would silently miss for every service. Whether the
legacy RRD data actually merges into the new graph also depends on the
service name being unchanged across the rename; if you renamed the service
when migrating off the stock plugin, the legacy RRD lives in a different
per-service directory and the translation cannot bridge it.
"""

from cmk.graphing.v1 import translations

translation_oposs_apc_wireless_temperature = translations.Translation(
    name="oposs_apc_wireless_temperature",
    check_commands=[translations.PassiveCheck("oposs_apc_wireless_temperature")],
    translations={
        "temp": translations.RenameTo("oposs_apc_temperature"),
    },
)

translation_oposs_apc_wireless_humidity = translations.Translation(
    name="oposs_apc_wireless_humidity",
    check_commands=[translations.PassiveCheck("oposs_apc_wireless_humidity")],
    translations={
        "humidity": translations.RenameTo("oposs_apc_humidity"),
    },
)
