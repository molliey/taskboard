# Task Board API Test Flow Description

This document describes how the test script simulates real user operation flows to verify API functionality.

## Test Steps

- Step 1: Start Redis server, open a separate terminal
  
```
docker run --name taskboard-redis -p 6379:6379 redis:7
```
**Every time you run this test, you need to restart the Redis server to reset data. If already started and you want to stop and restart, open another terminal and run `docker stop taskboard` and `docker rm taskboard`**

- Step 2: Start backend, open a separate terminal

```
uvicorn main:app --reload
```

- Step 3: Run test script

```
python3 test_api_flow.py --base-url http://localhost:8000 --verbose
```

- Step 4: Expected output, if errors occur, you'll also see backend errors in the terminal from step 3

```
z5489735@L-R4MR7D33F1 new_backend % python3 test_api_flow.py --base-url http://localhost:8000 --verbose
[10:43:39] 🚀 Starting complete API test flow...
[10:43:39] 
==================================================
[10:43:39] Step: User Registration
[10:43:39] ==================================================
[10:43:39] 
👤 Testing user registration...
[10:43:39] ✅ Register user 1: Alice Johnson - 200 (0.153s)
[10:43:39] ✅ Register user 2: Bob Smith - 200 (0.010s)
[10:43:39] ✅ Register user 3: Charlie Wilson - 200 (0.011s)
[10:43:39] ✅ Register user 4: Diana Chen - 200 (0.016s)
[10:43:39] 
==================================================
[10:43:39] Step: User Login
[10:43:39] ==================================================
[10:43:39] 
🔐 Testing user login...
[10:43:40] ✅ Login user: Alice Johnson - 200 (0.011s)
[10:43:40] ✅ Logged in as: Alice Johnson
[10:43:40] 
==================================================
[10:43:40] Step: Get Current User
[10:43:40] ==================================================
[10:43:40] 
👤 Testing get current user...
[10:43:40] ✅ Get current user - 200 (0.013s)
[10:43:40] 
==================================================
[10:43:40] Step: Get All Users
[10:43:40] ==================================================
[10:43:40] 
👥 Testing get all users...
[10:43:40] ✅ Get all users - 200 (0.010s)
[10:43:40] 
==================================================
[10:43:40] Step: Get User by ID
[10:43:40] ==================================================
[10:43:40] 
👤 Testing get user by ID...
[10:43:40] ✅ Get user by ID: Alice Johnson - 200 (0.008s)
[10:43:40] ✅ Get user by ID: Bob Smith - 200 (0.006s)
[10:43:40] 
==================================================
[10:43:40] Step: Project Creation
[10:43:40] ==================================================
[10:43:40] 
📁 Testing project creation...
[10:43:40] ✅ Create project 1: Web Application Development - 200 (0.012s)
[10:43:40] ✅ Create project 2: E-commerce Platform - 200 (0.013s)
[10:43:40] ✅ Create project 3: Mobile App Development - 200 (0.014s)
[10:43:40] 
==================================================
[10:43:40] Step: Get My Projects
[10:43:40] ==================================================
[10:43:40] 
📋 Testing get my projects...
[10:43:40] ✅ Get my projects - 200 (0.008s)
[10:43:40] 
==================================================
[10:43:40] Step: Get Project Details
[10:43:40] ==================================================
[10:43:40] 
📄 Testing get project details...
[10:43:40] ✅ Get project details: Web Application Development - 200 (0.005s)
[10:43:40] ✅ Get project details: E-commerce Platform - 200 (0.005s)
[10:43:40] ✅ Get project details: Mobile App Development - 200 (0.005s)
[10:43:40] 
==================================================
[10:43:40] Step: Add Project Members
[10:43:40] ==================================================
[10:43:40] 
👥 Testing add project members...
[10:43:40] ✅ Add member to project: Bob Smith - 200 (0.009s)
[10:43:40] ✅ Add member to project: Charlie Wilson - 200 (0.011s)
[10:43:40] 
==================================================
[10:43:40] Step: Get Project Members
[10:43:40] ==================================================
[10:43:40] 
👥 Testing get project members...
[10:43:40] ✅ Get project members: Web Application Development - 200 (0.012s)
[10:43:40] ✅ Get project members: E-commerce Platform - 200 (0.006s)
[10:43:40] ✅ Get project members: Mobile App Development - 200 (0.008s)
[10:43:40] 
==================================================
[10:43:40] Step: Task Creation
[10:43:40] ==================================================
[10:43:40] 
📝 Testing task creation...
[10:43:40] ✅ Create task 1: User Authentication System - 200 (0.009s)
[10:43:40] ✅ Create task 2: Database Schema Design - 200 (0.008s)
[10:43:40] ✅ Create task 3: Frontend Component Library - 200 (0.007s)
[10:43:40] 
==================================================
[10:43:40] Step: Get Project Board
[10:43:40] ==================================================
[10:43:40] 
📊 Testing get project board...
[10:43:40] ✅ Get project board: Web Application Development - 200 (0.009s)
[10:43:40] ✅ Get project board: E-commerce Platform - 200 (0.007s)
[10:43:40] ✅ Get project board: Mobile App Development - 200 (0.009s)
[10:43:40] 
==================================================
[10:43:40] Step: Task Movement
[10:43:40] ==================================================
[10:43:40] 
🔄 Testing task movement...
[10:43:40] ✅ Move task: User Authentication System (TO DO → IN PROGRESS) - 200 (0.014s)
[10:43:40] 
==================================================
[10:43:40] Step: Task Update
[10:43:40] ==================================================
[10:43:40] 
✏️ Testing task update...
[10:43:40] ✅ Update task: User Authentication System - 200 (0.009s)
[10:43:40] 
==================================================
[10:43:40] Step: Get Project Workload
[10:43:40] ==================================================
[10:43:40] 
📈 Testing get project workload...
[10:43:40] ✅ Get project workload: Web Application Development - 200 (0.008s)
[10:43:40] ✅ Get project workload: E-commerce Platform - 200 (0.011s)
[10:43:40] ✅ Get project workload: Mobile App Development - 200 (0.009s)
[10:43:40] 
==================================================
[10:43:40] Step: Task Deletion
[10:43:40] ==================================================
[10:43:40] 
🗑️ Testing task deletion...
[10:43:40] ✅ Delete task: Frontend Component Library - 200 (0.010s)
[10:43:40] 
==================================================
[10:43:40] Step: Remove Project Member
[10:43:40] ==================================================
[10:43:40] 
👋 Testing remove project member...
[10:43:40] ✅ Remove project member: Bob Smith - 200 (0.009s)
[10:43:40] 
==================================================
[10:43:40] Step: Project Update
[10:43:40] ==================================================
[10:43:40] 
✏️ Testing project update...
[10:43:40] ✅ Update project: Web Application Development - 200 (0.009s)
[10:43:40] 
==================================================
[10:43:40] Step: User Update
[10:43:40] ==================================================
[10:43:40] 
👤 Testing user update...
[10:43:40] ✅ Update user profile: Alice Johnson - 200 (0.009s)
[10:43:40] 
==================================================
[10:43:40] Step: Project Deletion
[10:43:40] ==================================================
[10:43:40] 
🗑️ Testing project deletion...
[10:43:40] ✅ Delete project: Mobile App Development - 200 (0.008s)
[10:43:40] 
==================================================
[10:43:40] Step: WebSocket Task Creation Event
[10:43:40] ==================================================
[10:43:40] 
🧪 Testing WebSocket task creation event...
/Users/z5489735/2023/0718/taskboard/new_backend/test_api_flow.py:652: RuntimeWarning: coroutine 'APITester.test_task_created_ws.<locals>.ws_and_create' was never awaited
  result, ws_event = ws_and_create()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
[10:43:40] ❌ Step 'WebSocket Task Creation Event' failed, exception: cannot unpack non-iterable coroutine object

============================================================
📊 Test Summary
============================================================
Total tests: 37
Success: 37 ✅
Failed: 0 ❌
Success rate: 100.0%

⏱️ Performance:
  Average response time: 0.013s
  Max response time: 0.153s
```


## Test Scenario Overview

Our test script simulates a complete Task Board application usage scenario, from user registration to creating projects, managing tasks, and finally performing cleanup operations.

## Detailed Test Flow

### Phase 1: User Management

#### 1. User Registration
**Test Goal:** Verify user registration functionality works properly

**Operation Steps:**
- Create 4 test users:
  - Alice Johnson (Frontend Developer)
  - Bob Smith (Backend Developer) 
  - Charlie Wilson (UI/UX Designer)
  - Diana Chen (Product Manager)

**Expected Results:**
- Each user should successfully register
- Returned user info contains correct ID, name, email, role, etc.
- User status is active

#### 2. User Login
**Test Goal:** Verify user login and JWT token generation

**Operation Steps:**
- Login using Alice Johnson's email and password

**Expected Results:**
- Login successful
- Return valid JWT access_token
- Return current user info

#### 3. User Info Query
**Test Goal:** Verify user information query functionality

**Operation Steps:**
- Get current logged-in user info
- Get all user list
- Get specific user info by ID

**Expected Results:**
- Can correctly get current user info
- Can get all user list
- Can get specific user details by ID

### Phase 2: Project Management

#### 4. Project Creation
**Test Goal:** Verify project creation functionality

**Operation Steps:**
- Create 3 test projects:
  - Web Application Development
  - E-commerce Platform
  - Mobile App Development

**Expected Results:**
- Each project successfully created
- Project info contains correct name, description, status, etc.
- Creator automatically becomes project member

#### 5. Project Query
**Test Goal:** Verify project query functionality

**Operation Steps:**
- Get all projects for current user
- Get specific project detailed info

**Expected Results:**
- Can get all projects user participates in
- Can get project detailed info

#### 6. Project Member Management
**Test Goal:** Verify project member management functionality

**Operation Steps:**
- Add Bob Smith and Charlie Wilson to first project
- Query project member list
- Remove a project member

**Expected Results:**
- Can successfully add project members
- Can get project member list
- Can successfully remove project members

### Phase 3: Task Management

#### 7. Task Creation
**Test Goal:** Verify task creation functionality

**Operation Steps:**
- Create 3 tasks in first project:
  - User Authentication System
  - Database Schema Design
  - Frontend Component Library

**Expected Results:**
- Tasks successfully created
- Task info contains title, description, tag, due date, assignee, etc.
- Tasks correctly assigned to specified columns (TO DO or IN PROGRESS)

#### 8. Board Query
**Test Goal:** Verify board data retrieval

**Operation Steps:**
- Get complete board data for projects

**Expected Results:**
- Can get all project columns (TO DO, IN PROGRESS, IN REVIEW, DONE)
- Each column contains correct task list

#### 9. Task Operations
**Test Goal:** Verify various task operations

**Operation Steps:**
- Move task from TO DO column to IN PROGRESS column
- Update task info (title, description, tag, etc.)
- Delete a task

**Expected Results:**
- Tasks can successfully move between different columns
- Task info can be successfully updated
- Tasks can be successfully deleted

### Phase 4: Statistics

#### 10. Workload Statistics
**Test Goal:** Verify project workload statistics functionality

**Operation Steps:**
- Get workload statistics for each project

**Expected Results:**
- Can get task statistics for each user
- Includes total tasks, completed tasks, in-progress tasks, etc.

### Phase 5: Data Updates

#### 11. Info Updates
**Test Goal:** Verify info update functionality

**Operation Steps:**
- Update project info (name, description, etc.)
- Update user info (name, role, etc.)

**Expected Results:**
- Project info can be successfully updated
- User info can be successfully updated

### Phase 6: Cleanup Operations

#### 12. Data Cleanup
**Test Goal:** Verify deletion functionality

**Operation Steps:**
- Delete a project
- Remove project member

**Expected Results:**
- Project can be successfully deleted
- Member can be successfully removed

## Test Data Summary

### Created Users
- Alice Johnson (Frontend Developer) - Main test user
- Bob Smith (Backend Developer) - Project member
- Charlie Wilson (UI/UX Designer) - Project member
- Diana Chen (Product Manager) - Backup user

### Created Projects
- Web Application Development - Main test project
- E-commerce Platform - Backup project
- Mobile App Development - Backup project

### Created Tasks
- User Authentication System - Authentication system development
- Database Schema Design - Database design
- Frontend Component Library - Frontend component library

## Test Verification Points

1. **Authentication Mechanism:** Whether JWT token is correctly generated and verified
2. **Data Integrity:** Whether created data contains all necessary fields
3. **Relationship Associations:** Whether user-project-task relationships are correctly established
4. **Permission Control:** Whether users can correctly access their own data
5. **Data Consistency:** Whether update operations are reflected in all related queries
6. **Error Handling:** Whether invalid requests return appropriate error info

## Performance Expectations

- Each API request response time should be within 1 second
- Batch operations (like getting all users) should complete within reasonable time
- System should be able to handle concurrent requests

This test flow simulates the complete process from user registration to using the Task Board application, ensuring all core functionality works properly.