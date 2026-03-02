#!/usr/bin/env python3

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    Metric,
    Unit,
)
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.perfometers import Perfometer, FocusRange, Closed

# Units
unit_celsius = Unit(DecimalNotation("\u00b0C"))
unit_percentage = Unit(DecimalNotation("%"))

# Metrics
metric_oposs_apc_temperature = Metric(
    name="oposs_apc_temperature",
    title=Title("Temperature"),
    unit=unit_celsius,
    color=Color.ORANGE,
)

metric_oposs_apc_humidity = Metric(
    name="oposs_apc_humidity",
    title=Title("Humidity"),
    unit=unit_percentage,
    color=Color.CYAN,
)

# Graphs
graph_oposs_apc_temperature = Graph(
    name="oposs_apc_temperature",
    title=Title("APC Wireless Temperature"),
    simple_lines=["oposs_apc_temperature"],
    minimal_range=MinimalRange(lower=0, upper=50),
)

graph_oposs_apc_humidity = Graph(
    name="oposs_apc_humidity",
    title=Title("APC Wireless Humidity"),
    simple_lines=["oposs_apc_humidity"],
    minimal_range=MinimalRange(lower=0, upper=100),
)

# Perfometers
perfometer_oposs_apc_humidity = Perfometer(
    name="oposs_apc_humidity",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(100),
    ),
    segments=["oposs_apc_humidity"],
)
