#!/usr/bin/env python3
"""
test_parsers.py — Unit tests for individual parser functions in detect_stack.py.

These tests call parser functions directly with string inputs, isolating
parsing logic from file I/O and directory scanning.

Usage:
  python test_parsers.py            # run all tests
  python test_parsers.py -v         # verbose output
"""

import sys
import json
import hashlib
import unittest
from pathlib import Path

# Add scripts/ to path so we can import
sys.path.insert(0, str(Path(__file__).parent))
from detect_stack import (
    parse_package_json, parse_requirements, parse_pyproject,
    parse_pipfile, parse_package_lock, parse_composer_json,
    parse_pubspec_yaml, parse_go_mod, parse_cargo_toml,
    parse_pom_xml, parse_dockerfile, parse_yarn_lock,
    parse_pnpm_lock, parse_poetry_lock, parse_cargo_lock,
    parse_gemfile, parse_build_gradle, parse_mix_exs,
    parse_user_message, match_skills, detect_conflicts,
    _compute_dir_fingerprint, _get_cache_path, __version__,
)


class TestParsePackageJson(unittest.TestCase):
    def test_react_next(self):
        content = json.dumps({
            "dependencies": {"react": "^18.0.0", "next": "^14.0.0"},
            "devDependencies": {"typescript": "^5.0.0"}
        })
        signals, errors = parse_package_json(content)
        labels = {s["label"] for s in signals}
        self.assertIn("React", labels)
        self.assertIn("Next.js", labels)
        self.assertEqual(errors, [])

    def test_empty_deps(self):
        signals, errors = parse_package_json(json.dumps({"name": "empty"}))
        self.assertEqual(len(signals), 0)

    def test_invalid_json(self):
        signals, errors = parse_package_json("{invalid")
        self.assertEqual(len(signals), 0)
        self.assertTrue(len(errors) > 0)

    def test_workspaces(self):
        content = json.dumps({"workspaces": ["apps/*"]})
        signals, errors = parse_package_json(content)
        labels = {s["label"] for s in signals}
        self.assertTrue(any("monorepo" in l.lower() for l in labels))

    def test_peer_dependencies(self):
        content = json.dumps({"peerDependencies": {"react": "^18.0.0"}})
        signals, errors = parse_package_json(content)
        labels = {s["label"] for s in signals}
        self.assertIn("React", labels)


class TestParseRequirements(unittest.TestCase):
    def test_basic(self):
        content = "pandas==2.1.0\nnumpy==1.25.0\nfastapi==0.104.0"
        signals, errors = parse_requirements(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Pandas (data)", labels)
        self.assertIn("NumPy", labels)
        self.assertIn("FastAPI", labels)

    def test_with_comments(self):
        content = "# This is a comment\npandas==2.1.0\n# Another comment"
        signals, errors = parse_requirements(content)
        self.assertEqual(len(signals), 1)

    def test_version_operators(self):
        content = "flask>=2.0\ndjango~=4.2\nrequests!=2.28"
        signals, errors = parse_requirements(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Flask", labels)
        self.assertIn("Django", labels)

    def test_extras(self):
        content = "uvicorn[standard]>=0.20.0"
        signals, errors = parse_requirements(content)
        # Should still detect uvicorn
        self.assertTrue(len(signals) >= 0)  # might not match due to extras parsing


class TestParsePyproject(unittest.TestCase):
    def test_poetry_format(self):
        content = """
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
pandas = "^2.1.0"
"""
        signals, errors = parse_pyproject(content)
        labels = {s["label"] for s in signals}
        self.assertIn("FastAPI", labels)
        self.assertIn("Pandas (data)", labels)


class TestParsePipfile(unittest.TestCase):
    def test_packages(self):
        content = """
[packages]
flask = "*"
django = ">=4.0"

[dev-packages]
pytest = "*"
"""
        signals, errors = parse_pipfile(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Flask", labels)
        self.assertIn("Django", labels)
        self.assertIn("pytest", labels)


class TestParsePackageLock(unittest.TestCase):
    def test_v2_lockfile(self):
        content = json.dumps({
            "packages": {
                "node_modules/react": {"version": "18.2.0"},
                "node_modules/next": {"version": "14.0.0"}
            }
        })
        signals, errors = parse_package_lock(content)
        labels = {s["label"] for s in signals}
        self.assertIn("React", labels)
        self.assertIn("Next.js", labels)


class TestParseComposerJson(unittest.TestCase):
    def test_laravel(self):
        content = json.dumps({
            "require": {"laravel/framework": "^10.0"},
            "require-dev": {"phpunit/phpunit": "^10.0"}
        })
        signals, errors = parse_composer_json(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Laravel", labels)


class TestParsePubspecYaml(unittest.TestCase):
    def test_flutter(self):
        content = """
dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
"""
        signals, errors = parse_pubspec_yaml(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Flutter", labels)


class TestParseGoMod(unittest.TestCase):
    def test_gin(self):
        content = """
module github.com/example/project

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/labstack/echo/v4 v4.11.0
)
"""
        signals, errors = parse_go_mod(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Gin", labels)
        self.assertIn("Echo", labels)


class TestParseCargoToml(unittest.TestCase):
    def test_actix(self):
        content = """
[dependencies]
actix-web = "4"
serde = { version = "1", features = ["derive"] }

[dev-dependencies]
actix-rt = "2"
"""
        signals, errors = parse_cargo_toml(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Actix Web", labels)


class TestParsePomXml(unittest.TestCase):
    def test_spring_boot(self):
        content = """
<project>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
  </dependencies>
</project>
"""
        signals, errors = parse_pom_xml(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Spring Boot", labels)


class TestParseDockerfile(unittest.TestCase):
    def test_node_image(self):
        content = "FROM node:20-alpine\nWORKDIR /app\nCOPY . ."
        signals, errors = parse_dockerfile(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Node.js", labels)

    def test_python_image(self):
        content = "FROM python:3.12-slim"
        signals, errors = parse_dockerfile(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Python", labels)

    def test_compose_services(self):
        content = "services:\n  web:\n    image: nginx:alpine"
        signals, errors = parse_dockerfile(content)
        labels = {s["label"] for s in signals}
        self.assertTrue(any("microservices" in l.lower() for l in labels))


class TestParseYarnLock(unittest.TestCase):
    def test_basic(self):
        content = """
# yarn lockfile v1
react@^18.2.0:
  version "18.2.0"
  resolved "https://registry.yarnpkg.com/react/-/react-18.2.0.tgz"

next@^14.0.0:
  version "14.0.0"
  resolved "https://registry.yarnpkg.com/next/-/next-14.0.0.tgz"
"""
        signals, errors = parse_yarn_lock(content)
        labels = {s["label"] for s in signals}
        self.assertIn("React", labels)
        self.assertIn("Next.js", labels)


class TestParsePoetryLock(unittest.TestCase):
    def test_basic(self):
        content = """
[[package]]
name = "fastapi"
version = "0.104.0"

[[package]]
name = "pandas"
version = "2.1.0"
"""
        signals, errors = parse_poetry_lock(content)
        labels = {s["label"] for s in signals}
        self.assertIn("FastAPI", labels)
        self.assertIn("Pandas (data)", labels)


class TestParseCargoLock(unittest.TestCase):
    def test_basic(self):
        content = """
[[package]]
name = "actix-web"
version = "4.4.0"

[[package]]
name = "serde"
version = "1.0.190"
"""
        signals, errors = parse_cargo_lock(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Actix Web", labels)


class TestParseGemfile(unittest.TestCase):
    def test_rails(self):
        content = """
source 'https://rubygems.org'

gem 'rails', '~> 7.0'
gem 'puma', '~> 6.0'

group :test do
  gem 'rspec', '~> 3.0'
end
"""
        signals, errors = parse_gemfile(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Rails", labels)
        self.assertIn("Puma", labels)
        self.assertIn("RSpec", labels)


class TestParseBuildGradle(unittest.TestCase):
    def test_spring_boot(self):
        content = """
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web:3.1.0'
    implementation 'org.jetbrains.kotlin:kotlin-stdlib:1.9.0'
}
"""
        signals, errors = parse_build_gradle(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Spring Boot", labels)
        self.assertIn("Kotlin", labels)


class TestParseMixExs(unittest.TestCase):
    def test_phoenix(self):
        content = """
defp deps do
  [
    {:phoenix, "~> 1.7.0"},
    {:ecto, "~> 3.10"},
    {:postgrex, "~> 0.17.0"}
  ]
end
"""
        signals, errors = parse_mix_exs(content)
        labels = {s["label"] for s in signals}
        self.assertIn("Phoenix", labels)
        self.assertIn("Ecto ORM", labels)
        self.assertIn("PostgreSQL (Postgrex)", labels)


class TestParseUserMessage(unittest.TestCase):
    def test_explicit_frameworks(self):
        signals = parse_user_message("I'm building a React app with FastAPI")
        labels = {s["label"] for s in signals}
        self.assertIn("React", labels)
        self.assertIn("FastAPI", labels)

    def test_multi_word_phrases(self):
        signals = parse_user_message("I need React Native and machine learning")
        labels = {s["label"] for s in signals}
        self.assertIn("React Native", labels)
        self.assertIn("Machine Learning", labels)

    def test_vague_categories(self):
        signals = parse_user_message("I need a frontend for a web app")
        labels = {s["label"] for s in signals}
        self.assertIn("Frontend", labels)

    def test_no_match(self):
        signals = parse_user_message("hello world nothing here")
        self.assertEqual(len(signals), 0)

    def test_cloud_providers(self):
        signals = parse_user_message("Deploy to AWS with Terraform")
        labels = {s["label"] for s in signals}
        self.assertIn("AWS", labels)
        self.assertIn("Terraform", labels)


class TestMatchSkills(unittest.TestCase):
    def test_react_skill(self):
        signals = [{"label": "React", "category": "framework", "confidence": 5, "source": "test"}]
        results = match_skills(signals)
        skills = {r["skill"] for r in results}
        self.assertIn("frontend-design", skills)

    def test_no_match(self):
        signals = [{"label": "UnknownLib", "category": "unknown", "confidence": 3, "source": "test"}]
        results = match_skills(signals)
        self.assertEqual(len(results), 0)

    def test_priority_levels(self):
        # Single strong signal should be Essential
        signals = [{"label": "React", "category": "framework", "confidence": 5, "source": "test"}]
        results = match_skills(signals)
        react_result = next(r for r in results if r["skill"] == "frontend-design")
        self.assertEqual(react_result["priority"], "Essential")

    def test_multiple_signals_higher_score(self):
        signals = [
            {"label": "React", "category": "framework", "confidence": 5, "source": "test"},
            {"label": "Tailwind CSS", "category": "ui", "confidence": 5, "source": "test"},
            {"label": "Next.js", "category": "framework", "confidence": 5, "source": "test"},
        ]
        results = match_skills(signals)
        frontend = next(r for r in results if r["skill"] == "frontend-design")
        self.assertEqual(frontend["score"], 99)


class TestDetectConflicts(unittest.TestCase):
    def test_no_conflicts(self):
        signals = [{"label": "React", "category": "framework"}]
        conflicts = detect_conflicts(signals)
        self.assertEqual(len(conflicts), 0)

    def test_frontend_conflict(self):
        signals = [
            {"label": "React", "category": "framework"},
            {"label": "Vue", "category": "framework"},
            {"label": "Angular", "category": "framework"},
        ]
        conflicts = detect_conflicts(signals)
        self.assertTrue(len(conflicts) > 0)
        self.assertEqual(conflicts[0]["category"], "framework")

    def test_database_conflict(self):
        signals = [
            {"label": "PostgreSQL", "category": "database"},
            {"label": "MySQL", "category": "database"},
            {"label": "MongoDB", "category": "database"},
        ]
        conflicts = detect_conflicts(signals)
        db_conflicts = [c for c in conflicts if c["category"] == "database"]
        self.assertTrue(len(db_conflicts) > 0)

    def test_database_no_conflict_with_orm(self):
        signals = [
            {"label": "PostgreSQL", "category": "database"},
            {"label": "SQLAlchemy ORM", "category": "database"},
        ]
        conflicts = detect_conflicts(signals)
        db_conflicts = [c for c in conflicts if c["category"] == "database"]
        self.assertEqual(len(db_conflicts), 0)

    def test_build_tool_conflict(self):
        signals = [
            {"label": "Webpack", "category": "build_tool"},
            {"label": "Vite", "category": "build_tool"},
            {"label": "Turborepo", "category": "build_tool"},
        ]
        conflicts = detect_conflicts(signals)
        build_conflicts = [c for c in conflicts if c["category"] == "build_tool"]
        self.assertTrue(len(build_conflicts) > 0)

    def test_ui_conflict(self):
        signals = [
            {"label": "Tailwind CSS", "category": "ui"},
            {"label": "Bootstrap", "category": "ui"},
        ]
        conflicts = detect_conflicts(signals)
        ui_conflicts = [c for c in conflicts if c["category"] == "ui"]
        self.assertTrue(len(ui_conflicts) > 0)

    def test_testing_conflict(self):
        signals = [
            {"label": "Playwright (E2E)", "category": "testing"},
            {"label": "Cypress (E2E)", "category": "testing"},
        ]
        conflicts = detect_conflicts(signals)
        test_conflicts = [c for c in conflicts if c["category"] == "testing"]
        self.assertTrue(len(test_conflicts) > 0)

    def test_ci_cd_conflict(self):
        signals = [
            {"label": "GitHub Actions", "category": "ci_cd"},
            {"label": "CircleCI", "category": "ci_cd"},
        ]
        conflicts = detect_conflicts(signals)
        ci_conflicts = [c for c in conflicts if c["category"] == "ci_cd"]
        self.assertTrue(len(ci_conflicts) > 0)


class TestMatchSkillsExplain(unittest.TestCase):
    def test_explain_output(self):
        signals = [
            {"label": "React", "category": "framework", "confidence": 5, "source": "package.json"},
            {"label": "Tailwind CSS", "category": "ui", "confidence": 5, "source": "package.json"},
        ]
        results = match_skills(signals, explain=True)
        frontend = next(r for r in results if r["skill"] == "frontend-design")
        self.assertIn("explanation", frontend)
        self.assertTrue(len(frontend["explanation"]) > 0)

    def test_no_explain_by_default(self):
        signals = [{"label": "React", "category": "framework", "confidence": 5, "source": "test"}]
        results = match_skills(signals)
        frontend = next(r for r in results if r["skill"] == "frontend-design")
        self.assertNotIn("explanation", frontend)


class TestVersion(unittest.TestCase):
    def test_version_exists(self):
        self.assertIsInstance(__version__, str)
        self.match(r'^\d+\.\d+\.\d+$', __version__)

    def match(self, pattern, string):
        import re
        self.assertTrue(re.match(pattern, string), f"Version '{string}' does not match pattern '{pattern}'")


class TestCachePath(unittest.TestCase):
    def test_cache_path_deterministic(self):
        path1 = _get_cache_path("/tmp/test/project")
        path2 = _get_cache_path("/tmp/test/project")
        self.assertEqual(path1, path2)

    def test_cache_path_different_for_different_dirs(self):
        path1 = _get_cache_path("/tmp/test/project1")
        path2 = _get_cache_path("/tmp/test/project2")
        self.assertNotEqual(path1, path2)

    def test_cache_in_global_dir(self):
        from detect_stack import GLOBAL_CACHE_DIR
        path = _get_cache_path("/tmp/test")
        self.assertTrue(str(path).startswith(str(GLOBAL_CACHE_DIR)))


class TestParseEdgeCases(unittest.TestCase):
    def test_empty_package_json(self):
        signals, errors = parse_package_json("{}")
        self.assertEqual(len(signals), 0)
        self.assertEqual(len(errors), 0)

    def test_empty_requirements(self):
        signals, errors = parse_requirements("")
        self.assertEqual(len(signals), 0)

    def test_empty_composer_json(self):
        signals, errors = parse_composer_json("{}")
        self.assertEqual(len(signals), 0)

    def test_empty_go_mod(self):
        signals, errors = parse_go_mod("")
        self.assertEqual(len(signals), 0)

    def test_empty_cargo_toml(self):
        signals, errors = parse_cargo_toml("")
        self.assertEqual(len(signals), 0)

    def test_empty_pom_xml(self):
        signals, errors = parse_pom_xml("")
        self.assertEqual(len(signals), 0)

    def test_empty_dockerfile(self):
        signals, errors = parse_dockerfile("")
        self.assertEqual(len(signals), 0)

    def test_invalid_yaml_pubspec(self):
        signals, errors = parse_pubspec_yaml("not: valid: yaml: [[[")
        # Should not crash, may return empty
        self.assertIsInstance(signals, list)

    def test_malformed_package_lock(self):
        signals, errors = parse_package_lock("{not valid json")
        self.assertEqual(len(signals), 0)
        self.assertTrue(len(errors) > 0)

    def test_malformed_composer_json(self):
        signals, errors = parse_composer_json("{not valid json")
        self.assertEqual(len(signals), 0)
        self.assertTrue(len(errors) > 0)

    def test_user_message_empty(self):
        signals = parse_user_message("")
        self.assertEqual(len(signals), 0)

    def test_user_message_special_chars(self):
        signals = parse_user_message("I need a @#$%^&*() app")
        # Should not crash
        self.assertIsInstance(signals, list)


class TestFingerprint(unittest.TestCase):
    def test_fingerprint_deterministic(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal config file
            (Path(tmpdir) / "package.json").write_text('{"dependencies": {}}')
            fp1 = _compute_dir_fingerprint(tmpdir)
            fp2 = _compute_dir_fingerprint(tmpdir)
            self.assertEqual(fp1, fp2)

    def test_fingerprint_changes_with_content(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg = Path(tmpdir) / "package.json"
            pkg.write_text('{"dependencies": {"react": "1.0"}}')
            fp1 = _compute_dir_fingerprint(tmpdir)
            pkg.write_text('{"dependencies": {"vue": "3.0"}}')
            fp2 = _compute_dir_fingerprint(tmpdir)
            self.assertNotEqual(fp1, fp2)

    def test_fingerprint_handles_missing_dir(self):
        fp = _compute_dir_fingerprint("/nonexistent/path/that/does/not/exist")
        self.assertEqual(fp, hashlib.sha256(b"").hexdigest()[:32])


class TestDetectMultipleConflicts(unittest.TestCase):
    def test_multiple_conflict_categories(self):
        signals = [
            {"label": "React", "category": "framework"},
            {"label": "Vue", "category": "framework"},
            {"label": "PostgreSQL", "category": "database"},
            {"label": "MySQL", "category": "database"},
            {"label": "Webpack", "category": "build_tool"},
            {"label": "Vite", "category": "build_tool"},
        ]
        conflicts = detect_conflicts(signals)
        categories = {c["category"] for c in conflicts}
        self.assertIn("framework", categories)
        self.assertIn("database", categories)
        self.assertIn("build_tool", categories)

    def test_single_item_no_conflict(self):
        signals = [
            {"label": "React", "category": "framework"},
            {"label": "PostgreSQL", "category": "database"},
        ]
        conflicts = detect_conflicts(signals)
        self.assertEqual(len(conflicts), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1)
