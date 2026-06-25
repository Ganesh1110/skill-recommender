#!/usr/bin/env python3
"""
run_tests.py — Evaluates skill-recommender output against known test cases.

Usage:
  python run_tests.py                   # run all tests
  python run_tests.py --test react      # run specific test by name
  python run_tests.py --json            # output results as JSON

Each test case defines:
  - input: simulated user message or config file content
  - input_type: "message" | "package_json" | "requirements" | "dockerfile"
  - expected_skills: skills that MUST appear in recommendations
  - forbidden_skills: skills that must NOT appear
  - expected_priority: {skill: "Essential"|"Helpful"|"Optional"}
"""

import sys
import json
import subprocess
import tempfile
import os
import shutil
from pathlib import Path

DETECT_SCRIPT = Path(__file__).parent / "detect_stack.py"

TEST_CASES = [
    {
        "name": "react_tailwind",
        "description": "React + Tailwind project via package.json",
        "input_type": "package_json",
        "input": json.dumps({
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "next": "^14.0.0",
                "tailwindcss": "^3.3.0",
                "@anthropic-ai/sdk": "^0.20.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "vitest": "^1.0.0"
            }
        }),
        "expected_skills": ["frontend-design", "product-self-knowledge"],
        "forbidden_skills": [],
        "expected_priority": {
            "frontend-design": "Essential",
            "product-self-knowledge": "Essential"
        }
    },
    {
        "name": "python_ml",
        "description": "Python ML project via requirements.txt",
        "input_type": "requirements",
        "input": "\n".join([
            "pandas==2.1.0",
            "numpy==1.25.0",
            "scikit-learn==1.3.0",
            "torch==2.1.0",
            "matplotlib==3.7.0",
            "pytest==7.4.0",
            "anthropic==0.20.0"
        ]),
        "expected_skills": ["product-self-knowledge"],
        "forbidden_skills": ["pptx", "docx"],
        "expected_priority": {
            "product-self-knowledge": "Essential"
        }
    },
    {
        "name": "fullstack_ai",
        "description": "Full-stack AI app with LangChain + Supabase",
        "input_type": "package_json",
        "input": json.dumps({
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "langchain": "^0.2.0",
                "@anthropic-ai/sdk": "^0.20.0",
                "@supabase/supabase-js": "^2.0.0",
                "tailwindcss": "^3.3.0",
                "@trpc/server": "^10.0.0",
                "prisma": "^5.0.0"
            },
            "devDependencies": {
                "playwright": "^1.40.0",
                "turbo": "^1.11.0"
            }
        }),
        "expected_skills": ["frontend-design", "product-self-knowledge"],
        "forbidden_skills": ["pdf-reading"],
        "expected_priority": {
            "frontend-design": "Essential",
            "product-self-knowledge": "Essential"
        }
    },
    {
        "name": "composer_laravel",
        "description": "Laravel PHP project via composer.json",
        "input_type": "composer",
        "input": json.dumps({
            "require": {
                "laravel/framework": "^10.0",
                "symfony/symfony": "^6.0"
            }
        }),
        "expected_skills": ["backend-frameworks"],
        "forbidden_skills": [],
        "expected_priority": {
            "backend-frameworks": "Essential"
        }
    },
    {
        "name": "go_gin",
        "description": "Go service using Gin framework via go.mod",
        "input_type": "go_mod",
        "input": "module github.com/example/project\n\nrequire (\n    github.com/gin-gonic/gin v1.9.0\n)\n",
        "expected_skills": ["backend-frameworks"],
        "forbidden_skills": [],
        "expected_priority": {
            "backend-frameworks": "Essential"
        }
    },
    {
        "name": "document_workflow",
        "description": "Document generation project",
        "input_type": "requirements",
        "input": "\n".join([
            "python-docx==1.1.0",
            "reportlab==4.0.0",
            "openpyxl==3.1.0",
            "pandas==2.1.0",
            "fastapi==0.104.0"
        ]),
        "expected_skills": ["docx", "pdf", "xlsx"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "containerized_microservices",
        "description": "Docker Compose microservices stack",
        "input_type": "dockerfile",
        "input": "\n".join([
            "FROM node:20-alpine",
            "WORKDIR /app",
            "services:",
            "  postgres:",
            "    image: postgres:15",
            "  redis:",
            "    image: redis:7",
            "  nginx:",
            "    image: nginx:alpine"
        ]),
        "expected_skills": [],
        "forbidden_skills": ["pptx", "docx"],
        "expected_priority": {}
    },
    {
        "name": "directory_signals",
        "description": "Project with CI/CD and infra directories detected",
        "input_type": "directory",
        "input": {
            ".github/workflows/ci.yml": "name: CI\non: push\n",
            ".github/workflows/deploy.yml": "name: Deploy\non: push\n",
            "kubernetes/deployment.yaml": "apiVersion: apps/v1\nkind: Deployment\n",
            "helm/values.yaml": "replicaCount: 3\n",
            "Dockerfile": "FROM python:3.12\n",
        },
        "expected_signals": ["GitHub Actions", "Kubernetes", "Helm (K8s)"],
        "expected_skills": ["devops"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "monorepo_multi",
        "description": "Monorepo with web (React) and api (Fastify) sub-projects",
        "input_type": "directory",
        "input": {
            "apps/web/package.json": json.dumps({
                "dependencies": {"react": "^18.0.0", "next": "^14.0.0"}
            }),
            "apps/api/package.json": json.dumps({
                "dependencies": {"fastify": "^4.0.0"}
            }),
            "package.json": json.dumps({
                "private": True,
                "workspaces": ["apps/*"]
            }),
        },
        "expected_signals": ["React", "Next.js", "Fastify", "npm/yarn workspaces (monorepo)"],
        "expected_skills": ["frontend-design", "backend-frameworks"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "node_modules_exclusion",
        "description": "node_modules package.json should NOT be parsed",
        "input_type": "directory",
        "input": {
            "package.json": json.dumps({
                "dependencies": {"react": "^18.0.0"}
            }),
            "node_modules/vue/package.json": json.dumps({
                "dependencies": {"vue": "^3.0.0"}
            }),
            ".git/config": "dummy config",
        },
        "expected_signals": ["React"],
        "forbidden_signals": ["Vue"],
        "expected_skills": ["frontend-design"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "user_message_explicit",
        "description": "User message with explicit framework names",
        "input_type": "user_message",
        "input": "I'm building a React app with Tailwind CSS and I need PostgreSQL",
        "expected_signals": ["React", "Tailwind CSS", "PostgreSQL"],
        "expected_skills": ["frontend-design", "database"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "user_message_vague",
        "description": "User message with vague category descriptions",
        "input_type": "user_message",
        "input": "I need a frontend for a web app",
        "expected_signals": ["Frontend"],
        "expected_skills": [],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "user_message_ml",
        "description": "User message describing ML project",
        "input_type": "user_message",
        "input": "I'm building a machine learning pipeline with Python and FastAPI",
        "expected_signals": ["Python", "FastAPI", "Machine Learning"],
        "expected_skills": ["backend-frameworks"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
    {
        "name": "user_message_with_file",
        "description": "User message combined with a config file",
        "input_type": "user_message_with_file",
        "file_content": json.dumps({
            "dependencies": {"react": "^18.0.0", "next": "^14.0.0"}
        }),
        "message": "I need Docker and PostgreSQL for deployment",
        "expected_signals": ["React", "Next.js", "Docker", "PostgreSQL"],
        "expected_skills": ["frontend-design", "devops", "database"],
        "forbidden_skills": [],
        "expected_priority": {}
    },
]


def run_detection(test_case):
    """Run detect_stack.py against a test case, return parsed JSON result."""

    if test_case["input_type"] == "directory":
        tmp_dir = Path(tempfile.mkdtemp())
        try:
            for filepath, content in test_case["input"].items():
                full_path = tmp_dir / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(DETECT_SCRIPT), str(tmp_dir), "--json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return None, result.stderr
            return json.loads(result.stdout), None
        except Exception as e:
            return None, str(e)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    if test_case["input_type"] == "user_message":
        try:
            result = subprocess.run(
                [sys.executable, str(DETECT_SCRIPT),
                 "--message", test_case["input"], "--json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return None, result.stderr
            return json.loads(result.stdout), None
        except Exception as e:
            return None, str(e)

    if test_case["input_type"] == "user_message_with_file":
        tmp_path = Path(tempfile.mktemp(suffix=".json"))
        try:
            tmp_path.write_text(test_case["file_content"], encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(DETECT_SCRIPT), str(tmp_path),
                 "--message", test_case["message"], "--json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return None, result.stderr
            return json.loads(result.stdout), None
        except Exception as e:
            return None, str(e)
        finally:
            tmp_path.unlink(missing_ok=True)

    suffix_map = {
        "package_json": "package.json",
        "requirements": "requirements.txt",
        "dockerfile": "Dockerfile",
        "composer": "composer.json",
        "pipfile": "Pipfile",
        "go_mod": "go.mod",
        "cargo": "Cargo.toml",
        "pom": "pom.xml",
        "pubspec": "pubspec.yaml",
        "message": "message.txt"
    }
    suffix = suffix_map.get(test_case["input_type"], "input.txt")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    ) as f:
        f.write(test_case["input"])
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, str(DETECT_SCRIPT), tmp_path, "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None, result.stderr
        return json.loads(result.stdout), None
    except Exception as e:
        return None, str(e)
    finally:
        os.unlink(tmp_path)


def score_test(test_case, detection_result):
    """Score a single test case. Returns (passed, score, details)."""
    if not detection_result:
        return False, 0, ["Detection failed — no output"]

    matched_skills = {m["skill"] for m in detection_result.get("skill_matches", [])}
    skill_priority = {
        m["skill"]: m["priority"]
        for m in detection_result.get("skill_matches", [])
    }
    detected_labels = {s["label"] for s in detection_result.get("signals", [])}

    details = []
    score = 100

    # Check expected signals present
    for signal in test_case.get("expected_signals", []):
        if signal in detected_labels:
            details.append(f"  ✅ Expected signal found: {signal}")
        else:
            details.append(f"  ❌ Expected signal MISSING: {signal}")
            score -= 15

    # Check forbidden signals absent
    for signal in test_case.get("forbidden_signals", []):
        if signal not in detected_labels:
            details.append(f"  ✅ Forbidden signal correctly absent: {signal}")
        else:
            details.append(f"  ❌ Forbidden signal incorrectly present: {signal}")
            score -= 15

    # Check expected skills present
    for skill in test_case.get("expected_skills", []):
        if skill in matched_skills:
            details.append(f"  ✅ Expected skill found: {skill}")
        else:
            details.append(f"  ❌ Expected skill MISSING: {skill}")
            score -= 20

    # Check forbidden skills absent
    for skill in test_case.get("forbidden_skills", []):
        if skill not in matched_skills:
            details.append(f"  ✅ Forbidden skill correctly absent: {skill}")
        else:
            details.append(f"  ❌ Forbidden skill incorrectly present: {skill}")
            score -= 15

    # Check priority levels
    for skill, expected_priority in test_case.get("expected_priority", {}).items():
        actual = skill_priority.get(skill)
        if actual == expected_priority:
            details.append(f"  ✅ Priority correct: {skill} = {expected_priority}")
        elif actual:
            details.append(f"  ⚠️  Priority wrong: {skill} = {actual} (expected {expected_priority})")
            score -= 5
        else:
            details.append(f"  ❌ Skill not found for priority check: {skill}")
            score -= 10

    passed = score >= 70
    return passed, max(score, 0), details


def run_all_tests(filter_name=None, as_json=False):
    results = []
    total_score = 0
    passed_count = 0

    tests = TEST_CASES
    if filter_name:
        tests = [t for t in TEST_CASES if t["name"] == filter_name]
        if not tests:
            print(f"No test found with name: {filter_name}")
            sys.exit(1)

    for test in tests:
        detection, error = run_detection(test)
        passed, score, details = score_test(test, detection)
        total_score += score
        if passed:
            passed_count += 1

        result = {
            "name": test["name"],
            "description": test["description"],
            "passed": passed,
            "score": score,
            "details": details,
            "error": error,
            "detected_signals": len(detection.get("signals", [])) if detection else 0,
            "recommended_skills": [m["skill"] for m in detection.get("skill_matches", [])] if detection else []
        }
        results.append(result)

        if not as_json:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"\n{status} [{score}/100] {test['name']}: {test['description']}")
            for d in details:
                print(d)
            if error:
                print(f"  Error: {error}")
            if detection:
                print(f"  Signals detected: {result['detected_signals']}")
                print(f"  Skills matched: {', '.join(result['recommended_skills']) or 'none'}")

    avg_score = total_score / len(tests) if tests else 0

    if as_json:
        print(json.dumps({
            "summary": {
                "total": len(tests),
                "passed": passed_count,
                "failed": len(tests) - passed_count,
                "average_score": round(avg_score, 1)
            },
            "results": results
        }, indent=2))
    else:
        print(f"\n{'═'*50}")
        print(f"Results: {passed_count}/{len(tests)} passed | Average score: {avg_score:.1f}/100")
        print(f"{'═'*50}")


if __name__ == "__main__":
    filter_name = None
    as_json = "--json" in sys.argv

    for arg in sys.argv[1:]:
        if arg == "--test" and sys.argv.index(arg) + 1 < len(sys.argv):
            filter_name = sys.argv[sys.argv.index(arg) + 1]
        elif arg.startswith("--test="):
            filter_name = arg.split("=", 1)[1]

    run_all_tests(filter_name=filter_name, as_json=as_json)