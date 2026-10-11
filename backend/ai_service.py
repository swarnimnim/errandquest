import os
import json
import logging
from typing import List, Optional, Dict, Any
import httpx
from pydantic import BaseModel, Field

from planner import parse_errands_from_text

logger = logging.getLogger("errandquest.ai")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

class ExtractedTask(BaseModel):
    title: str = Field(..., min_length=1)
    category: str = "General"
    suggested_stop: Optional[str] = None
    urgency: str = "medium"
    deadline: Optional[str] = None
    notes: Optional[str] = None
    prep_items: List[str] = Field(default_factory=list)
    is_perishable: bool = False

class ExtractedTaskList(BaseModel):
    tasks: List[ExtractedTask]

async def check_ollama_status() -> Dict[str, Any]:
    """Checks if Ollama service is reachable and lists installed models."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "available": True,
                    "active_engine": "Ollama Local AI",
                    "default_model": DEFAULT_MODEL,
                    "installed_models": models,
                    "endpoint": OLLAMA_BASE_URL
                }
    except Exception as e:
        logger.debug(f"Ollama check failed: {e}")

    return {
        "available": False,
        "active_engine": "Built-in Fast Heuristic NLP",
        "default_model": None,
        "installed_models": [],
        "endpoint": OLLAMA_BASE_URL,
        "note": "Ollama is not running. Using built-in deterministic parser (0ms latency, zero RAM overhead)."
    }

EXTRACTION_SYSTEM_PROMPT = """You are ErrandQuest AI, an assistant that extracts actionable errands from unstructured text.
Rules:
1. Break down user text into specific, separate real-world tasks.
2. For each task, extract:
   - title: concise errand name (e.g., 'Buy 2L milk', 'Print lab assignment')
   - category: one of ['Groceries', 'Printing & Stationery', 'Parcel & Mail', 'Pharmacy & Health', 'Banking & Cash', 'Personal Care', 'Services & Repair', 'General']
   - suggested_stop: name of shop or location (e.g. 'Supermarket', 'Print Shop', 'Post Office / Locker', 'ATM', 'Pharmacy')
   - urgency: 'low', 'medium', or 'high' (high if urgent words or specific deadline)
   - deadline: explicit time restriction if mentioned (e.g. 'before 5 PM') or null
   - prep_items: list of items to carry (e.g. ['Shopping bag', 'USB Drive', 'Parcel pickup code', 'ID card', 'Doctor prescription'])
   - is_perishable: true if refrigerated food/groceries (milk, meat, ice cream), false otherwise
3. Return ONLY a valid JSON object with a single key 'tasks' containing the array of tasks. Do not output markdown codeblocks or preamble."""

async def extract_errands_with_ai(text: str) -> Dict[str, Any]:
    """
    Attempts to extract tasks using Ollama.
    If Ollama is unavailable or response is malformed, falls back to deterministic NLP.
    """
    status = await check_ollama_status()
    
    if status["available"]:
        try:
            prompt = f"Extract all errands from this text: '{text}'"
            payload = {
                "model": DEFAULT_MODEL,
                "prompt": f"{EXTRACTION_SYSTEM_PROMPT}\n\nUser Input: {text}\nJSON Output:",
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1
                }
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
                if response.status_code == 200:
                    resp_json = response.json()
                    response_text = resp_json.get("response", "{}")
                    parsed_dict = json.loads(response_text)
                    
                    # Validate with Pydantic
                    validated = ExtractedTaskList(**parsed_dict)
                    
                    tasks = [t.model_dump() for t in validated.tasks]
                    if tasks:
                        return {
                            "tasks": tasks,
                            "source": "ollama",
                            "model": DEFAULT_MODEL,
                            "count": len(tasks)
                        }
        except Exception as e:
            logger.warning(f"Ollama generation failed or returned invalid JSON ({e}). Falling back to heuristic parser.")

    # Graceful Fallback
    heuristic_tasks = parse_errands_from_text(text)
    return {
        "tasks": heuristic_tasks,
        "source": "heuristic",
        "model": "built-in deterministic parser",
        "count": len(heuristic_tasks)
    }
