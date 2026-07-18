from utils.superbase_client import supabase


def save_embeddings(document_id, embedded_chunks):

    for chunk in embedded_chunks:

        supabase.table("document_chunks")\
            .update({
                "embedding": chunk["embedding"]
            })\
            .eq("document_id", document_id)\
            .eq("page_number", chunk["page_number"])\
            .eq("chunk_number", chunk["chunk_number"])\
            .execute()