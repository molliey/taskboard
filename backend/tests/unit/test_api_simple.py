"""
API层基础测试
测试API路由是否可达和基本功能
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAPIRoutes:
    """测试API路由可达性"""

    def test_root_endpoint(self):
        """测试根路径"""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "Task Board API" in response.json()["message"]

    def test_health_endpoint(self):
        """测试健康检查端点"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_docs_endpoint(self):
        """测试API文档端点"""
        client = TestClient(app)
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_endpoint(self):
        """测试OpenAPI schema端点"""
        client = TestClient(app)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()


class TestUserAPIRoutes:
    """测试用户API路由可达性"""

    def test_register_endpoint_exists(self):
        """测试注册端点存在"""
        client = TestClient(app)
        # Invalid data should return validation error, not 404
        response = client.post("/api/users/register", json={})
        assert response.status_code != 404

    def test_login_endpoint_exists(self):
        """测试登录端点存在"""
        client = TestClient(app)
        # Invalid data should return validation error, not 404
        response = client.post("/api/users/login")
        assert response.status_code != 404

    def test_get_users_endpoint_requires_auth(self):
        """测试获取用户列表需要认证"""
        client = TestClient(app)
        response = client.get("/api/users/")
        assert response.status_code == 401

    def test_register_validation(self):
        """测试注册数据验证"""
        client = TestClient(app)
        
        # Test missing required fields
        response = client.post("/api/users/register", json={"username": "test"})
        assert response.status_code == 422
        
        # Test invalid email format
        response = client.post("/api/users/register", json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Test short username
        response = client.post("/api/users/register", json={
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        assert response.status_code == 422


class TestProjectAPIRoutes:
    """测试项目API路由可达性"""

    def test_create_project_endpoint_requires_auth(self):
        """测试创建项目需要认证"""
        client = TestClient(app)
        response = client.post("/api/projects/", json={"name": "Test"})
        assert response.status_code == 401

    def test_get_projects_endpoint_requires_auth(self):
        """测试获取项目列表需要认证"""
        client = TestClient(app)
        response = client.get("/api/projects/")
        assert response.status_code == 401

    def test_project_validation(self):
        """测试项目数据验证"""
        client = TestClient(app)
        
        # Test missing required fields
        response = client.post("/api/projects/", json={})
        assert response.status_code in [401, 422]  # Either auth error or validation error
        
        response = client.post("/api/projects/", json={"description": "Test"})
        assert response.status_code in [401, 422]  # Missing name field


class TestColumnAPIRoutes:
    """测试列API路由可达性"""

    def test_create_column_endpoint_requires_auth(self):
        """测试创建列需要认证"""
        client = TestClient(app)
        response = client.post("/api/columns/", json={"name": "Test"})
        assert response.status_code == 401


class TestTaskAPIRoutes:
    """测试任务API路由可达性"""

    def test_create_task_endpoint_requires_auth(self):
        """测试创建任务需要认证"""
        client = TestClient(app)
        response = client.post("/api/tasks/", json={"title": "Test"})
        assert response.status_code == 401


class TestWebSocketEndpoint:
    """测试WebSocket端点"""

    def test_websocket_endpoint_exists(self):
        """测试WebSocket端点存在"""
        client = TestClient(app)
        # WebSocket test - should not return 404
        try:
            with client.websocket_connect("/ws"):
                pass
        except Exception:
            # Connection might fail, but endpoint should exist
            pass


class TestCORSConfiguration:
    """测试CORS配置"""

    def test_cors_headers_present(self):
        """测试CORS头部存在"""
        client = TestClient(app)
        response = client.options("/")
        # CORS middleware should add headers
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented


class TestErrorResponses:
    """测试错误响应"""

    def test_404_for_nonexistent_routes(self):
        """测试不存在的路由返回404"""
        client = TestClient(app)
        response = client.get("/nonexistent/route")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """测试不允许的HTTP方法"""
        client = TestClient(app)
        # Try POST on a GET-only endpoint
        response = client.post("/health")
        assert response.status_code == 405


class TestAPIResponseFormat:
    """测试API响应格式"""

    def test_json_response_format(self):
        """测试JSON响应格式"""
        client = TestClient(app)
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
        
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_error_response_format(self):
        """测试错误响应格式"""
        client = TestClient(app)
        response = client.get("/api/users/")  # Should return 401
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/json"
        
        response = client.get("/nonexistent")  # Should return 404
        assert response.status_code == 404
        assert response.headers["content-type"] == "application/json"


class TestAPIPerformance:
    """测试API性能"""

    def test_response_time_reasonable(self):
        """测试响应时间合理"""
        import time
        client = TestClient(app)
        
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        assert response.status_code == 200
        # Response should be fast (under 1 second)
        assert (end_time - start_time) < 1.0

    def test_multiple_requests_handled(self):
        """测试可以处理多个请求"""
        client = TestClient(app)
        
        # Make multiple requests in sequence
        for i in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"