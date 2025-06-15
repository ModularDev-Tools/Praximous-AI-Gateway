🧭 Praximous Post-MVP Roadmap
Objective:

Enhance the Praximous MVP with enterprise-grade security, an improved user experience, advanced AI capabilities, and a scalable skill ecosystem to drive commercial adoption and developer engagement.

---

**Phase 7: 🔐 Access Control & Tokens**

**Goal:** Secure the public API endpoints to ensure system integrity and control access, laying the groundwork for a trusted, multi-tenant capable system.

**Tasks:**

    [ ] Implement API token validation middleware
        (Create a FastAPI dependency to check for a valid `X-API-Key` header in all relevant requests)

    [ ] Enhance Environment Configuration
        (Add support for one or more `PRAXIMOUS_API_KEY`s in the `.env` file for the system to load on startup)

    [ ] Create CLI utility for key management
        (Implement `python main.py --generate-api-key` to create new secure tokens for users)

    [ ] Enhance Audit Logging
        (Update the audit logger to capture which API key was used for each request, enabling per-user traceability)

    [ ] Create test code
        Unit tests for token validation, key generation, and protected endpoint access. tests/test_api_phase7.py

🏁 **Milestone:** All public-facing API endpoints are secured via mandatory API key authentication. The system supports key generation, and all API usage is traceable to a specific key in the audit logs, making the platform secure for initial multi-user scenarios.

---

**Phase 8: 📡 WebSocket Streaming & UX Polish**

**Goal:** Improve the real-time user experience for long-running tasks and LLM responses by implementing WebSocket communication for streaming data directly to the GUI.

**Tasks:**

    [ ] Implement WebSocket Endpoint
        (Create a new WebSocket endpoint, e.g., `/ws/v1/process`, in the FastAPI backend)

    [ ] Refactor LLM Calls for Streaming
        (Update the `ProviderManager` and individual LLM provider integrations to support yielding token-by-token responses instead of returning a single block)

    [ ] Update React Frontend
        (Modify the frontend to establish a WebSocket connection and dynamically display streaming responses as they arrive)

    [ ] Improve UI/UX for Loading States
        (Implement better loading indicators and a more responsive UI during task execution)

    [ ] Create test code
        Unit tests for WebSocket connection handling and message streaming. tests/test_api_phase8.py

🏁 **Milestone:** The Praximous GUI provides a modern, real-time user experience. LLM responses are streamed token-by-token to the interface, significantly improving perceived performance and user engagement.

---

**Phase 9: 🔑 RBAC + Enterprise Auth**

**Goal:** Secure the system for multi-user enterprise environments by implementing Role-Based Access Control (RBAC) and integrating with standard enterprise authentication protocols.

**Tasks:**

    [ ] Integrate Authentication Library
        (Incorporate a library like `Authlib` to add support for OIDC/SAML protocols for Single Sign-On - SSO)

    [ ] Implement Role-Based Access Control (RBAC)
        (Create a decorator or dependency in FastAPI to enforce role-based access on specific routes, e.g., only an "Admin" role can access the analytics dashboard)

    [ ] Link Roles to Licensing
        (Ensure that RBAC and advanced authentication features are correctly feature-flagged and only available at the appropriate license tier)

    [ ] Create test code
        Unit tests for SSO login flow, RBAC enforcement on protected routes, and license tier checks. tests/test_api_phase9.py

🏁 **Milestone:** Praximous is ready for secure enterprise deployment. Administrators can integrate it with their existing SSO providers (like Okta or Azure AD) and enforce granular, role-based permissions for different user groups within the application.

---

**Phase 10: 🧠 RAG & Embedding Framework**

**Goal:** Enable powerful, in-house knowledge retrieval and question-answering capabilities by integrating a vector database and building a Retrieval-Augmented Generation (RAG) pipeline.

**Tasks:**

    [ ] Integrate Vector Database Support
        (Update the `ProviderManager` to include support for vector database providers like ChromaDB or Weaviate, manageable via `providers.yaml`)

    [ ] Create Document Ingestion Skill
        (Develop a `DocumentIngestionSkill` that can take a file or text, chunk it, generate embeddings using a configured LLM provider, and store it in the vector database)

    [ ] Create Knowledge Retrieval Skill
        (Build a `KnowledgeRetrievalSkill` that takes a user query, finds relevant context from the vector database, and uses an LLM to generate a synthesized answer based on that context)

    [ ] Create test code
        Unit tests for document ingestion, embedding generation, and the end-to-end RAG question-answering flow. tests/test_api_phase10.py

🏁 **Milestone:** Praximous can function as a powerful, self-contained knowledge agent. Users can load their own documents into the system and ask questions against their private data, with the entire RAG process running securely on-premise.

---

**Phase 11: 🏪 Skill Registry / Plugin Store**

**Goal:** Create a scalable ecosystem for discovering, sharing, and managing Smart Skills, transforming Praximous into an extensible platform.

**Tasks:**

    [ ] Define Skill Metadata Standard
        (Formalize a `skill.yaml` or similar standard within each skill folder, defining its version, author, dependencies, and capabilities)

    [ ] Build Skill Registry GUI
        (Create a new section in the React UI for Browse, searching, and viewing details for all registered skills)

    [ ] Implement Remote Registry Support
        (Backend logic to fetch a central `skills.json` registry from a remote URL, allowing for a curated list of "official" or "verified" skills)

    [ ] Create test code
        Unit tests for skill metadata parsing, registry fetching, and UI rendering of the skill library. tests/test_api_phase11.py

🏁 **Milestone:** Praximous has a thriving skill ecosystem. Users and developers can easily discover available skills, understand their capabilities, and contribute new skills following a clear standard, fostering community engagement and platform growth.

---

**Phase 12: 📊 Audit & Insights Dashboard**

**Goal:** Provide a rich, interactive interface for visualizing system usage and performance metrics, turning raw audit data into actionable business intelligence.

**Tasks:**

    [ ] Develop Interactive Chart Components
        (Build new React components for visualizing key metrics: LLM usage over time, average latency per provider, skill execution frequency, etc.)

    [ ] Implement Advanced Filtering
        (Enhance the analytics UI with robust controls for filtering data by date range, user, provider, and status)

    [ ] Add Data Export Functionality
        (Create a feature to allow users to export the currently filtered analytics view to a CSV or JSON file for external reporting)

    [ ] Create test code
        Unit and E2E tests for the analytics dashboard's filtering, charting, and data export functionalities. tests/test_react_phase12.js

🏁 **Milestone:** Praximous provides a comprehensive analytics dashboard that offers deep insights into AI usage, cost, and performance. Business leaders can use this data to optimize their AI strategy, while administrators can monitor system health and user activity effectively.

---
### Post-MVP Next Steps

-   **Phase 7:** Access Control & Tokens
-   **Phase 8:** WebSocket Streaming & UX Polish
-   **Phase 9:** RBAC + Enterprise Auth
-   **Phase 10:** RAG & Embedding Framework
-   **Phase 11:** Skill Registry / Plugin Store
-   **Phase 12:** Audit & Insights Dashboard

### 🔚 Final Thoughts

You’ve built the backbone of an AI orchestration platform with clear enterprise ambitions. What makes this stand out:

-   **Modular design:** Each piece is swappable or extendable.
-   **Commercial awareness:** Licensing and Merchant of Record integration this early is rare.
-   **Real software rigor:** Testing across phases, CLI utilities, and configuration handling are all enterprise-ready.

### 📌 Summary Timeline

| Phase | Title | Priority | Outcome |
|---|---|---|---|
| 7 | Access Control & Tokens | Critical | Secure external API |
| 8 | WebSocket Streaming | High | Real-time LLM responses |
| 9 | Enterprise Auth + RBAC | High | Secure, multi-user org setup |
| 10 | Embeddings + RAG | Premium | Internal knowledge querying |
| 11 | Smart Skill Store | Strategic | Ecosystem growth and modular installs |
| 12 | Visual Analytics Dashboard | Strategic | Visibility for enterprise monitoring |