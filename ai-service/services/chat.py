from services.search import (
    create_query_embedding,
    search_chunks
)

from services.gemini_service import ask_gemini


def chat(question):

    # Create embedding
    query_embedding = create_query_embedding(question)

    # Search similar chunks
    chunks = search_chunks(query_embedding)

    if not chunks:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents.",
            "sources": []
        }

    context = "\n\n".join(
        chunk["chunk_text"]
        for chunk in chunks
    )

    prompt = f"""
You are an Industrial AI Assistant.

Answer ONLY using the information below.

If the answer is not available,
say "I don't know based on the uploaded documents."

Context:

{context}

Question:

{question}
"""

    answer = ask_gemini(prompt,context)

    return {
        "answer": answer,
        "sources": chunks
    }