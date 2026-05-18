"""Shared helpers for repository diagrams.

Anything that gets reused across multiple diagrams (custom clusters, common
styles, group factories) should live here so individual diagram scripts stay
short and consistent.

Usage from a diagram script:

    from _shared import default_graph_attrs, region_cluster

`scripts/render_diagrams.sh` runs each diagram script from its source directory,
so importing `_shared` works without extra sys.path manipulation as long as the
script lives under `diagrams/python/<category>/`.
"""

from __future__ import annotations

# Sensible defaults so every diagram looks like it came from the same repo.
default_graph_attrs: dict[str, str] = {
    "fontname": "Helvetica",
    "fontsize": "12",
    "pad": "0.4",
    "splines": "spline",
    "nodesep": "0.5",
    "ranksep": "0.7",
}

default_node_attrs: dict[str, str] = {
    "fontname": "Helvetica",
    "fontsize": "11",
}

default_edge_attrs: dict[str, str] = {
    "fontname": "Helvetica",
    "fontsize": "10",
}
