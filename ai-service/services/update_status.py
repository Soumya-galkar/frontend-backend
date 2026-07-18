from utils.superbase_client import supabase


def update_status(document_id, status):

    supabase.table("documents")\
        .update({
            "status": status
        })\
        .eq("id", document_id)\
        .execute()