# Manual Test Guide

This document guides manual verification of core system functionality and frontend-backend integration (non-automated testing).

## Environment Setup
- Docker installed (for running Redis container)
- Node.js (frontend) and Python (backend) installed
- Code path: `${YOUR_PATH}/taskboard`

## Standard Startup

### 1. Start Redis Container
```bash
docker run --name taskboard-redis -p 6379:6379 -d redis:7

# If container already exists, restart it:
# docker stop taskboard-redis 2>/dev/null
# docker rm taskboard-redis 2>/dev/null
# docker run --name taskboard-redis -p 6379:6379 -d redis:7
```

### 2. Start Backend (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Start Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

## Test Steps

### 1. Verify Services
- **Redis**: `docker ps` shows `taskboard-redis` container running on port 6379
- **Backend**: http://localhost:8000 accessible, API docs at http://localhost:8000/docs
- **Frontend**: http://localhost:5173 displays login/registration page

### 2. Multi-User Setup
- Open two browser windows (Chrome + Safari, or two incognito windows)
- Both should access `http://localhost:5173` and show login/registration page

### 3. User Registration & Login
- **Window A**: Register and login User 1 (e.g., `jack@gmail.com`)
- **Window B**: Register and login User 2 (e.g., `alice@gmail.com`)
- **Expected**: Successful login enters dashboard; login failure shows clear error messages

### 4. Project Creation & Member Management (Real-time)
- **Window A**: Click `+` in left sidebar to create a project
- After selecting project, click `+ Add Member` button
- Enter User 2's email (`bob.smith@company.com`) and set role (default: "Developer")
- **Expected**:
  - Window A: Member added successfully, member list updates without refresh
  - Window B: Through WebSocket, sidebar shows new project in real-time

### 5. Task Creation (Real-time)
- **Window A**: In any column (e.g., TO DO), click `+ Create Task`
- Fill in title, description, due date, assignee (select from project members)
- **Expected**:
  - Window A: Task card appears immediately in corresponding column
  - Window B: Task appears almost instantly via WebSocket

### 6. Task Movement (Real-time)
- **Window A**: Drag task from `TO DO` to `IN PROGRESS` or `DONE` columns
- **Expected**:
  - Window A: Task moves to target column, disappears from source
  - Window B: Column changes sync in real-time without manual refresh

### 7. Task Assignment Testing
- Edit existing task and change assignee from one user to "Unassigned" or another user
- **Expected**: Assignment changes reflect immediately on both windows

## Expected Results & Checkpoints

### Authentication
- Login page displays by default
- Wrong credentials show clear error messages (not 401 popup)
- Successful login provides frontend `access_token` for authenticated API requests

### Projects
- Project creator is automatically a member
- After adding members, new member's sidebar immediately shows the project
- "My Projects" list only displays projects where current user is a member

### Board & Tasks
- Create/delete/move tasks update local UI immediately
- Changes sync to other logged-in users via WebSocket
- Assignee dropdown shows actual project members
- Task assignment switching (including "Unassigned") works correctly

### Real-time Features
- WebSocket connection maintains live sync between users
- Events broadcast to all connected clients without refresh

## Common Issues (Troubleshooting)

### Frontend Issues
- **Blank page**: Check `VITE_API_BASE_URL` in frontend config (default: `http://localhost:8000/api`)
- **Login redirect loops**: Browser console check network requests; ensure `/api/users/login` returns `{ success: true, access_token, user }`
- **Add Member white screen**: Check browser console for JavaScript errors (fixed in recent updates)

### Real-time Issues
- **No real-time updates**: Confirm WebSocket `ws://localhost:8000/ws` is connected; check backend logs for event broadcasts; browser console for errors
- **User doesn't see shared projects**: Confirm user was added as project member; backend Redis should contain project associations

### Task Assignment Issues
- **Cannot switch to "Unassigned"**: This issue has been fixed in recent updates; ensure latest code is running
- **Assignee dropdown empty**: Verify project has members added; check browser network tab for member API calls

## Additional Test Resources

### Manual Test Files
- **User Authentication**: Open `test-user-auth.html` in browser for auth flow testing
- **Project Switching**: Open `test-project-switching.html` in browser for project management testing
- **WebSocket Testing**: Open `test_websocket.html` in browser or run `python test_ws.py`

### API Testing
- **Automated tests**: `cd backend && python test_api_flow.py --base-url http://localhost:8000 --verbose`
- **API Documentation**: http://localhost:8000/docs (auto-generated FastAPI docs)

## Reference
- Backend API documentation: `backend/docs/API.md`
- API test script: `backend/test_api_flow.py`
- Test flow description: `backend/docs/TEST_FLOW.md`