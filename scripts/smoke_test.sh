#!/usr/bin/env bash
set -euo pipefail

curl -s http://localhost:8000/api/health | jq . || curl -s http://localhost:8000/api/health

echo "Backend is reachable. Open http://localhost:5173 for the frontend."
