# Praximous

An On-Premise AI Gateway for Your Business

The Problem

Using AI in a business is a chaotic mess. Different teams use different models from different providers (OpenAI, Gemini, a local Llama model, etc.). This creates a ton of problems: security is a nightmare, costs are unpredictable, you get locked into one provider, and development is way too complicated.

You end up paying for an expensive, powerful LLM for a simple task that a smaller, local model could have handled. You're losing control.

The Solution

A single, on-premise AI gateway that you control. Praximous is an orchestration layer that you deploy inside your own network (typically in Docker). It acts as the centeral, secure hub for every AI request your company makes.

It puts you back in charge of your data, your costs, and your tech stack.

What It Fixes

    💸 Control Costs: Set rules to route simple tasks to cheap, local models (like one running on Ollama) and save the expensive, powerful models (like top-tier Gemini) for the jobs that actually need them.

    🔐 Keep Your Data Secure: Since it runs on-premise, all requests go through Praximous first. Sensitive data never has to leave your network unless you explicitly allow it.

    🧱 Avoid Vendor Lock-In: Want to switch from one provider to another? It's a simple config change in one place, not a rewrite of a dozen different applications. You can use the best tool for the job, always.

    🧩 Simplify Development: Your developers only need to learn one simple, unified API. They can build reusable "Smart Skills" that chain together complex business logic and AI calls, which can then be used by any application in the company.

Core Features

    Pluggable AI Providers: The system is designed with a modular architecture. Adding a new AI provider—whether it's a cloud service or a local model hosted with Ollama—is as simple as creating a new plugin.

    Unified API Gateway: One clean, consistent API endpoint for all AI interactions.

    "Smart Skill" Engine: The core of the system. Build complex, multi-step workflows that can call different AI models, run business logic, and be reused across the entire organization.

    Dynamic Failover: If your primary AI provider goes down, Praximous automatically reroutes the request to a designated backup provider to ensure high availability.

    Cost & Security Policies: Implement rules at the gateway level to control which users or applications can access which models and to set spending limits.

The Tech Stack

No magic. Just solid, reliable tools.

    Python: For the core application logic.

    Docker / Kubernetes: For secure, containerized on-premise deployment.

    Redis: For high-speed caching of sessions and frequently accessed data.

    Nginx: As the reverse proxy to manage all incoming API requests.

The API

All requests are routed through a central API for easy management.

    POST /api/v1/invoke/skill/{skill_name}

        What it does: Runs a specific, pre-configured "Smart Skill." This is the recommended way to interact with the system for most tasks.

        Body: A JSON payload with the input for the skill.

    POST /api/v1/query/{provider_name}

        What it does: Sends a raw query directly to a specific AI provider. Useful for testing or simple, one-off tasks.

        Body: A JSON payload with the raw prompt.

    GET /api/v1/providers

        What it does: Returns a list of all currently configured and available AI providers and their status.

Stop letting your AI strategy be a chaotic mess. Build a central hub, take control, and own your stack. The code is the proof that a good architecture solves real business problems.
