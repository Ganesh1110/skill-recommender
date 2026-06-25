#!/usr/bin/env python3
"""
detect_stack.py — Deterministic tech stack detector for skill-recommender.

Usage:
  python detect_stack.py <file_or_dir>
  python detect_stack.py package.json
  python detect_stack.py ./my-project/
  cat package.json | python detect_stack.py --stdin

Output: JSON with detected signals, confidence scores, conflicts, and skill matches.
"""

import sys
import json
import re
import os
from pathlib import Path

# ── Skill registry ────────────────────────────────────────────────────────────
SKILL_REGISTRY = {
    "frontend-design": {
        "triggers": ["react", "vue", "angular", "svelte", "astro", "solid", "qwik",
                     "html", "css", "tailwind", "component", "ui", "dashboard",
                     "form", "widget", "next.js", "nuxt", "sveltekit", "shadcn",
                     "radix", "chakra", "material-ui", "bootstrap", "emotion",
                     "styled-components", "vite", "webpack", "astro.config", "remix"],
        "description": "UI/UX design tokens, component patterns, Tailwind, React/Vue"
    },
    "backend-frameworks": {
        "triggers": ["express", "fastify", "hono", "nestjs", "apollo", "trpc",
                     "spring", "spring boot", "django", "flask", "fastapi", "starlette",
                     "gin", "fiber", "actix", "rocket", "phoenix", "laravel"],
        "description": "Backend framework and API service patterns"
    },
    "database": {
        "triggers": ["postgres", "mysql", "mongodb", "redis", "sqlite", "dynamodb",
                     "elastic", "cassandra", "clickhouse", "pinecone", "qdrant",
                     "weaviate", "chromadb", "pgvector", "prisma", "sqlalchemy", "mongoose"],
        "description": "Database access, schema design, and persistence"
    },
    "data-analysis": {
        "triggers": ["pandas", "numpy", "polars", "matplotlib", "seaborn", "plotly",
                     "jupyter", "notebook", "dataframe", "visualization", "eda"],
        "description": "Data analysis, visualization, and exploratory workflows"
    },
    "ml-engineering": {
        "triggers": ["scikit-learn", "torch", "tensorflow", "keras", "xgboost",
                     "catboost", "lightgbm", "transformers", "huggingface", "training",
                     "model", "inference"],
        "description": "Machine learning model training, evaluation, and deployment"
    },
    "testing": {
        "triggers": ["jest", "vitest", "mocha", "playwright", "cypress", "pytest",
                     "unittest", "junit", "rspec", "go test", "test coverage",
                     "testing library", "selenium", "storybook"],
        "description": "Automated testing, coverage, and test strategy"
    },
    "devops": {
        "triggers": ["docker", "docker-compose", "kubernetes", "helm", "terraform",
                     "pulumi", "github actions", "circleci", "jenkins", "argocd",
                     "aws cdk", "cloudformation", "ci/cd", "deployment"],
        "description": "Infrastructure, deployment automation, and CI/CD"
    },
    "mobile": {
        "triggers": ["react native", "expo", "flutter", "swiftui", "jetpack compose",
                     "kotlin multiplatform", "capacitor", "ionic", "xcode", "apk", "ipa"],
        "description": "Mobile and cross-platform app development"
    },
    "api-docs": {
        "triggers": ["swagger", "openapi", "api docs", "postman", "raml", "graphql schema",
                     "asyncapi", "api documentation"],
        "description": "API documentation, spec generation, and contract design"
    },
    "ai-agents": {
        "triggers": ["autogen", "crewai", "langgraph", "pydantic-ai", "semantic kernel",
                     "agents", "agent", "orchestration", "workflow"],
        "description": "AI agent orchestration and multi-agent workflows"
    },
    "docx": {
        "triggers": ["report", "memo", "letter", "proposal", "word", ".docx", "document",
                     "word document", "ms word", "python-docx", "deliverable_docx",
                     "word generation", "docx generation"],
        "description": "Create/edit Word documents (.docx)"
    },
    "pdf": {
        "triggers": ["pdf", "certificate", "fillable form", "merge pdf", "watermark",
                     "reportlab", "weasyprint", "fpdf", "pdfkit", "deliverable_pdf",
                     "pdf generation", "pdf export"],
        "description": "Create, merge, fill, or watermark PDFs"
    },
    "pdf-reading": {
        "triggers": ["read pdf", "extract pdf", "parse pdf", "pymupdf", "pdfplumber",
                     "pypdf", "pdf2text", "ocr", "deliverable_pdf_read",
                     "pdf extraction"],
        "description": "Extract text/tables/images from existing PDFs"
    },
    "pptx": {
        "triggers": ["slides", "deck", "presentation", "powerpoint", ".pptx",
                     "pptxgenjs", "python-pptx", "slidev", "deliverable_pptx",
                     "presentation generation"],
        "description": "Build or edit PowerPoint presentations"
    },
    "xlsx": {
        "triggers": ["spreadsheet", "excel", "budget", "tracker", ".xlsx", ".csv",
                     "financial model", "openpyxl", "xlsxwriter", "sheetjs", "papaparse",
                     "deliverable_xlsx", "excel generation"],
        "description": "Spreadsheets, financial models, data tables"
    },
    "file-reading": {
        "triggers": ["uploaded file", "read this file", "extract from file", "parse file",
                     "file upload", "multipart"],
        "description": "Route-aware reader for any uploaded file type"
    },
    "product-self-knowledge": {
        "triggers": ["anthropic", "claude api", "@anthropic-ai/sdk", "claude sdk",
                     "model name", "rate limit", "pricing", "claude plan", "openai",
                     "langchain", "llama-index", "llamaindex", "ai sdk"],
        "description": "Accurate Claude/Anthropic API details, model names, pricing"
    },
    "skill-creator": {
        "triggers": ["create a skill", "edit skill", "build skill", "eval skill",
                     "skill performance", "skill.md", ".skill"],
        "description": "Create, test, iterate, and package skills"
    }
}

# ── Package → signal maps ─────────────────────────────────────────────────────
NPM_MAP = {
    # Frameworks
    "next": ("Next.js", "framework", 5),
    "react": ("React", "framework", 5),
    "react-dom": ("React", "framework", 5),
    "expo": ("Expo / React Native", "framework", 5),
    "react-native": ("React Native", "framework", 5),
    "vue": ("Vue", "framework", 5),
    "nuxt": ("Nuxt", "framework", 5),
    "@angular/core": ("Angular", "framework", 5),
    "svelte": ("Svelte", "framework", 5),
    "@sveltejs/kit": ("SvelteKit", "framework", 5),
    "vite": ("Vite", "build_tool", 5),
    "electron": ("Electron (desktop)", "framework", 5),
    # UI
    "tailwindcss": ("Tailwind CSS", "ui", 5),
    "shadcn-ui": ("shadcn/ui", "ui", 5),
    "@radix-ui/react-dialog": ("Radix UI", "ui", 5),
    "@mui/material": ("Material UI", "ui", 5),
    "bootstrap": ("Bootstrap", "ui", 4),
    "@emotion/react": ("Emotion CSS-in-JS", "ui", 4),
    "styled-components": ("Styled Components", "ui", 4),
    # Backend / API
    "express": ("Express.js", "framework", 5),
    "fastify": ("Fastify", "framework", 5),
    "hono": ("Hono", "framework", 5),
    "@nestjs/core": ("NestJS", "framework", 5),
    "graphql": ("GraphQL", "api", 5),
    "@apollo/server": ("Apollo GraphQL", "api", 5),
    "@trpc/server": ("tRPC", "api", 5),
    # Database / ORM
    "prisma": ("Prisma ORM", "database", 5),
    "drizzle-orm": ("Drizzle ORM", "database", 5),
    "@supabase/supabase-js": ("Supabase", "database", 5),
    "mongoose": ("MongoDB (Mongoose)", "database", 5),
    "pg": ("PostgreSQL", "database", 4),
    "mysql2": ("MySQL", "database", 4),
    # AI / LLM
    "openai": ("OpenAI SDK", "ai", 5),
    "@anthropic-ai/sdk": ("Anthropic SDK", "ai", 5),
    "langchain": ("LangChain", "ai", 5),
    "@langchain/core": ("LangChain", "ai", 5),
    "llamaindex": ("LlamaIndex", "ai", 5),
    "ai": ("Vercel AI SDK", "ai", 5),
    # Testing
    "jest": ("Jest", "testing", 5),
    "vitest": ("Vitest", "testing", 5),
    "playwright": ("Playwright (E2E)", "testing", 5),
    "cypress": ("Cypress (E2E)", "testing", 5),
    "mocha": ("Mocha", "testing", 4),
    "@testing-library/react": ("React Testing Library", "testing", 5),
    # Monorepo / Build
    "turbo": ("Turborepo", "build_tool", 5),
    "nx": ("Nx monorepo", "build_tool", 5),
    "webpack": ("Webpack", "build_tool", 4),
    "rollup": ("Rollup", "build_tool", 4),
    "parcel": ("Parcel", "build_tool", 4),
    "rspack": ("Rspack", "build_tool", 4),
    # Mobile
    "capacitor": ("Capacitor", "framework", 5),
    "@ionic/react": ("Ionic", "framework", 5),
}

PIP_MAP = {
    "fastapi": ("FastAPI", "framework", 5),
    "uvicorn": ("Uvicorn (ASGI)", "framework", 4),
    "django": ("Django", "framework", 5),
    "flask": ("Flask", "framework", 5),
    "starlette": ("Starlette", "framework", 4),
    "pandas": ("Pandas (data)", "data_science", 5),
    "numpy": ("NumPy", "data_science", 5),
    "matplotlib": ("Matplotlib", "data_science", 4),
    "seaborn": ("Seaborn", "data_science", 4),
    "scikit-learn": ("scikit-learn (ML)", "ml", 5),
    "sklearn": ("scikit-learn (ML)", "ml", 5),
    "torch": ("PyTorch", "ml", 5),
    "tensorflow": ("TensorFlow", "ml", 5),
    "keras": ("Keras", "ml", 5),
    "xgboost": ("XGBoost", "ml", 5),
    "langchain": ("LangChain", "ai", 5),
    "langchain-core": ("LangChain", "ai", 5),
    "llama-index": ("LlamaIndex", "ai", 5),
    "llama_index": ("LlamaIndex", "ai", 5),
    "openai": ("OpenAI SDK", "ai", 5),
    "anthropic": ("Anthropic SDK", "ai", 5),
    "crewai": ("CrewAI (agents)", "ai", 5),
    "autogen": ("AutoGen (agents)", "ai", 5),
    "dspy": ("DSPy", "ai", 5),
    "pydantic-ai": ("PydanticAI", "ai", 5),
    "semantic-kernel": ("Semantic Kernel", "ai", 5),
    "haystack": ("Haystack (RAG)", "ai", 5),
    "dbt-core": ("dbt", "data_pipeline", 5),
    "apache-airflow": ("Airflow", "data_pipeline", 5),
    "prefect": ("Prefect", "data_pipeline", 5),
    "dagster": ("Dagster", "data_pipeline", 5),
    "pytest": ("pytest", "testing", 5),
    "sqlalchemy": ("SQLAlchemy ORM", "database", 5),
    "psycopg2": ("PostgreSQL (psycopg2)", "database", 5),
    "pymongo": ("MongoDB (pymongo)", "database", 5),
    "redis": ("Redis", "database", 4),
    "celery": ("Celery (task queue)", "infra", 4),
    "pydantic": ("Pydantic", "framework", 4),
    "httpx": ("HTTPX", "framework", 3),
    "requests": ("Requests", "framework", 3),
    "streamlit": ("Streamlit", "framework", 5),
    # Document generation
    "python-docx": ("Word generation (python-docx)", "deliverable_docx", 5),
    "docx": ("Word generation", "deliverable_docx", 5),
    "reportlab": ("PDF generation (reportlab)", "deliverable_pdf", 5),
    "weasyprint": ("PDF generation (weasyprint)", "deliverable_pdf", 5),
    "fpdf2": ("PDF generation (fpdf2)", "deliverable_pdf", 5),
    "fpdf": ("PDF generation (fpdf)", "deliverable_pdf", 5),
    "pdfkit": ("PDF generation (pdfkit)", "deliverable_pdf", 5),
    "openpyxl": ("Excel generation (openpyxl)", "deliverable_xlsx", 5),
    "xlsxwriter": ("Excel generation (xlsxwriter)", "deliverable_xlsx", 5),
    "xlrd": ("Excel reading (xlrd)", "deliverable_xlsx", 4),
    "pymupdf": ("PDF reading (pymupdf)", "deliverable_pdf_read", 5),
    "pdfplumber": ("PDF reading (pdfplumber)", "deliverable_pdf_read", 5),
    "pypdf": ("PDF reading (pypdf)", "deliverable_pdf_read", 5),
    "pypdf2": ("PDF reading (pypdf2)", "deliverable_pdf_read", 5),
    "pptx": ("Presentation (python-pptx)", "deliverable_pptx", 5),
    "python-pptx": ("Presentation (python-pptx)", "deliverable_pptx", 5),
    "gradio": ("Gradio", "framework", 5),
}

GO_MAP = {
    "github.com/gin-gonic/gin": ("Gin", "framework", 5),
    "github.com/labstack/echo": ("Echo", "framework", 5),
    "github.com/gofiber/fiber": ("Fiber", "framework", 5),
}

CARGO_MAP = {
    "actix-web": ("Actix Web", "framework", 5),
    "axum": ("Axum", "framework", 5),
    "rocket": ("Rocket", "framework", 5),
}

POM_MAP = {
    "org.springframework:spring-boot-starter-web": ("Spring Boot", "framework", 5),
    "io.quarkus:quarkus-resteasy": ("Quarkus", "framework", 5),
    "org.jetbrains.kotlin:kotlin-stdlib": ("Kotlin", "language", 5),
}

COMPOSER_MAP = {
    "laravel/framework": ("Laravel", "framework", 5),
    "symfony/symfony": ("Symfony", "framework", 5),
}

PUBSPEC_MAP = {
    "flutter": ("Flutter", "framework", 5),
    "dart": ("Dart", "language", 5),
}

DOCKER_BASE_MAP = {
    "node": ("Node.js", "language", 5),
    "python": ("Python", "language", 5),
    "golang": ("Go", "language", 5),
    "rust": ("Rust", "language", 5),
    "openjdk": ("Java", "language", 5),
    "eclipse-temurin": ("Java", "language", 5),
    "ruby": ("Ruby", "language", 5),
    "php": ("PHP", "language", 5),
    "nginx": ("Nginx", "infra", 4),
    "alpine": ("Alpine Linux", "infra", 3),
    "ubuntu": ("Ubuntu", "infra", 3),
    "debian": ("Debian", "infra", 3),
}

FILE_SIGNAL_MAP = {
    "go.mod": ("Go", "language", 5),
    "Cargo.toml": ("Rust", "language", 5),
    "pom.xml": ("Java (Maven)", "language", 5),
    "build.gradle": ("Java/Kotlin (Gradle)", "language", 5),
    "build.gradle.kts": ("Kotlin (Gradle)", "language", 5),
    "tsconfig.json": ("TypeScript", "language", 5),
    "tailwind.config.js": ("Tailwind CSS", "ui", 5),
    "tailwind.config.ts": ("Tailwind CSS", "ui", 5),
    "next.config.js": ("Next.js", "framework", 5),
    "next.config.ts": ("Next.js", "framework", 5),
    "turbo.json": ("Turborepo monorepo", "build_tool", 5),
    "pnpm-workspace.yaml": ("pnpm monorepo", "build_tool", 5),
    "lerna.json": ("Lerna monorepo", "build_tool", 5),
    "Gemfile": ("Ruby", "language", 5),
    "composer.json": ("PHP", "language", 5),
    "pubspec.yaml": ("Dart/Flutter", "language", 5),
    "Package.swift": ("Swift", "language", 5),
    "*.tf": ("Terraform", "infra", 5),
    "Jenkinsfile": ("Jenkins CI/CD", "ci_cd", 5),
    ".circleci": ("CircleCI", "ci_cd", 5),
}

DIR_SIGNAL_MAP = {
    ".github/workflows": ("GitHub Actions", "ci_cd", 5),
    "kubernetes": ("Kubernetes", "infra", 5),
    "k8s": ("Kubernetes", "infra", 5),
    "helm": ("Helm (K8s)", "infra", 5),
}

ARTIFACT_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv",
                 "target", "vendor", ".next", "dist", "build", ".cache",
                 ".tox", ".eggs", ".pytest_cache", "bower_components", ".gitlab"}

# ── User message keyword matching ─────────────────────────────────────────────
# Sorted longest-first so "react native" matches before "react".
# (phrase, label, category, confidence)
USER_MESSAGE_KEYWORDS = [
    ("react native", "React Native", "mobile", 4),
    ("next.js", "Next.js", "framework", 4),
    ("nextjs", "Next.js", "framework", 4),
    ("sveltekit", "SvelteKit", "framework", 4),
    ("machine learning", "Machine Learning", "ml", 3),
    ("data science", "Data Science", "data_science", 3),
    ("deep learning", "Deep Learning", "ml", 3),
    ("data pipeline", "Data Pipeline", "data_pipeline", 3),
    ("data analysis", "Data Analysis", "data_science", 3),
    ("ai agent", "AI Agent", "ai", 3),
    ("ai agents", "AI Agents", "ai", 3),
    ("web app", "Web Application", "framework", 2),
    ("web application", "Web Application", "framework", 2),
    ("rest api", "REST API", "api", 2),
    ("graphql api", "GraphQL API", "api", 2),
    ("microservice", "Microservices", "architecture", 2),
    ("microservices", "Microservices", "architecture", 2),
    ("jetpack compose", "Jetpack Compose", "mobile", 4),
    ("github actions", "GitHub Actions", "ci_cd", 4),
    ("google cloud", "GCP", "cloud", 4),
    ("styled-components", "Styled Components", "ui", 3),
    ("material ui", "Material UI", "ui", 4),
    # Languages
    ("typescript", "TypeScript", "language", 4),
    ("javascript", "JavaScript", "language", 4),
    ("python", "Python", "language", 4),
    ("golang", "Go", "language", 4),
    ("rust", "Rust", "language", 4),
    ("java", "Java", "language", 4),
    ("kotlin", "Kotlin", "language", 4),
    ("swift", "Swift", "language", 4),
    ("ruby", "Ruby", "language", 4),
    ("php", "PHP", "language", 4),
    ("dart", "Dart", "language", 4),
    ("elixir", "Elixir", "language", 4),
    ("scala", "Scala", "language", 3),
    ("haskell", "Haskell", "language", 3),
    # Frameworks
    ("react", "React", "framework", 4),
    ("vue", "Vue", "framework", 4),
    ("angular", "Angular", "framework", 4),
    ("svelte", "Svelte", "framework", 4),
    ("next", "Next.js", "framework", 4),
    ("nuxt", "Nuxt", "framework", 4),
    ("astro", "Astro", "framework", 4),
    ("remix", "Remix", "framework", 4),
    ("solid", "Solid.js", "framework", 3),
    ("qwik", "Qwik", "framework", 3),
    ("htmx", "HTMX", "framework", 3),
    ("fastapi", "FastAPI", "framework", 4),
    ("django", "Django", "framework", 4),
    ("flask", "Flask", "framework", 4),
    ("starlette", "Starlette", "framework", 4),
    ("express", "Express.js", "framework", 4),
    ("fastify", "Fastify", "framework", 4),
    ("hono", "Hono", "framework", 4),
    ("nestjs", "NestJS", "framework", 4),
    ("gin", "Gin", "framework", 4),
    ("fiber", "Fiber", "framework", 3),
    ("actix", "Actix Web", "framework", 4),
    ("axum", "Axum", "framework", 4),
    ("rocket", "Rocket", "framework", 4),
    ("phoenix", "Phoenix", "framework", 4),
    ("rails", "Rails", "framework", 4),
    ("laravel", "Laravel", "framework", 4),
    ("spring", "Spring Boot", "framework", 4),
    ("quarkus", "Quarkus", "framework", 3),
    # UI / Styling
    ("tailwind", "Tailwind CSS", "ui", 4),
    ("shadcn", "shadcn/ui", "ui", 4),
    ("bootstrap", "Bootstrap", "ui", 4),
    ("antd", "Ant Design", "ui", 3),
    ("chakra", "Chakra UI", "ui", 3),
    ("emotion", "Emotion CSS-in-JS", "ui", 3),
    # Database
    ("postgresql", "PostgreSQL", "database", 4),
    ("postgres", "PostgreSQL", "database", 4),
    ("mysql", "MySQL", "database", 4),
    ("mongodb", "MongoDB", "database", 4),
    ("redis", "Redis", "database", 4),
    ("sqlite", "SQLite", "database", 4),
    ("dynamodb", "DynamoDB", "database", 3),
    ("elasticsearch", "Elasticsearch", "database", 3),
    ("pinecone", "Pinecone", "database", 3),
    ("qdrant", "Qdrant", "database", 3),
    ("chromadb", "ChromaDB", "database", 3),
    ("prisma", "Prisma ORM", "database", 4),
    ("sqlalchemy", "SQLAlchemy", "database", 4),
    ("supabase", "Supabase", "database", 4),
    ("firebase", "Firebase", "database", 4),
    # AI / LLM
    ("anthropic", "Anthropic SDK", "ai", 4),
    ("claude", "Claude API", "ai", 4),
    ("openai", "OpenAI SDK", "ai", 4),
    ("langchain", "LangChain", "ai", 4),
    ("llamaindex", "LlamaIndex", "ai", 4),
    ("llama-index", "LlamaIndex", "ai", 4),
    ("huggingface", "HuggingFace", "ai", 4),
    ("crewai", "CrewAI", "ai", 4),
    ("autogen", "AutoGen", "ai", 4),
    ("langgraph", "LangGraph", "ai", 4),
    ("dspy", "DSPy", "ai", 3),
    ("ollama", "Ollama", "ai", 3),
    ("vllm", "vLLM", "ai", 3),
    # Build / Infra
    ("docker", "Docker", "devops", 4),
    ("kubernetes", "Kubernetes", "infra", 4),
    ("k8s", "Kubernetes", "infra", 4),
    ("terraform", "Terraform", "infra", 4),
    ("pulumi", "Pulumi", "infra", 3),
    ("helm", "Helm", "infra", 4),
    ("circleci", "CircleCI", "ci_cd", 3),
    ("jenkins", "Jenkins", "ci_cd", 4),
    ("argocd", "ArgoCD", "infra", 3),
    # Cloud
    ("vercel", "Vercel", "cloud", 4),
    ("netlify", "Netlify", "cloud", 3),
    ("fly.io", "Fly.io", "cloud", 3),
    ("cloudflare", "Cloudflare", "cloud", 3),
    ("railway", "Railway", "cloud", 3),
    # Testing
    ("jest", "Jest", "testing", 4),
    ("vitest", "Vitest", "testing", 4),
    ("playwright", "Playwright", "testing", 4),
    ("cypress", "Cypress", "testing", 4),
    ("pytest", "pytest", "testing", 4),
    ("mocha", "Mocha", "testing", 3),
    ("storybook", "Storybook", "testing", 3),
    # API
    ("graphql", "GraphQL", "api", 4),
    ("trpc", "tRPC", "api", 4),
    ("grpc", "gRPC", "api", 3),
    ("websocket", "WebSocket", "api", 3),
    # Mobile
    ("expo", "Expo", "mobile", 4),
    ("capacitor", "Capacitor", "mobile", 3),
    ("ionic", "Ionic", "mobile", 3),
    ("flutter", "Flutter", "mobile", 4),
    ("swiftui", "SwiftUI", "mobile", 4),
    # Deliverables
    ("pdf", "PDF generation", "deliverable_pdf", 3),
    ("docx", "Word document", "deliverable_docx", 3),
    ("xlsx", "Excel spreadsheet", "deliverable_xlsx", 3),
    ("pptx", "PowerPoint", "deliverable_pptx", 3),
    ("word", "Word document", "deliverable_docx", 2),
    ("excel", "Excel spreadsheet", "deliverable_xlsx", 2),
    ("powerpoint", "PowerPoint", "deliverable_pptx", 2),
    ("spreadsheet", "Spreadsheet", "deliverable_xlsx", 2),
    ("slides", "Slides", "deliverable_pptx", 2),
    # Category descriptions (vague — low confidence)
    ("frontend", "Frontend", "ui", 2),
    ("front-end", "Frontend", "ui", 2),
    ("backend", "Backend", "framework", 2),
    ("back-end", "Backend", "framework", 2),
    ("fullstack", "Full-stack", "framework", 2),
    ("full-stack", "Full-stack", "framework", 2),
    ("database", "Database", "database", 2),
    ("devops", "DevOps", "devops", 2),
    ("ci/cd", "CI/CD", "ci_cd", 2),
    ("cloud", "Cloud", "cloud", 2),
    ("mobile", "Mobile", "mobile", 2),
    ("desktop", "Desktop", "framework", 2),
    ("server", "Server", "framework", 1),
    ("web", "Web", "framework", 1),
    ("app", "Application", "framework", 1),
    ("ai", "AI/LLM", "ai", 2),
    ("ml", "Machine Learning", "ml", 2),
    ("llm", "LLM", "ai", 2),
    ("go", "Go", "language", 3),
]


def star(n):
    return "★" * n + "☆" * (5 - n)


def parse_user_message(message):
    """Extract tech stack signals from a natural language user message.

    Matches against known keywords sorted longest-first so multi-word
    phrases like "react native" match before single-word "react".
    Returns a list of signal dicts with source='user_message'.
    """
    signals = []
    text = message.lower()
    matched_labels = set()

    for phrase, label, category, confidence in USER_MESSAGE_KEYWORDS:
        if phrase in text and label not in matched_labels:
            matched_labels.add(label)
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": f"user_message",
            })

    return signals


def parse_package_json(content):
    signals = []
    try:
        data = json.loads(content)
    except Exception:
        return signals, ["Failed to parse package.json — invalid JSON"]

    errors = []
    all_deps = {}
    for section in ["dependencies", "devDependencies", "peerDependencies"]:
        all_deps.update(data.get(section, {}))

    for pkg, (label, category, confidence) in NPM_MAP.items():
        if pkg in all_deps:
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": f"package.json › {pkg}"
            })

    # Detect workspace/monorepo from workspaces field
    if "workspaces" in data:
        signals.append({
            "label": "npm/yarn workspaces (monorepo)",
            "category": "build_tool",
            "confidence": 5,
            "source": "package.json › workspaces"
        })

    return signals, errors


def parse_requirements(content):
    signals = []
    errors = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Extract package name (before ==, >=, <=, ~=, !=, [extras])
        pkg = re.split(r"[=><!~\[\s]", line)[0].lower().replace("_", "-")
        if pkg in PIP_MAP:
            label, category, confidence = PIP_MAP[pkg]
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": f"requirements.txt › {pkg}"
            })
    return signals, errors


def parse_pyproject(content):
    signals = []
    errors = []
    deps_pattern = re.compile(r'^([a-zA-Z0-9_\-]+)\s*[=<>!~]', re.MULTILINE)
    for match in deps_pattern.finditer(content):
        pkg = match.group(1).lower().replace("_", "-")
        if pkg in PIP_MAP:
            label, category, confidence = PIP_MAP[pkg]
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": f"pyproject.toml › {pkg}"
            })
    return signals, errors


def parse_pipfile(content):
    signals = []
    errors = []
    section = None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.lower()
            continue
        if section in ("[packages]", "[dev-packages]"):
            pkg = line.split("=", 1)[0].strip().lower().replace("_", "-")
            pkg = re.split(r"[=><!~\[\s]", pkg)[0]
            if pkg in PIP_MAP:
                label, category, confidence = PIP_MAP[pkg]
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": f"Pipfile › {pkg}"
                })
    return signals, errors


def parse_package_lock(content):
    signals = []
    errors = []
    try:
        data = json.loads(content)
    except Exception:
        return signals, ["Failed to parse package-lock.json — invalid JSON"]
    names = set()
    for field in ("dependencies", "packages"):
        deps = data.get(field, {})
        if isinstance(deps, dict):
            for pkg in deps.keys():
                normalized = pkg.lower()
                if normalized.startswith("node_modules/"):
                    normalized = normalized.split("/")[-1]
                names.add(normalized)
    for pkg in names:
        if pkg in NPM_MAP:
            label, category, confidence = NPM_MAP[pkg]
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": f"package-lock.json › {pkg}"
            })
    return signals, errors


def parse_composer_json(content):
    signals = []
    errors = []
    try:
        data = json.loads(content)
    except Exception:
        return signals, ["Failed to parse composer.json — invalid JSON"]
    for section in ("require", "require-dev"):
        for pkg in data.get(section, {}).keys():
            normalized = pkg.lower()
            if normalized in COMPOSER_MAP:
                label, category, confidence = COMPOSER_MAP[normalized]
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": f"composer.json › {pkg}"
                })
    return signals, errors


def parse_pubspec_yaml(content):
    signals = []
    errors = []
    current = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("dependencies:"):
            current = "dependencies"
            continue
        if stripped.startswith("dev_dependencies:"):
            current = "dev_dependencies"
            continue
        if current and ":" in stripped:
            pkg = stripped.split(":", 1)[0].strip().lower().replace("_", "-")
            if pkg in PUBSPEC_MAP:
                label, category, confidence = PUBSPEC_MAP[pkg]
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": f"pubspec.yaml › {pkg}"
                })
    return signals, errors


def parse_go_mod(content):
    signals = []
    errors = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        match = re.match(r'^([a-zA-Z0-9_.\-/]+)\s+', line)
        if match:
            pkg = match.group(1)
            if pkg in GO_MAP:
                label, category, confidence = GO_MAP[pkg]
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": f"go.mod › {pkg}"
                })
    return signals, errors


def parse_cargo_toml(content):
    signals = []
    errors = []
    current = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped.lower()
            continue
        if current in ("[dependencies]", "[dev-dependencies]", "[build-dependencies]"):
            if not stripped or stripped.startswith("#"):
                continue
            pkg = stripped.split("=", 1)[0].strip().lower().replace("_", "-")
            pkg = re.split(r"[=<>!~\[\s]", pkg)[0]
            if pkg in CARGO_MAP:
                label, category, confidence = CARGO_MAP[pkg]
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": f"Cargo.toml › {pkg}"
                })
    return signals, errors


def parse_pom_xml(content):
    signals = []
    errors = []
    for group, artifact in re.findall(r'<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>', content):
        full = f"{group.strip()}:{artifact.strip()}".lower()
        if full in POM_MAP:
            label, category, confidence = POM_MAP[full]
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": f"pom.xml › {full}"
            })
    return signals, errors


def parse_dockerfile(content):
    signals = []
    errors = []
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("FROM"):
            parts = line.split()
            if len(parts) >= 2:
                image = parts[1].split(":")[0].split("/")[-1].lower()
                if image in DOCKER_BASE_MAP:
                    label, category, confidence = DOCKER_BASE_MAP[image]
                    signals.append({
                        "label": label,
                        "category": category,
                        "confidence": confidence,
                        "source": f"Dockerfile › FROM {parts[1]}"
                    })
        if "services:" in line:
            signals.append({
                "label": "Multi-container (microservices)",
                "category": "architecture",
                "confidence": 4,
                "source": "docker-compose.yml › services"
            })
        for db in ["postgres", "mysql", "mongodb", "redis", "elasticsearch"]:
            if db in line.lower():
                signals.append({
                    "label": db.capitalize(),
                    "category": "database",
                    "confidence": 4,
                    "source": f"Dockerfile/compose › {db}"
                })
    return signals, errors


def _rel_path(base, target):
    try:
        return target.relative_to(base)
    except ValueError:
        return target


def _in_artifact_dir(path):
    return any(part in ARTIFACT_DIRS for part in path.parts)


def scan_directory(path):
    """Scan a directory for known config files and aggregate signals."""
    signals = []
    errors = []
    conflicts = []
    p = Path(path)

    # File-based existence signals (e.g., go.mod → Go language)
    for filename, (label, category, confidence) in FILE_SIGNAL_MAP.items():
        if "*" in filename:
            for match in p.rglob(filename):
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": str(_rel_path(p, match))
                })
                break
        else:
            for match in p.rglob(filename):
                if not _in_artifact_dir(match):
                    signals.append({
                        "label": label,
                        "category": category,
                        "confidence": confidence,
                        "source": str(_rel_path(p, match))
                    })
                    break

    # Directory-based signals (e.g., .github/workflows → GitHub Actions)
    for dirname, (label, category, confidence) in DIR_SIGNAL_MAP.items():
        for match in p.rglob(dirname):
            if match.is_dir() and not _in_artifact_dir(match):
                signals.append({
                    "label": label,
                    "category": category,
                    "confidence": confidence,
                    "source": str(_rel_path(p, match))
                })
                break

    # Parse known config files across all subdirectories
    for fname, parser in [
        ("package.json", parse_package_json),
        ("package-lock.json", parse_package_lock),
        ("Pipfile", parse_pipfile),
        ("requirements.txt", parse_requirements),
        ("pyproject.toml", parse_pyproject),
        ("composer.json", parse_composer_json),
        ("pubspec.yaml", parse_pubspec_yaml),
        ("go.mod", parse_go_mod),
        ("Cargo.toml", parse_cargo_toml),
        ("pom.xml", parse_pom_xml),
        ("Dockerfile", parse_dockerfile),
        ("docker-compose.yml", parse_dockerfile),
        ("docker-compose.yaml", parse_dockerfile),
    ]:
        for fpath in sorted(p.rglob(fname)):
            if _in_artifact_dir(fpath):
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                s, e = parser(content)
                rel = _rel_path(p, fpath)
                for signal in s:
                    signal["source"] = f"{rel} › {signal['source'].split(' › ', 1)[-1]}"
                signals.extend(s)
                errors.extend(e)
            except Exception as ex:
                errors.append(f"Could not read {fname} at {_rel_path(p, fpath)}: {ex}")

    return signals, errors, conflicts


def detect_conflicts(signals):
    """Find contradictory signals in the same category."""
    conflicts = []
    by_category = {}
    for s in signals:
        cat = s["category"]
        by_category.setdefault(cat, []).append(s)

    framework_labels = [s["label"] for s in by_category.get("framework", [])]
    # Flag competing frontend frameworks
    frontend = [l for l in framework_labels if any(
        f in l for f in ["React", "Vue", "Angular", "Svelte"])]
    if len(set(frontend)) > 1:
        conflicts.append({
            "category": "framework",
            "signals": frontend,
            "resolution": f"Highest-confidence signal wins. Using: {frontend[0]}"
        })

    return conflicts


def match_skills(signals):
    """Score each installed skill against detected signals."""
    signal_labels = " ".join(
        s["label"].lower() + " " + s["category"].lower() for s in signals
    )
    results = []
    for skill_name, meta in SKILL_REGISTRY.items():
        score = 0
        matched = []
        first_match = True
        for trigger in meta["triggers"]:
            if trigger.lower() in signal_labels:
                matching_signals = [
                    s for s in signals
                    if trigger.lower() in (s["label"] + " " + s["category"]).lower()
                ]
                conf = max((s["confidence"] for s in matching_signals), default=3)
                # First match gives big base boost; subsequent matches add incremental score
                if first_match:
                    score += 50 + (conf * 2)
                    first_match = False
                else:
                    score += 8 + (conf * 2)
                matched.append(trigger)
        if score > 0:
            priority = "Essential" if score >= 60 else ("Helpful" if score >= 30 else "Optional")
            results.append({
                "skill": skill_name,
                "score": min(score, 99),
                "priority": priority,
                "matched_triggers": matched,
                "description": meta["description"]
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def detect_missing_skills(signals):
    """Flag stack components that have no matching installed skill."""
    GAP_MAP = {
        "data_science": ("data-analysis", "EDA, charting, statistical summaries"),
        "ml": ("ml-engineering", "model training, evaluation, deployment"),
        "testing": ("testing", "test generation, coverage analysis"),
        "ci_cd": ("devops", "CI/CD pipeline setup, Docker, K8s"),
        "data_pipeline": ("data-pipeline", "dbt, Airflow, Prefect workflow design"),
    }
    gaps = []
    found_categories = {s["category"] for s in signals}
    for category, (skill_name, description) in GAP_MAP.items():
        if category in found_categories:
            gaps.append({
                "category": category,
                "suggested_skill": skill_name,
                "description": description
            })
    return gaps


def run(source=None, user_message=None):
    signals, errors, conflicts = [], [], []

    if source:
        p = Path(source)
        if p.is_dir():
            signals, errors, conflicts = scan_directory(p)
        elif p.is_file():
            content = p.read_text(encoding="utf-8", errors="replace")
            name = p.name
            # Detect by exact name first, then by content heuristics
            if name == "package.json" or (name.endswith(".json") and '"dependencies"' in content):
                signals, errors = parse_package_json(content)
            elif name == "requirements.txt" or (name.endswith(".txt") and re.search(r'^[a-zA-Z0-9_\-]+(==|>=|<=|~=|!=|\[)', content, re.MULTILINE)):
                signals, errors = parse_requirements(content)
            elif name == "pyproject.toml" or name.endswith(".toml"):
                signals, errors = parse_pyproject(content)
            elif name == "package-lock.json":
                signals, errors = parse_package_lock(content)
            elif name == "Pipfile":
                signals, errors = parse_pipfile(content)
            elif name == "composer.json":
                signals, errors = parse_composer_json(content)
            elif name == "pubspec.yaml":
                signals, errors = parse_pubspec_yaml(content)
            elif name == "go.mod":
                signals, errors = parse_go_mod(content)
            elif name == "Cargo.toml":
                signals, errors = parse_cargo_toml(content)
            elif name == "pom.xml":
                signals, errors = parse_pom_xml(content)
            elif name in ("Dockerfile", "docker-compose.yml", "docker-compose.yaml") or "FROM " in content or "services:" in content:
                signals, errors = parse_dockerfile(content)
            else:
                # Try all parsers, pick the one that finds most signals
                best_signals, best_errors = [], []
                for parser in [
                    parse_package_json,
                    parse_package_lock,
                    parse_pipfile,
                    parse_requirements,
                    parse_pyproject,
                    parse_composer_json,
                    parse_pubspec_yaml,
                    parse_go_mod,
                    parse_cargo_toml,
                    parse_pom_xml,
                    parse_dockerfile,
                ]:
                    try:
                        s, e = parser(content)
                        if len(s) > len(best_signals):
                            best_signals, best_errors = s, e
                    except Exception:
                        pass
                if best_signals:
                    signals, errors = best_signals, best_errors
                else:
                    errors.append(f"Unrecognized file type: {name}")
        else:
            errors.append(f"Path not found: {source}")

    if user_message:
        msg_signals = parse_user_message(user_message)
        signals.extend(msg_signals)

    conflicts = detect_conflicts(signals)
    skill_matches = match_skills(signals)
    missing = detect_missing_skills(signals)

    # Deduplicate signals by label + category (keep highest confidence)
    seen = {}
    for s in signals:
        key = s["label"] + s["category"]
        if key not in seen or s["confidence"] > seen[key]["confidence"]:
            seen[key] = s
    unique_signals = list(seen.values())

    return {
        "source": source or "(user message)",
        "signals": unique_signals,
        "conflicts": conflicts,
        "skill_matches": skill_matches,
        "missing_skills": missing,
        "errors": errors
    }



def install_cmd(skill_name):
    """Return the install command for a skill."""
    INSTALL_URLS = {
        "frontend-design":        "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/frontend-design/frontend-design.skill",
        "docx":                   "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/docx/docx.skill",
        "pdf":                    "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/pdf/pdf.skill",
        "pdf-reading":            "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/pdf-reading/pdf-reading.skill",
        "pptx":                   "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/pptx/pptx.skill",
        "xlsx":                   "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/xlsx/xlsx.skill",
        "file-reading":           "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/file-reading/file-reading.skill",
        "product-self-knowledge": "https://raw.githubusercontent.com/anthropics/claude-skills/main/public/product-self-knowledge/product-self-knowledge.skill",
        "skill-creator":          "https://raw.githubusercontent.com/anthropics/claude-skills/main/examples/skill-creator/skill-creator.skill",
        "skill-recommender":      "https://raw.githubusercontent.com/Ganesh1110/skill-recommender/main/skill-recommender.skill",
    }
    COMMUNITY = {
        "mobile":            "Not in public registry yet. Build it: use skill-creator",
        "backend-frameworks":"Not in public registry yet. Build it: use skill-creator",
        "devops":            "Not in public registry yet. Build it: use skill-creator",
        "database":          "Not in public registry yet. Build it: use skill-creator",
        "testing":           "Not in public registry yet. Build it: use skill-creator",
        "data-analysis":     "Not in public registry yet. Build it: use skill-creator",
        "ml-engineering":    "Not in public registry yet. Build it: use skill-creator",
        "ai-agents":         "Not in public registry yet. Build it: use skill-creator",
        "api-docs":          "Not in public registry yet. Build it: use skill-creator",
    }
    if skill_name in INSTALL_URLS:
        url = INSTALL_URLS[skill_name]
        fname = url.split("/")[-1]
        return [
            f"curl -O {url}",
            f"# then: Claude Desktop -> Settings -> Skills -> Install -> {fname}",
        ]
    elif skill_name in COMMUNITY:
        return [COMMUNITY[skill_name]]
    return ["Check: Claude Desktop -> Settings -> Skills"]


def pretty_print(result):
    W = 58

    # Header
    print()
    print("=" * W)
    print(f"  skill-recommender")
    print(f"  Source: {result['source']}")
    print("=" * W)

    # Detected Stack
    print()
    print("  DETECTED STACK")
    print("  " + "-" * (W - 2))
    by_cat = {}
    for s in result["signals"]:
        by_cat.setdefault(s["category"], []).append(s)

    if by_cat:
        for cat, items in sorted(by_cat.items()):
            for item in items:
                print(f"  {cat:<18} {star(item['confidence'])}  {item['label']}")
                print(f"  {'':<18}   \u2514\u2500 {item['source']}")
    else:
        print("  No stack signals detected.")

    # Conflicts
    if result["conflicts"]:
        print()
        print("  CONFLICTS")
        print("  " + "-" * (W - 2))
        for c in result["conflicts"]:
            print(f"  !  {c['category']}: {', '.join(c['signals'])}")
            print(f"     Resolution: {c['resolution']}")

    # Recommended Skills
    print()
    print("=" * W)
    print("  RECOMMENDED SKILLS")
    print("=" * W)

    if not result["skill_matches"]:
        print("  No matching skills found for this stack.")
    else:
        for i, match in enumerate(result["skill_matches"], 1):
            p = match["priority"]
            badge = "[Essential]" if p == "Essential" else "[Helpful]  " if p == "Helpful" else "[Optional] "
            print()
            print(f"  {i}. {match['skill']}")
            print(f"     Priority : {badge}  Score: {match['score']}/99")
            print(f"     Why      : {match['description']}")
            print(f"     Matched  : {', '.join(match['matched_triggers'])}")
            print(f"     Install  :")
            for line in install_cmd(match["skill"]):
                print(f"       {line}")
            print("  " + "-" * (W - 2))

    # Skill Gaps
    if result["missing_skills"]:
        print()
        print("  SKILL GAPS")
        print("  " + "-" * (W - 2))
        for gap in result["missing_skills"]:
            print(f"  !  No skill for: {gap['category']}")
            print(f"     Suggested : {gap['suggested_skill']}")
            print(f"     Covers    : {gap['description']}")
            print(f"     Create    : run skill-creator to build '{gap['suggested_skill']}'")

    # Errors
    if result["errors"]:
        print()
        print("  ERRORS")
        print("  " + "-" * (W - 2))
        for e in result["errors"]:
            print(f"  x  {e}")

    # Footer
    print()
    print("=" * W)
    print(f"  {len(result['skill_matches'])} skill(s) matched  |  {len(result['missing_skills'])} gap(s) flagged")
    print("=" * W)
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_stack.py <file_or_directory> [options]")
        print("       python detect_stack.py --message \"I'm building a React app\"")
        print("       echo \"I need Python ML\" | python detect_stack.py --stdin")
        print("")
        print("Options:")
        print("  --message TEXT   Augment detection with a user message")
        print("  --stdin          Read user message from stdin")
        print("  --json           Output JSON instead of pretty-print")
        sys.exit(1)

    source = None
    user_message = None
    as_json = "--json" in sys.argv
    use_stdin = "--stdin" in sys.argv

    # Extract --message argument
    if "--message" in sys.argv:
        msg_idx = sys.argv.index("--message") + 1
        if msg_idx < len(sys.argv) and not sys.argv[msg_idx].startswith("--"):
            user_message = sys.argv[msg_idx]

    if use_stdin:
        user_message = sys.stdin.read().strip()

    # Determine source path (first positional arg that isn't a flag or --message's value)
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--message":
            i += 2  # skip --message and its value
            continue
        if arg.startswith("--"):
            i += 1
            continue
        source = arg
        break

    if not source and not user_message:
        print("Error: provide a file/directory path or --message/--stdin", file=sys.stderr)
        sys.exit(1)

    result = run(source, user_message)

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        pretty_print(result)