from utils.superbase_client import supabase
def get_all_documents():
    response = (
        supabase
        .table("documents")
        .select("*")
        .order("created_at",desc=True)
        .execute()
    )
    return response.data

def get_document_by_id(document_id):
    document = (
        supabase
        .table("documents")
        .select("*")
        .eq("id",document_id)
        .execute()
    )
    metadata = (
        supabase
        .table("document_metadata")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    )
    entities = (
        supabase
        .table("document_entities")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    )

    extracted_text = (
        supabase
        .table("extracted_text")
        .select("*")
        .eq("document_id", document_id)
        .order("page_number")
        .execute()
    )

    chunks = (
        supabase
        .table("document_chunks")
        .select("*")
        .eq("document_id", document_id)
        .order("page_number")
        .execute()
    )

    return{
        "document":document.data,
        "metadata":metadata.data,
        "entities":entities.data,
        "extracted_text":extracted_text.data,
        "chunks":chunks.data,

    }