from utils.superbase_client import supabase


def get_dashboard():

    documents = (
        supabase
        .table("documents")
        .select("*")
        .execute()
    )

    entities = (
        supabase
        .table("document_entities")
        .select("*")
        .execute()
    )

    graph_nodes = (
        supabase
        .table("graph_nodes")
        .select("*")
        .execute()
    )

    total_documents = len(documents.data)

    processed_documents = len(
        [d for d in documents.data if d["status"] == "processed"]
    )

    processing_documents = len(
        [d for d in documents.data if d["status"] == "processing"]
    )

    total_entities = len(entities.data)

    total_equipment = len([
        n for n in graph_nodes.data
        if n["node_type"] == "Equipment"
    ])

    total_work_orders = len([
        e for e in entities.data
        if e["entity_type"] == "Work Order"
    ])

    recent_documents = sorted(
        documents.data,
        key=lambda x: x["created_at"],
        reverse=True
    )[:5]

    return {
        "total_documents": total_documents,
        "processed_documents": processed_documents,
        "processing_documents": processing_documents,
        "total_entities": total_entities,
        "total_equipment": total_equipment,
        "total_work_orders": total_work_orders,
        "recent_documents": recent_documents
    }