# 📋 TaskBoard - Real-time Collaborative Task Management Platform

A modern, real-time task management platform built with FastAPI and React, featuring WebSocket-powered live collaboration and Redis-based data storage.

## ✨ Features

### 🚀 Core Features
- **Real-time Collaboration**: Live updates across all connected users via WebSocket
- **Project Management**: Create, edit, and manage multiple projects with team members
- **Kanban Board**: Drag-and-drop task management with customizable columns (TO DO → IN PROGRESS → IN REVIEW → DONE)
- **Task Operations**: Complete CRUD functionality for tasks with rich metadata
- **Team Management**: Add/remove project members with role-based access
- **User Authentication**: Secure JWT-based authentication system
- **Workload Analytics**: Visual task distribution and team workload insights

### 🔄 Real-time Features
- **Live Task Updates**: See tasks created, updated, and moved in real-time
- **Project Synchronization**: Instant project updates across all team members
- **Member Activity**: Real-time member addition/removal notifications
- **Board State Sync**: Synchronized board state for all connected users

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **Redis** - In-memory data structure store for fast data access
- **WebSocket** - Real-time bidirectional communication
- **JWT** - JSON Web Token authentication
- **Python 3.8+** - Backend runtime
- **Uvicorn** - ASGI server for FastAPI

### Frontend
- **React 19** - Latest React with modern features
- **Vite** - Fast build tool and development server
- **JavaScript/JSX** - Frontend development
- **CSS3** - Modern styling with responsive design
- **WebSocket Client** - Real-time communication with backend

### Infrastructure
- **Docker** - Containerization for Redis
- **Redis 7** - Primary data storage

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **Docker** (for Redis)

### 1. Clone Repository
```bash
git clone <repository-url>
cd taskboard
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Start Redis Server
```bash
# Start Redis container
docker run --name taskboard-redis -p 6379:6379 -d redis:7

# Or if already exists, restart it
docker stop taskboard-redis 2>/dev/null
docker rm taskboard-redis 2>/dev/null
docker run --name taskboard-redis -p 6379:6379 -d redis:7
```

### 5. Run the Application

#### Start Backend (Terminal 1)
```bash
cd backend
uvicorn main:app --reload
```

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

### 6. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Auto-generated FastAPI docs)

## 📁 Project Structure

```
taskboard/
├── backend/                    # Backend FastAPI application
│   ├── api/                   # API route modules
│   │   ├── users.py          # User authentication endpoints
│   │   ├── projects.py       # Project management endpoints
│   │   └── tasks.py          # Task management endpoints
│   ├── docs/                 # Documentation
│   │   ├── API.md           # API documentation
│   │   ├── MANUAL_TEST.md   # Manual testing guide
│   │   └── TEST_FLOW.md     # API test flow description
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Data models and schemas
│   ├── redis_client.py      # Redis connection and operations
│   ├── ws.py                # WebSocket connection handler
│   ├── requirements.txt     # Python dependencies
│   └── test_api_flow.py     # API testing script
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Board.jsx    # Kanban board component
│   │   │   ├── Card.jsx     # Task card component
│   │   │   ├── Column.jsx   # Board column component
│   │   │   ├── Sidebar.jsx  # Project sidebar
│   │   │   ├── Summary.jsx  # Project summary component
│   │   │   ├── Topbar.jsx   # Top navigation bar
│   │   │   └── modals/      # Modal components
│   │   ├── pages/           # Page components
│   │   │   ├── Auth.jsx     # Login/Register page
│   │   │   └── Home.jsx     # Main dashboard
│   │   ├── services/        # Service layers
│   │   │   ├── authService.js        # Authentication service
│   │   │   ├── projectDataService.js # Project data service
│   │   │   ├── userDataService.js    # User data service
│   │   │   └── websocketService.js   # WebSocket service
│   │   ├── api/             # API communication
│   │   │   └── taskboard.js # API client
│   │   ├── styles/          # CSS stylesheets
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── docker-compose.yml         # Docker configuration for PostgreSQL
└── README.md                  # Project documentation
```

## 🔌 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
All API requests (except login/registration) require Bearer token:
```
Authorization: Bearer <access_token>
```

### Key Endpoints

#### 🔐 User Authentication
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get current user info
- `GET /api/users/` - Get all users
- `PUT /api/users/{userId}` - Update user info

#### 📂 Project Management
- `GET /api/projects/my-projects` - Get user's projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{projectId}` - Get project details
- `PUT /api/projects/{projectId}` - Update project
- `DELETE /api/projects/{projectId}` - Delete project
- `GET /api/projects/{projectId}/members` - Get project members
- `POST /api/projects/{projectId}/members` - Add project member
- `DELETE /api/projects/{projectId}/members/{userId}` - Remove member
- `GET /api/projects/{projectId}/workload` - Get project workload statistics

#### 📝 Task Management
- `GET /api/projects/{projectId}/board` - Get project kanban board
- `POST /api/projects/{projectId}/tasks` - Create new task
- `PUT /api/projects/{projectId}/tasks/{taskId}` - Update task
- `PUT /api/projects/{projectId}/tasks/{taskId}/move` - Move task between columns
- `DELETE /api/projects/{projectId}/tasks/{taskId}` - Delete task

### 📊 WebSocket Real-time Events
- **Connection**: `ws://localhost:8000/ws?user_id={userId}`
- **Event Types**:
  - `task_created` - New task added
  - `task_updated` - Task modified
  - `task_moved` - Task moved between columns
  - `task_deleted` - Task removed
  - `project_created` - New project created
  - `project_updated` - Project modified
  - `member_added` - Member added to project
  - `member_removed` - Member removed from project

## 🧪 Testing

### API Testing
Run the comprehensive API test suite:

```bash
cd backend

# Start Redis server first
docker run --name taskboard-redis -p 6379:6379 -d redis:7

# Start backend server
uvicorn main:app --reload

# Run API tests (in another terminal)
python test_api_flow.py --base-url http://localhost:8000 --verbose
```

### Manual Testing
Follow the manual testing guide for end-to-end testing:
- See `backend/docs/MANUAL_TEST.md` for detailed testing procedures
- Test real-time collaboration with multiple browser windows
- Verify WebSocket functionality and live updates

### Test Coverage
- **User Management**: Registration, login, profile updates
- **Project Operations**: CRUD operations, member management
- **Task Management**: Board operations, task lifecycle
- **Real-time Features**: WebSocket events, live synchronization
- **Authentication**: JWT token handling, session management

## 🏗️ Architecture



### Data Flow
1. **Frontend** → API calls → **Backend FastAPI**
2. **Backend** → Data operations → **Redis**
3. **Backend** → Real-time events → **WebSocket** → **Frontend**

### Real-time Communication
- WebSocket connections maintain live sync between users
- Events are broadcasted to all connected clients
- Automatic reconnection handling for robust connectivity

### Data Storage
- **Redis** serves as the primary data store
- Key-value pairs for users, projects, tasks, and relationships
- Fast in-memory operations for real-time performance

## 🚀 Deployment

### Development
- Backend: `uvicorn main:app --reload`
- Frontend: `npm run dev`
- Redis: Docker container

### Production Considerations
- Use Redis cluster for high availability
- Configure CORS for production domains
- Set up SSL/TLS certificates
- Use process managers (PM2, supervisor)
- Configure reverse proxy (Nginx)

**Start collaborating with TaskBoard - where real-time teamwork meets efficient task management!** 🚀