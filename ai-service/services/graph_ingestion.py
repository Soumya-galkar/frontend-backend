"""Build the industrial knowledge graph from document-analyzer metadata."""
from services.graph_builder import create_edge, get_or_create_node


def _items(value):
    if not value:
        return []
    return value if isinstance(value, list) else [value]


def _name(value, *keys):
    if isinstance(value, dict):
        for key in keys:
            if value.get(key):
                return str(value[key]).strip()
        return ""
    return str(value).strip() if value else ""


def _parameter_nodes(parameters):
    pressures, temperatures = [], []
    for parameter in _items(parameters):
        label = _name(parameter, "name", "parameter", "type")
        value = _name(parameter, "value", "reading")
        node_name = " ".join(part for part in (label, value) if part)
        kind = label.lower()
        if "pressure" in kind:
            pressures.append(get_or_create_node("Pressure", node_name, parameter if isinstance(parameter, dict) else {}))
        elif "temperature" in kind or "temp" in kind:
            temperatures.append(get_or_create_node("Temperature", node_name, parameter if isinstance(parameter, dict) else {}))
    return pressures, temperatures


def ingest_document_graph(document_name, metadata):
    """Create all available domain nodes and deterministic relationships for one document."""
    document_id = get_or_create_node("Document", document_name, {"document_type": metadata.get("document_type", "")})
    equipment_nodes = []
    for equipment in _items(metadata.get("equipment")):
        equipment_name = _name(equipment, "id", "name", "equipment_id")
        node_id = get_or_create_node("Equipment", equipment_name, equipment if isinstance(equipment, dict) else {})
        if node_id:
            equipment_nodes.append(node_id)
            create_edge(node_id, document_id, "MENTIONED_IN")
            create_edge(document_id, node_id, "DESCRIBES")

    def attach_to_equipment(node_type, values, relationship, direction="equipment_to_node", keys=("id", "name", "value", "description")):
        for value in _items(values):
            node_id = get_or_create_node(node_type, _name(value, *keys), value if isinstance(value, dict) else {})
            for equipment_id in equipment_nodes:
                create_edge(node_id, equipment_id, relationship) if direction == "node_to_equipment" else create_edge(equipment_id, node_id, relationship)
            if node_id:
                create_edge(document_id, node_id, "CONTAINS")

    attach_to_equipment("Work Order", metadata.get("work_orders"), "HAS_WORK_ORDER")
    attach_to_equipment("Department", metadata.get("department"), "BELONGS_TO")
    attach_to_equipment("Maintenance Type", metadata.get("maintenance_type"), "REQUIRES")
    attach_to_equipment("Risk Level", metadata.get("risk_level"), "HAS_RISK")
    pressure_nodes, temperature_nodes = _parameter_nodes(metadata.get("parameters"))
    for equipment_id in equipment_nodes:
        for node_id in pressure_nodes + temperature_nodes:
            create_edge(equipment_id, node_id, "OPERATES_AT")
    attach_to_equipment("Inspection", metadata.get("inspection_findings"), "INSPECTED", "node_to_equipment")
    attach_to_equipment("Safety Procedure", metadata.get("safety_procedures") or metadata.get("regulations"), "GOVERNS", "node_to_equipment")
    attach_to_equipment("OEM Manual", metadata.get("oem_manuals"), "DOCUMENTED_BY", "node_to_equipment")
    attach_to_equipment("Technician", metadata.get("technicians"), "MAINTAINED", "node_to_equipment")
    attach_to_equipment("Manufacturer", metadata.get("manufacturers"), "MANUFACTURED_BY")
    attach_to_equipment("Process Unit", metadata.get("process_units"), "PART_OF")
    attach_to_equipment("Location", metadata.get("locations"), "LOCATED_AT")

    # Manufacturer found on individual equipment records is also graph-worthy.
    for equipment, equipment_id in zip(_items(metadata.get("equipment")), equipment_nodes):
        manufacturer = _name(equipment, "manufacturer")
        manufacturer_id = get_or_create_node("Manufacturer", manufacturer)
        create_edge(equipment_id, manufacturer_id, "MANUFACTURED_BY")
    return {"document_node": document_id, "equipment_nodes": equipment_nodes}
