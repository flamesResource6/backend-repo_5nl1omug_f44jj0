import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Presentation, Tool

app = FastAPI(title="Presentation Builder & Tool Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Helpers ---------
class IdModel(BaseModel):
    id: str

def to_serializable(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # convert nested ObjectIds if any
    for k, v in d.items():
        if isinstance(v, ObjectId):
            d[k] = str(v)
        if isinstance(v, list):
            d[k] = [str(x) if isinstance(x, ObjectId) else x for x in v]
    return d

@app.get("/")
def read_root():
    return {"message": "Presentation Builder & Tool Finder Backend"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# =======================
# Presentations Endpoints
# =======================
@app.post("/api/presentations", response_model=IdModel)
def create_presentation(payload: Presentation):
    new_id = create_document("presentation", payload)
    return {"id": new_id}

@app.get("/api/presentations")
def list_presentations(q: Optional[str] = Query(None, description="Search by title/description/tags")):
    filter_dict = {}
    if q:
        # basic OR search across fields
        filter_dict = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
            ]
        }
    items = [to_serializable(d) for d in get_documents("presentation", filter_dict)]
    return {"items": items}

# ==================
# Tool Finder Routes
# ==================
@app.post("/api/tools", response_model=IdModel)
def add_tool(payload: Tool):
    new_id = create_document("tool", payload)
    return {"id": new_id}

@app.get("/api/tools")
def search_tools(
    q: Optional[str] = Query(None, description="Search in name/description/tags"),
    category: Optional[str] = Query(None),
    free_only: bool = Query(False)
):
    filter_dict = {}
    clauses = []
    if q:
        clauses.append({
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
            ]
        })
    if category:
        clauses.append({"category": {"$regex": f"^{category}$", "$options": "i"}})
    if free_only:
        clauses.append({"is_free": True})
    if clauses:
        filter_dict = {"$and": clauses}
    tools = [to_serializable(d) for d in get_documents("tool", filter_dict)]
    return {"items": tools}
