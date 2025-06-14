🧭 Praximous Development Roadmap
Objective:

Build and deploy a fully containerized, intelligent, and self-aware Praximous MVP — ready for production use, Smart Skill development, and seamless LLM orchestration.

Phase 0: ⚙️ Foundation & Core Logic

Goal: Establish the core architectural and functional bedrock of Praximous by building a stateless, enterprise-ready backend API from the ground up. This phase focuses on creating a robust API endpoint, implementing a flexible skill execution system, and ensuring the architecture supports scalability and maintainability through stateless design.

Tasks:

    [✓] Implement Stateless Architecture
      (Achieved via self-contained API requests and reliance on shared config like identity.yaml, avoiding server-side client session state)

    [✓] Generalize Skill Execution
      (Implemented BaseSkill, SkillManager for auto-discovery from 'skills/' folder, and example skills with standardized responses and capabilities)

    [✓] Create /api/v1/process Endpoint
      (Established the main FastAPI endpoint for receiving and processing skill execution requests)

    [✓] Create test code
      Unit tests for core logic, skill execution, and API endpoint functionality. tests/test_api_phase0.py

✅ Milestone: Stateless API is live, accepting task requests via the `/api/v1/process` endpoint and invoking Smart Skills with contextual data. The architecture is stateless, relying on self-contained requests and shared configuration. A generalized skill execution framework (BaseSkill, SkillManager) allows for dynamic loading and execution of skills from the `skills/` directory, complete with standardized responses and self-describing capabilities.


Phase 1: 🧠 Identity Initialization & API Setup

Goal: Establish Praximous's unique operational identity and persona, enabling it to interact with LLMs in a contextually relevant and consistent manner. This involves setting up its core identity parameters, securely managing API credentials for external services, and implementing mechanisms for this identity to be loaded and utilized throughout the system.

Tasks:

    [✓] Interactive CLI or Config Wizard
      Prompt the user (via python main.py --init) or allow a prefilled identity.yaml.
      Fields: system_name, business_name, industry, persona_style, sensitivity_level, location.

    [✓] API Key Entry & Storage  
      Dynamically prompt for API keys based on `providers.yaml` (e.g., GEMINI_API_KEY, OLLAMA_API_URL) and allow entry of other custom environment variables.
      Write values to .env for secure access.

    [✓] SystemContext Loader
      Load identity.yaml on startup via core/system_context.py.
      Inject context into prompt building, log metadata, and skill metadata.

    [✓] Self-Naming Logic
      Derive a system display name (e.g., Praximous-Acme) at runtime from identity.yaml (system_name, business_name) and inject into logs.

    [✓] Identity Reset & Rename Support
      Provide CLI utilities (`python main.py --rename "New-Name"` and `python main.py --reset-identity`) for users to easily manage their system's configured identity, allowing for straightforward renaming of the `system_name` or complete reset (deletion) of `identity.yaml`.

    [✓] Create test code
      Unit tests for identity initialization, credential management, system context loading, and CLI utilities.tests/test_api_phase1.py

✅ Milestone: Praximous initializes itself with a unique identity, personalized tone, and API credentials — ready for usage and self-consistent behavior.

Phase 2: 🛡️ Resilient & Pluggable Architecture

Goal: Engineer a provider-agnostic and resilient architecture for LLM interactions. This involves creating a `ProviderManager` to handle diverse LLM provider integrations (e.g., Gemini, Ollama) based on `config/providers.yaml`, and a `ModelRouter` to dynamically select and route requests to the appropriate provider with automatic failover capabilities. The aim is to ensure continuous operation and flexibility in choosing LLM backends.

Tasks:

    [✓] Create config/providers.yaml 
      Defined a configuration file to list available LLM providers like Gemini and Ollama, and their settings like API keys and URLs.

    [✓] Build core/provider_manager.py 
      mplemented a manager to dynamically load, initialize, and provide access to LLM provider instances based on `providers.yaml`.

    [✓] Add core/model_router.py 
      Developed a router to select appropriate LLM providers for a given task, with logic for failover if a preferred provider is unavailable.

    [✓] Connect API to Model Router 
      Integrated the `ModelRouter` into the `/api/v1/process` endpoint, enabling it to route LLM-specific tasks to configured providers.

    [✓] Create test code
      Unit tests for provider management, model routing, failover logic, and API integration. tests/test_api_phase2.py

✅ Milestone: Praximous is now provider-agnostic, capable of dynamically loading and utilizing multiple LLM providers (e.g., Gemini, Ollama) as defined in `config/providers.yaml`. The system exhibits self-healing capabilities through the `ModelRouter`, which automatically attempts failover to alternative providers if a preferred one is unavailable or encounters an error during a request. This ensures greater resilience and flexibility in LLM task processing via the `/api/v1/process` endpoint.

Phase 3: 📊 Auditing & Analytics

Goal: Enable usage tracking, audit logging, and insight generation.

Tasks:

    [✓] Implement Centralized Logging (core/logger.py) (Established a robust, context-aware logging system that writes to both console and `logs/praximous.log`.)

    [✓] Log Each API Interaction (Ensured that all significant events within API endpoints, especially `/api/v1/process`, are logged, including request receipt, routing, skill/LLM execution, success, and errors.)

    [✓] Add /api/v1/analytics Endpoint (Implemented an endpoint to retrieve all logged interactions from the audit database, providing a basic way to view usage data.)

    [✓] Future-Proof for Analytics Dashboard (Enhanced the `/api/v1/analytics` endpoint and underlying audit log queries to support pagination and filtering, providing a robust foundation for a future analytics UI.)

    [✓] Create test code (Implemented unit and integration tests for audit logging and the analytics endpoint, covering log creation, pagination, and filtering. `tests/test_api_phase3.py`)

✅ Milestone: Praximous now has robust auditing capabilities. All API interactions, especially through `/api/v1/process`, are persistently logged to a dedicated SQLite audit database (`logs/praximous_audit.db`). Each log entry includes critical details such as a unique request ID, timestamp, task type, provider used (skill or LLM), status, latency, prompt, and response data. This information is readily accessible via the `/api/v1/analytics` endpoint, which supports pagination and filtering by `task_type`, providing essential enterprise visibility, traceability for every request, and a solid foundation for future analytics dashboards.

Phase 4: 🚀 Deployment & MVP Release

Goal: Containerize the app, finalize docs, and test for reproducible setup.

Tasks:

    [✓] Build Dockerfile (Created a multi-stage Dockerfile using a slim Python base image, established a non-root user for security, installed dependencies, and configured the application to run via `python main.py` on container start.)

    [✓] Write docker-compose.yml (Developed a `docker-compose.yml` to define the Praximous service, manage port mappings, handle environment variables via `.env`, and mount volumes for persistent `logs` and `config` data, ensuring easy local deployment and development.)

    [✓] Finalize .env.template and README.md (Created a template for environment variables and updated the main project documentation with setup and usage instructions.)

    [✓] Perform Full E2E Test (Successfully validated core functionalities including setup, identity, skill execution, LLM integration with failover, and audit logging.)

✅ Milestone: MVP is packaged and deployable in 5 minutes, with a demo Smart Skill working out of the box.

Phase 5: 🎨 Advanced GUI & User Experience

Goal: Develop a rich, intuitive, and responsive graphical user interface (GUI) for Praximous, enhancing user interaction, system administration, and data visualization. This phase aims to move beyond basic API interactions to a full-fledged web application experience.

Tasks:

    [✓] Select Frontend Framework: (Chosen: React)
        Evaluated and chose React for its robust ecosystem, component-based architecture, and suitability for building interactive dashboards and management UIs.

    [✓] Main Application Dashboard:
        Design and implement a central dashboard providing an overview of system status, recent activity, and quick access to key features.
        Included the basic task submission GUI, enhanced it within React, and added displays for system status and recent activity.

    [✓] Interactive Analytics Dashboard:
        Build a dynamic interface to visualize audit logs and analytics data.
        [✓] Include features like date range filtering, charting of usage patterns (e.g., requests per provider, tasks over time), and detailed log inspection.
        (Supersedes "Analytics Dashboard" from Post-MVP)

    [✓] Skill Library Management UI:
        Create an admin interface to view registered Smart Skills, their capabilities, and potentially manage skill configurations (if applicable in the future).
        (Supersedes "Skill Library UI" from Post-MVP)

    [✓] Provider & Routing Configuration UI (Optional - Advanced):
        Consider a UI for viewing (and potentially editing, with appropriate safeguards) `providers.yaml` and `ModelRouter` rules.

    [✓] Test code for interface (Initial tests for SkillLibrary component implemented)
    
✅ Milestone: Praximous features a comprehensive and user-friendly GUI, allowing users to easily submit tasks, monitor system activity, analyze usage patterns, view skill capabilities, and inspect system configurations, significantly improving the overall user experience and administrative efficiency.

Phase 6: 📈 Commercialization & Go-to-Market

Goal: Implement the business logic, licensing system, and online presence required for commercial sales and product-led growth.

Tasks:

    [✓] Expand Core Skill Library:
        Develop and integrate a broader range of sophisticated Smart Skills (e.g., data analysis, advanced text processing, integration with common business tools, RAG components).
        Provide clear documentation and templates for creating new custom skills.

    [>] Tiered Licensing Logic:

        [✓] Implement feature flags in the application code based on the license key's tier field (Pro vs. Enterprise). (Initial mechanism in core/license_manager.py)

        [>] Lock down premium features (RAG Interface, RBAC, PII Redaction) for non-Enterprise keys. (PIIRedactionSkill created and locked down; RAG Interface & RBAC to be locked down when implemented)

    [ ] Cryptographic License Key Generation:

        Develop a secure internal tool or service to generate signed license keys (containing customerName, tier, validityPeriodDays).

    [ ] License Verification & Enforcement Module:

        Build the license.py module within Praximous to handle key validation, first-use activation timestamping, and expiry checks on startup.

        Implement the "Degraded Functionality" mode for expired licenses and the "Hard Stop" for invalid keys.

    [ ] Website: Automated Purchase & Provisioning:

        Integrate a Merchant of Record (e.g., Paddle) for checkout and global tax handling.

        Create a secure backend endpoint (webhook receiver) to automate license key generation and delivery upon successful purchase.

    [ ] Website: The Dojo (Documentation Portal):

        Set up a dedicated documentation site (e.g., using GitBook/Docusaurus).

        Write initial "Quick Start Guide" and tutorials for core features.

    [ ] Website: The Town Hall (Content Hub):

        Launch a blog to post product updates and thought leadership articles.

✅ Milestone: Praximous is a commercially viable product. The website can handle automated sales, license provisioning, and customer self-service, enabling a scalable go-to-market strategy.


Post-MVP Next Steps

    Authentication: Basic token or API key validation  

    Analytics Dashboard: Visualize logs with a simple React/Vue UI  

    Skill Library UI: Admin interface to view/edit registered Smart Skills  

    WebSocket Streaming: Real-time LLM response streaming  

    Enterprise Auth Integration: Support for SSO / LDAP / SAML