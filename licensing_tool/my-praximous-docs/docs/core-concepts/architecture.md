---
id: architecture
title: Praximous Architecture
sidebar_label: Architecture
---

# Praximous Architecture

Understanding the architecture of Praximous is key to leveraging its full potential for secure, on-premise AI orchestration. Praximous is designed with modularity, resilience, and extensibility at its core.

## Core Philosophy

Praximous operates on a few fundamental principles:

*   **🛡️ On-Premise First**: All operations are designed to be run within your own environment, ensuring data sovereignty and control.
*   **🔒 Secure by Design**: Acts as a secure gateway, minimizing direct exposure of your internal systems and data to external services.
*   **🔗 Resilient & Agnostic**: Built to avoid vendor lock-in with support for multiple AI providers and dynamic failover capabilities.
*   **🧩 Extensible & Modular**: Easily extendable through custom "Smart Skills" and pluggable provider integrations.

## High-Level Components

Praximous consists of several key components that work together:

```mermaid
graph TD
    A[User/Application] --> B{Praximous API Gateway};
    B -- Request --> C[Skill Manager];
    C -- Identifies Skill --> D[Specific Smart Skill];
    D -- Needs AI Model --> E[Provider Manager];
    E -- Selects Provider --> F[AI Provider A (e.g., Gemini)];
    E -- Selects Provider --> G[AI Provider B (e.g., Ollama)];
    D -- Needs External Service --> H[External API/Service];
    F --> E;
    G --> E;
    H --> D;
    E --> D;
    D --> C;
    C -- Response --> B;
    B -- Response --> A;

    subgraph Praximous Core
        B
        C
        D
        E
    end

    subgraph External Services
        F
        G
        H
    end

    style B fill:#002147,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#002147,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#FF9F1C,stroke:#000,stroke-width:2px,color:#000
    style E fill:#002147,stroke:#fff,stroke-width:2px,color:#fff
```

1.  **API Gateway (FastAPI Application)**:
    *   The primary entry point for all interactions with Praximous, typically via the `/api/v1/process` endpoint.
    *   Handles request validation, authentication (if implemented), and routing to the appropriate internal components.
    *   Built using FastAPI for high performance and automatic API documentation (Swagger UI/ReDoc).

2.  **Skill Manager (`core.skill_manager.SkillManager`)**:
    *   Responsible for discovering, loading, and managing all available Smart Skills.
    *   Dynamically loads skills from the `skills/` directory.
    *   Orchestrates the execution of a specific skill based on the `task_type` in the API request.

3.  **Smart Skills (e.g., `skills/*_skill.py`)**:
    *   Modular, self-contained units of logic that perform specific tasks (e.g., `echo`, `default_llm_tasks`, custom business logic).
    *   Inherit from `core.skill_manager.BaseSkill`.
    *   Can interact with AI Providers, external APIs, or perform data processing.
    *   Define their own capabilities and parameters via the `get_capabilities()` method.

4.  **Provider Manager**:
    *   Manages connections and interactions with various AI model providers (e.g., Google Gemini, local Ollama instances, other third-party LLMs).
    *   Handles API key management (via `.env` and `config/providers.yaml`).
    *   Facilitates dynamic failover between providers if one becomes unavailable.

5.  **Configuration Layer**:
    *   **`identity.yaml`**: Defines the core identity and persona of the Praximous instance.
    *   **`providers.yaml`**: Configures available AI providers, their models, and parameters.
    *   **`.env`**: Stores sensitive information like API keys and external service URLs.

6.  **GUI (Web Interface)**:
    *   Provides a user-friendly interface for interacting with Praximous, submitting tasks, and potentially viewing logs or skill capabilities.
    *   Served by the same FastAPI application.

## Key Design Principles

*   **Statelessness**: The core Praximous application is designed to be stateless, meaning it doesn't store request-specific data between interactions. This is crucial for scalability and resilience, allowing multiple instances to run behind a load balancer. (State, if needed, would typically be managed by external databases or the skills themselves if they interact with stateful services).
*   **Pluggable Architecture**: Both Smart Skills and AI Providers are designed as plugins. New skills can be added by simply placing a Python file in the `skills/` directory. New providers can be integrated by adding their configuration and implementing a corresponding client.
*   **Security First**: By acting as an intermediary, Praximous limits direct exposure of your applications and data to external AI services. API key management and secure configuration are central.
*   **Configuration-Driven**: Many aspects of Praximous, from its identity to available AI models, are controlled through YAML configuration files and environment variables, allowing for easy customization without code changes.

## Data Flow Example: `/api/v1/process`

1.  A **User or Application** sends a POST request to `/api/v1/process` with a JSON payload (e.g., `{"task_type": "default_llm_tasks", "prompt": "What is AI?"}`).
2.  The **API Gateway** receives the request, validates it.
3.  The request is routed to the **Skill Manager**.
4.  The **Skill Manager** identifies the `default_llm_tasks` skill based on the `task_type`.
5.  The `default_llm_tasks` **Smart Skill** is executed.
6.  The skill determines it needs to interact with an LLM. It requests an LLM interaction from the **Provider Manager**.
7.  The **Provider Manager**, based on `providers.yaml` and availability, selects an **AI Provider** (e.g., Gemini).
8.  The request (prompt) is sent to the chosen AI Provider.
9.  The AI Provider processes the prompt and returns a response.
10. The response is returned through the Provider Manager to the Smart Skill.
11. The Smart Skill processes the LLM's response and builds a standardized output using `_build_response()`.
12. The skill's response is returned to the Skill Manager, then to the API Gateway.
13. The API Gateway sends the final JSON response back to the User/Application.

This architecture allows Praximous to be a flexible and powerful layer for integrating AI capabilities into your enterprise workflows securely and efficiently.
