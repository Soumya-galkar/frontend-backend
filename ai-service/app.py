from html import entities
import json
from fastapi.middleware.cors import CORSMiddleware
import os
from services.maintenance_agent import (
    get_equipment,
    get_related_documents,
    get_related_chunks,
    build_context,
    generate_maintenance_report
)
import json
from urllib import response
from fastapi import FastAPI
from httpcore import request
from utils.superbase_client import supabase
from services.pdf_parser import  extract_text_from_pdf
from pydantic import BaseModel
from services.download_file import download_file
from services.save_text import save_extracted_text
from services.update_status import update_status
from services.chunk_text import chunk_text
from services.save_chunks import save_chunks
from services.generate_embeddings import generate_embeddings
from services.save_embeddings import save_embeddings 
from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
from utils.superbase_client import supabase
from services.search import create_query_embedding
from services.search import search_chunks
from services.rag import rag_answer
from services.entity_extractor import extract_entities
from services.save_entities import save_entities
from services.document_analyzer import analyze_document
from services.save_document_metadata import save_document_metadata
from pydantic import BaseModel
from services.document_analyzer import analyze_document
from services.save_document_metadata import save_document_metadata
from models.question_request import QuestionRequest
from services.rag import rag_answer
from services.graph_query import get_graph
# from services.maintenance_agent import generate_maintenance_report
from services.graph_builder import(
    get_or_create_node,
    create_edge
)
from services.graph_ingestion import ingest_document_graph
app = FastAPI()



from services.download_file import download_file
@app.get("/")
def home():
    return {"message": "AI Service Running"}

@app.get("/documents")
def get_documents():
    response = supabase.table("documents").select("*").execute()
    return response.data

BUCKET = "industrial-documents"

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    file_name = f"{uuid4()}-{file.filename}"

    file_bytes = await file.read()

    # Upload to Supabase Storage
    supabase.storage.from_(BUCKET).upload(
        file_name,
        file_bytes,
        {"content-type": file.content_type}
    )
     # Save metadata
    response = supabase.table("documents").insert({
        "original_name": file.filename,
        "storage_path": file_name,
        "file_type": file.content_type,
        "file_size": len(file_bytes),
        "status": "uploaded"
    }).execute()

    return response.data
# @app.post("/test")
# def test():
#     response = supabase.table("documents").insert({
#         "original_name":"test.pdf",
#         "storage_path":"test.pdf",
#         "file_type":"application/pdf",
#         "file_size":1000,
#         "status":"uploaded"
#     }).execute()

#     return response.data

class SearchRequest(BaseModel):

    question:str
    from services.search import create_query_embedding
from services.search import create_query_embedding, search_chunks



@app.get("/parse")
def parse_pdf():

    text = extract_text_from_pdf("uploads/sample.pdf")

    return {
        "text": text
    }
class ProcessRequest(BaseModel):
    document_id: str
    storage_path: str


@app.post("/process-document")
def process_document(request: ProcessRequest):

    try:
        print("1. Updating status...")
        update_status(request.document_id, "processing")

        print("2. Downloading file...")
        local_path = download_file(request.storage_path)

        print("3. Parsing PDF...")
        # pages = extract_text_from_pdf(local_path)
        pages=parse_document(local_path)

        print("4. Saving extracted text...")
        save_extracted_text(request.document_id, pages)

        print("chunks = chunk_text(pages)")
        chunks = chunk_text(pages)

        print("5. Saving chunks...")
        save_chunks(request.document_id, chunks)

        print("6. Generating embeddings...")
        embedded_chunks = generate_embeddings(chunks)

        print("7. Saving embeddings...")
        save_embeddings(request.document_id, embedded_chunks)
        # 
# Combine all pages into one document
        full_text = "\n".join(page["text"] for page in pages)

        metadata = analyze_document(full_text)
        # newwwww
        pid_equipment = []

        for page in pages:
            pid_equipment.extend(page.get("equipment_tags", []))

            existing = {
    e["id"]
        for e in metadata.get("equipment", [])
        if isinstance(e, dict)
}

        for tag in set(pid_equipment):

            if tag not in existing:

                metadata.setdefault("equipment", []).append({
            "id": tag,
            "type": "Unknown",
            "manufacturer": "",
            "status": ""
        })
        # newwwww
        print(metadata)
        print(type(metadata))
        print(metadata.get("equipment"))
        print(type(metadata.get("equipment")))
        save_document_metadata(
            request.document_id,
            metadata
        )
        # graph processing
        document = (
        supabase
        .table("documents")
        .select("original_name")
        .eq("id",request.document_id)
        .single()
        .execute()
    )  
        document_name = document.data["original_name"]
        document_node=get_or_create_node(
        "Document",
        document_name
    )    
        equipment_list = metadata.get("equipment", [])
        if isinstance(equipment_list, str):
            try:
                equipment_list = json.loads(equipment_list)
            except json.JSONDecodeError:
                equipment_list = []
        # for equipment in metadata.get("equipment",[]):
        for equipment in equipment_list:
                equipment_node  =  get_or_create_node(
            "Equipment",
            equipment["id"],
            metadata=equipment
        )    
        create_edge(
            equipment_node,
            document_node,
            "MENTIONED_IN"
        )
        # new 
          # ==========================
    # STEP 1 - Work Orders
    # ==========================

        for work_order in metadata.get("work_orders", []):

                workorder_node = get_or_create_node(
            "WorkOrder",
            work_order["id"],
            metadata=work_order
        )

        create_edge(
            equipment_node,
            workorder_node,
            "HAS_WORK_ORDER"
        )

        create_edge(
            workorder_node,
            document_node,
            "REFERENCED_IN"
        )

    # ==========================
    # STEP 2 - Parameters
    # ==========================

        for parameter in metadata.get("parameters", []):

            parameter_node = get_or_create_node(
            "Parameter",
            parameter["name"],
            metadata=parameter
        )

        create_edge(
            equipment_node,
            parameter_node,
            "OPERATES_AT"
        )

    # ==========================
    # STEP 3 - Regulations
    # ==========================

        for regulation in metadata.get("regulations", []):

            regulation_node = get_or_create_node(
            "Regulation",
            regulation
        )

        create_edge(
            document_node,
            regulation_node,
            "COMPLIES_WITH"
        )

    # ==========================
    # STEP 4 - Inspection Findings
    # ==========================

        for finding in metadata.get("inspection_findings", []):

            finding_node = get_or_create_node(
            "InspectionFinding",
            finding
        )

        create_edge(
            equipment_node,
            finding_node,
            "HAS_FINDING"
        )

        create_edge(
            finding_node,
            document_node,
            "FOUND_IN"
        )

# Department
        department = metadata.get("department")

# Maintenance
        maintenance = metadata.get("maintenance_type")

# Risk
        risk = metadata.get("risk_level")
        # new
        
        department =  metadata.get("department")
        if department:
            department_node =get_or_create_node(
                "Department",
                department
            )
            create_edge(
                department_node,
                document_node,
                "OWNS"
            )
        maintenance = metadata.get("maintenance_type")
        if maintenance:
            maintenance_node = get_or_create_node(
                "Maintenance",
                 maintenance
            )
            create_edge(
                maintenance_node,
                document_node,
                "DESCRIBES"
            )
        risk=metadata.get("risk_level")
        if risk : 
            risk_node=get_or_create_node(
                "Risk",
                risk
            )
            create_edge(
            document_node,
            risk_node,
            "HAS_RISK"
            )

        # Build the complete, idempotent industrial graph.  The legacy block
        # above is retained for backwards compatibility with existing data;
        # this service adds the expanded domain model for every new ingestion.
        ingest_document_graph(document_name, metadata)
        # Extract entities from the text and save them
          # NEW CODE
        print("8. Extracting entities...")
        entities = []
        for page in pages:
            page_entities = extract_entities(page["text"])
            save_entities(request.document_id, page["page_number"], page_entities)
        entities.extend(page_entities)
            
        update_status(request.document_id, "processed")
        print("7. Done!")

        return{"message : Document processed successfully."} 
        # print("8. Updating status...")
        # update_status(request.document_id, "processed")

        return {
            "message": "Success"
         }
    except Exception as e:
          print("ERROR:", repr(e))   # This prints the real error in the terminal
          return {
            "status": "failed",
            "error": str(e)
          }
@app.get("/entities/{document_id}")
def get_entities(document_id: str):

    response = (
        supabase
        .table("document_entities")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    )

    return response.data
# @app.post("/search")

# def search(request:SearchRequest):

#     embedding = create_query_embedding(

#         request.question

#     )

#     results = search_chunks(

#         embedding

#     )

#     return results

@app.post("/search")
def search(request: SearchRequest):

    query_embedding = create_query_embedding(request.question)

    results = search_chunks(query_embedding)

    return {
        "question": request.question,
        "results": results
    }

from services.gemini_service import ask_gemini
@app.post("/gemini-test")
def gemini_test():
    answer = ask_gemini("What is AI")
    return {"answer": answer}



# @app.post("/ask")
# def ask(request: SearchRequest):
#     return rag_answer(request.question)
#     return response

@app.post("/ask")
def ask(request: QuestionRequest):

    return rag_answer(request.question)

@app.get("/document-metadata/{document_id}")
def get_document_metadata(document_id: str):

    response = (
        supabase
        .table("document_metadata")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    )

    return response.data

# @app.get("/graph/{equipment}")

# def graph(equipment):

#     node = (

#         supabase

#         .table("graph_nodes")

#         .select("*")

#         .eq("node_name", equipment)

#         .execute()

#     )

#     return node.data    

@app.get("/graph/{equipment_name}")
def graph(equipment_name:str):

    print("Equipment:", equipment_name)
    data = get_graph(equipment_name)
    if data is None:
        return {"message":"Equipment not found"}
    return {
        "equipment":equipment_name,
        "connections":data
    }

from services.get_document import get_all_documents 
from services.get_document import get_document_by_id
from services.document_viewer import get_document_viewer
@app.get("/documents")
def get_document():
    try:
        documents = get_all_documents()
        return {
            "status":"success",
            "count":len(documents),
            "documents":documents
        }
    except Exception as e:
        return {
            "status":"error",
            "message":str(e)
        }
    
@app.get("/documents/{document_id}")
def get_document(document_id: str):

    try:

        data = get_document_by_id(document_id)

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/document-viewer/{document_id}")
def document_viewer(document_id: str):
    """Viewer-ready document, pages, AI summary, metadata, and entities."""
    try:
        data = get_document_viewer(document_id)
        if data is None:
            return {"status": "error", "message": "Document not found"}
        return data
    except Exception as error:
        return {"status": "error", "message": str(error)}
from services.dashboard import get_dashboard

@app.get("/dashboard")
def dashboard():
    try:
        data = get_dashboard()
        return {
            "status":"success",
            "data":data
        }
    except Exception as e:
        return{
            "status":"err",
            "message":str(e)
        }
from services.chat import chat
from services.maintenance_service import build_maintenance_report
from pydantic import BaseModel
class ChatRequest(BaseModel):
      question:str


# gemini
# Import your routers if they are in different files
# from app.routes import chat_router 

# 1. Initialize the FastAPI application instance

# 2. Define allowed cross-origin parameters
origins = [
    "http://localhost:5173",    # Vite local address standard
    "http://127.0.0.1:5173",    # Loopback matching explicit IP
]

# 3. Add CORS Middleware directly to the instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
def chat_api(request:ChatRequest):
    try:
        result = chat(request.question)
        return{
            "status":"success",
            "data":result
        }      
    except Exception as e:
        return {
            "status":"error",
            "message":str(e)
        }



# @app.get("/maintenance/{equipment_id}")
# def maintenance_intelligence(equipment_id: str):
#     """Generate an evidence-grounded predictive maintenance report."""
#     try:
#         report = build_maintenance_report(equipment_id)
#         if report is None:
#             return {"status": "error", "message": "Equipment not found"}
#         return report
#     except (ValueError, json.JSONDecodeError) as error:
#         return {"status": "error", "message": f"Maintenance report generation failed: {error}"}
#     except Exception as error:
#         return {"status": "error", "message": str(error)}
# from services.parsers.parser_factory import parse_document
# from routes.maintenance_router import router as maintance_router
# @app.get("/maintenance/{equipment}")

# def maintenance(equipment: str):

#     return generate_maintenance_report(equipment)

# app.include_router(maintance_router)

# gemini
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# # Import your routers if they are in different files
# # from app.routes import chat_router 

# # 1. Initialize the FastAPI application instance
# app = FastAPI(title="Industrial Knowledge Intelligence API")

# # 2. Define allowed cross-origin parameters
# origins = [
#     "http://localhost:5173",    # Vite local address standard
#     "http://127.0.0.1:5173",    # Loopback matching explicit IP
# ]

# # 3. Add CORS Middleware directly to the instance
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 4. Bind your operational routes AFTER middleware is attached
# @app.post("/chat")
# def chat_api(request: ChatRequest):
#     try:
#         result = chat(request.question)
#         return {
#             "status": "success",
#             "data": result
#         }      
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# # If you are using APIRouter from external files, include them here:
# # app.include_router(chat_router)

@app.get("/maintenance/debug/{equipment}")
def maintenance_debug(equipment: str):

    eq = get_equipment(equipment)
    print("Equipment:", eq)

    if eq is None:
        return {"step": "get_equipment", "data": None}

    docs = get_related_documents(eq["id"])
    print("Documents:", docs)

    chunks = get_related_chunks(docs)
    print("Chunks:", chunks)

    context = build_context(eq, docs, chunks)
    print("Context:", context[:500])

    return {
        "equipment": eq,
        "documents": docs,
        "chunk_count": len(chunks),
        "context_preview": context[:500]
    }
