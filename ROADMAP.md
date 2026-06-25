# Roadmap

Prioritised roadmap for the Skill Recommender project.

---

## v1.1 — Immediate (Completed)

- [x] **Global cache directory** — Cache moved from target directory to `~/.cache/skill-recommender/` to avoid cluttering repos.
- [x] **`--exclude` flag** — Users can now exclude specific directories from scanning.
- [x] **Enhanced conflict detection** — Covers database, build tool, UI library, E2E framework, and CI/CD conflicts (not just frontend frameworks).
- [x] **Improved user-message keywords** — Added 150+ new keywords (dashboard, auth, analytics, etc.) for better coverage.
- [x] **`--explain` flag** — Shows why each skill was recommended (which signals matched which triggers).
- [x] **`--no-cache` option** — Skip reading/writing the cache file.
- [x] **Versioning** — Added `__version__` and `--version` flag.

---

## v1.2 — Near-Term

- [ ] **Config file validation** — Validate user-supplied config files against schemas (malformed JSON, TOML, YAML) with clear error messages.
- [ ] **AST-based parsing** — Use `ast` module (Python) and tree-sitter (JS/TS) to detect actual framework usage in source code, not just manifest/import patterns.
- [ ] **More package managers** — Add parsers for Conda (`environment.yml`), NuGet (`packages.config`), Rebar3 (`rebar.config`), Shards (`shard.yml`).
- [ ] **Cloud SDK detection** — Map packages like `boto3`, `@google-cloud/*`, `azure-*` to cloud-provider signals.
- [ ] **`--explain` in JSON output** — Include explanation data in JSON output for programmatic consumption.
- [ ] **Cache invalidation on source changes** — Extend fingerprint to include source files that affect import-pattern detection.
- [ ] **Per-sub-project output** — In monorepo mode, show which sub-projects contribute which signals.
- [ ] **Synonym support in user messages** — Match common abbreviations and synonyms (e.g., "k8s" → "kubernetes", "ts" → "typescript").

---

## v2.0 — Long-Term

- [ ] **Plugin architecture** — Allow third-party parsers and signal providers via Python entry points (`skill_recommender.parsers`). Decouple parsers into separate modules.
- [ ] **Interactive mode** — Ask clarifying questions when ambiguity is high (conflicting frameworks, vague messages).
- [ ] **Claude Desktop integration** — Install skills automatically via the Claude Desktop API instead of printing `curl` commands.
- [ ] **Full-source analysis** — Analyze entire source tree (not just first 10 lines) using AST for accurate usage detection.
- [ ] **Watch mode** — Continuous directory scanning for live updates during development.
- [ ] **Web UI / VS Code extension** — Visual stack analysis and skill recommendation explorer.
- [ ] **Performance benchmarking** — Track scan times, cache hit rates, and memory usage across repository sizes.
- [ ] **Fuzz testing** — Property-based tests that randomly mutate inputs to ensure parsers never crash.
- [ ] **Open-source CI** — GitHub Actions for automated testing on every PR across Python 3.9–3.13.
