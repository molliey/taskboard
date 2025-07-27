const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Enhanced error handling
class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

// Generic API request handler
async function apiRequest(url, options = {}) {
  try {
    const token = getAuthToken();
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    });

    // Handle different response types
    const contentType = response.headers.get('content-type');
    let data = null;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else if (response.status !== 204) { // 204 No Content
      data = await response.text();
    }

    if (!response.ok) {
      throw new APIError(
        data?.message || `HTTP Error: ${response.status}`,
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    
    // Network or other errors
    console.error('API Request failed:', error);
    throw new APIError('Network error or server unavailable', 0, null);
  }
}

// Task API functions
export const taskAPI = {
  // Get tasks for a specific column
  async getColumnTasks(columnId) {
    try {
      return await apiRequest(`${API_BASE_URL}/tasks/column/${columnId}`);
    } catch (error) {
      console.error(`Error fetching tasks for column ${columnId}:`, error);
      return [];
    }
  },

  // Get user's assigned tasks
  async getMyTasks(status = null) {
    try {
      const url = `${API_BASE_URL}/tasks/my-tasks${status ? `?status=${status}` : ''}`;
      return await apiRequest(url);
    } catch (error) {
      console.error('Error fetching my tasks:', error);
      return [];
    }
  },

  // Get all tasks with optional filtering
  async getAllTasks(filters = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      // Add filters to query params
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });
      
      const queryString = queryParams.toString();
      const url = `${API_BASE_URL}/tasks/${queryString ? `?${queryString}` : ''}`;
      
      return await apiRequest(url);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return [];
    }
  },

  // Get tasks by status
  async getTasksByStatus(status) {
    return this.getAllTasks({ status });
  },

  // Get single task by ID
  async getTaskById(taskId) {
    try {
      return await apiRequest(`${API_BASE_URL}/tasks/${taskId}`);
    } catch (error) {
      console.error(`Error fetching task ${taskId}:`, error);
      throw error;
    }
  },

  // Create new task
  async createTask(taskData) {
    try {
      // Validate required fields
      if (!taskData.title?.trim()) {
        throw new APIError('Task title is required', 400);
      }

      const response = await apiRequest(`${API_BASE_URL}/tasks/`, {
        method: 'POST',
        body: JSON.stringify(taskData),
      });
      
      console.log('Task created successfully:', response);
      return response;
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },

  // Update task (full update)
  async updateTask(taskId, taskData) {
    try {
      if (!taskId) {
        throw new APIError('Task ID is required', 400);
      }

      const response = await apiRequest(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify(taskData),
      });
      
      console.log('Task updated successfully:', response);
      return response;
    } catch (error) {
      console.error(`Error updating task ${taskId}:`, error);
      throw error;
    }
  },

  // Partial update task (PATCH)
  async patchTask(taskId, updates) {
    try {
      if (!taskId) {
        throw new APIError('Task ID is required', 400);
      }

      const response = await apiRequest(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify(updates),
      });
      
      console.log('Task patched successfully:', response);
      return response;
    } catch (error) {
      console.error(`Error patching task ${taskId}:`, error);
      throw error;
    }
  },

  // Delete task
  async deleteTask(taskId) {
    try {
      if (!taskId) {
        throw new APIError('Task ID is required', 400);
      }

      await apiRequest(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'DELETE',
      });
      
      console.log(`Task ${taskId} deleted successfully`);
      return true;
    } catch (error) {
      console.error(`Error deleting task ${taskId}:`, error);
      throw error;
    }
  },

  // Move task (drag & drop)
  async moveTask(moveData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/tasks/move`, {
        method: 'POST',
        body: JSON.stringify(moveData),
      });
      
      console.log('Task moved successfully:', response);
      return response;
    } catch (error) {
      console.error('Error moving task:', error);
      throw error;
    }
  },

  // Update task status (legacy method)
  async updateTaskStatus(taskId, newStatus, position = null) {
    try {
      const updates = { status: newStatus };
      if (position !== null) {
        updates.position = position;
      }
      
      return await this.patchTask(taskId, updates);
    } catch (error) {
      console.error(`Error updating task status ${taskId}:`, error);
      throw error;
    }
  },

  // Bulk operations
  async bulkUpdateTasks(updates) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/tasks/bulk-update`, {
        method: 'POST',
        body: JSON.stringify({ updates }),
      });
      
      console.log('Bulk update completed:', response);
      return response;
    } catch (error) {
      console.error('Error in bulk update:', error);
      throw error;
    }
  },

  // Search tasks
  async searchTasks(searchTerm, filters = {}) {
    try {
      const searchFilters = {
        ...filters,
        search: searchTerm,
      };
      
      return await this.getAllTasks(searchFilters);
    } catch (error) {
      console.error('Error searching tasks:', error);
      return [];
    }
  }
};

// Column API functions
export const columnAPI = {
  // Get project columns
  async getProjectColumns(projectId) {
    try {
      return await apiRequest(`${API_BASE_URL}/columns/project/${projectId}`);
    } catch (error) {
      console.error(`Error fetching columns for project ${projectId}:`, error);
      return [];
    }
  },

  // Create new column
  async createColumn(columnData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/columns/`, {
        method: 'POST',
        body: JSON.stringify(columnData),
      });
      
      console.log('Column created successfully:', response);
      return response;
    } catch (error) {
      console.error('Error creating column:', error);
      throw error;
    }
  },

  // Update column
  async updateColumn(columnId, columnData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/columns/${columnId}`, {
        method: 'PUT',
        body: JSON.stringify(columnData),
      });
      
      console.log('Column updated successfully:', response);
      return response;
    } catch (error) {
      console.error(`Error updating column ${columnId}:`, error);
      throw error;
    }
  },

  // Delete column
  async deleteColumn(columnId) {
    try {
      await apiRequest(`${API_BASE_URL}/columns/${columnId}`, {
        method: 'DELETE',
      });
      
      console.log(`Column ${columnId} deleted successfully`);
      return true;
    } catch (error) {
      console.error(`Error deleting column ${columnId}:`, error);
      throw error;
    }
  },
};

// Project API functions
export const projectAPI = {
  // Get user's projects
  async getMyProjects() {
    try {
      return await apiRequest(`${API_BASE_URL}/projects/my-projects`);
    } catch (error) {
      console.error('Error fetching my projects:', error);
      return [];
    }
  },

  // Get project details
  async getProject(projectId) {
    try {
      return await apiRequest(`${API_BASE_URL}/projects/${projectId}`);
    } catch (error) {
      console.error(`Error fetching project ${projectId}:`, error);
      throw error;
    }
  },

  // Create new project
  async createProject(projectData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/projects/`, {
        method: 'POST',
        body: JSON.stringify(projectData),
      });
      
      console.log('Project created successfully:', response);
      return response;
    } catch (error) {
      console.error('Error creating project:', error);
      throw error;
    }
  },

  // Update project
  async updateProject(projectId, projectData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/projects/${projectId}`, {
        method: 'PUT',
        body: JSON.stringify(projectData),
      });
      
      console.log('Project updated successfully:', response);
      return response;
    } catch (error) {
      console.error(`Error updating project ${projectId}:`, error);
      throw error;
    }
  },

  // Delete project
  async deleteProject(projectId) {
    try {
      await apiRequest(`${API_BASE_URL}/projects/${projectId}`, {
        method: 'DELETE',
      });
      
      console.log(`Project ${projectId} deleted successfully`);
      return true;
    } catch (error) {
      console.error(`Error deleting project ${projectId}:`, error);
      throw error;
    }
  },

  // Add member to project
  async addMember(projectId, memberData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/projects/${projectId}/members`, {
        method: 'POST',
        body: JSON.stringify(memberData),
      });
      
      console.log('Member added successfully:', response);
      return response;
    } catch (error) {
      console.error(`Error adding member to project ${projectId}:`, error);
      throw error;
    }
  },

  // Remove member from project
  async removeMember(projectId, userId) {
    try {
      await apiRequest(`${API_BASE_URL}/projects/${projectId}/members/${userId}`, {
        method: 'DELETE',
      });
      
      console.log(`Member ${userId} removed from project ${projectId}`);
      return true;
    } catch (error) {
      console.error(`Error removing member from project ${projectId}:`, error);
      throw error;
    }
  },
};

// User API functions 
export const userAPI = {
  // Login
  async login(credentials) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(credentials),
      });
      
      // Store token
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token);
      }
      
      return response;
    } catch (error) {
      console.error('Error logging in:', error);
      throw error;
    }
  },

  // Register
  async register(userData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/users/register`, {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      
      console.log('User registered successfully:', response);
      return response;
    } catch (error) {
      console.error('Error registering user:', error);
      throw error;
    }
  },

  // Logout
  logout() {
    localStorage.removeItem('access_token');
  },

  // Get current user
  async getCurrentUser() {
    try {
      return await apiRequest(`${API_BASE_URL}/users/me`);
    } catch (error) {
      console.error('Error fetching current user:', error);
      throw error;
    }
  },

  // Get all users (for assignment)
  async getAllUsers() {
    try {
      return await apiRequest(`${API_BASE_URL}/users/`);
    } catch (error) {
      console.error('Error fetching users:', error);
      return [];
    }
  },

  // Get user by ID
  async getUserById(userId) {
    try {
      return await apiRequest(`${API_BASE_URL}/users/${userId}`);
    } catch (error) {
      console.error(`Error fetching user ${userId}:`, error);
      throw error;
    }
  },

  // Update user profile
  async updateUser(userId, userData) {
    try {
      const response = await apiRequest(`${API_BASE_URL}/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(userData),
      });
      
      console.log('User updated successfully:', response);
      return response;
    } catch (error) {
      console.error(`Error updating user ${userId}:`, error);
      throw error;
    }
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!getAuthToken();
  },
};

// Export the APIError for use in components
export { APIError };