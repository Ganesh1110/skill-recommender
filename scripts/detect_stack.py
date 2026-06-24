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
    ".github/workflows": ("GitHub Actions", "ci_cd", 5),
    "Jenkinsfile": ("Jenkins CI/CD", "ci_cd", 5),
    ".circleci": ("CircleCI", "ci_cd", 5),
    "kubernetes": ("Kubernetes", "infra", 5),
    "k8s": ("Kubernetes", "infra", 5),
    "helm": ("Helm (K8s)", "infra", 5),
}


def star(n):
    return "★" * n + "☆" * (5 - n)


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


def scan_directory(path):
    """Scan a directory for known config files and aggregate signals."""
    signals = []
    errors = []
    conflicts = []
    p = Path(path)

    for filename, (label, category, confidence) in FILE_SIGNAL_MAP.items():
        if "*" in filename:
            matches = list(p.rglob(filename))
        else:
            matches = [p / filename] if (p / filename).exists() else []
            if not matches:
                matches = list(p.rglob(filename))
        for match in matches[:1]:
            signals.append({
                "label": label,
                "category": category,
                "confidence": confidence,
                "source": str(match.relative_to(p) if p in match.parents else match)
            })

    # Parse known config files
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
        fpath = p / fname
        if fpath.exists():
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                s, e = parser(content)
                signals.extend(s)
                errors.extend(e)
            except Exception as ex:
                errors.append(f"Could not read {fname}: {ex}")

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


def run(source):
    p = Path(source)
    signals, errors, conflicts = [], [], []

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

    conflicts = detect_conflicts(signals)
    skill_matches = match_skills(signals)
    missing = detect_missing_skills(signals)

    # Deduplicate signals by label
    seen = set()
    unique_signals = []
    for s in signals:
        key = s["label"] + s["category"]
        if key not in seen:
            seen.add(key)
            unique_signals.append(s)

    return {
        "source": str(source),
        "signals": unique_signals,
        "conflicts": conflicts,
        "skill_matches": skill_matches,
        "missing_skills": missing,
        "errors": errors
    }


def pretty_print(result):
    print("\n🔍 Detected Stack")
    print("-" * 50)
    by_cat = {}
    for s in result["signals"]:
        by_cat.setdefault(s["category"], []).append(s)

    for cat, items in sorted(by_cat.items()):
        for item in items:
            print(f"  {cat:<16} {star(item['confidence'])}  {item['label']}")
            print(f"  {'':16}   └─ {item['source']}")

    if result["conflicts"]:
        print("\n⚠️  Conflicts Detected")
        for c in result["conflicts"]:
            print(f"  {c['category']}: {', '.join(c['signals'])}")
            print(f"  → {c['resolution']}")

    print("\n═" * 50)
    print("  Recommended Skills")
    print("-" * 50)
    for i, match in enumerate(result["skill_matches"], 1):
        emoji = "✅" if match["priority"] == "Essential" else ("💡" if match["priority"] == "Helpful" else "🔧")
        print(f"\n{i}. {match['skill']:<25} Score: {match['score']}")
        print(f"   Priority: {emoji} {match['priority']}")
        print(f"   Matched:  {', '.join(match['matched_triggers'])}")
        print(f"   Why:      {match['description']}")

    if result["missing_skills"]:
        print("\n⚠️  No skill found for:")
        for gap in result["missing_skills"]:
            print(f"  {gap['category']} → suggest creating '{gap['suggested_skill']}' skill")
            print(f"  Coverage: {gap['description']}")

    if result["errors"]:
        print("\n⚠️  Errors:")
        for e in result["errors"]:
            print(f"  {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_stack.py <file_or_directory>")
        sys.exit(1)

    source = sys.argv[1]

    if "--json" in sys.argv:
        result = run(source)
        print(json.dumps(result, indent=2))
    else:
        result = run(source)
        pretty_print(result)