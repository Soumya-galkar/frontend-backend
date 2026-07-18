def chunk_text(pages, chunk_size=700, overlap=100):
    """
    Split extracted text into overlapping chunks.
    """

    chunks = []

    for page in pages:

        text = page["text"]

        start = 0
        chunk_no = 1

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append({
                "page_number": page["page_number"],
                "chunk_number": chunk_no,
                "chunk_text": chunk
            })

            start += chunk_size - overlap
            chunk_no += 1

    return chunks