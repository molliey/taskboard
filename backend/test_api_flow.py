#!/usr/bin/env python3
"""
Task Board API Flow Test Script

This script tests the complete API flow for the Task Board application.
It follows the natural user workflow and covers all major API endpoints.

Usage:
    python test_api_flow.py [--base-url BASE_URL] [--verbose]

Example:
    python test_api_flow.py --base-url http://localhost:8000 --verbose
"""

import requests
import json
import time
import argparse
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import websockets

@dataclass
class TestResult:
    """Test result data class"""
    test_name: str
    success: bool
    response_time: float
    status_code: int
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class APITester:
    """Main API tester class"""
    
    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        
        # Test data storage
        self.test_users: List[Dict] = []
        self.test_projects: List[Dict] = []
        self.test_tasks: List[Dict] = []
        self.access_token: Optional[str] = None
        self.current_user: Optional[Dict] = None
        
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, test_name: str = "") -> TestResult:
        """Make HTTP request and return test result"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        # Add authorization header if token exists
        if self.access_token and headers is None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
        elif self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            # Parse response
            try:
                response_data = response.json() if response.content else None
            except json.JSONDecodeError:
                response_data = {"raw_content": response.text}
            
            success = 200 <= response.status_code < 300
            error_message = None if success else f"HTTP {response.status_code}: {response.text}"
            
            result = TestResult(
                test_name=test_name,
                success=success,
                response_time=response_time,
                status_code=response.status_code,
                error_message=error_message,
                response_data=response_data
            )
            
            self.test_results.append(result)
            
            if success:
                self.log(f"✅ {test_name} - {response.status_code} ({response_time:.3f}s)")
            else:
                self.log(f"❌ {test_name} - {response.status_code} ({response_time:.3f}s): {error_message}")
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                success=False,
                response_time=response_time,
                status_code=0,
                error_message=str(e)
            )
            self.test_results.append(result)
            self.log(f"❌ {test_name} - Exception: {str(e)}")
            return result
    
    def test_user_registration(self) -> bool:
        """Test user registration flow"""
        self.log("\n👤 Testing User Registration...")
        
        # Test data for multiple users
        test_users_data = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "password": "password123",
                "role": "Frontend Developer"
            },
            {
                "name": "Bob Smith",
                "email": "bob.smith@company.com",
                "password": "password123",
                "role": "Backend Developer"
            },
            {
                "name": "Charlie Wilson",
                "email": "charlie.wilson@company.com",
                "password": "password123",
                "role": "UI/UX Designer"
            },
            {
                "name": "Diana Chen",
                "email": "diana.chen@company.com",
                "password": "password123",
                "role": "Product Manager"
            }
        ]
        
        all_success = True
        for i, user_data in enumerate(test_users_data):
            result = self.make_request(
                "POST", 
                "/api/users/register", 
                data=user_data,
                test_name=f"Register User {i+1}: {user_data['name']}"
            )
            
            if result.success and result.response_data:
                self.test_users.append(result.response_data)
            
            all_success = all_success and result.success
        
        return all_success
    
    def test_user_login(self) -> bool:
        """Test user login flow"""
        self.log("\n🔐 Testing User Login...")
        
        if not self.test_users:
            self.log("❌ No test users available for login test")
            return False
        
        # Login with first user
        login_data = {
            "email": self.test_users[0]["email"],
            "password": "password123"
        }
        
        result = self.make_request(
            "POST",
            "/api/users/login",
            data=login_data,
            test_name=f"Login User: {self.test_users[0]['name']}"
        )
        
        if result.success and result.response_data:
            self.access_token = result.response_data.get("access_token")
            self.current_user = result.response_data.get("user")
            self.log(f"✅ Logged in as: {self.current_user['name']}")
            return True
        
        return False
    
    def test_get_current_user(self) -> bool:
        """Test getting current user information"""
        self.log("\n👤 Testing Get Current User...")
        
        result = self.make_request(
            "GET",
            "/api/users/me",
            test_name="Get Current User"
        )
        
        return result.success
    
    def test_get_all_users(self) -> bool:
        """Test getting all users"""
        self.log("\n👥 Testing Get All Users...")
        
        result = self.make_request(
            "GET",
            "/api/users/",
            test_name="Get All Users"
        )
        
        return result.success
    
    def test_get_user_by_id(self) -> bool:
        """Test getting user by ID"""
        self.log("\n👤 Testing Get User by ID...")
        
        if not self.test_users:
            self.log("❌ No test users available")
            return False
        
        all_success = True
        for user in self.test_users[:2]:  # Test first 2 users
            result = self.make_request(
                "GET",
                f"/api/users/{user['id']}",
                test_name=f"Get User by ID: {user['name']}"
            )
            all_success = all_success and result.success
        
        return all_success
    
    def test_project_creation(self) -> bool:
        """Test project creation flow"""
        self.log("\n📁 Testing Project Creation...")
        
        test_projects_data = [
            {
                "name": "Web Application Development",
                "description": "Building a modern web application with React and FastAPI",
                "is_active": True
            },
            {
                "name": "E-commerce Platform",
                "description": "Online shopping platform with payment integration",
                "is_active": True
            },
            {
                "name": "Mobile App Development",
                "description": "Cross-platform mobile application",
                "is_active": True
            }
        ]
        
        all_success = True
        for i, project_data in enumerate(test_projects_data):
            result = self.make_request(
                "POST",
                "/api/projects/",
                data=project_data,
                test_name=f"Create Project {i+1}: {project_data['name']}"
            )
            
            if result.success and result.response_data:
                self.test_projects.append(result.response_data)
            
            all_success = all_success and result.success
        
        return all_success
    
    def test_get_my_projects(self) -> bool:
        """Test getting user's projects"""
        self.log("\n📋 Testing Get My Projects...")
        
        result = self.make_request(
            "GET",
            "/api/projects/my-projects",
            test_name="Get My Projects"
        )
        
        return result.success
    
    def test_get_project_details(self) -> bool:
        """Test getting project details"""
        self.log("\n📄 Testing Get Project Details...")
        
        if not self.test_projects:
            self.log("❌ No test projects available")
            return False
        
        all_success = True
        for project in self.test_projects:
            result = self.make_request(
                "GET",
                f"/api/projects/{project['id']}",
                test_name=f"Get Project Details: {project['name']}"
            )
            all_success = all_success and result.success
        
        return all_success
    
    def test_add_project_members(self) -> bool:
        """Test adding members to projects"""
        self.log("\n👥 Testing Add Project Members...")
        
        if not self.test_projects or len(self.test_users) < 2:
            self.log("❌ Need at least 1 project and 2 users for member test")
            return False
        
        all_success = True
        project = self.test_projects[0]
        
        # Add different users to the project
        for i, user in enumerate(self.test_users[1:3]):  # Skip first user (already member)
            member_data = {
                "user_id": user["id"],
                "role": f"Developer {i+1}"
            }
            
            result = self.make_request(
                "POST",
                f"/api/projects/{project['id']}/members",
                data=member_data,
                test_name=f"Add Member to Project: {user['name']}"
            )
            all_success = all_success and result.success
        
        return all_success
    
    def test_get_project_members(self) -> bool:
        """Test getting project members"""
        self.log("\n👥 Testing Get Project Members...")
        
        if not self.test_projects:
            self.log("❌ No test projects available")
            return False
        
        all_success = True
        for project in self.test_projects:
            result = self.make_request(
                "GET",
                f"/api/projects/{project['id']}/members",
                test_name=f"Get Project Members: {project['name']}"
            )
            all_success = all_success and result.success
        
        return all_success
    
    def test_task_creation(self) -> bool:
        """Test task creation flow"""
        self.log("\n📝 Testing Task Creation...")
        
        if not self.test_projects:
            self.log("❌ No test projects available for task creation")
            return False
        
        project = self.test_projects[0]
        test_tasks_data = [
            {
                "title": "User Authentication System",
                "description": "Implement user login and registration system with JWT tokens",
                "tag": "AUTHENTICATION",
                "due_date": "2025-02-15",
                "assignee_id": self.current_user["id"],
                "column_name": "TO DO"
            },
            {
                "title": "Database Schema Design",
                "description": "Design and implement PostgreSQL database schema",
                "tag": "DATABASE",
                "due_date": "2025-02-10",
                "assignee_id": self.current_user["id"],
                "column_name": "TO DO"
            },
            {
                "title": "Frontend Component Library",
                "description": "Create reusable React components",
                "tag": "FRONTEND",
                "due_date": "2025-02-20",
                "assignee_id": self.current_user["id"],
                "column_name": "IN PROGRESS"
            }
        ]
        
        all_success = True
        for i, task_data in enumerate(test_tasks_data):
            result = self.make_request(
                "POST",
                f"/api/projects/{project['id']}/tasks",
                data=task_data,
                test_name=f"Create Task {i+1}: {task_data['title']}"
            )
            
            if result.success and result.response_data:
                self.test_tasks.append(result.response_data)
            
            all_success = all_success and result.success
        
        return all_success
    
    def test_get_project_board(self) -> bool:
        """Test getting project board"""
        self.log("\n📊 Testing Get Project Board...")
        
        if not self.test_projects:
            self.log("❌ No test projects available")
            return False
        
        all_success = True
        for project in self.test_projects:
            result = self.make_request(
                "GET",
                f"/api/projects/{project['id']}/board",
                test_name=f"Get Project Board: {project['name']}"
            )
            all_success = all_success and result.success
        
        return all_success
    
    def test_task_movement(self) -> bool:
        """Test task movement between columns"""
        self.log("\n🔄 Testing Task Movement...")
        
        if not self.test_tasks or not self.test_projects:
            self.log("❌ No test tasks or projects available")
            return False
        
        project = self.test_projects[0]
        task = self.test_tasks[0]
        
        # Move task from TO DO to IN PROGRESS
        move_data = {
            "from_column": "TO DO",
            "to_column": "IN PROGRESS",
            "position": 0
        }
        
        result = self.make_request(
            "PUT",
            f"/api/projects/{project['id']}/tasks/{task['id']}/move",
            data=move_data,
            test_name=f"Move Task: {task['title']} (TO DO → IN PROGRESS)"
        )
        
        return result.success
    
    def test_task_update(self) -> bool:
        """Test task update"""
        self.log("\n✏️ Testing Task Update...")
        
        if not self.test_tasks:
            self.log("❌ No test tasks available")
            return False
        
        task = self.test_tasks[0]
        project = self.test_projects[0]
        
        update_data = {
            "title": f"Updated: {task['title']}",
            "description": f"Updated description for {task['title']}",
            "tag": "UPDATED",
            "due_date": "2025-02-25"
        }
        
        result = self.make_request(
            "PUT",
            f"/api/projects/{project['id']}/tasks/{task['id']}",
            data=update_data,
            test_name=f"Update Task: {task['title']}"
        )
        
        return result.success
    
    def test_get_project_workload(self) -> bool:
        """Test getting project workload statistics"""
        self.log("\n📈 Testing Get Project Workload...")
        
        if not self.test_projects:
            self.log("❌ No test projects available")
            return False
        
        all_success = True
        for project in self.test_projects:
            result = self.make_request(
                "GET",
                f"/api/projects/{project['id']}/workload",
                test_name=f"Get Project Workload: {project['name']}"
            )
            all_success = all_success and result.success
        
        return all_success
    
    def test_task_deletion(self) -> bool:
        """Test task deletion"""
        self.log("\n🗑️ Testing Task Deletion...")
        
        if not self.test_tasks or not self.test_projects:
            self.log("❌ No test tasks available")
            return False
        
        project = self.test_projects[0]
        task = self.test_tasks[-1]  # Delete last task
        
        result = self.make_request(
            "DELETE",
            f"/api/projects/{project['id']}/tasks/{task['id']}",
            test_name=f"Delete Task: {task['title']}"
        )
        
        if result.success:
            self.test_tasks.pop()  # Remove from test data
        
        return result.success
    
    def test_remove_project_member(self) -> bool:
        """Test removing project member"""
        self.log("\n👋 Testing Remove Project Member...")
        
        if not self.test_projects or len(self.test_users) < 2:
            self.log("❌ Need at least 1 project and 2 users")
            return False
        
        project = self.test_projects[0]
        user = self.test_users[1]  # Remove second user
        
        result = self.make_request(
            "DELETE",
            f"/api/projects/{project['id']}/members/{user['id']}",
            test_name=f"Remove Project Member: {user['name']}"
        )
        
        return result.success
    
    def test_project_update(self) -> bool:
        """Test project update"""
        self.log("\n✏️ Testing Project Update...")
        
        if not self.test_projects:
            self.log("❌ No test projects available")
            return False
        
        project = self.test_projects[0]
        update_data = {
            "name": f"Updated: {project['name']}",
            "description": f"Updated description for {project['name']}",
            "is_active": True
        }
        
        result = self.make_request(
            "PUT",
            f"/api/projects/{project['id']}",
            data=update_data,
            test_name=f"Update Project: {project['name']}"
        )
        
        return result.success
    
    def test_user_update(self) -> bool:
        """Test user profile update"""
        self.log("\n👤 Testing User Update...")
        
        if not self.current_user:
            self.log("❌ No current user available")
            return False
        
        update_data = {
            "name": f"Updated: {self.current_user['name']}",
            "role": "Senior Developer"
        }
        
        result = self.make_request(
            "PUT",
            f"/api/users/{self.current_user['id']}",
            data=update_data,
            test_name=f"Update User Profile: {self.current_user['name']}"
        )
        
        return result.success
    
    def test_project_deletion(self) -> bool:
        """Test project deletion"""
        self.log("\n🗑️ Testing Project Deletion...")
        
        if not self.test_projects:
            self.log("❌ No test projects available")
            return False
        
        project = self.test_projects[-1]  # Delete last project
        
        result = self.make_request(
            "DELETE",
            f"/api/projects/{project['id']}",
            test_name=f"Delete Project: {project['name']}"
        )
        
        if result.success:
            self.test_projects.pop()  # Remove from test data
        
        return result.success

    async def ws_receive_event(self, expected_type, timeout=3):
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as ws:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                event = json.loads(msg)
                assert event["type"] == expected_type, f"Expected {expected_type}, got {event['type']}"
                return event
            except Exception as e:
                raise AssertionError(f"WebSocket did not receive expected event {expected_type}: {e}")

    def test_task_created_ws(self):
        """Test if WebSocket receives push after task creation"""
        self.log("\n🧪 Testing WebSocket Task Created Event...")
        # Create task first
        project = self.test_projects[0]
        task_data = {
            "title": "WS Test Task",
            "description": "A test task for WS event",
            "tag": "WS",
            "due_date": "2025-02-28",
            "assignee_id": self.current_user["id"],
            "column_name": "TO DO"
        }
        # Start WebSocket listening
        async def ws_and_create():
            ws_task = asyncio.create_task(self.ws_receive_event("task_created"))
            # Use requests to create task (sync)
            result = self.make_request(
                "POST",
                f"/api/projects/{project['id']}/tasks",
                data=task_data,
                test_name="Create Task for WS"
            )
            ws_event = None
            try:
                ws_event = asyncio.get_event_loop().run_until_complete(ws_task)
            except Exception as e:
                self.log(f"❌ WebSocket event not received: {e}")
            return result, ws_event
        # Run
        result, ws_event = ws_and_create()
        if result.success and ws_event:
            self.log("✅ WebSocket received task_created event!")
            return True
        else:
            self.log("❌ WebSocket event test failed!")
            return False
    
    def run_complete_flow(self) -> bool:
        """Run the complete API test flow"""
        self.log("🚀 Starting Complete API Test Flow...")
        
        # Test flow steps
        test_steps = [
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Get All Users", self.test_get_all_users),
            ("Get User by ID", self.test_get_user_by_id),
            ("Project Creation", self.test_project_creation),
            ("Get My Projects", self.test_get_my_projects),
            ("Get Project Details", self.test_get_project_details),
            ("Add Project Members", self.test_add_project_members),
            ("Get Project Members", self.test_get_project_members),
            ("Task Creation", self.test_task_creation),
            ("Get Project Board", self.test_get_project_board),
            ("Task Movement", self.test_task_movement),
            ("Task Update", self.test_task_update),
            ("Get Project Workload", self.test_get_project_workload),
            ("Task Deletion", self.test_task_deletion),
            ("Remove Project Member", self.test_remove_project_member),
            ("Project Update", self.test_project_update),
            ("User Update", self.test_user_update),
            ("Project Deletion", self.test_project_deletion),
            ("WebSocket Task Created Event", self.test_task_created_ws),
        ]
        
        all_success = True
        for step_name, step_func in test_steps:
            self.log(f"\n{'='*50}")
            self.log(f"Step: {step_name}")
            self.log(f"{'='*50}")
            
            try:
                success = step_func() if not asyncio.iscoroutinefunction(step_func) else asyncio.get_event_loop().run_until_complete(step_func())
                if not success:
                    self.log(f"❌ Step '{step_name}' failed")
                    all_success = False
                    # Continue with other tests even if one fails
            except Exception as e:
                self.log(f"❌ Step '{step_name}' failed with exception: {str(e)}")
                all_success = False
        
        return all_success
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - successful_tests
        
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result.success:
                    print(f"  - {result.test_name}: {result.error_message}")
        
        # Performance summary
        if self.test_results:
            avg_response_time = sum(r.response_time for r in self.test_results) / len(self.test_results)
            max_response_time = max(r.response_time for r in self.test_results)
            print(f"\n⏱️ Performance:")
            print(f"  Average Response Time: {avg_response_time:.3f}s")
            print(f"  Maximum Response Time: {max_response_time:.3f}s")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Task Board API Flow Test")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = APITester(base_url=args.base_url, verbose=args.verbose)
    
    try:
        # Run complete test flow
        success = tester.run_complete_flow()
        
        # Print summary
        tester.print_summary()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        tester.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 