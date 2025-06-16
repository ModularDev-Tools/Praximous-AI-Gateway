🧭 Praximous Post-MVP Roadmap
Objective:

Refine the Praximous MVP into a polished, secure, and highly usable 'Standard' (free) tier to drive widespread adoption, while strategically layering features for Team, Pro, and Enterprise tiers. This involves enhancing user experience, implementing foundational security and tiering, and preparing for advanced AI capabilities and a scalable skill ecosystem to support both freemium growth and commercial success.

---

**Alignment with Business Model:**

This roadmap is structured to prioritize the development of a robust and feature-rich "Standard" (free) tier as outlined in the Praximous Business Plan. Subsequent phases will build upon this foundation to deliver features for the Team, Pro, and Enterprise tiers, enabling a clear upgrade path and supporting our product-led growth strategy.
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

**Freemium Consideration:** Secure API access is fundamental for all tiers, including the free Standard tier, to ensure system integrity and enable basic usage tracking. API keys can form the initial basis for distinguishing usage patterns and preparing for tier-specific limits.


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

**Freemium Consideration:** A polished user experience with real-time feedback is crucial for the adoption of the Standard (free) tier. WebSocket streaming directly contributes to this goal.


🏁 **Milestone:** The Praximous GUI provides a modern, real-time user experience. LLM responses are streamed token-by-token to the interface, significantly improving perceived performance and user engagement.

---

**Phase 9: 🔑 RBAC + Enterprise Auth**

**Goal:** Secure the system for multi-user enterprise environments by implementing Role-Based Access Control (RBAC) and integrating with standard enterprise authentication protocols.
**Goal:** Implement foundational mechanisms for feature tiering (supporting the 'Standard' free tier limitations) and prepare for advanced multi-user enterprise environments with Role-Based Access Control (RBAC) and standard enterprise authentication protocols for paid tiers.

**Tasks:**

    [ ] Integrate Authentication Library
        (Plan for future integration of a library like `Authlib` to add OIDC/SAML for SSO in Pro/Enterprise tiers)

    [ ] Implement Role-Based Access Control (RBAC)
        (Design basic feature flagging/tiering mechanism, e.g., based on API key properties. Defer full RBAC decorator/dependency for paid tiers)

    [ ] Implement basic user/API key tracking to support limitations for the Standard tier (e.g., the 5-user guideline, 1 external LLM provider).

    [ ] Link Roles to Licensing
        (Implement initial feature flagging for the 'Standard' tier. Ensure core features are enabled and limitations can be enforced. Advanced features will be linked to Pro/Enterprise licenses)

    [ ] Create test code
        Unit tests for basic tier feature flagging, user limit considerations, and planned SSO/RBAC (as applicable per tier). tests/test_api_phase9.py

**Freemium Consideration:** The immediate focus is on enabling the 'Standard' free tier with its defined limitations (e.g., user count, provider limits). Full enterprise authentication (SSO) and granular RBAC are features for higher-paid tiers (Pro/Enterprise).

🏁 **Milestone:** Praximous includes foundational support for feature differentiation by tier. The system can enforce limitations for the free 'Standard' tier. Advanced authentication (SSO) and RBAC are designed and planned for enterprise versions, ensuring a clear upgrade path.

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

**Freemium Consideration:** RAG and advanced embedding functionalities are premium features targeted for the Pro and Enterprise tiers, not the initial polished Standard (free) tier.

🏁 **Milestone:** Praximous can function as a powerful, self-contained knowledge agent (Pro/Enterprise Tiers). Users can load their own documents into the system and ask questions against their private data, with the entire RAG process running securely on-premise.

---

**Phase 11: 🏪 Skill Registry / Plugin Store**

**Goal:** Create a scalable ecosystem for discovering, sharing, and managing Smart Skills, transforming Praximous into an extensible platform.

**Goal:** Create a foundational ecosystem for discovering and managing Smart Skills to enhance the 'Standard' (free) tier, and pave the way for a scalable, community-driven platform with a richer Skill Registry for all tiers.

**Tasks:**

    [ ] Define Skill Metadata Standard
        (Formalize a `skill.yaml` or similar standard within each skill folder, defining its version, author, dependencies, and capabilities)

    [ ] Build Skill Registry GUI
        (Create a basic local Skill Registry GUI in the React UI for the Standard tier to view and manage locally available/developed skills)

    [ ] Implement Remote Registry Support
        (Plan for Remote Registry Support for curated/verified skills, potentially for Team+ tiers or as a platform growth feature)

    [ ] Create test code
        Unit tests for skill metadata parsing, registry fetching, and UI rendering of the skill library. tests/test_api_phase11.py

**Freemium Consideration:** A well-defined skill metadata standard and basic local skill management are essential for the "Full Smart Skill development framework" offered in the Standard (free) tier. A full-fledged remote skill store is a longer-term strategic goal.

🏁 **Milestone:** Praximous Standard tier users can easily manage and understand their local Smart Skills via a metadata standard and a basic GUI. The groundwork is laid for a future, more extensive skill ecosystem, including a remote registry.

---

**Phase 12: 📊 Audit & Insights Dashboard**

**Goal:** Provide a rich, interactive interface for visualizing system usage and performance metrics, turning raw audit data into actionable business intelligence.

**Goal:** Provide a basic analytics dashboard for the 'Standard' (free) tier (with 30-day data retention), and plan for a rich, interactive interface for visualizing system usage and performance metrics in premium tiers.

**Tasks:**

    [ ] Develop Interactive Chart Components
        (Build basic React chart components for the Standard tier dashboard: e.g., API usage counts, LLM calls, within a 30-day data view)

    [ ] Ensure audit data retention is configurable, defaulting to 30 days for the Standard tier (and 90 days for Team, etc., as per business plan).

    [ ] Implement Advanced Filtering
        (Implement basic filtering for the Standard tier dashboard, e.g., by date within the 30-day window. Defer advanced filtering for premium tiers)

    [ ] Add Data Export Functionality
        (Defer Data Export Functionality; consider for Pro/Enterprise tiers)

    [ ] Create test code
        Unit and E2E tests for the analytics dashboard's filtering, charting, and data export functionalities. tests/test_react_phase12.js

**Freemium Consideration:** The Standard (free) tier includes a "Basic analytics dashboard with a 30-day data retention limit." Advanced analytics, longer retention, and export are features for paid tiers.

🏁 **Milestone:** Praximous Standard tier provides a basic analytics dashboard offering insights into API usage with 30-day data retention. Advanced analytics capabilities and data export are planned for premium tiers, enabling deeper business intelligence.

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
| 8 | WebSocket Streaming & UX Polish | High | Real-time LLM responses & polished UX (Essential for Free) |
| 9 | Enterprise Auth + RBAC | High | Foundational tiering & user limits (Free); Full Ent. Auth/RBAC (Paid) |
| 10 | Embeddings + RAG | Premium | Internal knowledge querying (Premium/Paid Feature) |
| 11 | Smart Skill Store | Strategic | Basic local skill mgmt (Free); Full Skill Store & ecosystem (Paid) |
| 12 | Visual Analytics Dashboard | Strategic | Basic analytics dashboard (Free); Advanced visual analytics (Paid) |