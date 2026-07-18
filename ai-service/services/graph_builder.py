"""Idempotent helpers for the existing graph_nodes and graph_edges tables."""
from utils.superbase_client import supabase


def _normalise_name(value):
    return " ".join(str(value or "").strip().split())


def get_or_create_node(node_type, node_name, metadata=None):
    """Return an existing node or create it once; empty values never produce nodes."""
    # Preserve compatibility with node types produced by earlier ingestions.
    node_type = {
        "WorkOrder": "Work Order",
        "Maintenance": "Maintenance Type",
        "Risk": "Risk Level",
        "InspectionFinding": "Inspection",
    }.get(node_type, node_type)
    name = _normalise_name(node_name)
    if not name:
        return None

    existing = (
        supabase.table("graph_nodes")
        .select("id")
        .eq("node_type", node_type)
        .eq("node_name", name)
        .execute()
    )
    if existing.data:
        return existing.data[0]["id"]

    response = supabase.table("graph_nodes").insert({
        "node_type": node_type,
        "node_name": name,
        "metadata": metadata or {},
    }).execute()
    return response.data[0]["id"]


def create_edge(source, target, relationship):
    """Create one relationship only; the same edge is safe to process repeatedly."""
    if not source or not target or not relationship:
        return None
    existing = (
        supabase.table("graph_edges")
        .select("id")
        .eq("source_node", source)
        .eq("target_node", target)
        .eq("relationship", relationship)
        .execute()
    )
    if existing.data:
        return existing.data[0]["id"]
    response = supabase.table("graph_edges").insert({
        "source_node": source,
        "target_node": target,
        "relationship": relationship,
    }).execute()
    return response.data[0]["id"]
