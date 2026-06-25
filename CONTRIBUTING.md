# Contributing to Skill Recommender

Thanks for your interest in contributing! This document covers the basics.

## Development Setup

```bash
git clone https://github.com/Ganesh1110/skill-recommender.git
cd skill-recommender
python3 scripts/run_tests.py    # verify everything works
```

No external dependencies required — the project uses only Python 3.9+ stdlib.

## Project Structure

```
skill-recommender/
├── scripts/
│   ├── detect_stack.py      # Main detection engine
│   └── run_tests.py         # Test harness
├── config/
│   ├── npm.json             # NPM package → signal mappings
│   ├── pip.json             # PyPI package → signal mappings
│   ├── go.json              # Go module → signal mappings
│   ├── cargo.json           # Rust crate → signal mappings
│   ├── pom.json             # Maven artifact → signal mappings
│   ├── composer.json        # Composer package → signal mappings
│   ├── pubspec.json         # Dart/Flutter package → signal mappings
│   ├── docker.json          # Docker base image → signal mappings
│   ├── files.json           # Filename → signal mappings
│   ├── dirs.json            # Directory name → signal mappings
│   └── keywords.json        # User message keyword → signal mappings
├── SKILL.md                 # AI skill behavior guide (not user-facing)
├── references/
│   └── stack-catalog.md     # Extended framework catalog
├── LICENSE
└── CONTRIBUTING.md
```

## How to Add a New Package/Framework

1. Open the relevant JSON file in `config/` (e.g., `npm.json` for an npm package).
2. Add an entry with the package name as key and `[label, category, confidence]` as value.
3. Add a test case in `run_tests.py` to verify detection.
4. Run `python3 scripts/run_tests.py` to confirm all tests pass.

### Category Reference

| Category | Description |
|----------|-------------|
| `framework` | Server-side or full-stack framework |
| `language` | Programming language |
| `ui` | UI component library or CSS framework |
| `database` | Database client, ORM, or cache |
| `ai` | LLM SDK, RAG framework, AI agent |
| `ml` | Machine learning library |
| `data_science` | Data analysis, visualization |
| `data_pipeline` | ETL, orchestration |
| `testing` | Test framework or tool |
| `devops` | Container, CI/CD, infra |
| `infra` | Cloud infra, IaC |
| `ci_cd` | Continuous integration/delivery |
| `cloud` | Cloud provider |
| `api` | API protocol or tool |
| `mobile` | Mobile/cross-platform framework |
| `build_tool` | Bundler, monorepo tool |
| `architecture` | Architectural pattern |
| `deliverable_*` | Document generation (pdf, docx, xlsx, pptx) |

Confidence levels: 5 = config file, 4 = explicit user statement, 3 = file extension, 2 = vague keyword, 1 = single ambiguous word.

## Running Tests

```bash
# All tests
python3 scripts/run_tests.py

# Single test by name
python3 scripts/run_tests.py --test react_tailwind

# JSON output
python3 scripts/run_tests.py --json
```

## Code Style

- No external dependencies — stdlib only.
- Follow existing patterns in `detect_stack.py`.
- Each parser function returns `(signals, errors)`.
- Signal dicts must have: `label`, `category`, `confidence`, `source`.

## Pull Requests

1. Fork the repo and create a branch from `main`.
2. Add tests for any new functionality.
3. Ensure all tests pass: `python3 scripts/run_tests.py`
4. Keep changes focused — one feature or fix per PR.
5. Update this README if adding new config files or categories.

## Reporting Issues

Open an issue at https://github.com/Ganesh1110/skill-recommender/issues with:
- Steps to reproduce
- Expected vs actual behavior
- Sample config file if applicable
