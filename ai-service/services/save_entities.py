from utils.superbase_client import supabase

def save_entities(document_id, page_number, entities):

    print("Saving entities:", entities)

    rows = []

    for entity in entities:
        rows.append({
            "document_id": document_id,
            "page_number": page_number,
            "entity_type": entity["entity_type"],
            "entity_value": entity["entity_value"]
        })

    print(rows)

    if rows:
        response = supabase.table("document_entities").insert(rows).execute()
        print(response)