
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
from dotenv import load_dotenv, set_key

# Load existing .env
load_dotenv()

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
    reasoning: Optional[str] = None
    source: Optional[str] = None
    count: Optional[int] = 0
    last_date: Optional[str] = None
    subjects: Optional[List[str]] = []
    source: Optional[str] = None
    count: Optional[int] = 0
    last_date: Optional[str] = None
    subjects: Optional[List[str]] = []

class PipelineAction(BaseModel):
    action: str  # "sync", "auto", "rules", "classify", "archive"
    year: Optional[int] = None
    after: Optional[str] = None
    before: Optional[str] = None

class SettingsUpdate(BaseModel):
    google_api_key: Optional[str] = None

class DatabaseStats(BaseModel):
    file_size_mb: float
    total_records: int
    last_backup: Optional[str] = None

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

def _load_rules() -> Dict[str, Any]:
    if not os.path.exists(RULES_FILE):
        return {}
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def _save_rules_file(rules: Dict[str, Any]):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=4, ensure_ascii=False)

@app.get("/api/rules", response_model=List[Rule])
def get_rules():
    rules_dict = _load_rules()
    result = []
    # If it's old list format, convert it (defense)
    if isinstance(rules_dict, list):
        for r in rules_dict:
            if isinstance(r, dict) and 'sender' in r:
                result.append(Rule(**r))
        return result
        
    for sender, info in rules_dict.items():
        rule_data = {"sender": sender, **info}
        result.append(Rule(**rule_data))
    return result

@app.post("/api/rules")
def add_rule(rule: Rule):
    rules = _load_rules()
    if isinstance(rules, list):
        # Convert to dict if we found an old list
        rules = {r['sender']: {k:v for k,v in r.items() if k != 'sender'} for r in rules if 'sender' in r}
    
    sender = rule.sender
    rule_info = rule.dict(exclude={"sender"})
    rules[sender] = rule_info
    
    _save_rules_file(rules)
    
    # Sync to DB: Mark emails as 'Manual' for learning
    try:
        updated = (Email
                   .update(category=rule.category, rule_source='Manual', is_classified=True)
                   .where(Email.sender == sender)
                   .execute())
        logger.info(f"Added/Updated rule for {sender}. Sync'd {updated} emails as 'Manual' in DB.")
    except Exception as e:
        logger.error(f"Failed to sync manual rule to DB: {e}")

    return {"status": "success"}

@app.delete("/api/rules/{sender}")
def delete_rule(sender: str):
    rules = _load_rules()
    if isinstance(rules, list):
        new_rules = [r for r in rules if r.get('sender') != sender]
        _save_rules_file(new_rules)
    else:
        if sender in rules:
            del rules[sender]
            _save_rules_file(rules)
        else:
            raise HTTPException(status_code=404, detail="Rule not found")
            
    logger.info(f"Deleted rule for {sender}")
    return {"status": "success"}

# --- Endpoints: Pipeline ---
def background_sync(limit=None, year=None, after=None, before=None):
    try:
        syncer = EmailSyncer()
        syncer.sync(limit=limit, year=year, after=after, before=before)
        logger.info("Sync Job Completed.")
    except Exception as e:
        logger.error(f"Sync Failed: {e}")

def background_auto():
    try:
        logger.info("Starting Full Auto Pipeline (Sync -> Gen -> Apply)...")
        # 1. Sync last 100 emails
        syncer = EmailSyncer()
        syncer.sync(limit=100)
        
        # 2. Generate and Apply local rules
        gen = RuleGenerator()
        gen.generate_rules(top_n=100)
        gen.apply_rules()
        
        # 3. Push to Gmail
        applier = GmailApplier()
        applier.apply_to_gmail(archive_inbox=True)
        logger.info("Full Auto Pipeline Successful.")
    except Exception as e:
        logger.error(f"Auto Pipeline Failed: {e}")

def background_gen_rules():
    try:
        gen = RuleGenerator()
        gen.generate_rules(top_n=200)
        logger.info("Rule Generation Complete.")
    except Exception as e:
        logger.error(f"Rule Gen Failed: {e}")

def background_classify():
    try:
        gen = RuleGenerator()
        gen.apply_rules()
        logger.info("Local classification (DB update) complete.")
    except Exception as e:
        logger.error(f"Local Classify Failed: {e}")

def background_archive():
    try:
        applier = GmailApplier()
        applier.apply_to_gmail(archive_inbox=True)
        logger.info("Gmail Archive (Cloud labels) complete.")
    except Exception as e:
        logger.error(f"Cloud Archive Failed: {e}")

@app.post("/api/pipeline")
def run_pipeline(action: PipelineAction, background_tasks: BackgroundTasks):
    logger.info(f"Received pipeline request: action={action.action}, after={action.after}, before={action.before}")
    if action.action == "sync":
        background_tasks.add_task(background_sync, limit=None, year=action.year, after=action.after, before=action.before)
    elif action.action == "auto":
        background_tasks.add_task(background_auto)
    elif action.action == "rules":
        background_tasks.add_task(background_gen_rules)
    elif action.action == "classify":
        background_tasks.add_task(background_classify)
    elif action.action == "archive":
        background_tasks.add_task(background_archive)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    return {"status": "started", "action": action.action}

# --- Endpoints: Settings & DB Management ---
@app.get("/api/settings")
def get_settings():
    return {
        "google_api_key": os.getenv("GOOGLE_API_KEY", ""),
        "has_credentials": os.path.exists("credentials.json")
    }

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate):
    if settings.google_api_key:
        # Set in current environment
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key
        # Persist to .env file
        env_path = ".env"
        # Create empty .env if not exists
        if not os.path.exists(env_path):
            with open(env_path, "w") as f:
                pass
        
        set_key(env_path, "GOOGLE_API_KEY", settings.google_api_key)
        logger.info("Updated Google API Key in session and .env file.")
    return {"status": "success"}

@app.get("/api/database/stats")
def get_db_stats():
    db_path = "emails.db"
    size_mb = 0
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
    
    total = Email.select().count()
    return {
        "file_size_mb": round(size_mb, 2),
        "total_records": total
    }

@app.post("/api/database/clear")
def clear_database():
    try:
        # Safely delete all records
        q = Email.delete()
        q.execute()
        logger.info("Database cleared by user request.")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
