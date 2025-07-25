#!/bin/bash

echo "Step 1: Starting Docker container (Postgres)..."
docker compose up -d

echo "Step 2: Activating virtual environment and launching FastAPI backend..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/GENSPARK/genspark-board/backend && source .venv/bin/activate && uvicorn app.main:app --reload"'


echo "Step 3: Launching frontend with Vite..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/GENSPARK/genspark-board/frontend && npm run dev"'

echo "Done. Visit: http://localhost:5173"

