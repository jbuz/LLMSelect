#!/usr/bin/env bash
set -euo pipefail

MODE="check"
if [[ "${1:-}" == "--fix" ]]; then
  MODE="fix"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if ! command -v black >/dev/null 2>&1; then
  echo "black is required but not installed. Install it with 'pip install black'." >&2
  exit 1
fi

if ! command -v flake8 >/dev/null 2>&1; then
  echo "flake8 is required but not installed. Install it with 'pip install flake8'." >&2
  exit 1
fi

if [[ "${MODE}" == "fix" ]]; then
  echo "Running black to format Python files..."
  black llmselect tests
else
  echo "Checking Python formatting with black..."
  black --check --diff llmselect tests
fi

echo "Running flake8 lint checks..."
flake8 llmselect tests

echo "Python lint checks complete."
