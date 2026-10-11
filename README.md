# 🌿 ErrandQuest — One Trip. Everything Done.

> **Theme:** Touch Grass — Open-Source AI for Real-World Utility  
> **Stack:** React (Vite) + FastAPI (Python) + SQLite + Ollama (Hybrid Local AI Architecture)

---

## 🌟 Overview

ErrandQuest is an AI-powered personal assistant designed to turn a scattered inbox of daily tasks into **one organized outdoor outing**.

### Core Value Proposition:
Instead of remembering errands individually and making multiple trips throughout the day, users add everything into a single natural-language box. ErrandQuest extracts the tasks, clusters them into sensible stops, respects prerequisites and perishable food rules, auto-generates a packing checklist, and provides a mobile-first live execution checklist.

---

## 🚀 Key Features Built to PRD Specs

1. **Natural-Language Task Capture (Inbox View)**:
   * Type or paste tasks in free-form English (e.g. *"Buy milk and vegetables, print my assignment, collect parcel before 5, get shampoo, and withdraw cash at ATM"*).
   * Dual-engine extraction:
     * **Built-in Fast Heuristic NLP** (0ms latency, zero RAM footprint, 0% crash risk).
     * **Ollama Local AI** (`llama3.2:1b` / `qwen2.5`) with structured JSON schema and Pydantic validation.
   * Safe preview & confirmation drawer before saving.
   * **Duplicate Errand Warning**: Flags potential duplicates (e.g. *"Need milk too"* vs *"Buy milk"*) without deleting either task.
   * Single-task manual entry form for instant offline task addition.

2. **Smart Grouping & Trip Planning (Plan View)**:
   * Clusters related items (e.g. milk + vegetables $\rightarrow$ Grocery Store; print + photocopy $\rightarrow$ Print Shop).
   * **Prerequisite Ordering**: Banking / ATM stops scheduled first so cash is ready for subsequent stops.
   * **Urgency & Deadline Prioritization**: Tasks with tight deadlines (e.g. *"before 4 PM"*) are scheduled early.
   * **Refrigeration & Freshness Rule**: Perishable items (milk, ice cream, meat) are scheduled near the end so groceries don't spoil.
   * Interactive **Reordering**: Move stops up or down with one click.

3. **Departure Checklist (Ready to Leave? View)**:
   * Dynamically derived from tasks:
     * Groceries $\rightarrow$ Cloth / Shopping bags
     * Print shop $\rightarrow$ Document on USB drive / phone
     * Courier / Parcel pickup $\rightarrow$ Tracking OTP code & Photo ID
     * Banking $\rightarrow$ ATM card / Passbook
   * Interactive check-off toggles and custom packing item additions.

4. **Live Outing Execution (My Trip View)**:
   * Mobile-first high contrast UI for outdoor sunlight visibility.
   * Stop-by-stop execution with large touch targets.
   * Live completion progress bar.
   * **Graceful Incomplete Trips (FR-07)**: If an outing is ended early, completed tasks are saved as done, and remaining unfinished errands are automatically marked `carry_forward` for the next outing.
   * **Trip Summary (FR-09)**: Clear breakdown of completed tasks, visited stops, and carried-forward errands.

---

## 🛠️ How to Run

### Option 1: One-Click PowerShell Launcher
In the project directory:
```powershell
.\run_dev.ps1
```

### Option 2: Running Components Separately

#### 1. Backend (FastAPI):
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
* API runs at: `http://localhost:8000`
* Interactive OpenAPI Swagger docs: `http://localhost:8000/docs`

#### 2. Frontend (React + Vite):
```bash
cd frontend
npm run dev
```
* App opens at: `http://localhost:5173`

---

## 🧠 Optional Ollama Setup (Low RAM Friendly)

If you'd like to use a local LLM instead of the built-in fast parser:
1. Download Ollama from [ollama.ai](https://ollama.ai).
2. Pull the ultra-lightweight 1B model (only ~1.3 GB RAM):
   ```bash
   ollama run llama3.2:1b
   ```
3. ErrandQuest will automatically detect the running Ollama instance and switch the header badge from `⚡ Built-in Fast NLP` to `🤖 Ollama (llama3.2:1b)`.
4. If Ollama is closed, ErrandQuest immediately and seamlessly falls back to the built-in engine without errors or freezing.

---
