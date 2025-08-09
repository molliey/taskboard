# Manual Test Guide

This document guides manual verification of core system functionality and frontend-backend integration (non-automated testing).

## Environment Setup
- Docker installed (for running Redis container)
- Node.js (frontend) and Python (backend) installed
- Code path: `${YOUR_PATH}/taskboard`

## Quick Start
The project provides a one-click startup script that includes: Redis container, backend FastAPI, frontend Vite.

```bash
# Execute in project root directory
bash scripts/start.sh
# Terminal will display:
# Access frontend: http://localhost:5173
# Backend: http://localhost:8000
# Redis: localhost:6379
```

To start separately (optional):
- Redis (Docker):
  ```bash
  docker stop taskboard-redis 2>/dev/null
  docker rm taskboard-redis 2>/dev/null
  docker run --name taskboard-redis -p 6379:6379 -d redis:7
  ```
- Backend (FastAPI):
  ```bash
  cd backend
  # If using local virtual environment: source .venv/bin/activate
  uvicorn main:app --reload
  ```
- Frontend (Vite):
  ```bash
  cd frontend
  npm install
  npm run dev
  # Default http://localhost:5173
  ```

## Test Steps
1. Start Redis container
   - Automatically completed through `scripts/start.sh`; or use Docker command above.
   - Expected: `docker ps` shows `taskboard-redis`, Redis listening on 6379.

2. Start backend and frontend
   - Recommended to run `bash scripts/start.sh` directly.
   - Expected:
     - Backend service accessible at `http://localhost:8000/api`.
     - Frontend page accessible at `http://localhost:5173`.

3. Use two browser windows/different user sessions to access the frontend
   - Example: Chrome (Window A) + Safari (Window B), or two Chrome incognito windows.
   - Access `http://localhost:5173`, both should display login/registration page.

4. Register two accounts and log in
   - In Window A register and login User 1 (example: `alice.johnson@company.com`, custom password).
   - In Window B register and login User 2 (example: `bob.smith@company.com`, custom password).
   - Expected: Successful login enters dashboard homepage; login failure shows clear error in form (like "User not found/wrong password").

5. Create project, add members (real-time visible)
   - Window A: Click `+` in left sidebar to create a project (any name).
   - After selecting the project, click `Add Member` button, enter User 2's email (like `bob.smith@company.com`) in popup, set role and submit.
   - Expected:
     - A side: Member added successfully, member list updates without refresh.
     - B side: Through WebSocket push, sidebar shows new project in real-time (no refresh needed).

6. Enter project to create tasks (real-time visible)
   - Still in Window A: Click to enter the created project, in any column (like TO DO) click `+ Create Task`, fill in title, description, due date, assignee (supports selecting members), submit creation.
   - Expected:
     - A side: Task card immediately appears in corresponding column.
     - B side: Through WebSocket push, sees the same task card almost in real-time.

7. Drag tasks (real-time visible)
   - Window A: Drag task from `TO DO` to `IN REVIEW/DONE` etc. columns.
   - Expected:
     - A side: Task appears in target column, disappears from source column.
     - B side: Almost real-time sync sees column changes (no manual refresh needed).

## Expected Results & Checkpoints
- Authentication:
  - Login page displays by default; entering wrong info shows clear error hints (not 401 popup).
  - Successful login gives frontend `access_token`, can request authenticated APIs.
- Projects:
  - Creator is default project member; after adding members, added user's sidebar immediately shows this project.
  - "My Projects" list only shows projects where current logged-in user is a member.
- Board & Tasks:
  - Create/delete/move tasks immediately update local UI, and sync to other logged-in users' pages via WebSocket push.
  - Assignee dropdown/options when creating tasks are actual project members.
- Summary:
  - "Project Members" displays backend-returned members; workload updates with task distribution.

## Common Issues (Troubleshooting)
- Frontend blank page or wrong API domain:
  - Check frontend `VITE_API_BASE_URL`, default `http://localhost:8000/api`.
- Still returns to login page after login:
  - Browser console check network requests; ensure `/api/users/login` returns `{ success: true, access_token, user }`.
- Other side doesn't see real-time changes:
  - Confirm WebSocket `ws://localhost:8000/ws` is connected; backend logs have event broadcasts; browser console has no errors.
- Bob sees no projects:
  - Confirm Bob was added as project member; backend Redis `user:{bob_uid}:projects` should contain target project ID.

## Reference
- Backend API documentation: `backend/API.md`
- API flow test script (sample data and endpoints): `backend/TEST_FLOW.py`