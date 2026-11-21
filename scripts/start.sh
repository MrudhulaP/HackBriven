#!/usr/bin/env bash
set -e

echo "Starting BolKhata Full-Stack Services..."
cd "$(dirname "$0")/.."

# Start backend
(cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

# Start frontend
(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
