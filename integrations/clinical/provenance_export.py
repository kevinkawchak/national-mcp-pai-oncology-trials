"""Provenance export adapter.

Supports W3C PROV-N export, graph visualization data, and
lineage report generation in multiple formats (JSON, PROV-N,
DOT graph) for the National MCP PAI Oncology Trials platform.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExportFormat(Enum):
    """Supported provenance export formats."""

    JSON = "json"
    PROV_N = "prov_n"
    DOT = "dot"


class NodeType(Enum):
    """W3C PROV node types."""

    ENTITY = "entity"
    ACTIVITY = "activity"
    AGENT = "agent"


class EdgeType(Enum):
    """W3C PROV relationship types."""

    WAS_GENERATED_BY = "wasGeneratedBy"
    USED = "used"
    WAS_DERIVED_FROM = "wasDerivedFrom"
    WAS_ATTRIBUTED_TO = "wasAttributedTo"
    WAS_ASSOCIATED_WITH = "wasAssociatedWith"
    ACTED_ON_BEHALF_OF = "actedOnBehalfOf"
    WAS_INFORMED_BY = "wasInformedBy"


@dataclass(frozen=True)
class ProvenanceNode:
    """A node in the provenance graph."""

    node_id: str
    node_type: NodeType
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass(frozen=True)
class ProvenanceEdge:
    """A directed edge in the provenance graph."""

    source_id: str
    target_id: str
    edge_type: EdgeType
    attributes: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class ProvenanceGraph:
    """An in-memory provenance graph."""

    nodes: list[ProvenanceNode] = field(default_factory=list)
    edges: list[ProvenanceEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: ProvenanceNode) -> None:
        """Append a node to the graph."""
        self.nodes.append(node)

    def add_edge(self, edge: ProvenanceEdge) -> None:
        """Append an edge to the graph."""
        self.edges.append(edge)


# -- format renderers --------------------------------------


def _render_prov_n(graph: ProvenanceGraph) -> str:
    """Render a provenance graph in W3C PROV-N notation."""
    lines: list[str] = ["document"]
    for node in graph.nodes:
        attrs = ", ".join(f'{k}="{v}"' for k, v in node.attributes.items())
        attr_str = f" [{attrs}]" if attrs else ""
        lines.append(f"  {node.node_type.value}({node.node_id}{attr_str})")
    for edge in graph.edges:
        lines.append(f"  {edge.edge_type.value}({edge.target_id}, {edge.source_id})")
    lines.append("endDocument")
    return "\n".join(lines)


def _render_dot(graph: ProvenanceGraph) -> str:
    """Render a provenance graph in Graphviz DOT format."""
    lines: list[str] = ["digraph provenance {"]
    lines.append("  rankdir=BT;")
    shape_map: dict[NodeType, str] = {
        NodeType.ENTITY: "ellipse",
        NodeType.ACTIVITY: "box",
        NodeType.AGENT: "house",
    }
    for node in graph.nodes:
        shape = shape_map.get(node.node_type, "ellipse")
        label = node.label.replace('"', '\\"')
        lines.append(f'  "{node.node_id}" [label="{label}", shape={shape}];')
    for edge in graph.edges:
        label = edge.edge_type.value
        lines.append(f'  "{edge.source_id}" -> "{edge.target_id}" [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)


def _render_json(graph: ProvenanceGraph) -> str:
    """Render a provenance graph as a JSON string."""
    data: dict[str, Any] = {
        "nodes": [
            {
                "id": n.node_id,
                "type": n.node_type.value,
                "label": n.label,
                "attributes": n.attributes,
                "timestamp": n.timestamp,
            }
            for n in graph.nodes
        ],
        "edges": [
            {
                "source": e.source_id,
                "target": e.target_id,
                "type": e.edge_type.value,
                "attributes": e.attributes,
                "timestamp": e.timestamp,
            }
            for e in graph.edges
        ],
        "metadata": graph.metadata,
    }
    return json.dumps(data, indent=2)


def render_graph(
    graph: ProvenanceGraph,
    fmt: ExportFormat,
) -> str:
    """Render *graph* in the requested format.

    Parameters
    ----------
    graph:
        The provenance graph to render.
    fmt:
        Desired output format.

    Returns
    -------
    str
        Serialized provenance data.

    Raises
    ------
    ValueError
        If *fmt* is not supported.
    """
    renderers = {
        ExportFormat.JSON: _render_json,
        ExportFormat.PROV_N: _render_prov_n,
        ExportFormat.DOT: _render_dot,
    }
    renderer = renderers.get(fmt)
    if renderer is None:
        raise ValueError(f"Unsupported format: {fmt}")
    return renderer(graph)


class ProvenanceExportAdapter(ABC):
    """Abstract adapter for provenance data export.

    Implementations retrieve provenance records from the
    platform's audit/lineage store and render them in the
    requested format.
    """

    @abstractmethod
    async def get_graph(
        self,
        resource_id: str,
        *,
        depth: int = -1,
    ) -> ProvenanceGraph:
        """Build the provenance graph for a resource.

        Parameters
        ----------
        resource_id:
            Identifier of the root entity.
        depth:
            Maximum traversal depth (``-1`` for unlimited).

        Returns
        -------
        ProvenanceGraph
            The assembled provenance graph.
        """

    async def export(
        self,
        resource_id: str,
        fmt: ExportFormat = ExportFormat.JSON,
        *,
        depth: int = -1,
    ) -> str:
        """Export provenance data for a resource.

        Parameters
        ----------
        resource_id:
            Identifier of the root entity.
        fmt:
            Desired output format.
        depth:
            Maximum traversal depth.

        Returns
        -------
        str
            Rendered provenance data.
        """
        graph = await self.get_graph(resource_id, depth=depth)
        return render_graph(graph, fmt)

    @abstractmethod
    async def generate_lineage_report(
        self,
        resource_id: str,
        fmt: ExportFormat = ExportFormat.JSON,
    ) -> dict[str, Any]:
        """Generate a comprehensive lineage report.

        Returns
        -------
        dict[str, Any]
            Report payload containing rendered lineage data
            and summary statistics.
        """
