# 📋 TaskBoard - Real-time Collaborative Task Management

A modern task management platform with real-time collaboration, built with FastAPI and React.

## ✨ Features

- **Real-time Collaboration**: Live updates via WebSocket
- **Kanban Board**: Drag-and-drop task management (TO DO → IN PROGRESS → IN REVIEW → DONE)
- **Project Management**: Multi-project support with team members
- **User Authentication**: JWT-based secure authentication
- **Task Operations**: Complete CRUD with assignees, due dates, and descriptions

## 🛠️ Tech Stack

**Backend**: FastAPI, Redis, WebSocket, JWT
**Frontend**: React 19, Vite, CSS3
**Infrastructure**: Docker (Redis), Python 3.8+, Node.js 18+

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
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login
- `GET /api/users/me` - Current user info

### Projects
- `GET /api/projects/my-projects` - User's projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/members` - Project members
- `GET /api/projects/{id}/board` - Kanban board

### Tasks
- `POST /api/projects/{id}/tasks` - Create task
- `PUT /api/projects/{id}/tasks/{taskId}` - Update task
- `PUT /api/projects/{id}/tasks/{taskId}/move` - Move task
- `DELETE /api/projects/{id}/tasks/{taskId}` - Delete task

### WebSocket
- **URL**: `ws://localhost:8000/ws?user_id={userId}`
- **Events**: `task_created`, `task_updated`, `task_moved`, `task_deleted`

## 🧪 Testing

### API Tests
```bash
cd backend
python test_api_flow.py --base-url http://localhost:8000 --verbose
```

### Manual Testing
- Multiple browser windows for real-time collaboration
- Test files: `test-user-auth.html`, `test-project-switching.html`
- Documentation: `backend/docs/MANUAL_TEST.md`

## 🏗️ Architecture

**Data Flow**: Frontend → FastAPI → Redis → WebSocket → Frontend

**Storage**: Redis as primary data store with key-value pairs for users, projects, and tasks

**Real-time**: WebSocket connections broadcast events to all connected clients

## 🚀 Production Deployment

- Use Redis cluster for high availability
- Configure CORS for production domains
- Set up SSL/TLS certificates
- Use process managers (PM2, supervisor)
- Configure reverse proxy (Nginx)