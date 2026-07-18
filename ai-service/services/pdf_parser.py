# import fitz  # PyMuPDF


# def extract_text_from_pdf(pdf_path: str):

#     text = ""

#     doc = fitz.open(pdf_path)

#     for page in doc:
#         text += page.get_text()

#     doc.close()

#     return text


import fitz

def extract_text_from_pdf(pdf_path):

    document = fitz.open(pdf_path)

    pages = []

    for i, page in enumerate(document):

        pages.append({
            "page_number": i + 1,
            "text": page.get_text()
        })

    document.close()

    return pages