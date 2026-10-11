from typing import List, Optional
from pydantic import BaseModel, Field

class ErrandBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = "General"
    urgency: str = "medium"  # low, medium, high
    deadline: Optional[str] = None
    notes: Optional[str] = None
    prep_items: List[str] = Field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, carry_forward
    stop_id: Optional[str] = None

class ErrandCreate(ErrandBase):
    pass

class ErrandUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    urgency: Optional[str] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None
    prep_items: Optional[List[str]] = None
    status: Optional[str] = None
    stop_id: Optional[str] = None

class ErrandResponse(ErrandBase):
    id: str
    created_at: str

class StopBase(BaseModel):
    name: str
    category: str = "General"
    location_text: Optional[str] = None
    sequence_number: int = 0

class StopCreate(StopBase):
    pass

class StopResponse(StopBase):
    id: str

class PackingItemModel(BaseModel):
    id: str
    trip_id: str
    label: str
    checked: bool

class PackingItemToggle(BaseModel):
    checked: bool

class TripItemModel(BaseModel):
    id: str
    trip_id: str
    errand_id: str
    stop_id: Optional[str] = None
    completed: bool
    completed_at: Optional[str] = None
    errand: Optional[ErrandResponse] = None

class TripCreate(BaseModel):
    name: str = "My Errand Trip"
    errand_ids: List[str] = Field(default_factory=list)

class TripResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    stops: List[StopResponse] = Field(default_factory=list)
    items: List[TripItemModel] = Field(default_factory=list)
    packing_items: List[PackingItemModel] = Field(default_factory=list)
