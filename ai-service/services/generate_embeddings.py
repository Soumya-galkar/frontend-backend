from sentence_transformers import SentenceTransformer

# Load model only once
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks):
    """
    Generates embeddings for every chunk.
    """

    embedded_chunks = []

    for chunk in chunks:

        embedding = model.encode(
            chunk["chunk_text"]
        ).tolist()

        embedded_chunks.append({

            "page_number": chunk["page_number"],

            "chunk_number": chunk["chunk_number"],

            "chunk_text": chunk["chunk_text"],

            "embedding": embedding

        })

    return embedded_chunks