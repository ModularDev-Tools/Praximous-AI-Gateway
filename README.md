# Praximous: A Secure, On-Premise AI Gateway

**Version: 1.0 (MVP)**

## 🧠 Overview

Praximous is an intelligent, secure AI gateway for enterprises. It serves as a central, on-premise orchestration layer that gives you full control over AI usage. With dynamic failover, pluggable providers, and reusable "Smart Skills," Praximous transforms how you deploy and scale large language models (LLMs).

## 🚨 The Problems Praximous Solves

| Challenge              | Solution                                  |
| ---------------------- | ----------------------------------------- |
| 💸 **Uncontrolled Costs** | Use powerful LLMs only when needed.        |
| 🔐 **Data Security** | Keep all data on-premise via Docker.        |
| 🧱 **Vendor Lock-In** | Swap providers easily—no code changes.      |
| 🧩 **Dev Complexity** | Unified API endpoint + reusable Smart Skills|

## ⚙️ Core MVP Features

- **🧠 Smart Skill Platform**: Modular, business-specific logic units that run independently of LLMs (e.g., data transformation, simple calculations).
- **🛡️ Resilient Failover Architecture**: Use a primary external LLM (e.g., Gemini), with automatic failover to a secondary provider (e.g., a local Ollama model) to ensure uptime.
- **🏠 Secure On-Prem Deployment**: Fully containerized via Docker. No cloud dependencies—your data never leaves your environment.
- **🔌 Pluggable Provider Architecture**: Supports multiple LLM providers. Add or switch models by editing a simple config file.
- **📊 Analytics & Auditing**: Built-in SQLite logging for every API interaction, providing full traceability, usage tracking, and optimization insights via an analytics endpoint.
- **🧵 Centralized API Gateway**: One stable, authenticated endpoint for all internal tools and applications.
- **🎭 Context-Aware Persona**: Defines a unique identity (persona, industry context) for your gateway, ensuring all AI interactions are consistent with your business style.

## 🛠️ Tech Stack

- **Backend**: Python
- **API**: FastAPI
- **Deployment**: Docker
- **Database**: SQLite (for audit logging)

---

## 🚀 Quickstart: 5-Minute Setup

### 1. Prerequisites

- Docker & Docker Compose installed and running.

### 2. Get the Code

```bash
git clone [https://github.com/your-org/praximous.git](https://github.com/your-org/praximous.git)
cd praximous
```

### 3. Configure Your Environment

Copy the environment template to a new `.env` file.

```bash
cp .env.template .env
```
Now, open the `.env` file and add your API keys.

### 4. Initialize Praximous Identity

Before the first launch, run the interactive setup wizard. This defines your gateway’s unique identity and persona, creating the `config/identity.yaml` file.

```bash
docker-compose run --rm praximous python main.py --init
```
*(Note: This command will also guide you through setting API keys if you skipped the previous step).*

### 5. Launch Praximous

```bash
docker-compose up -d --build
```

The gateway is now running and accessible.
- **API URL**: `http://localhost:8000`
- **Interactive API Docs**: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### Process a Request
- **POST** `/api/v1/process`
- **Description**: The main endpoint for executing both LLM tasks and local Smart Skills.
- **Example Payload for an LLM task**:
  ```json
  {
    "task_type": "default_llm_tasks",
    "prompt": "Explain the concept of containerization in three sentences."
  }
  ```
- **Example Payload for a local skill**:
  ```json
  {
    "task_type": "echo",
    "prompt": "Hello world"
  }
  ```

### View Analytics
- **GET** `/api/v1/analytics`
- **Description**: Retrieves a paginated and filterable audit log of all interactions.
- **Query Parameters**:
    - `limit` (int, default: 50): Number of records to return.
    - `offset` (int, default: 0): Number of records to skip (for pagination).
    - `task_type` (string, optional): Filter by a specific task type.
- **Example**: `curl "http://localhost:8000/api/v1/analytics?limit=10&task_type=echo"`

### View Skills
- **GET** `/api/v1/skills`
- **Description**: Lists all registered Smart Skills and their capabilities.

---
## 🧭 Development Roadmap
(Your roadmap section can remain as is)

```
