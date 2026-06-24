# Stack Catalog Reference

Extended signal catalog for skill-recommender. Load this file when the user's
stack involves an area not covered in SKILL.md — especially enterprise, mobile,
embedded, or niche frameworks.

---

## Table of Contents

1. [Frontend Frameworks (extended)](#frontend)
2. [Backend Frameworks (extended)](#backend)
3. [Mobile & Cross-Platform](#mobile)
4. [AI / LLM Ecosystem (extended)](#ai)
5. [Data & Analytics Stack](#data)
6. [Cloud Providers (extended)](#cloud)
7. [Database Catalog](#databases)
8. [DevOps & Infra](#devops)
9. [Testing Frameworks](#testing)
10. [Build Tools & Monorepos](#build)
11. [Architecture Patterns](#architecture)
12. [Document & Reporting Tools](#documents)
13. [Deliverable → Skill Map](#deliverables)
14. [Language-Specific Ecosystems](#languages)

---

## 1. Frontend Frameworks (extended) {#frontend}

| Framework / Lib | Signals                                 | Skill             |
| --------------- | --------------------------------------- | ----------------- |
| React           | `react`, `react-dom`, `jsx`, `.tsx`     | `frontend-design` |
| Next.js         | `next`, `next.config.*`, `app/page.tsx` | `frontend-design` |
| Vue 3           | `vue`, `@vue/core`, `.vue` files        | `frontend-design` |
| Nuxt            | `nuxt`, `nuxt.config.*`                 | `frontend-design` |
| Angular         | `@angular/core`, `angular.json`         | `frontend-design` |
| Svelte          | `svelte`, `@sveltejs/kit`               | `frontend-design` |
| Astro           | `astro`, `astro.config.*`               | `frontend-design` |
| Remix           | `@remix-run/react`                      | `frontend-design` |
| Solid.js        | `solid-js`                              | `frontend-design` |
| Qwik            | `@builder.io/qwik`                      | `frontend-design` |
| HTMX            | `htmx.org`                              | `frontend-design` |
| Alpine.js       | `alpinejs`                              | `frontend-design` |

### CSS / Styling

| Tool              | Signal                             | Skill             |
| ----------------- | ---------------------------------- | ----------------- |
| Tailwind CSS      | `tailwindcss`, `tailwind.config.*` | `frontend-design` |
| shadcn/ui         | `shadcn-ui`, `@/components/ui`     | `frontend-design` |
| Radix UI          | `@radix-ui/*`                      | `frontend-design` |
| Material UI       | `@mui/material`                    | `frontend-design` |
| Ant Design        | `antd`                             | `frontend-design` |
| Chakra UI         | `@chakra-ui/react`                 | `frontend-design` |
| styled-components | `styled-components`                | `frontend-design` |
| Emotion           | `@emotion/react`                   | `frontend-design` |
| CSS Modules       | `.module.css`, `.module.scss`      | `frontend-design` |
| UnoCSS            | `unocss`                           | `frontend-design` |

---

## 2. Backend Frameworks (extended) {#backend}

### Node.js / TypeScript

| Framework    | Signal         | Notes                           |
| ------------ | -------------- | ------------------------------- |
| Express      | `express`      | Most common Node server         |
| Fastify      | `fastify`      | High-performance                |
| NestJS       | `@nestjs/core` | Enterprise Angular-like         |
| Hono         | `hono`         | Edge-first                      |
| Elysia       | `elysia`       | Bun-native                      |
| tRPC         | `@trpc/server` | Type-safe RPC                   |
| GraphQL Yoga | `graphql-yoga` | GraphQL server                  |
| Prisma       | `prisma`       | ORM → flag `database` skill gap |
| Drizzle      | `drizzle-orm`  | Lightweight ORM                 |

### Python

| Framework | Signal      | Notes                    |
| --------- | ----------- | ------------------------ |
| FastAPI   | `fastapi`   | Modern async API         |
| Django    | `django`    | Full-stack with ORM      |
| Flask     | `flask`     | Micro-framework          |
| Starlette | `starlette` | Async ASGI               |
| Litestar  | `litestar`  | FastAPI alternative      |
| Sanic     | `sanic`     | Async HTTP               |
| Tornado   | `tornado`   | Long-polling / WebSocket |

### Other Languages

| Framework   | Language | Signal                                    |
| ----------- | -------- | ----------------------------------------- |
| Spring Boot | Java     | `spring-boot`, `pom.xml` with spring deps |
| Quarkus     | Java     | `quarkus`                                 |
| Micronaut   | Java     | `micronaut`                               |
| Ktor        | Kotlin   | `ktor`                                    |
| Rails       | Ruby     | `Gemfile` with `rails`                    |
| Sinatra     | Ruby     | `Gemfile` with `sinatra`                  |
| Laravel     | PHP      | `composer.json` with `laravel/framework`  |
| Gin         | Go       | `go.mod` with `gin-gonic/gin`             |
| Echo        | Go       | `go.mod` with `labstack/echo`             |
| Fiber       | Go       | `go.mod` with `gofiber/fiber`             |
| Actix-web   | Rust     | `Cargo.toml` with `actix-web`             |
| Axum        | Rust     | `Cargo.toml` with `axum`                  |
| Phoenix     | Elixir   | `mix.exs` with `phoenix`                  |

---

## 3. Mobile & Cross-Platform {#mobile}

| Platform             | Signals                              | Skill gap                |
| -------------------- | ------------------------------------ | ------------------------ |
| React Native         | `react-native`, `expo`               | `mobile` (not installed) |
| Expo                 | `expo`, `expo-router`                | `mobile` (not installed) |
| Flutter              | `pubspec.yaml`, `flutter`            | `mobile` (not installed) |
| SwiftUI              | `.swift`, `Package.swift`, `Xcode`   | `mobile` (not installed) |
| UIKit                | `.swift`, UIViewController           | `mobile` (not installed) |
| Jetpack Compose      | `.kt`, `compose`, `build.gradle.kts` | `mobile` (not installed) |
| Kotlin Multiplatform | `KMM`, `commonMain`                  | `mobile` (not installed) |
| Capacitor            | `@capacitor/core`                    | `mobile` (not installed) |
| Ionic                | `@ionic/react`                       | `mobile` (not installed) |

---

## 4. AI / LLM Ecosystem (extended) {#ai}

### API Providers

| Provider    | Signal                                         | Skill                    |
| ----------- | ---------------------------------------------- | ------------------------ |
| Anthropic   | `@anthropic-ai/sdk`, `anthropic` pip           | `product-self-knowledge` |
| OpenAI      | `openai` npm/pip                               | `product-self-knowledge` |
| Google AI   | `@google/generative-ai`, `google-generativeai` | note: Gemini             |
| Mistral     | `@mistralai/mistralai`                         | note: Mistral            |
| Cohere      | `cohere`                                       | note: Cohere             |
| Together AI | `together`                                     | note: Together           |
| Groq        | `groq`                                         | note: Groq               |
| Replicate   | `replicate`                                    | note: Replicate          |

### Orchestration / RAG

| Tool       | Signal                         | Category            |
| ---------- | ------------------------------ | ------------------- |
| LangChain  | `langchain`, `@langchain/core` | RAG / pipelines     |
| LlamaIndex | `llama-index`, `llamaindex`    | RAG / pipelines     |
| Haystack   | `haystack-ai`                  | RAG / pipelines     |
| DSPy       | `dspy`                         | Prompt optimization |
| Instructor | `instructor`                   | Structured outputs  |
| Outlines   | `outlines`                     | Structured outputs  |
| Marvin     | `marvin`                       | AI functions        |

### Agents

| Tool            | Signal            | Category           |
| --------------- | ----------------- | ------------------ |
| CrewAI          | `crewai`          | Multi-agent        |
| AutoGen         | `autogen`         | Multi-agent        |
| LangGraph       | `langgraph`       | Agent graphs       |
| PydanticAI      | `pydantic-ai`     | Typed agents       |
| Semantic Kernel | `semantic-kernel` | Microsoft agents   |
| Swarm           | `openai-swarm`    | Lightweight agents |

### Inference / Hosting

| Tool        | Signal                            | Category             |
| ----------- | --------------------------------- | -------------------- |
| Ollama      | mentions "ollama"                 | Local inference      |
| vLLM        | `vllm`                            | GPU inference        |
| llama.cpp   | mentions "llama.cpp"              | Local inference      |
| HuggingFace | `transformers`, `huggingface-hub` | Model hub            |
| LiteLLM     | `litellm`                         | Multi-provider proxy |

---

## 5. Data & Analytics Stack {#data}

| Tool       | Signal              | Skill gap                       |
| ---------- | ------------------- | ------------------------------- |
| Pandas     | `pandas`            | `data-analysis` (not installed) |
| Polars     | `polars`            | `data-analysis` (not installed) |
| NumPy      | `numpy`             | `data-analysis` (not installed) |
| Matplotlib | `matplotlib`        | `data-analysis` (not installed) |
| Seaborn    | `seaborn`           | `data-analysis` (not installed) |
| Plotly     | `plotly`            | `data-analysis` (not installed) |
| Jupyter    | `jupyter`, `.ipynb` | `data-analysis` (not installed) |
| dbt        | `dbt-core`          | `data-pipeline` (not installed) |
| Airflow    | `apache-airflow`    | `data-pipeline` (not installed) |
| Prefect    | `prefect`           | `data-pipeline` (not installed) |
| Dagster    | `dagster`           | `data-pipeline` (not installed) |
| Spark      | `pyspark`           | `data-pipeline` (not installed) |
| Kafka      | mentions "kafka"    | `data-pipeline` (not installed) |
| Flink      | mentions "flink"    | `data-pipeline` (not installed) |

---

## 6. Cloud Providers (extended) {#cloud}

| Provider     | Signals                                                 | Notes                       |
| ------------ | ------------------------------------------------------- | --------------------------- |
| AWS          | `aws-cdk`, `@aws-sdk/*`, `boto3`, `serverless` with AWS | Lambda, ECS, RDS, S3...     |
| GCP          | `@google-cloud/*`, `firebase-admin`, `google-cloud`     | Cloud Run, BigQuery...      |
| Azure        | `@azure/*`, `azure-*` pip                               | Functions, AKS, CosmosDB... |
| Vercel       | `vercel.json`, `@vercel/*`                              | Edge, Serverless            |
| Netlify      | `netlify.toml`                                          | JAMstack                    |
| Railway      | `railway.json`                                          | Simple PaaS                 |
| Render       | mentions "render.com"                                   | PaaS                        |
| Fly.io       | `fly.toml`                                              | Global VMs                  |
| Cloudflare   | `wrangler.toml`, `@cloudflare/workers-types`            | Workers/Pages               |
| Supabase     | `@supabase/supabase-js`                                 | Postgres + Auth + Storage   |
| Firebase     | `firebase-admin`, `firebase`                            | Google BaaS                 |
| PlanetScale  | mentions "planetscale"                                  | Serverless MySQL            |
| Neon         | `@neondatabase/serverless`                              | Serverless Postgres         |
| Appwrite     | `appwrite`                                              | Open-source BaaS            |
| DigitalOcean | mentions "digitalocean"                                 | VPS / App Platform          |

---

## 7. Database Catalog {#databases}

| Database      | Signals                                    | Type                      |
| ------------- | ------------------------------------------ | ------------------------- |
| PostgreSQL    | `pg`, `psycopg2`, `postgres:` in compose   | Relational                |
| MySQL         | `mysql2`, `mysql:` in compose              | Relational                |
| SQLite        | `better-sqlite3`, `sqlite3`                | Embedded                  |
| MongoDB       | `mongoose`, `mongodb`, `mongo:` in compose | Document                  |
| Redis         | `ioredis`, `redis`, `redis:` in compose    | Cache / KV                |
| DynamoDB      | `@aws-sdk/client-dynamodb`                 | AWS NoSQL                 |
| Cassandra     | `cassandra-driver`                         | Wide-column               |
| ClickHouse    | `@clickhouse/client`                       | Analytics                 |
| Elasticsearch | `@elastic/elasticsearch`                   | Search                    |
| Pinecone      | `@pinecone-database/pinecone`              | Vector DB                 |
| Weaviate      | `weaviate-client`                          | Vector DB                 |
| Qdrant        | `@qdrant/js-client-rest`                   | Vector DB                 |
| Chroma        | `chromadb`                                 | Vector DB                 |
| PGVector      | `pgvector`                                 | Postgres vector extension |

---

## 8. DevOps & Infra {#devops}

| Tool           | Signal                              | Skill gap |
| -------------- | ----------------------------------- | --------- |
| Docker         | `Dockerfile`, `docker-compose.*`    | `devops`  |
| Kubernetes     | `k8s/`, `helm/`, `kind: Deployment` | `devops`  |
| Helm           | `Chart.yaml`, `values.yaml`         | `devops`  |
| Terraform      | `*.tf`, `terraform/`                | `devops`  |
| Pulumi         | `Pulumi.yaml`                       | `devops`  |
| AWS CDK        | `aws-cdk-lib`                       | `devops`  |
| GitHub Actions | `.github/workflows/*.yml`           | `devops`  |
| CircleCI       | `.circleci/config.yml`              | `devops`  |
| Jenkins        | `Jenkinsfile`                       | `devops`  |
| ArgoCD         | `argocd` in YAML                    | `devops`  |
| Nginx          | `nginx:` in compose, `nginx.conf`   | `devops`  |
| Traefik        | `traefik:` in compose               | `devops`  |

---

## 9. Testing Frameworks {#testing}

| Tool            | Language     | Type        | Skill gap |
| --------------- | ------------ | ----------- | --------- |
| Jest            | JS/TS        | Unit        | `testing` |
| Vitest          | JS/TS        | Unit        | `testing` |
| Mocha           | JS           | Unit        | `testing` |
| AVA             | JS           | Unit        | `testing` |
| Playwright      | JS/TS        | E2E         | `testing` |
| Cypress         | JS/TS        | E2E         | `testing` |
| Testing Library | JS/TS        | Integration | `testing` |
| Storybook       | JS/TS        | Component   | `testing` |
| pytest          | Python       | Unit        | `testing` |
| unittest        | Python       | Unit        | `testing` |
| RSpec           | Ruby         | Unit        | `testing` |
| JUnit           | Java         | Unit        | `testing` |
| Go test         | Go           | Unit        | `testing` |
| Detox           | React Native | Mobile E2E  | `testing` |

---

## 10. Build Tools & Monorepos {#build}

| Tool            | Signal                        | Type              |
| --------------- | ----------------------------- | ----------------- |
| Vite            | `vite`, `vite.config.*`       | Bundler           |
| Webpack         | `webpack`, `webpack.config.*` | Bundler           |
| Rollup          | `rollup`, `rollup.config.*`   | Bundler           |
| Parcel          | `parcel`                      | Bundler           |
| Rspack          | `rspack`                      | Bundler (Rust)    |
| esbuild         | `esbuild`                     | Bundler           |
| Turborepo       | `turbo.json`, `turbo`         | Monorepo          |
| Nx              | `nx.json`, `project.json`     | Monorepo          |
| Rush            | `rush.json`                   | Monorepo          |
| Lerna           | `lerna.json`                  | Monorepo          |
| pnpm workspaces | `pnpm-workspace.yaml`         | Monorepo          |
| Bazel           | `WORKSPACE`, `BUILD`          | Build system      |
| Bun             | `bun.lockb`, `bunfig.toml`    | Runtime + bundler |

---

## 11. Architecture Patterns {#architecture}

| Signal                                     | Pattern          | Notes                     |
| ------------------------------------------ | ---------------- | ------------------------- |
| `services:` in compose, multiple repos     | Microservices    | Flag devops skill         |
| Turborepo / Nx / pnpm workspaces           | Monorepo         | Multiple apps in one repo |
| Redux, Zustand, Jotai, MobX                | State management | Complex client state      |
| CQRS, event-sourcing mentioned             | Event-driven     | Enterprise pattern        |
| Clean Architecture, DDD mentioned          | Domain-driven    | Structured layers         |
| BFF (Backend for Frontend) mentioned       | BFF pattern      | API gateway layer         |
| Event bus, message queue (Kafka, RabbitMQ) | Event-driven     | `devops` skill gap        |
| GraphQL federation                         | Federated APIs   | Distributed schema        |
| gRPC, protobuf                             | RPC              | `api-docs` skill gap      |

---

## 12. Document & Reporting Tools {#documents}

| Signal                                      | Deliverable      | Skill                    |
| ------------------------------------------- | ---------------- | ------------------------ |
| "report", "memo", "letter", "proposal"      | Word document    | `docx`                   |
| `python-docx`, `docx`                       | Word generation  | `docx`                   |
| "slides", "deck", "presentation"            | PowerPoint       | `pptx`                   |
| `pptxgenjs`, `python-pptx`                  | Slide generation | `pptx`                   |
| "spreadsheet", "budget", "tracker", "model" | Excel            | `xlsx`                   |
| `openpyxl`, `xlsxwriter`, `SheetJS`         | Excel generation | `xlsx`                   |
| "PDF", "certificate", "form"                | PDF creation     | `pdf`                    |
| `reportlab`, `weasyprint`, `fpdf2`          | PDF generation   | `pdf`                    |
| `pymupdf`, `pdfplumber`, `pypdf`            | PDF extraction   | `pdf-reading`            |
| Uploaded `.pdf`, `.docx`, `.xlsx`, `.pptx`  | File reading     | `file-reading`           |
| "API docs", "Swagger", "OpenAPI"            | API docs         | `api-docs` (gap)         |
| "README", "ADR", "PRD", "RFC"               | Markdown docs    | inline (no skill needed) |

---

## 13. Deliverable → Skill Map {#deliverables}

Quick reference for matching project output to installed skills:

```
Output type              → Skill              Priority
─────────────────────────────────────────────────────
Word document (.docx)    → docx               Essential
PDF creation             → pdf                Essential
PDF reading/extract      → pdf-reading        Essential
Excel spreadsheet        → xlsx               Essential
PowerPoint slides        → pptx               Essential
Any uploaded file        → file-reading       Essential
React/Vue/HTML UI        → frontend-design    Essential
Anthropic/Claude API     → product-self-knowledge Essential
New or modified skill    → skill-creator      Essential
Python ML / data         → data-analysis      GAP ⚠️
DevOps / containers      → devops             GAP ⚠️
Mobile app               → mobile             GAP ⚠️
AI agent workflows       → ai-agents          GAP ⚠️
API documentation        → api-docs           GAP ⚠️
Test generation          → testing            GAP ⚠️
Database schema/queries  → database           GAP ⚠️
```

---

## 14. Language-Specific Ecosystems {#languages}

### TypeScript

- `tsconfig.json` → TypeScript confirmed (★★★★★)
- `tsc`, `ts-node`, `tsx` → TypeScript toolchain
- `.d.ts` files → TypeScript declarations
- Strict mode in tsconfig → typed project

### Python

- `pyproject.toml` with `[tool.poetry]` → Poetry project
- `Pipfile` → Pipenv project
- `setup.py` → legacy package
- `.py` extension + `if __name__ == "__main__"` → script-style

### Go

- `go.mod` + `go.sum` → Go modules (★★★★★)
- `cmd/`, `pkg/`, `internal/` dirs → idiomatic Go structure

### Rust

- `Cargo.toml` + `Cargo.lock` → Rust project (★★★★★)
- `src/main.rs` → binary crate
- `src/lib.rs` → library crate

### Java / Kotlin

- `pom.xml` → Maven (Java)
- `build.gradle` → Gradle (Java or Kotlin)
- `build.gradle.kts` → Kotlin DSL (Kotlin confirmed)
- `src/main/kotlin/` → Kotlin confirmed

### Ruby

- `Gemfile` → Ruby project (★★★★★)
- `config/routes.rb` → Rails confirmed

### PHP

- `composer.json` → PHP project (★★★★★)
- `artisan` → Laravel confirmed
