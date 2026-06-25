<p align="center">
  <h1 align="center">Skill Recommender <sup>v1.1.0</sup></h1>
  <p align="center">Automatically detect a project's tech stack and recommend the most relevant AI coding skills.</p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.9+-blue" alt="Python 3.9+">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
    <img src="https://img.shields.io/badge/dependencies-0-success" alt="Zero Dependencies">
    <img src="https://img.shields.io/badge/tests-66%20unit%20%2B%2016%20integration-brightgreen" alt="Tests">
  </p>
</p>

Skill Recommender analyzes project configuration files, directory structure, and natural language descriptions to identify frameworks, languages, infrastructure, and tooling — then recommends the AI skills that will provide the biggest productivity boost.

- ⚡ **Zero dependencies** — pure Python 3.9+ stdlib
- 🐙 **Monorepo aware** — recursive scanning with artifact exclusion
- 🎯 **Confidence scoring** — every signal ranked 1–5
- 🤖 **Natural language input** — describe your project in plain English
- 📄 **JSON output** — pipeline-ready for CI/CD and automation
- 🏠 **Offline** — no network calls, no telemetry

---

## Demo

```bash
$ python3 scripts/detect_stack.py --message "React app with FastAPI backend and PostgreSQL"

==========================================================
  skill-recommender
  Source: (user message)
==========================================================

  DETECTED STACK
  --------------------------------------------------------
  database           ★★★★☆  PostgreSQL
  framework          ★★★★☆  React
  framework          ★★★★☆  FastAPI

==========================================================
  RECOMMENDED SKILLS
==========================================================

  1. frontend-design
     Priority : [Essential]  Score: 99/99
     Why      : UI/UX design tokens, component patterns, Tailwind, React/Vue
     Matched  : react
     Install  :
       curl -O https://raw.githubusercontent.com/anthropics/claude-skills/main/public/frontend-design/frontend-design.skill

  2. backend-frameworks
     Priority : [Essential]  Score: 70/99
     Why      : Backend framework and API service patterns
     Matched  : fastapi

==========================================================
  2 skill(s) matched  |  0 gap(s) flagged
==========================================================
```

---

## Features

| Capability                   | What it does                                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Config file parsing**      | Reads 18+ file formats: `package.json`, `go.mod`, `Cargo.toml`, `Gemfile`, `Dockerfile`, `requirements.txt`, `pyproject.toml`, `build.gradle`, `mix.exs`, and more |
| **Lock file analysis**       | Extracts dependencies from `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`                                                                              |
| **Directory scanning**       | Detects signals from directory structure (`.github/workflows/`, `kubernetes/`, `helm/`)                                                                            |
| **File extension detection** | Identifies languages and frameworks from `.tsx`, `.vue`, `.svelte`, `.rs`, `.go`, `.kt`, `.scala`, `.hs`, and more                                                 |
| **Import pattern scanning**  | Checks first 10 lines of source files for import usage (React, Vue, FastAPI, PyTorch, LangChain, etc.)                                                             |
| **User message parsing**     | Recognizes ~350 keywords and phrases from natural language descriptions                                                                                            |
| **Conflict detection**       | Flags competing frameworks, databases, UI libraries, E2E tools, CI/CD systems, and build tools                                                                     |
| **Caching**                  | Fingerprint-based cache in `~/.cache/skill-recommender/` avoids re-scanning unchanged directories                                                                  |
| **Monorepo support**         | Recursively walks sub-packages, attributes signals with relative paths                                                                                             |
| **Explain mode**             | `--explain` shows exactly which signals matched which skill triggers                                                                                               |
| **Exclusion rules**          | `--exclude DIR` to skip directories; artifact dirs (`node_modules`, `.git`, `dist`) skipped by default                                                             |

---

## Quick Start

```bash
# Clone and run — no install step needed
git clone https://github.com/Ganesh1110/skill-recommender.git
cd skill-recommender

# Analyze a project directory
python3 scripts/detect_stack.py ~/my-project/

# Analyze a single config file
python3 scripts/detect_stack.py ~/my-project/package.json

# Describe your project in natural language
python3 scripts/detect_stack.py --message "I'm building a React Native app with Supabase"

# Augment file analysis with context
python3 scripts/detect_stack.py ~/my-project/ --message "We deploy on AWS ECS"

# Pipe from stdin
echo "Python ML pipeline with FastAPI" | python3 scripts/detect_stack.py --stdin

# Machine-readable output
python3 scripts/detect_stack.py ~/my-project/ --json
```

---

## How It Works

```
Project Directory or File or Message
              │
              ▼
    ┌─────────────────────┐
    │   Config Parsers    │  ← 18+ parsers (package.json, go.mod, Dockerfile, ...)
    │   Lock File Parsers │  ← 6 lock-file parsers (yarn.lock, Cargo.lock, ...)
    │   Extension Checks  │  ← 20+ file extension signals
    │   Import Scanning   │  ← First 10 lines of source files
    │   Keyword Matching  │  ← ~350 natural language keywords
    └────────┬────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Signal Merge &    │
    │   Deduplication     │  ← Keeps highest confidence per (label, category)
    └────────┬────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Conflict Detection│  ← Flags competing frameworks, DBs, UI libs, etc.
    └────────┬────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Skill Matching    │  ← Weighted scoring against 17 skill definitions
    └────────┬────────────┘
              │
              ▼
    Ranked Recommendations (Essential / Helpful / Optional)
```

---

## Supported Ecosystems

| Category           | Technologies                                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Languages**      | Python, JavaScript, TypeScript, Go, Rust, Java, Kotlin, PHP, Ruby, Dart, Elixir, Swift, Scala, Haskell                                |
| **Frontend**       | React, Next.js, Vue, Nuxt, Angular, Svelte, SvelteKit, Astro, Solid, Qwik, Remix, HTMX                                                |
| **Backend**        | FastAPI, Django, Flask, Express, Fastify, NestJS, Hono, Gin, Fiber, Actix, Spring Boot, Laravel, Rails, Phoenix                       |
| **UI / Styling**   | Tailwind CSS, shadcn/ui, Material UI, Bootstrap, Chakra UI, Emotion, Styled Components, Radix UI                                      |
| **Databases**      | PostgreSQL, MySQL, MongoDB, Redis, SQLite, Supabase, Firebase, Prisma, Drizzle, SQLAlchemy, Pinecone, Qdrant, ChromaDB, Elasticsearch |
| **AI / ML**        | OpenAI, Anthropic, LangChain, LlamaIndex, CrewAI, AutoGen, LangGraph, PyTorch, TensorFlow, scikit-learn, Hugging Face, DSPy           |
| **Infrastructure** | Docker, Docker Compose, Kubernetes, Helm, Terraform, Pulumi, Ansible                                                                  |
| **CI/CD**          | GitHub Actions, CircleCI, Jenkins, ArgoCD                                                                                             |
| **Cloud**          | AWS, GCP, Azure, Vercel, Netlify, Cloudflare, Fly.io, Railway                                                                         |
| **Testing**        | Jest, Vitest, Playwright, Cypress, pytest, RSpec, Mocha, Storybook, Selenium                                                          |
| **Mobile**         | React Native, Expo, Flutter, SwiftUI, Jetpack Compose, Ionic, Capacitor                                                               |
| **Documents**      | PDF generation, Word (.docx), Excel (.xlsx), PowerPoint (.pptx), PDF reading                                                          |
| **Build Tools**    | Vite, Webpack, Rollup, Parcel, Rspack, Turborepo, Nx, Lerna, pnpm workspaces                                                          |

---

## CLI Reference

| Flag             | Description                                           |
| ---------------- | ----------------------------------------------------- |
| `--message TEXT` | Augment detection with a natural language description |
| `--stdin`        | Read user message from pipe                           |
| `--json`         | Output JSON (machine-readable)                        |
| `--explain`      | Show which signals matched each skill trigger         |
| `--exclude DIR`  | Skip directory during scan (repeatable)               |
| `--no-cache`     | Bypass fingerprint cache                              |
| `--version`      | Print version and exit                                |
| `--help`, `-h`   | Show help message                                     |

---

## Detection Engine

Every detected technology is scored on a **confidence scale** (1–5):

| Level             | Source Examples                                                         |
| ----------------- | ----------------------------------------------------------------------- |
| **5** — Definite  | Explicit dependency in `package.json`, `requirements.txt`, `Cargo.toml` |
| **4** — Strong    | User message explicitly names a framework, file extension like `.tsx`   |
| **3** — Moderate  | File extension (`.py`), vague keyword match, user message with context  |
| **2** — Weak      | Generic term like "frontend", "backend", "database"                     |
| **1** — Ambiguous | Very broad terms like "web", "app", "server"                            |

Skills are scored by aggregating matching signal confidence × category weight:

```
skill_score = Σ (signal_confidence × category_weight) × 14
```

Results are bucketed:

- **Essential** (≥60) — critical for this project
- **Helpful** (≥30) — relevant but not essential
- **Optional** (<30) — tangentially related

---

## Performance

| Project Size                 | Scan Time | Memory |
| ---------------------------- | --------- | ------ |
| Small (few configs)          | <50 ms    | ~15 MB |
| Medium (monorepo, 50+ deps)  | ~150 ms   | ~25 MB |
| Large monorepo (1000+ files) | <1 s      | ~40 MB |

Cache hits reduce subsequent scans to near-instant. Fingerprint only checks config/lock file mtimes — not every source file.

---

## Extending

Adding support for a new framework is a single JSON edit:

```bash
# Add to the appropriate package map
vim config/npm.json

# Or add a new file-based signal
vim config/files.json
```

**Example — add Astro to npm detection:**

```json
{
  "astro": ["Astro", "framework", 5]
}
```

To add a new parser (new manifest format), see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Roadmap

### v1.1 — Complete in this release

- [x] Global cache directory (`~/.cache/skill-recommender/`)
- [x] `--exclude`, `--no-cache`, `--explain`, `--version` flags
- [x] Multi-category conflict detection (database, UI, build tools, CI/CD, testing)
- [x] 150+ new user-message keywords
- [x] Cache, versioning, and edge-case test coverage

### v1.2 — Near-term

- [ ] AST-based parsing (Python `ast`, JS/TS tree-sitter)
- [ ] Conda, NuGet, Rebar3, Shards parsers
- [ ] Cloud SDK package mapping (`boto3` → AWS, etc.)
- [ ] Cache invalidation on source file changes
- [ ] Per-sub-project output for monorepos

### v2.0 — Long-term

- [ ] Plugin architecture (entry-point based parsers)
- [ ] Interactive mode for ambiguous projects
- [ ] Claude Desktop API integration (auto-install)
- [ ] Watch mode for live development
- [ ] Web UI / VS Code extension

---

## Why Skill Recommender?

Choosing the right AI coding skills manually becomes difficult as projects grow across multiple languages and frameworks. Most developers end up guessing, installing everything, or ignoring skills entirely.

Skill Recommender **automatically discovers your stack** and suggests the most relevant skills, so AI assistants adapt to your project with zero configuration.

**Ideal for:**

- AI coding assistants (Claude, Copilot, etc.)
- Developer onboarding — automatically detect stack
- CI/CD pipelines — emit skill recommendations per branch
- Template/starter repos — pre-configure skills
- Internal developer platforms — standardize AI tooling

---

## Project Structure

```
skill-recommender/
├── scripts/
│   ├── detect_stack.py      # Detection engine (1,700+ lines)
│   ├── test_parsers.py      # Unit tests (66 tests)
│   └── run_tests.py         # Integration tests (16 tests)
├── config/
│   ├── npm.json             # NPM package → signal mappings
│   ├── pip.json             # PyPI package → signal mappings
│   ├── go.json              # Go module → signal mappings
│   ├── cargo.json           # Rust crate → signal mappings
│   ├── pom.json             # Maven artifact → signal mappings
│   ├── composer_packages.json # PHP Composer mappings
│   ├── pubspec.json         # Dart/Flutter mappings
│   ├── docker.json          # Docker base image mappings
│   ├── files.json           # File name → signal mappings
│   ├── dirs.json            # Directory name → signal mappings
│   ├── keywords.json        # User message keywords (~350 entries)
│   └── skills.json          # 17 skill definitions with triggers
├── SKILL.md                 # AI assistant behavior guide
├── references/
│   └── stack-catalog.md     # Extended framework reference
├── ROADMAP.md               # Development roadmap
├── CONTRIBUTING.md          # Contribution guide
├── LICENSE                  # MIT
└── README.md
```

---

## Running Tests

```bash
# Unit tests (66 tests — parser functions in isolation)
python3 scripts/test_parsers.py -v

# Integration tests (16 tests — full pipeline via subprocess)
python3 scripts/run_tests.py

# Single integration test
python3 scripts/run_tests.py --test react_tailwind

# JSON test report
python3 scripts/run_tests.py --json
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Adding new package/framework mappings
- Adding new parsers
- Code style and conventions
- PR guidelines

---

## License

MIT — see [LICENSE](LICENSE).
