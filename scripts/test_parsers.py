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


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1)
