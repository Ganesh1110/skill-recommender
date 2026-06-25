# Skill Recommender

Detects a project's tech stack from config files and natural language, then recommends the best AI skills to install. Zero dependencies — runs on Python 3.9+ stdlib.

## Quick Start

```bash
# Analyze a project directory
python3 scripts/detect_stack.py ./my-project/

# Analyze a single config file
python3 scripts/detect_stack.py package.json

# Augment with a user message
python3 scripts/detect_stack.py ./my-project/ --message "I need Docker deployment"

# Message-only (no files)
python3 scripts/detect_stack.py --message "I'm building a React app with FastAPI"

# Pipe from stdin
echo "I need Python ML" | python3 scripts/detect_stack.py --stdin

# JSON output
python3 scripts/detect_stack.py ./my-project/ --json
```

## What It Detects

| Source | Examples | Confidence |
|--------|----------|------------|
| Config files | `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml` | ★★★★★ |
| User message | "I'm using React", "I need PDF generation" | ★★★★☆ |
| Directory signals | `.github/workflows/`, `kubernetes/`, `helm/` | ★★★★★ |
| File signals | `tsconfig.json`, `tailwind.config.*`, `Dockerfile` | ★★★★★ |

### Supported Config Files

| File | Language/Ecosystem |
|------|--------------------|
| `package.json` | Node.js / JavaScript |
| `package-lock.json` | Node.js (lock file) |
| `requirements.txt` | Python |
| `pyproject.toml` | Python (Poetry/pip) |
| `Pipfile` | Python (Pipenv) |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` | Java (Maven) |
| `build.gradle` / `.kts` | Java/Kotlin (Gradle) |
| `composer.json` | PHP |
| `pubspec.yaml` | Dart/Flutter |
| `Dockerfile` | Container images |
| `docker-compose.yml` | Multi-container services |
| `Gemfile` | Ruby |

### Supported Directories

| Directory | Signal |
|-----------|--------|
| `.github/workflows/` | GitHub Actions CI/CD |
| `kubernetes/`, `k8s/` | Kubernetes |
| `helm/` | Helm charts |

### User Message Keywords

The tool recognizes ~190 keywords including framework names, languages, categories, and tool names. Examples:

- Explicit: "React", "FastAPI", "PostgreSQL", "Docker", "TypeScript"
- Phrases: "React Native", "machine learning", "data pipeline", "GitHub Actions"
- Vague: "frontend", "backend", "database", "mobile", "AI"

## Output Format

### Pretty-print (default)

```
==========================================================
  skill-recommender
  Source: ./my-project
==========================================================

  DETECTED STACK
  --------------------------------------------------------
  framework          ★★★★★  React
                       └─ package.json › react
  ui                 ★★★★★  Tailwind CSS
                       └─ tailwind.config.ts

==========================================================
  RECOMMENDED SKILLS
==========================================================

  1. frontend-design
     Priority : [Essential]  Score: 99/99
     Why      : UI/UX design tokens, component patterns
     Matched  : react, tailwind, ui
     Install  :
       curl -O https://raw.githubusercontent.com/.../frontend-design.skill
```

### JSON output (`--json`)

```json
{
  "source": "./my-project",
  "signals": [
    {
      "label": "React",
      "category": "framework",
      "confidence": 5,
      "source": "package.json › react"
    }
  ],
  "skill_matches": [
    {
      "skill": "frontend-design",
      "score": 99,
      "priority": "Essential",
      "matched_triggers": ["react", "tailwind"],
      "description": "UI/UX design tokens, component patterns"
    }
  ],
  "conflicts": [],
  "missing_skills": [],
  "errors": []
}
```

## CLI Options

| Flag | Description |
|------|-------------|
| `--json` | Output JSON instead of pretty-print |
| `--message TEXT` | Augment detection with a user message |
| `--stdin` | Read user message from stdin |
| `--explain` | Show why each skill was recommended (signal → trigger matches) |
| `--exclude DIR` | Exclude a directory from scanning (repeatable) |
| `--no-cache` | Skip reading/writing the cache file |
| `--version` | Show version and exit |
| `--help`, `-h` | Show help message and exit |

## Monorepo Support

Recursively scans all subdirectories. Config files in nested packages are detected and attributed with their relative path:

```
framework          ★★★★★  React
                     └─ apps/web/package.json › react
framework          ★★★★★  Fastify
                     └─ apps/api/package.json › fastify
```

Artifact directories (`node_modules`, `.git`, `dist`, `build`, etc.) are automatically excluded.

## Running Tests

```bash
python3 scripts/run_tests.py              # all 16 tests
python3 scripts/run_tests.py --test react_tailwind  # single test
python3 scripts/run_tests.py --json       # JSON output
```

## Project Structure

```
skill-recommender/
├── scripts/
│   ├── detect_stack.py      # Detection engine
│   └── run_tests.py         # Test harness (14 tests)
├── config/
│   ├── npm.json             # NPM package mappings
│   ├── pip.json             # PyPI package mappings
│   ├── go.json              # Go module mappings
│   ├── cargo.json           # Rust crate mappings
│   ├── pom.json             # Maven artifact mappings
│   ├── composer.json        # Composer package mappings
│   ├── pubspec.json         # Dart/Flutter mappings
│   ├── docker.json          # Docker base image mappings
│   ├── files.json           # Filename → signal mappings
│   ├── dirs.json            # Directory → signal mappings
│   └── keywords.json        # User message keywords
├── SKILL.md                 # AI skill behavior guide
├── references/
│   └── stack-catalog.md     # Extended framework catalog
├── LICENSE                  # MIT
├── ROADMAP.md               # Future development roadmap
├── CONTRIBUTING.md          # Contribution guide
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the prioritized development plan across v1.1 (immediate), v1.2 (near-term), and v2.0 (long-term).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.
