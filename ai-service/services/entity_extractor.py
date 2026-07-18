import re


def extract_entities(text):
    print("========== ENTITY EXTRACTOR ==========")
    print(text[:300])  # First 300 characters

    entities = []

    # Equipment IDs
    equipment_pattern = r"\b[A-Z]+-\d+\b"

    for match in re.findall(equipment_pattern, text):
        entities.append({
            "entity_type": "Equipment",
            "entity_value": match
        })

    # Pressure
    pressure_pattern = r"\b\d+(\.\d+)?\s?(bar|psi|kPa)\b"

    for match in re.finditer(pressure_pattern, text, re.IGNORECASE):
        entities.append({
            "entity_type": "Pressure",
            "entity_value": match.group()
        })

    # Temperature
    temperature_pattern = r"\b\d+(\.\d+)?\s?°?\s?(C|F)\b"

    for match in re.finditer(temperature_pattern, text, re.IGNORECASE):
        entities.append({
            "entity_type": "Temperature",
            "entity_value": match.group()
        })

    # Work Orders
    work_order_pattern = r"\bWO-\d+\b"

    for match in re.findall(work_order_pattern, text):
        entities.append({
            "entity_type": "Work Order",
            "entity_value": match
        })
    print("Extracted Entities:", entities)
    return entities