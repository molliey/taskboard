# API Documentation

This document describes all API endpoints expected by the frontend.

## WebSocket Real-time Events Description
- All data modification operations (such as task creation, task status changes, member changes, etc.) are completed through RESTful API.
- After data changes, the server pushes events to all online users through WebSocket (/ws).
- WebSocket is only used for event pushing, not for data writing.
- Event format is described in the "WebSocket Events" section at the end of the document.

## Base URL
```
http://localhost:8000/api
```

## Authentication
All API requests (except login/registration) require Bearer token:
```
Authorization: Bearer <access_token>
```

## 1. User Authentication

### 1.1 User Login
```
POST /api/users/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "avatar": "👩‍💼",
    "role": "Frontend Developer",
    "is_active": true,
    "created_at": "2025-01-20T10:00:00Z"
  }
}
```

### 1.2 User Registration
```
POST /api/users/register
```

**Request:**
```json
{
  "name": "New User",
  "email": "newuser@example.com",
  "password": "password123",
  "role": "Developer"
}
```

**Response:**
```json
{
  "id": 9,
  "name": "New User",
  "email": "newuser@example.com",
  "avatar": "👤",
  "role": "Developer",
  "is_active": true,
  "created_at": "2025-01-20T10:00:00Z"
}
```

### 1.3 Get Current User
```
GET /api/users/me
```

**Response:**
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice.johnson@company.com",
  "avatar": "👩‍💼",
  "role": "Frontend Developer",
  "is_active": true,
  "created_at": "2025-01-20T10:00:00Z"
}
```

### 1.4 Get All Users
```
GET /api/users/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "avatar": "👩‍💼",
    "role": "Frontend Developer",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob.smith@company.com",
    "avatar": "👨‍💻",
    "role": "Backend Developer",
    "is_active": false
  }
]
```

### 1.5 Get User by ID
```
GET /api/users/{userId}
```

**Response:**
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice.johnson@company.com",
  "avatar": "👩‍💼",
  "role": "Frontend Developer",
  "is_active": true,
  "created_at": "2025-01-20T10:00:00Z"
}
```

### 1.6 Update User
```
PUT /api/users/{userId}
```

**Request:**
```json
{
  "name": "Updated Name",
  "email": "updated@example.com",
  "role": "Senior Developer"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Name",
  "email": "updated@example.com",
  "avatar": "👩‍💼",
  "role": "Senior Developer",
  "is_active": true,
  "updated_at": "2025-01-20T11:00:00Z"
}
```

## 2. Project Management

### 2.1 Get My Projects
```
GET /api/projects/my-projects
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Web Application Development",
    "description": "Building Modern Web Applications",
    "is_active": true,
    "created_at": "2025-01-20T10:00:00Z",
    "updated_at": "2025-01-20T10:00:00Z"
  },
  {
    "id": 2,
    "name": "E-commerce Platform",
    "description": "Online Shopping Platform",
    "is_active": true,
    "created_at": "2025-01-20T10:00:00Z",
    "updated_at": "2025-01-20T10:00:00Z"
  }
]
```

### 2.2 Get Project
```
GET /api/projects/{projectId}
```

**Response:**
```json
{
  "id": 1,
  "name": "Web Application Development",
  "description": "Building Modern Web Applications",
  "is_active": true,
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

### 2.3 Create Project
```
POST /api/projects/
```

**Request:**
```json
{
  "name": "New Project",
  "description": "Project Description",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 3,
  "name": "New Project",
  "description": "Project Description",
  "is_active": true,
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```
**WebSocket Event:**
- type: project_created
- payload: { ...new project data... }

### 2.4 Update Project
```
PUT /api/projects/{projectId}
```

**Request:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated Description",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "description": "Updated Description",
  "is_active": true,
  "updated_at": "2025-01-20T11:00:00Z"
}
```
**WebSocket Event:**
- type: project_updated
- payload: { ...updated project data... }

### 2.5 Delete Project
```
DELETE /api/projects/{projectId}
```

**Response:**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```
**WebSocket Event:**
- type: project_deleted
- payload: { "project_id": ... }

### 2.6 Get Project Members
```
GET /api/projects/{projectId}/members
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "avatar": "👩‍💼",
    "role": "Frontend Developer",
    "is_active": true,
    "joined_at": "2025-01-20T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob.smith@company.com",
    "avatar": "👨‍💻",
    "role": "Backend Developer",
    "is_active": true,
    "joined_at": "2025-01-20T10:00:00Z"
  }
]
```

### 2.7 Add Project Member
```
POST /api/projects/{projectId}/members
```

**Request:**
```json
{
  "user_id": 3,
  "role": "Developer"
}
```

**Response:**
```json
{
  "id": 3,
  "name": "Charlie Wilson",
  "email": "charlie.wilson@company.com",
  "avatar": "👨‍🎨",
  "role": "UI/UX Designer",
  "is_active": true,
  "joined_at": "2025-01-20T11:00:00Z"
}
```
**WebSocket Event:**
- type: member_added
- payload: { ...member data... }

### 2.8 Remove Project Member
```
DELETE /api/projects/{projectId}/members/{userId}
```

**Response:**
```json
{
  "success": true,
  "message": "Member removed successfully"
}
```
**WebSocket Event:**
- type: member_removed
- payload: { "user_id": ..., "project_id": ... }

### 2.9 Get Project Workload
```
GET /api/projects/{projectId}/workload
```

**Response:**
```json
[
  {
    "user_id": 1,
    "name": "Alice Johnson",
    "avatar": "👩‍💼",
    "total_tasks": 5,
    "completed_tasks": 3,
    "in_progress_tasks": 1,
    "todo_tasks": 1
  },
  {
    "user_id": 2,
    "name": "Bob Smith",
    "avatar": "👨‍💻",
    "total_tasks": 3,
    "completed_tasks": 2,
    "in_progress_tasks": 1,
    "todo_tasks": 0
  }
]
```

## 3. Task Management

### 3.1 Get Project Board
```
GET /api/projects/{projectId}/board
```

**Response:**
```json
{
  "project_id": 1,
  "columns": {
    "TO DO": [
      {
        "id": "task-123",
        "title": "Task Title",
        "description": "Task Description",
        "tag": "Feature",
        "due_date": "2025-02-15",
        "assignee_id": 1,
        "created_at": "2025-01-20T10:00:00Z",
        "updated_at": "2025-01-20T10:00:00Z"
      }
    ],
    "IN PROGRESS": [],
    "IN REVIEW": [],
    "DONE": []
  }
}
```

### 3.2 Create Task
```
POST /api/projects/{projectId}/tasks
```

**Request:**
```json
{
  "title": "New Task",
  "description": "Task Description",
  "tag": "Feature",
  "due_date": "2025-02-15",
  "assignee_id": 1,
  "column_name": "TO DO"
}
```

**Response:**
```json
{
  "id": "task-123",
  "title": "New Task",
  "description": "Task Description",
  "tag": "Feature",
  "due_date": "2025-02-15",
  "assignee_id": 1,
  "column_name": "TO DO",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```
**WebSocket Event:**
- type: task_created
- payload: { ...task data... }

### 3.3 Update Task
```
PUT /api/projects/{projectId}/tasks/{taskId}
```

**Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated Description",
  "tag": "Bug",
  "due_date": "2025-02-20",
  "assignee_id": 2
}
```

**Response:**
```json
{
  "id": "task-123",
  "title": "Updated Title",
  "description": "Updated Description",
  "tag": "Bug",
  "due_date": "2025-02-20",
  "assignee_id": 2,
  "updated_at": "2025-01-20T11:00:00Z"
}
```
**WebSocket Event:**
- type: task_updated
- payload: { ...task data... }

### 3.4 Move Task
```
PUT /api/projects/{projectId}/tasks/{taskId}/move
```

**Request:**
```json
{
  "from_column": "TO DO",
  "to_column": "IN PROGRESS",
  "position": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Task moved successfully"
}
```
**WebSocket Event:**
- type: task_moved
- payload: { "task_id": ..., "from_column": ..., "to_column": ..., "project_id": ... }

### 3.5 Delete Task
```
DELETE /api/projects/{projectId}/tasks/{taskId}
```

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```
**WebSocket Event:**
- type: task_deleted
- payload: { "task_id": ..., "column_name": ..., "project_id": ... }

## 4. WebSocket Events

### 4.1 Connection
```
WebSocket URL: ws://localhost:8000/ws?user_id={userId}
```

### 4.2 Event Format
```json
{
  "type": "task_created", // Event type
  "payload": { ... }        // Event data
}
```

### 4.3 Event Types Overview
- task_created
- task_updated
- task_moved
- task_deleted
- project_created
- project_updated
- project_deleted
- member_added
- member_removed
- board_sync
- user_count

## 5. Error Response

All API endpoints may return the following error format:

```json
{
  "message": "Error description",
  "status_code": 400,
  "details": {
    "field": "Additional error details"
  }
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

# 6. Redis Database Architecture

Based on API requirements, the following are recommended Redis data structures:

## 6.1 User Management

### User Hash Table (user:{userId})
```redis
# Key: user:{userId}
# Type: Hash table
# Used by API: GET /api/users/me, GET /api/users/{userId}, PUT /api/users/{userId}

HSET user:1 name "Alice Johnson" email "alice.johnson@company.com" password_hash "$2b$12$..." avatar "👩‍💼" role "Frontend Developer" is_active "true" created_at "2025-01-20T10:00:00Z" updated_at "2025-01-20T10:00:00Z"

# Usage examples:
HGETALL user:1
HGET user:1 name
HSET user:1 role "Senior Developer"
```

### User Email Index (email:{email})
```redis
# Key: email:{email}
# Type: String (stores userId)
# Used by API: POST /api/users/login, POST /api/users/register

SET email:alice.johnson@company.com "1"
SET email:bob.smith@company.com "2"

# Usage examples:
GET email:alice.johnson@company.com  # Returns "1"
```

### All Users Set (users:all)
```redis
# Key: users:all
# Type: Set
# Used by API: GET /api/users/

SADD users:all "1" "2" "3" "4" "5" "6" "7" "8"

# Usage examples:
SMEMBERS users:all  # Returns all user IDs
```

### Active Users Set (users:active)
```redis
# Key: users:active
# Type: Set
# Used by API: GET /api/users/ (filter active users)

SADD users:active "1" "3" "4" "6" "8"

# Usage examples:
SINTER users:all users:active  # Returns only active user IDs
```

## 6.2 Project Management

### Project Hash Table (project:{projectId})
```redis
# Key: project:{projectId}
# Type: Hash table
# Used by API: GET /api/projects/{projectId}, PUT /api/projects/{projectId}, DELETE /api/projects/{projectId}

HSET project:1 name "Web Application Development" description "Building Modern Web Applications" is_active "true" created_at "2025-01-20T10:00:00Z" updated_at "2025-01-20T10:00:00Z"

# Usage examples:
HGETALL project:1
HGET project:1 name
HSET project:1 description "Updated Description"
```

### User Projects Set (user:{userId}:projects)
```redis
# Key: user:{userId}:projects
# Type: Set
# Used by API: GET /api/projects/my-projects

SADD user:1:projects "1" "2" "3"
SADD user:2:projects "1" "2"

# Usage examples:
SMEMBERS user:1:projects  # Returns user 1's project IDs
```

### All Projects Set (projects:all)
```redis
# Key: projects:all
# Type: Set
# Used by API: Project list and management

SADD projects:all "1" "2" "3"

# Usage examples:
SMEMBERS projects:all  # Returns all project IDs
```

### Active Projects Set (projects:active)
```redis
# Key: projects:active
# Type: Set
# Used by API: Filter active projects

SADD projects:active "1" "2"

# Usage examples:
SINTER projects:all projects:active  # Returns only active project IDs
```

## 6.3 Project Members

### Project Members Set (project:{projectId}:members)
```redis
# Key: project:{projectId}:members
# Type: Set
# Used by API: GET /api/projects/{projectId}/members, POST /api/projects/{projectId}/members, DELETE /api/projects/{projectId}/members/{userId}

SADD project:1:members "1" "2" "3" "6" "7"
SADD project:2:members "2" "3" "4" "6" "8"

# Usage examples:
SMEMBERS project:1:members  # Returns member user IDs
SISMEMBER project:1:members "5"  # Check if user 5 is member
SADD project:1:members "5"  # Add user 5 to project 1
SREM project:1:members "5"  # Remove user 5 from project 1
```

### User Project Roles Hash Table (project:{projectId}:roles)
```redis
# Key: project:{projectId}:roles
# Type: Hash table
# Used by API: GET /api/projects/{projectId}/members, POST /api/projects/{projectId}/members

HSET project:1:roles "1" "Frontend Developer" "2" "Backend Developer" "3" "UI/UX Designer"

# Usage examples:
HGET project:1:roles "1"  # Returns "Frontend Developer"
HSET project:1:roles "5" "Developer"  # Set role for user 5
```

### User Projects Set (user:{userId}:projects)
```redis
# Key: user:{userId}:projects
# Type: Set
# Used by API: User project membership queries

SADD user:1:projects "1" "3"
SADD user:2:projects "1" "2"

# Usage examples:
SMEMBERS user:1:projects  # Returns projects user 1 belongs to
```

## 6.4 Task Management

### Project Board Hash Table (project:{projectId}:board)
```redis
# Key: project:{projectId}:board
# Type: Hash table (stores JSON strings for each column)
# Used by API: GET /api/projects/{projectId}/board

HSET project:1:board "TO DO" '[{"id":"task-123","title":"Task Title","description":"Task Description","tag":"Feature","due_date":"2025-02-15","assignee_id":1,"created_at":"2025-01-20T10:00:00Z","updated_at":"2025-01-20T10:00:00Z"}]'
HSET project:1:board "IN PROGRESS" '[]'
HSET project:1:board "IN REVIEW" '[]'
HSET project:1:board "DONE" '[]'

# Usage examples:
HGET project:1:board "TO DO"  # Returns task JSON string
HGETALL project:1:board  # Returns all columns
```

### Task Hash Table (task:{taskId})
```redis
# Key: task:{taskId}
# Type: Hash table
# Used by API: POST /api/projects/{projectId}/tasks, PUT /api/projects/{projectId}/tasks/{taskId}, DELETE /api/projects/{projectId}/tasks/{taskId}

HSET task:task-123 project_id "1" title "Task Title" description "Task Description" tag "Feature" due_date "2025-02-15" assignee_id "1" column_name "TO DO" position "0" created_at "2025-01-20T10:00:00Z" updated_at "2025-01-20T10:00:00Z"

# Usage examples:
HGETALL task:task-123
HGET task:task-123 title
HSET task:task-123 title "Updated Title"
DEL task:task-123
```

### Project Tasks Set (project:{projectId}:tasks)
```redis
# Key: project:{projectId}:tasks
# Type: Set
# Used by API: Task list and management within project

SADD project:1:tasks "task-123" "task-124" "task-125"

# Usage examples:
SMEMBERS project:1:tasks  # Returns all task IDs for project 1
SADD project:1:tasks "task-126"  # Add new task
SREM project:1:tasks "task-123"  # Remove task
```

### User Assigned Tasks Set (user:{userId}:assigned_tasks)
```redis
# Key: user:{userId}:assigned_tasks
# Type: Set
# Used by API: GET /api/tasks/my-tasks

SADD user:1:assigned_tasks "task-123" "task-124"
SADD user:2:assigned_tasks "task-125"

# Usage examples:
SMEMBERS user:1:assigned_tasks  # Returns tasks assigned to user 1
```

### Task Column Index (project:{projectId}:column:{columnName}:tasks)
```redis
# Key: project:{projectId}:column:{columnName}:tasks
# Type: List (maintains order)
# Used by API: Task movement and ordering

LPUSH project:1:column:TO DO:tasks "task-123" "task-124"
LPUSH project:1:column:IN PROGRESS:tasks "task-125"

# Usage examples:
LRANGE project:1:column:TO DO:tasks 0 -1  # Returns all tasks in TO DO column
LPOP project:1:column:TO DO:tasks  # Remove first task
RPUSH project:1:column:IN PROGRESS:tasks "task-123"  # Add task to end of IN PROGRESS
```

## 6.5 Authentication and Sessions

### User Session Hash Table (session:{sessionId})
```redis
# Key: session:{sessionId}
# Type: Hash table
# Used by API: JWT token validation and session management

HSET session:abc123 user_id "1" token_hash "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." expires_at "2025-01-21T10:00:00Z" created_at "2025-01-20T10:00:00Z"

# Usage examples:
HGET session:abc123 user_id  # Returns "1"
EXPIRE session:abc123 86400  # Set TTL to 24 hours
```

### User Sessions Set (user:{userId}:sessions)
```redis
# Key: user:{userId}:sessions
# Type: Set
# Used by API: Session management and logout

SADD user:1:sessions "abc123" "def456"

# Usage examples:
SMEMBERS user:1:sessions  # Returns all session IDs for user 1
SREM user:1:sessions "abc123"  # Remove specific session
```

### Session Token Index (token:{tokenHash})
```redis
# Key: token:{tokenHash}
# Type: String (stores sessionId)
# Used by API: JWT token lookup

SET token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... "abc123"

# Usage examples:
GET token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Returns "abc123"
```

## 6.6 Statistics and Analytics

### Project Workload Hash Table (project:{projectId}:workload)
```redis
# Key: project:{projectId}:workload
# Type: Hash table
# Used by API: GET /api/projects/{projectId}/workload

HSET project:1:workload "1" '{"user_id":1,"name":"Alice Johnson","avatar":"👩‍💼","total_tasks":5,"completed_tasks":3,"in_progress_tasks":1,"todo_tasks":1}'
HSET project:1:workload "2" '{"user_id":2,"name":"Bob Smith","avatar":"👨‍💻","total_tasks":3,"completed_tasks":2,"in_progress_tasks":1,"todo_tasks":0}'

# Usage examples:
HGETALL project:1:workload  # Returns all workload data
```

### User Task Counters (user:{userId}:task_counts)
```redis
# Key: user:{userId}:task_counts
# Type: Hash table
# Used by API: Workload calculation and statistics

HSET user:1:task_counts total "5" completed "3" in_progress "1" todo "1"

# Usage examples:
HGETALL user:1:task_counts  # Returns all task counts
HINCRBY user:1:task_counts total 1  # Increment total task count
```

## 6.7 WebSocket and Real-time Features

### Online Users Set (online_users)
```redis
# Key: online_users
# Type: Set
# Used by API: WebSocket user count and online status

SADD online_users "1" "2" "3"

# Usage examples:
SCARD online_users  # Returns number of online users
SISMEMBER online_users "1"  # Check if user 1 is online
SADD online_users "4"  # User 4 comes online
SREM online_users "1"  # User 1 goes offline
```

### Project Subscribers Set (project:{projectId}:subscribers)
```redis
# Key: project:{projectId}:subscribers
# Type: Set
# Used by API: WebSocket real-time updates

SADD project:1:subscribers "user:1" "user:2" "user:3"

# Usage examples:
SMEMBERS project:1:subscribers  # Returns all subscribers
SADD project:1:subscribers "user:4"  # Add new subscriber
SREM project:1:subscribers "user:1"  # Remove subscriber
```

## 6.8 API Usage Summary

### User Management APIs
- **GET /api/users/me**: `user:{userId}`, `session:{sessionId}`
- **GET /api/users/{userId}**: `user:{userId}`
- **GET /api/users/**: `users:all`, `users:active`, `user:{userId}` (for each user)
- **PUT /api/users/{userId}**: `user:{userId}`
- **POST /api/users/login**: `email:{email}`, `user:{userId}`, `session:{sessionId}`, `user:{userId}:sessions`
- **POST /api/users/register**: `user:{userId}`, `email:{email}`, `users:all`, `users:active`

### Project Management APIs
- **GET /api/projects/my-projects**: `user:{userId}:projects`, `project:{projectId}`
- **GET /api/projects/{projectId}**: `project:{projectId}`
- **POST /api/projects/**: `project:{projectId}`, `user:{userId}:projects`, `projects:all`, `projects:active`
- **PUT /api/projects/{projectId}**: `project:{projectId}`
- **DELETE /api/projects/{projectId}**: `project:{projectId}`, `user:{userId}:projects`, `projects:all`, `projects:active`

### Project Member APIs
- **GET /api/projects/{projectId}/members**: `project:{projectId}:members`, `project:{projectId}:roles`, `user:{userId}`
- **POST /api/projects/{projectId}/members**: `project:{projectId}:members`, `project:{projectId}:roles`, `user:{userId}:projects`
- **DELETE /api/projects/{projectId}/members/{userId}**: `project:{projectId}:members`, `project:{projectId}:roles`, `user:{userId}:projects`

### Task Management APIs
- **GET /api/projects/{projectId}/board**: `project:{projectId}:board`, `task:{taskId}`
- **POST /api/projects/{projectId}/tasks**: `task:{taskId}`, `project:{projectId}:tasks`, `project:{projectId}:board`, `project:{projectId}:column:{columnName}:tasks`, `user:{userId}:assigned_tasks`
- **PUT /api/projects/{projectId}/tasks/{taskId}**: `task:{taskId}`, `project:{projectId}:board`
- **PUT /api/projects/{projectId}/tasks/{taskId}/move**: `task:{taskId}`, `project:{projectId}:column:{fromColumn}:tasks`, `project:{projectId}:column:{toColumn}:tasks`, `project:{projectId}:board`
- **DELETE /api/projects/{projectId}/tasks/{taskId}**: `task:{taskId}`, `project:{projectId}:tasks`, `project:{projectId}:board`, `project:{projectId}:column:{columnName}:tasks`, `user:{userId}:assigned_tasks`

### Statistics APIs
- **GET /api/projects/{projectId}/workload**: `project:{projectId}:workload`, `user:{userId}:task_counts`

### WebSocket Events
- **User count**: `online_users`
- **Task events**: `project:{projectId}:subscribers`, `task:{taskId}`, `project:{projectId}:board`
- **Board sync**: `project:{projectId}:board`, `project:{projectId}:subscribers`