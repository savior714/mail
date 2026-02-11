
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import queue
import threading
import json
import os
from datetime import datetime

# Import existing services
# Ensure root is in path or run as module
from src.models import init_db, Email, fn
from src.services.syncer import EmailSyncer
from src.services.rule_generator import RuleGenerator
from src.services.gmail_applier import GmailApplier

# --- Config ---
app = FastAPI(title="Gmail AI Archivist API")

# CORS for React frontend (default Vite port: 5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Logging & State ---
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put({
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": log_entry
        })

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Clear existing handlers to avoid dupes if reloaded
if not any(isinstance(h, QueueHandler) for h in logger.handlers):
    q_handler = QueueHandler()
    q_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(q_handler)

# --- Models ---
class Rule(BaseModel):
    sender: str
    category: str
    keywords: Optional[str] = None

class PipelineAction(BaseModel):
    action: str  # "sync", "auto", "rules"
    year: Optional[int] = None

# --- Startup ---
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized.")

# --- Endpoints: Dashboard ---
@app.get("/api/stats")
def get_stats():
    try:
        total = Email.select().count()
        classified = Email.select().where(Email.is_classified == True).count()
        trash_count = Email.select().where(Email.size_estimate > 1000000).count() # Dummy logic
        avg_size = Email.select(fn.AVG(Email.size_estimate)).scalar() or 0
        
        # Chart Data (Group by Month)
        monthly_data = (Email
                        .select(fn.strftime('%Y-%m', Email.date).alias('month'), fn.COUNT(Email.id).alias('count'))
                        .group_by(fn.strftime('%Y-%m', Email.date))
                        .order_by(fn.strftime('%Y-%m', Email.date).desc())
                        .limit(6))
        
        chart_data = [{"month": row.month, "count": row.count} for row in monthly_data]
        chart_data.reverse() # Chronological order

        return {
            "total_emails": total,
            "classified": classified,
            "trash_found": trash_count,
            "avg_size_kb": int(avg_size / 1024),
            "chart_data": chart_data
        }
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints: Rules ---
RULES_FILE = "rules.json"

def _load_rules():
    if not os.path.exists(RULES_FILE):
        return []
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_rules_file(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)

@app.get("/api/rules", response_model=List[Rule])
def get_rules():
    return _load_rules()

@app.post("/api/rules")
def add_rule(rule: Rule):
    rules = _load_rules()
    # Check duplicate
    if any(r['sender'] == rule.sender for r in rules):
        raise HTTPException(status_code=400, detail="Rule for sender already exists")
    
    rules.append(rule.dict())
    _save_rules_file(rules)
    logger.info(f"Added rule for {rule.sender}")
    return {"status": "success"}

@app.delete("/api/rules/{sender}")
def delete_rule(sender: str):
    rules = _load_rules()
    new_rules = [r for r in rules if r['sender'] != sender]
    if len(rules) == len(new_rules):
        raise HTTPException(status_code=404, detail="Rule not found")
    
    _save_rules_file(new_rules)
    logger.info(f"Deleted rule for {sender}")
    return {"status": "success"}

# --- Endpoints: Pipeline ---
def background_sync(limit=50, year=None):
    try:
        syncer = EmailSyncer()
        syncer.sync(limit=limit, year=year)
        logger.info("Sync Job Completed.")
    except Exception as e:
        logger.error(f"Sync Failed: {e}")

def background_auto():
    try:
        logger.info("Starting Full Auto Pipeline...")
        syncer = EmailSyncer()
        syncer.sync(limit=None, after="2024/01/01", before="2024/02/01")
        
        gen = RuleGenerator()
        gen.generate_rules()
        gen.apply_rules()
        
        applier = GmailApplier()
        applier.apply_to_gmail(archive_inbox=True)
        logger.info("Full Auto Pipeline Successful.")
    except Exception as e:
        logger.error(f"Auto Pipeline Failed: {e}")

def background_gen_rules():
    try:
        gen = RuleGenerator()
        gen.generate_rules()
        logger.info("Rule Generation Complete.")
    except Exception as e:
        logger.error(f"Rule Gen Failed: {e}")

@app.post("/api/pipeline")
def run_pipeline(action: PipelineAction, background_tasks: BackgroundTasks):
    if action.action == "sync":
        background_tasks.add_task(background_sync, limit=50, year=action.year)
    elif action.action == "auto":
        background_tasks.add_task(background_auto)
    elif action.action == "rules":
        background_tasks.add_task(background_gen_rules)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    return {"status": "started", "action": action.action}

# --- Endpoints: Logs ---
@app.get("/api/logs")
def get_logs():
    """Flush the queue and return logs."""
    logs = []
    while not log_queue.empty():
        try:
            logs.append(log_queue.get_nowait())
        except queue.Empty:
            break
    return logs

if __name__ == "__main__":
    import uvicorn
    # Reload=True for dev
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
