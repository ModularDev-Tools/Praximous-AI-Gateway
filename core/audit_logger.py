# core/audit_logger.py
import sqlite3
import os
from datetime import datetime, timezone # Import timezone
from typing import Optional, Dict, Any, List
from core.logger import log

LOGS_DIR = "logs"
DB_PATH = os.path.join(LOGS_DIR, "praximous_audit.db")

def init_db():
    # ... (this function remains unchanged)
    os.makedirs(LOGS_DIR, exist_ok=True)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    provider TEXT,
                    status TEXT NOT NULL,
                    latency_ms INTEGER,
                    prompt TEXT,
                    response_data TEXT
                )
            """)
            conn.commit()
            log.info(f"Audit database initialized successfully at '{DB_PATH}'.")
    except Exception as e:
        log.error(f"Failed to initialize audit database: {e}", exc_info=True)


def log_interaction(
    # ... (this function remains unchanged)
    request_id: str,
    task_type: str,
    status: str,
    latency_ms: int,
    provider: Optional[str] = None,
    prompt: Optional[str] = None,
    response_data: Optional[Dict[str, Any]] = None
):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interactions (request_id, timestamp, task_type, provider, status, latency_ms, prompt, response_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_id,
                datetime.now(timezone.utc).isoformat(), # Corrected to timezone.utc
                task_type,
                provider,
                status,
                latency_ms,
                prompt,
                str(response_data) if response_data else None
            ))
            conn.commit()
            log.info(f"Successfully logged interaction for request_id: {request_id}")
    except Exception as e:
        log.error(f"Failed to log interaction for request_id {request_id}: {e}", exc_info=True)

# --- MODIFIED FUNCTION ---
def get_all_interactions(
    limit: int = 100, 
    offset: int = 0, 
    task_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves a paginated and optionally filtered list of interaction records.
    """
    records = []
    if not os.path.exists(DB_PATH):
        return records

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Base query
            query = "SELECT * FROM interactions"
            params = []

            # Add filtering
            if task_type:
                query += " WHERE task_type = ?"
                params.append(task_type)

            # Add ordering, pagination
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
    except Exception as e:
        log.error(f"Failed to fetch interactions: {e}", exc_info=True)
    
    return records

# --- NEW FUNCTION ---
def count_interactions(task_type: Optional[str] = None) -> int:
    """Counts the total number of interactions, with an optional filter."""
    if not os.path.exists(DB_PATH):
        return 0
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM interactions"
            params = []
            if task_type:
                query += " WHERE task_type = ?"
                params.append(task_type)
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    except Exception as e:
        log.error(f"Failed to count interactions: {e}", exc_info=True)
        return 0

init_db()