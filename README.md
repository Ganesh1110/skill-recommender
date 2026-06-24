# Skill Recommender

A lightweight project that analyzes a software repository or config file to detect the tech stack and recommend the best installed skills for the project.

## What it does

- Detects languages, frameworks, infrastructure, and AI-related libraries from project files.
- Maps detected stack signals to installed skill recommendations.
- Flags conflicts, missing skill coverage, and provides confidence-based output.
- Supports structured JSON output for automation and pretty CLI output for humans.

## Why this matters

This repo is built for anyone who wants to:

- analyze a codebase and understand its stack automatically
- recommend the right skill or workflow for an AI assistant
- validate skill coverage for frontend, backend, data, cloud, and AI use cases
- make tech stack detection deterministic and repeatable

## Included files

- `scripts/detect_stack.py` — the detection engine that parses config files, package manifests, and directory structures
- `scripts/run_tests.py` — test harness for validating the detector against example inputs
- `SKILL.md` — project metadata, usage guidance, and the catalog of known stack signals
- `references/stack-catalog.md` — extended stack catalog for less common frameworks and platform signals

## How to use

### Detect the stack

```bash
python scripts/detect_stack.py <file_or_directory>
```

Example:

```bash
python scripts/detect_stack.py package.json
```

### Get machine-readable JSON output

```bash
python scripts/detect_stack.py <file_or_directory> --json
```

### Run tests

```bash
python scripts/run_tests.py
```

## Example scenarios

- `package.json` analysis for React/Next/Tailwind projects
- `requirements.txt` analysis for Python ML or data workflows
- `Dockerfile` or `docker-compose` detection for deployment and infra stacks
- `go.mod`, `Cargo.toml`, `composer.json` for language-specific ecosystem signals

## Shareable story for LinkedIn / Reddit

This project is a simple, practical tool for making AI-driven skill recommendations more reliable. It is especially useful when you want to:

- explain how to automatically choose the right assistant skill for a given repo
- demonstrate deterministic stack detection from config files
- show a reusable pattern for skill-aware tooling in AI-powered developer workflows

## Notes

- The repository is intentionally small and focused on deterministic detection.
- `SKILL.md` is the canonical skill registry and usage guide for this project.
- `references/stack-catalog.md` expands coverage for niche or enterprise frameworks.

---

If you want, I can also help craft a ready-to-post LinkedIn or Reddit announcement text for this project.
