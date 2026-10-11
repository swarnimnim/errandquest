import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from database import get_connection
from models import ErrandCreate, ErrandUpdate, ErrandResponse, StopCreate, StopResponse

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# --- ERRANDS ---

def get_all_errands(status: Optional[str] = None) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM errands WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM errands ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        item = dict(r)
        item["prep_items"] = json.loads(item["prep_items"] or "[]")
        result.append(item)
    return result

def get_errand(errand_id: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM errands WHERE id = ?", (errand_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    item = dict(row)
    item["prep_items"] = json.loads(item["prep_items"] or "[]")
    return item

def create_errand(data: ErrandCreate) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    eid = str(uuid.uuid4())
    now = _now_iso()
    prep_json = json.dumps(data.prep_items or [])
    
    cursor.execute("""
        INSERT INTO errands (id, title, category, urgency, deadline, notes, prep_items, status, stop_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (eid, data.title.strip(), data.category, data.urgency, data.deadline, data.notes, prep_json, data.status, data.stop_id, now))
    
    conn.commit()
    conn.close()
    return get_errand(eid)

def update_errand(errand_id: str, data: ErrandUpdate) -> Optional[dict]:
    existing = get_errand(errand_id)
    if not existing:
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = {}
    if data.title is not None:
        updates["title"] = data.title.strip()
    if data.category is not None:
        updates["category"] = data.category
    if data.urgency is not None:
        updates["urgency"] = data.urgency
    if data.deadline is not None:
        updates["deadline"] = data.deadline
    if data.notes is not None:
        updates["notes"] = data.notes
    if data.prep_items is not None:
        updates["prep_items"] = json.dumps(data.prep_items)
    if data.status is not None:
        updates["status"] = data.status
    if data.stop_id is not None:
        updates["stop_id"] = data.stop_id
        
    if updates:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [errand_id]
        cursor.execute(f"UPDATE errands SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
    conn.close()
    return get_errand(errand_id)

def delete_errand(errand_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM errands WHERE id = ?", (errand_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# --- STOPS ---

def get_all_stops() -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stops ORDER BY sequence_number ASC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_stop(data: StopCreate) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    sid = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO stops (id, name, category, location_text, sequence_number)
        VALUES (?, ?, ?, ?, ?)
    """, (sid, data.name.strip(), data.category, data.location_text, data.sequence_number))
    conn.commit()
    conn.close()
    return {"id": sid, "name": data.name.strip(), "category": data.category, "location_text": data.location_text, "sequence_number": data.sequence_number}

def delete_stop(stop_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stops WHERE id = ?", (stop_id,))
    affected = cursor.rowcount
    cursor.execute("UPDATE errands SET stop_id = NULL WHERE stop_id = ?", (stop_id,))
    conn.commit()
    conn.close()
    return affected > 0

# --- TRIPS & EXECUTION ---

def create_trip_from_plan(name: str, plan: dict) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    trip_id = str(uuid.uuid4())
    now = _now_iso()

    cursor.execute("""
        INSERT INTO trips (id, name, status, created_at)
        VALUES (?, ?, 'active', ?)
    """, (trip_id, name, now))

    # Add packing items
    for item_label in plan.get("departure_checklist", []):
        pack_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO packing_items (id, trip_id, label, checked)
            VALUES (?, ?, ?, 0)
        """, (pack_id, trip_id, item_label))

    # Insert stops and trip items
    for stop in plan.get("ordered_stops", []):
        stop_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO stops (id, name, category, sequence_number)
            VALUES (?, ?, ?, ?)
        """, (stop_id, stop["name"], stop.get("category", "General"), stop.get("sequence_number", 0)))

        for task in stop.get("tasks", []):
            task_id = task.get("id")
            # If the task doesn't have an ID in the DB yet, create it!
            if not task_id:
                task_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO errands (id, title, category, urgency, deadline, notes, prep_items, status, stop_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'in_progress', ?, ?)
                """, (
                    task_id,
                    task["title"],
                    task.get("category", "General"),
                    task.get("urgency", "medium"),
                    task.get("deadline"),
                    task.get("notes"),
                    json.dumps(task.get("prep_items", [])),
                    stop_id,
                    now
                ))
            else:
                cursor.execute("UPDATE errands SET stop_id = ?, status = 'in_progress' WHERE id = ?", (stop_id, task_id))

            # Add trip_item
            titem_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO trip_items (id, trip_id, errand_id, stop_id, completed)
                VALUES (?, ?, ?, ?, 0)
            """, (titem_id, trip_id, task_id, stop_id))

    conn.commit()
    conn.close()
    return get_trip(trip_id)

def get_trip(trip_id: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
    t_row = cursor.fetchone()
    if not t_row:
        conn.close()
        return None

    trip = dict(t_row)

    # Get packing items
    cursor.execute("SELECT * FROM packing_items WHERE trip_id = ?", (trip_id,))
    packing = [dict(r) for r in cursor.fetchall()]
    trip["packing_items"] = packing

    # Get trip items joined with errands and stops
    cursor.execute("""
        SELECT ti.id as item_id, ti.trip_id, ti.errand_id, ti.stop_id, ti.completed, ti.completed_at,
               e.title, e.category, e.urgency, e.deadline, e.notes, e.prep_items, e.status as errand_status,
               s.name as stop_name, s.sequence_number, s.category as stop_category
        FROM trip_items ti
        JOIN errands e ON ti.errand_id = e.id
        LEFT JOIN stops s ON ti.stop_id = s.id
        WHERE ti.trip_id = ?
        ORDER BY s.sequence_number ASC, e.urgency DESC
    """, (trip_id,))
    item_rows = cursor.fetchall()
    conn.close()

    # Structure into ordered stops
    stops_map = {}
    items = []
    for r in item_rows:
        row_dict = dict(r)
        row_dict["prep_items"] = json.loads(row_dict["prep_items"] or "[]")
        sid = row_dict["stop_id"] or "unassigned"
        if sid not in stops_map:
            stops_map[sid] = {
                "id": sid,
                "name": row_dict["stop_name"] or "Stop",
                "category": row_dict["stop_category"] or "General",
                "sequence_number": row_dict["sequence_number"] or 0,
                "tasks": []
            }
        stops_map[sid]["tasks"].append(row_dict)
        items.append(row_dict)

    trip["stops"] = sorted(list(stops_map.values()), key=lambda x: x["sequence_number"])
    trip["items"] = items
    return trip

def get_active_trip() -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM trips WHERE status = 'active' ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return get_trip(row["id"])
    return None

def update_trip_item_status(item_id: str, completed: bool) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    now = _now_iso() if completed else None
    cursor.execute("""
        UPDATE trip_items
        SET completed = ?, completed_at = ?
        WHERE id = ?
    """, (1 if completed else 0, now, item_id))
    
    # Also update errand status
    cursor.execute("""
        UPDATE errands
        SET status = ?
        WHERE id = (SELECT errand_id FROM trip_items WHERE id = ?)
    """, ("completed" if completed else "in_progress", item_id))
    
    conn.commit()
    conn.close()
    return {"item_id": item_id, "completed": completed, "completed_at": now}

def toggle_packing_item(item_id: str, checked: bool) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE packing_items
        SET checked = ?
        WHERE id = ?
    """, (1 if checked else 0, item_id))
    conn.commit()
    conn.close()
    return {"id": item_id, "checked": checked}

def complete_or_end_trip(trip_id: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    now = _now_iso()
    cursor.execute("UPDATE trips SET status = 'completed', completed_at = ? WHERE id = ?", (now, trip_id))

    # Mark remaining unfinished errands as 'carry_forward'
    cursor.execute("""
        UPDATE errands
        SET status = 'carry_forward'
        WHERE id IN (
            SELECT errand_id FROM trip_items
            WHERE trip_id = ? AND completed = 0
        )
    """, (trip_id,))

    # Metrics
    cursor.execute("SELECT count(*) FROM trip_items WHERE trip_id = ?", (trip_id,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM trip_items WHERE trip_id = ? AND completed = 1", (trip_id,))
    completed = cursor.fetchone()[0]

    cursor.execute("SELECT count(DISTINCT stop_id) FROM trip_items WHERE trip_id = ? AND completed = 1", (trip_id,))
    stops_visited = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return {
        "trip_id": trip_id,
        "status": "completed",
        "completed_at": now,
        "total_tasks": total,
        "completed_tasks": completed,
        "carried_forward": total - completed,
        "stops_visited": stops_visited
    }

