import re
from services.parsers.image_parser import extract_text_from_image


def parse_pid(file_path):

    pages = extract_text_from_image(file_path)

    equipment_pattern = (
    r"\b(?:"
    r"P|"
    r"V|"
    r"M|"
    r"HX|"
    r"TK|"
    r"CV|"
    r"FV|"
    r"XV|"
    r"PSV|"
    r"LT|"
    r"TT|"
    r"PT|"
    r"FT|"
    r"LIC|"
    r"PIC|"
    r"TI|"
    r"PI"
    r")-\d+\b"
    )

    for page in pages:

        text = page["text"]

        equipment = list(set(
            re.findall(
                equipment_pattern,
                text,
                re.IGNORECASE
            )
        ))

        page["equipment_tags"] = equipment

    return pages