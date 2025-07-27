```markdown
# Task Board Backend

A FastAPI-based backend for a collaborative task management application with real-time updates.

## Features

- **Project Management**: Create and manage multiple projects with team collaboration
- **Task Tracking**: Full CRUD operations with drag-and-drop support
- **Team Collaboration**: Role-based access control (Owner, Admin, Member)
- **Real-time Updates**: WebSocket support for live synchronization
- **Authentication**: JWT-based secure authentication
- **RESTful API**: Clean, well-documented API endpoints

## Tech Stack

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Alembic**: Database migrations
- **WebSockets**: Real-time communication
- **JWT**: Secure authentication
- **Pytest**: Testing framework

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```