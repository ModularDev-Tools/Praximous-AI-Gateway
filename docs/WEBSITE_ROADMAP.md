# 🧭 Praximous "Dojo" Website Roadmap

**Objective**:  
Overhaul the Docusaurus website to replace all placeholder content with custom branding, compelling marketing copy, and comprehensive documentation, establishing a professional and trustworthy hub for users and developers.

---

## Phase 1: 🎨 Branding & Core Identity

**Goal**: Erase the default Docusaurus look-and-feel and replace it with a strong Praximous brand identity.

### Tasks:

- [x] **Update Site Metadata (`docusaurus.config.js`)**  
  - [x] Change title to `"Praximous | Secure AI Gateway"`
  - [x] Update tagline: `"Your On-Premise Orchestration Layer for Enterprise AI."`
  - [x] Set `navbar.title` to `"Praximous"`
  - [x] Update copyright:
    ```js
    Copyright © ${new Date().getFullYear()} Praximous. All rights reserved.
    ```

- [x] **Create & Integrate Logo**  
  - [x] Design a professional Praximous logo  
  - [x] Replace `static/img/logo.svg` *(Config updated, asset placed & correctly named)*
  - [x] Generate and use new `static/img/favicon.ico` *(Config updated, asset placed)*


- [/] **Define & Implement Color Scheme**  
  - [x] Choose a primary and secondary color palette  
  - [/] Update CSS variables (`src/css/custom.css`): *(Initial implementation done, dark mode [x] & fine-tuning pending)*
    ```css
    --ifm-color-primary: #002147; /* Midnight Blue */
    --ifm-color-primary-dark: #001b3a; /* Darker shade of Midnight Blue */

    ```

- [x] **Create Social Media Card**  
  - [x] Design a 1200x630px image with logo and tagline  
  - [x] Replace `static/img/docusaurus-social-card.jpg` *(Config updated, asset pending)*

**🏁 Milestone**:  
The website consistently reflects the Praximous brand, with custom logo, color scheme, and accurate metadata, presenting a professional and cohesive identity. *(Partially achieved)*

---

## Phase 2: 📢 Homepage & Content Overhaul

**Goal**: Transform the homepage into a compelling landing page that communicates the value proposition of Praximous.

### Tasks:

- [ ] **Rewrite Homepage Hero (`src/pages/index.js`)**  
  - [ ] Update `<HomepageHeader>` with new title & tagline  
  - [ ] Change CTA link text to `"Get Started in 5 Minutes"`  
  - [ ] Update `to` prop to `"/docs/getting-started/quick-start"` *(Path updated due to doc restructure)*

- [ ] **Customize Homepage Features (`src/components/HomepageFeatures/index.js`)**  
  - [ ] Replace default features with:

    ```js
    {
      title: "Secure On-Premise Gateway",
      description: "Keep your data in your environment. Praximous acts as a central, secure orchestration layer, preventing sensitive information from being exposed to third-party services."
    },
    {
      title: "Resilient & Agnostic",
      description: "Never depend on a single AI provider. With dynamic failover and a pluggable architecture, Praximous ensures your applications remain operational and flexible."
    },
    {
      title: "Extensible Smart Skills",
      description: "Go beyond simple LLM calls. Build modular, reusable logic units—Smart Skills—to automate complex business processes and create powerful, context-aware workflows."
    }
    ```

- [ ] **Replace Placeholder Graphics**  
  - [ ] Design or source new SVGs:
    - Shield for Security
    - Network for Resilience
    - Puzzle/gears for Extensibility  
  - [ ] Replace `undraw_*` SVGs in `HomepageFeatures`

**🏁 Milestone**:  
The homepage effectively educates visitors on what Praximous is, its key benefits, and how to get started.

---

## Phase 3: 📚 Comprehensive Documentation

**Goal**: Structure and write clear, useful docs for installing, configuring, and extending Praximous.

### Tasks:

- [x] **Restructure Documentation**  
  - [/] Delete: `docs/tutorial-basics`, `docs/tutorial-extras` *(Pending user action, but placeholders for new structure created)*
  - [x] Create: *(Placeholder files created)*
    ```

    docs/
      getting-started/
      core-concepts/
      guides/
      api-reference/
    ```
  - [/] Move: *(In progress)*
    - [x] `docs/intro.md` → `docs/getting-started/introduction.md`
    - [/] `docs/quick-start.md` → `docs/getting-started/quick-start.md` *(Pending user action)*


- [x] **Define Logical Sidebar (`sidebars.js`)**  
  - [x] Replace auto-generated sidebar with manual hierarchy


- [/] **Expand Core Guides** *(Placeholders created, content pending)*
  - [x] Write `core-concepts/architecture.md` *(Placeholder exists)*
  - [x] Write `guides/configuration.md` (covering `identity.yaml`, `providers.yaml`, `.env`) *(Placeholder created)*
  - [x] Write `guides/licensing.md` *(Placeholder created)*
  - [x] Write `guides/skill-development.md` (based on `SKILL_DEVELOPMENT_GUIDE.md`) *(Placeholder with initial content created)*


- [/] **Create API Reference** *(Placeholder created, content pending)*
  - [x] Write `api-reference/process-endpoint.md` *(Placeholder created)*
    - Document `/api/v1/process` endpoint
    - Include:
      - Purpose
      - Request schema
      - Response schema
      - Task type examples

**🏁 Milestone**:  
Documentation is clear, structured, and practical—accelerating onboarding and deep adoption.

---

## Phase 4: ✍️ Content & Community Engagement

**Goal**: Use the blog and community links to share updates, attract contributors, and build trust.

### Tasks:

- [ ] **Write New Blog Posts**
  - [ ] ✅ 2–3 long-form posts:
    - 🧠 *A Deep Dive into Praximous’s Failover Architecture*
    - 🛠️ *Building a Custom Smart Skill: A Step-by-Step Tutorial*
    - 💼 *The Hidden Costs of Cloud AI: Why On-Premise Gateways are the Future for Enterprise*

- [ ] **Update Community Links**
  - [ ] Update navbar/footer links to:
    - GitHub Discussions or
    - Discord community
  - [ ] Remove default Docusaurus links

**🏁 Milestone**:  
The site becomes an active knowledge and engagement hub, fostering community around Praximous.

---
