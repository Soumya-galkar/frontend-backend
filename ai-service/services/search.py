# from sentence_transformers import SentenceTransformer
# from utils.superbase_client import supabase

# # Load once when FastAPI starts
# model = SentenceTransformer("all-MiniLM-L6-v2")


# def create_query_embedding(question: str):
#     embedding = model.encode(question)
#     return embedding.tolist()


# def search_chunks(query_embedding, match_count=5):

#     response = supabase.rpc(
#         "match_document_chunks",
#         {
#             "query_embedding": query_embedding,
#             "match_count": match_count
#         }
#     ).execute()

#     return response.data

from sentence_transformers import SentenceTransformer
from utils.superbase_client import supabase

# Load once when FastAPI starts
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_query_embedding(question: str):
    embedding = model.encode(question)
    return embedding.tolist()


def search_chunks(query_embedding, match_count=10, similarity_threshold=0.60):
    """
    Search the most relevant chunks using pgvector.
    Returns only chunks above the similarity threshold.
    Falls back to the best 3 chunks if nothing passes the threshold.
    """

    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count
        }
    ).execute()

    chunks = response.data or []

    # Remove weak matches
    filtered_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("similarity", 0) >= similarity_threshold
    ]

    # Fallback if every chunk was filtered out
    if not filtered_chunks:
        filtered_chunks = chunks[:3]

    return filtered_chunks