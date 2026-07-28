#!/usr/bin/env bash
set -euo pipefail

python -m coverage run -m pytest

python -m coverage report

python -m coverage html

echo "HTML report generated in htmlcov/index.html"
