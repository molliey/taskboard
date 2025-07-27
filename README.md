# 🚀 Task Board - Collaborative Task Management Platform

A modern task management platform with comprehensive project management and real-time collaboration features.

![Taskboard UI](https://github.com/user-attachments/assets/ed464712-766e-44f9-90fc-8c5902d0fac0)

## 📋 Features

### ✅ Features
- **Project Management**: Create, edit, and manage multiple projects
- **Status Flow**: Task progression through multiple states (TO DO → IN PROGRESS → IN REVIEW → DONE)
- **Task Operations**: Full CRUD functionality (Create, Read, Update, Delete)
- **Project Summary**: Live synchronization across users via WebSocket
- **Team Management**: Member management and task assignment capabilities
- **Data Visualization**: Task statistics and workload distribution charts

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - Python ORM framework
- **Alembic** - Database migration tool
- **JWT** - User authentication
- **WebSocket** - Real-time communication
- **Docker** - Containerization

### Frontend
- **React 19** - User interface library
- **Vite** - Build tool and development server
- **CSS3** - Styling and animations
- **WebSocket** - Real-time communication

## 🚀 Installation & Run

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 13+**
- **Docker & Docker Compose** (optional, for easy setup)

### 📦 Install Dependencies (One Time)

#### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Frontend(React+Vite)
```bash
cd frontend
npm install
```

### 🟢 Run App Quickly (frontend + backend + Docker)

```bash
bash scripts/start.sh

bash scripts/stop.sh
```

### Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
genspark-board/
├── backend/                 # Backend code
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── database/       # Database connection
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic layer
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # Application entry point
│   ├── migrations/         # Database migrations
│   ├── tests/              # Test code
│   └── requirements.txt    # Python dependencies
├── frontend/               # Frontend code
│   ├── src/
│   │   ├── api/            # API calls
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # Service layer
│   │   ├── styles/         # Style files
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── scripts/                # Deployment scripts
└── docker-compose.yml      # Docker configuration
```

## 🔧 API Documentation

### Authentication
All API requests require a JWT token in the header:
```
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### User Management
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get current user info

#### Project Management
- `GET /api/projects/` - Get user's project list
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

#### Task Management
- `GET /api/tasks/column/{column_id}` - Get tasks in a column
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PUT /api/tasks/{id}/move` - Move task

#### Real-time Communication
- `WS /ws/{project_id}` - WebSocket connection

## 🧪 Testing

### Test Types
- **E2E Tests**: Test complete business workflows
- **Unit Tests**: Test individual components and services

### Run Tests
```bash
cd backend

# Run all tests with complete report
python -m pytest -v -s

# Run e2e tests
python -m pytest tests/e2e

# Run unit tests
python -m pytest tests/unit

```

### Current Test Status
- **Total Tests**: 145
- **Passed**: 145 ✅
- **Failed**: 0 ❌
- **Test Coverage**: 100%

![Taskboard UI](https://github.com/user-attachments/assets/c0af268d-fa19-4ec9-bed6-9f6dbcbaad7f)


## 👥 Team

- **Project**: Task Board
- **Version**: 1.0.0

---

**Start using Task Board to boost your team collaboration efficiency!** 🎉 
