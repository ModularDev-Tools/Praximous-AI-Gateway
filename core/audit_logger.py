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
    task_type: Optional[str] = None,
    start_date: Optional[str] = None, # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
) -> List[Dict[str, Any]]:
    """
    Retrieves a paginated and optionally filtered list of interaction records by task_type and date range.
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
            conditions = []
            params = []

            # Add filtering
            if task_type:
                conditions.append("task_type = ?")
                params.append(task_type)
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(f"{start_date}T00:00:00.000Z") # Assume start of day UTC
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(f"{end_date}T23:59:59.999Z") # Assume end of day UTC
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

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
def count_interactions(
    task_type: Optional[str] = None,
    start_date: Optional[str] = None, # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
) -> int:
    """Counts the total number of interactions, with optional filters for task_type and date range."""
    if not os.path.exists(DB_PATH):
        return 0
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM interactions"
            conditions = []
            params = []
            if task_type:
                conditions.append("task_type = ?")
                params.append(task_type)
            if start_date:
                conditions.append("timestamp >= ?")
                params.append(f"{start_date}T00:00:00.000Z")
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(f"{end_date}T23:59:59.999Z")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    except Exception as e:
        log.error(f"Failed to count interactions: {e}", exc_info=True)
        return 0

def get_tasks_over_time_data(
    start_date: Optional[str] = None, # YYYY-MM-DD
    end_date: Optional[str] = None,   # YYYY-MM-DD
    granularity: str = "day" # "day", "month", "year" - default to day
) -> List[Dict[str, Any]]:
    """
    Retrieves aggregated data for tasks over time (count per day/month/year).
    """
    records = []
    if not os.path.exists(DB_PATH):
        return records

    date_format_str = "%Y-%m-%d"
    if granularity == "month":
        date_format_str = "%Y-%m"
    elif granularity == "year":
        date_format_str = "%Y"

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = f"SELECT STRFTIME('{date_format_str}', timestamp) as date_group, COUNT(*) as count FROM interactions"
            conditions = []
            params = []

            if start_date:
                conditions.append("timestamp >= ?")
                params.append(f"{start_date}T00:00:00.000Z")
            if end_date:
                conditions.append("timestamp <= ?")
                params.append(f"{end_date}T23:59:59.999Z")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " GROUP BY date_group ORDER BY date_group ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
    except Exception as e:
        log.error(f"Failed to fetch tasks over time data: {e}", exc_info=True)
    return records

def get_requests_per_provider_data(
    start_date: Optional[str] = None, # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
) -> List[Dict[str, Any]]:
    """Retrieves aggregated data for requests per provider."""
    records = []
    if not os.path.exists(DB_PATH):
        return records
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Ensure provider is not NULL for meaningful grouping
            query = "SELECT COALESCE(provider, 'N/A') as provider_name, COUNT(*) as count FROM interactions"
            conditions = ["provider IS NOT NULL"] # Start with this condition
            params = []
            if start_date: conditions.append("timestamp >= ?"); params.append(f"{start_date}T00:00:00.000Z")
            if end_date: conditions.append("timestamp <= ?"); params.append(f"{end_date}T23:59:59.999Z")
            
            query += " WHERE " + " AND ".join(conditions)
            query += " GROUP BY provider_name ORDER BY count DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
    except Exception as e:
        log.error(f"Failed to fetch requests per provider data: {e}", exc_info=True)
    return records

def get_average_latency_per_provider_data(
    start_date: Optional[str] = None, # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
) -> List[Dict[str, Any]]:
    """Retrieves aggregated data for average latency per provider."""
    records = []
    if not os.path.exists(DB_PATH):
        return records
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT COALESCE(provider, 'N/A') as provider_name, AVG(latency_ms) as average_latency FROM interactions"
            conditions = ["provider IS NOT NULL", "latency_ms IS NOT NULL"] # Filter for relevant records
            params = []
            if start_date: conditions.append("timestamp >= ?"); params.append(f"{start_date}T00:00:00.000Z")
            if end_date: conditions.append("timestamp <= ?"); params.append(f"{end_date}T23:59:59.999Z")
            query += " WHERE " + " AND ".join(conditions)
            query += " GROUP BY provider_name ORDER BY average_latency ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
    except Exception as e:
        log.error(f"Failed to fetch average latency per provider data: {e}", exc_info=True)
    return records

init_db()