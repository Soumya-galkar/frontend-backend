import json
import re

from services.gemini_service import ask_gemini


def analyze_document(text):

    prompt = f"""
You are an Industrial AI Assistant.

Analyze this industrial document and return ONLY valid JSON.

Return this schema:

{{
    "document_type":"",
    "department":"",
    "summary":"",
    "maintenance_type":"",
    "risk_level":"",
    "equipment":[],
    "keywords":[]
# }}
#     prompt = f"""
# You are an expert Industrial Knowledge Intelligence AI.

# Analyze the following industrial document and extract structured metadata.

# Return ONLY valid JSON.

# Do NOT include markdown.
# Do NOT explain anything.
# Do NOT wrap the response inside ```json.

# If any field is not found, return an empty string, empty array or empty object.

# Return EXACTLY this schema:

# {{
#     "document_type": "",

#     "department": "",

#     "summary": "",

#     "maintenance_type": "",

#     "risk_level": "",

#     "equipment": [
#         {{
#             "id": "",
#             "type": "",
#             "manufacturer": "",
#             "status": ""
#         }}
#     ],

#     "work_orders": [
#         {{
#             "id": "",
#             "priority": "",
#             "status": ""
#         }}
#     ],

#     "parameters": [
#         {{
#             "name": "",
#             "value": ""
#         }}
#     ],

#     "inspection_findings": [],

#     "regulations": [],

#     "safety_procedures": [],

#     "oem_manuals": [],

#     "technicians": [],

#     "manufacturers": [],

#     "process_units": [],

#     "locations": [],

#     "keywords": []
# }}

# Extraction Rules

# 1. Equipment
# Extract every equipment.

# Examples:
# Pump P-101
# Valve V-201
# Motor M-102
# Boiler B-01

# 2. Work Orders

# Extract all work order IDs.

# Examples

# WO-1045
# WO-5501

# If possible also detect:

# Priority

# Status

# 3. Parameters

# Extract every measurable value.

# Examples

# Pressure

# Temperature

# Flow Rate

# Voltage

# Current

# RPM

# Level

# Speed

# Example:

# Pressure -> 10 bar

# Temperature -> 85°C

# 4. Risks

# Examples

# Leakage

# Corrosion

# Fire Hazard

# Overheating

# High Pressure

# Failure

# 5. Maintenance

# Examples

# Routine Inspection

# Preventive Maintenance

# Calibration

# Lubrication

# Seal Replacement

# 6. Regulations

# Examples

# PESO

# OISD

# Factory Act

# ISO

# API

# ASME

# 7. Inspection Findings

# Extract observations.

# Example

# Seal leakage observed

# Abnormal vibration

# Bearing worn out

# 8. Industrial graph entities

# Extract safety procedures, OEM manuals, technicians, manufacturers, process units and locations when explicitly present.

# Return them in safety_procedures, oem_manuals, technicians, manufacturers, process_units and locations respectively.

# Do not infer or invent any value. Use empty arrays when it is not stated.

# 9. Keywords

# Return important technical keywords.

# 10. Summary

# Write a concise professional summary in 2–3 sentences.

# Document

# {text[:8000]}
# """
# Document:

# {text[:8000]}
# """

    response = ask_gemini(prompt, context=text[:8000])
 # Remove markdown fences if Gemini returns ```json ... ```
    response = re.sub(r"^```json|```$", "", response.strip(), flags=re.MULTILINE).strip()
    # Convert JSON string to Python dictionary
    return json.loads(response)






import json
import re

from services.gemini_service import ask_gemini


def analyze_document(text):

    prompt = f"""
You are an Industrial AI Assistant.

Analyze this industrial document and return ONLY valid JSON.

Return this schema:

{{
    "document_type":"",
    "department":"",
    "summary":"",
    "maintenance_type":"",
    "risk_level":"",
    "equipment":[],
    "keywords":[]
}}

Document:

{text[:8000]}
"""

    response = ask_gemini(prompt, context=text[:8000])
 # Remove markdown fences if Gemini returns ```json ... ```
    response = re.sub(r"^```json|```$", "", response.strip(), flags=re.MULTILINE).strip()
    # Convert JSON string to Python dictionary
    return json.loads(response)