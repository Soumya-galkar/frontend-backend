from utils.superbase_client import supabase
from datetime import datetime, timezone
def save_extracted_text(document_id, pages):

    for page in pages:

        print("Saving page:", page["page_number"])

        response = supabase.table("extracted_text").insert({
            "document_id": document_id,
            "page_number": page["page_number"],
            "extracted_text": page["text"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        print(response)