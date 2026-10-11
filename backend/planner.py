import re
from typing import List, Dict, Any, Tuple

# Categories and their keyword patterns
CATEGORY_RULES = {
    "Groceries": {
        "keywords": [
            r"\bmilk\b", r"\begg(s)?\b", r"\bvegetable(s)?\b", r"\bveggie(s)?\b", r"\bfruit(s)?\b",
            r"\bbread\b", r"\bgrocer(y|ies)\b", r"\bsupermarket\b", r"\bcheese\b", r"\bbutter\b",
            r"\byogurt\b", r"\bcurd\b", r"\bmeat\b", r"\bchicken\b", r"\bfish\b", r"\bsnack(s)?\b",
            r"\brice\b", r"\bflour\b", r"\boil\b", r"\bice cream\b", r"\bfrozen\b", r"\btomato(es)?\b",
            r"\bonion(s)?\b", r"\bpotato(es)?\b", r"\bapple(s)?\b", r"\bbanana(s)?\b"
        ],
        "default_stop": "Grocery Store / Supermarket",
        "prep_items": ["Cloth / Shopping bag", "Payment method"],
        "is_perishable": True
    },
    "Printing & Stationery": {
        "keywords": [
            r"\bprint(ing)?\b", r"\bphotocopy\b", r"\bxerox\b", r"\bscan\b", r"\bdocument(s)?\b",
            r"\bassignment\b", r"\blab file\b", r"\bfile\b", r"\bpaper(s)?\b", r"\bpen(s)?\b",
            r"\bnotebook(s)?\b", r"\bstationer(y|ies)\b", r"\bbind(ing)?\b", r"\blaminat(e|ion)\b"
        ],
        "default_stop": "Print / Stationery Shop",
        "prep_items": ["Document on USB drive / phone", "Sample / physical copy to xerox"],
        "is_perishable": False
    },
    "Parcel & Mail": {
        "keywords": [
            r"\bparcel\b", r"\bpackage\b", r"\bcourier\b", r"\bpost office\b", r"\bmail\b",
            r"\bpickup parcel\b", r"\bcollect.*parcel\b", r"\bamazon pickup\b", r"\bdeliver(y)?\b",
            r"\bshipment\b", r"\blocker\b"
        ],
        "default_stop": "Parcel Collection / Post Office",
        "prep_items": ["Parcel tracking number / OTP code", "Photo ID card"],
        "is_perishable": False
    },
    "Pharmacy & Health": {
        "keywords": [
            r"\bpharmac(y|ies)\b", r"\bmedicin(e|es)\b", r"\bchemist\b", r"\bdrugstore\b",
            r"\bprescription\b", r"\bpill(s)?\b", r"\btablet(s)?\b", r"\bbandage\b", r"\bsyrup\b",
            r"\beye drop(s)?\b", r"\bfirst aid\b", r"\bvitamins?\b"
        ],
        "default_stop": "Pharmacy / Chemist",
        "prep_items": ["Doctor's prescription", "Payment method"],
        "is_perishable": False
    },
    "Banking & Cash": {
        "keywords": [
            r"\batm\b", r"\bbank\b", r"\bcash\b", r"\bdeposit\b", r"\bwithdraw\b", r"\bcheque\b",
            r"\bcheck\b", r"\bpassbook\b", r"\bbranch\b"
        ],
        "default_stop": "ATM / Bank Branch",
        "prep_items": ["ATM card / Bank passbook", "Cash / Cheque book"],
        "is_perishable": False
    },
    "Personal Care": {
        "keywords": [
            r"\bshampoo\b", r"\bsoap\b", r"\btoothpaste\b", r"\bbrush\b", r"\blotion\b",
            r"\bcosmetic(s)?\b", r"\bhaircut\b", r"\bsalon\b", r"\bbarber\b", r"\bconditioner\b",
            r"\bskincare\b", r"\bdeodorant\b"
        ],
        "default_stop": "Personal Care / General Store",
        "prep_items": ["Payment method"],
        "is_perishable": False
    },
    "Services & Repair": {
        "keywords": [
            r"\blaundry\b", r"\bdry clean(ing)?\b", r"\btailor\b", r"\balteration\b", r"\bcobbler\b",
            r"\bshoe repair\b", r"\bcar wash\b", r"\bmechanic\b", r"\bhardware\b", r"\brepair\b",
            r"\blibrary book\b", r"\breturn book\b", r"\bbill payment\b", r"\belectricity bill\b"
        ],
        "default_stop": "Service Center / Local Shop",
        "prep_items": ["Items to repair / return", "Bill / account receipt"],
        "is_perishable": False
    }
}

DEADLINE_REGEX = re.compile(
    r"\b(before|by|until|prior to)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)?|\d{1,2}\s*o'?clock|noon|midnight|evening|closing)\b",
    re.IGNORECASE
)

URGENCY_REGEX = re.compile(
    r"\b(urgent|urgently|asap|priority|important|critical|immediately)\b",
    re.IGNORECASE
)

PERISHABLE_KEYWORDS = ["milk", "ice cream", "frozen", "curd", "yogurt", "cheese", "meat", "fish", "cold"]

def split_raw_text(text: str) -> List[str]:
    """Splits multiple errands from a paragraph or multi-item sentence."""
    # Split by newlines, bullets, or numbering first
    lines = [line.strip() for line in re.split(r"[\r\n]+", text) if line.strip()]
    if len(lines) > 1:
        tasks = []
        for line in lines:
            # Clean numbered list bullets like '1. ', '- '
            cleaned = re.sub(r"^(\d+[\.\)]|\-|\*|\•)\s*", "", line).strip()
            if cleaned:
                tasks.append(cleaned)
        return tasks

    # Single line: split by conjunctions or separators
    cleaned_text = text.strip()
    # Replace common phrase starters
    cleaned_text = re.sub(r"^(i need to|i have to|please|can you|errands:|tasks:)\s+", "", cleaned_text, flags=re.IGNORECASE)
    
    # Split on commas, semicolons, and "and" when it separates distinct actions
    # e.g., "buy milk, print my assignment, collect parcel before 5, and get cash at atm"
    parts = re.split(r",\s*(?:and\s+)?|;\s*|\s+and\s+(?=(?:buy|get|print|collect|pick up|visit|deposit|withdraw|return|go to|take|drop))\b", cleaned_text, flags=re.IGNORECASE)
    
    tasks = []
    for p in parts:
        p_clean = p.strip()
        if p_clean.lower().startswith("and "):
            p_clean = p_clean[4:].strip()
        if p_clean and len(p_clean) > 2:
            tasks.append(p_clean)
            
    return tasks if tasks else [cleaned_text]

def parse_single_errand(task_text: str) -> Dict[str, Any]:
    """Extracts structured errand properties from a single task text."""
    text_lower = task_text.lower()
    
    # Extract deadline
    deadline = None
    deadline_match = DEADLINE_REGEX.search(task_text)
    if deadline_match:
        deadline = deadline_match.group(0)
    
    # Extract urgency
    urgency = "medium"
    if URGENCY_REGEX.search(task_text) or (deadline and any(w in deadline.lower() for w in ["before", "by"])):
        urgency = "high"
        
    # Match category
    matched_category = "General"
    suggested_stop = "General Stop"
    prep_items = ["Payment method / Wallet"]
    is_perishable = False
    
    for category, rules in CATEGORY_RULES.items():
        for kw in rules["keywords"]:
            if re.search(kw, text_lower):
                matched_category = category
                suggested_stop = rules["default_stop"]
                prep_items = list(rules["prep_items"])
                is_perishable = rules.get("is_perishable", False)
                break
        if matched_category != "General":
            break

    # Check perishables explicitly
    if any(pk in text_lower for pk in PERISHABLE_KEYWORDS):
        is_perishable = True
        if "Cloth / Shopping bag" not in prep_items:
            prep_items.append("Cloth / Shopping bag")

    # Clean title nicely
    title = task_text.strip()
    if title:
        title = title[0].upper() + title[1:]

    return {
        "title": title,
        "category": matched_category,
        "suggested_stop": suggested_stop,
        "urgency": urgency,
        "deadline": deadline,
        "notes": None,
        "prep_items": prep_items,
        "is_perishable": is_perishable
    }

def parse_errands_from_text(text: str) -> List[Dict[str, Any]]:
    """Heuristic / Rule-based extractor for unstructured text."""
    raw_tasks = split_raw_text(text)
    results = []
    for raw in raw_tasks:
        if raw.strip():
            parsed = parse_single_errand(raw)
            results.append(parsed)
    return results

def plan_trip(errands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Groups errands into stops and sequences them following the PRD rules:
    1. Financial / ATM prerequisites early so cash is available if needed.
    2. High urgency / explicit deadlines scheduled early.
    3. General stops (printing, courier, pharmacy, services).
    4. Perishable / refrigerated groceries scheduled near the end so items don't spoil.
    """
    # Group tasks by suggested stop
    stops_dict: Dict[str, Dict[str, Any]] = {}
    
    for err in errands:
        # Determine stop name
        stop_name = err.get("suggested_stop")
        if not stop_name:
            cat = err.get("category", "General")
            stop_name = CATEGORY_RULES.get(cat, {}).get("default_stop", "General Stop")
            
        if stop_name not in stops_dict:
            stops_dict[stop_name] = {
                "name": stop_name,
                "category": err.get("category", "General"),
                "has_urgent": False,
                "has_perishable": False,
                "has_banking": "Bank" in stop_name or "ATM" in stop_name,
                "tasks": []
            }
            
        stops_dict[stop_name]["tasks"].append(err)
        if err.get("urgency") == "high" or err.get("deadline"):
            stops_dict[stop_name]["has_urgent"] = True
        if err.get("is_perishable"):
            stops_dict[stop_name]["has_perishable"] = True

    # Sequence score: lower score comes earlier
    # ATM/Banking: -100 (get cash first)
    # Urgent/Deadline: -50
    # Regular: 0
    # Perishable/Groceries: +100 (visit last)
    def stop_priority_key(stop_info: Dict[str, Any]) -> int:
        score = 0
        if stop_info["has_banking"]:
            score -= 100
        if stop_info["has_urgent"]:
            score -= 50
        if stop_info["has_perishable"]:
            score += 100
        return score

    sorted_stops = sorted(stops_dict.values(), key=stop_priority_key)
    
    # Assign sequence numbers
    ordered_stops = []
    for idx, stop_data in enumerate(sorted_stops, start=1):
        ordered_stops.append({
            "sequence_number": idx,
            "name": stop_data["name"],
            "category": stop_data["category"],
            "tasks": stop_data["tasks"]
        })

    # Generate Departure Checklist
    departure_checklist = set(["Wallet / Payment method / Phone"])
    for err in errands:
        for prep in err.get("prep_items", []):
            if prep:
                departure_checklist.add(prep)
                
    return {
        "ordered_stops": ordered_stops,
        "departure_checklist": sorted(list(departure_checklist)),
        "total_stops": len(ordered_stops),
        "total_tasks": len(errands)
    }
