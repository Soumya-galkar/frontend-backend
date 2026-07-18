"""Aggregate the existing ingestion outputs for the Document Viewer API."""
from utils.superbase_client import supabase


def get_document_viewer(document_id: str):
    """Return one document and all viewer-ready data without changing schema."""
    document_response = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .single()
        .execute()
    )
    if not document_response.data:
        return None

    pages_response = (
        supabase.table("extracted_text")
        .select("page_number, extracted_text, text")
        .eq("document_id", document_id)
        .order("page_number")
        .execute()
    )
    metadata_response = (
        supabase.table("document_metadata")
        .select("*")
        .eq("document_id", document_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    entities_response = (
        supabase.table("document_entities")
        .select("*")
        .eq("document_id", document_id)
        .order("page_number")
        .execute()
    )

    metadata = metadata_response.data[0] if metadata_response.data else {}
    pages = [
        {
            "page_number": row["page_number"],
            "text": row.get("extracted_text") or row.get("text") or "",
        }
        for row in pages_response.data
    ]

    return {
        "document": document_response.data,
        "pages": pages,
        "summary": metadata.get("summary", ""),
        "metadata": metadata,
        "entities": entities_response.data,
    }
