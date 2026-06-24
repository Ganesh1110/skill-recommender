---
name: skill-recommender
description: >
  Recommends the most appropriate installed skills by analyzing a user's
  programming language, framework, project architecture, infrastructure,
  uploaded files, configuration files, and intended deliverables.
  Use whenever the user describes a software project, shares repository files,
  pastes config files (package.json, requirements.txt, Dockerfile, Cargo.toml,
  go.mod, pyproject.toml, etc.), or asks which skills should be used.
  Also trigger when a user uploads any file and asks what can be done with it,
  or when they say "I'm building a...", "what skill do I need for...", or
  "help me pick the right skill".
---

# Skill Recommender (Stack-Aware, v3)

Analyzes a user's full tech stack and maps it to installed skills with
confidence scores, weighted ranking, and conflict detection.

**When to use `scripts/detect_stack.py`**: If the user shares a config file
path or uploads a file Claude can run the script on, execute it for deterministic
results. Otherwise follow the manual steps below.

**When to read `references/stack-catalog.md`**: For any framework, tool, or
platform not covered in this file — especially mobile, enterprise Java, Elixir,
edge compute, vector databases, or niche AI tooling.

---

## Step 1 — Collect Evidence

Gather signals from ALL available sources before detecting anything.

| Source                                             | What to extract                 | Weight |
| -------------------------------------------------- | ------------------------------- | ------ |
| Config file (package.json, requirements.txt, etc.) | Exact dependency names          | ★★★★★  |
| Explicit user statement                            | Named languages/frameworks      | ★★★★☆  |
| Code imports / syntax                              | `import`, `require`, type hints | ★★★★☆  |
| File extensions                                    | `.tsx`, `.py`, `.go`, `.rs`     | ★★★☆☆  |
| Vague wording                                      | "something like React"          | ★★☆☆☆  |
| Single ambiguous keyword                           | "frontend"                      | ★☆☆☆☆  |

If a config file is available as an uploaded file or pasted text, parse it
first. Don't ask questions that the config file already answers.

---

## Step 2 — Run Detection Script (when file is available)

If the user has uploaded or pasted a config file, run:

```bash
python scripts/detect_stack.py <file_or_directory> --json
```

The script outputs structured JSON with:

- `signals[]` — detected tech stack with confidence per signal
- `skill_matches[]` — ranked skill recommendations with scores
- `conflicts[]` — contradictory signals with resolution
- `missing_skills[]` — stack needs with no installed skill
- `errors[]` — any parse failures

Parse this JSON and use it as the basis for the output in Steps 6–9.
Skip to Step 6 if running the script.

---

## Step 3 — Parse Config Files Manually (when no script available)

### package.json — scan `dependencies` and `devDependencies`

| Package                                      | Signal               | Category   |
| -------------------------------------------- | -------------------- | ---------- |
| `next`                                       | Next.js              | framework  |
| `react`, `react-dom`                         | React                | framework  |
| `expo`, `react-native`                       | React Native / Expo  | framework  |
| `vue`, `nuxt`                                | Vue / Nuxt           | framework  |
| `@angular/core`                              | Angular              | framework  |
| `svelte`, `@sveltejs/kit`                    | Svelte / SvelteKit   | framework  |
| `vite`                                       | Vite bundler         | build_tool |
| `electron`                                   | Desktop app          | framework  |
| `tailwindcss`                                | Tailwind CSS         | ui         |
| `@mui/material`, `antd`, `@chakra-ui/react`  | UI component library | ui         |
| `shadcn-ui`, `@radix-ui/*`                   | Headless UI          | ui         |
| `prisma`, `drizzle-orm`                      | ORM                  | database   |
| `@supabase/supabase-js`                      | Supabase             | database   |
| `mongoose`, `pg`, `mysql2`                   | Database client      | database   |
| `openai`, `@anthropic-ai/sdk`                | LLM API              | ai         |
| `langchain`, `@langchain/core`               | LangChain            | ai         |
| `llamaindex`                                 | LlamaIndex           | ai         |
| `ai` (Vercel AI SDK)                         | AI SDK               | ai         |
| `jest`, `vitest`, `mocha`                    | Unit testing         | testing    |
| `playwright`, `cypress`                      | E2E testing          | testing    |
| `turbo`, `nx`, `lerna`                       | Monorepo             | build_tool |
| `webpack`, `rollup`, `parcel`, `rspack`      | Bundler              | build_tool |
| `express`, `fastify`, `hono`, `@nestjs/core` | Node.js server       | framework  |
| `graphql`, `@apollo/server`                  | GraphQL              | api        |
| `@trpc/server`                               | tRPC                 | api        |
| `@capacitor/core`, `@ionic/react`            | Mobile hybrid        | framework  |

### requirements.txt / pyproject.toml / setup.py

| Package                                            | Signal           | Category             |
| -------------------------------------------------- | ---------------- | -------------------- |
| `fastapi`, `uvicorn`                               | FastAPI          | framework            |
| `django`                                           | Django           | framework            |
| `flask`                                            | Flask            | framework            |
| `streamlit`, `gradio`                              | ML UI            | framework            |
| `pandas`, `numpy`, `polars`                        | Data science     | data_science         |
| `matplotlib`, `seaborn`, `plotly`                  | Data viz         | data_science         |
| `scikit-learn`, `sklearn`                          | ML               | ml                   |
| `torch`, `tensorflow`, `keras`                     | Deep learning    | ml                   |
| `transformers`                                     | HuggingFace      | ml                   |
| `langchain`, `llama-index`                         | RAG pipeline     | ai                   |
| `anthropic`, `openai`                              | LLM API          | ai                   |
| `crewai`, `autogen`, `langgraph`                   | AI agents        | ai                   |
| `dspy`, `pydantic-ai`                              | Structured AI    | ai                   |
| `dbt-core`, `apache-airflow`, `prefect`, `dagster` | Data pipeline    | data_pipeline        |
| `pytest`                                           | Testing          | testing              |
| `sqlalchemy`, `psycopg2`                           | Database         | database             |
| `python-docx`                                      | Word generation  | deliverable_docx     |
| `reportlab`, `weasyprint`, `fpdf2`                 | PDF generation   | deliverable_pdf      |
| `openpyxl`, `xlsxwriter`                           | Excel generation | deliverable_xlsx     |
| `pymupdf`, `pdfplumber`, `pypdf`                   | PDF reading      | deliverable_pdf_read |

### Dockerfile / docker-compose.yml

| Signal                          | Detected                        | Category     |
| ------------------------------- | ------------------------------- | ------------ |
| `FROM node:*`                   | Node.js                         | language     |
| `FROM python:*`                 | Python                          | language     |
| `FROM golang:*`                 | Go                              | language     |
| `FROM rust:*`                   | Rust                            | language     |
| `FROM openjdk:*`                | Java                            | language     |
| `services:` key                 | Multi-container / microservices | architecture |
| `postgres:`, `mysql:`, `mongo:` | Database in stack               | database     |
| `redis:` image                  | Cache / session store           | database     |
| `nginx:`, `traefik:`            | Reverse proxy                   | infra        |

### Other Config Files → Language Signals

| File present          | Signal               | Confidence |
| --------------------- | -------------------- | ---------- |
| `go.mod`              | Go                   | ★★★★★      |
| `Cargo.toml`          | Rust                 | ★★★★★      |
| `pom.xml`             | Java (Maven)         | ★★★★★      |
| `build.gradle.kts`    | Kotlin               | ★★★★★      |
| `tsconfig.json`       | TypeScript           | ★★★★★      |
| `tailwind.config.*`   | Tailwind CSS         | ★★★★★      |
| `next.config.*`       | Next.js              | ★★★★★      |
| `turbo.json`          | Turborepo monorepo   | ★★★★★      |
| `pnpm-workspace.yaml` | pnpm monorepo        | ★★★★★      |
| `.github/workflows/`  | GitHub Actions CI/CD | ★★★★★      |
| `*.tf` files          | Terraform IaC        | ★★★★★      |
| `fly.toml`            | Fly.io deployment    | ★★★★★      |
| `wrangler.toml`       | Cloudflare Workers   | ★★★★★      |
| `pubspec.yaml`        | Dart / Flutter       | ★★★★★      |
| `Gemfile`             | Ruby                 | ★★★★★      |
| `composer.json`       | PHP                  | ★★★★★      |

> For frameworks not listed here (mobile, enterprise, edge, vector DBs),
> read `references/stack-catalog.md` before proceeding.

---

## Step 4 — Detect Conflicts

Before scoring, check for contradictions:

```
Rule: Config file always overrides user statement.

If user says "I'm using React" but package.json has Vue → flag conflict, use Vue.
If two config files contradict (rare) → flag both, ask ONE question.
```

Conflict output format:

```
⚠️ Conflicting Signal
  User stated:    React
  package.json:   Vue ("vue": "^3.4.0")
  Resolution:     Using config file → Vue
```

---

## Step 5 — Score Each Signal

| Source                  | Stars | Numeric weight |
| ----------------------- | ----- | -------------- |
| Config file dependency  | ★★★★★ | 5              |
| Explicit user statement | ★★★★☆ | 4              |
| Code imports / syntax   | ★★★★☆ | 4              |
| File extension          | ★★★☆☆ | 3              |
| Vague or ambiguous      | ★★☆☆☆ | 2              |
| Single keyword guess    | ★☆☆☆☆ | 1              |

---

## Step 6 — Show Stack Summary Card

Always output this block before any recommendations:

```
🔍 Detected Stack
──────────────────────────────────────────
Language      ★★★★★  TypeScript
Framework     ★★★★★  Next.js 14 + Tailwind
Database      ★★★★★  PostgreSQL (Prisma ORM)
AI / LLM      ★★★★★  Anthropic SDK + LangChain
Testing       ★★★★☆  Vitest + Playwright
Build         ★★★★★  Turborepo (monorepo)
Infra         ★★★★☆  Docker → Vercel
Deliverables  ★★★☆☆  PDF reports

⚠️ Conflicts:  none
❓ Uncertain:  Database host (Neon vs self-hosted?)
Source:       package.json, turbo.json, Dockerfile
──────────────────────────────────────────
```

If something is uncertain with confidence ★★☆☆☆ or below, ask ONE targeted
question before proceeding. Never ask more than one.

---

## Step 7 — Score and Rank Skill Recommendations

Match detected signals against the Installed Skill Registry (Step 8).

**Scoring:**

- Core match (skill directly handles primary stack): +50
- Each additional matching signal (★★★★★ source): +12
- Each additional matching signal (★★★☆☆ source): +8
- Each additional matching signal (★★☆☆☆ source): +4
- All signals are low-confidence only: −20
- Skill handles secondary/optional concern: −10
- Cap at 99

**Priority thresholds:**

- Score ≥ 60 → ✅ Essential
- Score 30–59 → 💡 Helpful
- Score < 30 → 🔧 Optional

Output format (sorted by score, highest first):

```
═══════════════════════════════════════════
  Recommended Skills
═══════════════════════════════════════════

1. frontend-design                Score: 97
   Priority: ✅ Essential
   Confidence: ★★★★★

   Matched signals:
   ✓ React (package.json)
   ✓ Tailwind CSS (tailwind.config.ts)
   ✓ shadcn/ui (@radix-ui/* detected)
   ✓ Next.js (next.config.ts)

   Why: Your React + Tailwind stack maps directly to this skill's design
   tokens, component patterns, and Tailwind layout constraints.

   → Trigger: "Build me a login form" / "Design a dashboard layout"

───────────────────────────────────────────

2. product-self-knowledge         Score: 85
   Priority: ✅ Essential
   Confidence: ★★★★★

   Matched signals:
   ✓ @anthropic-ai/sdk (package.json)
   ✓ LangChain detected

   Why: Project integrates the Anthropic SDK. This skill ensures correct
   model names, rate limits, and API usage patterns.

   → Trigger: Auto-activates when Claude API questions arise

───────────────────────────────────────────

3. pdf                            Score: 42
   Priority: 💡 Helpful
   Confidence: ★★★☆☆

   Matched signals:
   ✓ "generate PDF reports" (user message)

   Why: Relevant if your app exports downloadable PDFs. Skip if output
   is HTML-only or if reporting is done in-browser.

   → Trigger: "Create a PDF report from this data"

═══════════════════════════════════════════
```

---

## Step 8 — Installed Skill Registry

Match signals against this registry. Add new skills here when installed.
Do NOT hardcode recommendations — always match dynamically.

```yaml
skills:
  frontend-design:
    triggers:
      - react, vue, angular, svelte, astro, remix, solid, qwik, htmx
      - next.js, nuxt, sveltekit
      - tailwind, shadcn, radix, material-ui, chakra, ant-design
      - component, ui, dashboard, form, widget, layout, design system
      - html, css, javascript (frontend context)

  docx:
    triggers:
      - report, memo, letter, proposal, word document, .docx
      - python-docx, docx generation, word generation

  pdf:
    triggers:
      - pdf, certificate, fillable form, merge pdf, watermark, pdf export
      - reportlab, weasyprint, fpdf, pdf generation

  pdf-reading:
    triggers:
      - read pdf, extract pdf, parse pdf, uploaded .pdf
      - pymupdf, pdfplumber, pypdf, pdf extraction, ocr

  pptx:
    triggers:
      - slides, deck, presentation, powerpoint, .pptx
      - pptxgenjs, python-pptx, slidev, slide generation

  xlsx:
    triggers:
      - spreadsheet, excel, budget, tracker, .xlsx, .csv
      - financial model, data table, openpyxl, xlsxwriter, sheetjs

  file-reading:
    triggers:
      - uploaded file, read this file, extract from file, parse file
      - what can you do with this file, analyze this document

  product-self-knowledge:
    triggers:
      - anthropic, @anthropic-ai/sdk, claude api, claude sdk
      - openai, langchain, llama-index, ai sdk, vercel ai
      - model name, rate limit, pricing, claude plan, max tokens

  skill-creator:
    triggers:
      - create a skill, edit skill, build skill, new skill
      - eval skill, skill performance, skill.md, .skill file
      - improve this skill, test this skill
```

---

## Step 9 — Flag Missing Skills

If the detected stack implies a need that no installed skill covers:

```
⚠️ No skill installed for: Python data science
   Detected:    pandas, numpy, scikit-learn, matplotlib
   Gap covers:  EDA, charting, statistical summaries, notebook workflows
   → Run skill-creator to build a "data-analysis" skill?

⚠️ No skill installed for: AI agent orchestration
   Detected:    CrewAI, LangGraph
   Gap covers:  Multi-agent design, memory, tool routing
   → Run skill-creator to build an "ai-agents" skill?
```

**Common skill gaps by detected category:**

| Category detected     | Suggested skill name | What it would cover                  |
| --------------------- | -------------------- | ------------------------------------ |
| `data_science`        | `data-analysis`      | EDA, charting, statistical summaries |
| `ml`                  | `ml-engineering`     | Training, evaluation, deployment     |
| `testing`             | `testing`            | Test generation, coverage, fixtures  |
| `ci_cd` / `infra`     | `devops`             | Docker, K8s, CI/CD pipelines         |
| `data_pipeline`       | `data-pipeline`      | dbt, Airflow, Prefect workflows      |
| `mobile` (RN/Flutter) | `mobile`             | Mobile UI, native APIs, app store    |
| `ai` (agents)         | `ai-agents`          | CrewAI, LangGraph, AutoGen           |
| API docs              | `api-docs`           | OpenAPI, Swagger, Postman            |
| `database` (schema)   | `database`           | Schema design, query optimization    |

---

## Step 10 — Closing Next Step

Always end with one concrete, specific action:

```
🚀 Start here:
   "[Exact phrase the user can type]"
   → This triggers [skill-name] immediately.

   Example: "Design a dashboard layout for my Next.js app"
   → Triggers frontend-design.
```

---

## Edge Cases

- **No stack info given**: Ask ONE question — "Can you share your package.json, requirements.txt, or briefly describe your stack?" — before recommending.
- **Monorepo with multiple sub-stacks**: List skills per layer.
  Example: `apps/web` → `frontend-design`; `apps/api` → `product-self-knowledge`; `packages/` → `skill-creator`
- **Pasted code only (no config)**: Infer from imports, type syntax, and naming conventions. Note confidence is ★★★★☆ max.
- **Conflicting signals**: Trust config file over user statement. Flag and explain.
- **All signals are low confidence**: Show the stack card marked ★★☆☆☆ and ask ONE targeted question.
- **No skills match at all**: Be honest. List what was detected, explain the gap, offer to create a custom skill via `skill-creator`.
- **User uploads a file and asks "what can you do?"**: Always recommend `file-reading` as Essential regardless of other signals.
- **Enterprise / niche stack not in this file**: Read `references/stack-catalog.md` before answering.

---

## Running Tests

To verify skill output quality against known test cases:

```bash
python scripts/run_tests.py              # run all 5 built-in test cases
python scripts/run_tests.py --test react_tailwind   # single test
python scripts/run_tests.py --json       # machine-readable output
```

Tests cover: React+Tailwind, Python ML, full-stack AI, document workflow, Docker microservices.
Expected pass rate: 5/5 at average score ≥ 85/100.
