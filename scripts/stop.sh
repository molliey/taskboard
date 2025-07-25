#!/bin/bash

echo "Stopping FastAPI backend..."
pkill -f "uvicorn app.main:app"

echo "Stopping Vite frontend..."
pkill -f "vite"
pkill -f "npm run dev"

echo "Stopping Docker container (Postgres)..."
docker compose stop

echo "All services stopped."

