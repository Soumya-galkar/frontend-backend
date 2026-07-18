from utils.superbase_client import supabase

def save_chunks(document_id, chunks):

    for chunk in chunks:

        supabase.table("document_chunks").insert({

            "document_id": document_id,

            "page_number": chunk["page_number"],

            "chunk_number": chunk["chunk_number"],

            "chunk_text": chunk["chunk_text"]

        }).execute()