#!/usr/bin/env bash
# Lance le site EcoSort (backend API + frontend) sur http://localhost:8000
set -e
cd "$(dirname "$0")"
python -m uvicorn backend.main:app --reload --port 8000
