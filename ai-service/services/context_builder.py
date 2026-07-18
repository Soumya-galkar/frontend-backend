from utils.superbase_client import supabase


def build_context(chunks):
    """
    Converts retrieved chunks into a structured prompt context.
    """

    context_sections = []

    for chunk in chunks:

        document = (
            supabase
            .table("documents")
            .select("original_name")
            .eq("id", chunk["document_id"])
            .single()
            .execute()
        )

        document_name = (
            document.data["original_name"]
            if document.data
            else "Unknown Document"
        )

        section = f"""
==================================================

Document:
{document_name}

Page:
{chunk["page_number"]}

Similarity:
{round(chunk["similarity"] * 100,2)}%

Content:

{chunk["chunk_text"]}

==================================================
"""

        context_sections.append(section)

    return "\n".join(context_sections)