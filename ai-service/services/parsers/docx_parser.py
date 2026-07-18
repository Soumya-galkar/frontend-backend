from docx import Document


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.

    Returns:
        [
            {
                "page_number": 1,
                "text": "..."
            }
        ]
    """

    doc = Document(file_path)

    text = []

    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text)

    return [
        {
            "page_number": 1,
            "text": "\n".join(text)
        }
    ]