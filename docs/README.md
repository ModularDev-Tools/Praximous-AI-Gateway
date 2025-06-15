# Praximous: A Secure, On-Premise AI Gateway

**Version: 1.0 (Commercially Viable MVP)**

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

- **🎨 Rich GUI**: An intuitive React-based web interface for task submission, system monitoring, analytics visualization, and skill exploration.
- **🧠 Smart Skill Platform**: Develop and deploy modular, business-specific logic units that can operate independently or in conjunction with LLMs.
- **🛡️ Resilient Failover Architecture**: Use a primary external LLM (e.g., Gemini), with automatic failover to a secondary provider (e.g., a local Ollama model) to ensure uptime.
- **🏠 Secure On-Prem Deployment**: Fully containerized via Docker. No cloud dependencies—your data never leaves your environment.
- **🔌 Pluggable Provider Architecture**: Supports multiple LLM providers. Add or switch models by editing a simple config file.
- **📊 Analytics & Auditing**: Built-in SQLite logging for every API interaction, providing full traceability, usage tracking, and optimization insights via an analytics endpoint and the GUI.
- **🧵 Centralized API Gateway**: One stable, authenticated endpoint for all internal tools and applications.
- **🎭 Context-Aware Persona**: Defines a unique identity (persona, industry context) for your gateway, ensuring all AI interactions are consistent with your business style.
- **📜 Tiered Licensing System**: Feature flags and license verification to support different product tiers (e.g., Pro, Enterprise).
- **📚 The Dojo (Documentation Portal)**: Comprehensive documentation including a Quick Start Guide and tutorials.
- **📰 The Town Hall (Content Hub)**: A blog for product updates and articles.

## 🛠️ Tech Stack

- **Backend**: Python
- **API**: FastAPI
- **Deployment**: Docker
- **Database**: SQLite (for audit logging)
- **Frontend GUI**: React

---

## 🌱 Development Journey: Challenges & Learnings

Building Praximous has been a rewarding experience, filled with its share of technical hurdles. Here are a few notable challenges and how we navigated them:

*   **Docker & Virtualization:** Early on, we encountered issues getting Docker to run correctly on a Windows development machine. This was traced back to virtualization support (like VSM or Intel VT-x/AMD-V) not being enabled in the system BIOS. Enabling this crucial setting was key to getting our containerized environment up and running smoothly.

*   **Documentation Site Deployment:** Setting up and deploying our Docusaurus-based documentation site ("The Dojo") to GitHub Pages had its moments. We faced issues with author configurations and ensuring the correct Git user and repository URLs were used for deployment. Diligent cache clearing, careful configuration checks, and ensuring the `GIT_USER` environment variable was correctly set for Windows deployments were essential to resolve these.

*   **API Key Management & Security:** Securely handling API keys for various LLM providers and for Praximous itself (for future API token authentication) required careful planning. We opted for environment variables (`.env` file) for storing sensitive keys, a separate `licensing_tool` for generating cryptographic license keys, and a robust verification module within Praximous.

*   **Configuration Complexity:** Managing various configurations (identity, providers, skills) led to the adoption of YAML files and clear structures, along with CLI tools for initialization and management, to keep things organized and user-friendly.

These experiences have reinforced the importance of thorough environment checks, meticulous configuration management, and the iterative nature of software development. Each challenge overcome has made Praximous a more robust and well-rounded platform.

---

## 🚀 Quickstart: 5-Minute Setup

### 1. Prerequisites

- Docker & Docker Compose installed and running.

### 2. Get the Code

```bash
git clone https://github.com/JamesTheGiblet/praximous_mvp_scaffold.git # Or your specific project repository URL
cd praximous_mvp_scaffold # Or your specific project directory name
3. Configure Your Environment
Copy the environment template to a new .env file.

bash
cp .env.template .env
Now, open the .env file and add your API keys.

4. Initialize Praximous Identity
Before the first launch, run the interactive setup wizard. This defines your gateway’s unique identity and persona, creating the config/identity.yaml file.

bash
docker-compose run --rm praximous python main.py --init
(Note: This command will also guide you through setting API keys if you skipped the previous step).

5. Launch Praximous
bash
docker-compose up -d --build
The gateway is now running and accessible.

API URL: http://localhost:8000
Interactive API Docs: http://localhost:8000/docs
Praximous GUI: http://localhost:8000/
Live Documentation (The Dojo): https://JamesTheGiblet.github.io/praximous_mvp_scaffold/
Blog (The Town Hall): https://JamesTheGiblet.github.io/praximous_mvp_scaffold/blog/
📡 API Endpoints
Process a Request
POST /api/v1/process
Description: The main endpoint for executing both LLM tasks and local Smart Skills.
Example Payload for an LLM task:
json
{
  "task_type": "default_llm_tasks",
  "prompt": "Explain the concept of containerization in three sentences."
}
Example Payload for a local skill:
json
{
  "task_type": "echo",
  "prompt": "Hello world"
}
View Analytics
GET /api/v1/analytics
Description: Retrieves a paginated and filterable audit log of all interactions.
Query Parameters:
limit (int, default: 50): Number of records to return.
offset (int, default: 0): Number of records to skip (for pagination).
task_type (string, optional): Filter by a specific task type.
Example: curl "http://localhost:8000/api/v1/analytics?limit=10&task_type=echo"
View Skills
GET /api/v1/skills
GET /api/v1/skills/{skill_name}/capabilities
Analytics Chart Data
GET /api/v1/analytics/charts/tasks-over-time
GET /api/v1/analytics/charts/requests-per-provider
GET /api/v1/analytics/charts/average-latency-per-provider
System & Configuration
GET /api/v1/system-status: View the status of configured LLM providers.
GET /api/v1/config/providers: View the content of providers.yaml.
Premium Features (Enterprise Tier)
RAG Interface (Placeholder):
POST /api/v1/rag/query
GET /api/v1/rag/settings
PII Redaction Skill:
task_type: "pii_redactor" via /api/v1/process
📜 Licensing
Praximous offers different tiers with varying features. A valid license key (set via the PRAXIMOUS_LICENSE_KEY environment variable) is required to unlock Pro and Enterprise features. License keys are cryptographically signed and validated by the system. For more information, please see our documentation at https://JamesTheGiblet.github.io/praximous_mvp_scaffold/.
🛠️ Management Commands
Praximous provides a few command-line utilities for managing your instance, run via python main.py (or docker-compose run --rm praximous python main.py <command> if you prefer to use the Docker environment).

Initialize Identity (as in Quickstart)
bash
python main.py --init
Sets up the initial config/identity.yaml and guides through API key configuration.

Rename System
bash
python main.py --rename "New-System-Identifier"
Updates the system_name in your config/identity.yaml. The display name in logs will update on the next application restart.

Reset Identity
bash
python main.py --reset-identity
Prompts for confirmation and then deletes the config/identity.yaml file, allowing you to re-initialize from scratch. Use with caution.

📚 Documentation & Community
The Dojo (Full Documentation): Visit https://JamesTheGiblet.github.io/praximous_mvp_scaffold/ for comprehensive guides, API references, and tutorials.
The Town Hall (Blog & Updates): Check out our blog at https://JamesTheGiblet.github.io/praximous_mvp_scaffold/blog/ for the latest news, product updates, and articles.
