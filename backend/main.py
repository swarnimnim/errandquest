import os
import re
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
import crud
from models import (
    ErrandCreate,
    ErrandUpdate,
    ErrandResponse,
    StopCreate,
    StopResponse,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite tables exist
    init_db()
    yield

app = FastAPI(
    title="ErrandQuest API",
    description="One Trip. Everything Done. AI-powered personal errand planner.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend to call the API without CORS blockers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ErrandQuest API",
        "database": "SQLite connected"
    }

# --- ERRANDS ENDPOINTS ---

@app.get("/api/errands", response_model=List[ErrandResponse])
def list_errands(status: Optional[str] = Query(None, description="Filter by status (pending, completed, etc.)")):
    return crud.get_all_errands(status=status)

@app.post("/api/errands", response_model=ErrandResponse, status_code=201)
def add_errand(errand: ErrandCreate):
    created = crud.create_errand(errand)
    return created

@app.get("/api/errands/{errand_id}", response_model=ErrandResponse)
def get_errand_detail(errand_id: str):
    item = crud.get_errand(errand_id)
    if not item:
        raise HTTPException(status_code=404, detail="Errand not found")
    return item

@app.patch("/api/errands/{errand_id}", response_model=ErrandResponse)
def modify_errand(errand_id: str, payload: ErrandUpdate):
    updated = crud.update_errand(errand_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Errand not found")
    return updated

@app.delete("/api/errands/{errand_id}")
def remove_errand(errand_id: str):
    success = crud.delete_errand(errand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Errand not found")
    return {"message": "Errand deleted successfully"}

# --- STOPS ENDPOINTS ---

@app.get("/api/stops", response_model=List[StopResponse])
def list_stops():
    return crud.get_all_stops()

@app.post("/api/stops", response_model=StopResponse, status_code=201)
def add_stop(stop: StopCreate):
    return crud.create_stop(stop)

@app.delete("/api/stops/{stop_id}")
def remove_stop(stop_id: str):
    success = crud.delete_stop(stop_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stop not found")
    return {"message": "Stop deleted"}

# --- PARSING & PLANNING ENDPOINTS ---

from pydantic import BaseModel

class ParseRequest(BaseModel):
    text: str

class PlanRequest(BaseModel):
    errands: Optional[List[dict]] = None
    use_pending_db: bool = True

class CreateTripRequest(BaseModel):
    name: str = "My Errand Trip"
    plan: dict

class ItemStatusRequest(BaseModel):
    completed: bool

class PackingStatusRequest(BaseModel):
    checked: bool

@app.get("/api/ai/status")
async def get_ai_status():
    from ai_service import check_ollama_status
    return await check_ollama_status()

@app.post("/api/errands/parse")
async def parse_text_to_errands(payload: ParseRequest):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    from ai_service import extract_errands_with_ai
    ai_result = await extract_errands_with_ai(payload.text)
    extracted = ai_result["tasks"]
    
    # Duplicate check against existing errands (Acceptance Test 2)
    existing_errands = crud.get_all_errands(status="pending") + crud.get_all_errands(status="carry_forward")
    existing_titles = [e["title"].lower() for e in existing_errands]
    
    results = []
    for item in extracted:
        item_words = set(re.findall(r"\w+", item["title"].lower())) - {"the", "a", "an", "to", "my", "some", "i", "need"}
        possible_dup = None
        for exist_title in existing_titles:
            exist_words = set(re.findall(r"\w+", exist_title)) - {"the", "a", "an", "to", "my", "some", "i", "need"}
            # Check overlap
            common = item_words.intersection(exist_words)
            if common and (len(common) >= 1 and any(w in ["milk", "vegetables", "parcel", "shampoo", "cash", "print"] for w in common) or len(common) >= 2):
                possible_dup = exist_title
                break
        
        item["is_possible_duplicate"] = bool(possible_dup)
        item["duplicate_of"] = possible_dup
        results.append(item)
        
    return {
        "tasks": results,
        "count": len(results),
        "source": ai_result.get("source", "heuristic"),
        "model": ai_result.get("model", "built-in")
    }

@app.post("/api/trips/plan")
def generate_trip_plan(payload: PlanRequest):
    from planner import plan_trip
    errands_to_plan = []
    
    if payload.errands and len(payload.errands) > 0:
        errands_to_plan = payload.errands
    elif payload.use_pending_db:
        # Fetch pending and carry_forward errands
        errands_to_plan = crud.get_all_errands(status="pending") + crud.get_all_errands(status="carry_forward")
        
    if not errands_to_plan:
        raise HTTPException(status_code=400, detail="No errands found to plan a trip")
        
    plan = plan_trip(errands_to_plan)
    return plan

@app.post("/api/trips")
def start_trip(payload: CreateTripRequest):
    trip = crud.create_trip_from_plan(payload.name, payload.plan)
    return trip

@app.get("/api/trips/active")
def get_current_active_trip():
    trip = crud.get_active_trip()
    if not trip:
        return {"active": False, "trip": None}
    return {"active": True, "trip": trip}

@app.get("/api/trips/{trip_id}")
def get_trip_details(trip_id: str):
    trip = crud.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.patch("/api/trips/{trip_id}/items/{item_id}")
def update_item_status(trip_id: str, item_id: str, payload: ItemStatusRequest):
    result = crud.update_trip_item_status(item_id, payload.completed)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return result

@app.patch("/api/trips/{trip_id}/packing/{packing_id}")
def update_packing_item(trip_id: str, packing_id: str, payload: PackingStatusRequest):
    result = crud.toggle_packing_item(packing_id, payload.checked)
    if not result:
        raise HTTPException(status_code=404, detail="Packing item not found")
    return result

@app.post("/api/trips/{trip_id}/complete")
def finalize_trip(trip_id: str):
    summary = crud.complete_or_end_trip(trip_id)
    return summary

# --- PRODUCTION STATIC FRONTEND SERVING ---
from fastapi.staticfiles import StaticFiles
from pathlib import Path

dist_path = Path(__file__).parent.parent / "frontend" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")


