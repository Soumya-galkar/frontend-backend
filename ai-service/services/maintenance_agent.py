# """
# Maintenance Intelligence Agent Service.
# Provides comprehensive asset health analytics, root cause analysis, 
# and maintenance strategy synthesis by unifying Vector Embeddings and Knowledge Graphs.
# """

# import logging
# from typing import Dict, Any, List

# # Importing existing interface utilities explicitly as requested
# from services.graph_query import get_graph
# from services.rag import create_query_embedding
# from services.search import search_chunks
# from services.gemini_service import ask_gemini

# # Import the specific error class thrown by PostgREST
# from postgrest.exceptions import APIError

# # Initialize logging configuration
# logger = logging.getLogger(__name__)


# def compute_confidence_level(chunks: List[Dict[str, Any]]) -> str:
#     """
#     Computes a programmatic confidence category based on vector search similarity metrics.
    
#     Ranges:
#     - Similarity > 0.90 -> High
#     - Similarity 0.75 to 0.90 -> Medium
#     - Similarity < 0.75 -> Low
#     """
#     if not chunks:
#         return "Low"
        
#     top_score = chunks[0].get("similarity", chunks[0].get("score", 0.0))
    
#     if top_score > 0.90:
#         return "High"
#     elif top_score >= 0.75:
#         return "Medium"
#     else:
#         return "Low"


# def build_structured_context(graph_data: Dict[str, Any], chunks: List[Dict[str, Any]]) -> str:
#     """
#     Normalizes Knowledge Graph nodes/edges and Vector Database text chunks into a 
#     structured, high-density analytical context payload for the LLM core.
#     """
#     context_lines = []
    
#     # 1. Structural Knowledge Graph Extraction
#     context_lines.append("=== KNOWLEDGE GRAPH TOPOLOGY ===")
#     nodes = graph_data.get("nodes", [])
#     edges = graph_data.get("edges", [])
    
#     context_lines.append(f"Found {len(nodes)} interconnected entities and {len(edges)} operational relationships.")
    
#     categories = [
#         "Equipment", "Document", "Department", "Maintenance", 
#         "Risk", "WorkOrder", "Parameter", "InspectionFinding", "Regulation"
#     ]
    
#     for category in categories:
#         matched_nodes = [n for n in nodes if n.get("type") == category or n.get("label") == category]
#         if matched_nodes:
#             context_lines.append(f"\n[{category} Entities]")
#             for node in matched_nodes:
#                 properties = node.get("properties", node.get("data", {}))
#                 props_str = ", ".join([f"{k}: {v}" for k, v in properties.items()])
#                 context_lines.append(f"  - Node ID: {node.get('id')} | Details: {props_str}")

#     if edges:
#         context_lines.append("\n[Operational Topology & Dependencies]")
#         for edge in edges:
#             context_lines.append(f"  - Relationship: {edge.get('source')} -> [{edge.get('type', 'RELATED_TO')}] -> {edge.get('target')}")

#     # 2. Unstructured/Semi-Structured Vector Space Documentation Extraction
#     context_lines.append("\n=== UNSTRUCTURED DOCUMENTATION CHUNKS ===")
#     for idx, chunk in enumerate(chunks, 1):
#         text_content = chunk.get("content", chunk.get("text", "No text provided."))
#         metadata = chunk.get("metadata", {})
        
#         doc_name = metadata.get("document_name", metadata.get("source", "Unknown Document"))
#         page_num = metadata.get("page_number", metadata.get("page", "N/A"))
#         chunk_id = chunk.get("id", f"chk-{idx}")
#         score = chunk.get("similarity", chunk.get("score", 0.0))
        
#         context_lines.append(f"\n[Source Piece #{idx}] (ID: {chunk_id}, Doc: {doc_name}, Page: {page_num}, Match Weight: {score:.4f})")
#         context_lines.append(f"Content: {text_content}")

#     return "\n".join(context_lines)


# def generate_maintenance_report(equipment_name: str) -> Dict[str, Any]:
#     """
#     Generates a high-fidelity diagnostic and prognostic maintenance report 
#     by contextualizing structural graphs with semantic vector spaces.
    
#     Safely bypasses PGRST116 row-coercion errors if the equipment doesn't exist in the graph yet.
#     """
#     logger.info(f"Initiating Maintenance Intelligence parsing for asset identity: '{equipment_name}'")
    
#     # Declare empty fallback data structure for the graph layer
#     graph_data = {"nodes": [], "edges": []}
    
#     try:
#         # STEP 1: Load Knowledge Graph Ecosystem with safe exception handling
#         try:
#             logger.debug(f"Querying asset topological relationships via graph database for: {equipment_name}")
#             graph_data = get_graph(equipment_name)
#         except APIError as api_err:
#             # Check specifically for PostgREST 0 rows exception (PGRST116)
#             if api_err.code == "PGRST116":
#                 logger.warning(f"Asset '{equipment_name}' not mapped inside Knowledge Graph tables yet. Continuing with empty graph layer.")
#             else:
#                 # Re-raise if it's an authentication or connection issue
#                 raise api_err
        
#         # STEP 2: Execute Hybrid Vector Space Evaluation
#         logger.debug(f"Calculating multi-dimensional query embedding tensor for: {equipment_name}")
#         query_embedding = create_query_embedding(equipment_name)
        
#         logger.debug("Executing similarity matrix search across vector table shards")
#         chunks = search_chunks(query_embedding)
        
#         # STEP 3: Synthesize Uniform Target Context
#         structured_context = build_structured_context(graph_data, chunks)
        
#         # STEP 4: Programmatic Determination of Semantic Matching Confidence
#         confidence_metric = compute_confidence_level(chunks)
        
#         # STEP 5: Construct Systemic Prompt Framework with Zero-Hallucination Boundaries
#         prompt = f"""
# You are acting as a Principal Reliability Engineer and Senior Predictive Maintenance Director in a critical asset environment.
# Your task is to generate a comprehensive, definitive Engineering Diagnostic and Maintenance Strategy Report for the following target asset: "{equipment_name}".

# You must construct this entire document relying EXCLUSIVELY on the verified context payload provided below. 

# =========================================
# VERIFIED ENGINEERING DATA CONTEXT PAYLOAD
# =========================================
# {structured_context}
# =========================================

# -----------------------------------------
# STRICT OPERATIONAL DIRECTIVES & GUARDRAILS
# -----------------------------------------
# 1. ZERO HALLUCINATION CONSTRAINT: Do not synthesize, assume, project, or invent engineering metrics, history, data parameters, or procedures.
# 2. MISSING DATA HANDLING: If a specific block of information, structural node, parameter value, or historical event requested in the format layout is absent from the provided context payload, write EXACTLY: "Information not found in uploaded documents." under that section header.
# 3. ABSOLUTE SOURCE CITATION RULE: Every diagnostic claim, status statement, risk classification, and maintenance recommendation MUST be explicitly cross-referenced to its origin inline.
#    - For Graph entities, cite the Node ID and Entity Class (e.g., [Graph Node: WO-1045, WorkOrder]).
#    - For Unstructured chunks, cite the filename and page number precisely as provided (e.g., [Inspection Report Page 3], [OEM Manual Page 12]).
# 4. OUTPUT FORMATTING: Your output must be exclusively standard raw Markdown string formatting. Do not wrap the final output inside any markdown outer wrappers like ```markdown or ```json blocks. Start directly with the first h1 header.

# You must format the generated report exactly according to this structural specification:

# # Equipment Summary
# **Current Health:** [Insert state + Citation]
# **Current Status:** [Insert state + Citation]
# **Equipment Type:** [Insert classification + Citation]
# **Risk Level:** [Insert category + Citation]

# ---

# # Root Cause Analysis
# **Possible Root Cause:** [Insert engineering deduction + Citation]
# **Supporting Evidence:** [Provide explicit structural/textual verification details + Citation]
# **Confidence:** [High / Medium / Low based on data depth and consistency]

# ---

# # Maintenance Recommendation
# **Immediate Actions:** [List clear tactical operations + Citation]
# **Preventive Maintenance:** [List time/metric based actions + Citation]
# **Long-term Maintenance:** [List strategic lifecycle recommendations + Citation]

# ---

# # Risk Assessment
# **Risk Score:** [Numeric or explicit scale + Citation]
# **Severity:** [Impact ranking + Citation]
# **Likelihood:** [Probability assessment + Citation]
# **Impact:** [Description of system dependencies + Citation]

# ---

# # Maintenance Schedule
# **Immediate:** [Actionable tasks within 24-48 hours + Citation]
# **30 Days:** [Tasks + Citation]
# **90 Days:** [Tasks + Citation]
# **180 Days:** [Tasks + Citation]
# **Annual:** [Tasks + Citation]

# ---

# # Required Spare Parts
# [Enumerate part names, item codes, quantities found in context. If none found, write "Information not found in uploaded documents."]

# ---

# # Safety Precautions
# [Detail specific lockout/tagout (LOTO), PPE, isolation protocols, or regulatory safety criteria. If none found, write "Information not found in uploaded documents."]

# ---

# # Evidence Used
# [Compile an explicit bulleted list of every reference document, log sheet, work order item, and graph entity parsed to build the report.]
# """

#         logger.debug("Dispatching unified diagnostic prompt to Gemini 2.5 Flash Engine")
        
#         report_markdown = ask_gemini(question=f"Generate maintenance report for {equipment_name}", context=prompt)
        
#         extracted_sources = []
#         for c in chunks:
#             meta = c.get("metadata", {})
#             source_entry = {
#                 "document_name": meta.get("document_name", meta.get("source", "Unknown Document")),
#                 "page_number": meta.get("page_number", meta.get("page", "N/A")),
#                 "similarity_score": c.get("similarity", c.get("score", 0.0))
#             }
#             if source_entry not in extracted_sources:
#                 extracted_sources.append(source_entry)

#         return {
#             "equipment": equipment_name,
#             "report": report_markdown,
#             "graph": graph_data,
#             "sources": extracted_sources,
#             "confidence": confidence_metric
#         }

#     except Exception as e:
#         logger.error(f"Fatal error executing AI Maintenance Agent logic for {equipment_name}: {str(e)}", exc_info=True)
#         raise e

from utils.superbase_client import supabase
from services.rag import ask_gemini

def get_equipment(equipment_name: str):
    """
    Fetch an equipment node from the knowledge graph.
    """

    response = (
        supabase
        .table("graph_nodes")
        .select("*")
        .eq("node_type", "Equipment")
        .eq("node_name", equipment_name)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]

print(get_equipment("P-101"))

from utils.superbase_client import supabase


def get_related_documents(equipment_id: str):
    """
    Return every document connected to an equipment node.
    """

    edges = (
        supabase
        .table("graph_edges")
        .select("*")
        .eq("source_node", equipment_id)
        .eq("relationship", "MENTIONED_IN")
        .execute()
    )

    documents = []

    for edge in edges.data:

        doc = (
            supabase
            .table("graph_nodes")
            .select("*")
            .eq("id", edge["target_node"])
            .single()
            .execute()
        )

        if doc.data:
            documents.append(doc.data)

    return documents

equipment = get_equipment("P-101")

docs = get_related_documents(equipment["id"])

print(docs)

def get_related_chunks(documents):
    """
    Fetch all chunks belonging to the related documents.
    """

    if not documents:
        return []

    document_ids = [doc["id"] for doc in documents]

    response = (
        supabase
        .table("document_chunks")
        .select("*")
        .in_("document_id", document_ids)
        .order("page_number")
        .order("chunk_number")
        .execute()
    )

    return response.data
def build_context(equipment, documents, chunks):

    context = []

    context.append("=" * 60)
    context.append("EQUIPMENT INFORMATION")
    context.append("=" * 60)

    context.append(f"Equipment : {equipment['node_name']}")
    context.append(f"Metadata  : {equipment.get('metadata', {})}")

    context.append("")

    context.append("=" * 60)
    context.append("RELATED DOCUMENTS")
    context.append("=" * 60)

    for doc in documents:

        context.append(f"- {doc['node_name']}")

    context.append("")

    context.append("=" * 60)
    context.append("DOCUMENT CONTENT")
    context.append("=" * 60)

    for chunk in chunks:

        context.append(
            f"""
Document ID : {chunk["document_id"]}
Page        : {chunk["page_number"]}

{chunk["chunk_text"]}

---------------------------------------------------------
"""
        )

    return "\n".join(context)


def generate_maintenance_report(equipment_name):

    equipment = get_equipment(equipment_name)

    if equipment is None:
        return {
            "error": "Equipment not found"
        }

    documents = get_related_documents(equipment["id"])

    chunks = get_related_chunks(documents)

    context = build_context(
        equipment,
        documents,
        chunks
    )

    prompt = f"""
You are a Senior Industrial Reliability Engineer.

Use ONLY the information below.

{context}

Generate:

# Equipment Summary

# Current Health

# Root Cause Analysis

# Maintenance Recommendation

# Risk Assessment

# Maintenance Schedule

# Safety Precautions

If any information is missing,
explicitly say

Information not found in uploaded documents.

Never hallucinate.
"""

    report = ask_gemini(prompt, "")

    return {

        "equipment": equipment_name,

        "report": report,

        "documents": len(documents),

        "chunks": len(chunks)
    }