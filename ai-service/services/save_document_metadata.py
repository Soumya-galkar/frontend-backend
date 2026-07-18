from utils.superbase_client import supabase


def save_document_metadata(document_id, metadata):

   response = supabase.table("document_metadata").insert({

        "document_id": document_id,

        "document_type": metadata.get("document_type", ""),

        "department": metadata.get("department", ""),

        "summary": metadata.get("summary", ""),

        "maintenance_type": metadata.get("maintenance_type", ""),

        "risk_level": metadata.get("risk_level", ""),

        "equipment": metadata.get("equipment", []),

        "keywords": metadata.get("keywords", [])

    }).execute()
   
   return response
