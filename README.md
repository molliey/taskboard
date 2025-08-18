# 📋 TASKBOARD - Real-time Collaborative Task Management

A collaborative task board application enabling project, team, and task management with real-time updates.

<img width="1911" height="1072" alt="Image" src="https://github.com/user-attachments/assets/03e2a1bb-0e4d-4dc5-87dd-595b13947022" />

## ✨ Features

- **Project Management**: Multi-project support with team members
- **Kanban Board**: Drag-and-drop task management (TO DO → IN PROGRESS → IN REVIEW → DONE)
- **Task Operations**: Complete CRUD with assignees, due dates, and descriptions
- **User Authentication**: JWT-based secure authentication
- **Real-time Collaboration**: Live updates via WebSocket

## 🛠️ Tech Stack

- **Backend**: FastAPI, Redis, RESTful API, WebSocket, JWT
- **Frontend**: React, Vite, CSS3

## 🏗️ Architecture

- **Data Flow**: Frontend → FastAPI → Redis → WebSocket → Frontend
- **Storage**: Redis as primary data store with key-value pairs for users, projects, and tasks
- **Real-time**: WebSocket connections broadcast events to all connected clients

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Docker

### Setup & Run

1. **Start Redis**
```bash
docker run --name taskboard-redis -p 6379:6379 -d redis:7
```

2. **Backend** (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

3. **Frontend** (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
taskboard/
├── backend/                # FastAPI application
│   ├── api/               # API endpoints (users, projects, tasks)
│   ├── main.py           # Application entry point
│   ├── models.py         # Data models
│   ├── redis_client.py   # Redis operations
│   └── ws.py             # WebSocket handler
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API & auth services
│   │   └── api/          # API client
│   └── package.json
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/users/register` - user registration
- `POST /api/users/login` - user login

### Projects
- `POST /api/projects/` - create project
- `DELETE /api/projects/{project_id}` - delete project

### Tasks
- `POST /api/projects/{id}/tasks` - create task
- `PUT /api/projects/{id}/tasks/{taskId}` - update task
- `PUT /api/projects/{id}/tasks/{taskId}/move` - move task
- `DELETE /api/projects/{id}/tasks/{taskId}` - delete task

### WebSocket
- **URL**: `ws://localhost:8000/ws?user_id={userId}`
- **Events**: `task_created`, `task_updated`, `task_moved`, `task_deleted`, `member_added`, `member_removed`, `project_updated`

## 🧪 Testing

### API Tests
```bash
cd backend
python test_api_flow.py --base-url http://localhost:8000 --verbose
```

### Manual Testing
- Test files: `test-user-auth.html`, `test-project-switching.html`
- Documentation: `backend/docs/MANUAL_TEST.md`

## 🎥 Demo Videos

### User Register & Login
https://vimeo.com/1110828095

### Platform Overview
https://vimeo.com/1110828115

### Real-time Collaboration
https://vimeo.com/1110828130

