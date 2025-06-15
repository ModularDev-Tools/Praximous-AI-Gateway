# 🧭 Praximous "Dojo" Website Roadmap

**Objective**:  
Overhaul the Docusaurus website to replace all placeholder content with custom branding, compelling marketing copy, and comprehensive documentation, establishing a professional and trustworthy hub for users and developers.

---

## Phase 1: 🎨 Branding & Core Identity

**Goal**: Erase the default Docusaurus look-and-feel and replace it with a strong Praximous brand identity.

### Tasks:

- [ ] **Update Site Metadata (`docusaurus.config.js`)**  
  - [ ] Change title to `"Praximous | Secure AI Gateway"`
  - [ ] Update tagline: `"Your On-Premise Orchestration Layer for Enterprise AI."`
  - [ ] Set `navbar.title` to `"Praximous"`
  - [ ] Update copyright:
    ```js
    Copyright © ${new Date().getFullYear()} Praximous. All rights reserved.
    ```

- [ ] **Create & Integrate Logo**  
  - [ ] Design a professional Praximous logo  
  - [ ] Replace `static/img/logo.svg`  
  - [ ] Generate and use new `static/img/favicon.ico`

- [ ] **Define & Implement Color Scheme**  
  - [ ] Choose a primary and secondary color palette  
  - [ ] Update CSS variables (`src/css/custom.css`):
    ```css
    --ifm-color-primary: ...;
    --ifm-color-primary-dark: ...;
    ```

- [ ] **Create Social Media Card**  
  - [ ] Design a 1200x630px image with logo and tagline  
  - [ ] Replace `static/img/docusaurus-social-card.jpg`

**🏁 Milestone**:  
The website consistently reflects the Praximous brand, with custom logo, color scheme, and accurate metadata, presenting a professional and cohesive identity.

---

## Phase 2: 📢 Homepage & Content Overhaul

**Goal**: Transform the homepage into a compelling landing page that communicates the value proposition of Praximous.

### Tasks:

- [ ] **Rewrite Homepage Hero (`src/pages/index.js`)**  
  - [ ] Update `<HomepageHeader>` with new title & tagline  
  - [ ] Change CTA link text to `"Get Started in 5 Minutes"`  
  - [ ] Update `to` prop to `"/docs/quick-start"`

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

- [ ] **Restructure Documentation**  
  - [ ] Delete: `docs/tutorial-basics`, `docs/tutorial-extras`
  - [ ] Create:
    ```
    docs/
      getting-started/
      core-concepts/
      guides/
      api-reference/
    ```
  - [ ] Move:
    - `docs/intro.md` → `docs/getting-started/introduction.md`
    - `docs/quick-start.md` → `docs/getting-started/quick-start.md`

- [ ] **Define Logical Sidebar (`sidebars.js`)**  
  - [ ] Replace auto-generated sidebar with manual hierarchy

- [ ] **Expand Core Guides**
  - [ ] Revise `quick-start.md` into standalone guide  
  - [ ] Write `core-concepts/architecture.md`  
  - [ ] Write `guides/configuration.md` (covering `identity.yaml`, `providers.yaml`, `.env`)  
  - [ ] Write `guides/licensing.md`  
  - [ ] Write `guides/skill-development.md` (based on `SKILL_DEVELOPMENT_GUIDE.md`)

- [ ] **Create API Reference**
  - [ ] Write `api-reference/process-endpoint.md`
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
