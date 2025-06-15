# populate_fake_audit_data.py
import sqlite3
import os
import uuid
from datetime import datetime, timedelta, timezone
import random
import json

LOGS_DIR = "logs"
DB_PATH = os.path.join(LOGS_DIR, "praximous_audit.db")

def generate_fake_data(num_records=100):
    """Generates and inserts fake interaction records into the audit database."""

    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        print(f"Created directory: {LOGS_DIR}")

    # Ensure the table exists (init_db from audit_logger would do this, but we can be safe)
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
    except Exception as e:
        print(f"Error ensuring table exists: {e}")
        return

    task_types = ["default_llm_tasks", "echo", "text_manipulation", "simple_math", "internal_summary", "datetime_tool", "weather_tool", "web_scraper", "csv_parser", "sentiment_analyzer", "web_search_tool", "email_sender", "pii_redactor"]
    providers = ["gemini_pro_model", "ollama_default", "skill:echo", "skill:text_manipulation", "skill:simple_math", "skill:internal_summary", "skill:datetime_tool", "skill:weather_tool", "skill:web_scraper", "skill:csv_parser", "skill:sentiment_analyzer", "skill:web_search_tool", "skill:email_sender", "skill:pii_redactor", None]
    statuses = ["success", "error"]
    sample_prompts = [
        "What is the capital of France?",
        "Explain quantum computing simply.",
        "Hello there!",
        "Convert this to uppercase: test",
        "Calculate 2 + 2",
        "Summarize the following text: ...",
        "What time is it in London?",
        "Get current weather for Berlin",
        "Extract text from example.com",
        "What's the date today?",
        "name,value\nitem1,10\nitem2,20", # Sample CSV data
        "I love using Praximous, it's fantastic!", # Sample text for sentiment
        "Current news about renewable energy", # Sample search query
        "Send a status update email", # Sample prompt for email
        "My phone number is 555-1234 and I live at 123 Main St." # Sample prompt for PII redaction
    ]

    records_to_insert = []
    start_time = datetime.now(timezone.utc)

    for i in range(num_records):
        request_id = str(uuid.uuid4())
        # Spread timestamps over the last 30 days
        timestamp_dt = start_time - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        timestamp = timestamp_dt.isoformat()
        task_type = random.choice(task_types)
        provider = random.choice(providers)
        status = random.choice(statuses)
        latency_ms = random.randint(50, 3000) if status == "success" else random.randint(100, 500)
        prompt = random.choice(sample_prompts)
        
        response_content = {}
        if status == "success":
            response_content = {"result": f"Successful response for {prompt[:20]}...", "provider": provider}
        else:
            response_content = {"detail": f"Error processing {task_type}", "provider": provider}
        response_data_str = json.dumps(response_content)

        records_to_insert.append((
            request_id, timestamp, task_type, provider, status, latency_ms, prompt, response_data_str
        ))

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO interactions (request_id, timestamp, task_type, provider, status, latency_ms, prompt, response_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, records_to_insert)
            conn.commit()
        print(f"Successfully inserted {len(records_to_insert)} fake records into '{DB_PATH}'.")
    except Exception as e:
        print(f"Failed to insert fake records: {e}")

if __name__ == "__main__":
    num = input("How many fake records do you want to generate? (default: 100): ")
    try:
        num_records = int(num) if num else 100
    except ValueError:
        num_records = 100
        print("Invalid input, defaulting to 100 records.")
    generate_fake_data(num_records)