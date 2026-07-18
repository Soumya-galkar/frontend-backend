from PIL import Image
import pytesseract

# Change this path if Tesseract is installed elsewhere
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = r"D:\OCR_ENGINE\tesseract.exe"


def extract_text_from_image(file_path):
    """
    Extract text from an image using OCR.
    Returns the same format as other parsers.
    """

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return [
        {
            "page_number": 1,
            "text": text
        }
    ]