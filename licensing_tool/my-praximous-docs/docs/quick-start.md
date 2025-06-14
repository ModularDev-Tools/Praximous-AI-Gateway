---
sidebar_position: 1
title: Quick Start Guide
---

# Quick Start Guide

Welcome to Praximous! This guide will walk you through setting up and running your own instance of Praximous, the secure, on-premise AI gateway.

## Introduction to Praximous

Praximous is designed to be an intelligent and self-aware AI gateway that allows for seamless LLM orchestration and Smart Skill development. It provides a robust backend API, a flexible skill execution system, and is built with an enterprise-ready, stateless architecture.

This guide is for developers and administrators looking to deploy and interact with Praximous for the first time.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker and Docker Compose:** Praximous is designed to run in containers. [Install Docker](https://docs.docker.com/get-docker/)
*   **Git:** For cloning the Praximous repository. [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
*   **(Optional)** A basic understanding of APIs, LLMs, and YAML configuration files.

## Step 1: Getting the Praximous Code

First, clone the Praximous repository to your local machine:

```bash
git clone https://github.com/TheGiblets/Praximous.git # Replace with your actual repository URL
cd Praximous # Or your project directory name, e.g., praximous_mvp_scaffold
```

## Step 2: Environment Configuration (`.env` file)

Praximous uses an `.env` file to manage environment-specific configurations, especially API keys.

1.  In the root of the cloned project, copy the template file:
    ```bash
    cp .env.template .env
    ```
2.  Open the newly created `.env` file in a text editor.
3.  Fill in the required API keys and URLs:
    *   `GEMINI_API_KEY`: Your API key for Google Gemini models.
    *   `OLLAMA_API_URL`: The full URL for your running Ollama instance (e.g., `http://host.docker.internal:11434` if Ollama is on your host and Praximous is in Docker, or `http://localhost:11434` if both are local).
    *   Review other optional variables like `SEARCH_API_KEY`, `WEATHER_API_KEY`, and SMTP settings if you plan to use those skills immediately.

## Step 3: Initializing Praximous Identity

Praximous needs an operational identity to function. This is done via an interactive command:

```bash
docker-compose run --rm praximous python main.py --init
```

This command will:
*   Prompt you for system identity details (System Name, Business Name, Industry, etc.).
*   Prompt you for API keys that were not found in your `.env` file (based on `config/providers.yaml`).
*   Save your identity to `config/identity.yaml` and API keys to your `.env` file.

## Step 4: Launching Praximous

Once the identity and environment are configured, you can launch Praximous using Docker Compose:

```bash
docker-compose up -d --build
```

*   The `--build` flag ensures images are built if they don't exist or if the Dockerfile has changed.
*   The `-d` flag runs the containers in detached mode (in the background).

To confirm Praximous is running:
*   Check Docker Desktop or run `docker ps`. You should see a container for the `praximous` service.
*   Praximous API will be available at: `http://localhost:8000`
*   Interactive API Docs (Swagger UI): `http://localhost:8000/docs`
*   Praximous GUI: `http://localhost:8000/`

## Step 5: Making Your First API Request

You can interact with Praximous using tools like `curl`, Postman, or any HTTP client.

**Example 1: Calling the `echo` skill**

Send a POST request to `http://localhost:8000/api/v1/process` with the following JSON body:

```json
{
  "task_type": "echo",
  "prompt": "Hello Praximous!"
}
```

**Example 2: Calling an LLM task (e.g., `default_llm_tasks`)**

Ensure your `GEMINI_API_KEY` or `OLLAMA_API_URL` is correctly set up.
Send a POST request to `http://localhost:8000/api/v1/process` with:

```json
{
  "task_type": "default_llm_tasks",
  "prompt": "What is the capital of France?"
}
```

**Expected Response Structure:**
You'll receive a JSON response similar to this:
```json
{
  "status": "success", // or "error"
  "result": { /* skill-specific or LLM output */ },
  "message": "Descriptive message",
  "request_id": "unique-request-id"
}
```

## Step 6: Exploring the GUI

Navigate to `http://localhost:8000/` in your web browser to access the Praximous GUI. From here, you can (depending on implemented features):
*   Submit tasks.
*   View system status.
*   Explore analytics and audit logs.
*   View available skills and their capabilities.

## Next Steps & Further Reading

Congratulations! You've successfully set up and interacted with Praximous.
*   Explore the **Interactive API Docs** (`http://localhost:8000/docs`) for detailed endpoint information.
*   Dive deeper into **Skill Development** by reading the `SKILL_DEVELOPMENT_GUIDE.md` in the project root.
*   Check out the full list of available **Skills** and their capabilities via the API or GUI.
*   Review the project **ROADMAP.md** to see what's next for Praximous.