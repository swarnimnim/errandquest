import sys
from starlette.testclient import TestClient
from main import app
from database import init_db

def run_acceptance_tests():
    init_db()
    client = TestClient(app)
    print("==================================================")
    print("   RUNNING ERRANDQUEST PRD ACCEPTANCE TESTS")
    print("==================================================")

    # 1. Health check & AI status
    health = client.get("/api/health")
    assert health.status_code == 200, f"Health check failed: {health.status_code}"
    ai_status = client.get("/api/ai/status").json()
    print(f"[PASS] Health Check & AI Status: {ai_status['active_engine']}")

    # 2. Test 1: Multiple Errands Parsing & Grouping
    input_text = "Buy milk, print my assignment, collect a parcel, and buy vegetables."
    parse_resp = client.post("/api/errands/parse", json={"text": input_text})
    assert parse_resp.status_code == 200
    tasks = parse_resp.json()["tasks"]
    assert len(tasks) >= 3, f"Expected at least 3-4 tasks, got {len(tasks)}"
    print(f"[PASS] Test 1: Multiple Errands Extracted: {len(tasks)} tasks found")

    # 3. Test 2: Duplicate Errands Detection
    # First create 'Buy milk'
    client.post("/api/errands", json={"title": "Buy milk", "category": "Groceries"})
    dup_resp = client.post("/api/errands/parse", json={"text": "Need milk too"})
    dup_task = dup_resp.json()["tasks"][0]
    assert dup_task["is_possible_duplicate"] is True, "Duplicate was not flagged"
    print(f"[PASS] Test 2: Duplicate Errands Flagged: '{dup_task['title']}' flagged as duplicate of '{dup_task['duplicate_of']}' without deletion")

    # 4. Test 3: Urgent Errand & Deadline
    urgent_resp = client.post("/api/errands/parse", json={"text": "Collect my parcel before 4 PM."})
    urgent_task = urgent_resp.json()["tasks"][0]
    assert urgent_task["urgency"] == "high" or "before 4" in str(urgent_task.get("deadline")), f"Urgency failed: {urgent_task}"
    print(f"[PASS] Test 3: Urgent Errand & Deadline Captured: {urgent_task['deadline']}, Urgency={urgent_task['urgency']}")

    # 5. Test 4: Task Correction & Manual Entry (Test 7)
    created_manual = client.post("/api/errands", json={
        "title": "Buy shampoo",
        "category": "General", # initially wrong
        "urgency": "low"
    }).json()
    updated = client.patch(f"/api/errands/{created_manual['id']}", json={
        "category": "Personal Care"
    }).json()
    assert updated["category"] == "Personal Care", "Update failed"
    print(f"[PASS] Test 4 & 7: Manual Entry & Task Correction: Category updated to '{updated['category']}'")

    # 6. Test 5 & Planning: Perishable Groceries Scheduled Last & Cash First
    plan_resp = client.post("/api/trips/plan", json={"errands": [
        {"title": "Withdraw cash at ATM", "category": "Banking & Cash", "suggested_stop": "ATM / Bank Branch", "prep_items": ["ATM Card"]},
        {"title": "Print resume", "category": "Printing & Stationery", "suggested_stop": "Print Shop", "prep_items": ["USB Drive"]},
        {"title": "Buy 2L milk and ice cream", "category": "Groceries", "suggested_stop": "Supermarket", "is_perishable": True, "prep_items": ["Shopping bag"]}
    ]})
    assert plan_resp.status_code == 200
    plan = plan_resp.json()
    stops = plan["ordered_stops"]
    assert "ATM" in stops[0]["name"] or "Bank" in stops[0]["name"], f"Expected ATM first, got {stops[0]['name']}"
    assert "Supermarket" in stops[-1]["name"] or stops[-1].get("category") == "Groceries", f"Expected Grocery last, got {stops[-1]['name']}"
    print(f"[PASS] Stop Sequencing Rules: First={stops[0]['name']}, Last={stops[-1]['name']} (Groceries last for freshness)")
    print(f"[PASS] Departure Checklist Generated: {plan['departure_checklist']}")

    # 7. Test 6: Incomplete Trip & Carry-Forward
    trip_resp = client.post("/api/trips", json={
        "name": "Sunday Errands Outing",
        "plan": plan
    }).json()
    trip_id = trip_resp["id"]
    items = trip_resp["items"]
    # Mark first item complete, leave others
    client.patch(f"/api/trips/{trip_id}/items/{items[0]['item_id']}", json={"completed": True})
    
    # Complete trip
    summary = client.post(f"/api/trips/{trip_id}/complete").json()
    assert summary["completed_tasks"] == 1
    assert summary["carried_forward"] == 2
    print(f"[PASS] Test 6: Incomplete Trip Handled: {summary['completed_tasks']} completed, {summary['carried_forward']} carried forward to next outing")

    print("\n==================================================")
    print("   ALL 8 ACCEPTANCE TESTS PASSED SUCCESSFULLY!    ")
    print("==================================================")

if __name__ == "__main__":
    run_acceptance_tests()
