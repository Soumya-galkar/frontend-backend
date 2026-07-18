"""Evidence-grounded Maintenance Intelligence reporting."""
import json
import re

from utils.superbase_client import supabase

MISSING = "Information not available in uploaded documents."


def _query(table, **filters):
    query = supabase.table(table).select("*")
    for field, value in filters.items():
        query = query.eq(field, value)
    return query.execute().data or []


def _first(items):
    return items[0] if items else {}


def get_equipment(equipment_id):
    """Return the graph equipment node and its persisted metadata."""
    response = (
        supabase.table("graph_nodes").select("*")
        .eq("node_type", "Equipment").eq("node_name", equipment_id).execute()
    )
    equipment = _first(response.data)
    if not equipment:
        return None
    return equipment


def get_connected_nodes(equipment_node_id):
    """Read all first-hop graph relationships in either direction."""
    outgoing = _query("graph_edges", source_node=equipment_node_id)
    incoming = _query("graph_edges", target_node=equipment_node_id)
    connections = []
    for edge in outgoing + incoming:
        other_id = edge["target_node"] if edge["source_node"] == equipment_node_id else edge["source_node"]
        node = _first(_query("graph_nodes", id=other_id))
        if node:
            connections.append({"relationship": edge["relationship"], "direction": "outgoing" if edge["source_node"] == equipment_node_id else "incoming", "node": node})
    return connections


def get_related_documents(connections):
    """Resolve graph-linked Document nodes into document records."""
    names = {item["node"]["node_name"] for item in connections if item["node"].get("node_type") == "Document"}
    documents = []
    for name in names:
        result = supabase.table("documents").select("*").eq("original_name", name).execute().data or []
        documents.extend(result)
    return documents


def get_work_orders(connections):
    """Return graph-backed work orders and preserve node metadata where present."""
    orders = []
    for item in connections:
        node = item["node"]
        if node.get("node_type") == "Work Order":
            details = node.get("metadata") or {}
            orders.append({
                "id": node["node_name"],
                "status": details.get("status", MISSING),
                "priority": details.get("priority", MISSING),
                "date": details.get("date", MISSING),
                "summary": details.get("summary", MISSING),
            })
    return orders


def get_maintenance_history(connections):
    """Collect graph maintenance and inspection evidence without inventing events."""
    history = []
    inspections = []
    for item in connections:
        node = item["node"]
        node_type = node.get("node_type")
        if node_type == "Maintenance Type":
            history.append({"activity": node["node_name"], "evidence": item["relationship"]})
        elif node_type == "Inspection":
            inspections.append({"finding": node["node_name"], "evidence": item["relationship"]})
    return history, inspections


def get_rag_context(equipment_id):
    """Find semantically related maintenance evidence using the existing pgvector RPC."""
    from services.search import create_query_embedding, search_chunks
    query = f"{equipment_id} maintenance work orders inspections failures risks pressure temperature safety spare parts"
    chunks = search_chunks(create_query_embedding(query), match_count=15, similarity_threshold=0.35)
    document_ids = {chunk.get("document_id") for chunk in chunks if chunk.get("document_id")}
    documents = {doc_id: _first(_query("documents", id=doc_id)) for doc_id in document_ids}
    sources = [
        {
            "document_id": chunk.get("document_id"),
            "document": documents.get(chunk.get("document_id"), {}).get("original_name", "Unknown document"),
            "page_number": chunk.get("page_number"),
            "similarity": round(float(chunk.get("similarity", 0)), 3),
        }
        for chunk in chunks
    ]
    context = "\n\n".join(
        f"Document: {source['document']} | Page: {source['page_number']} | Similarity: {source['similarity']}\n{chunk.get('chunk_text', '')}"
        for source, chunk in zip(sources, chunks)
    )
    return context, sources, [document for document in documents.values() if document]


def _json_response(prompt):
    # Import lazily so route registration and read-only data helpers do not
    # fail at application startup when Gemini is intentionally unavailable.
    from services.gemini_service import client
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.text.strip(), flags=re.IGNORECASE)
    return json.loads(raw)


def generate_maintenance_report(equipment, connections, work_orders, history, inspections, context, sources):
    """Ask Gemini for structured conclusions strictly grounded in retrieved evidence."""
    graph_evidence = [
        {"type": item["node"].get("node_type"), "name": item["node"].get("node_name"), "relationship": item["relationship"], "metadata": item["node"].get("metadata") or {}}
        for item in connections
    ]
    prompt = f"""
You are a maintenance reliability engineer. Return ONLY valid JSON, with no markdown.
Use ONLY the EVIDENCE supplied below. Never infer missing facts.
For every unavailable textual field use exactly: {MISSING!r}
For unavailable lists use []. Health must be Healthy, Attention Required, Critical, or {MISSING!r}.
Risk level must be Low, Medium, High, Critical, or {MISSING!r}.

Return exactly this object:
{{
  "equipment": {{"name":"", "type":"", "department":"", "location":"", "current_status":"", "manufacturer":"", "design_parameters":[]}},
  "health": {{"status":"", "reason":""}},
  "risk": {{"level":"", "reason":""}},
  "failure_prediction": {{"predictions":[{{"failure":"", "evidence":"", "confidence":"High|Medium|Low"}}]}},
  "maintenance_history": [{{"activity":"", "evidence":""}}],
  "inspection_summary": [{{"finding":"", "abnormality":""}}],
  "work_orders": [{{"id":"", "status":"", "priority":"", "date":"", "summary":""}}],
  "root_cause_analysis": [{{"possible_cause":"", "evidence":"", "confidence":"High|Medium|Low"}}],
  "recommendations": {{"immediate":[], "within_7_days":[], "within_30_days":[], "preventive_actions":[], "long_term":[]}},
  "required_spares": [],
  "safety_precautions": [],
  "connected_documents": []
}}

EQUIPMENT NODE: {json.dumps(equipment, default=str)}
GRAPH EVIDENCE: {json.dumps(graph_evidence, default=str)}
WORK ORDER EVIDENCE: {json.dumps(work_orders, default=str)}
MAINTENANCE HISTORY: {json.dumps(history, default=str)}
INSPECTIONS: {json.dumps(inspections, default=str)}
RAG EVIDENCE:\n{context or MISSING}
"""
    report = _json_response(prompt)
    report["sources"] = sources
    return report


def build_maintenance_report(equipment_id):
    equipment = get_equipment(equipment_id)
    if not equipment:
        return None
    connections = get_connected_nodes(equipment["id"])
    work_orders = get_work_orders(connections)
    history, inspections = get_maintenance_history(connections)
    context, sources, rag_documents = get_rag_context(equipment_id)
    report = generate_maintenance_report(equipment, connections, work_orders, history, inspections, context, sources)
    graph_documents = get_related_documents(connections)
    all_documents = {doc.get("id"): doc for doc in graph_documents + rag_documents if doc}
    report["connected_documents"] = [
        {"id": doc.get("id"), "name": doc.get("original_name"), "status": doc.get("status"), "file_type": doc.get("file_type")}
        for doc in all_documents.values()
    ]
    report["work_orders"] = report.get("work_orders") or work_orders
    report["maintenance_history"] = report.get("maintenance_history") or history
    report["inspection_summary"] = report.get("inspection_summary") or inspections
    return report
