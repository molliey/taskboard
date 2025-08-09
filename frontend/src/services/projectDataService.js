// 项目数据管理服务 - 为每个项目存储独立的看板数据
class ProjectDataService {
  constructor() {
    // 存储每个项目的看板数据
    this.projectsData = new Map();
    this.initializeDefaultData();
  }

  // 初始化默认数据
  initializeDefaultData() {
    // Project A 数据 (Web Application Development)
    this.projectsData.set(1, {
      "TO DO": [
        { 
          id: "PA-1", 
          title: "User Authentication System", 
          tag: "AUTHENTICATION",
          description: "Implement user login and registration system with JWT tokens",
          due_date: "2025-02-05",
          assignee_id: 1
        },
        { 
          id: "PA-2", 
          title: "Database Schema Design", 
          tag: "DATABASE",
          description: "Design and implement PostgreSQL database schema for user management",
          due_date: "2025-02-03",
          assignee_id: 2
        },
        { 
          id: "PA-3", 
          title: "Frontend Component Library", 
          tag: "FRONTEND",
          description: "Create reusable React components for the application",
          due_date: "2025-02-10",
          assignee_id: 3
        }
      ],
      "IN PROGRESS": [
        { 
          id: "PA-4", 
          title: "REST API Development", 
          tag: "BACKEND",
          description: "Develop REST API endpoints for CRUD operations",
          due_date: "2025-02-04",
          assignee_id: 6
        },
        { 
          id: "PA-5", 
          title: "User Interface Mockups", 
          tag: "DESIGN",
          description: "Create high-fidelity mockups for main application screens",
          due_date: "2025-02-02",
          assignee_id: 3
        }
      ],
      "IN REVIEW": [
        { 
          id: "PA-6", 
          title: "Security Implementation", 
          tag: "SECURITY",
          description: "Implement OAuth2 and security middleware",
          due_date: "2025-02-15",
          assignee_id: 2
        },
        { 
          id: "PA-7", 
          title: "Unit Testing Setup", 
          tag: "TESTING",
          description: "Set up Jest and testing framework for backend APIs",
          due_date: "2025-02-01",
          assignee_id: 7
        }
      ],
      "DONE": [
        { 
          id: "PA-8", 
          title: "Project Setup & Configuration", 
          tag: "SETUP",
          description: "Initialize project structure and development environment",
          due_date: "2024-01-30",
          assignee_id: 6
        },
        { 
          id: "PA-9", 
          title: "Requirements Analysis", 
          tag: "PLANNING",
          description: "Gather and document functional requirements",
          due_date: "2024-01-25",
          assignee_id: 1
        }
      ]
    });

    // Project B 数据 (E-commerce Platform)
    this.projectsData.set(2, {
      "TO DO": [
        { 
          id: "PB-1", 
          title: "Product Catalog Frontend", 
          tag: "FRONTEND",
          description: "Build responsive product catalog with search and filtering",
          due_date: "2025-02-06",
          assignee_id: 3
        },
        { 
          id: "PB-2", 
          title: "Payment Gateway Integration", 
          tag: "PAYMENT",
          description: "Integrate Stripe payment processing with checkout flow",
          due_date: "2024-03-01",
          assignee_id: 2
        },
        { 
          id: "PB-3", 
          title: "Inventory Management System", 
          tag: "BACKEND",
          description: "Develop inventory tracking and stock management APIs",
          due_date: "2024-02-28",
          assignee_id: 6
        }
      ],
      "IN PROGRESS": [
        { 
          id: "PB-4", 
          title: "Shopping Cart Functionality", 
          tag: "FRONTEND",
          description: "Implement add to cart, quantity updates, and cart persistence",
          due_date: "2025-02-04",
          assignee_id: 3
        },
        { 
          id: "PB-5", 
          title: "Order Management Backend", 
          tag: "BACKEND",
          description: "Create APIs for order processing and status tracking",
          due_date: "2024-02-20",
          assignee_id: 2
        },
        { 
          id: "PB-6", 
          title: "Product Images & Media", 
          tag: "DESIGN",
          description: "Design and implement product image gallery and zoom features",
          due_date: "2024-02-16",
          assignee_id: 8
        }
      ],
      "IN REVIEW": [
        { 
          id: "PB-7", 
          title: "User Reviews & Ratings", 
          tag: "FEATURE",
          description: "Allow users to rate and review products with moderation",
          due_date: "2024-02-22",
          assignee_id: 6
        },
        { 
          id: "PB-8", 
          title: "Email Notifications", 
          tag: "NOTIFICATION",
          description: "Send order confirmations and shipping notifications",
          due_date: "2024-02-19",
          assignee_id: 4
        }
      ],
      "DONE": [
        { 
          id: "PB-9", 
          title: "Database Design", 
          tag: "DATABASE",
          description: "Design e-commerce database schema for products, orders, users",
          due_date: "2024-02-05",
          assignee_id: 2
        },
        { 
          id: "PB-10", 
          title: "Brand Identity & Logo", 
          tag: "DESIGN",
          description: "Create brand guidelines and logo for e-commerce platform",
          due_date: "2024-02-01",
          assignee_id: 8
        }
      ]
    });

    // Project C 数据 (Mobile App Development)
    this.projectsData.set(3, {
      "TO DO": [
        { 
          id: "PC-1", 
          title: "Push Notifications System", 
          tag: "MOBILE",
          description: "Implement Firebase push notifications for iOS and Android",
          due_date: "2024-02-28",
          assignee_id: 5
        },
        { 
          id: "PC-2", 
          title: "Offline Data Sync", 
          tag: "MOBILE",
          description: "Implement offline mode with data synchronization",
          due_date: "2024-03-05",
          assignee_id: 6
        },
        { 
          id: "PC-3", 
          title: "App Store Optimization", 
          tag: "MARKETING",
          description: "Prepare app store listings and optimize for discovery",
          due_date: "2024-03-10",
          assignee_id: 4
        }
      ],
      "IN PROGRESS": [
        { 
          id: "PC-4", 
          title: "React Native Setup", 
          tag: "MOBILE",
          description: "Initialize React Native project with navigation and state management",
          due_date: "2025-02-03",
          assignee_id: 6
        },
        { 
          id: "PC-5", 
          title: "API Integration Layer", 
          tag: "INTEGRATION",
          description: "Connect mobile app with backend REST APIs",
          due_date: "2024-02-24",
          assignee_id: 1
        },
        { 
          id: "PC-6", 
          title: "User Authentication Flow", 
          tag: "MOBILE",
          description: "Implement login, signup, and session management",
          due_date: "2024-02-20",
          assignee_id: 6
        },
        { 
          id: "PC-7", 
          title: "Camera Integration", 
          tag: "FEATURE",
          description: "Add photo capture and image processing features",
          due_date: "2024-02-26",
          assignee_id: 5
        }
      ],
      "IN REVIEW": [
        { 
          id: "PC-8", 
          title: "App Icon & Splash Screen", 
          tag: "DESIGN",
          description: "Design app icon and splash screen for both platforms",
          due_date: "2024-02-14",
          assignee_id: 8
        }
      ],
      "DONE": [
        { 
          id: "PC-9", 
          title: "Market Research & Analysis", 
          tag: "RESEARCH",
          description: "Analyze competitor apps and user behavior patterns",
          due_date: "2024-01-25",
          assignee_id: 4
        },
        { 
          id: "PC-10", 
          title: "UI/UX Wireframes", 
          tag: "DESIGN",
          description: "Create detailed wireframes and user flow diagrams",
          due_date: "2024-02-02",
          assignee_id: 8
        },
        { 
          id: "PC-11", 
          title: "Technical Architecture", 
          tag: "ARCHITECTURE",
          description: "Define mobile app architecture and technology stack",
          due_date: "2024-02-08",
          assignee_id: 7
        }
      ]
    });
  }

  // 获取指定项目的数据
  getProjectData(projectId) {
    if (!this.projectsData.has(projectId)) {
      // 如果项目不存在，创建空的看板数据
      this.projectsData.set(projectId, {
        "TO DO": [],
        "IN PROGRESS": [],
        "IN REVIEW": [],
        "DONE": []
      });
    }
    return this.projectsData.get(projectId);
  }

  // 更新项目数据
  updateProjectData(projectId, newData) {
    this.projectsData.set(projectId, newData);
  }

  // 添加任务到指定项目
  addTaskToProject(projectId, columnName, task) {
    const projectData = this.getProjectData(projectId);
    if (projectData[columnName]) {
      projectData[columnName].push(task);
      this.updateProjectData(projectId, projectData);
    }
  }

  // 移动任务
  moveTaskInProject(projectId, taskId, fromColumn, toColumn) {
    const projectData = this.getProjectData(projectId);
    const task = projectData[fromColumn]?.find(t => t.id === taskId);
    
    if (task) {
      // 从原列移除
      projectData[fromColumn] = projectData[fromColumn].filter(t => t.id !== taskId);
      // 添加到新列
      projectData[toColumn].push(task);
      this.updateProjectData(projectId, projectData);
    }
  }

  // 删除任务
  deleteTaskFromProject(projectId, taskId, columnName) {
    const projectData = this.getProjectData(projectId);
    if (projectData[columnName]) {
      projectData[columnName] = projectData[columnName].filter(t => t.id !== taskId);
      this.updateProjectData(projectId, projectData);
    }
  }

  // 获取所有项目ID
  getAllProjectIds() {
    return Array.from(this.projectsData.keys());
  }

  // 清除项目数据（用于重置）
  clearProjectData(projectId) {
    this.projectsData.set(projectId, {
      "TO DO": [],
      "IN PROGRESS": [],
      "IN REVIEW": [],
      "DONE": []
    });
  }
}

// 创建单例实例
const projectDataService = new ProjectDataService();

export default projectDataService;